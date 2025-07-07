from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    plaid_client_id: str
    plaid_secret: str
    plaid_env: str
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()


