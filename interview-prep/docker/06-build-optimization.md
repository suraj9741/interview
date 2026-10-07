# 06 · Build & Build Optimization

## How `docker build` works

```bash
docker build -t app:1.0 -f Dockerfile .
```

- The `.` at the end is the **build context**: the folder that gets **sent to the builder**. `COPY` can only see files inside the context.
- A large context (with `.git`, `node_modules`, data files) makes **every build slow**. Fix it with `.dockerignore`.
- **BuildKit** is the default builder in Docker Engine 23.0 and later. It runs independent stages in parallel, skips stages you don't need, and supports secrets and cache mounts. `docker buildx` is its full CLI.

## Layer caching rules ⭐

1. Docker reuses a cached layer only if **the instruction is unchanged** and, for `COPY`/`ADD`, **the copied files' contents are unchanged** (it compares checksums).
2. Once one layer has to be rebuilt, **every layer after it is rebuilt too**.
3. So: put the steps that **rarely change at the top** and the ones that **change often at the bottom**.

```dockerfile
# ❌ Bad: any code change reinstalls all dependencies
COPY . .
RUN pip install -r requirements.txt

# ✅ Good: dependencies stay cached until requirements.txt changes
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

⚠️ **The stale apt cache trap:** a separate `RUN apt-get update` line is cached forever, so a later `apt-get install` uses an **old package list**. Always write `RUN apt-get update && apt-get install -y …` on one line.

## Multi-stage builds ⭐

Build in a big image, then copy only the result into a small image:

```dockerfile
FROM golang:1.23 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app ./cmd/api

FROM gcr.io/distroless/static-debian12
COPY --from=build /app /app
USER nonroot
ENTRYPOINT ["/app"]
```

The result: a small image (often 10–20 MB, mostly your binary), with **no compiler, no shell and no package manager**. That's smaller, faster to pull, and has far fewer vulnerabilities.

![Multi-stage build](diagrams/06-multi-stage-build.drawio.svg)

## Image size checklist

- [ ] Small base image (slim, alpine or distroless).
- [ ] Multi-stage build: no build tools in the final stage.
- [ ] Clean up **in the same `RUN`**: `apt-get install -y --no-install-recommends … && rm -rf /var/lib/apt/lists/*`. Deleting in a later layer **doesn't shrink** the image, because the earlier layer still contains the files.
- [ ] `pip install --no-cache-dir`, `npm ci --omit=dev`.
- [ ] A `.dockerignore` file.
- [ ] Find what's taking space with `docker history` or the `dive` tool.

## BuildKit cache mounts (faster rebuilds)

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
```

The download cache is kept **between builds**, but it's **not stored in the image**.

## Caching in CI ⭐

A fresh CI runner has an empty cache. Fix that by storing the cache in the registry or in the GitHub Actions cache:

```bash
docker buildx build --cache-from type=gha --cache-to type=gha,mode=max -t app:${GIT_SHA} --push .
```

Or use `type=registry,ref=repo/app:buildcache`. In GitHub Actions, `docker/build-push-action` supports the same options.

## Multi-platform builds

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t repo/app:1.0 --push .
```

## Useful build commands

| Command | Purpose |
|---|---|
| `docker build --no-cache .` | Ignore the cache (for example, to pick up security patches) |
| `docker build --target build .` | Build only up to one stage |
| `docker build --progress=plain .` | Show the full build output |
| `docker build --build-arg VERSION=1.2 .` | Pass a build argument |
| `docker builder prune` | Clear the build cache |

## Interview angle

- ⭐ "Builds are slow every time. How do you fix it?" → order the layers (dependencies first), `.dockerignore`, BuildKit cache mounts, a registry or GHA cache in CI, multi-stage builds.
- ⭐ "How do you reduce image size?" → small base, multi-stage, clean up in the same layer, `.dockerignore`, then measure with `dive`.
- "I deleted files in a later `RUN`, so why is the image still big?" → the earlier layer still contains them, because layers only add.
- "When would you use `--no-cache`?" → scheduled rebuilds that pick up base-image and OS security patches.

## Practice

1. Build your API with a single-stage `python:3.12` image and note its size.
2. Rebuild it multi-stage on `python:3.12-slim` and compare the sizes.
3. Change one line of code and rebuild. Which steps show `CACHED`?
4. Move `COPY . .` above the dependency install and rebuild again. Watch the cache break.
