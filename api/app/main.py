import logging
import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import Base, SessionLocal, engine
from .seed import seed_demo_data
from .routers import auth, projects, tasks, comments, attachments, reports, health, pages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskops")

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(attachments.router)
app.include_router(reports.router)
app.include_router(health.router)


@app.on_event("startup")
def startup() -> None:
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(settings.report_dir, exist_ok=True)
    last_error = None
    for attempt in range(30):
        try:
            Base.metadata.create_all(bind=engine)
            db = SessionLocal()
            try:
                seed_demo_data(db)
            finally:
                db.close()
            logger.info("database initialized")
            return
        except Exception as exc:
            last_error = exc
            logger.warning("database is not ready, retry %s", attempt + 1)
            time.sleep(2)
    raise RuntimeError(f"database initialization failed: {last_error}")
