from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserCreate


def create_user(db:Session, user:UserCreate):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db:Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()

def get_all_users(db:Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

def update_user_access_token(db: Session, user_id: str, new_token: str):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.access_token = new_token
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: str):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user