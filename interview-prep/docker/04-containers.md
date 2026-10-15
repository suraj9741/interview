# 04 · Docker Containers ⭐

![Container lifecycle](diagrams/04-container-lifecycle.drawio.svg)

- Container = image layers + its own **writable layer**, as an isolated process. Removed → writable layer **gone** ([07](07-storage.md)).
- States in `docker ps -a`: created, running, paused, restarting, exited, dead.

## Signals and PID 1 ⭐ (Hemant asks this)

![docker stop and PID 1](diagrams/04-pid1-signals.drawio.svg)

## Exit codes ⭐

| Code | Meaning |
|---|---|
| `0` | Success (also a clean SIGTERM shutdown) |
| `1` | App error |
| `125` | `docker run` itself failed |
| `126` | Found but not executable |
| `127` | Command not found |
| `137` | 128 + 9 = **SIGKILL**: usually **OOM**, or `docker kill` |
| `139` | 128 + 11 = SIGSEGV |
| `143` | 128 + 15 = **SIGTERM** with no handler |

`docker inspect -f '{{.State.ExitCode}} OOM={{.State.OOMKilled}}' c`

## Commands

| Command | Does |
|---|---|
| `docker run [opts] image [cmd]` | Create + start |
| `docker ps [-a]` | Running / all |
| `docker logs -f --tail 100 c` | Follow logs |
| `docker exec -it c sh` | New process **inside** its namespaces |
| `docker stop c` / `docker kill c` | SIGTERM then SIGKILL after 10 s / SIGKILL now |
| `docker start` · `restart` · `pause` · `unpause` | Pause = cgroup freezer |
| `docker rm [-f] c` | Remove (`-f` kills first, no graceful stop) |
| `docker inspect c` · `stats` · `top c` · `port c` | Details · live usage · processes · port maps |
| `docker cp c:/path ./local` | Copy in or out |
| `docker container prune` | Remove stopped containers |

## `docker run` flags

| Flag | Example |
|---|---|
| `-d` / `-it` / `--rm` / `--name` | background / interactive / auto-delete / name |
| `-p host:container` | `-p 8080:80` |
| `-e` / `--env-file` | `-e ENV=dev` |
| `-v` / `--mount` | `-v data:/var/lib/data` |
| `--network` | `--network appnet` |
| `--restart` | `no` (default) · `on-failure[:N]` · `always` · `unless-stopped` |
| `--memory` / `--cpus` | `--memory 512m --cpus 1` |
| `--user` / `--read-only` | `--user 10001` |
| `--init` | tini as PID 1 (reaps zombies) |
| `--entrypoint` | `--entrypoint sh` |

> **Kubernetes link:** pod delete = SIGTERM, wait `terminationGracePeriodSeconds` (30 s), then SIGKILL.

## Interview angle

| Question | Answer |
|---|---|
| ⭐ Exits immediately? | PID 1 finished or crashed (e.g. service started in background). Logs + exit code. |
| ⭐ Exit 137? | SIGKILL, usually OOM (`OOMKilled` in Kubernetes). |
| ⭐ 10 s to stop? | PID 1 ignores SIGTERM: shell form or no handler. |
| stop vs kill? | Graceful SIGTERM with timeout vs immediate SIGKILL. |
| How does `exec` get in? | Starts a new process in the container's existing namespaces. |

## Practice 🖥️

```bash
docker run -d --name web -p 8080:80 nginx
curl -I http://localhost:8080
docker exec -it web sh
docker stop web
docker inspect -f '{{.State.ExitCode}}' web
docker run --rm --memory 20m python:3.12-slim python -c "x = ' ' * 100_000_000"
echo $?   # 137: OOM-killed
```
