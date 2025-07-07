from pydantic import BaseModel

class UserBase(BaseModel):
    user_id:str

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    model_config = {
        "from_attributes": True
    }



