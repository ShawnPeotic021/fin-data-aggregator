from sqlalchemy import Column, String, Float, Date, ForeignKey
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(String, primary_key=True)
    amount = Column(Float)
    authorized_date = Column(Date)
    category = Column(String)
    merchant = Column(String)
    iso_currency_code = Column(String)
    logo = Column(String, nullable=True)


    user_id = Column(String, ForeignKey("users.user_id"))
    institution_id =  Column(String, ForeignKey("institutions.institution_id"))
    institution_name = Column(String)
    account_id = Column(String, ForeignKey("accounts.account_id"))

