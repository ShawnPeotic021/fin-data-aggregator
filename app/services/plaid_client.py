# services/plaid_client.py
from datetime import datetime, timedelta

from fastapi import HTTPException
from plaid.api import plaid_api
from plaid import Configuration, ApiClient
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Institution

#initialize plaid client
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


#  based on user_id, retrieve access token
def get_access_tokens_by_user(db: Session, user_id: str):
    institutions = db.query(Institution).filter(Institution.user_id == user_id).all()
    if not institutions:
        raise HTTPException(status_code=404, detail="No tokens found for user.")
    return [
        {
            "access_token": inst.access_token,
            "item_id": inst.item_id,
            "institution_id": inst.institution_id,
            "institution_name": inst.institution_name
        }
        for inst in institutions
    ]


# tidy up transactions
def tidy_transactions(raw_transactions):
    result = []
    for trans in raw_transactions:
        result.append({
            "transaction_id": trans.get("transaction_id"),
            "account_id": trans.get("account_id"),
            "account_owner": trans.get("account_owner"),
            "amount": trans.get("amount"),
            "authorized_date": trans.get("authorized_date").isoformat() if trans.get("authorized_date") else None,
            "authorized_datetime": trans.get("authorized_datetime"),
            "category": trans.get("personal_finance_category", {}).get("primary"),
            "merchant": trans.get("merchant_name"),
            "iso_currency_code": trans.get("iso_currency_code"),
            "logo": trans.get("logo_url")
        })
    return result


# main function: retrieve nested user-data structure from Plaid
def call_plaid_and_format(user_id: str, db: Session):
    try:
        inst_tokens = get_access_tokens_by_user(db, user_id)
        per_insti_result = []

        for item in inst_tokens:
            access_token = item["access_token"]
            item_id = item["item_id"]
            institution_id = item["institution_id"]
            institution_name = item["institution_name"]

            # get transactions
            end_date = datetime.today().date()
            start_date = end_date - timedelta(days=30)

            trans_request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date,
                options=TransactionsGetRequestOptions(count=30)
            )
            response = plaid_client.transactions_get(trans_request).to_dict()
            transactions = response.get("transactions", [])
            ready_transactions = tidy_transactions(transactions)

            # get accounts
            account_request = AccountsGetRequest(access_token=access_token)
            account_info = plaid_client.accounts_get(account_request).to_dict()

            accounts = []
            for acct in account_info.get("accounts", []):
                per_acct_trans = [t for t in ready_transactions if t["account_id"] == acct["account_id"]]
                accounts.append({
                    "account_id": acct.get("account_id"),
                    "name": acct.get("name"),
                    "type": acct.get("type"),
                    "subtype": acct.get("subtype"),
                    "official_name": acct.get("official_name"),
                    "balance": float(acct.get("balances", {}).get("available", 0.0)),
                    "institution_id": institution_id,
                    "institution_name": institution_name,
                    "transactions": per_acct_trans
                })

            per_insti_result.append({
                "institution_id": institution_id,
                "institution_name": institution_name,
                "accounts": accounts,
                "access_token": access_token,
                "item_id":  item_id
            })

        return {
            "user_id": user_id,
            "user_data": per_insti_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plaid sync failed: {str(e)}")