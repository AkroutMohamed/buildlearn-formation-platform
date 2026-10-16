import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.ai.api.routes import router as ai_router
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.instructor import router as instructor_router
from app.routers.notification import router as notification_router
from app.routers.public import router as public_router
from app.routers.student import router as student_router
import app.models  

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("formation_platform")

if settings.debug:
    from alembic.config import Config as AlembicConfig
    from alembic import command as alembic_command

    _alembic_ini = Path(__file__).resolve().parent.parent / "alembic.ini"
    alembic_command.upgrade(AlembicConfig(str(_alembic_ini)), "head")

app = FastAPI(title=settings.app_name)
app.include_router(admin_router)
app.include_router(ai_router)
app.include_router(instructor_router)
app.include_router(public_router)
app.include_router(student_router)
app.include_router(notification_router)
app.include_router(auth_router)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


settings.upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_path), name="uploads")

logger.info("starting %s debug=%s", settings.app_name, settings.debug)

@app.get("/")
def root():
    return {"message": "API running"}
