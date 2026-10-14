# 1.3 · Addresses, Ports and Protocols

> **Level 1 · Networking fundamentals** · Lesson 3 of 5 · ⏱️ about 60 minutes (estimate)
> ⬅️ [1.2 Network devices](02-network-devices.md) · ➡️ [1.4 Network performance](04-network-performance.md)

## What you'll learn

- What a **network interface** is, and the special ones (`lo`, `eth0`, `en0`, `docker0`, `veth…`).
- The three labels on every piece of traffic: **MAC address**, **IP address** and **port**, and why we need all three.
- What **sockets** and the **5-tuple** are.
- The names for a piece of data at each stage: **frame, packet, segment, datagram**.
- What a **protocol** really is, and who writes the rules.
- ⭐ Why an app listening on `127.0.0.1` can't be reached from outside, while one on `0.0.0.0` can.

## Before you start

- [1.1](01-what-is-a-network.md): inside a network vs between networks.
- [1.2](02-network-devices.md): a switch reads MAC addresses; a router reads IP addresses.

---

## The idea in plain words

To deliver a letter to **one person** in **one flat** in **another city**, you need three pieces of information:

| You need to find… | Networking label | Example | Used by |
|---|---|---|---|
| The right **building** anywhere in the world | **IP address** | `142.250.183.4` | Routers, across networks |
| The right **door** on this street, for the next step only | **MAC address** | `02:42:ac:11:00:02` | Switches, inside one network |
| The right **person** (program) inside the building | **Port** | `443` | The operating system, to pick the program |

- The **IP address** stays the same from start to finish (unless NAT changes it, [3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md)).
- The **MAC address** changes at every hop: it only ever says "who carries it next on this street".
- The **port** picks the program: a server may run a web server (port 443) and SSH (port 22) at the same IP.

## Why it matters

Nearly every "it can't connect" problem is a wrong or unreachable **address**, or a wrong **port**, or a program listening on the wrong **interface**. Knowing which label each device reads tells you where to look.

## Network interfaces

An **interface** is a network connection point on a device: a real card or a virtual one. Each interface has a MAC address and can have one or more IP addresses.

| Name | What it is |
|---|---|
| `lo` | **Loopback**: a virtual interface for the machine to talk **to itself**, always `127.0.0.1` (and `::1` in IPv6). Traffic never leaves the machine. |
| `eth0`, `ens5`, `enp0s3` | A wired (or cloud) network card on Linux. Also the name of the card **inside every Docker container**. |
| `wlan0` | A Wi-Fi card on Linux |
| `en0` | The Wi-Fi card on a Mac |
| `docker0` | Docker's default **bridge** (a software switch), `172.17.0.1` |
| `br-xxxxxxxx` | One bridge per **user-defined** Docker network |
| `vethxxxxxxx` | One end of a **virtual Ethernet pair** (a virtual cable). The other end is a container's `eth0`. |

Source: the interface tables from the original basics notes, all seen on this Mac and in Docker Desktop's VM **(tested on the Mac, Oct 2026)**.

## MAC addresses (layer 2)

A **MAC address** (Media Access Control address) is the **hardware address** of a network interface.

- **48 bits**, written as 6 pairs of hexadecimal digits: `d6:15:f1:59:b2:a3` (hex is explained in [2.1](../02-ip-addressing-and-subnetting/01-binary-decimal-and-hex.md)).
- The **first half** (24 bits) is the **OUI** (Organizationally Unique Identifier), assigned to the manufacturer. The second half is chosen by the manufacturer.
- One bit in the first byte says whether the address is **globally unique** (burned in at the factory) or **locally administered** (made up by software). Virtual machines, containers and phones (privacy mode) use locally administered addresses. Wireshark shows this bit: `LG bit: Locally administered address (this is NOT the factory default)` **(tested in the lab container)**.
- **Only meaningful on the local network.** Routers don't forward MAC addresses; every hop gets a new frame with new MACs.
- Special address: `ff:ff:ff:ff:ff:ff` = **broadcast**, "every device on this local network".

## IP addresses (layer 3)

An **IP address** (Internet Protocol address) is the **logical address** of an interface: it says **which network** the device is on and **which device** it is in that network.

| | IPv4 | IPv6 |
|---|---|---|
| Size | 32 bits | 128 bits |
| Looks like | `192.168.29.1` (4 numbers, 0–255) | `2405:201:1006:e906::c0a8:1d01` (hex, groups of 4) |
| How many | About 4.3 billion: not enough for the world | 2¹²⁸: practically unlimited |

**On your Mac (tested on the Mac, Oct 2026):** your router has both kinds. `2405:201:…::c0a8:1d01` ends in `c0a8:1d01`, which is hex for **192.168.29.1**, the router's IPv4 address.

An IP address is **assigned**, not built in: by you, by **DHCP** ([2.8](../02-ip-addressing-and-subnetting/08-dhcp.md)), or by a cloud provider. Move a laptop from home to office and its IP changes; its MAC doesn't.

Level 2 is all about IP addresses: [2.2](../02-ip-addressing-and-subnetting/02-ipv4-addresses-and-ranges.md) (IPv4), [2.3](../02-ip-addressing-and-subnetting/03-subnet-masks-and-cidr.md) (subnets), [2.6](../02-ip-addressing-and-subnetting/06-ipv6-fundamentals.md) (IPv6).

### MAC vs IP: why have both?

| | MAC address | IP address |
|---|---|---|
| Layer | 2 (data link) | 3 (network) |
| Assigned by | The manufacturer (or software, for virtual cards) | The network: an admin, DHCP, or the cloud |
| Structure | Flat: says nothing about location | **Hierarchical**: the network part says where the device is |
| Scope | One local network | End to end, across the world |
| Changes as the packet travels? | **Yes, at every router** | **No** (unless NAT) |

The key is **hierarchy**. A router can't keep a list of every MAC address in the world. It can keep a list of **networks** ("`10.0.2.0/24` is that way"), because IP addresses are grouped by network. The next hop then uses **ARP** ([2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md)) to find the MAC for the final delivery.

## Ports (layer 4)

An IP address finds the **machine**. A **port** finds the **program** on it. Ports are numbers from **0 to 65535**, used by **TCP** and **UDP** ([3.2](../03-core-networking-protocols/02-tcp-and-udp.md)).

| Range | Name | Meaning |
|---|---|---|
| 0–1023 | **Well-known** ports | Standard services. On Linux, a program needs root (or a special capability) to listen on them. |
| 1024–49151 | **Registered** ports | Registered with IANA for specific software (e.g. 3306 MySQL, 5432 PostgreSQL) |
| 49152–65535 | **Dynamic / private** ports | IANA's suggested range for temporary client ports |

Common ones you'll meet in these notes:

| Port | Used by |
|---|---|
| 22 | SSH |
| 53 | DNS (UDP, and TCP for large answers) |
| 80 / 443 | HTTP / HTTPS |
| 3306 · 5432 · 6379 | MySQL · PostgreSQL · Redis |
| 6443 | Kubernetes API server |
| 10250 | kubelet |
| 2379–2380 | etcd |

The full list, checked against the IANA registry, is in [references/common-ports.md](../references/common-ports.md). The protocols behind them are explained in [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md).

### Ephemeral ports: the client's side

When a program **connects out**, the operating system gives the client side a temporary **ephemeral port**.

- On Linux the range is **32768–60999** by default **(tested in the lab container)**. Check it with:
  ```bash
  cat /proc/sys/net/ipv4/ip_local_port_range
  ```
- Docker Desktop's VM uses **55000–65535** **(tested on the Mac, Oct 2026)**.
- Windows and macOS use IANA's 49152–65535.

> **AWS link ⭐:** a **NACL is stateless**, so it must allow the **return traffic to ephemeral ports** (AWS suggests 1024–65535). A security group is stateful and doesn't need this. Forgetting it gives **timeouts**.

## Sockets and the 5-tuple

A **socket** is one end of a conversation: **an IP address + a port + a protocol**, held open by a program. A server's listening socket looks like `0.0.0.0:443`; a client's like `10.10.0.1:48766`.

Every connection is identified by a **5-tuple**:

```
protocol   source IP   source port   destination IP   destination port
TCP        10.10.0.1   48766         10.10.0.2        8080
```

Two connections from the same client to the same server differ by their **source port**. That's how one browser can have 10 connections to one website at once. Firewalls, NAT and Linux connection tracking all work on this 5-tuple ([3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md), [8.6](../08-linux-networking/06-netfilter-nat-and-conntrack.md)).

See sockets on Linux:

```bash
ss -tan
```

`-t` TCP, `-a` all states, `-n` show numbers instead of names. **Expected output (tested in the lab container, [Lab 3.1](../13-hands-on-labs/lab-03.1-capture-a-tcp-handshake.md)),** on the server:

```
State     Recv-Q Send-Q Local Address:Port Peer Address:Port Process
LISTEN    0      5          10.10.0.2:8080      0.0.0.0:*
TIME-WAIT 0      0          10.10.0.2:8080    10.10.0.1:48766
```

- `LISTEN … 10.10.0.2:8080` is the **server socket**, waiting for connections.
- `TIME-WAIT … 10.10.0.1:48766` is a finished connection from a client that used **ephemeral port 48766**. (TIME-WAIT is explained in [3.3](../03-core-networking-protocols/03-tcp-in-depth.md).)

## Packets, frames, segments: names for data

The same data gets a different name depending on which layer has wrapped it. You'll see why in [1.5](05-osi-and-tcp-ip-models.md).

| Name | Layer | It's… | Its addresses |
|---|---|---|---|
| **Data** / message | Application | What the program sends, e.g. `GET /index.html` | n/a |
| **Segment** (TCP) / **datagram** (UDP) | Transport | Data + a TCP or UDP header | **Ports** |
| **Packet** | Network | A segment + an IP header | **IP addresses** |
| **Frame** | Data link | A packet + an Ethernet (or Wi-Fi) header and trailer | **MAC addresses** |
| **Bits** | Physical | The frame as signals on the wire | n/a |

In everyday talk, people say "packet" for all of these. In an interview, using the right word at the right layer shows you understand the stack.

## Protocols: the rules

A **protocol** defines three things:

1. **Syntax:** the format. Which bytes mean what (e.g. "the first 6 bytes of an Ethernet frame are the destination MAC").
2. **Semantics:** the meaning. What each message asks for or reports (e.g. "a TCP packet with the SYN flag asks to open a connection").
3. **Timing and order:** who sends what, when (e.g. "after SYN, wait for SYN-ACK, then send ACK").

Who writes the rules:

| Body | Writes | Examples |
|---|---|---|
| **IETF** (Internet Engineering Task Force) | **RFCs** (Requests for Comments): the internet's standards | IP (RFC 791), TCP (RFC 9293), HTTP (RFC 9110), DNS (RFC 1034/1035) |
| **IEEE** (Institute of Electrical and Electronics Engineers) | LAN standards | Ethernet (802.3), Wi-Fi (802.11), VLANs (802.1Q) |
| **IANA** (Internet Assigned Numbers Authority) | The number registries | Port numbers, protocol numbers, the root of IP address allocation |

The RFCs used in these notes are listed in [references/standards-and-rfcs.md](../references/standards-and-rfcs.md).

## ⭐ `127.0.0.1` vs `0.0.0.0`: the most common "it doesn't work" cause

When a program **listens**, it chooses **which address** to listen on:

| Listens on | Who can connect |
|---|---|
| `127.0.0.1:8000` | **Only programs on the same machine** (through `lo`). In a container, that means only the same container. |
| `0.0.0.0:8000` | **Anyone who can reach any of the machine's addresses**, including traffic arriving through `-p` port publishing |
| A specific address, e.g. `10.10.0.2:8000` | Only traffic sent to that address |

`0.0.0.0` in a **listening** socket means "all my IPv4 addresses". (`::` is the IPv6 equivalent.)

**Proof (tested on the Mac, Oct 2026):** the same Python app in a container, published with `-p 8081:8000`.

Listening on `127.0.0.1`, as seen with `ss -lntp` inside the container:

```
LISTEN 0  5   127.0.0.1:8000   0.0.0.0:*
```

From the Mac:

```
curl: (56) Recv failure: Connection reset by peer
```

Inside the container it worked (status 200). Docker delivered the request to the container's **eth0** (`172.17.0.x`), but the app only listens on **lo**.

Listening on `0.0.0.0` instead:

```
LISTEN 0  5     0.0.0.0:8000   0.0.0.0:*
```

From the Mac: `200`. ✅

**The same on plain Linux (tested in the lab container, [Lab 3.5](../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md) fault 7):** a server listening on `127.0.0.1:8080` is refused when a client on another machine connects:

```
LISTEN 0      5          127.0.0.1:8080      0.0.0.0:*    users:(("python3",pid=4442,fd=3))
```

```
curl: (7) Failed to connect to app.lab port 8080 after 1 ms: Couldn't connect to server
```

This is why the Flask example needs `--host=0.0.0.0`: Flask listens on `127.0.0.1` by default.

## In the real world

- **Kubernetes:** all containers in one pod share one network namespace (one set of interfaces), so they talk over `localhost` and can't both use port 80. A pod's app must listen on `0.0.0.0` (or the pod IP) for a Service to reach it.
- **Security:** binding admin interfaces (databases, debug ports) to `127.0.0.1` is a deliberate protection. Exposing them on `0.0.0.0` on a public server is a classic breach cause.
- **Cloud:** an EC2 instance's **ENI** (elastic network interface) has a MAC and private IPs; its public IP is mapped by the internet gateway and never appears on the interface.

## Common mistakes

| Mistake | Reality |
|---|---|
| "A device has one IP address." | An **interface** has addresses, and one device can have many interfaces and many addresses. |
| "The MAC address travels with the packet to the server." | Each router writes a new frame with new MACs. The server sees the **last router's** MAC. |
| "Port 8080 is HTTP." | Ports are conventions. Any program can listen on any port; HTTP on 8080 is common, but nothing enforces it. |
| "`0.0.0.0` is an address I can connect to." | As a **listening** address it means "all interfaces". As a **destination** it's not valid (Linux treats a connect to it as local, which only confuses things). |
| "Ephemeral ports are random and unlimited." | They come from a fixed range (about 28,000 ports on Linux). Busy clients or NAT devices can **run out** ([3.8](../03-core-networking-protocols/08-nat-pat-and-port-forwarding.md)). |

## Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| Works with `curl localhost:8000` on the server, fails from another machine | App listens on `127.0.0.1` | `ss -lntp` on the server: look at the local address |
| `Connection refused` from another machine | Nothing listens on that IP:port (or a firewall REJECTs) | `ss -lntp`, and check the port number |
| `bind: address already in use` when starting an app | Another program already holds that port | `ss -lntp \| grep :8000`; on a Mac `lsof -nP -iTCP:8000 -sTCP:LISTEN` |
| Two machines on the LAN can't talk; `ip neigh` shows `FAILED` | The MAC address couldn't be found (ARP failed): wrong subnet, cable, or the other machine is off | `ip neigh`, then check both IPs and masks ([2.7](../02-ip-addressing-and-subnetting/07-default-gateway-routing-table-and-arp.md)) |

## Hands-on lab

- [Lab 1.1 · Inspect your own network](../13-hands-on-labs/lab-01.1-inspect-your-own-network.md): list your interfaces, MAC and IP addresses, and listening sockets.
- [Lab 1.2 · Build a tiny network with namespaces](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md): give interfaces addresses yourself and watch ARP turn an IP into a MAC.

## Interview angle

- ⭐ **"The app works inside the container but not from outside."** → It listens on `127.0.0.1`, not `0.0.0.0`; or the port isn't published. Check with `ss -lntp`.
- **"MAC vs IP address?"** → MAC = hardware address, used by switches for the **next hop** only, changes at every router. IP = logical, hierarchical address of the **final destination**, stays the same end to end unless NAT.
- **"What's a socket? What's the 5-tuple?"** → A socket is an IP + port + protocol endpoint. A connection is identified by protocol, source IP, source port, destination IP and destination port.
- **"Why do NACLs need ephemeral ports open?"** → Because they're stateless: the reply comes back to the client's ephemeral port and must be allowed explicitly.

## Check yourself

1. Which of MAC address, IP address and port changes at every router hop?
2. A client at `10.0.1.25` opens two connections to `10.0.2.15:443`. What makes the two connections different?
3. What is the PDU called at layer 3? At layer 2?
4. `ss -lnt` on a server shows `127.0.0.1:5432`. Can an app on another server connect to this database?
5. Is a MAC address starting with `02:` likely burned in by a manufacturer?

<details>
<summary><b>Answers</b> (try first)</summary>

1. The MAC addresses (source and destination). IPs and ports stay the same unless NAT changes them.
2. The client's **source port** (two different ephemeral ports).
3. Layer 3: packet. Layer 2: frame.
4. No. It listens only on loopback. It must listen on `0.0.0.0` or the server's own IP (and the firewall must allow it).
5. No. `02` has the "locally administered" bit set, so it was made up by software (a VM, container or privacy setting).

</details>

## Summary

- **Interfaces** are network connection points; `lo` is the machine talking to itself.
- **MAC** = local, next-hop hardware address (48 bits). **IP** = logical, hierarchical, end-to-end address. **Port** = which program.
- A connection = the **5-tuple**. Clients use **ephemeral ports** from a limited range.
- Data is a **segment/datagram** (L4), **packet** (L3), **frame** (L2), **bits** (L1).
- A **protocol** = format + meaning + order. The IETF writes RFCs, the IEEE writes LAN standards, IANA keeps the numbers.
- Listening on `127.0.0.1` = local only; on `0.0.0.0` = all interfaces.

## Next

➡️ [1.4 · Network performance](04-network-performance.md): how fast (bandwidth, throughput), how slow (latency), how steady (jitter) and how reliable (packet loss) a network is, and why bits and bytes are not the same.
