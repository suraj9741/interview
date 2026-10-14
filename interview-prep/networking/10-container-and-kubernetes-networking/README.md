# Level 10 · Container and Kubernetes Networking

> 🚧 **Status: partly written.** One deep note and one lab exist; the other lessons are an outline. The [content audit](../00-learning-roadmap/content-audit.md) tracks them. A lot of Kubernetes networking is already covered in the [Kubernetes notes](../../kubernetes/README.md); this level will connect it to the fundamentals rather than repeat it.

**Goal:** explain, and debug, how a container gets an address and reaches the world, how `-p` publishing works, how pods talk across nodes, how Services, Ingress and DNS work inside a cluster, and how NetworkPolicy filters it all.

**Start here if:** you've finished [Level 3](../03-core-networking-protocols/README.md). [8.6 · Netfilter, NAT and conntrack](../08-linux-networking/06-netfilter-nat-and-conntrack.md) is strongly recommended.

⏱️ **Estimated time when written:** about 20 hours (an estimate).

## The idea underneath it all: network namespaces

A **network namespace** is a private copy of the network stack: its own interfaces, IP addresses, routing table and firewall rules. A new one starts **empty** (only `lo`). You built several by hand in [Lab 1.2](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md).

- **Docker:** every container gets its own network namespace. Docker then adds a "door" (a **veth pair**: one end is `eth0` inside the container, the other is attached to the host) and connects it to a "corridor" (the **bridge**, `docker0`). See [10.1](01-docker-bridge-networking-inside-out.md).
- **Kubernetes:** all containers in **one pod share one network namespace** (held by the small "pause" container). That's why containers in the same pod talk to each other on `localhost`, and why two containers in one pod can't both listen on port 80.

## The one story behind Docker networking

![Docker networking explained as an apartment building](../diagrams/00-building-story.drawio.svg)

| Real thing | In the story |
|---|---|
| Your computer (the **host**) | **The building**, with a street address (`10.0.1.25`) |
| A **container** | **A flat** inside it, with a flat number (`172.17.0.2`) that only means something inside the building |
| A **packet** | **A letter**, with a **FROM** address and a **TO** address |
| A **port** | **A counter number** inside a flat (nginx sits at counter 80) |
| **Bridge** (`docker0`) | **The corridor** that connects all the flats |
| **veth pair** | **The door** of each flat: one side inside (`eth0`), one side in the corridor |
| **iptables NAT** | **Reception**: the only place that changes addresses on letters |
| **MASQUERADE** | Reception **masks the FROM** address on letters going **out** |
| **DNAT** | Reception **changes the TO** address on letters coming **in** (only because of `-p`) |
| **conntrack** | Reception's **register**: it remembers every change, so replies find their way back |
| **DNS** | **The phonebook**: turns a name into an address |

## Lessons

| # | Lesson | Status | You'll be able to… |
|---|---|---|---|
| 10.1 | [Docker bridge networking, inside out](01-docker-bridge-networking-inside-out.md) ⭐ | **written** | Walk through `docker run -p 8080:80`: namespace, veth, bridge, routes, MASQUERADE, DNAT, docker-proxy |
| 10.2 | Docker network types and DNS | planned | Bridge, host, none, macvlan, user-defined networks and the embedded DNS server (`127.0.0.11`); for now see [Docker 08](../../docker/08-networking.md) |
| 10.3 | The Kubernetes network model | planned | The three rules (every pod gets an IP, pods reach pods without NAT, nodes reach pods) and what implements them |
| 10.4 | CNI plugins | planned | Compare routed (AWS VPC CNI), overlay (flannel VXLAN) and eBPF (Cilium) designs; IP address exhaustion |
| 10.5 | Services and kube-proxy | planned | ClusterIP, NodePort, LoadBalancer; iptables vs IPVS vs eBPF; why a Service has no process listening |
| 10.6 | Ingress and Gateway API | planned | Layer 7 routing into a cluster; TLS termination; for now see [Kubernetes 09](../../kubernetes/09-ingress-and-gateway-api.md) |
| 10.7 | DNS in the cluster | planned | CoreDNS, search domains and `ndots:5` (already in [3.4](../03-core-networking-protocols/04-dns.md#dns-inside-kubernetes-)) |
| 10.8 | NetworkPolicy | planned | Default deny, allowing DNS, debugging a policy that broke everything |
| 10.9 | Service meshes | planned | Sidecars and ambient mode, mTLS between services, what a mesh adds and costs |

## Practice

| Type | Link |
|---|---|
| 🖥️ Lab 10.1 | [Docker bridge, NAT and DNS](../13-hands-on-labs/lab-10.1-docker-bridge-nat-and-dns.md) (Mac + Docker Desktop, 20 min) |
| 🖥️ Planned | Pod-to-pod and Service traffic in a local `kind` cluster (free) |
| ✍️ Scenarios | [Docker, Kubernetes and AWS troubleshooting scenarios N1–N13](../15-interview-preparation/troubleshooting-scenarios-docker-kubernetes-aws.md) |

## Interview angle

- ⭐ "Walk me through `docker run -p 8080:80 nginx`." → [10.1](01-docker-bridge-networking-inside-out.md), interview angle.
- "How do two containers in the same pod talk?" → Over `localhost`: they share one network namespace.
- "The app works inside the container but not from outside." → It listens on `127.0.0.1`, not `0.0.0.0`, or the port isn't published ([1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md), scenario N1).

## Related notes in this repository

- [Docker 08 · Networking](../../docker/08-networking.md): network types, the default-bridge DNS trap, port publishing.
- Kubernetes: [08 · Services and DNS](../../kubernetes/08-services-and-dns.md), [09 · Ingress and Gateway API](../../kubernetes/09-ingress-and-gateway-api.md), [14 · Cluster networking](../../kubernetes/14-cluster-networking.md), [17 · Troubleshooting](../../kubernetes/17-troubleshooting.md), [20 · EKS](../../kubernetes/20-eks.md).

➡️ **Next level:** [Level 11 · Network automation and observability](../11-network-automation-and-observability/README.md)
