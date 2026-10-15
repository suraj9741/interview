# Solutions · Lab 3.5 Troubleshooting Challenge

> ⚠️ **Spoilers.** Try each fault in [Lab 3.5](../../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md) first. Read the **hints** before the full answers.
>
> Every output below was captured by running `broken-network.sh` in the lab container **(tested in the lab container)**. Ports, MAC addresses, process IDs and timings will differ on your run.

## Hints only

| Fault | Hint |
|---|---|
| 1 | The error says which step failed. Where does the client send its DNS questions? |
| 2 | Can the client reach the first hop? Is the first hop **the right one**? |
| 3 | `traceroute` shows nothing at all, not even hop 1. Which box should be passing packets along? |
| 4 | The path works as far as `r2`. Can the server **answer**? |
| 5 | DNS works. A timeout (not a refusal) on the web port means something is quietly dropping packets. |
| 6 | A refusal comes back immediately. Who is listening on 8080? |
| 7 | Same error as 6, but something **is** listening. On which address? |
| 8 | The response code is 200, but 0 bytes arrived. Try a small page. Then try `tracepath` from the **server's** side. |

---

## Fault 1 · Wrong DNS server

**The complaint:**

```text
curl: (28) Resolving timed out after 5000 milliseconds
000 0 bytes
```

**Diagnosis.** `Resolving timed out` points straight at **step 1 (DNS)**. Check where the client sends its questions, and whether the path itself works:

```console
$ ip netns exec client cat /etc/resolv.conf
nameserver 10.2.2.99
$ ip netns exec client dig +time=2 +tries=1 app.lab
;; communications error to 10.2.2.99#53: timed out
;; no servers could be reached
$ ip netns exec client curl -sS -m 5 -o /dev/null -w '%{http_code} %{size_download} bytes\n' http://10.2.2.20:8080/big.txt
200 200000 bytes
```

By **IP**, the download works: the network and the app are fine. The resolver is `10.2.2.99`, an address where nothing exists. (The baseline said `10.2.2.20`.)

**Fix and verify:**

```bash
echo "nameserver 10.2.2.20" > /etc/netns/client/resolv.conf
./broken-network.sh test        # → 200 200000 bytes
```

**In the real world:** a wrong DHCP option set in a VPC, a stale `/etc/resolv.conf` baked into an image, a VPN that pushed its own DNS server, a container started with `--dns` pointing nowhere. The tell is always the same: **by IP it works, by name it doesn't**.

---

## Fault 2 · Wrong default gateway

**The complaint:** `curl: (28) Resolving timed out after 5001 milliseconds`, the same as fault 1. The first error is only where to **start**.

**Diagnosis.** The resolver setting is correct (`nameserver 10.2.2.20`), so ask whether the client can reach anything beyond its own subnet:

```console
$ ip netns exec client curl -sS -m 5 -o /dev/null http://10.2.2.20:8080/
curl: (7) Failed to connect to 10.2.2.20 port 8080 after 1036 ms: Couldn't connect to server
$ ip netns exec client ping -c1 -W1 10.1.1.1
64 bytes from 10.1.1.1: icmp_seq=1 ttl=64 time=0.240 ms
$ ip -n client route
default via 10.1.1.254 dev eth0
10.1.1.0/24 dev eth0 proto kernel scope link src 10.1.1.10
$ ip -n client neigh
10.1.1.254 dev eth0 INCOMPLETE
10.1.1.1 dev eth0 lladdr b6:66:c9:ac:ed:2a REACHABLE
```

Step 2 (route). The router at `10.1.1.1` answers, but the default route points at `10.1.1.254`, which doesn't exist: ARP for it never completes (`INCOMPLETE`, later `FAILED`). curl's `(7)` after about **1 second** is the kernel giving up on ARP (`No route to host`), not a refusal from the server. `traceroute` shows `*` from hop 1, and `tracepath` reports `!H` (host unreachable) from the client's own address.

**Fix and verify:**

```bash
ip -n client route replace default via 10.1.1.1
./broken-network.sh test        # → 200 200000 bytes
```

**In the real world:** a static IP configured by hand with a typo, a DHCP server handing out the wrong router option, a VRRP/HSRP virtual IP that moved. On AWS you'd see this as a route table pointing at a deleted target (`blackhole` state).

---

## Fault 3 · A router that doesn't forward

**The complaint:** `curl: (28) Resolving timed out after 5000 milliseconds`.

**Diagnosis.** Resolver is right, gateway is right and answers. But nothing past it does:

```console
$ ip netns exec client ping -c1 -W1 10.1.1.1
64 bytes from 10.1.1.1: icmp_seq=1 ttl=64 time=0.327 ms
$ ip netns exec client ping -c1 -W1 10.2.2.1
1 packets transmitted, 0 received, 100% packet loss, time 0ms
$ ip netns exec client traceroute -n -q1 -w1 -m4 10.2.2.20
 1  *
 2  *
 3  *
 4  *
$ ip netns exec r1 sysctl net.ipv4.ip_forward
net.ipv4.ip_forward = 0
```

Step 2 (route). The gateway answers when you ping **it**, but drops everything meant for somewhere else, silently and without even a time-exceeded message (so not even hop 1 shows in traceroute). `ip_forward = 0`: `r1` is behaving like a host, not a router.

**Fix and verify:**

```bash
ip netns exec r1 sysctl -w net.ipv4.ip_forward=1
./broken-network.sh test        # → 200 200000 bytes
```

**In the real world:** a Linux box meant to be a router or NAT instance after a reboot (the setting wasn't made permanent in `/etc/sysctl.d/`); on AWS, a NAT instance with **source/destination check** still enabled; Docker networking breaking after something reset `ip_forward`.

---

## Fault 4 · No route back from the server

**The complaint:** `curl: (28) Resolving timed out after 5000 milliseconds`.

**Diagnosis.** Packets get further this time:

```console
$ ip netns exec client ping -c1 -W1 10.2.2.1
64 bytes from 10.2.2.1: icmp_seq=1 ttl=63 time=1.08 ms
$ ip netns exec client ping -c1 -W1 10.2.2.20
1 packets transmitted, 0 received, 100% packet loss, time 0ms
$ ip netns exec client traceroute -n -q1 -w1 -m4 10.2.2.20
 1  10.1.1.1  0.031 ms
 2  10.0.0.2  0.182 ms
 3  *
 4  *
$ ip -n server route
10.2.2.0/24 dev eth0 proto kernel scope link src 10.2.2.20
```

Step 2 (route), **the return path**. `r2`, right next to the server, answers. The server **receives** the requests; a capture on the server shows SYNs arriving and nothing going back:

```console
$ ip netns exec server tcpdump -i eth0 -nn -t 'tcp port 8080 or icmp'      # while the client runs curl
IP 10.1.1.10.55676 > 10.2.2.20.8080: Flags [S], seq 423112797, win 64240, options [mss 1460,sackOK,TS val 3062038303 ecr 0,nop,wscale 10], length 0
IP 10.1.1.10.55676 > 10.2.2.20.8080: Flags [S], seq 423112797, win 64240, options [mss 1460,sackOK,TS val 3062039322 ecr 0,nop,wscale 10], length 0
```

It has **no default route**, so it can't send anything to `10.1.1.10`. From the client this looks exactly like a firewall drop: a timeout. Only looking **at the far end** finds it ([Lab 2.2](../../13-hands-on-labs/lab-02.2-routing-between-two-subnets.md), steps 4–5).

**Fix and verify:**

```bash
ip -n server route add default via 10.2.2.1
./broken-network.sh test        # → 200 200000 bytes
```

**In the real world:** a server with two network interfaces whose replies leave by the wrong one (asymmetric routing), a VPC peering or Transit Gateway route added on one side only, an on-premises network missing the route back to a cloud CIDR.

---

## Fault 5 · A firewall silently dropping the web port

**The complaint:**

```text
curl: (28) Connection timed out after 5002 milliseconds
000 0 bytes
```

**Diagnosis.** For the first time, the error isn't about resolving: DNS works. `Connection timed out` means the SYN got no answer at all.

```console
$ ip netns exec client ping -c1 -W1 10.2.2.20
64 bytes from 10.2.2.20: icmp_seq=1 ttl=62 time=0.244 ms
$ ip netns exec server ss -ltnp | grep -E 'State|8080'
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
LISTEN 0      5            0.0.0.0:8080      0.0.0.0:*    users:(("python3",pid=11135,fd=3))
$ ip netns exec server iptables -S INPUT
-P INPUT ACCEPT
-A INPUT -p tcp -m tcp --dport 8080 -j DROP
```

The server is reachable (ping works), the app listens on all addresses, and a firewall rule **drops** TCP port 8080. Step 5 (rules). A `DROP` gives a **timeout**; a `REJECT` would have given an immediate error ([Lab 3.1](../../13-hands-on-labs/lab-03.1-capture-a-tcp-handshake.md), part D).

**Fix and verify:**

```bash
ip netns exec server iptables -D INPUT -p tcp --dport 8080 -j DROP
./broken-network.sh test        # → 200 200000 bytes
```

**In the real world:** the single most common cause of a timeout: a **security group** without an inbound rule for the port, a **network ACL**, a Kubernetes **NetworkPolicy**, a host firewall (`ufw`, `firewalld`). Note that **ping working proves nothing** about the TCP port.

---

## Fault 6 · Nothing listening

**The complaint:**

```text
curl: (7) Failed to connect to app.lab port 8080 after 0 ms: Couldn't connect to server
000 0 bytes
```

**Diagnosis.** `(7)` after **0 ms**: the server answered immediately with a TCP reset. The network is fine; the question is step 4 (listener):

```console
$ ip netns exec server ss -ltnup
Netid State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
udp   UNCONN 0      0          10.2.2.20:53        0.0.0.0:*    users:(("dnsmasq",pid=11191,fd=4))
tcp   LISTEN 0      32         10.2.2.20:53        0.0.0.0:*    users:(("dnsmasq",pid=11191,fd=5))
```

DNS listens on 53; **nothing** listens on 8080.

**Fix and verify:** start the app:

```bash
(cd /tmp/broken-network/www && ip netns exec server python3 -m http.server 8080 > /tmp/broken-network/web.log 2>&1 &)
sleep 1; ./broken-network.sh test        # → 200 200000 bytes
```

**In the real world:** the app crashed or hasn't started yet, a deployment is in progress, the app listens on a different port than the one in the load balancer's target group, or a Kubernetes Service's `targetPort` doesn't match the container port.

---

## Fault 7 · Listening on localhost only

**The complaint:** `curl: (7) Failed to connect to app.lab port 8080 after 1 ms: Couldn't connect to server`, the same as fault 6.

**Diagnosis.** This time something **is** listening:

```console
$ ip netns exec server ss -ltnp | grep -E 'State|8080'
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
LISTEN 0      5          127.0.0.1:8080      0.0.0.0:*    users:(("python3",pid=11251,fd=3))
```

The app is bound to **`127.0.0.1`**, so it only accepts connections from the server itself. A connection arriving on `10.2.2.20:8080` finds no listener and gets a reset. Compare with the baseline: `0.0.0.0:8080` (all addresses).

**Fix and verify:** restart the app bound to all addresses:

```bash
PID=$(ip netns exec server ss -ltnpH 'sport = :8080' | grep -o 'pid=[0-9]*' | cut -d= -f2)
kill $PID; sleep 0.5
(cd /tmp/broken-network/www && ip netns exec server python3 -m http.server 8080 > /tmp/broken-network/web.log 2>&1 &)
sleep 1; ./broken-network.sh test        # → 200 200000 bytes
```

**In the real world:** very common in containers. A dev server (Flask, Vite, Rails, many others) defaults to `127.0.0.1`; inside a container that means "only reachable from inside the container", so `docker run -p` and Kubernetes Services can't reach it. Behind a port forward the error is often `curl: (56) Recv failure: Connection reset by peer` instead ([3.11](../../03-core-networking-protocols/11-troubleshooting-connectivity.md#read-the-error-first--it-tells-you-the-step)). The fix is in the app's config: listen on `0.0.0.0`.

---

## Fault 8 · Path MTU black hole

**The complaint:**

```text
curl: (28) Operation timed out after 5002 milliseconds with 0 out of 200000 bytes received
200 0 bytes
```

**Diagnosis.** Status **200** but **0 bytes**: the connection worked and the headers arrived, then the body never did. Everything in steps 1–5 checks out: DNS answers, ping works, `traceroute` shows all three hops, the app listens, no INPUT rules. Step 6: compare a small response with a large one:

```console
$ ip netns exec client curl -sS -m 5 -o /dev/null -w '%{http_code} %{size_download} bytes\n' http://10.2.2.20:8080/
200 21 bytes
$ ip netns exec client curl -sv -m 5 -o /dev/null http://10.2.2.20:8080/big.txt 2>&1 | grep -E '^< (HTTP|Content-Length)|timed out'
< HTTP/1.0 200 OK
< Content-Length: 200000
* Operation timed out after 5002 milliseconds with 0 out of 200000 bytes received
```

**Small works, large hangs**: the classic MTU signature ([3.7](../../03-core-networking-protocols/07-icmp-ping-and-traceroute.md#mtu-and-path-mtu-discovery)). Now test the path size **in both directions**:

```console
$ ip netns exec client tracepath -n 10.2.2.20 | tail -1
     Resume: pmtu 1400 hops 3 back 3
$ ip netns exec server tracepath -n 10.1.1.10 | tail -3
30:  no reply
     Too many hops: pmtu 1500
     Resume: pmtu 1500
```

From the client, path MTU discovery works and finds 1400. From the **server**, it never learns about the 1400-byte link: the big packets just disappear. The data flows server → client, so that's the direction that matters. Look for what's eating the ICMP "fragmentation needed" messages on the server's side of the narrow link:

```console
$ ip netns exec r2 iptables -L OUTPUT -n -v
Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination
    9  5184 DROP       1    --  *      *       0.0.0.0/0            0.0.0.0/0            icmptype 3 code 4
```

ICMP type 3 code 4 is **"fragmentation needed and DF set"**. `r2` correctly refuses the server's 1500-byte packets (the link to `r1` takes only 1400), tries to tell the server, and its own firewall drops the message: 9 times in this run. The server keeps retransmitting the same full-size segments forever. A capture on the server shows the same `seq 192:1640` segment (1448 bytes of data) sent again and again, and `ss -ti` on the server shows `mss:1448 pmtu:1500` with a growing `retrans` count.

**Fix (either one; both tested):**

```bash
# a) Stop dropping the ICMP message (the real fix)
ip netns exec r2 iptables -D OUTPUT -p icmp --icmp-type fragmentation-needed -j DROP

# b) Or clamp the TCP MSS on the router, so TCP never sends packets that are too big
ip netns exec r2 iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu

./broken-network.sh test        # → 200 200000 bytes
```

**In the real world:** a firewall or security appliance that "blocks all ICMP", across a **VPN**, **GRE/IPsec** tunnel, **VXLAN** overlay or a link with **jumbo frames** on one side. Symptoms: SSH connects but hangs on large output, web pages half-load, `git clone` stalls, TLS handshakes with large certificate chains hang. AWS: traffic over a VPN or Transit Gateway has a smaller MTU than inside a VPC (which supports up to 9001-byte jumbo frames). MSS clamping on the tunnel endpoint is the standard workaround; allowing ICMP type 3 code 4 is the real fix.

---

## Summary: same first error, different causes

| Fault | First error | What told the faults apart | Step |
|---|---|---|---|
| 1 | `Resolving timed out` | By IP works; `resolv.conf` points nowhere | 1 · DNS |
| 2 | `Resolving timed out` | By IP: `(7)` after ~1 s; gateway in `ip neigh` is `INCOMPLETE`/`FAILED` | 2 · Route (local) |
| 3 | `Resolving timed out` | Gateway pings, nothing beyond it; traceroute all `*`; `ip_forward = 0` | 2 · Route (forwarding) |
| 4 | `Resolving timed out` | Reaches `r2`, not the server; server has no default route | 2 · Route (return path) |
| 5 | `Connection timed out` | Ping works, app listens, `iptables` has a DROP | 5 · Rules |
| 6 | `(7) Couldn't connect` instantly | `ss` shows nothing on 8080 | 4 · Listener |
| 7 | `(7) Couldn't connect` instantly | `ss` shows `127.0.0.1:8080` | 4 · Listener |
| 8 | `200` with `0 bytes`, then timeout | Small page works; `tracepath` from the server can't find the MTU; ICMP 3/4 dropped | 6 · Size / MTU |

Three lessons to take into an interview:

1. **The first error tells you where to start, not what's wrong.** Four different faults all said "Resolving timed out", because DNS is the first thing that crosses the network.
2. **Remove a layer to split the problem.** Testing **by IP** instantly separated fault 1 (DNS) from faults 2–4 (the network).
3. **Look at the far end.** Faults 4, 5, 7 and 8 were only provable from the **server** or `r2`, not from the client.
