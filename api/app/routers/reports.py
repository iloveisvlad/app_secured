import json
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from redis import Redis
from sqlalchemy.orm import Session
from .. import models, schemas
from ..config import settings
from ..database import get_db
from ..security import get_current_user

router = APIRouter(tags=["reports"])


def job_to_read(job: models.ReportJob) -> schemas.ReportJobRead:
    download_url = f"/reports/{job.id}/download" if job.status == "done" and job.result_path else None
    return schemas.ReportJobRead(
        id=job.id,
        status=job.status,
        format=job.format,
        requested_by_id=job.requested_by_id,
        project_id=job.project_id,
        result_path=job.result_path,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
        download_url=download_url,
    )


@router.post("/reports/export", response_model=schemas.ReportJobRead, status_code=status.HTTP_202_ACCEPTED)
def export_report(payload: schemas.ReportExportRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if payload.format not in {"json", "csv"}:
        raise HTTPException(status_code=400, detail="format must be json or csv")
    if payload.project_id is not None:
        project = db.query(models.Project).filter(models.Project.id == payload.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="project not found")
    job = models.ReportJob(status="queued", format=payload.format, requested_by_id=current_user.id, project_id=payload.project_id)
    db.add(job)
    db.commit()
    db.refresh(job)

    redis_client = Redis.from_url(settings.redis_url)
    redis_client.lpush(settings.redis_report_queue, json.dumps({"job_id": job.id}))
    return job_to_read(job)


@router.get("/reports/{job_id}", response_model=schemas.ReportJobRead)
def get_report(job_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    job = db.query(models.ReportJob).filter(models.ReportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="report job not found")
    return job_to_read(job)


@router.get("/reports/{job_id}/download")
def download_report(job_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    job = db.query(models.ReportJob).filter(models.ReportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="report job not found")
    if job.status != "done" or not job.result_path:
        raise HTTPException(status_code=409, detail="report is not ready")
    if not os.path.exists(job.result_path):
        raise HTTPException(status_code=404, detail="report file not found")
    media_type = "application/json" if job.format == "json" else "text/csv"
    return FileResponse(job.result_path, filename=os.path.basename(job.result_path), media_type=media_type)
