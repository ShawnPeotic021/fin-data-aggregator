import json
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta

from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

from app.services.plaid_client import plaid_client

from rich import print_json
from fastapi.encoders import jsonable_encoder

from colorama import Fore, Style, init
init(autoreset=True)


router = APIRouter()

def get_saved_token(user_id:str):
    try:
        with open("app/services/token.json","r") as f:
            data = json.load(f)
            if user_id in data:
                inst_access_token = []
                for inst in data[user_id]:
                    inst_access_token.append(inst["access_token"])
                return inst_access_token

    except Exception as e:
        print("Error 1: ", e)
        raise HTTPException(status_code=404, detail = "User not found")


def tidy_transactions(raw_transactions):
    result = []
    for trans in raw_transactions:
        result.append({
            "account_id": trans.get("account_id"),
            "account_owner": trans.get("account_owner"),
            "amount": trans.get("amount"),
            "authorized_date": trans.get("authorized_date").isoformat(),
            'authorized_datetime': trans.get('authorized_datetime'),
            "category": trans.get("personal_finance_category", {}).get("primary"),
            "merchant": trans.get("merchant_name"),
            "iso_currency_code": trans.get("iso_currency_code"),
            "logo": trans.get("logo_url")
        })
    return result

#Defines a GET route /transactions/ that will return recent transactions.
@router.get("/")
def get_transactions():
    try:
        user_id = "demo_user"
        list_acc_token = get_saved_token(user_id)

        #Date range: last 30 days
        #Specifies the transaction search window — from today going back 30 days.
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=30)

        if list_acc_token is not None:
            per_inst_transac = []
            for access_token in list_acc_token:
                #to get institution
                request_token = AccountsGetRequest(access_token=access_token)
                print(Fore.LIGHTYELLOW_EX + "responses: ", request_token)

                acct_info = plaid_client.accounts_get(request_token).to_dict()

                item_info = acct_info.get("item",{})
                institution_id = item_info.get("institution_id")
                institution_name = item_info.get("institution_name")

                trans_request = TransactionsGetRequest(
                    access_token = access_token,
                    start_date = start_date,
                    end_date = end_date,
                    options = TransactionsGetRequestOptions (count = 100)
                )

                #This is where the real API call happens.
                response = plaid_client.transactions_get(trans_request).to_dict()

                # Extract transactions§
                transactions = response.get("transactions",[])

                tidied_transaction = tidy_transactions(transactions)

                per_insti_data = {
                    "institution_id": institution_id,
                    "institution_name": institution_name,
                    "transactions": tidied_transaction
                }
                per_inst_transac.append(per_insti_data)

            send_front_end = {
                "user_id": user_id,
                "user_data":per_inst_transac
            }
            print_json(data=jsonable_encoder(send_front_end))
            return send_front_end
        else:
            return {}

    except Exception as e:
        print("Error 2: ", e)
        raise HTTPException(status_code =500, detail = str(e))







