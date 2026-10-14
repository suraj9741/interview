# Level 1 · Networking Fundamentals

**Goal:** understand what a network is, what the boxes in it do, what labels traffic carries, how to measure it, and the layered model everyone uses to talk about it.

**Start here if:** you have zero networking knowledge. No prerequisites.

⏱️ **Estimated time:** about 6 hours (lessons ~5 h, labs ~1 h). This is an estimate; take longer if a topic is new.

## Lessons (read in this order)

| # | Lesson | You'll be able to… | ⏱️ (estimate) |
|---|---|---|---|
| 1.1 | [What is a computer network?](01-what-is-a-network.md) | Explain networks, LAN/WLAN/WAN/the internet, client–server vs peer-to-peer | 45 min |
| 1.2 | [Network devices](02-network-devices.md) | Say what a NIC, hub, switch, router, modem, AP, firewall and load balancer each read and do | 60 min |
| 1.3 | [Addresses, ports and protocols](03-addresses-ports-and-protocols.md) | Tell MAC, IP and port apart; read sockets and the 5-tuple; explain `127.0.0.1` vs `0.0.0.0` ⭐ | 60 min |
| 1.4 | [Network performance](04-network-performance.md) | Convert bits and bytes 🔥; explain bandwidth, throughput, latency, jitter, loss and BDP; measure them | 60 min |
| 1.5 | [The OSI and TCP/IP models](05-osi-and-tcp-ip-models.md) ⭐ | Name every layer, place protocols and devices on it, and explain encapsulation on a real packet | 90 min |

## Practice

| Type | Link |
|---|---|
| 🖥️ Lab 1.1 | [Inspect your own network](../13-hands-on-labs/lab-01.1-inspect-your-own-network.md) (Mac + Linux, 20 min) |
| 🖥️ Lab 1.2 | [Build a tiny network with namespaces](../13-hands-on-labs/lab-01.2-build-a-tiny-network-with-namespaces.md) (Linux lab container, 45 min) |
| ✍️ Exercises | [Level 1 exercises](../14-practice-exercises/01-level-1-fundamentals.md) · [solutions](../14-practice-exercises/solutions/01-level-1-fundamentals-solutions.md) |

## Milestone: you're ready for Level 2 when you can…

- [ ] Draw your home network (laptop, phone, router box, provider) and label which parts are LAN, WAN and internet.
- [ ] Explain switch vs router in two sentences without notes.
- [ ] Explain why an app on `127.0.0.1` can't be reached from another machine.
- [ ] Convert 300 Mbit/s into MB/s in your head.
- [ ] List the 7 OSI layers in order, with one protocol and one device for each where one exists.
- [ ] Score at least 80% on the [Level 1 exercises](../14-practice-exercises/01-level-1-fundamentals.md).

➡️ **Next level:** [Level 2 · IP addressing and subnetting](../02-ip-addressing-and-subnetting/README.md)
