import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Obtén las variables de entorno
client_id = os.environ["AZURE_CLIENT_ID"]
client_secret = os.environ["AZURE_CLIENT_SECRET"]
tenant_id = os.environ["AZURE_TENANT_ID"]
vault_url = "https://credentials.vault.azure.net"  # Reemplaza con la URL real de tu Key Vault

# Crea las credenciales utilizando DefaultAzureCredential
credential = DefaultAzureCredential(
    client_id=client_id,
    client_secret=client_secret,
    tenant_id=tenant_id
)

# Crea el cliente de SecretClient
secret_client = SecretClient(vault_url=vault_url, credential=credential)

# Nombre del secreto a recuperar
secret_name = "PAT"

# Recupera el valor del secreto
retrieved_secret = secret_client.get_secret(secret_name)
secret_value = retrieved_secret.value

print(f"El valor del secreto '{secret_name}' es: {secret_value}")
