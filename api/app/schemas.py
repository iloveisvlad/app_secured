from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    created_at: datetime

    class Config:
        orm_mode = True


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    description: Optional[str] = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    tasks_count: int = 0

    class Config:
        orm_mode = True


class TaskCreate(BaseModel):
    project_id: int
    title: str = Field(..., min_length=3, max_length=160)
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=160)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    project_id: int
    assignee_id: Optional[int]
    created_by_id: int
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    comments_count: int = 0
    attachments_count: int = 0

    class Config:
        orm_mode = True


class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=4000)


class CommentRead(BaseModel):
    id: int
    task_id: int
    author_id: int
    body: str
    created_at: datetime
    author_username: Optional[str] = None

    class Config:
        orm_mode = True


class AttachmentRead(BaseModel):
    id: int
    task_id: int
    uploaded_by_id: int
    filename: str
    content_type: Optional[str]
    size_bytes: int
    created_at: datetime

    class Config:
        orm_mode = True


class ReportExportRequest(BaseModel):
    project_id: Optional[int] = None
    format: str = "json"


class ReportJobRead(BaseModel):
    id: int
    status: str
    format: str
    requested_by_id: int
    project_id: Optional[int]
    result_path: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    download_url: Optional[str] = None

    class Config:
        orm_mode = True


class HealthRead(BaseModel):
    status: str
    database: str
    redis: str
    app: str
