import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User, Role, Photo
from src.routes import photo as router_photo
from src.routes import routes_auth
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Зазначте теку для шаблонів
templates = Jinja2Templates(directory="src/templates")
app = FastAPI()


app.include_router(router_photo.router, prefix="/api")
app.include_router(routes_auth.router, prefix="/api")

# @app.get("/")
# async def home(request: Request, db: Session = Depends(get_db)):
#     # create role
#     roles = ["Admin", "Moderator", "User"]
#     for role_name in roles:
#         existing_role = db.query(Role).filter(Role.role == role_name).first()
#         if not existing_role:
#             db.add(Role(role=role_name))
#     db.commit()

#     # create Admin
#     admin_role = db.query(Role).filter(Role.role == "Admin").first()
#     if not admin_role:
#         admin_role = Role(role="Admin")
#         db.add(admin_role)
#         db.commit()

#     # Check if Admin user already exists
#     existing_admin = db.query(User).filter(User.email == "Admin@gmail.com").first()
#     if existing_admin:
#         raise HTTPException(status_code=400, detail="Admin user already exists.")

#     user = User(
#         username="Admin",
#         email="Admin@gmail.com",
#         hashed_password="qwerty",
#         avatar="avatar",
#         confirmed=True,
#         role=admin_role,
#     )
#     db.add(user)
#     db.commit()

#     return "OK"



@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    photos_all = db.query(Photo).all()
    users = db.query(User).all()
    return templates.TemplateResponse("home.html", {"request": request, "photos_all": photos_all, "users": users})

@app.get("/create_photo", response_class=HTMLResponse)
async def create_photo(request: Request):
    return templates.TemplateResponse("create_photo.html", {"request": request})

@app.get("/change_photo/{photo_id}", response_class=HTMLResponse)
async def change_photo(request: Request, photo_id: int):
    return templates.TemplateResponse("change_photo.html", {"request": request, "photo_id": photo_id})


@app.get("/delete_photo/{photo_id}", response_class=HTMLResponse)
async def delete_photo(request: Request, photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id==photo_id).first()
    user = db.query(User).filter(User.id==Photo.user_id).first()
    if photo:
        return templates.TemplateResponse("delete_photo.html", {"request": request, "photo": photo, "user": user})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

if __name__ == "__main__":  
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

