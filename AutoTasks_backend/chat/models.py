from django.db import models
from django.conf import settings
from AutoTasks_backend import secrets_manager
import openai
from reminders.models import Reminder
import json
from . import gpt_tools
from datetime import datetime
from .prompt import system_prompt_text
from django.contrib.auth import get_user_model
User = get_user_model()


class Chat(models.Model):
    SYSTEM_MESSAGE = system_prompt_text
    GPT_MODEL = "gpt-4-1106-preview"
    client = openai.Client(api_key=secrets_manager.OPENAI_API_KEY, max_retries=3)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat'
    )
    response_history = models.JSONField(default=list)  # Store an array of chat completion objects
    messages = models.JSONField(default=list)  # Store an array of messages
    tools = gpt_tools.tools

    def __str__(self):
        return f"Chat for {self.user.username}"

    def get_latest_message_content(self):
        return self.messages[-1].get('content', 'None')  # Can't use self.messages[-1].content like openAI API because the API translates the dict to an object

    def update_users_system_prompt_with_reminders_from_database(self):  # TODO: FIX THIS to use new chat structure
        try:
            # Fetch reminders from the database for the given user
            reminders = Reminder.objects.filter(user=self.user)

            # Format each reminder as a string and append it to the reminder_list
            reminder_list = ["Reminder(reminder_id, title, description, reminder_time, recurring_interval, urgency)"]  # Example format
            for reminder in reminders:
                formatted_reminder = str(reminder)
                reminder_list.append(formatted_reminder)

            # Join all formatted reminders into a single string
            reminders_string = "\n".join(reminder_list)

            # Update the system prompt with the new reminders, also update with current datetime
            updated_system_message = "Current datetime: " + str(datetime.now()) + "\n" + self.SYSTEM_MESSAGE + "\n" + reminders_string

            # Update the first message (system message) in messages. Can change to a a for loop to find system message if system message isn't always first message
            if self.messages[0]['role'] == 'system':
                self.messages[0]['content'] = updated_system_message
                self.save()  # TODO: Maybe only save at the end to prevent partial stuff getting saved in the database?
            else:
                print("No system message found in the chat object.")

        except Exception as e:
            print("Error updating system prompt in chat object")
            print(f"Exception: {e}")

    def get_response_and_add_to_history(self):
        response = self.client.chat.completions.create(
            messages=self.messages,
            model=self.GPT_MODEL,
            tools=self.tools,
            tool_choice='auto',
            max_tokens=150,
            )  # TODO: Adjust max_tokens
        response_in_dict = response.model_dump(exclude_unset=True)  # Convert to dict so it can be converted to JSON for database

        self.response_history.append(response_in_dict)
        return response

    @classmethod
    def create_with_starter_messages(cls, user, first_message):
        starter_messages = [
            {"role": "system", "content": cls.SYSTEM_MESSAGE},
            {"role": "user", "content": first_message},
        ]
        chat = cls(user=user, messages=starter_messages)

        return chat

    @classmethod
    def chat_completion_from_sms(cls, user: User, body: str):
        # Query the database for a Chat object associated with the user
        chat = cls.objects.filter(user=user).first()

        # If a Chat object exists, append a new message to the messages list in the chat_object
        if chat:
            chat.messages.append({"role": "user", "content": body})
            chat.save()
        else:
            # If a Chat object does not exist, create a new one
            chat = Chat.create_with_starter_messages(user, body)
            chat.save()

        # Update the system prompt with the latest reminders before processing
        chat.update_users_system_prompt_with_reminders_from_database()

        # Call the API method with the arguments
        response = chat.get_response_and_add_to_history()

        while response.choices[0].message.tool_calls:
            response_message = response.choices[0].message
            response_message_dict = response.model_dump(exclude_unset=True)['choices'][0]['message']
            chat.messages.append(response_message_dict)  # extend conversation with reply
            chat.save()  # TODO: Maybe only save at the end to prevent partial stuff getting saved in the database?

            tool_calls = response_message.tool_calls
            # Check if the model wanted to call a function
            if tool_calls:
                # Call the function
                # TODO: Handle errors
                available_functions = {
                    'create_reminder': Reminder.create_reminder,
                    'edit_reminder': Reminder.edit_reminder,
                    'delete_reminder': Reminder.delete_reminder,
                }
                # Step 4: send the info for each function call and function response to the model
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = available_functions[function_name]
                    function_args = json.loads(tool_call.function.arguments)

                    try:
                        function_response = function_to_call(user=user, **function_args)  # Call function, manually add in 'user' so ChatGPT doesn't mess up which user is calling the function
                    except Exception as e:
                        function_response = f"Error: {e}"

                    chat.messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )  # extend conversation with function response

                response = chat.get_response_and_add_to_history()

        chat.save()  # TODO: Maybe only save at the end to prevent partial stuff getting saved in the database?

        # Update the system prompt with the latest reminders after processing
        chat.update_users_system_prompt_with_reminders_from_database()

        return response

    @classmethod
    def gpt_outreach():
        """
        This function gets called every hour(?) and allow ChatGPT to outreach to users based on their reminders
        """
        pass
