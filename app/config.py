from pydoc import stripid
from pydantic import BaseSettings

# this is to validate that all environment variables exist and that they are set appropriately

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()