# Solutions · Troubleshooting Scenarios

> ⚠️ Spoilers for the [troubleshooting scenarios](../04-troubleshooting-scenarios.md). Each answer gives the step, the cause, one confirming command, the fix and how to prevent it. Cloud-specific details are marked as vendor-specific.

---

## 🟢 Beginner

### T1 · Could not resolve host

- **Step:** 1 · DNS. `curl: (6)` means the name never became an IP; by IP the wiki answers `200`, so the network and the app are fine.
- **Likely cause:** the laptop isn't using the **company's DNS** for `corp.example` (the VPN didn't push its DNS settings, or the OS sends that domain's queries to the home router). Alternative: the record doesn't exist or was mistyped.
- **Confirm:** `scutil --dns` on a Mac (or `resolvectl status` on Linux) to see which resolver handles `corp.example`; then `dig @<company DNS IP> wiki.corp.example` to see whether the company DNS knows the name.
- **Fix:** reconnect the VPN with "use company DNS" / split DNS enabled, or fix the VPN profile.
- **Prevent:** push DNS settings (servers **and** search domains) with the VPN profile, and monitor name resolution, not just reachability.

### T2 · A 169.254.x.x address

- **Step:** 2 · Local configuration. `169.254.0.0/16` is **link-local** (APIPA): the laptop asked for an address by **DHCP**, got no answer, and gave itself one. It has no gateway and no DNS, so nothing beyond the link works ([2.8](../../02-ip-addressing-and-subnetting/08-dhcp.md)).
- **Likely cause:** the router's DHCP server is down or its pool is exhausted. Alternative: the Wi-Fi joined a network or VLAN with no DHCP server.
- **Confirm:** renew and watch: `sudo ipconfig set en0 DHCP` on a Mac, or `sudo dhclient -v <iface>` on Linux; "no offers" confirms it. Check whether other devices got addresses.
- **Fix:** restart the router's DHCP service, enlarge the pool or shorten leases; as a stopgap, set a static address in the right subnet.
- **Prevent:** size DHCP pools for peak devices (phones, guests); monitor pool usage.

### T3 · Ping by IP works, names don't

- **Step:** 1 · DNS. The route to the internet works (`8.8.8.8` replies); `Temporary failure in name resolution` means the resolver at `10.0.0.53` didn't answer.
- **Likely cause:** `10.0.0.53` is wrong or down (a leftover from an old network, or a resolver that was decommissioned). Alternative: a firewall blocks **UDP** 53 to it.
- **Confirm:** `dig @10.0.0.53 archive.ubuntu.com` (timeout or refused?), then `dig @8.8.8.8 archive.ubuntu.com` (works → the path is fine, the resolver isn't).
- **Fix:** point the system at a working resolver, in the place that manages `/etc/resolv.conf` on that system (netplan, systemd-resolved, DHCP options), not by hand-editing a file that will be overwritten.
- **Prevent:** at least two resolvers; configuration management for DNS settings.

---

## 🟡 Intermediate

### T4 · Port timeout, ping works

- **Step:** 5 · Rules (reached via 3 · Port). A **timeout** on a TCP port, while the host answers ping and the database listens on all addresses, means packets to 5432 are **dropped**.
- **Likely cause:** a firewall or security group doesn't allow TCP 5432 from the app server. Alternative: a host firewall on the database server (`ufw`, `firewalld`, `iptables`).
- **Confirm:** on the database server, `sudo tcpdump -ni any 'tcp port 5432'` while retrying. **No SYN arriving** → something on the path drops it; **SYNs arriving with no reply** → the host firewall. Then read the rules on that hop.
- **Fix:** allow TCP 5432 **from the app servers only** (their subnet or security group), not from everywhere.
- **Prevent:** define database access rules in code alongside the app; test with `nc -zv` from the app host in deployment checks. Remember ping proves nothing about a TCP port.

### T5 · Refused instantly; listening on 127.0.0.1

- **Step:** 4 · Listener. `(7)` after 0 ms means the host answered with a **reset**: nothing listens on `10.20.5.30:8080`. `ss` shows why: the app listens on **`127.0.0.1:8080`** only.
- **Likely cause:** the app's default bind address is localhost (common for development servers). Alternative: the app listens on a different port.
- **Confirm:** `ss -ltnp | grep 8080` (already shown) and compare with `curl` from the host itself (works) versus from outside (refused).
- **Fix:** configure the app to listen on `0.0.0.0` (or the host's IP) and restart it. Then make sure the firewall allows 8080 from the clients that need it.
- **Prevent:** a health check that runs **from outside** the host (load balancer or monitoring), not `curl localhost`.

### T6 · Requests arrive, replies don't come back

- **Step:** 2 · Route, the **return path**. The data-centre server receives the echo requests but doesn't answer usefully: its route to `10.60.0.25` goes via `10.10.0.1`, and from there the route back to the new office is missing.
- **Likely cause:** the new subnet `10.60.0.0/24` was added on the office side of the WAN, but the data-centre routers (or the WAN/VPN routing) don't have a route back to it. Internet access works because it goes out through a different path (the office's own internet breakout or NAT). Alternative: a firewall in the data centre doesn't allow the new subnet.
- **Confirm:** on `10.10.0.1` (and the WAN routers), `ip route get 10.60.0.25` or `show ip route 10.60.0.25`: no route, or a default route pointing to the internet. A capture on the data-centre server's uplink shows replies leaving towards the wrong place, or `traceroute` from the server stops at the first router.
- **Fix:** add the route to `10.60.0.0/24` (or advertise it in the dynamic routing protocol) on the data-centre side, and update firewall rules for the new range.
- **Prevent:** a checklist for new subnets: routes **both** ways, firewall rules, DNS, monitoring. Summarisable address plans make this a single route ([2.5](../../02-ip-addressing-and-subnetting/05-vlsm-and-route-summarization.md)).

### T7 · The MAC address keeps changing

- **Step:** 2 · Local (layer 2/3). The same IP maps to **two different MAC addresses** at different times: a **duplicate IP address**. Clients send to whichever machine answered ARP last, so connections break and recover.
- **Likely cause:** another device was given `192.168.10.20` statically (or a DHCP pool overlaps a static address). Alternative: an ARP-spoofing attack (less likely on a normal office network, but the evidence looks the same).
- **Confirm:** `sudo arping -D -I eth0 -c 3 192.168.10.20` from a host on the subnet: replies from **more than one MAC** confirm a conflict. Look up the second MAC's vendor prefix (`8c:16:45`) and find its switch port in the switch's MAC table.
- **Fix:** give the intruding device a different address, or move the static address out of the DHCP pool.
- **Prevent:** keep static addresses outside DHCP ranges, use DHCP reservations, enable duplicate-address detection and DHCP snooping / dynamic ARP inspection on managed switches.

---

## 🟠 Advanced

### T8 · One in three requests gets a 502

- **Step:** 6 · App. A `502` comes from the **load balancer**: it got an invalid response, or none, from a backend. A regular one-in-three pattern with three backends points to **one bad backend**.
- **Likely cause:** one backend is broken for `/cart` (a failed deploy, a missing config or dependency), but the health check only tests `GET /`, which still works, so the load balancer keeps sending it traffic. Alternative: one backend has a keep-alive timeout shorter than the load balancer's idle timeout, so the LB sometimes reuses a connection the backend has just closed. That causes **intermittent** 502s, usually not a strict pattern.
- **Confirm:** call each backend **directly**, bypassing the load balancer: `curl -s -o /dev/null -w '%{http_code}\n' http://<backend-ip>:<port>/cart` for each one, and read the load balancer's access log for which target returned the error.
- **Fix:** take the bad backend out of service, fix or redeploy it.
- **Prevent:** health checks on an endpoint that exercises the real dependencies (a `/health` that checks the database), and deployment checks before a backend receives traffic.

### T9 · Small works, large hangs, over a new VPN

- **Step:** 6 · Size / path MTU (it's a route-layer problem that looks like an app problem).
- **Likely cause:** a **path MTU black hole**. The VPN adds headers, so the tunnel carries packets smaller than 1500 bytes. A full-size packet is refused somewhere, and the ICMP "fragmentation needed" message never reaches the sender. The evidence: a 1,500-byte packet with DF set disappears **silently** (no "Frag needed" error comes back), while 1,378 bytes gets through.
- **Confirm:** find the largest size that works: `ping -M do -s <size>` and bisect between 1350 and 1472; `tracepath` from **both** ends. A capture on the sending server shows the same large segment being retransmitted.
- **Fix:** **clamp the TCP MSS** on the VPN gateways (`iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu` on Linux, or the vendor's "TCP MSS adjust" setting), and allow ICMP type 3 code 4 (and ICMPv6 "packet too big") on firewalls. Tested in [Lab 3.5](../../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md), fault 8.
- **Prevent:** never block all ICMP; document the tunnel MTU and set MSS clamping as part of every VPN build.

### T10 · Asymmetric routing through stateful firewalls

- **Step:** 2 · Route (and 5 · Rules). The server **does** answer (SYN-ACKs leave), but they never reach the client, and the client keeps retransmitting its SYN.
- **Likely cause:** **asymmetric routing**. The SYN goes through firewall **A**, which records the new connection. The SYN-ACK returns through firewall **B**, which has never seen the SYN, so it treats the SYN-ACK as an invalid, out-of-state packet and **drops** it. Stateful devices need to see **both directions** of a flow.
- **Confirm:** `traceroute` in both directions (already shown: A out, B back); check firewall B's logs or counters for dropped "invalid state" / "no session" packets from `10.2.8.10:443`.
- **Fix:** make routing **symmetric** for these subnets (fix the routing change so both directions use the same firewall), or cluster the firewalls so they share connection state.
- **Prevent:** design paths through stateful devices to be symmetric; when changing routes, check both directions. The same thing happens with multiple NAT gateways or load balancers.

### T11 · Browser OK, app fails: the missing intermediate

- **Step:** 6 · App (TLS).
- **Likely cause:** the server sends **only its own certificate** (`0 s:`), not the **intermediate CA** certificate that links it to a trusted root. Clients need the full chain. Browsers often hide the problem because they cache intermediates from other sites or download them using the certificate's AIA (Authority Information Access) URL; `curl`, Java and most libraries don't. `Verify return code: 21 (unable to verify the first certificate)` with a single certificate in the chain is the signature.
- **Confirm:** `openssl s_client -showcerts …`: only one certificate is sent. Online checkers show "chain incomplete" too.
- **Fix:** the **server** must be configured with the full chain (its certificate followed by the intermediate, in one "fullchain" file). Don't "fix" it on clients by disabling verification, or by trusting the intermediate on every client.
- **Prevent:** deploy the fullchain file; monitor certificates with a client that doesn't fetch missing intermediates.

---

## 🔴 Expert

### T12 · NAT port exhaustion

- **Step:** 3 · Port, on the NAT device (new connections fail, existing ones work).
- **Likely cause:** **source-port exhaustion** on the NAT gateway. All workers call **one destination** (one IP, port 443, TCP), and each call opens a **new** connection, so the NAT needs a fresh source port per call. Vendor-specific (AWS): a NAT gateway supports up to 55,000 simultaneous connections to each unique destination per public IP address, and `ErrorPortAllocation` counts the connections it couldn't create. Connections closed recently also hold their ports for a while.
- **Confirm:** `ErrorPortAllocation` > 0 at exactly the failure times, and `ActiveConnectionCount` near the limit; the client side shows connect timeouts, not TLS or HTTP errors.
- **Fix (combine):** **reuse connections** (HTTP keep-alive and a connection pool per worker; this alone usually removes the problem); **add public IPs** to the NAT gateway, or spread the subnets over **more NAT gateways**; spread the batch over time.
- **Prevent:** alarm on `ErrorPortAllocation`; load-test with realistic connection patterns, not just request rates.

### T13 · Idle connections silently dropped

- **Step:** 5 · Rules / state, on the middlebox.
- **Likely cause:** the firewall or NAT keeps a **state table** with an **idle timeout**. After a quiet period, it deletes the entry for an idle connection. Neither the app nor the database knows. The next packet the app sends matches no entry, and the device answers with a **reset** (or drops it, which shows up as a long hang instead). Vendor-specific example: an AWS NAT gateway times out idle connections after 350 seconds and sends a RST.
- **Confirm:** find the device's idle timeout setting; capture at the app server: the first query after the quiet period gets an immediate **RST**. The failures correlate with idle time, not with load.
- **Fix:** keep connections alive or retire them before the timeout: a connection-pool **max idle time** shorter than the device's timeout, or **TCP keepalive** with `tcp_keepalive_time` below it (the Linux default, 7,200 s, is longer than most middlebox timeouts). Retry once on a reset for idempotent queries.
- **Prevent:** know the idle timeout of every stateful device on long-lived paths (NAT, firewalls, load balancers) and set pool and keepalive settings below the **smallest**.

### T14 · One long-distance TCP stream is slow

- **Step:** 6 · Performance (no error: it's a throughput problem).
- **Why one stream is slow:** a single TCP connection can't send more than its **congestion window** per round trip. Here `cwnd:580` × `mss:1448` ≈ 840 KB per 170 ms ≈ **39.5 Mbit/s**, exactly what `ss` reports. To fill 1 Gbit/s at 170 ms, about **21 MB** must be in flight ([bandwidth-delay product](../../01-networking-fundamentals/04-network-performance.md)), roughly 14,700 segments. Eight streams each get their own window, so the total rises.
- **Likely cause:** **packet loss** keeps the window small. `retrans:0/1834` shows 1,834 retransmissions over the connection's life; CUBIC cuts its window on every loss and grows it back slowly on a long RTT. Alternatives: socket buffer limits (`net.ipv4.tcp_wmem` / `tcp_rmem` maximums smaller than the BDP), or a shaper or policer on the path.
- **Confirm:** watch `ss -tin` over time (does `cwnd` collapse at each retransmission?); check the buffer maximums with `sysctl net.ipv4.tcp_wmem net.ipv4.tcp_rmem`; test with `iperf3 -c <server> -t 30` and then `-P 8` to compare one stream with many.
- **Fix:** find and fix the loss if possible (an interface with errors, a congested link); raise buffer maximums to at least the BDP; try **BBR** on the **sender** (`sysctl -w net.ipv4.tcp_congestion_control=bbr`, if the kernel has it), which tolerates random loss better; keep parallel streams for bulk copies.
- **Prevent:** benchmark long-haul transfers with `iperf3` before relying on them; for user-facing traffic, reduce the RTT instead (serve from a nearer region or CDN).
