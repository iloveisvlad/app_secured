# Residual risks and accepted exceptions

## Summary

After hardening, the TaskOps stand uses non-root containers, read-only root filesystems, AppArmor, no-new-privileges, dropped Linux capabilities, CPU/memory/PIDs limits, healthchecks, separated Docker networks, an internal backend network, host firewalling, Docker audit rules, Docker event collection, and Falco runtime detection evidence.

The final scans show that Nginx, Redis, and PostgreSQL images have no HIGH or CRITICAL vulnerabilities. Trivy config scan reports no Dockerfile misconfigurations. Secret scan does not detect leaked secrets in the scanned project files.

Some findings remain and are documented below as residual risks or accepted exceptions.

## Trivy residual findings

### API and worker Debian OS vulnerabilities

The API and worker images still contain HIGH/CRITICAL findings in the Debian OS layer inherited from the pinned `python:3.12-slim-trixie` base image. Python package dependencies are clean for HIGH/CRITICAL findings.

These findings are kept as residual because the vulnerable packages are inherited from the upstream base image and do not currently have a safe local package-level remediation inside the selected base image. Migrating API and worker to Alpine or distroless images is possible, but it is a separate compatibility task because the application uses packages with native/runtime dependencies.

Compensating controls:
- containers run as non-root users;
- root filesystems are read-only;
- Linux capabilities are dropped;
- no-new-privileges is enabled;
- AppArmor docker-default profile is enforced;
- API and worker are not directly published to the host;
- backend services are placed on an internal Docker network;
- CPU, memory and PIDs limits are configured;
- Trivy scans are preserved as evidence.

### Starlette MEDIUM vulnerability

A previous HIGH Starlette vulnerability was fixed by upgrading FastAPI and Starlette. A remaining MEDIUM finding requires Starlette 1.0.1. It is kept as residual because Starlette 1.x may require a different FastAPI compatibility path and the current application stack is stable after the HIGH-severity remediation.

## Docker Bench residual warnings

### 2.2 Default bridge traffic restriction

The application does not use Docker's default bridge network for service-to-service communication. The Compose deployment uses dedicated frontend and backend networks, and the backend network is marked as internal. Docker Bench also reports that the default bridge `docker0` is not used by the application containers.

### 2.9 User namespace remapping

User namespace remapping was not enabled because it can break existing bind mounts and named volume ownership in the lab environment. The project instead applies non-root users, read-only root filesystems, dropped capabilities, no-new-privileges, AppArmor and resource limits for every application container.

### 2.12 Docker authorization plugin

Docker authorization plugin was not enabled. This control is mainly relevant for shared production Docker hosts or exposed Docker APIs. The lab host is single-user and Docker daemon is not exposed over TCP.

### 2.13 Centralized and remote logging

Remote centralized logging was not configured because it requires additional infrastructure such as syslog, ELK, Loki or SIEM. The stand collects runtime evidence through Docker logs, Docker events, auditd, AppArmor status and Falco trigger tests.

### 4.5 Docker Content Trust

Docker Content Trust was not enabled for local custom images. The project uses digest-pinned base images, SBOM generation, Trivy scans and image cleanup as compensating supply-chain controls.

### 5.8 Privileged host port 80

Nginx is intentionally published on host port 80 inside the VM to match the VirtualBox NAT access path used by the stand. This is accepted as a lab-specific exposure.

### 5.9 Only needed ports

Only the Nginx entrypoint is published externally. API, PostgreSQL, Redis and worker are not published to the host. The exposed Nginx port is required for application access.

## Production improvements outside the lab scope

The following controls are recommended for a production deployment but were not implemented in the lab stand:
- user namespace remapping with adjusted volume ownership;
- remote centralized logging;
- Docker authorization plugin or policy-based Docker API access;
- registry-backed image signing with a modern signing workflow;
- migration of API and worker to Alpine or distroless base images after compatibility testing;
- TLS termination with managed certificates if the service is exposed outside localhost/lab NAT.
