# 01 · Docker Fundamentals

## What is Docker?

- Docker is a platform to **build, ship and run** applications as **containers**.
- A container packages the app **plus everything it needs** (runtime, libraries, config), so it runs the same on a laptop, in CI and in production.
- ⭐ Under the hood a container is just a **Linux process** with **isolation** (namespaces) and **limits** (cgroups). See [02](02-architecture-internals.md).

> **Mac note:** containers need a Linux kernel. Docker Desktop on macOS runs a small **Linux VM**, and your containers run inside it. That's why your Mac's own tools don't show container processes.

## Container vs virtual machine ⭐

| | Container | Virtual machine |
|---|---|---|
| Kernel | **Shares** the host kernel | Runs its **own** guest OS kernel |
| Isolation by | Namespaces + cgroups | Hypervisor |
| Start time | Milliseconds to seconds | Tens of seconds or more |
| Size | MBs | GBs |
| How many per host | Hundreds | Tens |
| Isolation strength | Weaker (one shared kernel) | Stronger |
| OS choice | Same kernel family (Linux containers need a Linux kernel) | Any OS |

![Virtual machines vs containers](diagrams/01-container-vs-vm.drawio.svg)

**One line to remember:** a VM virtualises the **hardware**; a container virtualises the **operating system**.

## Why use Docker?

- **Consistency:** no more "works on my machine". The same image runs everywhere.
- **Portability:** laptop, CI, cloud VM, Kubernetes.
- **Speed:** containers start in seconds, which makes deploys and scaling fast.
- **Density and cost:** many containers share one host.
- **Dependency isolation:** two apps can use different versions of Python, Node and so on.
- **Immutable artifacts:** CI builds one image and promotes it through every environment.
- **The foundation for Kubernetes**, ECS and other orchestrators.

## Key terms

| Term | Meaning |
|---|---|
| **Image** | Read-only template: filesystem layers plus metadata (default command, env, user) |
| **Container** | A running (or stopped) instance of an image, with its own writable layer |
| **Dockerfile** | Text file with the steps to build an image |
| **Layer** | One filesystem change in an image; layers are cached and shared |
| **Registry** | Server that stores images (Docker Hub, ECR, GHCR, Harbor) |
| **Repository** | A named set of related images in a registry (for example `nginx`) |
| **Tag** | A movable label for one image version (`1.27`, `latest`) |
| **Digest** | A fixed content hash (`sha256:…`) for exactly one image; it never changes |
| **Volume** | Persistent storage managed by Docker |
| **Network** | Virtual network that containers attach to |
| **dockerd** | The Docker daemon (engine) that manages everything |
| **Docker Compose** | Tool that runs multi-container apps from one YAML file |
| **OCI** | Open Container Initiative: the standards for images and runtimes |

**Analogy:** an image is like a **program file on disk**; a container is a **running process** of that program. You can start many containers from one image.

## OCI (why Docker images run everywhere)

- Docker images follow the **OCI image spec**, and containers are started with an **OCI runtime** (runc).
- So the same image runs on Docker, containerd, Podman, CRI-O and **Kubernetes**.

## Interview angle

- "What is a container, really?" → a Linux process with **namespaces** (what it can see), **cgroups** (what it can use) and its own root filesystem built from the image layers.
- "Can a Linux host run a Windows container?" → no. Containers share the host kernel.
- "Docker vs Kubernetes?" → Docker builds and runs containers on **one host**; Kubernetes **orchestrates** containers across many hosts (scheduling, self-healing, scaling).
- "Is a container secure like a VM?" → less isolated, because they share one kernel. A kernel exploit can escape the container. See [10-security](10-security.md).

## Practice

```bash
docker version
docker info
docker run hello-world
docker run -it --rm alpine sh
```

Inside the alpine container, run `ps`, `hostname` and `cat /etc/os-release`, then `exit`. Notice that `ps` shows only a few processes, with your shell as PID 1. That's the PID namespace at work.
