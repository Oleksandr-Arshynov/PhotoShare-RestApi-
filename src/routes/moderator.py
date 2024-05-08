from src.repository.comment import update_comment_rep
from src.database.models import Photo, Comment, User
from src.schemas.coment_schemas import (
    CommentUpdateSchema,
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
)
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import photo as repository_photo
from src.conf import messages
from src.auth.dependencies_auth import auth_service


router = APIRouter(prefix="/moderator", tags=["moderator"])


@router.delete("/{photo_id}", status_code=status.HTTP_200_OK)
async def delete_photo(
    request: Request,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Deletes a photo as a moderator.

    Args:
        request (Request): The incoming request.
        photo_id (int): The ID of the photo to delete.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The deleted photo details.
    """
    if current_user.role_id == 2 or current_user.role_id == 1:
        photo = await repository_photo.delete_photo(current_user.id, photo_id, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.ACCESS_FORBIDDEN,
        )
    return photo


@router.put("/{comment_id}")
async def update_comment(
    updated_comment: CommentUpdateSchema,
    comment_id: int,
    photo_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Updates an existing comment for a specific photo as a moderator.

    Args:
        updated_comment (CommentUpdateSchema): The updated comment data.
        comment_id (int): The ID of the comment to update.
        photo_id (int): The ID of the photo.
        user_id (int): The ID of the user.
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: The updated comment details.
    """
    if current_user.role_id == 2 or current_user.role_id == 1:
        photo = db.query(Photo).filter(Photo.id == photo_id).first()
        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
            )
        else:
            comment = (
                db.query(Comment)
                .filter(
                    Comment.id == comment_id,
                    Comment.photo_id == photo_id,
                    Comment.user_id == current_user.id,
                )
                .first()
            )
            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
                )

            comment = update_comment_rep(db, comment_id, updated_comment)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.ACCESS_FORBIDDEN,
        )
    return comment
