from openai import OpenAI
from AutoTasks_backend.chat.secrets_manager import OPENAI_API_KEY
from user.models import User
from .models import Chat


GPT_MODEL = "gpt-4-vision-preview"
client = OpenAI(api_key=OPENAI_API_KEY, max_retries=3)
SYSTEM_MESSAGE = """You are part of a task manager application.
Assist the user in creating, updating, and deleting tasks.
Feel free to ask questions to clarify the user's intent, as long as it's short."""


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

        # Call the API method with the arguments  ## ADD TOOL PARAMETER
        user_message_log = chat.chat_object['messages']
        response = client.chat.completions.create(messages=user_message_log, model=GPT_MODEL)

        # Update the chat object in the database
        chat.chat_object = response
        chat.save()

        return response

    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")

        return e


chat_completion = chat_completion_from_sms(messages_temp)
print(chat_completion)
