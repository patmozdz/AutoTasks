from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from AutoTasks_backend import secrets_manager
import openai
from reminders import Reminder
import json
from user.models import User
import gpt_tools


class Chat(models.Model):
    STARTER_SYSTEM_MESSAGE = """You are part of a task manager application.
Assist the user in creating, updating, and deleting tasks.
Feel free to ask questions to clarify the user's intent, as long as it's short. Below is a list of all the user's reminders, with the first one being the format:"""
    GPT_MODEL = "gpt-4-vision-preview"
    client = openai.Client(secrets_manager.OPENAI_API_KEY, max_retries=3, max_tokens=150)  # TODO: Fix max tokens

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat'
    )
    response_history = JSONField(default=list)  # Store an array of chat completion objects
    messages = JSONField(default=list)  # Store an array of messages
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

            # Update the system prompt with the new reminders
            updated_system_message = self.SYSTEM_MESSAGE + "\n" + reminders_string

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
        response = self.client.chat.completions.create(messages=self.messages, model=self.GPT_MODEL, tools=self.tools)
        self.response_history.append(response)
        return response

    @classmethod
    def create_with_starter_messages(cls, user, starter_message):
        starter_messages = [
            {"role": "system", "content": cls.STARTER_SYSTEM_MESSAGE},
            {"role": "user", "content": starter_message},
        ]
        chat = cls(user=user, messages=starter_messages)

        return chat

    @classmethod
    def chat_completion_from_sms(cls, user: User, body: str):
        try:
            # Query the database for a Chat object associated with the user
            chat = cls.objects.filter(user=user).first()

            # If a Chat object exists, append a new message to the messages list in the chat_object
            if chat:
                chat.messages.append({"role": "user", "content": body})
                chat.save()
            else:
                # If a Chat object does not exist, create a new one
                chat = Chat.create_with_starter_messages(user, body)  # chat.chat_object_history is still blank, TODO: append when chat_completion is called
                chat.save()

            # Update the system prompt with the latest reminders before processing
            chat.update_system_prompt_with_reminders_from_database(user)

            # Call the API method with the arguments
            response = chat.get_response_and_add_to_history()
            # TODO: Call execute_while_gpt_calls_functions(response) here
            while response.choices[0].message.tool_calls:
                response_message = response.choices[0].message
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
                    chat.messages.append(response_message)  # extend conversation with reply
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
            chat.update_system_prompt_with_reminders_from_database(user)

            return response

        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")

            return e

    @classmethod
    def gpt_outreach():
        """
        This function gets called every hour(?) and allow ChatGPT to outreach to users based on their reminders
        """
        pass