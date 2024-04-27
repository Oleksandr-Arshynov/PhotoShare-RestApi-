from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from auth.dependencies import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_db,
    authenticate_user,
    get_password_hash,
    create_access_token,
    require_role,
)
from auth.models import User
from auth.schemas import Token, UserCreate

router = APIRouter()

# Реєстрація користувача з роллю
@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Користувач вже існує")

    # Визначаємо роль: перший користувач - адмін, решта - юзер
    is_admin = db.query(User).count() == 0
    role = "admin" if is_admin else "user"

    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        email=user.email,
        role=role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"msg": "Користувач зареєстрований", "user": {"username": new_user.username, "role": new_user.role}}

# Авторизація з додаванням ролі
@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Невірне ім'я користувача або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},  # Додаємо роль
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Ендпоінт, доступний лише для адміністраторів
@router.get("/admin-endpoint", dependencies=[Depends(require_role("admin"))])
def admin_only():
    return {"msg": "Цей ендпоінт доступний лише для адміністраторів"}

# Ендпоінт, доступний лише для модераторів
@router.get("/moderator-endpoint", dependencies=[Depends(require_role("moderator"))])
def moderator_only():
    return {"msg": "Цей ендпоінт доступний лише для модераторів"}
