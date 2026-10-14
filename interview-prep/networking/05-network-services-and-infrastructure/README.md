# Level 5 · Network Services and Infrastructure

> 📝 **Status: planned.** The lessons below are an outline; they haven't been written yet. The [content audit](../00-learning-roadmap/content-audit.md) tracks them.

**Goal:** understand the services every production network depends on, and how to run them reliably: load balancers, proxies, CDNs, DNS and DHCP at scale, time, and VPNs.

**Start here if:** you've finished [Level 3](../03-core-networking-protocols/README.md). Level 4 helps but isn't required.

⏱️ **Estimated time when written:** about 15 hours (an estimate).

## Planned lessons

| # | Lesson | You'll be able to… |
|---|---|---|
| 5.1 | Load balancing | Compare layer 4 and layer 7 load balancers, algorithms, health checks, connection draining, sticky sessions |
| 5.2 | Proxies | Forward vs reverse proxies; `X-Forwarded-For` and the PROXY protocol; corporate proxies and `HTTP_PROXY` |
| 5.3 | CDNs and anycast | How a CDN picks an edge, caches, and protects an origin |
| 5.4 | Running DNS | Authoritative hosting, split-horizon DNS, GeoDNS and failover records, resolver design |
| 5.5 | DHCP and IPAM at scale | Relays, failover, reservations; tracking address space |
| 5.6 | Time (NTP, PTP) | Why clocks matter for TLS, Kerberos and logs; how NTP picks a source |
| 5.7 | VPNs | Site-to-site vs remote access; IPsec and WireGuard; split tunnelling; MTU impact |

## Planned labs (free, in the lab container)

- A load balancer (HAProxy or nginx) in front of three backends: health checks, a failing backend, connection draining.
- A WireGuard tunnel between two namespaces, then measure its MTU.

## Related material that already exists

- [3.5 · HTTP and HTTPS](../03-core-networking-protocols/05-http-and-https.md): 502/503/504 at load balancers, `X-Forwarded-For`.
- [3.4 · DNS](../03-core-networking-protocols/04-dns.md) and [Lab 3.2](../13-hands-on-labs/lab-03.2-trace-dns-resolution.md): a full private DNS hierarchy.
- [2.8 · DHCP](../02-ip-addressing-and-subnetting/08-dhcp.md): relays and IPAM basics.
- [3.9 · Everyday protocols and ports](../03-core-networking-protocols/09-everyday-protocols-and-ports.md): NTP, SSH tunnels, VPN ports.

➡️ **Next level:** [Level 6 · Network security](../06-network-security/README.md)
