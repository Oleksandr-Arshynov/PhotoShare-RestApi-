from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from src.conf.messages import ACCESS_TOKEN_EXPIRE_MINUTES
from src.database.db import get_db
from src.auth.dependencies_auth import (
    authenticate_user,
    get_password_hash,
    create_access_token,
)
from src.schemas.schemas_auth import Token
from src.database.models import User
from src.schemas.user_schemas import UserCreate


router = APIRouter(prefix="/auth", tags=["auth"])


# Реєстрація користувача з роллю
@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Користувач вже існує")

    # Перший користувач - адмін, другий - модератор, решта - юзери
    user_count = db.query(User).count()
    if user_count == 0:
        role_id = 1  # Адміністратор
    elif user_count == 1:
        role_id = 2  # Модератор
    else:
        role_id = 3  # Звичайний користувач

    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        email=user.email,
        role_id=role_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "msg": "Користувач зареєстрований",
        "user": {"username": new_user.username, "role_id": new_user.role_id},
    }


# Авторизація з додаванням ролі
@router.post("/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Невірне ім'я користувача або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.id},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
