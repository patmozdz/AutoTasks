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
from zoneinfo import ZoneInfo

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

            # TODO: Maybe use the user's timezone instead of hardcoding it to Chicago
            timezone = ZoneInfo('America/Chicago')
            #  the system prompt with the new reminders, also  with current datetime
            dated_system_message = "Current datetime: " + str(datetime.now(timezone)) + "\n" + self.SYSTEM_MESSAGE + "\n" + reminders_string

            #  the first message (system message) in messages. Can change to a a for loop to find system message if system message isn't always first message
            if self.messages[0]['role'] == 'system':
                self.messages[0]['content'] = dated_system_message
                self.save()  # TODO: Maybe only save at the end to prevent partial stuff getting saved in the database?
            else:
                print("No system message found in the chat object.")

        except Exception as e:
            print("Error updating system prompt in chat object")
            print(f"Exception: {e}")

    def get_response_and_add_to_history(self, tool_choice='auto'):  # Can be given a specific tool_choice to force the model to use a specific function
        self.update_users_system_prompt_with_reminders_from_database()

        assert self.messages[0]['role'] == 'system', "First message in chat object is not a system message."
        messages_sent = [self.messages[0]] + self.messages[-5:]  # Only use the system prompt and 5 most recent messages to avoid using too many tokens
        # TODO: Adjust above. Maybe 10 messages?

        response = self.client.chat.completions.create(
            messages=messages_sent,
            model=self.GPT_MODEL,
            tools=self.tools,
            tool_choice='auto',
            max_tokens=150,
            )  # TODO: Adjust max_tokens

        response_message_dict = response.model_dump(exclude_unset=True)['choices'][0]['message']
        self.messages.append(response_message_dict)  # extend conversation with reply
        full_response_in_dict = response.model_dump(exclude_unset=True)  # Convert to dict so it can be converted to JSON for database
        self.response_history.append(full_response_in_dict)
        self.save()

        self.update_users_system_prompt_with_reminders_from_database()
        return response

    @classmethod
    def create_with_starter_messages(cls, user, first_message):
        starter_messages = [
            {"role": "system", "content": cls.SYSTEM_MESSAGE},
            {"role": "user", "content": first_message},
        ]
        chat = cls(user=user, messages=starter_messages)

        return chat

    @classmethod  # Class method so that calling function does't need to handle the Chat instance's lifecycle
    def chat_completion_from_sms_body(cls, user: User, body: str):
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

        # Call the API method with the arguments
        response = chat.get_and_save_response_with_tools_options()

        return response

    @classmethod
    def chat_completion_from_reminder(cls, user: User, reminder: Reminder):  # TODO: Might get messed up if you're actively chatting with ChatGPT while a reminder is triggered
        """
        This function gets triggered when a reminder time has passed.
        """
        assert reminder.user == user, "Reminder user does not match chat user."

        chat = cls.objects.filter(user=user).first()
        if not reminder.notified:  # Treat the notification differently if the reminder was already notified before
            chat.messages.append(
                            {
                                "role": "system",
                                "content": f"The reminder with id {reminder.id} was triggered.",
                            }
                        )  # extend conversation with reminder notification
            reminder.notified = True
            reminder.save()
            chat.save()
        else:
            chat.messages.append(
                            {
                                "role": "system",
                                "content": f"A follow up for the reminder with id {reminder.id} was triggered.",
                            }
                        )  # extend conversation with follow up reminder notification.
            chat.save()

        response = chat.get_and_save_response_with_tools_options()
        return response

    def get_and_save_response_with_tools_options(self, tool_names: list = None):
        # Call the API method with the arguments
        response = self.get_response_and_add_to_history()

        while tool_calls := response.choices[0].message.tool_calls:
            # Check if the model wanted to call a function
            if tool_calls:
                # TODO: Handle errors

                # If tool_names is used to ensure specific functions are used, filter out available functions that don't match
                all_functions = {
                    'create_reminder': Reminder.create_reminder,
                    'edit_reminder': Reminder.edit_reminder,
                    'delete_reminder': Reminder.delete_reminder,
                }
                if tool_names:
                    available_functions = {name: function for name, function in all_functions.items() if name in tool_names}
                else:
                    available_functions = all_functions

                # Send the info for each function call and function response to the model
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = available_functions[function_name]
                    function_args = json.loads(tool_call.function.arguments)

                    try:
                        function_response = function_to_call(user=self.user, **function_args)  # Call function, manually add in 'user' so ChatGPT doesn't mess up which user is calling the function
                    except Exception as e:
                        function_response = f"Error: {e}"

                    self.messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )  # extend conversation with function response

                response = self.get_response_and_add_to_history()

        self.save()  # TODO: Maybe only save at the end to prevent partial stuff getting saved in the database?

        return response
