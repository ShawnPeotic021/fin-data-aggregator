from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.routes.exchange_token import router
from app.schemas.account import AccountRead
from app.schemas.user import UserCreate, UserRead
from app.crud import user as crud_user
from app.dependencies import get_db

router = APIRouter()

@router.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud_user.create_user(db, user)

@router.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user= crud_user.get_user(db,user_id)
    if db_user is None:
        raise HTTPException(status_code= 404, detail="User not found")
    return db_user

@router.put("/users/{user_id}", response_model = UserRead)
def update_user(user_id:str, token:str, db:Session = Depends(get_db)):
    return crud_user.update_user_access_token(db, user_id, token)

@router.delete("/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    return crud_user.delete_user(db, user_id)