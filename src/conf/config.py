from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = "sqlalchemy"
    secret_key: str = "secret_key"
    algorithm: str = "algorithms"
    mail_username: str = "mail"
    mail_password: str= "password"
    mail_from: str = "mail@gmail.com"
    mail_port: int = 3452
    mail_server: str = "postgres"
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: str = None
    cloudinary_name: str = "claud"
    cloudinary_api_key: str = "api_key"
    cloudinary_api_secret: str = "api_secret"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()