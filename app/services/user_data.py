# services/user_data.py
from colorama import Fore
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import User, Institution, Account, Transaction
from app.schemas.nested import UserDataResponse, InstitutionWithAccounts, AccountWithTransactions, TransactionRead
from app.models import Transaction, Account

def get_user_data(db: Session, user_id: str) -> UserDataResponse:
    # Step 1: 查出所有该用户的账户
    accounts = db.query(Account).filter(Account.user_id == user_id).all()

    # Step 2: 按 institution_id 分组账户
    institution_map = {}
    institution_accounts = {}

    for account in accounts:
        inst_id = account.institution_id

        # 如果是第一次遇到这个 institution_id
        if inst_id not in institution_map:
            institution = db.query(Institution).filter(Institution.institution_id == inst_id).first()
            institution_map[inst_id] = institution.institution_name
            institution_accounts[inst_id] = []

        # 查该账户对应的交易
        transactions = db.query(Transaction).filter(Transaction.account_id == account.account_id).all()
        transaction_list = [
            TransactionRead(
                account_id=t.account_id,
                amount=t.amount,
                authorized_date=t.authorized_date,
                category=t.category,
                merchant=t.merchant,
                iso_currency_code=t.iso_currency_code,
                logo=t.logo
            ) for t in transactions
        ]

        # 构造账户对象（包含 institution_name 展示）
        account_data = AccountWithTransactions(
            account_id=account.account_id,
            name=account.name,
            type=account.type,
            subtype=account.subtype,
            official_name=account.official_name,
            balance=account.balance,
            institution_id=account.institution_id,
            institution_name=institution_map[inst_id],
            transactions=transaction_list
        )

        institution_accounts[inst_id].append(account_data)

    # Step 3: 构造 user_data 响应结构
    user_data = [
        InstitutionWithAccounts(
            institution_id=inst_id,
            institution_name=institution_map[inst_id],
            accounts=institution_accounts[inst_id]
        ) for inst_id in institution_accounts
    ]

    return UserDataResponse(user_id=user_id, user_data=user_data)


def delete_user_data(db: Session, user_id: str):
    # 1. delete transaction
    db.query(Transaction).filter(Transaction.user_id == user_id).delete()

    # 2. delete account
    db.query(Account).filter(Account.user_id == user_id).delete()

    # 3. delete institution
    db.query(Institution).filter(Institution.user_id == user_id).delete()

    db.commit()
    return {Fore.LIGHTGREEN_EX + "detail": f"All data for user {user_id} has been deleted."}


def delete_institution_data(db: Session, user_id: str, institution_id: str):
    # 删除所有交易
    db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.institution_id == institution_id
    ).delete()

    # 删除所有账户
    db.query(Account).filter(
        Account.user_id == user_id,
        Account.institution_id == institution_id
    ).delete()

    # 删除 institution 本身
    deleted = db.query(Institution).filter(
        Institution.user_id == user_id,
        Institution.institution_id == institution_id
    ).delete()

    db.commit()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Institution not found")

    return {"detail": f"Institution {institution_id} and all related data deleted."}

def delete_account_data(db: Session, user_id: str, institution_id: str, account_id: str):
    # 先删除交易
    db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.institution_id == institution_id,
        Transaction.account_id == account_id
    ).delete()

    # 再删除账户
    deleted = db.query(Account).filter(
        Account.user_id == user_id,
        Account.institution_id == institution_id,
        Account.account_id == account_id
    ).delete()

    db.commit()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Account not found")

    return {"detail": f"Account {account_id} and its transactions deleted."}




