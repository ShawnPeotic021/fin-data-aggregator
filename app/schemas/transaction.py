from pydantic import BaseModel
from typing import Optional

class TransactionBase(BaseModel):
    transaction_id: str
    account_id: str
    amount: float
    authorized_date: str
    category: str
    merchant: Optional[str] = None
    iso_currency_code: str
    logo: Optional[str] = None
    user_id: str
    institution_id: str
    institution_name:str

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    model_config = {
        "from_attributes": True
    }
