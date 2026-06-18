# TaskOps Board — vulnerable deployment

TaskOps Board — учебный стенд для практики по безопасному развертыванию контейнерного приложения. Само приложение реализовано как рабочий task manager для небольшой команды: вход в систему, проекты, задачи, комментарии, вложения и экспорт отчетов через фонового worker.


## Состав стенда

```text
nginx        reverse proxy и входная точка
api          fastapi backend и html-интерфейс
postgres     база данных
redis        очередь заданий для экспортов
worker       фоновая обработка report jobs
```

## Что нужно установить


Минимально нужно:

```text
1. git
2. docker desktop или docker engine
3. docker compose v2
4. trivy, если будут выполняться сканирования
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


```bash
./scripts/docker_bench.sh
```

## Намеренные проблемы в этой версии

## Остановка и очистка

```bash
docker compose down
```

Удалить volume базы данных:

```bash
docker compose down -v
```
