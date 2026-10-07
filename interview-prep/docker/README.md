# 🐳 Docker Notes: Interview Edition

My own Docker notes for the interview with Hemant (One2N). They cover the same topics as the Instagram "Docker Complete Handbook", with its mistake fixed and the deeper points Hemant usually asks about added.

## How to use these notes

- Read one file at a time, then do its **Practice** section, then answer its **Interview angle** questions **out loud**.
- ⭐ = very likely interview topic.
- 🖥️ = he may ask you to show it live.
- **Kubernetes link** boxes connect each Docker idea to Kubernetes, because he'll move from one to the other.

## Diagrams

All diagrams are in [diagrams/](diagrams/) as **`.drawio.svg`** files: a normal picture that also contains the editable draw.io diagram.

- **To view:** they appear inside the notes in the Markdown preview.
- **To edit:** open the `.drawio.svg` file in VS Code (the Draw.io Integration extension opens it as a diagram editor), or in draw.io / [app.diagrams.net](https://app.diagrams.net). When you save, the picture in the notes updates automatically.
- **To redraw them on a whiteboard in the interview:** practise drawing the architecture (02), bridge network (08) and lifecycle (04) diagrams from memory.

## Contents

| # | File | What's inside |
|---|---|---|
| 01 | [Fundamentals](01-fundamentals.md) | What Docker is, container vs VM, key terms, OCI |
| 02 | [Architecture & Internals](02-architecture-internals.md) | CLI → dockerd → containerd → runc, namespaces, cgroups, overlay2 ⭐ |
| 03 | [Images](03-images.md) | Layers, tags vs digests, base images, registries, multi-arch |
| 04 | [Containers](04-containers.md) | Lifecycle, `docker run` flags, signals, exit codes ⭐ |
| 05 | [Dockerfile](05-dockerfile.md) | Instructions, CMD vs ENTRYPOINT, ARG vs ENV, example Dockerfile ⭐ |
| 06 | [Build Optimization](06-build-optimization.md) | Build context, layer caching, multi-stage, BuildKit, CI cache |
| 07 | [Storage & Volumes](07-storage.md) | Volumes vs bind mounts vs tmpfs, backup and restore |
| 08 | [Networking](08-networking.md) | Network types, how bridge and port mapping really work, DNS ⭐ |
| 09 | [Docker Compose](09-compose.md) | compose.yaml, health checks, override files |
| 10 | [Security](10-security.md) | Image, build, runtime and host security ⭐ |
| 11 | [Production](11-production.md) | Limits, health checks, logging, restart policies, why orchestration |
| 12 | [Troubleshooting](12-troubleshooting.md) | Debugging method and common problems ⭐ |
| 13 | [Interview Questions](13-interview-questions.md) | 25 questions in Hemant's style, with short answers |
| 14 | [Docker Command List](14-docker-commands.md) | Every command by task, `docker inspect` one-liners, Docker → kubectl ⭐ |

## Related files

- [3-day prep plan](../devops-interview-prep-plan.md): Day 1 morning is Docker.
- [Hemant's past questions](../hemant-past-interview-questions.md) and [model answers](../hemant-model-answers.md): Q20, Q21 and Q58 tie into these notes.
