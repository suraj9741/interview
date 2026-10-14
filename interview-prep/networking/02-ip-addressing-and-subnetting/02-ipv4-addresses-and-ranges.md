# 2.2 · IPv4 Addresses and Ranges

> **Level 2 · IP addressing and subnetting** · Lesson 2 of 8 · ⏱️ about 60 minutes (estimate)
> ⬅️ [2.1 Binary, decimal and hex](01-binary-decimal-and-hex.md) · ➡️ [2.3 Subnet masks and CIDR](03-subnet-masks-and-cidr.md)

## What you'll learn

- How an IPv4 address is built: **32 bits**, a **network part** and a **host part**.
- The old **address classes** (A, B, C, D, E), why they were dropped, and why people still mention them.
- ⭐ **Public vs private** addresses, and the three **RFC 1918** private ranges by heart.
- The **special ranges** you'll meet in real systems: loopback, link-local, CGNAT / shared, multicast, documentation.
- **Unicast, broadcast and multicast**.

## Before you start

- [2.1](01-binary-decimal-and-hex.md): binary for 0–255, and that an IPv4 address is 32 bits.
- [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md): MAC vs IP.

---

## The idea in plain words

An IPv4 address is a **32-bit number**, written as **4 octets** in decimal with dots between them: `192.168.1.10`. This is called **dotted-decimal** notation.

Like a postal address ("Flat 10, Rose Building, MG Road"), it has two parts:

| Part | Meaning | In `192.168.1.10/24` |
|---|---|---|
| **Network part** (the network ID, or **prefix**) | Which network the device is on: the same for every device in that network | `192.168.1` |
| **Host part** (the host ID) | Which device in that network | `.10` |

**Where the split falls** is not visible in the address itself. It's given separately by the **subnet mask** or the **`/24`** (prefix length). That's the whole of [2.3](03-subnet-masks-and-cidr.md). For now: `/24` = the first 24 bits are network, the last 8 are host.

## Why it matters

- Routers forward by the **network part** only. That's what lets the internet scale: a router needs one entry per network, not one per device.
- Knowing private vs public addresses explains **why NAT exists** ([3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md)), why your container's address means nothing outside your laptop, and why two VPCs can't be connected if they use the **same** range.
- The special ranges explain values you'll see daily: `127.0.0.1`, `169.254.169.254`, `100.64.x.x`.

## How it works

### Address classes (historical context)

Before 1993, the split between network and host was fixed by the **first bits** of the address. This was **classful** addressing:

| Class | First bits | First octet | Default network part | Hosts per network | Meant for |
|---|---|---|---|---|---|
| **A** | `0` | 1–126 | 8 bits (`/8`) | ~16.7 million | Huge organisations |
| **B** | `10` | 128–191 | 16 bits (`/16`) | 65,534 | Large organisations |
| **C** | `110` | 192–223 | 24 bits (`/24`) | 254 | Small networks |
| **D** | `1110` | 224–239 | n/a | n/a | **Multicast** |
| **E** | `1111` | 240–255 | n/a | n/a | Reserved / experimental |

(127 is technically in class A's range, but is reserved for loopback.)

**Why classes were abandoned:** the sizes were too coarse. A company needing 2,000 addresses was too big for a class C (254) and got a class B (65,534), wasting 63,000 addresses. The internet was running out. In 1993, **CIDR** (Classless Inter-Domain Routing, [2.3](03-subnet-masks-and-cidr.md)) replaced classes: the split can now be at **any** bit.

**Why you still hear about them:** old documentation, exam questions, and some defaults (a tool may assume `/24` for `192.168.x.x`). In modern networks, **always state the prefix length**. "It's a class C" tells you nothing about how a network is actually split.

### ⭐ Public vs private addresses

| | Public address | Private address |
|---|---|---|
| Unique… | Worldwide | Only within your own network |
| Routed on the internet? | ✅ Yes | ❌ No: internet routers drop them |
| Who assigns it | Regional registries → providers → you (or your cloud provider) | You, freely |
| Example | `8.8.8.8` (Google DNS) | `192.168.29.10` (your laptop at home) |

Some address ranges are reserved as **private** by **RFC 1918**. Anyone can use them inside their own network; nobody can use them on the internet.

| Private range (RFC 1918) | In CIDR | Addresses | Where you've seen it |
|---|---|---|---|
| `10.0.0.0` – `10.255.255.255` | `10.0.0.0/8` | 16,777,216 | AWS VPCs (e.g. `10.0.0.0/16`) |
| `172.16.0.0` – `172.31.255.255` | `172.16.0.0/12` | 1,048,576 | Docker's default bridge `172.17.0.0/16`, and Compose networks `172.18–172.20` |
| `192.168.0.0` – `192.168.255.255` | `192.168.0.0/16` | 65,536 | Your home Wi-Fi (`192.168.29.x`), Docker Desktop's VM (`192.168.65.x`) |

> ⚠️ **Classic trap:** `172.16.0.0/12` covers **172.16.x.x to 172.31.x.x only**. `172.32.0.1` is a **public** address. (Why /12 stops at 31 is a block-size question; you'll see it in [2.4](04-subnetting-step-by-step.md).)

**Why private addresses matter:** a device with a private address can't receive replies from the internet directly. Something has to swap its address for a public one on the way out. That's **NAT** ([3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md)). Private addressing plus NAT is what kept IPv4 alive long after the world ran out of public addresses.

### Special-purpose ranges

These are reserved by the IETF and recorded in IANA's special-purpose address registry. You'll meet most of them in real systems:

| Range | Name | What it's for | Where you'll see it |
|---|---|---|---|
| `0.0.0.0/8` | "This network" | `0.0.0.0` as a **source** = "I don't have an address yet" (DHCP). As a **listening** address = all interfaces ([1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md)). `0.0.0.0/0` in a route = **everything** (the default route). | DHCP, `ss -lnt`, route tables |
| `127.0.0.0/8` | **Loopback** | The machine talking to itself. Never leaves the host. | `127.0.0.1`, `localhost` |
| `169.254.0.0/16` | **Link-local** | Self-assigned when DHCP fails (APIPA); only works on the local link | A laptop with no DHCP answer; **AWS: instance metadata `169.254.169.254`**, the VPC DNS at `169.254.169.253` |
| `100.64.0.0/10` | **Shared address space** (CGNAT) | For providers doing carrier-grade NAT ([3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md)) | Mobile and ISP networks; often used as the **secondary CIDR for pods** on EKS ([scenario deep dives](../../hemant-scenario-deep-dives.md), A3) |
| `224.0.0.0/4` | **Multicast** (old class D) | One sender, many chosen receivers | Routing protocols (OSPF uses `224.0.0.5`), streaming in data centres |
| `240.0.0.0/4` | Reserved (old class E) | Not usable on the internet | n/a |
| `255.255.255.255/32` | **Limited broadcast** | "Everyone on this local network" | DHCP Discover |
| `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` | **Documentation** (TEST-NET-1/2/3) | Safe example addresses for books and docs; never routed | These notes use `203.0.113.x` as "a public address" in labs |
| `198.18.0.0/15` | Benchmarking | Network test equipment | Lab gear |

**Check any address with Python (tested in the lab container):**

```bash
python3 -c "import ipaddress as i; [print(a, i.ip_address(a).is_private, i.ip_address(a).is_global) for a in ['10.0.1.25','172.32.0.1','100.64.0.10','169.254.169.254','8.8.8.8','203.0.113.50']]"
```

```
10.0.1.25 True False
172.32.0.1 False True
100.64.0.10 False False
169.254.169.254 True False
8.8.8.8 False True
203.0.113.50 True False
```

- `172.32.0.1` → **global** (public): the trap from above, confirmed.
- `100.64.0.10` → **neither** private nor global: shared address space is its own category.
- Python's `is_private` means "**not globally routable**" (from IANA's special-purpose list), which is broader than RFC 1918: it's `True` for `169.254.x.x` and documentation ranges too.

### Network address and broadcast address

In every traditional subnet, two addresses are special and can't be given to a device:

| Address | Host bits | Meaning | In `192.168.1.0/24` |
|---|---|---|---|
| **Network address** | All **0** | The name of the subnet itself | `192.168.1.0` |
| **Broadcast address** | All **1** | "Every device in this subnet" | `192.168.1.255` |

So a `/24` has 256 addresses but **254 usable** for devices. (Exceptions for `/31` and `/32`, and AWS's extra reserved addresses, are in [2.3](03-subnet-masks-and-cidr.md).)

### Unicast, broadcast, multicast (and anycast)

| Type | One sender to… | IPv4 example |
|---|---|---|
| **Unicast** | **One** receiver | Almost all traffic: your browser to a web server |
| **Broadcast** | **Everyone** on the local network | `255.255.255.255`, or a subnet's broadcast address; ARP and DHCP use it |
| **Multicast** | **Everyone who joined a group** | `224.0.0.5` (all OSPF routers) |
| **Anycast** | The **nearest** of several receivers sharing one address | `1.1.1.1` and `8.8.8.8` are anycast: many servers worldwide announce the same address, and routing delivers you to the closest |

Broadcasts **never cross a router** ([1.2](../01-networking-fundamentals/02-network-devices.md)). IPv6 has no broadcast at all; it uses multicast instead ([2.6](06-ipv6-fundamentals.md)).

### Who hands out public addresses

**IANA** gives large blocks to five **Regional Internet Registries** (RIRs): ARIN (North America), RIPE NCC (Europe, Middle East), **APNIC (Asia-Pacific, including India)**, LACNIC (Latin America) and AFRINIC (Africa). They allocate to providers and large organisations, who assign them to customers. The registries have run out of free IPv4 addresses, or only ration the last small blocks; today IPv4 addresses are mostly re-used, transferred or **bought**. That's why AWS charges for every public IPv4 address, and why [IPv6](06-ipv6-fundamentals.md) matters.

## Worked example: classify every address in a real setup

| Address | Seen where | Public or private? | Why |
|---|---|---|---|
| `192.168.29.10` | Your laptop at home | Private (RFC 1918) | `192.168.0.0/16` |
| `192.168.29.1` | Your home router, LAN side | Private | Same range |
| `49.36.x.x` | Your router's WAN side (what websites see) | Public | Assigned by your provider; not in any private range |
| `172.17.0.2` | A Docker container | Private | Inside `172.16.0.0/12` |
| `10.0.1.25` | An EC2 instance's `eth0` | Private | `10.0.0.0/8` |
| `54.x.x.x` | The same instance's public IP | Public | Mapped by the internet gateway; **never appears on the instance's interface** |
| `169.254.169.254` | The EC2 metadata service | Link-local | Only reachable from the instance itself |

To see your own public address, ask something outside what address it sees:

```bash
curl http://checkip.amazonaws.com
```

In the [Docker lab](../13-hands-on-labs/lab-10.1-docker-bridge-nat-and-dns.md) (test 3), a container and the Mac both got **the same public IP** back: neither private address (`172.17.0.2`, `192.168.29.x`) ever reached the internet **(tested on the Mac, Oct 2026)**.

## In the real world

- **Plan private ranges so they never overlap** with anything you might connect later: other VPCs, offices, VPNs, Docker's `172.17.0.0/16`. Overlapping ranges can't be routed to each other without NAT ([scenario deep dives](../../hemant-scenario-deep-dives.md), A2). This is one of the most expensive mistakes to undo.
- **AWS VPCs** can use any RFC 1918 range, plus `100.64.0.0/10` as a secondary range. Using a public range you don't own inside a VPC is allowed but makes those real internet addresses unreachable from that VPC.
- **Kubernetes** needs two more private ranges that don't overlap the nodes': one for **pods** and one for **Services**.

## Common mistakes

| Mistake | Reality |
|---|---|
| "172.x.x.x is private." | Only **172.16–172.31**. |
| "A class C network is a /24." | Classes are obsolete. A `192.168.x.x` network can be a `/16`, `/22`, `/28`… |
| "My computer's IP is the one websites see." | At home, websites see your router's **public** IP, after NAT. |
| "169.254.x.x means the network is fine but slow." | It means **DHCP failed** and the device gave itself an address that only works on the local link. |
| "Private addresses are more secure." | They're not routable from the internet, which helps, but they're not a security control. Firewalls are. |

## Troubleshooting

| You see | It means | Next step |
|---|---|---|
| Your IP is `169.254.x.x` | No DHCP answer | Check the Wi-Fi/cable and the DHCP server ([2.8](08-dhcp.md)) |
| Your container or VPN can't reach `172.17.x.x` / `10.x.x.x` addresses in the office | An address overlap: your machine thinks that range is local (e.g. Docker's bridge) | `ip route` / `netstat -rn`, look for two routes covering the same range ([2.7](07-default-gateway-routing-table-and-arp.md)) |
| A server with a private IP can't be reached from the internet | Expected: private addresses aren't routed | Use a public IP, a load balancer, or port forwarding (NAT) |
| Two VPCs refuse to peer | Their CIDRs overlap | Re-plan the ranges, or use NAT-based options |

## Hands-on lab

- [Lab 2.1 · Subnetting by hand, then verify](../13-hands-on-labs/lab-02.1-subnetting-by-hand-then-verify.md), part A: classify addresses on paper, then check them with Python and `ipcalc`.
- [Lab 3.4 · NAT and port forwarding](../13-hands-on-labs/lab-03.4-nat-and-port-forwarding.md), step 1: watch a "public" server fail to answer a private address, before NAT is switched on.

## Interview angle

- **"Why do private IP ranges exist?"** → There aren't enough IPv4 addresses, and private addresses can be reused everywhere. They aren't routable on the internet, so to go out they need NAT.
- **"Name the private ranges."** → `10.0.0.0/8`, `172.16.0.0/12` (172.16–31), `192.168.0.0/16`. Bonus: `100.64.0.0/10` shared space, `169.254.0.0/16` link-local.
- **"What's `169.254.169.254`?"** → The link-local address of the EC2 instance metadata service (IMDS); only reachable from the instance.
- **"Why did classful addressing die?"** → Fixed sizes (/8, /16, /24) wasted huge numbers of addresses. CIDR allows any prefix length.

## Check yourself

1. Is `172.20.5.4` private or public? And `172.40.5.4`?
2. What are the network and broadcast addresses of `192.168.1.0/24`? How many usable hosts?
3. A laptop shows `169.254.33.7`. What happened?
4. Which special range might EKS use for a secondary pod CIDR?
5. Under the old class system, what class was `150.10.0.1`, and what was its default prefix?

<details>
<summary><b>Answers</b> (try first)</summary>

1. `172.20.5.4` is private (inside 172.16–31). `172.40.5.4` is public.
2. Network `192.168.1.0`, broadcast `192.168.1.255`, **254** usable.
3. It didn't get an answer from a DHCP server, so it gave itself a link-local address.
4. `100.64.0.0/10` (shared address space).
5. Class **B** (first octet 128–191), default `/16`.

</details>

## Summary

- IPv4 = **32 bits**, written as 4 decimal octets. The **prefix length** splits it into **network** and **host** parts.
- **Classes** (A/B/C/D/E) are history; **CIDR** replaced them in 1993.
- **Private (RFC 1918):** `10/8`, `172.16/12`, `192.168/16`. Not routed on the internet, so they need NAT to go out.
- Special ranges: **loopback** `127/8`, **link-local** `169.254/16`, **shared** `100.64/10`, **multicast** `224/4`, **documentation** `192.0.2/24`, `198.51.100/24`, `203.0.113/24`.
- Host bits all 0 = **network address**; all 1 = **broadcast**.

## Next

➡️ [2.3 · Subnet masks and CIDR](03-subnet-masks-and-cidr.md): how the `/N` and the mask `255.255.255.0` say where the network part ends, and how to calculate the network, broadcast and host range of any address.
