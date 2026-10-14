# Level 1 Exercises · Networking Fundamentals

> Covers [Level 1](../01-networking-fundamentals/README.md): networks, devices, addresses and ports, performance, the OSI and TCP/IP models.
> ⏱️ about 60–90 minutes (estimate) · Solutions: [solutions/01-level-1-fundamentals-solutions.md](solutions/01-level-1-fundamentals-solutions.md)
> Difficulty: 🟢 beginner · 🟡 intermediate · 🟠 advanced · 🔴 expert

**How to use this:** write your answers down (paper or a file) before opening the solutions. For calculations, show the steps: in an interview the method matters more than the final number. Aim for 80% before moving to Level 2.

Units used here: **1 byte = 8 bits**; network speeds are decimal (**1 Mbit/s = 1,000,000 bit/s**); file sizes are decimal too (**1 MB = 1,000,000 bytes**, **1 GB = 1,000,000,000 bytes**) unless a question says GiB.

---

## 🟢 Beginner

**1. Match each device to its job.**

Devices: hub · switch · router · wireless access point · modem · firewall · load balancer

| Job | Device |
|---|---|
| a) Connects different IP networks and picks the next hop for each packet | |
| b) Forwards frames inside one LAN, only to the port where the destination MAC lives | |
| c) Repeats every signal out of every port | |
| d) Converts between the provider's line (fibre, cable, DSL) and Ethernet | |
| e) Joins Wi-Fi clients to the wired LAN | |
| f) Allows or blocks traffic according to rules | |
| g) Spreads incoming requests across several servers | |

**2. LAN or WAN?**

a) The laptops, printer and TV in your flat.
b) The private link between a company's Mumbai data centre and its Singapore data centre.
c) The 40 servers in one rack, connected to one top-of-rack switch.

**3. Client, server, or both?**

a) A web browser. b) PostgreSQL. c) An nginx reverse proxy in front of an app. d) A DNS resolver such as `8.8.8.8`.

**4. Which identifier?** MAC address, IP address or port number:

a) Identifies an **application** on a host.
b) Identifies a network interface **on the local link**, and is rewritten at every router.
c) Identifies a host **across networks**, end to end.

**5. Speeds and sizes.**

a) How many megabytes per second (MB/s) is 1 Gbit/s, at most?
b) How long does a 100 MB file take over a 100 Mbit/s link, ignoring overhead?

**6. Put the TCP/IP model's four layers in order**, from the one closest to the cable to the one closest to the application, and give one protocol for each.

---

## 🟡 Intermediate

**7. Backup window.** A nightly backup is 2 GB. The office's upload link is 50 Mbit/s.

a) How long does the upload take, ignoring overhead?
b) If the backup were 2 **GiB** instead, how long would it take?

**8. The speed of light.** Light in fibre travels at about 200,000 km/s. Assume 7,200 km of fibre between Mumbai and London.

a) What is the one-way propagation delay?
b) What is the minimum possible round-trip time?
c) A colleague says "upgrade to a 10 Gbit/s link and the ping to London will drop". Are they right?

**9. Which layer is broken?** For each symptom, name the OSI layer (number and name) where the problem is.

a) The laptop's Ethernet cable is unplugged; the link light is off.
b) The laptop is plugged into a switch port in the wrong VLAN.
c) The laptop has no default gateway, so it can reach its own subnet only.
d) A security group blocks TCP port 5432 to the database.
e) `curl` reports `SSL certificate problem: certificate has expired`.
f) `curl` reports `Could not resolve host`.

**10. Read the MAC address.** For each, say whether it is **unicast or multicast/broadcast**, and **universally or locally administered**:

a) `3c:22:fb:12:34:56`
b) `02:42:ac:11:00:02`
c) `ff:ff:ff:ff:ff:ff`
d) `01:00:5e:00:00:fb`
e) `a6:5b:91:0c:4e:7d`

**11. Why not 1000?** On a 1 Gbit/s Ethernet link, `iperf3` reports about 940 Mbit/s of TCP throughput. Where did the other 60 Mbit/s go? Calculate the expected maximum for 1500-byte packets carrying TCP with the timestamps option. (Per packet on the wire: 8 bytes preamble, 14 bytes Ethernet header, 4 bytes FCS, 12 bytes inter-frame gap; IPv4 header 20 bytes; TCP header 32 bytes with timestamps.)

**12. Encapsulation.** A 100-byte HTTP request is sent over TCP (20-byte header, no options) and IPv4 (20-byte header) on Ethernet (14-byte header, 4-byte FCS).

a) How big is the IP packet?
b) How big is the Ethernet frame (header to FCS)?
c) What percentage of that frame is the HTTP request?

---

## 🟠 Advanced

**13. Collision and broadcast domains.** A router has two interfaces. Interface 1 connects to a **switch** with 4 PCs. Interface 2 connects to a **hub** with 3 PCs. How many collision domains and how many broadcast domains are there? Explain each.

**14. Latency budget.** A 1500-byte packet crosses one link, 1,000 km of fibre.

a) What is the serialisation (transmission) delay on a 10 Mbit/s link? On a 1 Gbit/s link?
b) What is the propagation delay?
c) Which one dominates on each link speed?

**15. Bandwidth-delay product.** A link is 10 Gbit/s with an 80 ms RTT.

a) How much data must be "in flight" to fill it?
b) TCP without window scaling allows at most 65,535 bytes in flight. What is the maximum throughput on this path without window scaling?

**16. What changes at the home router?** Your laptop (`192.168.1.20`, MAC `aa:aa:aa:aa:aa:aa`) sends a TCP packet from source port 51000 to `142.250.183.100:443`. The home router's LAN MAC is `bb:bb:bb:bb:bb:bb` and its public IP is `49.36.10.5`. List every field that is different when the packet leaves the router towards the internet, and say why.

---

## 🔴 Expert

**17. "The download is slow."** A user in Mumbai downloads a large file from a server in the US over a single TCP connection. Their connection is 1 Gbit/s, the RTT is 200 ms, and they get a steady 50 Mbit/s.

a) What amount of data in flight (the effective window) would cap throughput at exactly 50 Mbit/s?
b) What would be needed to fill the 1 Gbit/s link?
c) Give three changes, from the client side, the server side or the architecture, that would raise the throughput. Say which ones are general and which are specific to a vendor.

**18. Out loud, in two minutes.** "What happens when you type `https://example.com` into a browser and press Enter?" Write your answer as a numbered list of 8–10 steps, naming the protocol and the layer at each step. Stop at the point where the HTML arrives.

**19. Draw it.** Draw your home network as in [Lab 1.1](../13-hands-on-labs/lab-01.1-inspect-your-own-network.md): every device, its IP, the router's LAN and WAN sides, and your public IP. Mark which box does routing, switching, Wi-Fi, NAT, DHCP and DNS. (No single answer: compare with the example in the solutions.)
