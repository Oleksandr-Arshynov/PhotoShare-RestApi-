
from src.database.models import Photo, User, Comment
from sqlalchemy import and_, select
from datetime import datetime
from fastapi import HTTPException, status, UploadFile


from src.schemas.coment_schemas import CommentSchema, CommentUpdateSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.conf.config import settings
from src.conf import messages



def create_comment(db: Session,user_id: int,photo_id: int, comment: CommentSchema):

    new_comment = Comment(**comment.dict(), user_id=user_id, photo_id=photo_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

def update_comment(db: Session, user_id: int, photo_id: int, updated_comment: CommentUpdateSchema) :
    comment = db.query(Comment).filter(Comment.user_id == user_id, Comment.photo_id == photo_id).first()
    if comment:
        comment.content = updated_comment.content
        db.commit()
        db.refresh(comment)
    return comment

def delete_comment(db: Session, photo_id: int, user_id: int):
    comment = db.query(Comment).filter(Comment.user_id == user_id, Comment.photo_id == photo_id).first()
    if comment:
        db.delete(comment)
        db.commit()
    return comment