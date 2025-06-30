from fastapi import APIRouter
from app.services.plaid_client import plaid_client

from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

router = APIRouter()

@router.get("/")
# @router.get("/")：是装饰器，告诉 FastAPI：
# 当访问这个子路由的 / 路径时，调用下面这个函数。
def create_link_token():
    request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(
            client_user_id="user-123"
        ),
        client_name="Fin Aggregator",
        products=[Products("auth"), Products("transactions")],
        country_codes=[CountryCode('US')],
        language="en"
    )

    response = plaid_client.link_token_create(request)
    return {"link_token": response["link_token"]}









