# 11 · Docker in Production

## Production checklist

- [ ] Immutable image, tagged with the **git SHA** (deployed by digest), from a private registry.
- [ ] **Resource limits** on every container.
- [ ] **Health checks.**
- [ ] **Restart policy** (or an orchestrator).
- [ ] Logs to **stdout/stderr**, with **rotation**, shipped centrally.
- [ ] **Graceful shutdown**: handles SIGTERM, exec-form CMD.
- [ ] Config through environment variables or mounted files, never baked into the image.
- [ ] Hardened runtime ([10-security](10-security.md)).
- [ ] Monitoring and alerts.

## Resource limits ⭐

| Flag | Effect |
|---|---|
| `--memory 512m` | Hard memory limit. Going over → **OOM-killed (exit 137)** |
| `--memory-reservation 256m` | A soft target used when the host is short of memory |
| `--cpus 1.5` | At most 1.5 CPUs' worth of time. Going over → **throttled** |
| `--pids-limit 200` | Maximum number of processes or threads |

Without limits, one leaking container can starve every other container on the host.

> **Kubernetes link:** `requests` (what the scheduler reserves) and `limits` (these cgroup caps). Same behaviour: memory over the limit → OOMKilled; CPU over the limit → throttled.

## Health checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || exit 1
```

- The status appears in `docker ps` as `starting`, `healthy` or `unhealthy`.
- ⚠️ Plain Docker **does not restart** unhealthy containers. It only reports the status. Swarm acts on it, and Compose can wait for it.
- The image needs `curl` (or use your app's own runtime) for the check to work.

> **Kubernetes link ⭐:** Kubernetes **ignores** the Dockerfile `HEALTHCHECK` and uses its own **liveness, readiness and startup probes** instead.

## Logging ⭐

- Apps should log to **stdout/stderr**. Docker captures it with a **logging driver**.
- Drivers: `json-file` (default), `local`, `journald`, `syslog`, `awslogs` (CloudWatch), `fluentd`, `gelf`.
- ⚠️ **The default `json-file` driver has no size limit**, so logs can **fill the disk**. Set rotation in `/etc/docker/daemon.json`, then restart the Docker daemon. It applies only to containers created **after** that:

```json
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```

- Commands: `docker logs -f --tail 100 c`, `docker logs --since 10m c`.

## Monitoring

- Quick look: `docker stats`, `docker events`.
- Proper monitoring: **cAdvisor** (per-container metrics) + **node_exporter** → **Prometheus** → **Grafana**; logs → **Loki** or CloudWatch. (See Hemant's Q45–49 in the model answers.)

## Graceful shutdown

1. `docker stop` sends **SIGTERM** (or the image's `STOPSIGNAL`).
2. The app stops taking new requests, finishes the ones in flight, closes database connections and exits.
3. After the timeout (`docker stop -t 30`, 10 seconds by default) Docker sends **SIGKILL**.

Requirements: exec-form CMD, an app that handles SIGTERM, and `--init` if the app starts child processes.

## Why you need an orchestrator

Plain Docker runs containers on **one host**. Production needs:

| Need | Plain Docker | Orchestrator (Kubernetes / ECS / Swarm) |
|---|---|---|
| Spread containers across many hosts | ❌ | ✅ |
| Self-healing (replace failed containers or hosts) | Restart policy only | ✅ |
| Scaling | Manual | ✅ Autoscaling |
| Rolling updates and rollback | Manual | ✅ |
| Service discovery and load balancing | Single host only | ✅ |
| Secrets and config management | Limited | ✅ |

**Kubernetes** is the industry standard and Hemant's focus. **ECS** is AWS-native and simpler. **Docker Swarm** is easy but rarely used now; know only that it exists.

## Docker → Kubernetes mapping ⭐

| Docker | Kubernetes |
|---|---|
| Container | Container inside a **Pod** |
| `docker run --restart always` | **Deployment** (self-healing ReplicaSet) |
| `-p 8080:80` | **Service** (ClusterIP / NodePort / LoadBalancer) |
| Container name on a user-defined network | **Service DNS name** through CoreDNS |
| `-e`, `--env-file` | `env`, **ConfigMap**, **Secret** |
| `-v` volume | **PersistentVolumeClaim** |
| `--memory`, `--cpus` | `resources.requests` / `limits` |
| `HEALTHCHECK` | **liveness / readiness / startup probes** |
| ENTRYPOINT / CMD | `command` / `args` |
| `--user`, `--read-only`, `--cap-drop` | `securityContext` |
| Compose file | Manifests or a **Helm chart** |

## Interview angle

- ⭐ "What do you need before running containers in production?" → walk through the checklist at the top.
- ⭐ "The disk filled up on a Docker host. Why?" → container logs (no rotation), old images, stopped containers, unused volumes. Check `docker system df`.
- "Docker HEALTHCHECK vs Kubernetes probes?" → Kubernetes ignores HEALTHCHECK. Probes are richer: liveness restarts, readiness controls traffic.
- "Why Kubernetes over Swarm?" → ecosystem, flexibility, managed offerings (EKS), and community.
