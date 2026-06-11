from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(tags=["comments"])


def comment_to_read(comment: models.Comment) -> schemas.CommentRead:
    return schemas.CommentRead(
        id=comment.id,
        task_id=comment.task_id,
        author_id=comment.author_id,
        body=comment.body,
        created_at=comment.created_at,
        author_username=comment.author.username if comment.author else None,
    )


@router.get("/tasks/{task_id}/comments", response_model=list[schemas.CommentRead])
def list_comments(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    comments = db.query(models.Comment).filter(models.Comment.task_id == task_id).order_by(models.Comment.created_at.asc()).all()
    return [comment_to_read(comment) for comment in comments]


@router.post("/tasks/{task_id}/comments", response_model=schemas.CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(task_id: int, payload: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    comment = models.Comment(task_id=task.id, author_id=current_user.id, body=payload.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment_to_read(comment)
