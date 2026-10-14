# Level 8 · Linux Networking

> 🚧 **Status: partly written.** One note exists ([8.6](06-netfilter-nat-and-conntrack.md)); the other lessons are an outline. The [content audit](../00-learning-roadmap/content-audit.md) tracks them.

**Goal:** be fluent with the Linux network stack that every server, container host and Kubernetes node runs: interfaces, namespaces, routing policy, netfilter, conntrack, traffic control and the tools to inspect them.

**Start here if:** you've finished [Level 3](../03-core-networking-protocols/README.md) and done the namespace labs ([1.2](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md), [2.2](../13-hands-on-labs/lab-02.2-routing-between-two-subnets.md), [3.4](../13-hands-on-labs/lab-03.4-nat-and-port-forwarding.md)), which already use most of these tools.

⏱️ **Estimated time when written:** about 15 hours (an estimate).

## Lessons

| # | Lesson | Status | You'll be able to… |
|---|---|---|---|
| 8.1 | Interfaces and `iproute2` | planned | Manage links, addresses, routes and neighbours with `ip`; read `ip -s link` counters |
| 8.2 | Namespaces, veth pairs and bridges | planned | Build container-style networking by hand (labs 1.2 and 3.4 are the hands-on part) |
| 8.3 | Policy routing | planned | Use `ip rule` and multiple routing tables; fix asymmetric routing on multi-homed hosts |
| 8.4 | Kernel tuning with `sysctl` | planned | Forwarding, socket buffers, ephemeral ports, conntrack limits: what to change and when |
| 8.5 | Traffic control (`tc`) | planned | Shape, delay and drop traffic for testing (netem) |
| 8.6 | [Netfilter, NAT and conntrack](06-netfilter-nat-and-conntrack.md) ⭐ | **written** | MASQUERADE, SNAT and DNAT; the five netfilter hooks; conntrack; the ufw bypass with Docker |
| 8.7 | nftables | planned | Read and write nftables rules; how iptables-nft maps onto them |
| 8.8 | eBPF and XDP, an introduction | planned | What Cilium and modern tools do differently from iptables |
| 8.9 | Inspection tools in depth | planned | `ss`, `tcpdump`/`tshark` filters, `ethtool`, `nstat`, `conntrack -E` |

## Practice

| Type | Link |
|---|---|
| 🖥️ Labs that already cover Linux networking | [1.2](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md) (namespaces, bridge, `tc`) · [2.2](../13-hands-on-labs/lab-02.2-routing-between-two-subnets.md) (routing, `sysctl`) · [3.4](../13-hands-on-labs/lab-03.4-nat-and-port-forwarding.md) (iptables NAT, conntrack) · [10.1](../13-hands-on-labs/lab-10.1-docker-bridge-nat-and-dns.md) (Docker's rules) |
| 📋 Reference | [Network command cheatsheet](../references/network-commands-cheatsheet.md) |

➡️ **Next level:** [Level 9 · Cloud networking](../09-cloud-networking/README.md)
