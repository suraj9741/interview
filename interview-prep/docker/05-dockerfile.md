# 05 · Dockerfile ⭐

`docker build` runs a Dockerfile top to bottom to make an image.

| Instruction | Does | Layer? |
|---|---|---|
| `FROM` | Base image; starts a stage (`AS build`) | n/a |
| `RUN` | Command at **build** time | **Yes** |
| `COPY` / `ADD` | Files from the context (ADD also unpacks tars, fetches URLs) | **Yes** |
| `WORKDIR` | Working dir for later steps and the container (`RUN cd` lasts one line only) | Metadata |
| `ENV` / `ARG` | Var at build **and** run / build only (`--build-arg`) | Metadata |
| `USER` | User for later steps and the container | Metadata |
| `EXPOSE` | **Documents** a port; `-p` publishes it | Metadata |
| `CMD` / `ENTRYPOINT` | Default args / the executable | Metadata |
| `HEALTHCHECK` · `VOLUME` · `LABEL` · `STOPSIGNAL` | Health cmd · anonymous volume · metadata · stop signal | Metadata |

## CMD vs ENTRYPOINT ⭐

![CMD vs ENTRYPOINT](diagrams/05-cmd-entrypoint.drawio.svg)

## Secrets at build time ⭐

- ⚠️ **Never ARG or ENV for secrets**: both are saved in image metadata (`docker history`, `inspect`).
- Use a **BuildKit secret**: available to one `RUN`, never stored in a layer.

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
```

```bash
docker build --secret id=npmrc,src=$HOME/.npmrc -t app .
```

## A good Dockerfile (Python API)

```dockerfile
# syntax=docker/dockerfile:1

# ---------- build stage: full image with compilers, so any package can build ----------
FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- runtime stage: only what's needed to run ----------
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
RUN useradd --create-home --uid 10001 appuser
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- **Dependencies before code** (cache, [06](06-build-optimization.md)) · **multi-stage**: gcc stays in the builder; same Debian release in both stages, and add runtime libs (e.g. `libpq`) to the final stage.
- Pinned **slim** base · **non-root** · **exec-form** CMD · health check.
- Listens on **0.0.0.0**: `127.0.0.1` is the container's own loopback, so `-p` traffic can't reach it.

## .dockerignore

```text
.git
.env
*.pem
node_modules
__pycache__
*.log
Dockerfile
.dockerignore
```

Faster builds, and secrets don't leak into the image.

## Checklist

- [ ] Pinned base version (or digest), never `latest` · small base (slim, distroless)
- [ ] Least-changing steps first · multi-stage
- [ ] `apt-get update && apt-get install` in **one** `RUN`, cleaned up in the same line
- [ ] Non-root `USER` · exec-form `CMD` / `ENTRYPOINT` · `.dockerignore`
- [ ] No secrets in ARG, ENV or COPY · one main process per container

## Interview angle

| Question | Answer |
|---|---|
| ⭐ CMD vs ENTRYPOINT? | Default args vs executable; Kubernetes `args` / `command`. |
| ⭐ COPY vs ADD? | ADD also unpacks tars and fetches URLs. Prefer COPY. |
| Does EXPOSE publish? | No, documentation only; `-p` (or a Service) publishes. |
| ⭐ Secret at build time? | BuildKit `--secret` + `RUN --mount=type=secret`. |
| Why `0.0.0.0`? | `127.0.0.1` is the container's loopback; outside traffic can't reach it. |

## Practice

Write the Dockerfile above for a small API, build it, run with `-p 8000:8000`, `curl localhost:8000/health`, then `docker history` it.
