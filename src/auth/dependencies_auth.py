from fastapi import HTTPException, Header, status, Depends
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.models import User
from src.database.db import SessionLocal, get_db
from passlib.context import CryptContext
from src.conf.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Автентифікація користувача
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# Створення токена з додаванням ролі
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY_JWT, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_token(authorization: str = Header(...)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не вказано токен доступу",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_prefix, token = authorization.split()
    if token_prefix.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний префікс токена. Очікується 'Bearer'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


# Отримання поточного користувача з токена
def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY_JWT, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не вдалося автентифікувати користувача",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Користувача не знайдено",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недійсний токен",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Декоратор для контролю доступу за роллю
def require_role(role: int):
    def role_decorator(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Цей ендпоінт доступний лише для ролі {role}",
            )
        return current_user

    return role_decorator
