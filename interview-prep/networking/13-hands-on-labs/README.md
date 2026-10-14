# 13 · Hands-On Labs 🖥️

Reading about a TCP handshake is not the same as capturing one. Every lab here builds something small, makes it work, then **breaks it on purpose** so you learn what each failure looks like.

## Start here

1. Set up the lab environment once: [00 · Lab environment setup](00-lab-environment-setup.md). It's one Docker image on your Mac (or any Ubuntu VM).
2. Do each lab **after** its lesson, in the order below.
3. Write your answers down **before** you read the expected output.

## How each lab is laid out

Objective · prerequisites · tools · topology · steps (with expected output) · expected results · verification · troubleshooting · 🧹 cleanup · challenges.

## What "tested" means here

| Label | Meaning |
|---|---|
| **(tested)** / **(tested in the lab container)** | The command was run and the output was copied from that run: Ubuntu 24.04.5, kernel 6.18, 14 Oct 2026. Addresses, ports, timings, MACs and IDs **will** differ on your run |
| **(tested on the Mac, Oct 2026)** | Run on macOS with Docker Desktop |
| **(illustrative)** | Shows the shape of the output; it was **not** captured from a real run |

**How the labs were checked (14 Oct 2026).** Labs 1.2 to 3.4 were re-run end to end by running every `bash` block in order as one script, cleanup included (Lab 2.2's step table was run step by step the same way). Lab 3.5's baseline, all eight faults and all eight fixes were run. The re-run found and fixed two problems: a `wait` in Lab 3.1 that hung on the background web server, and a capture window in Lab 2.3 too short when the client needs a second Discover. Labs 1.1 and 10.1 run on macOS with Docker Desktop and were **not** re-run; their outputs come from the original runs on the Mac (7–8 Oct 2026).

The lab container's [Dockerfile](files/netlab/Dockerfile) installs the same packages, but **the image itself was not built** during testing: the commands ran in an equivalent Ubuntu 24.04 environment. If a package is missing in yours, `apt-get install` it and please fix the Dockerfile.

## Cost

| Icon | Meaning |
|---|---|
| 💰 **free** | Runs on your own machine. Nothing to pay, nothing to clean up in a cloud account |
| 💸 **may cost money** | Creates cloud resources. Each such lab states what it creates, the expected cost, and a cleanup step. **None of the current labs do** |

## Lab index

| Lab | What you do | Runs on | Time (estimate) | Cost |
|---|---|---|---|---|
| [00 · Environment setup](00-lab-environment-setup.md) | Build and start the lab container | 💻 Mac + Docker | 20 min | 💰 free |
| **Level 1 · Fundamentals** | | | | |
| [1.1 · Inspect your own network](lab-01.1-inspect-your-own-network.md) | Find your interfaces, IP, MAC, gateway, DNS, public IP and listening ports | 💻 Mac | 20 min | 💰 free |
| [1.2 · Build a tiny network with namespaces](lab-01.2-build-a-tiny-network-with-namespaces.md) | Two PCs and a cable, then a switch; ARP, flooding, no-gateway errors; throttle a link and measure it | 🐧 lab container | 45 min | 💰 free |
| **Level 2 · IP addressing and subnetting** | | | | |
| [2.1 · Subnetting by hand, then verify](lab-02.1-subnetting-by-hand-then-verify.md) 🔥 | Classify addresses, solve 10 subnets on paper, build a VLSM plan, test summaries | 📝 paper + 🐍 Python | 60 min | 💰 free |
| [2.2 · Routing between two subnets](lab-02.2-routing-between-two-subnets.md) | Fix routing one step at a time, reading each error; TTL, traceroute, a silent hop, MTU | 🐧 lab container | 65 min | 💰 free |
| [2.3 · DHCP: capture DORA](lab-02.3-dhcp-dora-capture.md) | Run a DHCP server and client, capture Discover/Offer/Request/Ack, release | 🐧 lab container | 30 min | 💰 free |
| **Level 3 · Core protocols** | | | | |
| [3.1 · Capture a TCP handshake](lab-03.1-capture-a-tcp-handshake.md) | Handshake, close, TIME_WAIT; closed ports; DROP vs REJECT; UDP; HTTP by hand | 🐧 lab container | 60 min | 💰 free |
| [3.2 · Trace DNS resolution](lab-03.2-trace-dns-resolution.md) | Your own root, TLD and authoritative servers; caching, negative caching, search domains, four failures | 🐧 lab container | 60 min | 💰 free |
| [3.3 · TLS: certificates and the handshake](lab-03.3-tls-certificates-and-handshake.md) | Be a CA; serve HTTPS; reproduce untrusted, mismatch and expired errors; see SNI; mTLS | 🐧 lab container | 60 min | 💰 free |
| [3.4 · NAT and port forwarding](lab-03.4-nat-and-port-forwarding.md) | A home router in miniature: no NAT, MASQUERADE, conntrack, a port rewrite, DNAT | 🐧 lab container | 45 min | 💰 free |
| [3.5 · Troubleshooting challenge](lab-03.5-troubleshooting-challenge.md) ⭐🔥 | Find and fix eight hidden faults with the 6-step method ([solutions](../14-practice-exercises/solutions/lab-03.5-troubleshooting-challenge-solutions.md)) | 🐧 lab container | 2 h | 💰 free |
| **Level 10 · Containers and Kubernetes** | | | | |
| [10.1 · Docker bridge, NAT and DNS](lab-10.1-docker-bridge-nat-and-dns.md) | Look inside Docker Desktop's VM: the bridge, veth pairs, MASQUERADE, DNAT, embedded DNS, the `127.0.0.1` trap | 💻 Mac + Docker | 20 min | 💰 free |

Total for Levels 1–3: about **9 hours** of lab time (an estimate; your first lab will take longer while you learn the tools).

## Planned labs (not written yet)

These belong to modules that are still outlines. They're listed so you can see where the labs are going; the [content audit](../00-learning-roadmap/content-audit.md) tracks them.

| Planned lab | Module | Runs on | Cost |
|---|---|---|---|
| VLANs and 802.1Q trunks on a Linux bridge | [4 · Switching and routing](../04-switching-and-routing/README.md) | 🐧 lab container | 💰 free |
| Dynamic routing with FRRouting (OSPF, then BGP) | [4](../04-switching-and-routing/README.md) / [7](../07-advanced-networking/README.md) | 🐧 lab container + FRR | 💰 free |
| A load balancer with health checks (HAProxy or nginx) | [5 · Network services](../05-network-services-and-infrastructure/README.md) | 🐧 lab container | 💰 free |
| Stateful firewall rules with nftables | [6 · Network security](../06-network-security/README.md) | 🐧 lab container | 💰 free |
| A WireGuard VPN between two namespaces | [6](../06-network-security/README.md) / [7](../07-advanced-networking/README.md) | 🐧 lab container | 💰 free |
| A VPC with public and private subnets, an internet gateway and a NAT gateway | [9 · Cloud networking](../09-cloud-networking/README.md) | ☁️ AWS | 💸 **may cost money**: a NAT gateway is billed for every hour it exists (even idle) plus per GB it processes; delete it straight after |
| Pod-to-pod and Service traffic in a local cluster (kind) | [10 · Containers and Kubernetes](../10-container-and-kubernetes-networking/README.md) | 💻 Mac + Docker + kind | 💰 free |
| Flow logs and packet metrics with Prometheus | [11 · Automation and observability](../11-network-automation-and-observability/README.md) | 🐧 lab container | 💰 free |

## Safety

- The Linux labs need a **privileged** container (to create namespaces and firewall rules). They only change the container, never your Mac's network.
- Every lab ends with a **cleanup** step. If a lab breaks halfway, `ip netns list` shows what's left; `ip netns del <name>` removes each one.
- Two labs write to `/etc/netns/<name>/` (2.3 and 3.3). The cleanup removes those directories. Lab 2.3 explains why that file must exist **before** you run `dhclient`.

## Files

| Path | Used by |
|---|---|
| [files/netlab/Dockerfile](files/netlab/Dockerfile) | The lab container ([setup](00-lab-environment-setup.md)) |
| [files/lab-02.1/subnet_check.py](files/lab-02.1/subnet_check.py) | Lab 2.1, and the [Level 2 drills](../14-practice-exercises/02-level-2-subnetting-drills.md) |
| [files/lab-03.2/dns-lab.sh](files/lab-03.2/dns-lab.sh) | Lab 3.2 |
| [files/lab-03.5/broken-network.sh](files/lab-03.5/broken-network.sh) | Lab 3.5 (don't read it before you've done the challenge) |
