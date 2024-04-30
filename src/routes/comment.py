from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.schemas.coment_schemas import CommentResponse,CommentSchema, CommentUpdateSchema
from src.database.models import Comment
from src.database.db import get_db
from src.conf import messages

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

@router.post("/", response_model=CommentResponse)
def create_comment(comment: CommentSchema, user_id: int,  photo_id: int, db: Session = Depends(get_db)):

    existing_comment = db.query(Comment).filter(Comment.user_id == user_id, Comment.photo_id == photo_id).first()
    if existing_comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.COMMENT_ALREADY_EXISTS
        )
    return create_comment(comment, user_id, photo_id, db)


@router.put("/{comment_id}")
def update_comment(updated_comment: CommentUpdateSchema,photo_id: int, user_id: int, db: Session = Depends(get_db)):

    existing_comment = db.query(Comment).filter(Comment.user_id == user_id, Comment.photo_id == photo_id).first()
    if not existing_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.COMMENT_NOT_FOUND
        )
    return update_comment(updated_comment, user_id, photo_id,db)



@router.delete("/{comment_id}")
def delete_comment(comment_id: int, photo_id: int, db: Session = Depends(get_db)):

    existing_comment = db.query(Comment).filter(Comment.photo_id == photo_id, Comment.user_id == comment_id).first()
    if not existing_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.CONTACT_NOT_FOUND
        )
    return delete_comment( comment_id, photo_id,db)