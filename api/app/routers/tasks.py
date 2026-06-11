from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(tags=["tasks"])

ALLOWED_STATUSES = {"todo", "in_progress", "blocked", "done"}
ALLOWED_PRIORITIES = {"low", "medium", "high", "critical"}


def task_to_read(task: models.Task) -> schemas.TaskRead:
    return schemas.TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        project_id=task.project_id,
        assignee_id=task.assignee_id,
        created_by_id=task.created_by_id,
        due_date=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at,
        comments_count=len(task.comments),
        attachments_count=len(task.attachments),
    )


def validate_task_values(status_value: Optional[str], priority_value: Optional[str]) -> None:
    if status_value is not None and status_value not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of {sorted(ALLOWED_STATUSES)}")
    if priority_value is not None and priority_value not in ALLOWED_PRIORITIES:
        raise HTTPException(status_code=400, detail=f"priority must be one of {sorted(ALLOWED_PRIORITIES)}")


@router.get("/tasks", response_model=list[schemas.TaskRead])
def list_tasks(
    project_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Task)
    if project_id is not None:
        query = query.filter(models.Task.project_id == project_id)
    if status_filter is not None:
        query = query.filter(models.Task.status == status_filter)
    tasks = query.order_by(models.Task.updated_at.desc()).all()
    return [task_to_read(task) for task in tasks]


@router.post("/tasks", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    validate_task_values(payload.status, payload.priority)
    project = db.query(models.Project).filter(models.Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    if payload.assignee_id is not None:
        assignee = db.query(models.User).filter(models.User.id == payload.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="assignee not found")
    task = models.Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        project_id=payload.project_id,
        assignee_id=payload.assignee_id,
        created_by_id=current_user.id,
        due_date=payload.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task_to_read(task)


@router.get("/tasks/{task_id}", response_model=schemas.TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task_to_read(task)


@router.patch("/tasks/{task_id}", response_model=schemas.TaskRead)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    data = payload.dict(exclude_unset=True)
    validate_task_values(data.get("status"), data.get("priority"))
    if "assignee_id" in data and data["assignee_id"] is not None:
        assignee = db.query(models.User).filter(models.User.id == data["assignee_id"]).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="assignee not found")
    for field, value in data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task_to_read(task)
