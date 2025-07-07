from sqlalchemy import Column, ForeignKey,String
from sqlalchemy.orm import relationship
from app.database import Base

class Institution(Base):
    __tablename__ = "institutions"
    institution_id =  Column(String, primary_key=True)
    institution_name = Column(String)
    user_id = Column(String, ForeignKey("users.user_id"))
    access_token = Column(String, nullable = False)
    item_id = Column(String, nullable=True)

    user = relationship("User", back_populates="institutions")
    accounts = relationship("Account",back_populates="institution")



