import uvicorn
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User, Role
from src.routes import photo as router_photo

app = FastAPI()


app.include_router(router_photo.router, prefix='/api')


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)): #, current_user: User = Depends(auth_service.get_current_user)
    # create role
    roles = ["Admin", "Moderator", "User"]
    for role in roles:
        existing_role = db.query(Role).filter(Role.role == role).first()
        if not existing_role:
            db.add(Role(role=role))
    db.commit()

    # create Admin
    user = User(username="Admin", 
                email="Admin@gmail.com",
                password="qwerty",
                avatar="avatar",
                confirmed=True,
                role_id=15)
    db.add(user)
    db.commit()

    return "OK"

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)