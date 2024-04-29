from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from dependencies_auth import get_current_user
from src.conf.messages import ACCESS_TOKEN_EXPIRE_MINUTES
from src.database.db import get_db
from src.auth.dependencies_auth import (
    authenticate_user,
    get_password_hash,
    create_access_token,
    require_role,
)
from src.schemas.schemas_auth import Token
from src.database.models import User, Photo, Comment
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


# АДМІНІСТРАТОР
router = APIRouter(prefix="/admin", tags=["admin"])

# Ендпоінт перегляду всіх коментарів
@router.get("/comments", dependencies=[Depends(require_role(1))])  # Доступ лише для адміністратора
def get_all_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    return comments

# Ендпоінт перегляду всіх фото
@router.get("/photos", dependencies=[Depends(require_role(1))])  # Доступ лише для адміністратора
def get_all_photos(db: Session = Depends(get_db)):
    photos = db.query(Photo).all()
    return photos

# Ендпоінт видалення користувача за ID
@router.delete("/delete-user/{user_id}", dependencies=[Depends(require_role(1))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    
    db.delete(user)
    db.commit()
    
    return {"msg": f"Користувач {user.username} видалений"}


# МОДЕРАТОР
router = APIRouter(prefix="/moderator", tags=["moderator"])

# Ендпоінт перегляду всіх коментарів
@router.get("/comments", dependencies=[Depends(require_role(2))])
def get_all_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    return comments

# Ендпоінт видалення окремого коментаря
@router.delete("/delete-comment/{comment_id}", dependencies=[Depends(require_role(2))])
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Коментар не знайдено")
    
    db.delete(comment)
    db.commit()
    
    return {"msg": "Коментар видалено"}

# Ендпоінт перегляду всіх фото
@router.get("/photos", dependencies=[Depends(require_role(2))])
def get_all_photos(db: Session = Depends(get_db)):
    photos = db.query(Photo).all()
    return photos

# Ендпоінт видалення окремого фото
@router.delete("/delete-photo/{photo_id}", dependencies=[Depends(require_role(2))])
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Фото не знайдено")
    
    db.delete(photo)
    db.commit()
    
    return {"msg": "Фото видалено"}


# ПРОСТИЙ КОРИСТУВАЧ
router = APIRouter(prefix="/user", tags=["user"])

# Ендпоінт перегляду всіх коментарів інших користувачів
@router.get("/comments")
def get_all_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    return comments

# Ендпоінт перегляду всіх фото інших користувачів
@router.get("/photos")
def get_all_photos(db: Session = Depends(get_db)):
    photos = db.query(Photo).all()
    return photos

# Видалення власного фото
@router.delete("/delete-photo/{photo_id}")
def delete_own_photo(
    photo_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Шукаємо фото за ID та перевіряємо, чи є власником поточний користувач
    photo = db.query(Photo).filter(Photo.id == photo_id, Photo.owner_id == current_user.id).first()
    if not photo:
        raise HTTPException(
            status_code=404, 
            detail="Фото не знайдено або ви не маєте дозволу видалити це фото"
        )
    
    db.delete(photo)
    db.commit()
    
    return {"msg": "Фото успішно видалено"}

# Видалення власного коментаря
@router.delete("/delete-comment/{comment_id}")
def delete_own_comment(
    comment_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Перевіряємо, чи існує коментар і чи належить він поточному користувачу
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.owner_id == current_user.id).first()
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Коментар не знайдено або ви не маєте дозволу видалити цей коментар"
        )
    
    db.delete(comment)
    db.commit()
    
    return {"msg": "Коментар успішно видалено"}