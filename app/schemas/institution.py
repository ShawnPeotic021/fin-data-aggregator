from typing import Optional

from pydantic import BaseModel

class InstitutionBase(BaseModel):
    institution_id: str
    institution_name: str
    user_id: str

class InstitutionCreate(InstitutionBase):
    access_token: str
    item_id: str

class InstitutionUpdate(BaseModel):
    institution_name: Optional[str] = None
    access_token: Optional[str] = None
    item_id: Optional[str] = None

class InstitutionRead(InstitutionBase):
    model_config = {
        "from_attributes": True
    }

