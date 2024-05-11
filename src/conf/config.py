from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:111111@localhost:5432/abc"
    SECRET_KEY_JWT: str = "1234567890"
    ALGORITHM: str = "HS256"
    CLD_NAME: str = "dcluqr6zi"
    CLD_API_KEY: int = 218578366288237
    CLD_API_SECRET: str = "RIPZB8w29CJyB02a_lDUo0L6_Pk"
    PG_DB: str = "photo_share_db"
    PG_USER: str ="postgres"
    PG_PASSWORD: str ="567234"
    PG_PORT: int = 5432
    PG_DOMAIN: str ="localhost"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()