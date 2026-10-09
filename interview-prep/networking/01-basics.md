# 01 · Networking Basics

The building blocks used by every other file. Keep the story in mind: **a packet is a letter with a FROM and a TO address.**

## IP addresses

An IP address is **where a letter is delivered**.

| | IPv4 | IPv6 |
|---|---|---|
| Looks like | `192.168.29.1` (4 numbers, 0–255) | `2405:201:1006:e906::c0a8:1d01` (hex, much longer) |
| How many | About 4.3 billion: not enough for the world | Practically unlimited |

**On your Mac (tested):** your router has both kinds. `2405:201:…::c0a8:1d01` ends in `c0a8:1d01`, which is hex for **192.168.29.1**, the router's IPv4 address.

## Private vs public IP addresses ⭐

Some address ranges are reserved as **private**: they work only **inside** a network (a home, a VPC, a Docker host), and the internet never routes them.

| Private range (RFC 1918) | Where you've seen it |
|---|---|
| `10.0.0.0/8` | AWS VPCs (e.g. `10.0.0.0/16`) |
| `172.16.0.0/12` (172.16.x – 172.31.x) | Docker's default bridge `172.17.0.0/16`, and your Compose networks `172.18–172.20` |
| `192.168.0.0/16` | Your home Wi-Fi (`192.168.29.x`), Docker Desktop's VM (`192.168.65.x`) |

Two more special ranges that come up in AWS and EKS:

| Range | What it is |
|---|---|
| `169.254.0.0/16` (link-local) | EC2 metadata at `169.254.169.254`, the VPC DNS at `169.254.169.253` |
| `100.64.0.0/10` (shared address space) | Often used as the **secondary CIDR for pods** on EKS ([scenario deep dives](../hemant-scenario-deep-dives.md), A3) |

**Why private addresses matter:** a private address can't receive replies from the internet. Something has to swap it for a public address on the way out. That's **NAT**, in [02](02-nat.md).

## CIDR: what `/16` and `/24` mean

`172.17.0.0/16` means **the first 16 bits are fixed**; the rest are free for hosts. Addresses in the block = **2^(32 − N)**.

| CIDR | Addresses | Usable in an AWS subnet | Example |
|---|---|---|---|
| `/32` | 1 | n/a | One exact host, e.g. in a security group rule |
| `/28` | 16 | 11 | The smallest AWS subnet |
| `/24` | 256 | **251** | A typical subnet: `10.0.1.0/24` |
| `/20` | 4,096 | 4,091 | The default subnet size in a default VPC |
| `/16` | 65,536 | n/a | The largest VPC block, and Docker's default bridge |

**AWS keeps 5 addresses in every subnet:** `.0` (network), `.1` (VPC router), `.2` (DNS), `.3` (reserved for the future), and the last one (broadcast). So a `/24` has 256 − 5 = **251** usable addresses.

## Ports: the counter number

An IP address finds the **machine** (the flat). A **port** finds the **program** inside it (the counter). Ports go from 0 to 65535.

| Port | Used by |
|---|---|
| 22 | SSH |
| 53 | DNS (UDP, and TCP for large answers) |
| 80 / 443 | HTTP / HTTPS |
| 3306 · 5432 · 6379 | MySQL · PostgreSQL · Redis |
| 6443 | Kubernetes API server |
| 10250 | kubelet |
| 2379–2380 | etcd |

**Ephemeral ports:** when you connect *out*, your side uses a random temporary port, like `45000` in our examples. The range on a normal Linux server is **32768–60999** (check with `cat /proc/sys/net/ipv4/ip_local_port_range`). Docker Desktop's VM uses 55000–65535 **(tested)**.

> **AWS link ⭐:** a **NACL is stateless**, so it must allow the **return traffic to ephemeral ports** (AWS suggests 1024–65535). A security group is stateful and doesn't need this. Forgetting it gives **timeouts**.

## TCP vs UDP

| | TCP | UDP |
|---|---|---|
| Like | A **phone call**: connect first, then talk | A **postcard**: just send it |
| Setup | 3-way handshake: **SYN → SYN-ACK → ACK** | None |
| Reliable? | Yes: lost packets are resent, order is kept | No |
| Used by | HTTP, SSH, databases, the Kubernetes API | DNS (mostly), video calls, VXLAN overlays |

The **SYN** is the very first packet of a TCP connection. In the [lab](05-hands-on-lab.md), the DNAT rule's counter showed exactly **1 packet of 60 bytes**: that SYN.

## Network interfaces

An interface is a **network card**, real or virtual.

| Name | What it is |
|---|---|
| `lo` | Loopback: `127.0.0.1`, the machine talking to itself |
| `eth0` | The main network card (on Linux, and inside every container) |
| `en0` | The Wi-Fi card on your Mac |
| `docker0` | Docker's default bridge (the corridor), `172.17.0.1` |
| `br-xxxxxxxx` | One bridge per **user-defined** network (your Compose networks) |
| `vethxxxxxxx` | The host side of a container's door (veth pair) |

## `127.0.0.1` vs `0.0.0.0` ⭐ (the most common "it doesn't work" cause)

When a program **listens**, it chooses **which address** to listen on:

| Listens on | Who can connect |
|---|---|
| `127.0.0.1:8000` | **Only programs on the same machine.** In a container, that means only the same container. |
| `0.0.0.0:8000` | **Anyone who can reach any of its addresses**, including traffic arriving through `-p` |

**Proof (tested):** the same Python app, published with `-p 8081:8000`.

Listening on `127.0.0.1`, as seen with `ss -lntp` inside the container:

```
LISTEN 0  5   127.0.0.1:8000   0.0.0.0:*
```

From the Mac:

```
curl: (56) Recv failure: Connection reset by peer
```

Inside the container it worked (status 200). DNAT delivered the request to the container's **eth0** (`172.17.0.x`), but the app only listens on **lo**.

Listening on `0.0.0.0` instead:

```
LISTEN 0  5     0.0.0.0:8000   0.0.0.0:*
```

From the Mac: `200`. ✅

This is why the Flask example needs `--host=0.0.0.0`: Flask listens on `127.0.0.1` by default.

## The default gateway

The **gateway** is "where to send anything that isn't local". It's the building's exit.

| Where | Its gateway (tested) | How to see it |
|---|---|---|
| Your Mac | `192.168.29.1` (your router) | `route -n get default` |
| A container | `172.17.0.1` (docker0) | `docker exec <c> ip route` → `default via 172.17.0.1 dev eth0` |
| An AWS subnet | The route table's `0.0.0.0/0` entry: an **internet gateway** (public subnet) or a **NAT gateway** (private subnet) | The route table in the console, or `aws ec2 describe-route-tables` |

## Network namespaces: the private room

A **network namespace** is a private copy of the network stack: its own interfaces, IPs, routing table and firewall rules. A new one starts **empty** (only `lo`).

- **Docker:** every container gets its own network namespace. Docker then adds the door (veth) and connects it to the corridor (bridge). See [03](03-docker-bridge.md).
- **Kubernetes:** all containers in **one pod share one network namespace** (held by the small "pause" container). That's why containers in the same pod talk to each other on `localhost`, and why two containers in one pod can't both listen on port 80.

## Interview angle

- ⭐ "The app works inside the container but not from outside." → It listens on `127.0.0.1`, not `0.0.0.0`; or the port isn't published. Check with `ss -lntp`.
- "How many usable IPs in a `/24` subnet on AWS?" → 251, because AWS reserves 5.
- "Why do private IP ranges exist?" → There aren't enough IPv4 addresses, and private addresses aren't reachable from the internet. To go out, they need NAT.
- "Which protocol does DNS use?" → UDP port 53, and TCP for large answers.
- "How do two containers in the same pod talk?" → Over `localhost`: they share one network namespace.
- "Security group vs NACL timeouts?" → A NACL is stateless, so it must also allow the return traffic on ephemeral ports.

## Practice 🖥️ (on your Mac)

Your Mac's IP address and gateway:

```bash
ipconfig getifaddr en0
```

```bash
route -n get default
```

Programs listening on your Mac:

```bash
lsof -nP -iTCP -sTCP:LISTEN
```

A container's addresses and routes:

```bash
docker run --rm alpine ip addr
```

```bash
docker run --rm alpine ip route
```
