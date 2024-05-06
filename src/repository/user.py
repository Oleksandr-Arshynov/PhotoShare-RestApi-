
from sqlalchemy.orm import Session
from src.database.models import User



async def get_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id==user_id).first()
    return user

async def get_username(username: int, db: Session):
    user = db.query(User).filter(User.username==username).first()
    return user