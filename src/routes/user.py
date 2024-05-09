from fastapi import APIRouter, Depends, HTTPException, Request

from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.repository import user as repository_user
from src.auth.dependencies_auth import auth_service


router = APIRouter(prefix="/user", tags=["user"])


@router.get("")
async def get_me_info(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    GET CURRENT USER INFO

    Method: GET
    URL: /photo

    Description:
    This endpoint allows a user to retrieve their own information.

    Response:
    Returns the user object containing information about the current user.

    Status Codes:
    - 200: User information retrieved successfully.
    - 404: User not found.
    """
    user = await repository_user.get_user(current_user.id, db)
    if user == None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{username}")
async def get_user_info(
    request: Request,
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    GET USER INFO BY USERNAME

    Method: POST
    URL: /photo/{username}

    Description:
    This endpoint allows a user to retrieve information about another user by their username.

    Parameters:
    - username (str, path, required): The username of the user whose information is being retrieved.

    Response:
    Returns the user object containing information about the specified user.

    Status Codes:
    - 200: User information retrieved successfully.
    - 404: Username not found.
    """
    user = await repository_user.get_username(username, db)
    if user == None:
        raise HTTPException(status_code=404, detail="Username not found")
    return user
