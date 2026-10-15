# 06 · Probes: Liveness, Readiness, Startup ⭐

![Probes](diagrams/06-probes.drawio.svg)

| Probe | Question | On failure |
|---|---|---|
| **Liveness** | Is the process stuck? | **Restart** the container |
| **Readiness** | Can it serve traffic **now**? | **Remove from endpoints**, no restart |
| **Startup** | Has it finished starting? | Others paused until it passes; keeps failing → restart |

| Field | Default |
|---|---|
| `initialDelaySeconds` | 0 |
| `periodSeconds` | 10 |
| `timeoutSeconds` | 1 |
| `failureThreshold` | 3 |
| `successThreshold` | 1 |

```yaml
containers:
- name: api
  image: myapi:1.0
  ports:
  - containerPort: 8080
  startupProbe:                # gives slow starts up to 30 × 10 s = 300 s
    httpGet:
      path: /healthz
      port: 8080
    failureThreshold: 30
    periodSeconds: 10
  livenessProbe:               # only "is the process alive?"
    httpGet:
      path: /healthz
      port: 8080
    periodSeconds: 10
    failureThreshold: 3
  readinessProbe:              # "can I take traffic now?"
    httpGet:
      path: /readyz
      port: 8080
    periodSeconds: 5
    failureThreshold: 2
```

## Best practices ⭐

- **Liveness checks only the container, never dependencies.** DB slow → every pod restarts → outage.
- Readiness may check a critical dependency, but all pods unready at once = no endpoints = **503**.
- Slow start → **startup probe**, not a huge `initialDelaySeconds`.
- Separate cheap endpoints: `/healthz` (liveness), `/readyz` (readiness).
- No readiness probe → traffic arrives as soon as the container starts.

> **Docker link:** Kubernetes **ignores** the Dockerfile `HEALTHCHECK` ([Docker 11](../docker/11-production.md)).

## Interview angle

| Question | Answer |
|---|---|
| ⭐ Liveness vs readiness? | Restart vs stop sending traffic. |
| ⭐ Liveness checks the DB? | Cascading restarts of every pod during a DB slowdown. |
| Java app takes 3 min, keeps getting killed? | Startup probe with `failureThreshold × periodSeconds` > 3 min. |
| Running but `0/1` READY? | Readiness failing; `describe` shows why (path, port, dependency). |

## Practice 🖥️ (break it on purpose)

1. In [practice/deploy.yaml](practice/deploy.yaml) set the readiness `path` to `/wrong`, then apply.
2. `kubectl get pods` → `0/1`. `kubectl describe pod <pod>` → `Readiness probe failed: … 404`.
3. `kubectl get endpointslices -l kubernetes.io/service-name=web` → the IP is gone.
4. Put the path back to `/` and apply again.
