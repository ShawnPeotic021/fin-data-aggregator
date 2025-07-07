import json
from cgitb import reset
from datetime import datetime, timedelta
from http.client import responses

from colorama import Fore
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from rich import print_json

from app.services.plaid_client import plaid_client

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
        print("Error 1: ",e)
        raise HTTPException(status_code=500, detail="Fail to read saved token.")

    raise HTTPException(status_code=404, detail="Token for user not found")


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

@router.get("/")
def get_user_data():
    try:
        user_id = "demo_user"
        list_acc_token = get_saved_token(user_id)
        #account data requests + transac data requests
        per_insti_result = []
        if list_acc_token is not None:
            for access_token in list_acc_token:

                #transactions
                end_date = datetime.today().date()
                start_date = end_date - timedelta(days=30)

                #prepare transac request object
                trans_request = TransactionsGetRequest(
                    access_token = access_token,
                    start_date = start_date,
                    end_date= end_date,
                    options = TransactionsGetRequestOptions(count = 30)
                )
                #Call Plaid API
                response = plaid_client.transactions_get(trans_request).to_dict()

                #Extract transac
                transactions = response.get("transactions",[])

                ready_transactions = tidy_transactions(transactions)
                print(Fore.LIGHTGREEN_EX + "transactions")


                #accounts: prepare token object
                request_object =  AccountsGetRequest(access_token = access_token)
                print(Fore.LIGHTYELLOW_EX + "prepare token_object: ",request_object)

                account_info = plaid_client.accounts_get(request_object).to_dict()
                item = account_info.get("item",{})
                institution_id =  item.get("institution_id",{})
                institution_name = item.get("institution_name",{})
                print(Fore.LIGHTGREEN_EX+institution_name)

                accounts = []
                for acct in account_info.get("accounts",[]):
                    per_acct_trans = []
                    for trans in ready_transactions:
                        if acct["account_id"] == trans["account_id"]:
                            per_acct_trans.append(trans)
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

                print(Fore.LIGHTGREEN_EX + "accounts")

                per_insti_data = {
                    "institution_id": institution_id,
                    "institution_name": institution_name,
                    "accounts": accounts
                }
                per_insti_result.append(per_insti_data)
                print(Fore.LIGHTGREEN_EX + "per institution")


        send_front_end ={
            "user_id":user_id,
            "user_data": per_insti_result
        }
        print_json(data=jsonable_encoder(send_front_end))
        return send_front_end

    except Exception as e:
        print("Error 3: ", e)
        raise HTTPException(status_code=500, detail=str(e))


