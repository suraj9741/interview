# 10 · Docker Security ⭐ (part of Hemant's 🔥 security homework)

![4 security layers](diagrams/10-security-layers.drawio.svg)

## 1. Image

- Trusted minimal base, **pinned**. **Scan** in CI, fail on HIGH/CRITICAL: `trivy image app:1.0`, `docker scout cves app:1.0`, Grype; ECR scan on push.
- **SBOM** with Syft or `docker scout sbom` (`docker sbom` is deprecated). **Sign** with cosign; verify before deploy.
- **Rebuild regularly** for base-image patches, even with no code change.

## 2. Build

- No secrets in `ARG`, `ENV`, copied files or layers: **BuildKit secrets** ([05](05-dockerfile.md)). `.dockerignore` for `.env`, `.git`, `*.pem`. Multi-stage.

## 3. Runtime

| Control | How |
|---|---|
| Non-root | `USER 10001` or `--user` |
| Read-only FS | `--read-only --tmpfs /tmp` |
| Drop capabilities | `--cap-drop ALL --cap-add NET_BIND_SERVICE` |
| No privilege escalation | `--security-opt no-new-privileges` |
| Never `--privileged` | Disables nearly every protection |
| **Never mount `docker.sock`** | Control of the whole host |
| Limits | `--memory`, `--cpus`, `--pids-limit` |
| Keep seccomp / AppArmor | Never `unconfined` |
| Network | User-defined networks, publish only what's needed, bind `127.0.0.1` |

```bash
docker run -d --name api \
  --user 10001 \
  --read-only --tmpfs /tmp \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --memory 512m --cpus 1 --pids-limit 200 \
  -p 127.0.0.1:8000:8000 \
  myapi:1.0
```

## 4. Secrets at runtime, and the host

- Env vars show in `docker inspect` and `/proc/<pid>/environ`: low-risk config only. Prefer **secret files** (tmpfs, Compose secrets, Kubernetes Secrets, Secrets Manager at startup).
- Registry logins are **base64** in `~/.docker/config.json` without a credential helper (osxkeychain, `ecr-login`).
- Host: patch · **`docker` group = root** · never TCP **2375** (no TLS; 2376 has TLS) · **rootless** or `userns-remap` · `docker-bench-security` (CIS) · log rotation ([11](11-production.md)).

> **Kubernetes link ⭐:** the same in `securityContext`: `runAsNonRoot`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation: false`, `drop: ["ALL"]`; Pod Security `restricted` enforces it.

## Interview angle

| Question | Answer |
|---|---|
| ⭐ Secure a container? | The 4 layers: image, build, runtime, host. |
| ⭐ Why not root? | No user namespace by default: container root = host root after an escape. |
| ⭐ How do secrets leak? (Q57) | ARG/ENV, copied files in layers, `inspect`, logs, committed `.env`, base64 logins. |
| Why is `--privileged` dangerous? | All capabilities, host devices, no seccomp/AppArmor: ≈ host root. |
| Shift-left for containers? (Q55) | Scan, lint (hadolint), sign in CI; enforce policy at admission. |

## Practice

```bash
docker run --rm aquasec/trivy image python:3.12        # compare vulnerability counts
docker run --rm aquasec/trivy image python:3.12-slim
docker run --rm --read-only alpine touch /x             # fails: read-only FS
docker run --rm --cap-drop ALL alpine chown nobody /tmp # fails: no capabilities, even as root
```
