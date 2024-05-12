from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
import jose.jwt
import fastapi
import fastapi.security
import passlib.context
from sqlalchemy import select

from src.database.db import get_db
import src.database.models as models

from sqlalchemy.orm import Session

from src.tests.logger import logger


class Auth:
    HASH_CONTEXT = passlib.context.CryptContext(schemes=["bcrypt"])
    ALGORITM = "HS256"
    SECRET = "My secret key"
    oauth2_scheme = fastapi.security.OAuth2PasswordBearer("api/auth/login")

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.HASH_CONTEXT.verify(plain_password, hashed_password)

    def get_password_hash(self, plain_password):
        return self.HASH_CONTEXT.hash(plain_password)

    async def create_access_token(self, payload: dict) -> str:
        to_encode = payload.copy()
        to_encode.update({"exp": datetime.now(timezone.utc) + timedelta(minutes=15)})
        encoded_jwt = jose.jwt.encode(to_encode, self.SECRET, algorithm=self.ALGORITM)
        return encoded_jwt

    async def create_refresh_token(self, payload: dict) -> str:
        to_encode = payload.copy()
        to_encode.update({"exp": datetime.now(timezone.utc) + timedelta(days=7)})
        encoded_jwt = jose.jwt.encode(to_encode, self.SECRET, algorithm=self.ALGORITM)
        return encoded_jwt

    async def get_current_user(
        self,
        token: str = fastapi.Depends(oauth2_scheme),
        db=fastapi.Depends(get_db),
    ):
        
        credentials_exception = fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        logger.critical(credentials_exception)
        try:
            payload = jose.jwt.decode(token, self.SECRET, algorithms=[self.ALGORITM])
        except jose.ExpiredSignatureError:
            raise credentials_exception
        except jose.JWTError:
            raise credentials_exception

        email = payload.get("sub")
        if email is None:
            raise credentials_exception

        user = (
            db.query(models.User)
            .filter(models.User.email == email)
            .first()
        )
        if user is None:
            raise credentials_exception
        return user

    async def decode_refresh_token(self, token: str) -> str:
        try:
            payload = jose.jwt.decode(token, Auth.SECRET, algorithms=[Auth.ALGORITM])
            return payload.get("sub")
        except jose.ExpiredSignatureError:
            raise fastapi.HTTPException(status_code=401, detail="Token has expired")
        except (jose.JWTError, ValueError):
            raise fastapi.HTTPException(
                status_code=401, detail="Could not validate credentials"
            )

    async def update_token(
        user: models.User, token: str | None, db=fastapi.Depends(get_db)
    ):
        user.refresh_token = token
        await db.commit()

    async def get_user_by_email(self, email: str, db=fastapi.Depends(get_db)):
        stmt = select(models.User).filter_by(email=email)
        user = db.execute(stmt)
        user = user.scalar_one_or_none()
        return user

    async def confirmed_email(
        self, email: str, db=fastapi.Depends(get_db)
    ) -> None:
        user = await Auth.get_user_by_email(self, email=email, db=db)
        user.confirmed = True
        db.commit()

    def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jose.jwt.encode(to_encode, self.SECRET, algorithm=self.ALGORITM)
        return token

    async def get_email_from_token(self, token: str):
        try:
            payload = jose.jwt.decode(token, self.SECRET, algorithms=[self.ALGORITM])
            email = payload["sub"]
            return email
        except jose.JWTError as e:
            print(e)
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )

    async def create_user(self, body: models.User, db=fastapi.Depends(get_db)):

        new_user = models.User(**body.model_dump())
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    def authenticate_user(db: Session, username: str, password: str):
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user or not auth_service.verify_password(password, user.hashed_password):
            return None
        return user
    
    def require_role(role: int):
        def role_decorator(current_user: models.User = fastapi.Depends(auth_service.get_current_user)):
            if current_user.role != role:
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_403_FORBIDDEN,
                    detail=f"Цей ендпоінт доступний лише для ролі {role}",
                )
            return current_user
        return role_decorator

auth_service = Auth()

conf = ConnectionConfig(
    MAIL_USERNAME="fastapi_project@meta.ua",
    MAIL_PASSWORD="Pythoncourse2024",
    MAIL_FROM=str("fastapi_project@meta.ua"),
    MAIL_PORT=465,
    MAIL_SERVER="smtp.meta.ua",
    MAIL_FROM_NAME="ContactManager",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: str, username: str, host: str):
    try:
        token_verification = auth_service.create_email_token(data={"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)