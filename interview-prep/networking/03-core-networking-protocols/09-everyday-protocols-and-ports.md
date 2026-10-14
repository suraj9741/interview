# 3.9 · Everyday Protocols and Ports

> **Level 3 · Core networking protocols** · Lesson 9 of 11 · ⏱️ about 60 minutes (estimate)
> ⬅️ [3.8 NAT, PAT and port forwarding](08-nat-pat-and-port-forwarding.md) · ➡️ [3.10 Packet flow end to end](10-packet-flow-end-to-end.md)

## What you'll learn

- What the protocols you'll meet on the job **do**, which **port and transport** they use, and whether they're **encrypted**.
- **SSH** in enough depth for daily DevOps work: keys, host keys, tunnels and jump hosts.
- Why **NTP** (time) quietly breaks TLS, Kerberos and logs when it fails.
- Which ports a **Kubernetes** cluster, a **monitoring** stack and a **VPN** need open.

## Before you start

- [3.2](02-tcp-and-udp.md): TCP vs UDP and port ranges.
- [3.6](06-tls-and-certificates.md): what "encrypted with TLS" means.

---

## The idea in plain words

Ports are **doors with signs on them**. Port 22 says "SSH", port 443 says "HTTPS". The sign is a **convention** (registered with IANA, listed in `/etc/services`), not a law: you can run SSH on port 2222, and a firewall that allows "443" allows **anything** that uses port 443. Knowing the common doors lets you read firewall rules, security groups and `ss` output at a glance.

## Why it matters

- Security groups, NACLs and NetworkPolicies are lists of **protocol + port**. You need to know what each one means and what breaks if it's closed.
- Many old protocols send **passwords in clear text** (Telnet, FTP, SNMPv2c, plain LDAP). Spotting them is an easy security win.

---

## How it works

The port numbers below for the classic protocols were checked against the lab container's `/etc/services` (`getent services <port>/<proto>`) **(tested in the lab container)**. Application ports that aren't in that file (e.g. 6443, 9090, 10250) are the projects' own defaults. A longer list is in [references/common-ports.md](../references/common-ports.md).

### Remote access and file transfer

| Protocol | Port | Encrypted? | Notes |
|---|---|---|---|
| **SSH** | 22/tcp | ✅ | Shell, file copy (`scp`, **SFTP**), tunnels. See below |
| Telnet | 23/tcp | ❌ | Clear-text remote shell. Only for lab devices; useful as a crude TCP port tester |
| **FTP** | 21/tcp (control) + 20/tcp or a random high port (data) | ❌ | Two connections: painful through NAT and firewalls (**active** mode: server connects back to the client; **passive**: client connects to a random server port). Prefer SFTP. FTPS = FTP over TLS |
| TFTP | 69/udp | ❌ | Trivial file transfer, no authentication. Network boot (PXE), device firmware |
| **RDP** | 3389/tcp (and udp) | ✅ | Windows remote desktop. Never expose to the internet; use a VPN, bastion or AWS Systems Manager |
| rsync | 873/tcp (daemon mode) | ❌ | Usually run **over SSH** instead |

### Infrastructure services

| Protocol | Port | Notes |
|---|---|---|
| **DNS** | 53/udp + 53/tcp | [3.4](04-dns.md). DoT 853/tcp, DoH 443/tcp |
| **DHCP** | 67/udp (server), 68/udp (client) | [2.8](../02-ip-addressing-and-subnetting/08-dhcp.md). DHCPv6: 547/udp server, 546/udp client |
| **NTP** | 123/udp | Time synchronisation. See below |
| **Syslog** | 514/udp (traditional), 6514/tcp (over TLS) | Log shipping from network devices and servers |
| **SNMP** | 161/udp (queries), 162/udp (traps) | Monitoring network devices. v1/v2c use a clear-text "community string" as a password; **v3** adds authentication and encryption |
| **LDAP** / LDAPS | 389/tcp / 636/tcp | Directory lookups (users, groups). Active Directory also uses 3268 (Global Catalog) |
| **Kerberos** | 88/tcp+udp | Ticket-based authentication (Active Directory). Needs clocks within 5 minutes by default |
| **SMB** | 445/tcp | Windows file shares. Never expose to the internet |
| **NFS** | 2049/tcp | Unix file shares; **AWS EFS** uses it |
| **BGP** | 179/tcp | Routing between networks ([Level 4](../04-switching-and-routing/README.md)) |

### Email

| Protocol | Port | Notes |
|---|---|---|
| **SMTP** (server to server) | 25/tcp | Relaying mail between servers. **AWS restricts outbound port 25 from EC2 by default**; you request removal or use a mail service |
| SMTP **submission** (client to server) | 587/tcp (STARTTLS), 465/tcp (implicit TLS) | What apps should use to send mail (e.g. to Amazon SES) |
| IMAP / IMAPS | 143 / 993 tcp | Reading mail, kept on the server |
| POP3 / POP3S | 110 / 995 tcp | Downloading mail |

### Web and APIs

| Protocol | Port | Notes |
|---|---|---|
| HTTP / HTTPS | 80 / 443 tcp; HTTP/3 on **443/udp** | [3.5](05-http-and-https.md) |
| Alternate HTTP | 8080, 8443, 8000, 3000, 5000 | Conventions for dev servers and app containers |
| gRPC | Usually 443 or the app's own port | HTTP/2 underneath |
| WebSocket | Same as HTTP/HTTPS | Starts as HTTP, upgrades (`101 Switching Protocols`) |

### Databases, caches and queues

| Service | Port |
|---|---|
| MySQL / MariaDB | 3306/tcp |
| PostgreSQL | 5432/tcp |
| Microsoft SQL Server | 1433/tcp |
| Oracle | 1521/tcp (convention) |
| MongoDB | 27017/tcp |
| Redis | 6379/tcp |
| Memcached | 11211/tcp |
| RabbitMQ (AMQP) / management UI | 5672/tcp / 15672/tcp |
| Kafka | 9092/tcp |
| Elasticsearch / OpenSearch | 9200/tcp |

### VPNs and overlays

| Protocol | Port / protocol | Notes |
|---|---|---|
| **IPsec** | 500/udp (IKE), 4500/udp (NAT traversal), plus IP protocol **50 (ESP)** | Site-to-site VPNs, **AWS Site-to-Site VPN**. ESP isn't TCP or UDP, so firewall rules need the protocol number |
| **WireGuard** | 51820/udp (default) | Simple, fast modern VPN |
| OpenVPN | 1194/udp (default) | |
| **VXLAN** | 4789/udp (IANA); Linux/flannel default **8472/udp** | Ethernet frames inside UDP: Kubernetes overlays (flannel, Calico VXLAN mode) |
| Geneve | 6081/udp | Newer overlay; used by AWS Gateway Load Balancer and some CNIs |

### Kubernetes and observability

| Component | Port |
|---|---|
| kube-apiserver | **6443/tcp** |
| etcd | **2379/tcp** (clients), **2380/tcp** (peers) |
| kubelet API | **10250/tcp** |
| kube-controller-manager / kube-scheduler | 10257/tcp / 10259/tcp |
| NodePort Services | **30000–32767** (tcp/udp) |
| Prometheus / Alertmanager / node exporter | 9090 / 9093 / 9100 tcp |
| Grafana | 3000/tcp |
| OpenTelemetry (OTLP gRPC / HTTP) | 4317 / 4318 tcp |
| StatsD | 8125/udp |
| HashiCorp Vault | 8200/tcp |

### SSH in practice

SSH (RFC 4253 and friends) gives an encrypted channel for a shell, file transfer and tunnels.

**Two kinds of keys, often confused:**

| Key | Proves | Where you see it |
|---|---|---|
| **Host key** | The **server** is the one you connected to last time | `~/.ssh/known_hosts`; the "authenticity of host can't be established" prompt; `REMOTE HOST IDENTIFICATION HAS CHANGED!` when it changes (rebuilt server, or a man-in-the-middle) |
| **User key** (`~/.ssh/id_ed25519`) | **You** are allowed in | Your public key in the server's `~/.ssh/authorized_keys` |

**Everyday commands** (not run in the lab container, which has no SSH tools installed):

```bash
ssh-keygen -t ed25519 -C "you@laptop"          # create a key pair
ssh-copy-id user@server                        # install your public key on a server
ssh -J user@bastion user@10.0.2.15             # jump through a bastion (ProxyJump)
ssh -L 5432:db.internal:5432 user@bastion      # local forward: localhost:5432 → db via the bastion
ssh -R 8080:localhost:3000 user@server         # remote forward: server:8080 → your laptop:3000
ssh -D 1080 user@server                        # dynamic SOCKS proxy
ssh -v user@server                             # verbose: see which keys and algorithms are tried
```

**In AWS**, prefer **Systems Manager Session Manager** or **EC2 Instance Connect** over opening port 22 to the internet: no inbound rule, no long-lived keys, and sessions are logged.

### NTP: why time is a network dependency

NTP (123/udp) keeps clocks in sync, usually to within milliseconds. When clocks drift:

- **TLS** fails: certificates look "not yet valid" or "expired" ([3.6](06-tls-and-certificates.md)).
- **Kerberos / Active Directory** logins fail beyond 5 minutes of skew.
- **Logs and traces** from different machines can't be put in order; distributed databases and token expiry misbehave.

AWS provides the **Amazon Time Sync Service** at `169.254.169.123` (link-local, reachable from every instance). On Linux, `chronyc tracking` or `timedatectl` shows the sync state.

---

## Try it

```bash
getent services 22/tcp 53/udp 443/tcp 5432/tcp   # Linux: what /etc/services calls a port
grep -w 6379 /etc/services                       # macOS and Linux
ss -tulpn                                        # Linux: what's listening, on which protocol
lsof -nP -iTCP -sTCP:LISTEN                      # macOS: TCP listeners
nc -zv -w 3 smtp.gmail.com 587                   # does a TCP port answer?
openssl s_client -connect smtp.gmail.com:587 -starttls smtp </dev/null | head   # STARTTLS
```

## In the real world

- **Security group design:** open the **service port** only to the **source that needs it** (e.g. 5432 only from the app's security group), never `0.0.0.0/0` for databases, SSH or RDP.
- **EKS / Kubernetes:** the control plane talks to kubelets on **10250**; worker nodes need **443** to the API; pods need **53 tcp/udp** to CoreDNS; overlays need their UDP port open between nodes.
- **Corporate networks** often allow only 80/443 out; tools that need other ports (Git over SSH on 22, database clients) fail there. GitHub offers SSH over port 443 (`ssh.github.com`) for that reason.

## Common mistakes

| Mistake | Fix |
|---|---|
| "Port 443 is open, so it's HTTPS" | A port is a convention; check what actually answers (`openssl s_client`, `curl -v`) |
| Opening SSH/RDP/DB ports to the world | Restrict by source, use a bastion/VPN/Session Manager |
| Allowing only TCP for VPN or overlay traffic | IPsec needs UDP 500/4500 **and** ESP (protocol 50); VXLAN is UDP |
| Ignoring time sync | Monitor NTP/chrony; many "TLS" and "auth" bugs are clock bugs |
| Using SNMPv2c or Telnet on production devices | SNMPv3 and SSH |

## Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| `ssh: connect to host … port 22: Connection timed out` | Security group / firewall / routing | `nc -zv host 22`; SG inbound rule from **your** IP |
| `Permission denied (publickey)` | Wrong key, wrong user (`ec2-user` vs `ubuntu`), or key not in `authorized_keys` | `ssh -v`: which key is offered? |
| `REMOTE HOST IDENTIFICATION HAS CHANGED!` | Server rebuilt with new host keys (or a real attack) | Verify, then `ssh-keygen -R host` |
| App can't send mail from EC2 | Port 25 restricted | Use 587 to a mail service (e.g. SES) |
| Kerberos/AD login errors, TLS "not yet valid" | Clock skew | `timedatectl`, `chronyc tracking` |

## Hands-on lab

No dedicated lab: use `ss -tulpn` (Linux) or `lsof -nP -i` (Mac) on your own machine and identify every listening port with this lesson and [references/common-ports.md](../references/common-ports.md). Then do the [Level 3 exercises](../14-practice-exercises/03-level-3-protocols.md), section B (ports).

## Interview angle

- **"Which ports does Kubernetes need?"** → 6443 API, 2379–2380 etcd, 10250 kubelet, 30000–32767 NodePorts, plus the CNI's overlay port and 53 for DNS.
- **"SFTP vs FTPS?"** → SFTP runs over SSH (one port, 22). FTPS is FTP inside TLS (still two connections, firewall-unfriendly).
- **"How do you reach a private database from your laptop?"** → SSH local forward through a bastion (`ssh -L`), or Session Manager port forwarding; never open the DB to the internet.
- **"Why does time sync matter?"** → TLS validity, Kerberos, log correlation, token expiry.
- **"What does IPsec need through a firewall?"** → UDP 500, UDP 4500 (NAT-T), and IP protocol 50 (ESP).

## Check yourself

1. Name the port and transport for: SSH, DNS, NTP, PostgreSQL, the Kubernetes API, HTTP/3.
2. Which of these send credentials in clear text: Telnet, SSH, FTP, SFTP, SNMPv2c, LDAPS?
3. What does `ssh -L 8443:internal-api:443 user@bastion` let you do?
4. Your first SSH to a new server asks you to confirm a fingerprint. What is it, and why does it matter?
5. A VPN between two sites won't come up; UDP 500 and 4500 are allowed. What else might be blocked?

<details>
<summary><b>Answers</b> (try first)</summary>

1. SSH **22/tcp**; DNS **53/udp + tcp**; NTP **123/udp**; PostgreSQL **5432/tcp**; Kubernetes API **6443/tcp**; HTTP/3 **443/udp**.
2. **Telnet, FTP, SNMPv2c.** (SSH, SFTP and LDAPS are encrypted.)
3. Open `https://localhost:8443` on your laptop and reach `internal-api:443` **through the bastion**, over the encrypted SSH connection.
4. The server's **host key** fingerprint. Accepting it stores it in `known_hosts`, so a later different key (a server rebuild or a man-in-the-middle) triggers a warning.
5. **ESP** (IP protocol 50), if the VPN isn't using NAT traversal (which wraps ESP in UDP 4500).

</details>

## Summary

- A port is a **convention**; check what actually answers.
- Clear-text legacy protocols (Telnet, FTP, SNMPv2c, LDAP) have encrypted replacements (SSH, SFTP, SNMPv3, LDAPS).
- **SSH**: host keys protect you from impostors; user keys let you in; `-J`, `-L`, `-R`, `-D` cover most access needs.
- **NTP** failures break TLS and authentication.
- Know the Kubernetes, monitoring and VPN port sets; open each only to the sources that need it.

## Next

➡️ [3.10 · Packet flow end to end](10-packet-flow-end-to-end.md): everything from Levels 1–3 in one walk, from typing a URL to the page arriving.
