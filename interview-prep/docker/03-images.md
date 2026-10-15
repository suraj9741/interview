# 03 · Docker Images

![Image names, tags, digests, multi-arch](diagrams/03-image-anatomy.drawio.svg)

- An image = **read-only layers** + **config** (command, env, user, ports). **Immutable**: you build a new one.
- Layers are stored by **content hash**, so identical layers are stored once and shared.
- No registry → Docker Hub (`nginx` = `docker.io/library/nginx`). No tag → `latest`.

> **Kubernetes link:** deploy by digest or an immutable tag (git SHA) so every node runs the same image; turn on ECR "immutable tags".

## Image commands

| Command | Does |
|---|---|
| `docker pull nginx:1.27` | Download |
| `docker images` | List local images |
| `docker build -t app:1.0 .` | Build |
| `docker tag app:1.0 repo/app:1.0` | Add a name |
| `docker push repo/app:1.0` | Upload |
| `docker history app:1.0` | Layers and the step that made each |
| `docker image inspect app:1.0` | Config, layers, architecture |
| `docker rmi app:1.0` · `docker image prune [-a]` | Remove one / dangling (or all unused) |
| `docker save -o app.tar app:1.0` · `docker load -i app.tar` | Export / import without a registry |

## Base images

| Base | Size | Notes |
|---|---|---|
| `scratch` | 0 | Static binaries only (Go, Rust) |
| **distroless** | Tiny | Runtime only: **no shell, no package manager**; `:debug` variants for debugging |
| **alpine** | ~5 MB | **musl**, not glibc: some packages behave differently |
| **`-slim`** (debian) | Small | glibc, safe default |
| Full (`python:3.12`) | ~1 GB | Compilers included: **build stage only** |

## Registries

- **Docker Hub** rate-limits anonymous pulls: log in or mirror in CI.
- **ECR:** IAM auth, scanning, **lifecycle policies**, **immutable tags**, **pull-through cache**. Also GHCR, Harbor, Artifact Registry, ACR.

```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-south-1.amazonaws.com
```

## Interview angle

| Question | Answer |
|---|---|
| ⭐ What's a layer; why care? | Each file-changing step is a layer; cached and shared → faster builds, less storage. |
| ⭐ Why not `latest` in prod? | It moves: you can't tell what runs or roll back. Use git SHA or digest. |
| Works on Mac, `exec format error` on EC2? | arm64 vs amd64. `buildx --platform`. |
| Keep a registry clean? | ECR lifecycle: keep last 30 tagged, delete untagged after 7 days. |

## Practice

```bash
docker pull python:3.12
docker pull python:3.12-slim
docker images python
docker history python:3.12-slim
docker image inspect -f '{{.Architecture}}' python:3.12-slim
```
