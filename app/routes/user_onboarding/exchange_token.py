from fastapi import APIRouter, Body
from fastapi.params import Depends
from fastapi import HTTPException, Request

from sqlalchemy.orm import Session

from app.models import Institution
from app.services.plaid_client import plaid_client
from app.config import settings
from app.services.storage import save_token
from app.dependencies import get_db
from app.models.user import User

from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.item_get_request import ItemGetRequest
# 还需调用 institutions_get_by_id 获取 institution_name（可选）
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.country_code import CountryCode

from rich import print_json
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.post("/")
async def exchange_token(request: Request, db:Session = Depends(get_db)):
    try:
        # 从前端请求中提取 public_token
        body = await request.json()
        public_token = body.get("public_token")
        print("\npublic_token received:", public_token)

        if not public_token:
            raise HTTPException(status_code=400, detail = "Missing public_token")
        print("Plaid client initialized with:", settings.plaid_client_id)

        # 交换 token
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(request)
        print(response)
        access_token = response["access_token"]
        item_id = response["item_id"]
        print("access_token Received: ", access_token)


        # 获取 institution_id
        item_req = ItemGetRequest(access_token=access_token)
        item_resp = plaid_client.item_get(item_req)
        institution_id = item_resp["item"]["institution_id"]


        # 获取 institution_name
        inst_req = InstitutionsGetByIdRequest(
            institution_id=institution_id,
            country_codes=[CountryCode('US')]
        )
        inst_resp = plaid_client.institutions_get_by_id(inst_req)
        institution_name = inst_resp["institution"]["name"]

        user_id = "demo_user"  # 可替换成从 JWT 中提取的真实 user_id
        # ✅ 若用户不存在，先插入 User 表（幂等）
        existing_user = db.query(User).filter(User.user_id == user_id).first()
        if not existing_user:
            new_user = User(user_id = user_id)
            db.add(new_user)
            db.commit()

        # ✅ 插入 Institution 表（多条）
        institution = Institution(
            institution_id=institution_id,
            institution_name=institution_name,
            access_token=access_token,
            item_id=item_id,
            user_id=user_id
        )
        db.add(institution)
        db.commit()

        save_token("demo_user",access_token, item_id,institution_id,institution_name)

        return {
            # 生产环境建议不返回 token 给前端
            "access_token": "Access token stored"
        }

    except Exception as e:
        print("❌ Plaid token exchange error:", str(e))
        raise HTTPException(status_code=500, detail = f"Token exchange failed: {str(e)}")



