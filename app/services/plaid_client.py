# services/plaid_client.py

from plaid.api import plaid_api
from plaid import Configuration, ApiClient
from app.config import settings

configuration = Configuration(
    host=f"https://{settings.plaid_env}.plaid.com",
    api_key={
        "clientId": settings.plaid_client_id,
        "secret": settings.plaid_secret,
        "environment": settings.plaid_env
    }
)

api_client = ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

print("Client ID:", settings.plaid_client_id)

