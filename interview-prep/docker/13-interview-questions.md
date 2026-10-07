# 13 · Docker Interview Questions (Hemant style)

Answer each one **out loud, in under 2 minutes**, then tick it. Expect a "why?" after every answer. The file in brackets has the full explanation.

## Basics

- [ ] **1. What is a container, really?** → A Linux process with namespaces (what it sees), cgroups (what it uses) and its own root filesystem built from image layers. *Follow-up: "Then how is it different from a VM?"* → It shares the host kernel; a VM has its own. [01]
- [ ] **2. Image vs container?** → A read-only template vs a running instance with its own writable layer. Many containers can run from one image. [01, 03]
- [ ] **3. What happens when you run `docker run nginx`?** → CLI → API socket → dockerd → pull if missing → create the writable layer and network (veth, bridge, NAT) → containerd → shim → runc → nginx runs as PID 1. [02]
- [ ] **4. containerd vs runc?** → containerd manages containers; runc creates one container through the kernel and exits. Kubernetes talks to containerd through the CRI (dockershim was removed in 1.24). [02]

## Images and the Dockerfile

- [ ] **5. What is a layer, and why does instruction order matter?** → `RUN`/`COPY`/`ADD` each create a layer. Once one layer is rebuilt, every later layer is too, so put dependencies before code. [06]
- [ ] **6. CMD vs ENTRYPOINT?** → Executable vs default arguments. `docker run img x` replaces CMD; `--entrypoint` replaces ENTRYPOINT. In Kubernetes, `command` replaces ENTRYPOINT and `args` replaces CMD. Use the exec form. [05]
- [ ] **7. COPY vs ADD?** → ADD also unpacks tar files and fetches URLs. Prefer COPY. [05]
- [ ] **8. ARG vs ENV?** → Build time only vs build time and run time. Never put secrets in either; use BuildKit `--secret`. [05]
- [ ] **9. How do you make an image smaller?** → Slim or distroless base, multi-stage, clean up in the same RUN, `.dockerignore`, measure with `dive`. [06]
- [ ] **10. Why not deploy `latest`?** → It can change, so you lose traceability and reliable rollback. Use the git SHA or a digest. [03]
- [ ] **11. Works on my Mac, `exec format error` on EC2?** → arm64 vs amd64. Build for multiple platforms with buildx. [03]

## Runtime

- [ ] **12. Why does my container exit immediately?** → PID 1 finished or crashed; check the logs and exit code. A service running in the background (daemon mode) exits right away; run it in the foreground. [04]
- [ ] **13. Exit code 137? 143? 127?** → killed by SIGKILL (often out of memory); killed by SIGTERM (the app didn't handle it; a graceful exit is usually 0); command not found. [04]
- [ ] **14. Why does `docker stop` take 10 seconds?** → PID 1 doesn't handle SIGTERM: shell-form CMD, or no handler. Fix: exec form, handle the signal, `--init`. [04]
- [ ] **15. What is a zombie process, and why does PID 1 matter in containers?** → A finished child whose parent hasn't collected its exit status. PID 1 must collect them; use tini (`--init`). (Hemant Q20/Q21) [04]

## Storage and networking

- [ ] **16. Volume vs bind mount vs tmpfs?** → Docker-managed production data; a host path for development and config; memory for secrets and temporary files. [07]
- [ ] **17. ⚠️ Two containers can't reach each other by name. Why?** → They're on the default bridge, which has no DNS. Use a user-defined network; its DNS server is at 127.0.0.11. [08]
- [ ] **18. How does `-p 8080:80` actually work?** → An iptables DNAT rule forwards host port 8080 to the container's IP and port 80, through the docker0 bridge and the veth pair into the network namespace. [08]
- [ ] **19. The app runs, but I can't reach it from the host.** → It listens on 127.0.0.1 instead of 0.0.0.0, or there's no `-p`. [08, 12]
- [ ] **20. Bridge vs host network?** → Isolated with NAT vs sharing the host's network stack (faster, no isolation, port clashes). [08]

## Security and production

- [ ] **21. How do you secure a container?** → Four layers: image (minimal, scanned, signed), build (no secrets, multi-stage), runtime (non-root, read-only, drop capabilities, no-new-privileges, limits, no `--privileged`, no `docker.sock`), host (patching, docker group, TLS, rootless). [10]
- [ ] **22. Why is mounting `/var/run/docker.sock` dangerous?** → Control of the Docker API = root on the host. [02, 10]
- [ ] **23. How do secrets leak in Docker?** → ARG/ENV and image layers, `docker inspect`, logs, a committed `.env`, base64 registry logins. Use secrets mounted as files and a secret manager. (Hemant Q57) [10]
- [ ] **24. A Docker host's disk is full. What do you check?** → `docker system df`: logs without rotation, old images, stopped containers, volumes, build cache. Set `max-size` for logs. [11, 12]
- [ ] **25. Docker HEALTHCHECK vs Kubernetes probes?** → Docker only reports the status; Kubernetes ignores HEALTHCHECK and uses liveness, readiness and startup probes. [11]

## Live demo practice 🖥️ (he may ask you to share your screen)

- [ ] Build a multi-stage image and show the size difference.
- [ ] Show an OOM kill (exit 137) and find it with `docker inspect`.
- [ ] Show DNS failing on the default bridge and working on a user-defined network.
- [ ] Show a container's namespaces (`ls -l /proc/1/ns` inside it).
- [ ] Scan an image with Trivy and explain the results.
