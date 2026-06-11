# Архитектура TaskOps Board

TaskOps Board моделирует типичное небольшое контейнерное приложение с несколькими сервисами.

```text
user browser
    |
    v
nginx reverse proxy
    |
    v
fastapi api
    |             \
    v              v
postgres          redis
                   |
                   v
                 worker
```

## Назначение компонентов

`nginx` принимает входящие HTTP-запросы и проксирует их в `api`.

`api` содержит FastAPI backend, HTML-интерфейс, авторизацию, CRUD-процессы для проектов и задач, загрузку вложений и постановку report jobs в очередь.

`postgres` хранит users, projects, tasks, comments, attachments и report_jobs.

`redis` используется как очередь фоновых заданий. API кладет в очередь id report job, worker забирает его и формирует файл отчета.

`worker` формирует json/csv-отчеты и записывает результат в общий каталог `/app/reports`.

## Почему приложение не минимальное

В стенде намеренно есть несколько сервисов и реальная рабочая логика. Это позволяет показать не только сканирование образа, но и типовые проблемы контейнерной эксплуатации: опубликованные внутренние порты, общая сеть, секреты в окружении, отсутствие resource limits, отсутствие read-only root filesystem, запуск от root, отсутствие healthcheck и слабую организацию volumes.

## Почему Kubernetes не используется

Практика ограничена Docker и Docker Compose. Kubernetes, service mesh, admission policies и kube-bench не входят в объем работы. Это позволяет сфокусироваться на Dockerfile, docker-compose, образах, runtime-конфигурации, Trivy, Docker Bench Security и базовом runtime-наблюдении.
