from fastapi import APIRouter
from redis import Redis
from sqlalchemy import text
from ..config import settings
from ..database import engine
from ..schemas import HealthRead

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthRead)
def health():
    database_status = "ok"
    redis_status = "ok"
    try:
        with engine.connect() as connection:
            connection.execute(text("select 1"))
    except Exception:
        database_status = "error"
    try:
        Redis.from_url(settings.redis_url).ping()
    except Exception:
        redis_status = "error"
    overall = "ok" if database_status == "ok" and redis_status == "ok" else "degraded"
    return HealthRead(status=overall, database=database_status, redis=redis_status, app=settings.app_name)
