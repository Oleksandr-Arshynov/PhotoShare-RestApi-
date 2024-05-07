from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request
)

from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import user as repository_user


router = APIRouter(prefix="/user", tags=["user"])

USER_ID = 1

@router.get("")
async def get_me_info( 
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = USER_ID # Поки немає авторизації
    user = await repository_user.get_user(user_id, db)
    if user == None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/{username}")
async def get_user_info( 
    request: Request,
    username: str,
    db: Session = Depends(get_db)
):
    user = await repository_user.get_username(username, db)
    if user == None:
        raise HTTPException(status_code=404, detail="Username not found")
    return user
