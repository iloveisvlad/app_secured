from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "TaskOps Board"
    environment: str = "development"

    database_url: str
    redis_url: str = "redis://redis:6379/0"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    upload_dir: str = "/app/uploads"
    report_dir: str = "/app/reports"
    max_upload_mb: int = 10

    redis_report_queue: str = "taskops:report_jobs"


settings = Settings()