# Метрики baseline и protected-сравнения

## Trivy image

```text
- количество critical/high/medium/low cve;
- количество fixable vulnerabilities;
- список top packages by severity;
- размер образа api и worker.
```

## Trivy config

```text
- количество dockerfile misconfigurations;
- количество docker-compose misconfigurations;
- severity findings;
- какие finding исправлены в app_secured.
```

## Trivy fs

```text
- найденные секреты;
- уязвимости в зависимостях;
- misconfigurations в репозитории.
```

## Docker Bench Security

```text
- количество pass;
- количество warn;
- количество info;
- список применимых рекомендаций;
- список исключений, которые не относятся к учебному стенду.
```

## Инженерные метрики

```text
- опубликованные host-порты;
- наличие root/non-root user;
- наличие healthcheck;
- наличие read-only root filesystem;
- наличие cap_drop;
- наличие no-new-privileges;
- наличие pids_limit;
- наличие memory limits;
- количество сетей compose;
- размер образов.
```

## Команды сбора

```bash
./scripts/scan_trivy_image.sh
./scripts/scan_trivy_config.sh
./scripts/scan_trivy_fs.sh
./scripts/collect_baseline_metrics.sh
```
