# 05 · Dockerfile ⭐

A **Dockerfile** is a text file of instructions that `docker build` runs, top to bottom, to create an image.

## Instructions

| Instruction | What it does | Creates a filesystem layer? |
|---|---|---|
| `FROM` | Base image; starts a build stage (`FROM node:20 AS build`) | n/a |
| `RUN` | Runs a command at **build** time | **Yes** |
| `COPY` | Copies files from the build context | **Yes** |
| `ADD` | Like COPY, but also unpacks local tar files and can fetch URLs | **Yes** |
| `WORKDIR` | Sets the working directory for the following steps (creates it if needed) | Metadata |
| `ENV` | Environment variable at **build and run** time | Metadata |
| `ARG` | Variable at **build time only** (`--build-arg`) | Metadata |
| `USER` | The user that following steps and the container run as | Metadata |
| `EXPOSE` | **Documents** a port. It does **not** publish it (`-p` does). | Metadata |
| `CMD` | Default command or arguments | Metadata |
| `ENTRYPOINT` | The fixed executable | Metadata |
| `HEALTHCHECK` | A command Docker runs to check health | Metadata |
| `VOLUME` | Marks a path as a volume (an anonymous volume is created at run time) | Metadata |
| `LABEL` | Key-value metadata (version, maintainer, source) | Metadata |
| `STOPSIGNAL` | The signal `docker stop` sends (default SIGTERM) | Metadata |

## CMD vs ENTRYPOINT ⭐

- **ENTRYPOINT** = *what* runs (the executable). **CMD** = the default *arguments*, or the default command if there's no ENTRYPOINT.
- `docker run image something` **replaces CMD**. `--entrypoint` replaces ENTRYPOINT.

```dockerfile
ENTRYPOINT ["python", "app.py"]
CMD ["--port", "8000"]
```

`docker run img` runs `python app.py --port 8000`. `docker run img --port 9000` runs `python app.py --port 9000`.

**Always use the exec form** `["a", "b"]`. The shell form (`CMD python app.py`) wraps your app in `/bin/sh -c`, which makes sh PID 1, and SIGTERM never reaches your app ([04](04-containers.md)).

> **Kubernetes link ⭐:** in a pod spec, `command:` **replaces ENTRYPOINT** and `args:` **replaces CMD**.

## COPY vs ADD

| | COPY | ADD |
|---|---|---|
| Local files | ✅ | ✅ |
| Auto-unpacks local `.tar` files | ❌ | ✅ |
| Downloads URLs | ❌ | ✅ |
| **Use it?** | **Default choice** | Only when you need the unpacking. It's less predictable. |

## ARG vs ENV ⭐

| | ARG | ENV |
|---|---|---|
| Available during build | ✅ | ✅ |
| Available in the running container | ❌ | ✅ |
| Set with | `docker build --build-arg V=1` | `ENV V=1`, or `-e` at run time |

⚠️ **Never pass secrets with ARG or ENV.** They're saved in the image metadata (`docker history`, `docker inspect`). Use **BuildKit secrets** instead:

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
```

```bash
docker build --secret id=npmrc,src=$HOME/.npmrc -t app .
```

The secret is available only during that one `RUN` step and is **never stored in a layer**.

## WORKDIR vs `RUN cd`

- `RUN cd /app` only lasts for **that one RUN line**. The next instruction starts back in the old directory.
- `WORKDIR /app` applies to **all following instructions** and to the running container. Always use WORKDIR.

## A good Dockerfile (Python API example)

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

Why it's good:
- **Dependencies before code**, so changing code doesn't reinstall packages ([06](06-build-optimization.md)).
- **Multi-stage**: the builder is the full `python:3.12` image (it has gcc), so any package can compile. Only the installed packages are copied into the small `-slim` image, so the compilers stay behind. Both images use the same Debian release, so the compiled packages work in both. If a package needs a system library at run time (for example `libpq`), install that library in the runtime stage too.
- **Slim base** with a **pinned version**.
- **Non-root user.**
- **Exec-form CMD.**
- A health check.
- The app listens on **0.0.0.0**, not 127.0.0.1. Otherwise nothing outside the container can reach it.

## .dockerignore

Keeps files out of the build context, which makes builds faster and stops secrets leaking into the image:

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

## Best practices checklist

- [ ] Pin the base image version (or digest). Never use `latest`.
- [ ] Use a small base image (slim or distroless).
- [ ] Order steps so the least-changing ones come first (dependencies before code).
- [ ] Use multi-stage builds.
- [ ] Combine `apt-get update && apt-get install` in **one** `RUN`, and clean up in the same line.
- [ ] Run as a non-root `USER`.
- [ ] Use exec-form `CMD` / `ENTRYPOINT`.
- [ ] Add a `.dockerignore` file.
- [ ] Keep secrets out of ARG, ENV and COPY; use BuildKit secrets.
- [ ] One main process per container.

## Interview angle

- ⭐ "CMD vs ENTRYPOINT?" → executable vs default arguments; how to override each; in Kubernetes, `command` and `args`.
- ⭐ "COPY vs ADD?" → ADD also unpacks tar files and fetches URLs. Prefer COPY.
- "Does EXPOSE publish the port?" → no, it's documentation. `-p` publishes (and in Kubernetes, a Service).
- ⭐ "How do you pass a secret at build time?" → BuildKit `--secret` with `RUN --mount=type=secret`. Never ARG or ENV.
- "Why `0.0.0.0` and not `127.0.0.1`?" → 127.0.0.1 inside the container is **the container's own loopback**, so traffic arriving through `-p` can't reach the app.

## Practice

Write the Dockerfile above for your own small API, build it, run it with `-p 8000:8000`, and check it with `curl localhost:8000/health`. Then run `docker history` on it.
