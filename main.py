from fastapi import FastAPI
import uvicorn

import routes.photoshare

app = FastAPI()


app.include_router(routes.photoshare.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)