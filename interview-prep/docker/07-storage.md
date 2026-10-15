# 07 · Storage & Volumes

The writable layer is **temporary** (deleted with the container) and **slow** for heavy writes. Data that must survive lives **outside** it.

![Volume vs bind mount vs tmpfs](diagrams/07-mount-types.drawio.svg)

| | **Volume** ⭐ | **Bind mount** | **tmpfs** |
|---|---|---|---|
| Stored in | `/var/lib/docker/volumes/` | Any host path | Memory only |
| Survives `docker rm` | ✅ | ✅ | ❌ |
| Portable | ✅ (drivers for NFS, cloud disks) | ❌ | n/a |
| Best for | **Production data, databases** | **Local dev** (live reload), config | **Secrets, temp files** |

```bash
docker run -v db-data:/var/lib/postgresql/data postgres:16
docker run -v "$(pwd)/src":/app/src:ro myapp
docker run --mount type=volume,src=db-data,dst=/var/lib/postgresql/data postgres:16
docker run --mount type=bind,src="$(pwd)/src",dst=/app/src,readonly myapp
docker run --mount type=tmpfs,dst=/app/cache myapp
```

- `--mount` is clearer for scripts. Gotcha: `-v` with a missing host path **silently creates** an empty folder; `--mount type=bind` **errors**.
- **Named** (`-v data:/path`) vs **anonymous** (`-v /path` or Dockerfile `VOLUME`, random name, easy to lose).

| Command | Purpose |
|---|---|
| `docker volume create / ls / inspect / rm` | Manage volumes |
| `docker volume prune` | Remove unused volumes ⚠️ data loss |
| `docker rm -v c` | Remove container **and** its anonymous volumes |

## Backup and restore

```bash
docker run --rm -v db-data:/data -v "$(pwd)":/backup alpine tar czf /backup/db-data.tgz -C /data .
docker run --rm -v db-data:/data -v "$(pwd)":/backup alpine tar xzf /backup/db-data.tgz -C /data
```

- ⚠️ Databases: use `pg_dump` or stop the DB first; copying live files can break the backup.

## Common problems

| Symptom | Cause |
|---|---|
| Permission denied on a bind mount | Container UID (e.g. 10001) doesn't own the host folder → fix owner or `--user` |
| "My data disappeared" | Written to the writable layer, then the container was removed |
| Disk full | Old anonymous volumes and logs → `docker system df` ([12](12-troubleshooting.md)) |

> **Kubernetes link:** volume → **PVC** · bind mount → **hostPath** (avoid) · tmpfs → **`emptyDir` `medium: Memory`**. In prod prefer **RDS** over a DB in a container.

## Interview angle

| Question | Answer |
|---|---|
| ⭐ Volume vs bind mount? | Docker-managed, portable (prod data) vs a host path (dev, config). |
| Secrets on disk? | tmpfs, or a secret mounted as a file. |
| Back up a volume? | A throwaway container with tar, or the DB's dump tool. |
| Databases in containers in prod? | Possible with care; a managed service handles backups, failover, patching. |

## Practice

```bash
docker volume create pgdata
docker run -d --name pg -e POSTGRES_PASSWORD=dev -v pgdata:/var/lib/postgresql/data postgres:16
sleep 5
docker exec -it pg psql -U postgres -c "create table t(x int); insert into t values (1);"
docker rm -f pg
docker run -d --name pg2 -e POSTGRES_PASSWORD=dev -v pgdata:/var/lib/postgresql/data postgres:16
sleep 5
docker exec -it pg2 psql -U postgres -c "select * from t;"   # data survived: it's in the volume
```
