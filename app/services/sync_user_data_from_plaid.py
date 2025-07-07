from colorama import Fore
from sqlalchemy.orm import Session
from app.schemas.account import AccountCreate
from app.schemas.transaction import TransactionCreate
from app.models import Institution
from app.crud import account as account_crud
from app.crud import transaction as transaction_crud
from sqlalchemy.orm import Session

from app.services.user_data import delete_user_data


def add_institution_data(
        db: Session, user_id: str,
        institution_id: str,
        institution_name: str,
        accounts: list[dict],
        access_token: str,
        item_id: str
        ):
    # Add the institution if it doesn't already exist for the user
    existing = db.query(Institution).filter(
        Institution.institution_id == institution_id,
        Institution.user_id == user_id
    ).first()
    if not existing:
        db.add(Institution(
            institution_id=institution_id,
            institution_name=institution_name,
            user_id=user_id,
            access_token = access_token,
            item_id = item_id
        ))
        db.commit()
    print(Fore.LIGHTBLUE_EX + "a new institution is added successfully!")

    # Add each account and its associated transactions
    for acct in accounts:
        account_data = AccountCreate(
            account_id=acct["account_id"],
            name=acct["name"],
            type=acct["type"],
            subtype=acct["subtype"],
            official_name=acct.get("official_name"),
            balance=acct.get("balance", 0.0),
            user_id=user_id,
            institution_id=institution_id,
            institution_name = institution_name
        )
        account_crud.create_account(db, account_data)
        print(Fore.LIGHTYELLOW_EX + "a new account is added successfully!")

        for txn in acct.get("transactions", []):
            txn_data = TransactionCreate(
                transaction_id=txn["transaction_id"],
                account_id=acct["account_id"],
                amount=txn["amount"],
                authorized_date=txn["authorized_date"],
                category=txn["category"],
                merchant=txn.get("merchant"),
                logo=txn.get("logo"),
                iso_currency_code=txn["iso_currency_code"],
                account_owner=txn.get("account_owner"),
                authorized_datetime=txn.get("authorized_datetime"),
                user_id=user_id,
                institution_id=institution_id,
                institution_name = institution_name
            )
            transaction_crud.create_transaction(db, txn_data)
            print(Fore.LIGHTMAGENTA_EX + "a new transaction is added successfully!")

    return {"detail": f"Institution {institution_name} and its data added for user {user_id}."}


def add_account_data(db: Session, user_id: str, institution_id: str, account_dict: dict):
    # Add a single account and its associated transactions
    account_data = AccountCreate(
        account_id=account_dict["account_id"],
        name=account_dict["name"],
        type=account_dict["type"],
        subtype=account_dict["subtype"],
        official_name=account_dict.get("official_name"),
        balance=account_dict.get("balance", 0.0),
        user_id=user_id,
        institution_id=institution_id
    )
    account_crud.create_account(db, account_data)

    for txn in account_dict.get("transactions", []):
        txn_data = TransactionCreate(
            transaction_id=txn["transaction_id"],
            account_id=account_dict["account_id"],
            amount=txn["amount"],
            authorized_date=txn["authorized_date"],
            category=txn["category"],
            merchant=txn.get("merchant"),
            logo=txn.get("logo"),
            iso_currency_code=txn["iso_currency_code"],
            account_owner=txn.get("account_owner"),
            authorized_datetime=txn.get("authorized_datetime"),
            user_id=user_id,
            institution_id=institution_id
        )
        transaction_crud.create_transaction(db, txn_data)

    return {"detail": f"Account {account_dict['account_id']} and its transactions added."}


def sync_user_data_from_plaid(db: Session, user_id: str, plaid_user_data: dict):
    """
    Perform full synchronization:
    Step 1 - Delete old user data
    Step 2 - Insert all institutions, accounts, and transactions from Plaid

    Args:
        user_id (str): The ID of the user
        plaid_user_data (dict): The parsed structure from Plaid (containing institutions and accounts)
    """
    # Step 1: 删除旧数据
    delete_user_data(db, user_id)

    # Step 2: 遍历所有 institution + account + transaction
    for inst in plaid_user_data.get("user_data", []):
        institution_id = inst.get("accounts", [{}])[0].get("institution_id")  # 从第一个账户提取
        institution_name = inst.get("institution_name")
        access_token = inst.get("access_token")
        item_id = inst.get("item_id")

        accounts = inst.get("accounts", [])

        if institution_id and accounts:
            add_institution_data(
                db=db,
                user_id=user_id,
                institution_id=institution_id,
                institution_name=institution_name,
                accounts=accounts,
                item_id = item_id,
                access_token = access_token
            )

    return {"detail": f"User {user_id} data synchronized from Plaid."}
