from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(String, primary_key=True)
    name = Column(String)
    type = Column(String)
    subtype = Column(String)
    official_name = Column(String)
    balance = Column(Float)

    user_id = Column(String, ForeignKey("users.user_id"))
    institution_id = Column(String, ForeignKey("institutions.institution_id"))
    institution_name = Column(String)

    user = relationship("User",back_populates = "accounts")
    institution = relationship("Institution", back_populates="accounts")