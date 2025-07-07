from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Account, Institution
from app.schemas.account import AccountCreate

def create_account(db: Session, account: AccountCreate) -> Account:
    # Convert Pydantic object (accountcreate) obtained form front end into
    # a normal python dict (model_dump), Account pass the data to SQLAlchemy's model Account, to create a db  instance
    db_account = Account(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts_by_user(db: Session, user_id: str) -> List[Account]:
    return db.query(Account).filter(Account.user_id == user_id).all()

def get_accounts_by_institution(db: Session, user_id: str, institution_id:str) -> List[Account]:
    return db.query(Account).filter(
        Account.institution_id == institution_id,
        Account.user_id == user_id
    ).all()

def get_account(db: Session, user_id: str, institution_id: str, account_id: str) -> Optional[Account]:
    return db.query(Account).filter(
        Account.institution_id == institution_id,
        Account.user_id == user_id,
        Account.account_id == account_id
    ).first()

def delete_account(db: Session, user_id:str, institution_id:str, account_id: str):
    account = db.query(Account).filter(
        Account.institution_id == institution_id,
        Account.user_id == user_id,
        Account.account_id == account_id
    ).first()
    if not account:
        return None
    db.delete(account)
    db.commit()
    return{"detail": f"Account {account_id} deleted."}
