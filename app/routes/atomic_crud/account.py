from fastapi import APIRouter,HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.crud import account
from app.dependencies import get_db
from app.models import Institution
from app.schemas.account import AccountRead, AccountCreate

router = APIRouter()

@router.post("/accounts",response_model = AccountRead)
def create_account(acct: AccountCreate, db: Session = Depends(get_db)):
    return account.create_account(db,acct)

@router.get("/accounts/{user_id}", response_model=list[AccountRead])
def read_accounts_by_user(user_id: str, db: Session = Depends(get_db)):
    acct = account.get_accounts_by_user(db,user_id)
    if not acct:
        raise HTTPException(status_code=404, detail="Accounts not found.")
    return acct

@router.get("/accounts/{user_id}/{insitution_id}", response_model= list[AccountRead])
def read_accounts_by_institution(user_id:str, institution_id:str, db: Session = Depends(get_db)):
    acct = account.get_accounts_by_institution(db,user_id,institution_id)
    if not acct:
        raise HTTPException(status_code = 404, detail = "Accounts not found.")
    return acct

@router.get("/accounts/{user_id}/{institution_id}/{account_id}", response_model= AccountRead)
def get_account(user_id:str, institution_id:str, account_id: str, db: Session = Depends(get_db)):
    acct = account.get_account(db,user_id,institution_id,account_id)
    if not acct:
        raise HTTPException(status_code = 404, detail = "Account not found.")
    return acct

@router.delete("/accounts/{user_id}/{institution_id}/{account_id}")
def delete_account (account_id: str, db: Session = Depends(get_db)):
    result = account.delete_account(db, account_id)
    if not result:
        raise HTTPException(status_code = 404, detail = "Account not found.")
    return result

