# app/main.py
from fastapi import FastAPI
from app.routes import connect, exchange_token, accounts, transactions,user_data
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 添加 CORS 允许
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境可以允许所有源，生产应改成特定前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#register routers
app.include_router(connect.router, prefix= "/connect")
app.include_router(exchange_token.router, prefix="/exchange-token")
app.include_router(accounts.router, prefix = "/accounts")
app.include_router(transactions.router, prefix ="/transactions")
app.include_router(user_data.router, prefix ="/user-data")

# App entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)












