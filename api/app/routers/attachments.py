import os
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from .. import models, schemas
from ..config import settings
from ..database import get_db
from ..security import get_current_user

router = APIRouter(tags=["attachments"])


def safe_filename(filename: str) -> str:
    cleaned = filename.replace("/", "_").replace("\\", "_").strip()
    return cleaned or "attachment.bin"


@router.get("/tasks/{task_id}/attachments", response_model=list[schemas.AttachmentRead])
def list_attachments(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return db.query(models.Attachment).filter(models.Attachment.task_id == task_id).order_by(models.Attachment.created_at.desc()).all()


@router.post("/tasks/{task_id}/attachments", response_model=schemas.AttachmentRead, status_code=status.HTTP_201_CREATED)
def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    task_dir = Path(settings.upload_dir) / str(task_id)
    task_dir.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(file.filename or "attachment.bin")
    stored_path = task_dir / filename

    size = 0
    with stored_path.open("wb") as buffer:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > settings.max_upload_mb * 1024 * 1024:
                raise HTTPException(status_code=413, detail="file is too large")
            buffer.write(chunk)

    attachment = models.Attachment(
        task_id=task.id,
        uploaded_by_id=current_user.id,
        filename=filename,
        stored_path=str(stored_path),
        content_type=file.content_type,
        size_bytes=size,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.get("/tasks/{task_id}/attachments/{attachment_id}/download")
def download_attachment(task_id: int, attachment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    attachment = db.query(models.Attachment).filter(models.Attachment.id == attachment_id, models.Attachment.task_id == task_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="attachment not found")
    if not os.path.exists(attachment.stored_path):
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(attachment.stored_path, filename=attachment.filename, media_type=attachment.content_type)
