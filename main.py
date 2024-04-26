from fastapi import FastAPI
import uvicorn

# from src.routes import photoshare
from fastapi import FastAPI, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import Tag
from src.repository.tags import create_tag

app = FastAPI()


# app.include_router(photoshare.router)


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)): #, current_user: User = Depends(auth_service.get_current_user)
    await create_tag("admin")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)