from fastapi import APIRouter, HTTPException
from app.services.plaid_client import plaid_client
import json
from plaid.model.accounts_get_request import AccountsGetRequest
from colorama import Fore, Style, init
init(autoreset=True)

from rich import print_json
from fastapi.encoders import jsonable_encoder

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
        print("❌ Error reading file:", e)
        raise HTTPException(status_code = 500, detail = "Failed to to read saved token")

    raise HTTPException(status_code=404, detail="Token for user not found")


@router.get("/")
def get_accounts():
    user_id = "demo_user" #假设当前是这个测试用户
    list_acc_token = get_saved_token(user_id)

    try:
        per_insti_result = []
        if list_acc_token is not None:
            for access_token in list_acc_token:
                #prepare the request object
                request_token = AccountsGetRequest(access_token=access_token)
                print(Fore.LIGHTYELLOW_EX + "responses: ", request_token)

                acct_info = plaid_client.accounts_get(request_token).to_dict()

                item_info = acct_info.get("item",{})
                institution_id = item_info.get("institution_id")
                institution_name = item_info.get("institution_name")

                # 提取信息简化返回
                accounts = []
                for acct in acct_info.get("accounts", []):
                    accounts.append({
                        "account_id": acct.get("account_id"),
                        "name": acct.get("name"),
                        "type": acct.get("type"),
                        "subtype": acct.get("subtype"),
                        "official_name": acct.get("official_name"),
                        "balance": float(acct.get("balances", {}).get("available", 0.0))
                    })

                per_insti_data = {
                    "institution_id": institution_id,
                    "institution_name": institution_name,
                    "accounts": accounts
                }
                per_insti_result.append(per_insti_data)

            send_front_end = {
                "user_id": user_id,
                "user_data": per_insti_result
            }
            print_json(data=jsonable_encoder(send_front_end))
            return send_front_end

        else:
            return {}

    except Exception as e:
        print(Fore.LIGHTRED_EX + "❌ Error reading file 1111:",e)
        raise HTTPException(status_code=500, detail=f"Failed to fetch accounts: {str(e)}")



