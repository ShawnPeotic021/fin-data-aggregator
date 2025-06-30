from fastapi import APIRouter, Body
from app.services.plaid_client import plaid_client
from fastapi import APIRouter, HTTPException, Request
from app.config import settings
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from app.services.storage import save_token

from plaid.model.item_get_request import ItemGetRequest
# 还需调用 institutions_get_by_id 获取 institution_name（可选）
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.country_code import CountryCode

from rich import print_json
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.post("/")
async def exchange_token(request: Request):
    try:
        # 从前端请求中提取 public_token
        body = await request.json()
        public_token = body.get("public_token")
        print("\npublic_token received:", public_token)
        print("\n")

        if not public_token:
            raise HTTPException(status_code=400, detail = "Missing public_token")

        print("Plaid client initialized with:", settings.plaid_client_id)
        print("\n")

        # 创建请求对象
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        # 使用 Plaid SDK 交换 token
        response = plaid_client.item_public_token_exchange(request)
        print(response)

        access_token = response["access_token"]
        item_id = response["item_id"]
        print("access_token Received: ", access_token)

        # 使用 access_token 获取 item 信息
        item_req = ItemGetRequest(access_token=access_token)
        item_resp = plaid_client.item_get(item_req)

        # 使用 access_token 获取institution_id
        institution_id = item_resp["item"]["institution_id"]
#
        #使用institution_id 获取 institution_name
        inst_req = InstitutionsGetByIdRequest(
            institution_id=institution_id,
            country_codes=[CountryCode('US')]
        )
        inst_resp = plaid_client.institutions_get_by_id(inst_req)
        institution_name = inst_resp["institution"]["name"]

        save_token("demo_user",access_token, item_id,institution_id,institution_name)

        return {
            # 生产环境建议不返回 token 给前端
            "access_token": "Access token stored",
            "item_id": item_id
        }

    except Exception as e:
        print("❌ Plaid token exchange error:", str(e))
        raise HTTPException(status_code=500, detail = f"Token exchange failed: {str(e)}")



