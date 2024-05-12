import fastapi
import fastapi.security
from src.tests.logger import logger

from src.database.db import get_db
from src.schemas import schemas_auth
from src.database import models
from src.auth.dependencies_auth import auth_service, send_email


router = fastapi.APIRouter(prefix="/auth", tags=["auth"])

get_refresh_token = fastapi.security.HTTPBearer()


@router.post("/signup", status_code=fastapi.status.HTTP_201_CREATED)
async def create_user(
    bt: fastapi.BackgroundTasks,
    body: schemas_auth.UserCreate,
    request: fastapi.Request,
    db=fastapi.Depends(get_db),
):
    """
    Create a new user.

    - **username**: The username of the user.
    - **email**: The email of the user.
    - **password**: The password of the user.

    Returns:
      - **User**: The created user.

    If the first user registers, they are assigned the role of admin.
    If the second user registers, they are assigned the role of moderator.
    For subsequent registrations, users are assigned the role of regular users.
    """
    total_users = db.query(models.User).count()
    if total_users == 0:
        role_id = 1  # Admin
    elif total_users == 1:
        role_id = 2  # Moderator
    else:
        role_id = 3  # Regular User

    user = await auth_service.get_user_by_email(body.email, db)
    if user:
        raise fastapi.HTTPException(status_code=409, detail="User already exists")

    hashed_password = auth_service.get_password_hash(body.password)

    new_user = models.User(
        username=body.username,
        email=body.email,
        hashed_password=hashed_password,
        role_id=role_id,
    )

    db.add(new_user)
    db.commit()

    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login")
async def login(
    body: fastapi.security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db=fastapi.Depends(get_db),
) -> schemas_auth.Token:
    """
    Login to the application.

    - **email**: The email of the user.
    - **password**: The password of the user.

    Returns:
      - **Token**: The access token and refresh token.
    """
    user = db.query(models.User).filter(models.User.email == body.username).first()
    if not user:
        raise fastapi.HTTPException(status_code=401, detail="User not found")
    if not user:
        logger.critical(user.hashed_password)
        logger.critical(body.password)

        raise fastapi.HTTPException(status_code=401, detail="User not confirmed")
    verification = auth_service.verify_password(body.password, user.hashed_password)
    if not verification:
        raise fastapi.HTTPException(status_code=400, detail="Incorrect credentials")

    refresh_token = await auth_service.create_access_token(
        payload={"sub": body.username}
    )
    access_token = await auth_service.create_access_token(
        payload={"sub": body.username}
    )

    user.refresh_token = refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db=fastapi.Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await auth_service.get_user_by_email(email, db)
    if user is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await auth_service.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.get("/refresh_token")
async def refresh_token(
    credentials: fastapi.security.HTTPAuthorizationCredentials = fastapi.Security(
        get_refresh_token
    ),
    db=fastapi.Depends(get_db),
):
    """
    Refresh access token.

    - **Authorization**: The bearer token.

    Returns:
      - **Token**: The new access token and refresh token.
    """
    token = credentials.credentials
    username = await auth_service.decode_refresh_token(token)
    user = db.query(models.User).filter(models.User.refresh_token == token).first()
    if user.refresh_token != token:
        await auth_service.update_token(user, new_token=None, db=db)
        raise fastapi.HTTPException(status_code=400, detail="Invalid token")

    refresh_token = await auth_service.create_refresh_token(payload={"sub": username})
    access_token = await auth_service.create_access_token(payload={"sub": username})
    user.refresh_token = refresh_token
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/{username}")
async def request_email(username: str, response: fastapi.Response, db=fastapi.Depends(get_db)):
    print("__________")
    print(f"{username} зберігаємо")
    print("__________")
    return fastapi.responses.FileResponse("src/static/open_chek.png", media_type="image/png", content_disposition_type="inline")