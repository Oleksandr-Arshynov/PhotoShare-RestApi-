import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User, Role
from src.routes import photo as router_photo
from src.routes import routes_auth
from src.routes import comment as router_comment
from src.routes import admin as routes_admin
from src.routes import moderator as routes_moderator
from src.routes import user as routes_user

app = FastAPI()

app.include_router(routes_auth.router, prefix="/api")
app.include_router(routes_admin.router, prefix="/api")
app.include_router(routes_moderator.router, prefix="/api")
app.include_router(routes_user.router, prefix="/api")
app.include_router(router_photo.router, prefix="/api")
app.include_router(router_comment.router, prefix="/api")


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    # create role
    roles = ["Admin", "Moderator", "User"]
    for role_name in roles:
        existing_role = db.query(Role).filter(Role.role == role_name).first()
        if not existing_role:
            db.add(Role(role=role_name))
    db.commit()

    # create Admin
    admin_role = db.query(Role).filter(Role.role == "Admin").first()
    if not admin_role:
        admin_role = Role(role="Admin")
        db.add(admin_role)
        db.commit()

    # Check if Admin user already exists
    existing_admin = db.query(User).filter(User.email == "Admin@gmail.com").first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin user already exists.")

    user = User(
        username="Admin",
        email="Admin@gmail.com",
        hashed_password="qwerty",
        avatar="avatar",
        confirmed=True,
        role=admin_role,
    )
    db.add(user)
    db.commit()

    return "OK"


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000) # , reload=True
