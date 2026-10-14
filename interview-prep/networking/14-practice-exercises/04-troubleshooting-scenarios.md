# Troubleshooting Scenarios · Beginner to Expert

> Practises the 6-step method from [3.11 · Troubleshooting connectivity](../03-core-networking-protocols/11-troubleshooting-connectivity.md).
> ⏱️ about 5–10 minutes per scenario (estimate) · Solutions: [solutions/04-troubleshooting-scenarios-solutions.md](solutions/04-troubleshooting-scenarios-solutions.md)
> Difficulty: 🟢 beginner · 🟡 intermediate · 🟠 advanced · 🔴 expert

**How to use this.** For each scenario, answer four questions **out loud or in writing** before reading the solution:

1. **Which step** of the method does the evidence point to (DNS, route, port, listener, rules, app)?
2. What's the **most likely cause**? Name one alternative.
3. What **one command** (and where would you run it) would confirm it?
4. What's the **fix**, and how would you **prevent** it next time?

**About the evidence.** Each scenario says where its evidence comes from. **(tested)** means the same output was captured in one of this curriculum's labs. **(illustrative)** means the output was written for the exercise, in the format the real tool prints, but not captured from a real run. Container and Kubernetes cases are in the [interview scenarios N1–N13](../15-interview-preparation/troubleshooting-scenarios-docker-kubernetes-aws.md); these focus on general networks.

---

## 🟢 Beginner

### T1 · "The internal wiki doesn't open"

A colleague on the office VPN can't open `http://wiki.corp.example`. Other websites work.

```text
$ curl -sS http://wiki.corp.example/
curl: (6) Could not resolve host: wiki.corp.example
$ curl -sS -o /dev/null -w '%{http_code}\n' http://10.40.2.15/
200
```

Evidence: **(illustrative)**; the `curl: (6)` message format was tested on the Mac.

### T2 · "Wi-Fi is connected, but nothing works"

A laptop shows full Wi-Fi bars. No website loads, and the router's admin page doesn't open either.

```text
$ ipconfig getifaddr en0
169.254.23.7
```

Evidence: **(illustrative)**.

### T3 · "Ping works, websites don't"

A Linux server can't install packages.

```text
$ ping -c 2 8.8.8.8
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
$ ping -c 2 archive.ubuntu.com
ping: archive.ubuntu.com: Temporary failure in name resolution
$ cat /etc/resolv.conf
nameserver 10.0.0.53
```

Evidence: **(illustrative)**.

---

## 🟡 Intermediate

### T4 · "The database times out, but the server is up"

An app server can't connect to PostgreSQL on `10.20.3.15`.

```text
$ ping -c 2 10.20.3.15
2 packets transmitted, 2 received, 0% packet loss
$ nc -zv -w 5 10.20.3.15 5432
nc: connect to 10.20.3.15 port 5432 (tcp) timed out: Operation now in progress
```

On the database server, PostgreSQL is running and `ss -ltn` shows `0.0.0.0:5432`.
Evidence: **(illustrative)**; a timed-out connection with ping working was reproduced in [Lab 3.5](../13-hands-on-labs/lab-03.5-troubleshooting-challenge.md).

### T5 · "Connection refused, instantly"

A new service was deployed on `10.20.5.30`. From another host:

```text
$ curl -sS http://10.20.5.30:8080/health
curl: (7) Failed to connect to 10.20.5.30 port 8080 after 0 ms: Couldn't connect to server
```

On the service host:

```text
$ curl -s http://localhost:8080/health
{"status":"ok"}
$ ss -ltnp | grep 8080
LISTEN 0      5          127.0.0.1:8080      0.0.0.0:*    users:(("python3",pid=10060,fd=3))
```

Evidence: **(tested)**, same pattern as Lab 3.5; addresses changed for the exercise.

### T6 · "The new office can reach the internet, but not the data centre"

A new office subnet `10.60.0.0/24` was connected to the company WAN. Its users can browse the internet, but nothing in the data centre (`10.10.0.0/16`) answers. A capture on a data-centre server, while an office laptop pings it:

```text
IP 10.60.0.25 > 10.10.4.20: ICMP echo request, id 41, seq 1, length 64
IP 10.60.0.25 > 10.10.4.20: ICMP echo request, id 41, seq 2, length 64
```

```text
$ ip route get 10.60.0.25          # on the data-centre server
10.60.0.25 via 10.10.0.1 dev eth0 src 10.10.4.20
```

Evidence: **(illustrative)**; the "request arrives, no reply" pattern was tested in [Lab 2.2](../13-hands-on-labs/lab-02.2-routing-between-two-subnets.md).

### T7 · "It works, then it doesn't, then it works"

Users report that the file server `192.168.10.20` disconnects every few minutes. On a client:

```text
$ ip neigh show 192.168.10.20
192.168.10.20 dev eth0 lladdr 3c:22:fb:12:34:56 REACHABLE
… two minutes later …
$ ip neigh show 192.168.10.20
192.168.10.20 dev eth0 lladdr 8c:16:45:aa:bb:cc STALE
```

Evidence: **(illustrative)**.

---

## 🟠 Advanced

### T8 · "One request in three fails"

A web app sits behind a load balancer with three backends. Users see an error page about one time in three:

```text
$ for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w '%{http_code} ' https://shop.example.com/cart; done; echo
200 502 200 200 502 200
```

The load balancer's health check is `GET /` and shows all three backends **healthy**.
Evidence: **(illustrative)**.

### T9 · "SSH works over the VPN, but `git clone` hangs"

After moving to a new site-to-site VPN, engineers can SSH to build servers and run small commands. `git clone` of a large repository starts, then hangs forever. Small web pages from the same servers load; large downloads stall.

```text
$ ping -c 1 -M do -s 1472 10.30.1.10
PING 10.30.1.10 (10.30.1.10) 1472(1500) bytes of data.

--- 10.30.1.10 ping statistics ---
1 packets transmitted, 0 received, 100% packet loss, time 0ms
$ ping -c 1 -M do -s 1350 10.30.1.10
1358 bytes from 10.30.1.10: icmp_seq=1 ttl=62 time=21.4 ms
```

Evidence: **(illustrative)**; the same symptom (headers, then 0 bytes, then a timeout) was reproduced in Lab 3.5.

### T10 · "SYN goes out, SYN-ACK goes out, nobody connects"

A network has two firewalls in parallel (A and B) between the users and the servers, both stateful. After a routing change, some users can't connect to a server. On the **server**:

```text
IP 10.1.5.40.53122 > 10.2.8.10.443: Flags [S], seq 1840022317, win 64240, length 0
IP 10.2.8.10.443 > 10.1.5.40.53122: Flags [S.], seq 993102211, ack 1840022318, win 65160, length 0
IP 10.1.5.40.53122 > 10.2.8.10.443: Flags [S], seq 1840022317, win 64240, length 0
IP 10.2.8.10.443 > 10.1.5.40.53122: Flags [S.], seq 993102211, ack 1840022318, win 65160, length 0
```

The client's capture shows only its own SYNs, never a SYN-ACK. `traceroute` from the client goes through firewall **A**; `traceroute` from the server back to the client goes through firewall **B**.
Evidence: **(illustrative)**.

### T11 · "It works in the browser, but not from the app"

Browsers open `https://partner-api.example.net` without any warning. A Java service and `curl` on a Linux server both fail:

```text
$ curl -sS https://partner-api.example.net/
curl: (60) SSL certificate problem: unable to get local issuer certificate
$ echo | openssl s_client -connect partner-api.example.net:443 -servername partner-api.example.net 2>/dev/null | grep -E '^ *[0-9] s:|^ *i:|Verify return'
 0 s:CN = partner-api.example.net
   i:C = US, O = Example Trust, CN = Example Trust Intermediate CA 2
Verify return code: 21 (unable to verify the first certificate)
```

The server's CA bundle is up to date. Evidence: **(illustrative)**; the error messages are the ones reproduced in [Lab 3.3](../13-hands-on-labs/lab-03.3-tls-certificates-and-handshake.md).

---

## 🔴 Expert

### T12 · "New connections fail at peak, old ones keep working"

During a daily batch job, 400 workers in private subnets call one payment provider's API through a single NAT gateway. At peak, new calls fail with connection timeouts, while long-running calls complete normally. The NAT gateway's metrics show a non-zero `ErrorPortAllocation` during the failures, and `ActiveConnectionCount` reaches about 55,000. Each worker opens a new HTTPS connection for every call.
Evidence: **(illustrative)**; the metric names are AWS's.

### T13 · "The first query after lunch always fails"

A reporting service keeps a pool of database connections. Every morning and after quiet periods, the first query on some connections fails with `Connection reset by peer`; a retry works. The service reaches the database through a firewall (or NAT) appliance. During busy hours there are no errors.
Evidence: **(illustrative)**.

### T14 · "Uploads to Singapore are slow, but the link is fast"

A backup job copies large files from Frankfurt to a server in Singapore over a 1 Gbit/s path with an RTT of about 170 ms. One copy runs at about 40 Mbit/s. With 8 parallel copies, total throughput rises to about 300 Mbit/s.

```text
$ ss -tin dst 203.0.113.80
… cubic wscale:7,7 rto:372 rtt:170.2/0.4 mss:1448 cwnd:580 … send 39.5Mbps … retrans:0/1834 …
```

Evidence: **(illustrative)**; fields as printed by `ss -ti` (Lab 3.1 shows a tested example).
