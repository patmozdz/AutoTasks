from azure.identity import AzureCliCredential
from azure.keyvault.secrets import SecretClient


key_vault_uri = 'https://autotasksvault.vault.azure.net/'
credential = AzureCliCredential()
client = SecretClient(vault_url=key_vault_uri, credential=credential)

OPENAI_API_KEY = client.get_secret("OPENAIAPIKEY").value
