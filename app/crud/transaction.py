from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Transaction
from app.schemas.transaction import TransactionCreate

def create_transaction(db: Session, transaction: TransactionCreate) -> Transaction:
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def read_transactions_by_user(db: Session,user_id: str) -> List[Transaction]:
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()

def read_transactions_by_institution(db: Session,user_id: str, institution_id: str) -> List[Transaction]:
    return db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.institution_id == institution_id
    ).all()

def read_transactions_by_account(db: Session, user_id: str, institution_id: str, account_id: str) -> List[
    Transaction]:
    return db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.institution_id == institution_id,
        Transaction.account_id == account_id
    ).all()

def get_transaction(db: Session, user_id: str, institution_id: str, account_id: str, transaction_id: str):
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id,
        Transaction.user_id == user_id,
        Transaction.institution_id == institution_id,
        Transaction.account_id == account_id
    ).first()
    return transaction

def delete_transaction(db:Session, user_id: str, institution_id:str, transaction_id:str):
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id,
        Transaction.user_id == user_id,
        Transaction.institution_id == institution_id
    ).first()
    if not transaction:
        return None

    db.delete(transaction)
    db.commit()
    return {"detail": f"Transaction {transaction_id} deleted."}


