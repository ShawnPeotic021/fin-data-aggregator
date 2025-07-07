from typing import List

from pydantic import BaseModel
from app.schemas.account import AccountRead
from app.schemas.transaction import TransactionRead

class AccountWithTransactions(AccountRead):
    institution_id: str               #
    institution_name: str             # for presentation purposes, not stored in DB

    transactions: List[TransactionRead]
    model_config = {
        "from_attributes": True
    }

class InstitutionWithAccounts(BaseModel):
    institution_id: str
    institution_name: str
    accounts: List[AccountWithTransactions]

    model_config = {
        "from_attributes": True
    }

class UserDataResponse(BaseModel):
    user_id : str
    user_data: List[InstitutionWithAccounts]

    model_config = {
        "from_attributes": True
    }



