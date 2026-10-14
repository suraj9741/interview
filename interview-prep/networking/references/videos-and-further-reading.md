# Videos and Further Reading

> **Reference.** Watch a video **before** a lesson to get the picture, then do the lesson and its lab. Books and docs are for going deeper once a level feels solid.
>
> The video links were collected from the original networking notes and the [Oct 9 interview review](../../interview-transcript-review-oct-9.md), where each one's title, channel and length were checked when it was added. The links in this file were **not re-checked** during the reorganisation; if one has moved, search for its title and channel.

## Videos, by level

| Level | Video | Channel | Length | Watch before |
|---|---|---|---|---|
| 2 | [what is an IP Address? // You SUCK at Subnetting // EP 1](https://www.youtube.com/watch?v=5WfiTHiU4x8) | NetworkChuck | 18 min | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |
| 2 | [Public vs Private IP Address](https://www.youtube.com/watch?v=po8ZFG0Xc4Q) | PowerCert | 7 min | [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) |
| 2 | [subnetting is simple](https://www.youtube.com/watch?v=ecCuyq-Wprc) | Sunny Classroom | 13 min | [2.4](../02-ip-addressing-and-subnetting/04-subnetting-step-by-step.md) |
| 3 | [DNS explained](https://www.youtube.com/watch?v=mpQZVYPuDGU) | not recorded | 6 min | [3.4](../03-core-networking-protocols/04-dns.md) |
| 3 | ⭐ [NAT Explained](https://www.youtube.com/watch?v=FTUV0t6JaDA) | PowerCert | 4 min | [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md) |
| 9 | [VPC explained](https://www.youtube.com/watch?v=TuBA5maXFgc) (title not recorded) | Server Gyan | 7 min | [Level 9](../09-cloud-networking/README.md) |
| 10 | [Docker networking is CRAZY!!](https://www.youtube.com/watch?v=bKFMS5C4CG0) | NetworkChuck | 39 min | [10.1](../10-container-and-kubernetes-networking/01-docker-bridge-networking-inside-out.md) |
| 10 | [Kubernetes Services explained: ClusterIP vs NodePort vs LoadBalancer](https://www.youtube.com/watch?v=T4Z7visMM4E) | TechWorld with Nana | 24 min | [Level 10](../10-container-and-kubernetes-networking/README.md) |
| 10 | [Life of a Packet](https://www.youtube.com/watch?v=0Omvgd7Hg1I) | Michael Rubin, Google (KubeCon) | 34 min | [Level 10](../10-container-and-kubernetes-networking/README.md) |

## Books

| Book | Why read it | Best for |
|---|---|---|
| *Computer Networking: A Top-Down Approach*, Kurose and Ross | The standard university textbook: clear explanations of every layer, starting from applications | Levels 1–4, as a second explanation of anything that didn't click |
| *TCP/IP Illustrated, Volume 1* (2nd edition), Fall and Stevens | Every protocol explained **with packet traces**, the same "capture it and read it" approach as the labs here | Levels 3 and 8, and expert-level TCP |
| *High Performance Browser Networking*, Ilya Grigorik | Latency, TCP, TLS, HTTP/2 and mobile networks from a web-performance angle. Free to read online at [hpbn.co](https://hpbn.co/) | Levels 3 and 5, performance questions |
| *Networking for Systems Administrators*, Michael W. Lucas | Short and practical: what a sysadmin actually needs | Levels 1–3, quick revision |

## Online references

| Resource | Use it for |
|---|---|
| [RFC Editor](https://www.rfc-editor.org/) | The standards themselves ([which ones matter](standards-and-rfcs.md)) |
| [Cloudflare Learning Center](https://www.cloudflare.com/learning/) | Short, accurate explainers on DNS, TLS, DDoS, CDNs and BGP |
| [Amazon VPC User Guide](https://docs.aws.amazon.com/vpc/latest/userguide/) | Vendor-specific: subnets, route tables, gateways, security groups, NACLs, limits |
| [Kubernetes: cluster networking](https://kubernetes.io/docs/concepts/cluster-administration/networking/) | The Kubernetes network model and its requirements |
| [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/) | Sockets from a programmer's side: what `connect`, `bind` and `listen` really do |
| [Wizard Zines](https://wizardzines.com/) (Julia Evans) | Friendly illustrated guides to networking tools (`tcpdump`, `dig`, HTTP) |

## Related notes in this repository

- [Docker 08 · Networking](../../docker/08-networking.md): network types, the default-bridge DNS trap, port publishing.
- Kubernetes: [08 · Services and DNS](../../kubernetes/08-services-and-dns.md), [14 · Cluster networking](../../kubernetes/14-cluster-networking.md), [17 · Troubleshooting](../../kubernetes/17-troubleshooting.md), [20 · EKS](../../kubernetes/20-eks.md).
- [Scenario deep dives](../../hemant-scenario-deep-dives.md): A2 overlapping CIDRs, A3 node vs pod CIDR, B1 and B10–B13 (network scenarios).
