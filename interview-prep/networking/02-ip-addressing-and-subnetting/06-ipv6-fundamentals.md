# 2.6 · IPv6 Fundamentals

> **Level 2 · IP addressing and subnetting** · Lesson 6 of 8 · ⏱️ about 90 minutes (estimate)
> ⬅️ [2.5 VLSM and route summarisation](05-vlsm-and-route-summarization.md) · ➡️ [2.7 Default gateway, routing table and ARP](07-default-gateway-routing-table-and-arp.md)

## What you'll learn

- Why IPv6 exists and what changed from IPv4.
- How to **read, shorten and expand** an IPv6 address (the `::` rules).
- The **prefix** structure: why every LAN is a **`/64`**, and what a `/48` or `/56` gives you.
- The address **types**: global, unique local, **link-local**, multicast, loopback.
- How devices get addresses (**SLAAC** and **DHCPv6**), and how **NDP** replaces ARP.
- **Dual stack**, and what IPv6 means in AWS, Docker and Kubernetes.

## Before you start

- [2.1](01-binary-decimal-and-hex.md): hexadecimal (4 bits per hex digit).
- [2.2](02-ipv4-addresses-and-ranges.md) and [2.3](03-subnet-masks-and-cidr.md): network and host parts, prefix lengths.

---

## The idea in plain words

IPv4 has about 4.3 billion addresses, and the world ran out ([2.2](02-ipv4-addresses-and-ranges.md#who-hands-out-public-addresses)). NAT stretched it, at the cost of complexity ([3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md)).

**IPv6** uses **128-bit** addresses: 2¹²⁸ ≈ 3.4 × 10³⁸. That's enough to give **every LAN in the world** a block of 2⁶⁴ addresses (18 quintillion) and never run out. With that much space:

- every device can have a **real, globally unique address**, so **NAT isn't needed**;
- subnetting becomes simpler: **almost every LAN is a `/64`**;
- devices can **configure their own address** from what the router advertises.

IPv6 is not a "bigger IPv4" you switch on. It's a **separate protocol** that runs **alongside** IPv4 (dual stack) on most networks today.

## Why it matters

- Your home already uses it: your Mac's DNS server is an IPv6 address (below).
- Mobile networks and large providers run mostly on IPv6.
- **AWS charges for every public IPv4 address**; IPv6 addresses are free, and **EKS can run IPv6 clusters** to escape pod IP exhaustion ([scenario deep dives](../../hemant-scenario-deep-dives.md), A2 option 5).
- Things behave differently: no broadcast, no ARP, no NAT by default, so **firewall rules matter more**.

## Reading an IPv6 address

128 bits, written as **8 groups of 4 hex digits** (each group = 16 bits), separated by colons:

```
2405:0201:1006:e906:0000:0000:c0a8:1d01
```

### Two rules for shortening

1. **Drop leading zeros in any group:** `0201` → `201`, `0000` → `0`.
2. **Replace one run of consecutive all-zero groups with `::`** (only **once** per address, otherwise you couldn't tell how many zeros each `::` stands for).

```
2405:0201:1006:e906:0000:0000:c0a8:1d01
2405:201:1006:e906:0:0:c0a8:1d01        (rule 1)
2405:201:1006:e906::c0a8:1d01           (rule 2)
```

**The standard way to write it (RFC 5952):** lowercase; shorten the **longest** run of zeros; if two runs are equal, shorten the **first**; don't use `::` for a single zero group.

**Check with Python (tested in the lab container):**

```bash
python3 -c "import ipaddress as i; a=i.ip_address('2001:0db8:0000:0000:0000:ff00:0042:8329'); print(a.compressed); print(a.exploded)"
```

```
2001:db8::ff00:42:8329
2001:0db8:0000:0000:0000:ff00:0042:8329
```

And the tie rule: `2001:db8:0:0:1:0:0:1` compresses to **`2001:db8::1:0:0:1`** (the first of two equal runs) **(tested in the lab container)**.

**Your own router (tested on the Mac, Oct 2026):** `nslookup` reported its DNS server as `2405:201:1006:e906::c0a8:1d01`. Expanded, that's `2405:0201:1006:e906:0000:0000:c0a8:1d01`. The last 32 bits, `c0a8:1d01`, are hex for **192.168.29.1**: your router chose an interface ID that embeds its IPv4 address ([2.1](01-binary-decimal-and-hex.md#hexadecimal-base-16)).

### Ports and URLs

Because colons are already used, an IPv6 address with a port is written in **square brackets**: `[2001:db8::1]:443`, and in a URL `https://[2001:db8::1]/`.

## The structure: prefix and interface ID

A typical **global unicast** address splits like this:

```
| 48 bits: global routing prefix | 16 bits: subnet ID | 64 bits: interface ID |
|   given to your site by the ISP | your subnets      | the device              |
|<-------------- 64-bit network prefix ------------->|
```

- **`/64` is the standard subnet size.** SLAAC (below) only works on a `/64`. Don't make LANs smaller.
- A site typically gets a **`/48`** (65,536 subnets of `/64`) or a **`/56`** (256 subnets) from its provider. Homes often get a `/56` or `/64`.
- **AWS:** a VPC gets a `/56`; each subnet a `/64` (or larger prefixes in recent options).

**IPv6 subnetting is easier:** you almost never calculate host counts (every `/64` is "enough"). You just number subnets in the 16-bit subnet ID:

```bash
python3 -c "import ipaddress as i; n=i.ip_network('2001:db8:abcd::/48'); print(2**(64-48), list(n.subnets(new_prefix=64))[:3])"
```

**Output (tested in the lab container):**

```
65536 [IPv6Network('2001:db8:abcd::/64'), IPv6Network('2001:db8:abcd:1::/64'), IPv6Network('2001:db8:abcd:2::/64')]
```

Subnet 0, 1, 2… is just the 4th group counting up. Nibble (4-bit) boundaries (`/48`, `/52`, `/56`, `/60`, `/64`) keep it readable.

## Address types

| Type | Prefix | Like IPv4's… | Notes |
|---|---|---|---|
| **Global unicast** | `2000::/3` (starts with `2` or `3`) | Public addresses | Routed on the internet. `2405:201:…` is one (APNIC region). |
| **Unique local (ULA)** | `fc00::/7` (in practice **`fd00::/8`**) | RFC 1918 private | Not routed on the internet. Pick a random `/48` inside `fd00::/8` to avoid collisions. The [DNS lab](../13-hands-on-labs/lab-03.2-trace-dns-resolution.md) uses `fd00:53::80`. |
| **Link-local** | `fe80::/10` | `169.254.0.0/16` | **Every IPv6 interface always has one**, automatically. Only valid on that one link; routers never forward it. Used by NDP and routing protocols. |
| **Multicast** | `ff00::/8` | Multicast **and broadcast** | `ff02::1` = all nodes on the link; `ff02::2` = all routers. **IPv6 has no broadcast.** |
| **Loopback** | `::1/128` | `127.0.0.1` | |
| **Unspecified** | `::/128` | `0.0.0.0` | "No address yet"; `[::]:80` in `ss` = listening on all IPv6 addresses |
| **IPv4-mapped** | `::ffff:0:0/96` | n/a | How an IPv6 socket shows an IPv4 client: `::ffff:192.0.2.10` |
| **Documentation** | `2001:db8::/32` | `192.0.2.0/24` etc. | For examples only |

Because a link-local address is valid on **every** link, you must say **which interface** you mean: `ping fe80::1%eth0` (`%eth0` is the **zone ID**).

## How IPv6 works on a LAN

### NDP replaces ARP

**NDP** (Neighbor Discovery Protocol) uses **ICMPv6** messages, sent to **multicast** groups, instead of ARP broadcasts:

| ICMPv6 message | Type | Job |
|---|---|---|
| **Router Solicitation (RS)** | 133 | Host: "any routers here?" |
| **Router Advertisement (RA)** | 134 | Router: "I'm a router; the prefix here is `2001:db8:abcd:1::/64`; use me as your gateway" |
| **Neighbor Solicitation (NS)** | 135 | "Who has `2001:db8:abcd:1::20`? Tell me your MAC" (ARP request equivalent) |
| **Neighbor Advertisement (NA)** | 136 | "That's me, here's my MAC" (ARP reply equivalent) |
| Redirect | 137 | "Use a better router for that destination" |

NDP also does **duplicate address detection (DAD)**: before using an address, a host asks whether anyone else has it.

> ⚠️ **Blocking ICMPv6 breaks IPv6.** In IPv4, blocking all ICMP is merely harmful ([3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md)); in IPv6, NDP, router discovery and path MTU discovery all run on ICMPv6.

### Getting an address: SLAAC and DHCPv6

| Method | How | Who decides the address |
|---|---|---|
| **SLAAC** (stateless address autoconfiguration) | The host hears a Router Advertisement with a `/64` prefix and builds the last 64 bits **itself** | The host |
| **Stateless DHCPv6** | SLAAC for the address, DHCPv6 only for extras (DNS servers, domain) | The host (address) + server (options) |
| **Stateful DHCPv6** | A DHCPv6 server hands out addresses, like IPv4 DHCP | The server |

Flags in the RA tell hosts which to use. (Android doesn't support stateful DHCPv6, which is one reason most LANs use SLAAC.)

**How a host builds its interface ID:**

- **EUI-64** (older): from the MAC address. `00:1a:2b:3c:4d:5e` → flip the 7th bit of the first byte, insert `ff:fe` in the middle → `fe80::21a:2bff:fe3c:4d5e` **(calculated, checked with Python in the lab container)**. Downside: the MAC is visible in every address, so a device can be tracked across networks.
- **Privacy / stable random addresses** (modern default on macOS, Windows, iOS, Android and most Linux): random interface IDs that change over time or per network.

### What's different from IPv4

| | IPv4 | IPv6 |
|---|---|---|
| Address size | 32 bits | 128 bits |
| Header | 20–60 bytes, with a checksum | **Fixed 40 bytes**, no checksum (L2 and L4 already check) |
| Broadcast | Yes | **No** (multicast instead) |
| Address resolution | ARP | **NDP** (ICMPv6) |
| Auto-configuration | DHCP | **SLAAC** (and DHCPv6) |
| Fragmentation | Routers may fragment | **Only the sender** fragments; routers send ICMPv6 "packet too big". Minimum MTU **1280** bytes |
| TTL field | TTL | **Hop limit** (same job) |
| NAT | Everywhere | Normally **not used**: devices have global addresses, so **firewalls do the protecting** |
| DNS record | `A` | **`AAAA`** ([3.4](../03-core-networking-protocols/04-dns.md)) |

## Living with both: dual stack and transition

- **Dual stack:** a device has **both** an IPv4 and an IPv6 address and uses whichever works. This is the normal case today.
- **Happy Eyeballs (RFC 8305):** when a name has both `A` and `AAAA` records, browsers and many libraries try IPv6 and IPv4 **nearly in parallel** and use whichever connects first, so a broken IPv6 path doesn't cause long waits.
- **NAT64 / DNS64:** lets IPv6-only clients reach IPv4-only servers (common on mobile networks, and used by EKS IPv6 clusters to reach IPv4 destinations).
- **Tunnels** (6in4 and others) carry IPv6 inside IPv4 across networks that only speak IPv4.

## Try it (on your Mac)

> **Not tested in my lab container:** its kernel had no IPv6 support, so the commands below are **illustrative**; the addresses you see will differ. The Python checks above were tested.

Your IPv6 addresses (look for `inet6`; one will be `fe80::…%en0`, link-local):

```bash
ifconfig en0 | grep inet6
```

Ping the IPv6 loopback, then all nodes on your Wi-Fi (several devices may answer):

```bash
ping6 -c 2 ::1
```

```bash
ping6 -c 2 ff02::1%en0
```

The IPv6 neighbour table (NDP's version of `arp -a`):

```bash
ndp -an
```

Does your connection work over IPv6 end to end?

```bash
curl -6 -sS -o /dev/null -w '%{http_code}\n' https://www.google.com
```

On Linux: `ip -6 addr`, `ip -6 route`, `ip -6 neigh`, `ping -6`.

## In the real world

- **AWS:** IPv6 addresses in a VPC are **global**. Outbound-only internet for private subnets uses an **egress-only internet gateway** (the IPv6 answer to "NAT gateway"); security groups do the filtering. IPv6-only subnets and **EKS IPv6 clusters** remove pod IP exhaustion entirely.
- **Docker** has IPv6 off by default on bridge networks; it can be enabled per network.
- **Kubernetes** supports IPv4, IPv6 and **dual-stack** clusters (Services and pods with both families).
- **Security:** with no NAT, an inbound firewall policy ("deny unsolicited inbound") must be explicit. "It's behind NAT" is no longer a hidden protection.

## Common mistakes

| Mistake | Reality |
|---|---|
| Using `::` twice in one address | Only once; otherwise the address is ambiguous |
| Subnets smaller than `/64` on a LAN | SLAAC needs `/64`. Use `/64` for LANs (`/127` is fine for router-to-router links) |
| Blocking all ICMPv6 "for security" | Breaks NDP, router discovery and PMTUD. Allow the necessary types (RFC 4890 lists them) |
| "IPv6 is off, so I don't need IPv6 firewall rules" | Many OSes enable it by default; link-local works with no configuration |
| Treating a ULA like a public address | `fd…` addresses aren't routed on the internet |
| Forgetting brackets in URLs | `http://[2001:db8::1]:8080/` |

## Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| Some sites slow to start, then work | A broken IPv6 path; the client waits before falling back to IPv4 | `curl -6` vs `curl -4` to the same site |
| A host has only an `fe80::` address | No Router Advertisement received (no router, RA blocked, or ICMPv6 filtered) | Capture ICMPv6 type 134; check the router's RA config |
| IPv6 works on the LAN but not to the internet | No default route, or the provider/cloud has no IPv6 path | `ip -6 route`; check the gateway |
| Large transfers over IPv6 hang | ICMPv6 "packet too big" blocked, so PMTUD fails ([3.7](../03-core-networking-protocols/07-icmp-ping-and-traceroute.md)) | Allow ICMPv6 type 2 |

## Interview angle

- **"Why IPv6?"** → IPv4 exhaustion. 128-bit addresses remove the need for NAT, simplify subnetting (`/64` everywhere) and allow auto-configuration.
- **"What replaces ARP and broadcast?"** → NDP over ICMPv6, using multicast.
- **"What's `fe80::`?"** → Link-local: auto-assigned on every interface, valid only on that link.
- **"Private addresses in IPv6?"** → ULA, `fd00::/8`. But usually you use global addresses and protect them with firewalls.
- **"How do EKS IPv6 clusters help?"** → Each pod gets an IPv6 address from a huge range, so subnets never run out; NAT64 / egress rules handle IPv4 destinations.

## Check yourself

1. Shorten `2001:0db8:0000:0000:0000:0000:0000:0001`.
2. Expand `fe80::1:2`.
3. How many `/64` subnets are in a `/56`?
4. Which address type would you see on every IPv6 interface, even with no router?
5. Why must ICMPv6 not be blocked completely?

<details>
<summary><b>Answers</b> (try first)</summary>

1. `2001:db8::1`.
2. `fe80:0000:0000:0000:0000:0000:0001:0002`.
3. 2^(64 − 56) = **256**.
4. A **link-local** address (`fe80::/10`).
5. NDP (address resolution, router discovery, duplicate detection) and path MTU discovery all use ICMPv6.

</details>

## Summary

- IPv6 = **128 bits**, 8 groups of 4 hex digits. Shorten with **leading-zero removal** and **one `::`**.
- **`/64` per LAN**; sites get `/48` or `/56`. Subnetting = numbering the subnet ID.
- Types: **global** `2000::/3`, **ULA** `fd00::/8`, **link-local** `fe80::/10` (always present), **multicast** `ff00::/8`, **loopback** `::1`.
- **NDP** (ICMPv6) replaces ARP and broadcast; **SLAAC** lets hosts configure themselves.
- No NAT by default, so **firewalls** do the protecting. Most networks are **dual stack**.

## Next

➡️ [2.7 · Default gateway, routing table and ARP](07-default-gateway-routing-table-and-arp.md): how a host actually decides where to send each packet, and how it finds the MAC address of the next hop.
