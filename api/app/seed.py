from sqlalchemy.orm import Session
from . import models
from .security import get_password_hash


def seed_demo_data(db: Session) -> None:
    if db.query(models.User).count() > 0:
        return

    admin = models.User(
        username="admin",
        full_name="admin user",
        role="admin",
        hashed_password=get_password_hash("admin123"),
    )
    analyst = models.User(
        username="analyst",
        full_name="security analyst",
        role="analyst",
        hashed_password=get_password_hash("analyst123"),
    )
    db.add_all([admin, analyst])
    db.flush()

    project_a = models.Project(
        name="container hardening lab",
        description="учебный проект для анализа слабого контейнерного развертывания",
        owner_id=admin.id,
    )
    project_b = models.Project(
        name="soc automation backlog",
        description="задачи по автоматизации базового мониторинга и отчетности",
        owner_id=analyst.id,
    )
    db.add_all([project_a, project_b])
    db.flush()

    task_1 = models.Task(
        title="scan vulnerable api image with trivy",
        description="получить baseline-отчет по cve и сохранить результат в reports/baseline",
        status="todo",
        priority="high",
        project_id=project_a.id,
        assignee_id=analyst.id,
        created_by_id=admin.id,
    )
    task_2 = models.Task(
        title="check exposed database and redis ports",
        description="зафиксировать, что внутренние сервисы опубликованы наружу в docker-compose",
        status="in_progress",
        priority="critical",
        project_id=project_a.id,
        assignee_id=admin.id,
        created_by_id=admin.id,
    )
    task_3 = models.Task(
        title="prepare log review checklist",
        description="описать какие события должны попадать в журналы nginx, api и worker",
        status="todo",
        priority="medium",
        project_id=project_b.id,
        assignee_id=analyst.id,
        created_by_id=analyst.id,
    )
    db.add_all([task_1, task_2, task_3])
    db.flush()

    db.add(models.Comment(task_id=task_1.id, author_id=admin.id, body="начать со сканирования image и config"))
    db.add(models.Comment(task_id=task_2.id, author_id=analyst.id, body="порты 5432 и 6379 намеренно открыты для baseline"))
    db.commit()
