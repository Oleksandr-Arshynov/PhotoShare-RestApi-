from fastapi import FastAPI
import uvicorn

# from src.routes import photoshare
from fastapi import FastAPI, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Tag, User, Role
from src.repository import photo as repository_photo
from src.routes import photo as router_photo

app = FastAPI()


app.include_router(router_photo.router, prefix='/api')


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)): #, current_user: User = Depends(auth_service.get_current_user)
    # create role
    # roles = ["Admin", "Moderator", "User"]
    # for role in roles:
    #     db.add(Role(role=role))
    # db.commit()

    # await create_tag("admin")

    # create Admin
    # user = User(username="Admin", 
    #             email="Admin@gmail.com",
    #             password="qwerty",
    #             avatar="avatar",
    #             confirmed=True,
    #             role_id=1)
    # db.add(user)
    # db.commit()

    tags = ["Max1","Love","Friend1","Python","Money"]
    photo = "file"
    description = "Like"
    
    await repository_photo.create_photo(user_id=1, photo=photo, description=description, tags=tags, db=db)
    # await repository_photo.delete_photo(user_id=1, photo_id=3, db=db)
    return "OK"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)