from azure.identity import AzureCliCredential
from azure.keyvault.secrets import SecretClient
import os

# For production:
# key_vault_uri = 'https://autotasksvault.vault.azure.net/'
# credential = AzureCliCredential()
# client = SecretClient(vault_url=key_vault_uri, credential=credential)

# # OpenAI
# OPENAI_API_KEY = client.get_secret("OPENAI-API-KEY").value

# For development:
# OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


# Registration code
REGISTRATION_CODE = os.environ.get("REGISTRATION_CODE")

# Django
DJANGO_SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
INTERNAL_TOKEN = os.environ.get("INTERNAL_TOKEN")

# Discord
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DISCORD_BOT_BROKER_URL = os.environ.get("DISCORD_BOT_BROKER_URL")
