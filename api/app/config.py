import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = os.getenv("APP_NAME", "TaskOps Board")
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("DATABASE_URL", "postgresql://taskops:taskops123@postgres:5432/taskops")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-hardcoded-for-training")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    upload_dir: str = os.getenv("UPLOAD_DIR", "/app/uploads")
    report_dir: str = os.getenv("REPORT_DIR", "/app/reports")
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    redis_report_queue: str = "taskops:report_jobs"


settings = Settings()
