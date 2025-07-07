from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)

    institutions = relationship("Institution", back_populates="user")
    accounts = relationship("Account", back_populates="user")


