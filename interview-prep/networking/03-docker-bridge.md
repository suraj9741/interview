# 03 · Docker Bridge Networking, Inside Out ⭐

What really happens when you run `docker run -p 8080:80 nginx`. Every output here is **real (tested)**, from a container called `flat-a` on your Docker Desktop.

For network types, the default-bridge DNS trap and port publishing options, see [Docker 08 Networking](../docker/08-networking.md).

![How the default bridge network works](../docker/diagrams/08-bridge-network.drawio.svg)

## The 4 pieces

A new container gets its own **network namespace** (a private room), which starts empty. Docker connects it in 4 steps:

| # | Piece | In the story | Its job |
|---|---|---|---|
| 1 | **Bridge** `docker0` | The corridor | A virtual switch that connects all containers |
| 2 | **veth pair** | The door | A virtual cable: one end is `eth0` inside the container, the other end plugs into the bridge |
| 3 | **MASQUERADE** | Reception masks the FROM | Lets containers reach the internet |
| 4 | **DNAT** | Reception changes the TO | Lets the outside reach a container, for `-p` only |

## 1. The bridge: `docker0`

Created **once**, when Docker starts:

```
16: docker0: <BROADCAST,MULTICAST,UP,LOWER_UP> ... state UP
    inet 172.17.0.1/16
```

- Containers plugged into it talk to each other **directly**, without NAT. In the lab, `flat-b` fetched nginx from `172.17.0.2` through the corridor.
- Its IP, `172.17.0.1`, is **every container's default gateway**.
- **Every user-defined network gets its own bridge and subnet.** Your Compose networks showed up as `br-cb1f…` (172.19), `br-9189…` (172.20) and `br-3662…` (172.18). Containers on different bridges can't talk to each other.

## 2. The veth pair: one door, two sides

Inside the container:

```
11: eth0@if17: ...
    inet 172.17.0.2/16
```

On the host:

```
17: veth14a2cac@if11: ... master docker0
```

- `eth0@if17` means: "I am #11, and my other end is **#17**."
- `veth14a2cac@if11` means: "I am #17, my other end is **#11**, and I'm plugged into **docker0**."
- They point at each other, so they're **one cable**.

Two details from the lab:

- **Both containers' doors said `@if11`.** Each container numbers its own interfaces from scratch, so each one's `eth0` happened to be #11.
- **Stopping a container removes its door**, and starting it again creates a **new** one with a new number.

To find a container's door on a Linux host:

```bash
docker exec flat-a cat /sys/class/net/eth0/iflink
```

That prints the peer's number (e.g. `17`). Then `ip link | grep "^17:"`.

## 3. The container's routing table

```
default via 172.17.0.1 dev eth0          ← anything not local goes to docker0
172.17.0.0/16 dev eth0 scope link        ← other containers: deliver directly
```

## 4. The packet's journey ⭐ (draw this on the whiteboard)

![A packet's journey: going out (MASQUERADE) and coming in (DNAT)](../docker/diagrams/08-packet-flow.drawio.svg)

```text
OUTBOUND: container eth0 → veth → docker0 → host routing → MASQUERADE (src = host IP) → host eth0 → internet
INBOUND:  internet → host eth0:8080 → DNAT in PREROUTING (dst = 172.17.0.2:80) → host routing → docker0 → veth → container eth0:80
```

- The same pieces, in opposite order.
- The address changes in **one place only**: the NAT step ([02](02-nat.md)).
- The host must allow forwarding: `net.ipv4.ip_forward = 1`. Docker turns it on **(tested)**.

## 5. `docker-proxy`: the helper

`docker-proxy` is a small program, **one per published port**, that listens on the host port and copies the bytes to the container.

**Why it's needed:** when the host itself connects to `127.0.0.1:8080`, Linux won't route a loopback (`127.x`) packet out to docker0, so DNAT alone can't deliver it. docker-proxy simply accepts the connection and opens a new one to the container.

| | Normal Linux server (EC2) | Your Docker Desktop (tested) |
|---|---|---|
| Setting | `userland-proxy: true` (the default) | `"userland-proxy": false` (read from the VM's `daemon.json`) |
| Who holds port 8080 (`ss -lntp`) | A **`docker-proxy`** process | **`dockerd`** itself |
| How localhost traffic works | Through docker-proxy | An extra rule: `-A POSTROUTING -o docker0 -m addrtype --src-type LOCAL -j MASQUERADE` |

## 6. What Docker Desktop on your Mac hides

Docker Desktop runs everything inside a **hidden Linux VM**. That changes what you can see:

| Thing | On a Linux server | On your Mac |
|---|---|---|
| `docker0`, veths, iptables | On the host, visible with `ip` and `sudo iptables` | Inside the VM. To see them, use the "building shell" from the [lab](05-hands-on-lab.md) |
| `--network=host` | The **server's** network | The **VM's** network, not your Mac's |
| Traffic from your browser to `localhost:8080` | Goes through the DNAT rule | Docker Desktop forwards it by a **shortcut**: the DNAT counter stayed at **0** for Mac traffic, but went up for traffic sent inside the VM **(tested)** |
| `docker-proxy` | Present | Turned off |

So the textbook path is what you'll see on **EC2, CI runners and Kubernetes nodes**, not on your Mac.

## 7. Default bridge vs user-defined network (tested)

| | Default bridge | User-defined network |
|---|---|---|
| DNS server in `/etc/resolv.conf` | `192.168.65.7` on Docker Desktop (the host's DNS on Linux) | **`127.0.0.11`**, Docker's built-in DNS |
| Can containers find each other by name? | ❌ `wget: bad address 'flat-a'` | ✅ Yes |

## Interview angle

- ⭐ **"Walk me through what happens when you run `docker run -p 8080:80 nginx`."** → A new network namespace; a veth pair with `eth0` inside and the other end on docker0; an IP from `172.17.0.0/16` with gateway `172.17.0.1`; a DNAT rule for 8080; MASQUERADE already exists for outbound traffic. (The full `docker run` flow is in [Docker 02](../docker/02-architecture-internals.md).)
  - **He'll push: "How do you find which veth belongs to which container?"** → `cat /sys/class/net/eth0/iflink` inside the container gives the peer's interface number; find it with `ip link` on the host.
- **"Two containers on the same bridge talk. Does NAT happen?"** → No. They talk directly through the bridge (layer 2).
- **"What is docker-proxy for?"** → It handles traffic DNAT can't, mainly the host's own `localhost` connections. It can be turned off with `"userland-proxy": false`.
- **"How would you get into a container's network if it has no tools?"** → `docker run --rm -it --network container:<name> nicolaka/netshoot`, or on the host `nsenter -t <PID> -n ip addr` (the PID comes from `docker inspect -f '{{.State.Pid}}' <name>`).

## Practice 🖥️

The [hands-on lab](05-hands-on-lab.md) shows every output on this page on your own Mac.
