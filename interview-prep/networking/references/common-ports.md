# Common Ports

> **Reference.** The ports you'll meet in DevOps, cloud and interview work. Lessons: [1.3](../01-networking-fundamentals/03-addresses-ports-and-protocols.md) (what a port is) and [3.9](../03-core-networking-protocols/09-everyday-protocols-and-ports.md) (what each protocol does).

**How this list was checked.** The **Source** column says where each number comes from:

- **services**: listed in `/etc/services` on Ubuntu 24.04 (package `netbase` 6.4), which is generated from the IANA registry. Checked with `getent services <name>` on 14 Oct 2026.
- **default**: not in that file; it's the project's documented default or a strong convention. Software can be configured to use other ports, so always confirm with `ss -ltnp` on the real host.

Registered ≠ in use: a port number tells you what *usually* runs there, never what *actually* does.

## Port ranges

| Range | Name | Meaning |
|---|---|---|
| 0–1023 | Well-known (system) ports | Standard services. On Linux, binding to them needs root (or `CAP_NET_BIND_SERVICE`) |
| 1024–49151 | Registered ports | Assigned by IANA to specific applications on request |
| 49152–65535 | Dynamic / private | IANA's suggested range for ephemeral ports |
| 32768–60999 | Linux ephemeral range (default) | What Linux actually uses for outgoing connections: `cat /proc/sys/net/ipv4/ip_local_port_range` |

## Remote access and file transfer

| Port | Protocol | Service | Source |
|---|---|---|---|
| 22 | TCP | SSH, SCP, SFTP | services |
| 23 | TCP | Telnet (clear text; avoid) | services |
| 20, 21 | TCP | FTP data, FTP control | services |
| 69 | UDP | TFTP | services |
| 873 | TCP | rsync daemon | services |
| 3389 | TCP (and UDP) | RDP (Windows remote desktop) | services (`ms-wbt-server`, TCP) |

## Core network services

| Port | Protocol | Service | Source |
|---|---|---|---|
| 53 | UDP and TCP | DNS | services (`domain`) |
| 853 | TCP (and UDP for DNS over QUIC) | DNS over TLS | services (`domain-s`) |
| 67, 68 | UDP | DHCP server, client | services (`bootps`, `bootpc`) |
| 546, 547 | UDP | DHCPv6 client, server | default (RFC 8415) |
| 123 | UDP | NTP | services |
| 161, 162 | UDP (TCP also listed) | SNMP, SNMP traps | services |
| 514 | UDP | Syslog | services |
| 6514 | TCP | Syslog over TLS | services (`syslog-tls`) |
| 88 | TCP and UDP | Kerberos | services |
| 389 | TCP (and UDP) | LDAP | services |
| 636 | TCP | LDAPS | services |
| 3268 | TCP | Active Directory Global Catalog | default |
| 445 | TCP | SMB (Windows file sharing) | services (`microsoft-ds`) |
| 2049 | TCP (and UDP) | NFS (and AWS EFS) | services |
| 179 | TCP | BGP | services |

## Web and mail

| Port | Protocol | Service | Source |
|---|---|---|---|
| 80 | TCP | HTTP | services |
| 443 | TCP | HTTPS | services |
| 443 | UDP | HTTP/3 (QUIC) | services (listed as `https` 443/udp) |
| 8080, 8443, 8000, 3000, 5000 | TCP | Common development / alternate HTTP ports | default (convention only) |
| 25 | TCP | SMTP, server to server | services |
| 587 | TCP | SMTP submission (STARTTLS) | services (`submission`) |
| 465 | TCP | SMTP submission over implicit TLS | services (`submissions`) |
| 143, 993 | TCP | IMAP, IMAPS | services (`imap2`, `imaps`) |
| 110, 995 | TCP | POP3, POP3S | services |

## Databases, caches and queues

| Port | Protocol | Service | Source |
|---|---|---|---|
| 5432 | TCP | PostgreSQL | services |
| 3306 | TCP | MySQL, MariaDB | services |
| 1433 | TCP | Microsoft SQL Server | services (`ms-sql-s`) |
| 1521 | TCP | Oracle listener | default |
| 27017 | TCP | MongoDB | default |
| 6379 | TCP | Redis | services |
| 11211 | TCP | Memcached | default |
| 5672 | TCP | AMQP (RabbitMQ) | services |
| 15672 | TCP | RabbitMQ management UI | default |
| 9092 | TCP | Kafka broker | default |
| 9200 | TCP | Elasticsearch / OpenSearch HTTP API | default |

## VPNs and overlays

| Port | Protocol | Service | Source |
|---|---|---|---|
| 500 | UDP | IPsec IKE | services (`isakmp`) |
| 4500 | UDP | IPsec NAT traversal | services (`ipsec-nat-t`) |
| (IP protocol 50) | ESP | IPsec encrypted payload: a protocol number, **not a port** | IANA protocol numbers |
| 1194 | UDP (and TCP) | OpenVPN | services |
| 51820 | UDP | WireGuard | default |
| 4789 | UDP | VXLAN (IANA-assigned) | default (not in this `/etc/services`) |
| 8472 | UDP | VXLAN as used by the Linux kernel's default and flannel | default |
| 6081 | UDP | Geneve | default |

## Kubernetes and monitoring

| Port | Protocol | Component | Source |
|---|---|---|---|
| 6443 | TCP | kube-apiserver | default |
| 2379, 2380 | TCP | etcd client, peer | default |
| 10250 | TCP | kubelet API | default |
| 10257 | TCP | kube-controller-manager | default |
| 10259 | TCP | kube-scheduler | default |
| 30000–32767 | TCP and UDP | NodePort Services | default (configurable) |
| 9090 | TCP | Prometheus | default |
| 9093 | TCP | Alertmanager | default |
| 9100 | TCP | node exporter | default |
| 3000 | TCP | Grafana | default |

## Check a port yourself

```bash
getent services 5432                 # what /etc/services calls it (Linux)
grep -w 5432 /etc/services           # the same, on a Mac
ss -ltnp | grep ':5432'              # what is actually listening (Linux)
lsof -nP -iTCP:5432 -sTCP:LISTEN     # the same, on a Mac
nc -zv <host> 5432                   # can I connect from here?
```
