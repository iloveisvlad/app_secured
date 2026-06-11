# Намеренно небезопасное развертывание

Этот документ фиксирует проблемы первой версии, чтобы позже использовать их как backlog для `app_secured`.

## Dockerfile

```text
1. api и worker запускаются от root.
2. используется python:3.9-bullseye.
3. установлены лишние утилиты: curl, wget, netcat-openbsd, vim, procps, gcc.
4. apt cache не очищается.
5. используется add вместо copy.
6. нет healthcheck.
7. нет .dockerignore.
8. в build context есть api/secrets/demo_token.txt.
9. зависимости закреплены непоследовательно.
10. uvicorn запускается с --reload.
```

## Docker Compose

```text
1. api опубликован наружу на 8000.
2. postgres опубликован наружу на 5432.
3. redis опубликован наружу на 6379.
4. все сервисы находятся в одной сети по умолчанию.
5. пароли и jwt secret заданы прямо в compose.
6. нет read_only.
7. нет cap_drop.
8. нет security_opt no-new-privileges.
9. нет pids_limit.
10. нет memory limits.
11. нет healthcheck на уровне compose.
12. нет нормальной restart policy.
```

## Что исправлять позже

```text
- заменить базовые образы и уменьшить размер;
- убрать лишние пакеты;
- создать non-root user;
- добавить .dockerignore;
- заменить add на copy;
- добавить healthcheck;
- убрать секреты из репозитория и compose;
- закрыть порты postgres и redis;
- разделить сети frontend/backend;
- добавить read_only и tmpfs;
- добавить cap_drop all;
- добавить no-new-privileges;
- добавить pids_limit и memory limits;
- настроить controlled volumes;
- добавить trivy quality gate.
```
