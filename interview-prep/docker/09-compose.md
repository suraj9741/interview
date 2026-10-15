# 09 · Docker Compose

![Docker Compose: one network, services found by name](diagrams/09-compose.drawio.svg)

- A **multi-container app from one YAML file** (`compose.yaml`). `docker compose` (v2, in the CLI) replaced Python `docker-compose` (v1).
- Creates a **project network**: services reach each other **by service name**.
- For **local dev and testing**; prod uses Kubernetes or ECS.

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      DATABASE_URL: postgresql://app:app@db:5432/app
      REDIS_URL: redis://cache:6379/0
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      timeout: 3s
      retries: 5

  cache:
    image: redis:7

volumes:
  db-data:
```

- Top-level `version:` is **obsolete**; leave it out.
- `depends_on` alone waits for **start**; `condition: service_healthy` waits for the **health check**.
- `app` / `app` are dev-only; real secrets go in an uncommitted `.env`.

| Command | Purpose |
|---|---|
| `docker compose up -d [--build]` | Create and start (force rebuild) |
| `docker compose ps` · `logs -f api` · `exec api sh` · `restart api` | Status · logs · shell · restart |
| `docker compose down [-v]` | Remove containers + network (⚠️ `-v` deletes volumes) |
| `docker compose config` | Final merged config |
| `docker compose pull` | Newer images |

## Env and multiple files

- `${VAR}` in `compose.yaml` comes from your shell or a `.env` **next to the file**; `env_file:` passes vars **into** the container. Commit `.env.example`, never `.env`.
- `compose.override.yaml` loads **automatically** (dev extras). Pick files: `docker compose -f compose.yaml -f compose.prod.yaml up -d` (later wins).
- **Profiles:** `profiles: ["debug"]` + `docker compose --profile debug up`.

```text
myapp/
├── compose.yaml
├── compose.override.yaml   # dev-only: bind mounts, debug ports
├── .env.example            # committed
├── .env                    # NOT committed (.gitignore)
├── Dockerfile
├── .dockerignore
└── src/
```

> **Kubernetes link:** service ≈ **Deployment + Service** · volume ≈ **PVC** · `env_file` ≈ **ConfigMap / Secret** · `healthcheck` ≈ **probes**. Compose is one host, no self-healing across machines.

## Interview angle

| Question | Answer |
|---|---|
| ⭐ Keep local dev in sync with dev env? (Q36) | Same Dockerfile/image, Compose with the **same** DB and cache versions, `make up`, env-var config, `.env.example`. |
| Does `depends_on` wait for the DB? | Only with `condition: service_healthy`; apps should retry too. |
| Compose in prod? | OK for one small server; no multi-host scheduling or self-healing. |

## Practice

Put your API, Postgres and Redis in a `compose.yaml`. `up -d` → `ps` → `logs -f api` → `down`, then `down -v` and compare.
