from fastapi import FastAPI
import uvicorn

import src.routes.photoshare

app = FastAPI()


app.include_router(src.routes.photoshare)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)