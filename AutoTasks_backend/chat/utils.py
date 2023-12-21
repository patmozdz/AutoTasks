from openai import OpenAI
from AutoTasks_backend.chat.secrets_manager import OPENAI_API_KEY
from user.models import User
from .models import Chat
from reminders.models import Reminder


GPT_MODEL = "gpt-4-vision-preview"
client = OpenAI(api_key=OPENAI_API_KEY, max_retries=3)
SYSTEM_MESSAGE = """You are part of a task manager application.
Assist the user in creating, updating, and deleting tasks.
Feel free to ask questions to clarify the user's intent, as long as it's short. Below is a list of all the user's reminders, with the first one being the format:"""


def chat_completion_from_sms(user: User, body: str):
    try:
        # Query the database for a Chat object associated with the user
        chat = Chat.objects.filter(user=user).first()

        # If a Chat object exists, append a new message to the messages list in the chat_object
        if chat:
            chat.chat_object['messages'].append({"role": "user", "content": body})
            chat.save()
        else:
            # If a Chat object does not exist, create a new one
            starter_messages = [
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": body},
            ]
            chat = Chat(user=user, chat_object={'messages': starter_messages})
            chat.save()

        # Update the system prompt with the latest reminders before processing
        update_system_prompt(user)

        # Call the API method with the arguments  ## ADD TOOL PARAMETER
        user_message_log = chat.chat_object['messages']
        response = client.chat.completions.create(messages=user_message_log, model=GPT_MODEL)

        # Update the chat object in the database
        chat.chat_object = response
        chat.save()

        # Update the system prompt with the latest reminders after processing
        update_system_prompt(user)

        return response

    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")

        return e


def update_system_prompt(user):
    try:
        # Fetch reminders from the database for the given user
        reminders = Reminder.objects.filter(user=user)

        # Format each reminder as a string and append it to the reminder_list
        reminder_list = ["Reminder(reminder_id, title, description, reminder_time, recurring_interval, urgency)"]  # Example format
        for reminder in reminders:
            formatted_reminder = f"Reminder({reminder.id}, '{reminder.title}', '{reminder.description}', '{reminder.reminder_time}', '{reminder.recurring_interval}', '{reminder.urgency}')"
            reminder_list.append(formatted_reminder)

        # Join all formatted reminders into a single string
        reminders_string = "\n".join(reminder_list)

        # Update the system prompt with the new reminders
        updated_system_message = SYSTEM_MESSAGE + "\n" + reminders_string

        # Fetch the Chat object for the user
        chat = Chat.objects.filter(user=user).first()
        if chat:
            # Update the first message (system message) in chat_object. Can change to a a for loop to find system message if system message isn't always at start
            if chat.chat_object['messages'] and chat.chat_object['messages'][0]['role'] == 'system':
                chat.chat_object['messages'][0]['content'] = updated_system_message
                chat.save()
            else:
                print("No system message found in the chat object.")
            # Save the updated chat object back to the database
            chat.save()

    except Exception as e:
        print("Error updating system prompt in chat object")
        print(f"Exception: {e}")


chat_completion = chat_completion_from_sms(messages_temp)
print(chat_completion)

tools = [
    {
        "type": "function",
        "function": {
            "name": "create_reminder",
            "description": "Creates a new reminder",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the reminder"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the reminder"
                    },
                    "reminder_time": {
                        "type": "string",
                        "description": "Time for the reminder in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
                    },
                    "recurring_interval": {
                        "type": "integer",
                        "description": "Interval for recurring reminders in minutes, if applicable",
                        "minimum": 1
                    },
                    "urgency": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5],
                        "description": "Urgency level of the reminder (1 to 5)"
                    }
                },
                "required": ["title", "description", "reminder_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_reminder",
            "description": "Edits an existing reminder",
            "parameters": {
                "type": "object",
                "properties": {
                    "reminder_id": {
                        "type": "integer",
                        "description": "ID of the reminder to edit"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title of the reminder"
                    },
                    "description": {
                        "type": "string",
                        "description": "New detailed description of the reminder"
                    },
                    "reminder_time": {
                        "type": "string",
                        "description": "New time for the reminder in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
                    },
                    "recurring_interval": {
                        "type": "integer",
                        "description": "New interval for recurring reminders in minutes, if applicable",
                        "minimum": 1
                    },
                    "urgency": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5],
                        "description": "New urgency level of the reminder (1 to 5)"
                    }
                },
                "required": ["reminder_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_reminder",
            "description": "Deletes an existing reminder",
            "parameters": {
                "type": "object",
                "properties": {
                    "reminder_id": {
                        "type": "integer",
                        "description": "ID of the reminder to delete"
                    }
                },
                "required": ["reminder_id"]
            }
        }
    }
]



tools = [
    {
        "type": "function",
        "function": {
            "name": "create_reminder",
            "description": "creates a new reminder",
            "parameters": {
                "type": "string",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_n_day_weather_forecast",
            "description": "Get an N-day weather forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast",
                    }
                },
                "required": ["location", "format", "num_days"]
            },
        }
    },
]