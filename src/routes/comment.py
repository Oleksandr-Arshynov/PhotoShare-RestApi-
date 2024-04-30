from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.repository import photo as repository_photo
from src.schemas.coment_schemas import CommentResponse,CommentSchema, CommentUpdateSchema, CommentBase
from src.database.models import Comment, Photo
from src.database.db import get_db
from src.conf import messages
from src.repository.comment import create_comment_rep, update_comment_rep, delete_comment_rep

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

@router.post("/", response_model=CommentResponse)
async def create_comment(comment: CommentSchema, user_id: int,  photo_id: int, db: Session = Depends(get_db)):

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.PHOTO_NOT_FOUND
        )
    else:
        comment = create_comment_rep(db, user_id, photo_id, comment)
        return comment
    


@router.put("/{comment_id}")
async def update_comment(updated_comment: CommentUpdateSchema,comment_id: int, photo_id: int, user_id: int, db: Session = Depends(get_db)):

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.PHOTO_NOT_FOUND
        )
    else:
        comment = db.query(Comment).filter(Comment.id == comment_id, Comment.photo_id == photo_id, Comment.user_id == user_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.COMMENT_NOT_FOUND
            )

        comment = update_comment_rep(db, comment_id, updated_comment)
        return comment



@router.delete("/{comment_id}")
def delete_comment(comment_id: int,user_id:int, photo_id: int, db: Session = Depends(get_db)):

    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.PHOTO_NOT_FOUND
        )
    else:
        comment = db.query(Comment).filter(Comment.id == comment_id, Comment.photo_id == photo_id, Comment.user_id == user_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.COMMENT_NOT_FOUND
            )

        comment = delete_comment_rep(db,photo_id, comment_id)
        return comment
