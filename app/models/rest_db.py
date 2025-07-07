# app/models/reset_db.py

from app.database import Base, engine

# ✅ 手动导入所有模型，确保表都注册到 Base.metadata 中
from app.models.user import User
from app.models.institution import Institution
from app.models.account import Account
from app.models.transaction import Transaction

if __name__ == "__main__":
    print("⚠️ Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped.")

    print("🔧 Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully.")
