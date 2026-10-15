# 11 · Docker in Production

## Checklist

- [ ] Immutable image tagged with the **git SHA** (deployed by digest), private registry
- [ ] **Resource limits** · **health checks** · **restart policy** (or an orchestrator)
- [ ] Logs to **stdout/stderr**, **rotated**, shipped centrally
- [ ] **Graceful shutdown** (SIGTERM handled, exec-form CMD, [04](04-containers.md))
- [ ] Config from env or files, never baked in · hardened runtime ([10](10-security.md)) · monitoring

## Resource limits ⭐

| Flag | Effect |
|---|---|
| `--memory 512m` | Hard limit → over = **OOM-killed (137)** |
| `--memory-reservation 256m` | Soft target under host pressure |
| `--cpus 1.5` | Over → **throttled** |
| `--pids-limit 200` | Max processes / threads |

> **Kubernetes link:** `requests` (scheduler) + `limits` (these cgroups), same OOM / throttle behaviour.

## Health checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || exit 1
```

- `docker ps` shows `starting` / `healthy` / `unhealthy`. ⚠️ Plain Docker **doesn't restart** unhealthy containers (Swarm acts; Compose can wait).
- The image needs `curl` (or use the app's runtime). **Kubernetes ignores HEALTHCHECK** and uses probes.

## Logging ⭐

- Drivers: `json-file` (default), `local`, `journald`, `syslog`, `awslogs`, `fluentd`, `gelf`.
- ⚠️ **`json-file` has no size limit by default** → full disk. Set rotation, restart dockerd; applies to **new** containers only:

```json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```

- Monitoring: `docker stats`, `docker events`; properly: **cAdvisor** + node_exporter → **Prometheus** → Grafana, logs → Loki / CloudWatch (Q45–49).

## Why an orchestrator

| Need | Plain Docker | Kubernetes / ECS |
|---|---|---|
| Many hosts | ❌ | ✅ |
| Self-healing | Restart policy only | ✅ |
| Scaling, rolling updates, rollback | Manual | ✅ |
| Discovery, LB, secrets | One host, limited | ✅ |

- **Kubernetes** = standard (Hemant's focus) · **ECS** = AWS-native, simpler · **Swarm** = rarely used.

## Docker → Kubernetes ⭐

| Docker | Kubernetes |
|---|---|
| Container | Container in a **Pod** |
| `--restart always` | **Deployment** |
| `-p 8080:80` | **Service** |
| Name on a user-defined network | **Service DNS** (CoreDNS) |
| `-e`, `--env-file` | `env`, **ConfigMap**, **Secret** |
| `-v` volume | **PVC** |
| `--memory`, `--cpus` | `resources.requests` / `limits` |
| `HEALTHCHECK` | **Probes** |
| ENTRYPOINT / CMD | `command` / `args` |
| `--user`, `--read-only`, `--cap-drop` | `securityContext` |
| Compose file | Manifests / **Helm chart** |

## Interview angle

| Question | Answer |
|---|---|
| ⭐ Before running in prod? | The checklist above. |
| ⭐ Docker host disk full? | Unrotated logs, old images, stopped containers, volumes. `docker system df`. |
| HEALTHCHECK vs probes? | Kubernetes ignores HEALTHCHECK; liveness restarts, readiness controls traffic. |
| Kubernetes over Swarm? | Ecosystem, flexibility, managed offerings (EKS), community. |
