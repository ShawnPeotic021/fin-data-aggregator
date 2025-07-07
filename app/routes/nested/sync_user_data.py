from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.sync_user_data_from_plaid import sync_user_data_from_plaid
from app.services.plaid_client import call_plaid_and_format

router = APIRouter()

@router.post("/{user_id}", status_code=status.HTTP_200_OK)
def sync_user_data(user_id: str, db: Session = Depends(get_db)):
    plaid_data = call_plaid_and_format(user_id,db)  # 你自己调用 Plaid 并返回格式化数据
    print("🔍 access_token sample:", plaid_data["user_data"][0].get("access_token"))
    print("🔍 item_id sample:", plaid_data["user_data"][0].get("item_id"))

    return sync_user_data_from_plaid(db, user_id, plaid_data)



