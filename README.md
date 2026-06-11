# TaskOps Board — vulnerable deployment

TaskOps Board — учебный стенд для практики по безопасному развертыванию контейнерного приложения. Само приложение реализовано как рабочий task manager для небольшой DevOps/SOC-команды: вход в систему, проекты, задачи, комментарии, вложения и экспорт отчетов через фонового worker.

Важное ограничение: эта версия называется `app_vulnerable`, потому что Dockerfile, docker-compose и окружение намеренно сделаны небезопасными. Код приложения не содержит специально добавленных SQL injection, RCE или SSRF. Основная демонстрируемая проблема — небезопасное контейнерное развертывание.

## Состав стенда

```text
nginx        reverse proxy и входная точка
api          fastapi backend и html-интерфейс
postgres     база данных
redis        очередь заданий для экспортов
worker       фоновая обработка report jobs
```

## Что нужно установить

Для Windows рекомендуется использовать WSL2 Ubuntu и Docker Desktop с включенной интеграцией WSL.

Минимально нужно:

```text
1. git
2. docker desktop или docker engine
3. docker compose v2
4. wsl2 ubuntu, если работа идет на windows
5. trivy, если будут выполняться сканирования
```

Проверка:

```bash
docker --version
docker compose version
```

Trivy можно установить позже. Для первого запуска приложения он не нужен.

## Быстрый запуск

Из каталога `app_vulnerable`:

```bash
docker compose up --build
```

После старта открыть:

```text
http://localhost/
```

Также backend напрямую намеренно опубликован наружу:

```text
http://localhost:8000/docs
http://localhost:8000/health
```

PostgreSQL и Redis тоже намеренно опубликованы на host:

```text
localhost:5432
localhost:6379
```

## Демо-учетные записи

```text
admin / admin123
analyst / analyst123
```

## Проверка основной логики

Через веб-интерфейс можно:

```text
1. войти в систему;
2. посмотреть созданные демо-проекты;
3. создать новый проект;
4. создать задачу;
5. изменить статус задачи;
6. добавить комментарий;
7. загрузить вложение;
8. запустить экспорт отчета;
9. скачать сформированный json или csv отчет.
```

Через API можно использовать Swagger UI:

```text
http://localhost:8000/docs
```

Для авторизации в Swagger используйте `/auth/login`, затем вставьте полученный token в Authorize как bearer token.

## Сканирование baseline

После запуска и сборки образов:

```bash
chmod +x scripts/*.sh
./scripts/scan_trivy_image.sh
./scripts/scan_trivy_config.sh
./scripts/scan_trivy_fs.sh
./scripts/collect_baseline_metrics.sh
```

Отчеты будут сохранены в:

```text
reports/baseline/
```

Docker Bench Security лучше запускать в Linux VM или полноценной Linux-среде. В Docker Desktop на Windows/WSL2 результат может быть неполным:

```bash
./scripts/docker_bench.sh
```

## Намеренные проблемы в этой версии

На уровне Dockerfile:

```text
- запуск api и worker от root;
- тяжелый устаревающий базовый образ python:3.9-bullseye;
- лишние пакеты curl, wget, netcat-openbsd, vim, procps, gcc;
- нет healthcheck;
- нет .dockerignore;
- используется add вместо copy;
- apt cache не очищается;
- часть зависимостей закреплена непоследовательно;
- в build context есть демонстрационный секрет.
```

На уровне docker-compose:

```text
- наружу опубликованы api, postgres и redis;
- все сервисы находятся в одной сети;
- секреты и пароли заданы прямо в compose;
- нет read_only;
- нет cap_drop;
- нет no-new-privileges;
- нет pids_limit;
- нет memory limits;
- нет healthcheck на уровне compose;
- uploads и exports примонтированы грубо;
- нет нормальной политики restart.
```

Эти проблемы будут исправляться позже в отдельной защищенной версии `app_secured` после baseline-сканов.

## Остановка и очистка

```bash
docker compose down
```

Удалить volume базы данных:

```bash
docker compose down -v
```
