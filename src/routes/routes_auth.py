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
    require_role,
)
from src.schemas.schemas_auth import Token
from src.database.models import User
from src.schemas.user_schemas import UserCreate

import src.routes.admin as Admin
import src.routes.moderator as Moderator
import src.routes.user as Check_User


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


# Авторизація адміністратора
@router.post("/admin-login", response_model=Token)
def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user.role_id != 1:
        raise HTTPException(
            status_code=403,
            detail="Доступ дозволено лише адміністраторам",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role_id},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Авторизація модератора
@router.post("/moderator-login", response_model=Token)
def moderator_login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user.role_id != 2:
        raise HTTPException(
            status_code=403,
            detail="Доступ дозволено лише модераторам",
        )
    
    # Створюємо JWT-токен з інформацією про роль
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role_id},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Авторизація юзера
@router.post("/user-login", response_model=Token)
def user_login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user.role_id != 3:
        raise HTTPException(
            status_code=403,
            detail="Доступ дозволено лише звичайним користувачам",
        )
    
    # Створюємо JWT-токен з інформацією про роль
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role_id},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Доступ адміністратора
admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/admin-only", dependencies=[Depends(require_role(1))])
def admin_only():
    return Admin

# Доступ модератора
moderator_router = APIRouter(prefix="/moderator", tags=["moderator"])

@moderator_router.get("/moderator-only", dependencies=[Depends(require_role(2))])
def moderator_only():
    return Moderator

# Доступ звичайного користувача
user_router = APIRouter(prefix="/user", tags=["user"])

@user_router.get("/user-only", dependencies=[Depends(require_role(3))])
def user_only():
    return Check_User
