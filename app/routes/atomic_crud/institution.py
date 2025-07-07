from http.client import HTTPException
from typing import List

from fastapi import APIRouter, Depends
from fastapi.openapi.utils import status_code_ranges
from sqlalchemy.orm import Session

from app.crud.institution import create_institution, get_institutions_by_user
from app.dependencies import get_db
from app.models import Institution
from app.crud import institution

from app.schemas.institution import InstitutionCreate, InstitutionRead, InstitutionUpdate

router = APIRouter()

@router.post("/insitutions",response_model = InstitutionRead)
def create_inst(inst: InstitutionCreate, db: Session = Depends(get_db)):
    return create_institution(db, inst)

@router.get("/institutions/{user_id}", response_model = List[InstitutionRead])
def read_user_institutions(user_id:str, db: Session = Depends(get_db)):
    institutions = get_institutions_by_user(db,user_id)
    if not institutions:
        raise HTTPException (status_code = 404, detail = "No institutions found")
    return institutions

@router.get("/institutions/{institution_id}", response_model = InstitutionRead)
def get_institution(institution_id: str, db: Session = Depends(get_db)):
    inst = institution.get_institutions_by_user(db, institution_id)
    if not inst:
        raise HTTPException(status_code = 404, detail = "Institution not found.")
    return inst

@router.put("/institutions/{insititution_id}", response_model = InstitutionRead)
def update_institution(institution_id: str, updates: InstitutionUpdate, db: Session = Depends(get_db)):
    inst = institution.InstitutionUpdate(db, institution_id, updates)
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")
    return inst

@router.delete("/institutions/{insitution_id}")
def delete_institution(institution_id: str, db: Session = Depends(get_db)):
    result = institution.delete_institution(db, institution_id)
    if not result:
        raise HTTPException(status_code=404, detail="Institution not found.")
    return result




