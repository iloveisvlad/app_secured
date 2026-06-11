from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "TaskOps Board"})


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "title": "Dashboard"})


@router.get("/projects/{project_id}/view", response_class=HTMLResponse)
def project_page(project_id: int, request: Request):
    return templates.TemplateResponse("project.html", {"request": request, "title": "Project", "project_id": project_id})


@router.get("/tasks/{task_id}/view", response_class=HTMLResponse)
def task_page(task_id: int, request: Request):
    return templates.TemplateResponse("task.html", {"request": request, "title": "Task", "task_id": task_id})


@router.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request, "title": "Reports"})
