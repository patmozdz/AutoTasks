from azure.identity import AzureCliCredential
from azure.keyvault.secrets import SecretClient
import os

# For production:
# key_vault_uri = 'https://autotasksvault.vault.azure.net/'
# credential = AzureCliCredential()
# client = SecretClient(vault_url=key_vault_uri, credential=credential)

# # OpenAI
# OPENAI_API_KEY = client.get_secret("OPENAI-API-KEY").value

# # Twilio
# # Twilio Account SID and Auth Token can be found at twilio.com/console
# TWILIO_ACCOUNT_SID = client.get_secret("TWILIO-ACCOUNT-SID").value
# TWILIO_AUTH_TOKEN = client.get_secret("TWILIO-AUTH-TOKEN").value

# For development:
# OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Twilio
# Twilio Account SID and Auth Token can be found at twilio.com/console
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
