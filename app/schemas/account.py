from pydantic import BaseModel

class AccountBase(BaseModel):
    account_id: str
    name: str
    type: str
    subtype: str
    official_name: str
    balance: float
    institution_id: str
    institution_name:str
    user_id: str

class AccountCreate(AccountBase):
    pass

class AccountRead(AccountBase):
    model_config = {
        "from_attributes": True
    }

