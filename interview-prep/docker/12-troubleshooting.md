# 12 · Docker Troubleshooting ⭐

![Container troubleshooting flowchart](diagrams/12-debug-flow.drawio.svg)

## Debugging method (say these steps in the interview)

1. **Status:** `docker ps -a`. Is it running, restarting, or exited (with which code)?
2. **Logs:** `docker logs --tail 100 c`. What did the app say before it died?
3. **Details:** `docker inspect c`. Look at `State.ExitCode`, `State.OOMKilled`, `State.Error`, the mounts, the network and the command.
4. **Look inside:** `docker exec -it c sh`. Check files, env vars and listening ports; `curl localhost`.
5. **Resources:** `docker stats`. Is it at the memory limit, or using a lot of CPU?
6. **Events:** `docker events --since 30m`. Shows OOM kills, restarts and health check changes.
7. **The host:** `docker system df` (disk) and the daemon logs (`journalctl -u docker` on Linux).

## Common problems

| Symptom | Likely cause | How to confirm / fix |
|---|---|---|
| Container **exits immediately** | The main process finished or crashed; the service runs in the background instead of the foreground | `docker logs`, exit code. Run the app in the foreground. |
| **Exit 137** | **Out of memory** (or `docker kill`) | `inspect` shows `OOMKilled=true`. Raise `--memory` or fix the leak. |
| **Exit 127** | Command not found in the image | Wrong CMD, a missing binary, or a distroless image without a shell |
| **`exec format error`** | Wrong CPU architecture (arm64 vs amd64), or a script without a `#!` shebang line | `image inspect -f '{{.Architecture}}'`, build with buildx `--platform`; add the shebang |
| **`no such file or directory`** for a script that exists | Windows line endings (CRLF), so the interpreter path ends in an invisible `\r` | Convert with `dos2unix`, or set `eol=lf` in `.gitattributes` |
| **"port is already allocated"** | Another container or process uses that host port | `docker ps`, `lsof -i :8080`. Change the host port. |
| **App unreachable from the host** | App listens on `127.0.0.1` inside the container, or no `-p` | `docker exec c ss -tlnp` or `netstat -tlnp` (slim images may not have them; use the netshoot command below). Bind to `0.0.0.0`. |
| **Can't reach another container by name** | Both are on the **default bridge** | Use a user-defined network ([08](08-networking.md)) |
| **Permission denied** on a volume or bind mount | The container's user ID doesn't own the host folder | Fix the owner, or use a matching `--user` |
| **`no space left on device`** | Logs, old images, volumes, build cache | `docker system df`, prune, log rotation |
| **Image pull fails** | Not logged in, Docker Hub rate limit, wrong name or tag, network or proxy | `docker login`, a mirror, ECR's pull-through cache |
| **Build is slow** | Cache broken by layer order, big build context | [06](06-build-optimization.md) |
| **Container stays "unhealthy"** | The health command fails (wrong port or path, `curl` not in the image) | `docker inspect -f '{{json .State.Health}}' c` |
| **Takes 10 seconds to stop** | PID 1 ignores SIGTERM | Exec-form CMD, handle SIGTERM, `--init` |

## Useful commands

```bash
docker inspect -f '{{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' c
docker inspect -f '{{json .State.Health}}' c
docker logs --since 10m c
docker events --since 30m
docker stats --no-stream
docker system df
docker system prune
docker run -it --rm --network container:c nicolaka/netshoot
```

⚠️ `docker system prune -a --volumes` deletes **all unused images and volumes**. That's data loss if a volume held important data. Look at `docker system df -v` first.

## If the container has no shell (distroless)

- Use the image's `:debug` variant, or
- start a tool container in the same namespaces: `docker run -it --rm --network container:c --pid container:c busybox sh`.

> **Kubernetes link:** the same method using `kubectl get pods` → `describe` → `logs --previous` → `exec` → `get events`, plus `kubectl debug` with an ephemeral container for distroless pods. See Day 2 of the [prep plan](../devops-interview-prep-plan.md).

## Interview angle

- ⭐ "A container keeps restarting. How do you debug it?" → the 7 steps above. Mention the exit code and OOMKilled early.
- ⭐ "Exit code 137 vs 143?" → killed by SIGKILL (often out of memory) vs killed by SIGTERM (the app didn't handle it). A clean, graceful shutdown usually exits 0.
- ⭐ "The app works inside the container but not from the browser." → the bind address (`0.0.0.0`), the `-p` mapping, then the host firewall.
- "How do you debug a container that has no shell?" → a `:debug` image, or a sidecar tool container sharing its namespaces; in Kubernetes, `kubectl debug`.

## Practice: break it and fix it 🖥️

1. Run the Python memory hog from [04](04-containers.md) with `--memory 20m` and find out why it dies. (Docker refuses limits below 6 MB, so very small values fail at start-up instead.)
2. Run a container with a typo in its command and read the exit code.
3. Run two containers on the default bridge and try to `ping` one by name. Then move both to a user-defined network and try again.
4. Run a Python web server bound to `127.0.0.1` inside a container with `-p`, and work out why `curl` from your Mac fails.
