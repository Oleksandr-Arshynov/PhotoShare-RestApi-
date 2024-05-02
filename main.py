import uvicorn
from sqlalchemy.orm import Session
from fastapi import FastAPI, Request, Depends, HTTPException, status

from src.database.db import get_db
from src.database.models import User, Role
from src.routes import routes_auth
from src.routes import admin as routes_admin
from src.routes import moderator as routes_moderator
from src.routes import user as routes_user
from src.routes import transformation_photo as routes_transformation_photo

app = FastAPI()

app.include_router(routes_auth.router, prefix="/api")
app.include_router(routes_admin.router, prefix="/api")
app.include_router(routes_moderator.router, prefix="/api")
app.include_router(routes_user.router, prefix="/api")
app.include_router(routes_transformation_photo.router, prefix="/api")


@app.get("/", status_code=status.HTTP_200_OK)
async def static(request: Request, db: Session = Depends(get_db)):
    try:
        # create role
        roles = ["Admin", "Moderator", "User"]
        for role_name in roles:
            existing_role = db.query(Role).filter(Role.role == role_name).first()
            if not existing_role:
                db.add(Role(role=role_name))
        db.commit()

        admin = User(
            username="Admin",
            email="Admin@gmail.com",
            hashed_password=routes_auth.get_password_hash("qwerty"),
            avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ0cFYTSmgeLGCEAApBVBVkVcxe2COuA2sYja0IUfwe0w&s",
            confirmed=True,
            role=db.query(Role).filter(Role.role=="Admin").first(),
        )
        db.add(admin)
        db.commit()

        moderator = User(
            username="Moderator",
            email="Moderator@gmail.com",
            hashed_password=routes_auth.get_password_hash("qwerty"),
            avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfhs8u11hfQyBqgGQSp_lWzoHkcSIjm6KGDC0gg567yg&s",
            confirmed=True,
            role=db.query(Role).filter(Role.role=="Moderator").first(),
        )
        db.add(moderator)
        db.commit()

        user = User(
            username="User",
            email="User@gmail.com",
            hashed_password=routes_auth.get_password_hash("qwerty"),
            avatar="https://img.pixers.pics/pho_wat(s3:700/FO/33/04/37/38/700_FO33043738_f6c745438728a9e2cd116e7c28a15ffa.jpg,700,700,cms:2018/10/5bd1b6b8d04b8_220x50-watermark.png,over,480,650,jpg)/stickers-fire-font-letter-u.jpg.jpg",
            confirmed=True,
            role=db.query(Role).filter(Role.role=="User").first(),
        )
        db.add(user)
        db.commit()
        return "OK"  
    except Exception as _:
        return "Exception"

    


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # , reload=True
