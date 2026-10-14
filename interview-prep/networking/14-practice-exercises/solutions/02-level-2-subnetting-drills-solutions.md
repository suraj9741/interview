# Solutions · Level 2 Subnetting Drills

> ⚠️ Spoilers for the [Level 2 drills](../02-level-2-subnetting-drills.md). Every numeric answer here was computed and checked with Python's `ipaddress` module (the same one [`subnet_check.py`](../../13-hands-on-labs/files/lab-02.1/subnet_check.py) uses). The worked methods follow [2.3](../../02-ip-addressing-and-subnetting/03-subnet-masks-and-cidr.md), [2.4](../../02-ip-addressing-and-subnetting/04-subnetting-step-by-step.md) and [2.5](../../02-ip-addressing-and-subnetting/05-vlsm-and-route-summarization.md).

## Set A · Binary, decimal and hex

**A1.**

| Decimal | 192 | 172 | 10 | 255 | 128 | 224 | 248 | 63 |
|---|---|---|---|---|---|---|---|---|
| Binary | `11000000` | `10101100` | `00001010` | `11111111` | `10000000` | `11100000` | `11111000` | `00111111` |

Method: subtract bit values from the left (128, 64, 32, 16, 8, 4, 2, 1). 172 = 128 + 32 + 8 + 4 → `10101100`.

**A2.** `11000000` = 192 · `10101000` = 168 · `11111100` = 252 · `00001111` = 15 · `11110000` = 240 · `01111111` = 127

**A3.** 255 = `0xFF` · 172 = `0xAC` · 16 = `0x10` · 192 = `0xC0`. `0xFE` = 254 · `0x80` = 128 · `0xA9` = 169 · `0x1F` = 31.
Shortcut: one hex digit = 4 bits. 172 = `1010 1100` = `A` `C`.

**A4.** `11000000.10101000.00001010.01001101` (77 = 64 + 8 + 4 + 1).

**A5.** `/20` = `255.255.240.0` · `/27` = `255.255.255.224` · `/13` = `255.248.0.0` · `/30` = `255.255.255.252` · `/9` = `255.128.0.0`

**A6.** `255.255.248.0` = `/21` · `255.255.255.252` = `/30` · `255.224.0.0` = `/11` · `255.255.255.128` = `/25` · `255.255.192.0` = `/18`

**A7.** Not valid:
- `255.255.0.255`: a mask's 1-bits must be **contiguous** from the left. Here a block of 1s comes after 0s.
- `255.255.255.200`: 200 = `11001000`, which has a 0 between 1s.

`255.255.240.0` (`/20`) and `255.254.0.0` (`/15`) are valid. The valid values for one mask octet are only 0, 128, 192, 224, 240, 248, 252, 254, 255.

## Set B · Network, broadcast and hosts

| # | Address | Network | Broadcast | First host | Last host | Usable |
|---|---|---|---|---|---|---|
| B1 | `192.168.10.77/24` | `192.168.10.0/24` | `192.168.10.255` | `192.168.10.1` | `192.168.10.254` | 254 |
| B2 | `10.4.19.200/22` | `10.4.16.0/22` | `10.4.19.255` | `10.4.16.1` | `10.4.19.254` | 1,022 |
| B3 | `172.16.45.14/27` | `172.16.45.0/27` | `172.16.45.31` | `172.16.45.1` | `172.16.45.30` | 30 |
| B4 | `192.168.1.130/25` | `192.168.1.128/25` | `192.168.1.255` | `192.168.1.129` | `192.168.1.254` | 126 |
| B5 | `10.0.255.255/15` | `10.0.0.0/15` | `10.1.255.255` | `10.0.0.1` | `10.1.255.254` | 131,070 |
| B6 | `172.31.64.1/18` | `172.31.64.0/18` | `172.31.127.255` | `172.31.64.1` | `172.31.127.254` | 16,382 |
| B7 | `192.168.200.63/26` | `192.168.200.0/26` | `192.168.200.63` | `192.168.200.1` | `192.168.200.62` | 62 |
| B8 | `10.10.10.10/29` | `10.10.10.8/29` | `10.10.10.15` | `10.10.10.9` | `10.10.10.14` | 6 |
| B9 | `100.70.17.250/10` | `100.64.0.0/10` | `100.127.255.255` | `100.64.0.1` | `100.127.255.254` | 4,194,302 |
| B10 | `198.51.100.97/28` | `198.51.100.96/28` | `198.51.100.111` | `198.51.100.97` | `198.51.100.110` | 14 |
| B11 | `10.123.45.67/20` | `10.123.32.0/20` | `10.123.47.255` | `10.123.32.1` | `10.123.47.254` | 4,094 |
| B12 | `172.20.0.4/30` | `172.20.0.4/30` | `172.20.0.7` | `172.20.0.5` | `172.20.0.6` | 2 |

**Two worked examples.**

- **B2, `10.4.19.200/22`.** `/22` → the interesting octet is the **3rd**, mask 252, **block 4**. Multiples of 4 below 19: 0, 4, 8, 12, **16**, 20. So the network starts at `10.4.16.0`; the next one starts at `10.4.20.0`, so the broadcast is one less: `10.4.19.255`. Usable: 2^10 − 2 = 1,022.
- **B11, `10.123.45.67/20`.** `/20` → 3rd octet, mask 240, **block 16**. Multiples of 16: 0, 16, 32, 48. The largest that isn't above 45 is **32**. Network `10.123.32.0`, next `10.123.48.0`, broadcast `10.123.47.255`.

**B13.** The traps:
- **B7** `192.168.200.63/26` is the **broadcast** address of `192.168.200.0/26` (block 64: 0–63).
- **B12** `172.20.0.4/30` is the **network** address of its `/30` (block 4: 4–7).

Looks like a trap, but isn't: **B5** `10.0.255.255/15`. An address ending in `.255` is only a broadcast if all the **host bits** are 1. In a `/15`, the broadcast is `10.1.255.255`; `10.0.255.255` is an ordinary host. (Also: B9 is in `100.64.0.0/10`, the shared CGNAT range. It's a normal host address inside a provider's network, just not a private RFC 1918 one.)

## Set C · Sizing and splitting

**C1.** Find the smallest number of host bits *h* with 2^h − 2 ≥ hosts.

| Need | Host bits | Prefix | Usable |
|---|---|---|---|
| a) 500 | 9 | **`/23`** | 510 |
| b) 60 | 6 | **`/26`** | 62 |
| c) 2 | 2 | **`/30`** | 2 (or a `/31` on a point-to-point link: 2, RFC 3021) |
| d) 1,000 | 10 | **`/22`** | 1,022 |

**C2.** In AWS, usable = total − 5, and the smallest subnet is `/28`:

| Need | Prefix | AWS usable | Note |
|---|---|---|---|
| a) 500 | **`/23`** | 507 | |
| b) 60 | **`/25`** | 123 | Not `/26`: 64 − 5 = **59**, one short. The classic AWS trap |
| c) 2 | **`/28`** | 11 | AWS doesn't allow smaller than `/28` |
| d) 1,000 | **`/22`** | 1,019 | |

**C3.** 6 subnets need 3 borrowed bits (2² = 4 is too few, 2³ = 8 is enough) → **`/19`**, block 32 in the 3rd octet:
`10.0.0.0/19`, `10.0.32.0/19`, `10.0.64.0/19`, `10.0.96.0/19`, `10.0.128.0/19`, `10.0.160.0/19`, `10.0.192.0/19`, `10.0.224.0/19`. Use six, **2 spare**.

**C4.** 2^(27−24) = **8** · 2^(27−20) = **128** · 2^(24−16) = **256**.

**C5.** `172.16.0.0/24`, `172.16.1.0/24`, `172.16.2.0/24`, `172.16.3.0/24`.

**C6.** `/26` = block 64 in the 4th octet: `10.20.0.0`, `10.20.0.64`, `10.20.0.128`, `10.20.0.192`, then the 5th is **`10.20.1.0/26`** (the 4th octet wraps into the 3rd).

**C7.** Add the block size; carry into the next octet when you pass 255.
a) `10.0.64.0/20` · b) `192.168.2.0/27` · c) 252 + 4 = 256 → carry → **`172.17.0.0/22`** · d) 248 + 8 = 256, carried all the way → **`11.0.0.0/29`**.

**C8.** `192.168.4.0/23` covers `192.168.4.0`–`192.168.5.255`. `192.168.4.255` is in the **middle** of it → **valid host**. `192.168.5.255` is the **broadcast** → not valid.

**C9.** a) **No**: `10.1.2.0/24` vs `10.1.3.0/24`. b) **Yes**: both in `10.1.2.0/23`. c) **No**: `172.16.16.0/20` vs `172.16.32.0/20` (block 16: 16–31, then 32–47).

**C10.** `/31`: **2** usable, with no network or broadcast address (RFC 3021). Used on **point-to-point links** between routers, saving half the addresses of a `/30`. `/32`: **1** address. Used for a **single host**: a loopback address on a router, a host route, a firewall or security group rule for exactly one IP (`203.0.113.10/32`).

## Set D · VLSM and overlaps

**D1.** Largest first, each starting at the next free multiple of its block size:

| Need | Hosts | Prefix | Subnet | Range |
|---|---|---|---|---|
| Sales | 100 | `/25` (126) | **`10.50.0.0/25`** | .0–.127 |
| Engineering | 50 | `/26` (62) | **`10.50.0.128/26`** | .128–.191 |
| HR | 25 | `/27` (30) | **`10.50.0.192/27`** | .192–.223 |
| Management | 10 | `/28` (14) | **`10.50.0.224/28`** | .224–.239 |
| Link 1 | 2 | `/30` | **`10.50.0.240/30`** | .240–.243 |
| Link 2 | 2 | `/30` | **`10.50.0.244/30`** | .244–.247 |
| Link 3 | 2 | `/30` | **`10.50.0.248/30`** | .248–.251 |

Left over: **`10.50.0.252/30`**. (With `/31` links you'd save 6 addresses.)

**D2.** **It doesn't fit.** The smallest subnet for each need:

| Need | Prefix | Addresses |
|---|---|---|
| A: 400 | `/23` | 512 |
| B: 200 | `/24` | 256 |
| C: 100 | `/25` | 128 |
| Guests: 100 | `/25` | 128 |
| Servers: 20 | `/27` | 32 |
| **Total** | | **1,056** |

A `/22` has only **1,024** addresses. Allocating largest first fills it exactly with the first four (`192.168.8.0/23`, `192.168.10.0/24`, `192.168.11.0/25`, `192.168.11.128/25`), leaving nothing for the servers. What to change (any one is a good answer, with its trade-off):
- Use a bigger block, `192.168.8.0/21`, if it's free.
- Put the servers in a **separate** block (they often belong in a different security zone anyway).
- Shrink guests to a `/26` (62) only if 62 guests really is enough, and say so: don't silently under-size.

Spotting "this can't fit" **before** allocating is the skill: add up the block sizes first.

**D3.** Three overlapping pairs:
- `10.1.0.0/16` and `10.1.64.0/18` (the `/18` is inside the `/16`)
- `10.1.0.0/16` and `10.1.255.0/24`
- `172.16.0.0/12` and `172.31.0.0/16` (`172.16.0.0/12` runs to `172.31.255.255`)

No overlap: `10.1.64.0/18` (`10.1.64.0`–`10.1.127.255`) and `10.1.255.0/24`; `192.168.0.0/16` and `192.169.0.0/16`. Note that **`192.169.0.0/16` is public address space**, not private: only `192.168.0.0/16` is. Using it internally would break access to whoever owns it on the internet.

**D4.** **No.** `10.0.128.0/20` (`10.0.128.0`–`10.0.143.255`) lies inside `10.0.0.0/16`. AWS doesn't allow peering between VPCs with overlapping IPv4 CIDRs, and even if it did, a route to `10.0.128.0/20` in VPC A would conflict with its own local route. Fix: give one VPC a non-overlapping range (for example `10.1.0.0/16` for B). It's painful later because **a VPC's primary CIDR can't be changed**: you build a new VPC and migrate every workload. (Alternatives that avoid renumbering, such as PrivateLink for specific services, or NAT between the networks, add cost and complexity.) That's why the IP plan comes first.

**D5.** The laptop has two routes that match `172.17.5.10`: `172.16.0.0/12` via the VPN, and `172.17.0.0/16` on `docker0`. **Longest prefix match** picks the `/16`, so office traffic for `172.17.x.x` goes into Docker's bridge and never reaches the VPN. `172.20.5.0/24` only matches the `/12`, so it works.
Fixes: move Docker's networks out of the office range in `/etc/docker/daemon.json` (`"bip"` for the default bridge and `"default-address-pools"` for user-defined networks), then restart Docker; or have the VPN push a more specific route (`172.17.5.0/24`), which is a workaround rather than a fix. ([Interview scenarios](../../15-interview-preparation/troubleshooting-scenarios-docker-kubernetes-aws.md) has more Docker routing cases.)

## Set E · Summarisation and real-world design

**E1.** Eight networks, starting at 8 (a multiple of 8) → borrow back 3 bits from `/16` → **`10.8.0.0/13`** (`10.8.0.0`–`10.15.255.255`).

**E2.** Eight networks starting at 16 (a multiple of 8) → **`192.168.16.0/21`**.

**E3.** a) Exact: **`172.16.4.0/22`** (4, 5, 6, 7) **+ `172.16.8.0/24`**. Five networks never summarise into one exact prefix; and 4–8 crosses the boundary at 8.
b) Smallest single prefix: **`172.16.0.0/20`** (`172.16.0.0`–`172.16.15.255`). It also covers `172.16.0.0`–`172.16.3.255` and `172.16.9.0`–`172.16.15.255`, which aren't in your list. Advertising that could attract traffic for networks someone else uses, so only do it if that space is yours and unused.

**E4.** `10.1.1.0` and `10.1.6.255` must both be inside: block 8 in the 3rd octet covers 0–7 → **`10.1.0.0/21`**.

**E5.** Longest prefix match:
a) `10.20.30.40` → `/24` → **firewall appliance** · b) `10.20.31.1` → `/16` → **peering** · c) `10.21.0.1` → `/8` → **VPN** · d) `11.0.0.1` → only `/0` → **internet gateway**.

**E6.** a) 2^(32−12) = **1,048,576** addresses, `10.96.0.0`–`10.111.255.255`.
b) **Yes.** The VPC `10.100.0.0/16` is inside the Service range. The cluster may hand out a ClusterIP that is also a real host's IP in the VPC; traffic from pods to that address is then intercepted as Service traffic instead of reaching the host, and troubleshooting becomes confusing. Choose a Service range that overlaps nothing you route to (the VPC, peered VPCs, on-premises, VPN clients). The Pod CIDR `10.244.0.0/16` doesn't overlap the VPC.
c) A `/16` holds 2^(24−16) = **256** node `/24`s, so 256 nodes. (Each `/24` gives 254 pod addresses, more than the kubelet's default limit of 110 pods per node.)

**E7.** 2^(64−56) = **256** subnets. First `2001:db8:1234:5600::/64`, second `2001:db8:1234:5601::/64`, last **`2001:db8:1234:56ff::/64`**. The subnet ID is the two hex digits after `56`.

**E8.** One good plan. The idea: give each **region** one large, aligned block, so it can be summarised in a single route, and leave whole blocks free for growth.

| Scope | Block | Notes |
|---|---|---|
| On-premises (existing) | `10.0.0.0/12` | `10.0.0.0`–`10.15.255.255`. Untouched |
| AWS region 1 | **`10.16.0.0/12`** | One summary route from on-premises: `10.16.0.0/12` |
| · prod | `10.16.0.0/16` | |
| · staging | `10.17.0.0/16` | |
| · dev | `10.18.0.0/16` | |
| · shared services | `10.19.0.0/16` | |
| · free for new VPCs | `10.20.0.0`–`10.31.255.255` | 12 more `/16`s |
| AWS region 2 | **`10.32.0.0/12`** | Same layout: `10.32.0.0/16` prod … `10.35.0.0/16` shared |
| Region 3 (future) | `10.48.0.0/12` | Reserved, nothing allocated |
| Kubernetes Service ranges | e.g. `172.20.0.0/16` | Outside everything routed; can be reused in each cluster, because Service IPs never leave the cluster |

Why it works:
- **No overlaps**, so any VPC can later be peered or attached to a Transit Gateway with any other.
- **Aligned `/12` per region**: on-premises needs one route per region, and adding a VPC in a region doesn't change on-premises routing.
- **Room to grow** at every level: free `/16`s inside each region, and free `/12`s for new regions.
- A `/16` per VPC is AWS's maximum per CIDR block and leaves room for large subnets (Kubernetes pods using VPC IPs consume addresses fast).

Interviewers mostly listen for: "I start from the **IP plan**, avoid overlaps with on-premises and between VPCs, keep blocks **aligned** so they summarise, and leave room to grow."
