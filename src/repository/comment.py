
from src.database.models import Photo, User, Comment
from sqlalchemy import and_, select
from datetime import datetime
from fastapi import HTTPException, status, UploadFile


from src.schemas.coment_schemas import CommentSchema, CommentUpdateSchema, CommentBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.conf.config import settings
from src.conf import messages



def create_comment_rep(db: Session,user_id: int,photo_id: int, comment: CommentSchema) :
    # new_comment = Comment(comment.photo_id, comment.user_id,comment.comment)
    new_comment = Comment(**comment.dict(), user_id=user_id, photo_id=photo_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

def update_comment_rep(db: Session, comment_id: int, updated_comment: CommentUpdateSchema) :
    comment_to_update = db.query(Comment).filter(Comment.id == comment_id).first()
    print(comment_to_update)
    comment_to_update.comment = updated_comment.comment
    db.commit()
    db.refresh(comment_to_update)
    return comment_to_update


def delete_comment_rep(db: Session, photo_id: int, comment_id: int):


    # stmt = select(Comment).filter_by(id=comment_id,photo_id = photo_id)
    # comment = db.execute(stmt)
    # comment = comment.scalar_one_or_none()
    comment_to_delete = db.query(Comment).filter(Comment.id == comment_id, Comment.photo_id == photo_id).first()
    if comment_to_delete:
        db.delete(comment_to_delete)
        db.commit()
    return comment_to_delete
