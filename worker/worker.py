import csv
import json
import os
import time
from datetime import datetime
from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app import models

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
redis_client = Redis.from_url(settings.redis_url)


def serialize_task(task: models.Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "project_id": task.project_id,
        "project_name": task.project.name if task.project else None,
        "assignee_id": task.assignee_id,
        "created_by_id": task.created_by_id,
        "comments_count": len(task.comments),
        "attachments_count": len(task.attachments),
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


def write_json_report(path: str, tasks: list[models.Task], job: models.ReportJob) -> None:
    payload = {
        "generated_at": datetime.utcnow().isoformat(),
        "job_id": job.id,
        "project_id": job.project_id,
        "tasks": [serialize_task(task) for task in tasks],
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def write_csv_report(path: str, tasks: list[models.Task]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "title", "status", "priority", "project_id", "project_name", "comments_count", "attachments_count"],
        )
        writer.writeheader()
        for task in tasks:
            data = serialize_task(task)
            writer.writerow({key: data[key] for key in writer.fieldnames})


def process_job(job_id: int) -> None:
    db = SessionLocal()
    try:
        job = db.query(models.ReportJob).filter(models.ReportJob.id == job_id).first()
        if not job:
            return
        job.status = "running"
        job.updated_at = datetime.utcnow()
        db.commit()

        query = db.query(models.Task).order_by(models.Task.created_at.asc())
        if job.project_id is not None:
            query = query.filter(models.Task.project_id == job.project_id)
        tasks = query.all()

        os.makedirs(settings.report_dir, exist_ok=True)
        filename = f"taskops_report_{job.id}.{job.format}"
        path = os.path.join(settings.report_dir, filename)
        if job.format == "csv":
            write_csv_report(path, tasks)
        else:
            write_json_report(path, tasks, job)

        job.status = "done"
        job.result_path = path
        job.error_message = None
        job.updated_at = datetime.utcnow()
        db.commit()
    except Exception as exc:
        db.rollback()
        job = db.query(models.ReportJob).filter(models.ReportJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(exc)
            job.updated_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


def main() -> None:
    print("taskops worker started", flush=True)
    while True:
        item = redis_client.brpop(settings.redis_report_queue, timeout=5)
        if not item:
            time.sleep(1)
            continue
        _, raw_payload = item
        try:
            payload = json.loads(raw_payload.decode("utf-8"))
            process_job(int(payload["job_id"]))
        except Exception as exc:
            print(f"worker failed to process queue item: {exc}", flush=True)


if __name__ == "__main__":
    main()
