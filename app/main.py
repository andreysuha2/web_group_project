from fastapi import FastAPI, APIRouter
from app.settings import settings
from datetime import datetime, UTC
import uvicorn

app = FastAPI()

base_router = APIRouter(tags=['base'])

routers = [base_router]

@base_router.get("/")
def status():
    return {"version": settings.app.VERSION, "name": settings.app.NAME, "status": "ok", "env": settings.app.ENV, "datetime": datetime.now(UTC)}

[app.include_router(router, prefix=settings.app.BASE_URL_PREFIX) for router in routers]

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.app.HOST, port=settings.app.PORT, reload=settings.app.ENV == "development")