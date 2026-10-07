# 14 · Docker Command List

Every Docker command you're likely to need, grouped by task. Each command and flag here was checked against the `--help` output of the Docker CLI installed on your Mac (Docker 29.6, Compose v5).

**Placeholders:** `<c>` = container name or ID · `<img>` = image (`name:tag`) · `<net>` = network · `<vol>` = volume

---

## ⭐ The 20 to know by heart

| Command | What it does |
|---|---|
| `docker run -d --name web -p 8080:80 nginx:1.27` | Start a container in the background with a published port |
| `docker ps -a` | List all containers, including stopped ones |
| `docker logs -f --tail 100 <c>` | Follow the last 100 log lines |
| `docker exec -it <c> sh` | Open a shell inside a running container |
| `docker inspect <c>` | Full details: state, exit code, IP, mounts, env |
| `docker stop <c>` | Graceful stop: SIGTERM, then SIGKILL after 10 s |
| `docker rm -f <c>` | Kill and remove a container |
| `docker build -t <img> .` | Build an image from the Dockerfile here |
| `docker images` | List local images |
| `docker pull <img>` / `docker push <img>` | Download or upload an image |
| `docker tag <img> <registry>/<repo>:1.0` | Give an image a new name for a registry |
| `docker history <img>` | Show the layers and the steps that made them |
| `docker stats` | Live CPU and memory per container |
| `docker network create appnet` | Create a user-defined network (with DNS by name) |
| `docker volume create <vol>` | Create a named volume |
| `docker compose up -d` | Start every service in `compose.yaml` |
| `docker compose down` | Stop and remove them |
| `docker system df` | Disk used by images, containers, volumes and build cache |
| `docker system prune` | Remove stopped containers, unused networks, dangling images and build cache |
| `docker cp <c>:/path/file .` | Copy a file out of a container |

---

## 1. Setup and system info

| Command | What it does |
|---|---|
| `docker version` | Client and daemon (server) versions |
| `docker info` | Daemon details: storage driver, cgroup version, container and image counts |
| `docker system df` | Disk used by images, containers, volumes and build cache |
| `docker system df -v` | The same, item by item |
| `docker context ls` | Which Docker engine the CLI is talking to |
| `docker login` / `docker logout` | Sign in to or out of a registry (Docker Hub by default) |

## 2. Images

| Command | What it does |
|---|---|
| `docker pull nginx:1.27` | Download an image |
| `docker pull --platform linux/amd64 nginx:1.27` | Download a specific CPU architecture |
| `docker images` | List local images (same as `docker image ls`) |
| `docker images --digests` | Also show each image's digest |
| `docker image ls --filter dangling=true` | Untagged leftovers from old builds |
| `docker history <img>` | Layers, their sizes and the instruction behind each |
| `docker history --no-trunc <img>` | The same, with full commands |
| `docker image inspect <img>` | Full image metadata (JSON) |
| `docker image inspect -f '{{.Architecture}}' <img>` | Just the CPU architecture |
| `docker buildx imagetools inspect nginx:1.27` | Every platform inside a multi-arch image, read from the registry |
| `docker tag <img> <registry>/<repo>:1.0` | Add a new name (no copy is made) |
| `docker push <registry>/<repo>:1.0` | Upload to a registry |
| `docker rmi <img>` | Remove an image |
| `docker image prune` | Remove dangling images |
| `docker image prune -a` | Remove every image not used by a container |
| `docker save -o app.tar <img>` | Export an image to a tar file |
| `docker load -i app.tar` | Import an image from a tar file |
| `docker search nginx` | Search Docker Hub |

## 3. Build images

| Command | What it does |
|---|---|
| `docker build -t <img> .` | Build using `./Dockerfile` and the current folder as context |
| `docker build -f Dockerfile.prod -t <img> .` | Use a different Dockerfile |
| `docker build --no-cache -t <img> .` | Ignore the cache (picks up security patches) |
| `docker build --pull -t <img> .` | Always pull a newer base image first |
| `docker build --target build -t <img> .` | Stop at one stage of a multi-stage build |
| `docker build --build-arg VERSION=1.2 -t <img> .` | Pass a build argument (never a secret) |
| `docker build --secret id=npmrc,src=$HOME/.npmrc -t <img> .` | Pass a secret safely; it's never stored in a layer |
| `docker build --progress=plain -t <img> .` | Show the full build output |
| `docker buildx build --platform linux/amd64,linux/arm64 -t <registry>/<repo>:1.0 --push .` | Build for Intel and ARM in one go, then push |
| `docker buildx build --cache-from type=gha --cache-to type=gha,mode=max -t <img> .` | Reuse build cache in GitHub Actions |
| `docker builder prune` | Clear the build cache |

## 4. Run containers: `docker run` flags

| Flag | Meaning | Example |
|---|---|---|
| `-d` | Run in the background | `docker run -d nginx` |
| `-it` | Interactive with a terminal | `docker run -it ubuntu bash` |
| `--rm` | Delete the container when it exits | `docker run --rm alpine echo hi` |
| `--name` | Give it a name | `--name web` |
| `-p host:container` | Publish a port | `-p 8080:80` |
| `-p 127.0.0.1:host:container` | Publish only on the host's localhost | `-p 127.0.0.1:8080:80` |
| `-P` | Publish every `EXPOSE`d port on random host ports | `docker run -d -P nginx` |
| `-e` / `--env-file` | Set environment variables | `-e ENV=dev --env-file .env` |
| `-v` | Volume or bind mount | `-v data:/var/lib/data` · `-v "$(pwd)":/app:ro` |
| `--mount` | Same, longer and clearer syntax | `--mount type=volume,src=data,dst=/data` |
| `--tmpfs` | In-memory mount | `--tmpfs /tmp` |
| `--network` | Attach to a network (`host`, `none`, or one you created) | `--network appnet` |
| `--restart` | Restart policy: `no`, `on-failure[:N]`, `always`, `unless-stopped` | `--restart unless-stopped` |
| `--memory` / `--cpus` | Resource limits | `--memory 512m --cpus 1` |
| `--pids-limit` | Maximum number of processes | `--pids-limit 200` |
| `--user` | Run as this user | `--user 10001` |
| `--read-only` | Read-only root filesystem | `--read-only --tmpfs /tmp` |
| `--cap-drop` / `--cap-add` | Remove or add Linux capabilities | `--cap-drop ALL --cap-add NET_BIND_SERVICE` |
| `--security-opt` | Security options | `--security-opt no-new-privileges` |
| `--init` | Run tini as PID 1 (signals and zombies) | `--init` |
| `--entrypoint` | Override the image's ENTRYPOINT | `--entrypoint sh` |
| `-w` | Working directory | `-w /app` |
| `--add-host` | Add a hosts-file entry | `--add-host=host.docker.internal:host-gateway` |
| `--platform` | Run a specific CPU architecture | `--platform linux/amd64` |
| `--pull` | When to pull the image: `missing`, `always`, `never` | `--pull always` |

```bash
docker run -d --name web -p 8080:80 nginx:1.27
docker run -it --rm ubuntu bash
docker run -d --name api --network appnet --restart unless-stopped --memory 512m --cpus 1 -e ENV=prod myapi:1.0
```

## 5. Container lifecycle

| Command | What it does |
|---|---|
| `docker create --name web nginx` | Create a container without starting it |
| `docker start <c>` | Start a stopped container |
| `docker start -ai <c>` | Start it and attach to its terminal |
| `docker stop <c>` | SIGTERM, then SIGKILL after 10 seconds |
| `docker stop -t 30 <c>` | Wait up to 30 seconds before SIGKILL |
| `docker restart <c>` | Stop, then start |
| `docker kill <c>` | SIGKILL immediately |
| `docker kill -s HUP <c>` | Send a specific signal (for example, reload config) |
| `docker pause <c>` / `docker unpause <c>` | Freeze or unfreeze every process in it |
| `docker rename <c> new-name` | Rename a container |
| `docker update --memory 1g --cpus 2 <c>` | Change limits on a running container |
| `docker update --restart unless-stopped <c>` | Change the restart policy |
| `docker wait <c>` | Block until it stops, then print its exit code |
| `docker rm <c>` | Remove a stopped container |
| `docker rm -f <c>` | Kill and remove a running container (no graceful stop) |
| `docker rm -v <c>` | Also remove its anonymous volumes |
| `docker container prune` | Remove all stopped containers |

## 6. Look inside and debug

| Command | What it does |
|---|---|
| `docker ps` | Running containers |
| `docker ps -a` | All containers, including exited ones |
| `docker ps -q` | Just the IDs (useful in scripts) |
| `docker ps -s` | Include the size of each writable layer |
| `docker ps --filter status=exited` | Only exited containers |
| `docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'` | Choose the columns |
| `docker logs <c>` | Everything the container wrote to stdout and stderr |
| `docker logs -f --tail 100 <c>` | Follow, starting from the last 100 lines |
| `docker logs --since 10m -t <c>` | The last 10 minutes, with timestamps |
| `docker exec -it <c> sh` | Shell inside a running container (`bash` if the image has it) |
| `docker exec -u 0 -it <c> sh` | Shell as root, even if the container runs as another user |
| `docker exec -e DEBUG=1 -w /app <c> env` | Run one command with extra env and working directory |
| `docker attach <c>` | Attach to the main process. ⚠️ Ctrl+C stops the container; detach with Ctrl+P, Ctrl+Q |
| `docker top <c>` | Processes inside the container |
| `docker stats` / `docker stats --no-stream` | Live, or one snapshot of, CPU, memory, network and disk use |
| `docker port <c>` | Port mappings |
| `docker diff <c>` | Files added (A), changed (C) or deleted (D) in the writable layer |
| `docker cp <c>:/etc/nginx/nginx.conf .` | Copy a file out of a container |
| `docker cp ./app.conf <c>:/etc/app/` | Copy a file into a container |
| `docker events --since 30m` | Daemon events: start, die, OOM, health changes |
| `docker events --filter event=oom` | Only out-of-memory kills |
| `docker export -o rootfs.tar <c>` | Save the container's filesystem as a tar file |

## 7. `docker inspect` one-liners ⭐

| Command | Shows |
|---|---|
| `docker inspect -f '{{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' <c>` | Status, exit code and whether it was OOM-killed |
| `docker inspect -f '{{json .State.Health}}' <c>` | Health check results |
| `docker inspect -f '{{.RestartCount}}' <c>` | How many times it has restarted |
| `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <c>` | Container IP address |
| `docker inspect -f '{{json .Mounts}}' <c>` | Volumes and bind mounts |
| `docker inspect -f '{{json .Config.Env}}' <c>` | Environment variables. ⚠️ This is how secrets in env vars leak. |
| `docker inspect -f '{{.State.Pid}}' <c>` | The container's main process ID on the host |
| `docker inspect -f '{{.LogPath}}' <c>` | Where its log file lives on the host |
| `docker image inspect -f '{{json .RepoDigests}}' <img>` | The image's digest(s) |
| `docker image inspect -f '{{json .Config.Entrypoint}} {{json .Config.Cmd}}' <img>` | The image's ENTRYPOINT and CMD |

## 8. Networks

| Command | What it does |
|---|---|
| `docker network ls` | List networks |
| `docker network create appnet` | Create a user-defined bridge (containers find each other by name) |
| `docker network create --driver bridge --subnet 172.30.0.0/16 appnet` | Choose the driver and subnet |
| `docker network inspect appnet` | Subnet, gateway and attached containers |
| `docker network connect appnet <c>` | Attach a running container |
| `docker network disconnect appnet <c>` | Detach it |
| `docker network rm appnet` | Remove a network |
| `docker network prune` | Remove all unused networks |
| `docker run --network host nginx` | Use the host's network stack (Linux hosts) |
| `docker run --network none alpine` | No network at all |
| `docker run -it --rm --network container:<c> nicolaka/netshoot` | Debugging tools inside another container's network |

## 9. Volumes and mounts

| Command | What it does |
|---|---|
| `docker volume ls` | List volumes |
| `docker volume create <vol>` | Create a named volume |
| `docker volume inspect <vol>` | Mount point and driver |
| `docker volume rm <vol>` | Remove a volume |
| `docker volume prune` | Remove unused **anonymous** volumes |
| `docker volume prune -a` | Remove **all** unused volumes, named ones too ⚠️ data loss |
| `docker run -v <vol>:/data <img>` | Mount a named volume |
| `docker run -v "$(pwd)":/app:ro <img>` | Bind-mount the current folder, read-only |
| `docker run --mount type=bind,src="$(pwd)",dst=/app,readonly <img>` | The same with `--mount` (errors if the folder is missing) |
| `docker run --tmpfs /tmp <img>` | In-memory mount |

Back up and restore a volume:

```bash
docker run --rm -v <vol>:/data -v "$(pwd)":/backup alpine tar czf /backup/vol.tgz -C /data .
docker run --rm -v <vol>:/data -v "$(pwd)":/backup alpine tar xzf /backup/vol.tgz -C /data
```

## 10. Docker Compose

| Command | What it does |
|---|---|
| `docker compose up -d` | Create and start all services in the background |
| `docker compose up -d --build` | Rebuild images first |
| `docker compose up -d --force-recreate` | Recreate containers even if nothing changed |
| `docker compose ps` | Status of the services |
| `docker compose logs -f api` | Follow one service's logs (leave out the name for all) |
| `docker compose exec api sh` | Shell in a running service |
| `docker compose run --rm api pytest` | One-off command in a new container for that service |
| `docker compose build` / `docker compose pull` | Build or pull the images |
| `docker compose restart api` | Restart one service |
| `docker compose stop` / `docker compose start` | Stop or start without removing |
| `docker compose down` | Stop and remove containers and the network |
| `docker compose down -v` | Also remove volumes ⚠️ deletes data |
| `docker compose config` | Print the final merged config |
| `docker compose top` | Processes in each service |
| `docker compose ls` | Running Compose projects |
| `docker compose -f compose.yaml -f compose.prod.yaml up -d` | Combine files; later ones override earlier ones |
| `docker compose --profile debug up -d` | Also start services in the `debug` profile |
| `docker compose watch` | Rebuild or sync automatically when files change |

## 11. Registries

| Command | What it does |
|---|---|
| `docker login` | Log in to Docker Hub |
| `echo "$GITHUB_TOKEN" \| docker login ghcr.io -u <user> --password-stdin` | Log in to GitHub's registry without typing the token |
| `aws ecr get-login-password --region ap-south-1 \| docker login --username AWS --password-stdin <account>.dkr.ecr.ap-south-1.amazonaws.com` | Log in to Amazon ECR with your AWS identity |
| `docker tag <img> <account>.dkr.ecr.ap-south-1.amazonaws.com/<repo>:<git-sha>` | Name the image for ECR |
| `docker push <account>.dkr.ecr.ap-south-1.amazonaws.com/<repo>:<git-sha>` | Push it |
| `docker logout ghcr.io` | Log out of a registry |

## 12. Cleanup

| Command | Removes |
|---|---|
| `docker container prune` | Stopped containers |
| `docker image prune` | Dangling images |
| `docker image prune -a` | All images not used by a container |
| `docker volume prune` | Unused anonymous volumes |
| `docker network prune` | Unused networks |
| `docker builder prune` | Build cache |
| `docker system prune` | Stopped containers, unused networks, dangling images, build cache |
| `docker system prune -a --volumes` | ⚠️ Everything unused, including images and anonymous volumes |
| `docker image prune -a --filter until=24h` | Only unused images older than 24 hours |

Check what will go first with `docker system df -v`.

## 13. Security checks

| Command | What it does |
|---|---|
| `docker scout quickview <img>` | Summary of known vulnerabilities |
| `docker scout cves <img>` | Full vulnerability list |
| `docker scout sbom <img>` | List every package in the image |
| `docker run --rm aquasec/trivy image <img>` | Scan with Trivy (no install needed) |
| `docker run --rm --read-only --cap-drop ALL --security-opt no-new-privileges --user 10001 <img>` | Run with the main hardening flags |

## 14. Handy one-liners

| Command | What it does |
|---|---|
| `docker stop $(docker ps -q)` | Stop every running container |
| `docker rm $(docker ps -aq --filter status=exited)` | Remove every exited container |
| `docker exec -it $(docker ps -lq) sh` | Shell into the most recently created container |
| `docker ps -q \| xargs docker inspect -f '{{.Name}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'` | Name and IP of every running container |
| `docker images --format '{{.Size}}\t{{.Repository}}:{{.Tag}}'` | Image sizes |
| `docker run --rm --memory 20m python:3.12-slim python -c "x = ' ' * 100_000_000"; echo $?` | Show an OOM kill (prints `137`) |
| `docker run -it --rm --privileged --pid=host alpine nsenter -t 1 -m -u -n -i sh` | On a Mac: open a shell inside the Docker Desktop Linux VM |

Copy a file out of an image without running it:

```bash
docker create --name tmp nginx:1.27
docker cp tmp:/etc/nginx/nginx.conf .
docker rm tmp
```

## 15. Docker → Kubernetes equivalents

Hemant will move from Docker to Kubernetes, so know the matching `kubectl` command.

| Docker | Kubernetes |
|---|---|
| `docker ps` | `kubectl get pods` |
| `docker logs -f <c>` | `kubectl logs -f <pod>` (add `--previous` for the crashed container) |
| `docker exec -it <c> sh` | `kubectl exec -it <pod> -- sh` |
| `docker inspect <c>` | `kubectl describe pod <pod>` / `kubectl get pod <pod> -o yaml` |
| `docker stats` | `kubectl top pod` |
| `docker cp <c>:/path .` | `kubectl cp <pod>:/path ./path` |
| `docker run -p 8080:80 …` | `kubectl port-forward svc/<svc> 8080:80` |
| `docker run -it --rm busybox sh` | `kubectl run tmp --rm -it --image=busybox --restart=Never -- sh` |
| `docker events` | `kubectl get events --sort-by=.lastTimestamp` |
| `docker run -it --rm --network container:<c> nicolaka/netshoot` | `kubectl debug -it <pod> --image=nicolaka/netshoot` |
