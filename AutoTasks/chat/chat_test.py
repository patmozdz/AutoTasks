# import the OpenAI Python library for calling the OpenAI API
from openai import OpenAI
from AutoTasks.chat.secrets_manager import OPENAI_API_KEY
from tenacity import retry, wait_random_exponential, stop_after_attempt


GPT_MODEL = "gpt-4-vision-preview"
client = OpenAI(api_key=OPENAI_API_KEY)
messages_temp = [
        {
            "role": "user",
            "content": "Say this is a test",
        }
]


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages: dict, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        # Temporarily while tools are not implemented
        args = {
            "messages": messages,
            "model": model,
        }

        # Conditionally include the 'tools' parameter
        if tools is not None:
            args["tools"] = tools

        # Call the API method with the arguments
        response = client.chat.completions.create(**args)

        return response

    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")

        return e


chat_completion = chat_completion_request(messages_temp)
print(chat_completion)


# Example tools:
# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_current_weather",
#             "description": "Get the current weather",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "location": {
#                         "type": "string",
#                         "description": "The city and state, e.g. San Francisco, CA",
#                     },
#                     "format": {
#                         "type": "string",
#                         "enum": ["celsius", "fahrenheit"],
#                         "description": "The temperature unit to use. Infer this from the users location.",
#                     },
#                 },
#                 "required": ["location", "format"],
#             },
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_n_day_weather_forecast",
#             "description": "Get an N-day weather forecast",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "location": {
#                         "type": "string",
#                         "description": "The city and state, e.g. San Francisco, CA",
#                     },
#                     "format": {
#                         "type": "string",
#                         "enum": ["celsius", "fahrenheit"],
#                         "description": "The temperature unit to use. Infer this from the users location.",
#                     },
#                     "num_days": {
#                         "type": "integer",
#                         "description": "The number of days to forecast",
#                     }
#                 },
#                 "required": ["location", "format", "num_days"]
#             },
#         }
#     },
# ]