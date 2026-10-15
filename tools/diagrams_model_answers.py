#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/hemant-model-answers.md.

Run once:  python3 tools/diagrams_model_answers.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "diagrams"


def observability_stack():
    d = Diagram("46-observability-stack", 1000, 600,
                "Observability stack: metrics, logs and traces (open source, budget-friendly)")
    d.text("h-src", 20, 46, 180, 22, "Sources", size=13, bold=True)
    d.text("h-col", 280, 46, 190, 22, "Collectors", size=13, bold=True)
    d.text("h-be", 545, 46, 200, 22, "Store and query", size=13, bold=True)
    d.text("h-s3", 810, 46, 180, 22, "Long-term storage", size=13, bold=True)

    d.box("src-m", 20, 80, 180, 54, "Apps & nodes\nexpose /metrics", "blue")
    d.box("src-l", 20, 165, 180, 54, "Pod stdout / stderr\nlogs", "blue")
    d.box("src-t", 20, 250, 180, 54, "Apps with\nOpenTelemetry SDK", "blue")
    d.box("onprem", 20, 335, 180, 54, "On-prem servers\nAlloy / OTel agents", "purple")

    d.box("prom", 280, 80, 190, 54, "Prometheus\n(scrapes, alert rules)", "orange")
    d.box("fb", 280, 165, 190, 54, "Fluent Bit / Alloy\n(DaemonSet on each node)", "orange")
    d.box("otel", 280, 250, 190, 54, "OTel Collector\n(receives and samples)", "orange")

    d.group("be", 545, 66, 200, 252, "", "outline", dashed=True)
    d.box("mimir", 560, 80, 170, 54, "Mimir / Thanos\n(long-term metrics)", "green")
    d.box("loki", 560, 165, 170, 54, "Loki\n(indexes labels only)", "green")
    d.box("tempo", 560, 250, 170, 54, "Tempo\n(traces)", "green")

    d.box("s3", 820, 80, 160, 224, "Amazon S3\ncheap, durable\nobject storage", "yellow", shape="cylinder")

    d.box("grafana", 300, 410, 445, 64,
          "Grafana\ndashboards for metrics, logs and traces,\nlinked by labels and trace IDs", "blue")
    d.box("alert", 300, 505, 210, 54, "Alerting\nAlertmanager / Grafana", "red")
    d.box("notify", 600, 505, 190, 54, "On-call\nSlack · PagerDuty · email", "white")

    d.edge("src-m", "prom", "scraped\n(pull)")
    d.edge("src-l", "fb", "tailed")
    d.edge("src-t", "otel", "OTLP")
    d.edge("prom", "mimir", "remote_write")
    d.edge("fb", "loki", "push")
    d.edge("otel", "tempo", "OTLP")
    d.edge("mimir", "s3")
    d.edge("loki", "s3")
    d.edge("tempo", "s3")
    d.edge("onprem", "be", "push over VPN / Direct Connect", points=[(645, 362)])
    d.edge("grafana", "be", "queries: PromQL · LogQL · TraceQL", points=[(705, 390)])
    d.edge("grafana", "alert", "alert rules")
    d.edge("alert", "notify", "notify")
    d.text("caption", 0, 568, 1000, 26,
           "Alert on the golden signals; logs and traces explain why. All long-term data sits in cheap S3 storage.",
           size=11)
    return d


def url_to_page():
    d = Diagram("01-url-to-page", 1200, 400, "Q1 · What happens when you type mixy.com")
    steps = [("1 · Parse\nURL or search?\nno scheme → https\n(HSTS list)", "gray"),
             ("2 · DNS\nbrowser → OS cache, /etc/hosts\n→ resolver: root → .com\n→ authoritative (TTL)", "blue"),
             ("3 · Routing\nnot local → default gateway\nARP for its MAC\nrouter NAT → ISP", "purple"),
             ("4 · TCP handshake\nSYN, SYN-ACK, ACK\nto IP:443 from an\nephemeral port", "yellow"),
             ("5 · TLS handshake\nSNI, certificate checked\nagainst trusted CAs,\nsession keys", "orange"),
             ("6 · HTTP request\nGET /\nHost, cookies,\nheaders", "green"),
             ("7 · Server side\nCDN → load balancer\n→ app → database\nstatus, headers, body", "red"),
             ("8 · Render\nparse HTML → CSS, JS,\nimages = more requests\n(same connection)", "gray")]
    for i, (label, c) in enumerate(steps):
        row, col = divmod(i, 4)
        d.box(f"s{i}", 20 + col * 290, 60 + row * 150, 270, 100, label, c, size=11)
        if i and i != 4:
            d.edge(f"s{i - 1}", f"s{i}")
    d.edge("s3", "s4", points=[(1025, 185), (155, 185)])
    d.text("cap", 20, 330, 1160, 56,
           "Caches at every DNS step (browser, OS, resolver) for the TTL · DNS failures: NXDOMAIN, SERVFAIL, timeout\n"
           "HTTP/3 = QUIC over UDP: transport and TLS handshakes in one", size=11)
    return d


def dns_hierarchy():
    d = Diagram("09-dns-hierarchy", 1100, 440, "Q9 · Who answers what in DNS")
    d.box("stub", 20, 180, 190, 80, "Your machine\nstub resolver\n(resolv.conf)", "white", size=11)
    d.box("rec", 300, 170, 260, 100, "Recursive resolver\nISP · 8.8.8.8 · 1.1.1.1\nAWS: VPC base + 2\ndoes the walking, caches (TTL)",
          "green", size=11)
    d.box("root", 700, 50, 380, 76, "Root servers (13 names a–m, anycast)\n→ referral: ask the .com TLD servers", "gray", size=11)
    d.box("tld", 700, 182, 380, 76, "TLD .com (run by Verisign)\n→ referral: mixy.com's name servers (+ glue)", "blue", size=11)
    d.box("auth", 700, 314, 380, 76, "Authoritative (Route 53, ns1.google.com)\n→ FINAL answer: A, AAAA, CNAME, MX, TXT", "orange", size=11)
    d.edge("stub", "rec", "1", both=True)
    d.edge("rec", "root", "2", both=True)
    d.edge("rec", "tld", "3", both=True)
    d.edge("rec", "auth", "4", both=True)
    d.text("cap", 20, 300, 640, 120,
           "dig +trace google.com shows the walk\n\"Non-authoritative answer\" = from a resolver's cache\n"
           "(can be up to TTL seconds old)\naa flag = straight from the authoritative server\n"
           "Route 53 = authoritative for your hosted zone", size=11, align="left")
    return d


def private_ip_nat():
    d = Diagram("11-private-ip-nat", 1100, 400, "Q10–Q12 · How a laptop with a private IP talks to anything")
    d.box("lap", 20, 150, 220, 80, "Laptop\n192.168.1.20/24", "blue", size=12)
    d.box("dec", 300, 150, 210, 80, "Same subnet?\n(destination AND mask)", "yellow", size=11)
    d.box("loc", 580, 50, 260, 70, "Yes → ARP for its MAC\nsend frames directly", "green", size=11)
    d.box("rtr", 580, 240, 260, 80, "No → default gateway\n(router 192.168.1.1)\ndoes NAT / PAT", "purple", size=11)
    d.box("nat", 880, 230, 200, 100, "NAT table\n192.168.1.20:51515\n↔ 49.36.10.5:40001\nreplies reversed", "white", size=11)
    d.edge("lap", "dec")
    d.edge("dec", "loc", "yes")
    d.edge("dec", "rtr", "no")
    d.edge("rtr", "nat", dashed=True)
    d.text("cap", 20, 335, 1060, 56,
           "RFC 1918 private: 10.0.0.0/8 · 172.16.0.0/12 (to 172.31.255.255; 172.32.x.x is PUBLIC) · 192.168.0.0/16\n"
           "AWS: private subnet → NAT gateway; an instance's \"public IP\" is 1:1 NAT at the internet gateway", size=11)
    return d


def tcp_tls_http():
    d = Diagram("14-tcp-tls-http", 1000, 480, "Q13–Q16 · TCP, then TLS, then HTTP")
    d.box("c", 100, 45, 200, 40, "Client (browser)", "blue", size=12)
    d.box("sv", 600, 45, 200, 40, "Server :443", "green", size=12)
    d.box("cl", 196, 90, 8, 360, "", "gray")
    d.box("sl", 696, 90, 8, 360, "", "gray")
    msgs = [(110, "SYN  seq=x", True), (145, "SYN-ACK  seq=y, ack=x+1", False), (180, "ACK  ack=y+1", True),
            (230, "ClientHello (SNI = mixy.com)", True), (265, "ServerHello + certificate", False),
            (300, "Finished: session keys agreed", True), (350, "GET / HTTP/1.1  Host: mixy.com", True),
            (385, "HTTP/1.1 200 OK + body", False), (425, "FIN / ACK (first closer waits in TIME_WAIT)", True)]
    for i, (y, label, right) in enumerate(msgs):
        d.box(f"a{i}", 204, y - 6, 2, 12, "", "none")
        d.box(f"b{i}", 694, y - 6, 2, 12, "", "none")
        d.edge(f"a{i}", f"b{i}", label) if right else d.edge(f"b{i}", f"a{i}", label)
    for y, h, label, c in [(95, 110, "TCP\n1 round trip", "yellow"), (215, 100, "TLS 1.3\n1 round trip\n(1.2: 2)", "orange"),
                           (335, 70, "HTTP", "green")]:
        d.box(f"p{y}", 830, y, 150, h, label, c, size=11)
    d.text("cap", 20, 100, 160, 300,
           "Prove HTTP rides on TCP:\n\nnc example.com 80\nthen type GET by hand\n\ncurl -v: \"Connected\"\nbefore the headers\n\n"
           "tcpdump: SYN, SYN-ACK,\nACK, then HTTP data", size=10, align="left")
    return d


def recv_send_q():
    d = Diagram("24-recv-send-q", 1100, 370, "Q24 · Recv-Q and Send-Q: where the bytes are stuck")
    d.box("app", 20, 60, 200, 170, "Your app\nread() / write()", "blue", size=12)
    d.box("rq", 280, 60, 280, 70, "Recv-Q\nreceived by the kernel,\nnot read by the app yet", "yellow", size=11)
    d.box("sq", 280, 160, 280, 70, "Send-Q\nsent, not yet acknowledged\nby the remote side", "orange", size=11)
    d.box("net", 620, 60, 200, 170, "Network", "gray", size=12)
    d.box("peer", 880, 60, 200, 170, "Remote peer", "white", size=12)
    d.edge("net", "rq")
    d.edge("rq", "app")
    d.edge("app", "sq")
    d.edge("sq", "net")
    d.edge("peer", "net", both=True)
    d.box("d1", 20, 260, 340, 76, "Recv-Q growing\n→ the APP is slow or stuck reading\n(busy CPU, blocked, deadlock)", "red", size=11)
    d.box("d2", 380, 260, 340, 76, "Send-Q growing\n→ peer or network slow\nss -ti, netstat -s | grep retrans", "orange", size=11)
    d.box("d3", 740, 260, 340, 76, "Listening socket: Recv-Q ≈ Send-Q\n→ accept queue FULL, drops\nraise backlog / somaxconn", "yellow", size=11)
    return d


def path_debug():
    d = Diagram("26-path-debug", 1200, 340, "Q26 · /ABC works, /DEF doesn't: follow the path")
    d.text("top", 20, 42, 1160, 24,
           "/ABC works → DNS, TLS and reaching the load balancer are fine. Only one path fails → look at ROUTING.",
           size=12, bold=True)
    layers = [("CDN\nbehaviour or\ncache per path", "gray"), ("ALB listener\nrules: path →\ntarget group", "orange"),
              ("Ingress rules\npathType,\nrewrites", "purple"), ("Service\n→ endpoints", "blue"),
              ("Pods for\nthat backend", "blue"), ("App: does\nthe route\nexist?", "green"),
              ("Dependencies\nDB, downstream\nAPIs", "yellow")]
    for i, (label, c) in enumerate(layers):
        d.box(f"l{i}", 20 + i * 168, 85, 150, 90, label, c, size=11)
        if i:
            d.edge(f"l{i - 1}", f"l{i}")
    d.box("curl", 20, 205, 560, 70, "curl -v /DEF vs /ABC\ncompare status and headers (server, x-cache): WHICH layer answered?",
          "white", size=11)
    d.box("code", 620, 205, 560, 70, "404 from nginx = routing · 404 from the app = app\n502 / 503 / 504 = the LB says the backend is the problem",
          "white", size=11)
    d.text("cap", 20, 290, 1160, 40, "Also: ALB access logs, DEF target group health, ingress controller logs, app logs, recent deploys.", size=11)
    return d


def five_xx():
    d = Diagram("28-5xx-who", 1100, 380, "Q28–Q29 · Which 5xx came from where")
    d.box("cl", 20, 70, 160, 80, "Client", "white", size=12)
    d.box("lb", 230, 60, 260, 100, "Proxy / load balancer\nALB · ingress-nginx", "purple", size=12)
    d.box("app", 560, 70, 200, 80, "Upstream app", "blue", size=12)
    d.box("ae", 820, 60, 260, 100, "From the APP itself\n500 Internal Server Error\n501 Not Implemented", "gray", size=11)
    d.edge("cl", "lb")
    d.edge("lb", "app")
    d.edge("app", "ae", dashed=True)
    d.group("gen", 10, 190, 1080, 125, "Generated by the proxy / LB, not by the app", "gray", size=12)
    d.box("e2", 25, 222, 340, 80, "502 Bad Gateway\nbad or no response: app crashed, wrong port\nor protocol, app keep-alive < ALB idle timeout",
          "red", size=11)
    d.box("e3", 380, 222, 340, 80, "503 Service Unavailable\nno healthy targets / no ready endpoints,\noverloaded, maintenance", "orange", size=11)
    d.box("e4", 735, 222, 340, 80, "504 Gateway Timeout\nupstream too slow\n(app, database, or timeout too low)", "yellow", size=11)
    d.edge("lb", "gen")
    d.text("cap", 20, 325, 1060, 44,
           "Who answered? Server: awselb/2.0 = the ALB · an nginx page = ingress · JSON = the app.  "
           "CloudWatch: HTTPCode_ELB_5XX_Count vs HTTPCode_Target_5XX_Count", size=11)
    return d


def build_once():
    d = Diagram("38-build-once-promote", 1200, 390, "Q35–Q39 · Build once, promote the same image everywhere")
    d.box("cm", 20, 70, 170, 70, "Merge to main\ncommit 4f2a9c1", "white", size=11)
    d.box("bd", 240, 60, 250, 90, "CI builds ONCE\ntag = commit SHA 4f2a9c1\nrecord the digest", "purple", size=11)
    d.box("rg", 540, 65, 180, 80, "Registry (ECR)", "gray", shape="cylinder", size=11)
    d.box("ar", 780, 60, 400, 90, "Argo CD in each cluster pulls its folder\nwhat runs = what Git says\n(no CI access to clusters)",
          "green", size=11)
    d.edge("cm", "bd")
    d.edge("bd", "rg")
    d.group("gx", 20, 185, 1160, 125, "GitOps repo: one folder per environment · promotion = a PR that changes the tag", "blue", size=12)
    for i, env in enumerate(["dev", "qa", "prod"]):
        d.box(f"e{i}", 60 + i * 390, 225, 300, 66, f"{env}/values.yaml\nimage.tag: 4f2a9c1", "white", size=11)
    d.edge("e0", "e1", "tests pass\n→ PR")
    d.edge("e1", "e2", "approval\n→ PR")
    d.text("cap", 20, 322, 1160, 56,
           "Environments differ ONLY by runtime config and secrets (Helm values, ConfigMaps, Secrets Manager).\n"
           "What you tested is byte-for-byte what reaches prod. No branch per environment: branches drift (Q39).", size=11)
    return d


def db_scaling():
    d = Diagram("41-db-scaling-ladder", 1100, 420, "Q41 · The database won't scale: cheapest fix first")
    d.box("m", 20, 55, 1060, 50, "Measure first: CPU, IOPS, connections, locks or specific queries?  (Performance Insights, pg_stat_statements)",
          "blue", size=11)
    steps = [("1 · Optimise queries + indexes (Q44)", "green"), ("2 · Connection pooling\nPgBouncer / RDS Proxy", "green"),
             ("3 · Cache hot reads\nRedis (ElastiCache)", "green"), ("4 · Scale up\nbigger instance, gp3 / io2 IOPS", "yellow"),
             ("5 · Read replicas\napp sends reads there", "yellow"), ("6 · Partition big tables\n+ archive old data", "yellow"),
             ("7 · Analytics off the primary\nqueues for write spikes", "orange"),
             ("8 · Aurora\nauto storage, 15 replicas, fast failover", "orange"), ("9 · Sharding (Citus)\nlast resort: complexity", "red")]
    for i, (label, c) in enumerate(steps):
        row, col = divmod(i, 3)
        d.box(f"s{i}", 20 + col * 360, 130 + row * 80, 340, 64, label, c, size=11)
    d.text("cap", 20, 370, 1060, 40, "Reads → replicas and caching · Writes → partitioning, queues or sharding", size=12, bold=True)
    return d


def pg_to_rds():
    d = Diagram("42-pg-to-rds", 1200, 420, "Q42–Q43 · Postgres on EC2 → RDS with near-zero downtime")
    d.box("app", 20, 70, 160, 70, "App", "white", size=12)
    d.box("ec2", 260, 55, 300, 100, "Postgres on EC2 (source)\nwal_level = logical (restart)\nCREATE PUBLICATION", "blue",
          shape="cylinder", size=11)
    d.box("rds", 880, 55, 300, 100, "Amazon RDS (target)\nschema: pg_dump --schema-only\nCREATE SUBSCRIPTION", "green",
          shape="cylinder", size=11)
    d.edge("app", "ec2", "today")
    d.edge("ec2", "rds", "initial copy, then\nstream every change")
    d.group("cut", 20, 190, 1160, 130, "Cutover (rehearse it in staging first)", "gray", size=12)
    for i, (label, c) in enumerate([("Days before:\nlower DNS TTL", "white"), ("Validate: counts,\nchecksums, lag ≈ 0", "white"),
                                    ("PAUSE writes\n(a few seconds)", "red"), ("Lag = 0,\nsync sequences", "yellow"),
                                    ("Switch endpoint\nDNS / config /\nRDS Proxy", "orange"), ("Resume; keep EC2 +\nreverse replication\nfor rollback", "green")]):
        d.box(f"c{i}", 35 + i * 190, 228, 175, 76, label, c, size=11)
        if i:
            d.edge(f"c{i - 1}", f"c{i}")
    d.text("cap", 20, 332, 1160, 76,
           "Limits: sequences and schema changes aren't replicated; UPDATE/DELETE need a primary key. Or AWS DMS (full load + CDC).\n"
           "Why not dual writes? No transaction spans two databases → silent divergence, and app changes.\n"
           "RDS can't be a physical replica of an external primary, so it's logical replication.", size=11)
    return d


def loki():
    d = Diagram("49-loki", 1100, 390, "Q49 · How Loki works: index the labels, not the text")
    d.box("ag", 20, 60, 200, 80, "Agents\nAlloy · Fluent Bit\nOTel Collector", "white", size=11)
    d.box("di", 270, 60, 180, 80, "Distributor\nreceives, validates", "purple", size=11)
    d.box("in", 500, 60, 200, 80, "Ingester\nbuilds chunks in memory,\nflushes them", "blue", size=11)
    d.box("s3", 760, 50, 320, 100, "S3: compressed chunks\n+ an index of LABELS only", "orange", shape="cylinder", size=11)
    d.box("gf", 20, 200, 200, 80, "Grafana\nLogQL", "green", size=11)
    d.box("qr", 270, 200, 430, 80, "Query-frontend → querier\npick chunks by labels, then grep the text", "yellow", size=11)
    d.box("cp", 760, 200, 320, 80, "Compactor\nenforces retention", "gray", size=11)
    d.edge("ag", "di")
    d.edge("di", "in")
    d.edge("in", "s3")
    d.edge("gf", "qr")
    d.edge("qr", "s3")
    d.edge("cp", "s3")
    d.text("cap", 20, 300, 1060, 76,
           "Labels: low cardinality (app, namespace, pod, level). request_id as a label = millions of tiny streams.\n"
           "LogQL: {app=\"api\"} |= \"error\" | json | status >= 500  ·  rate({app=\"api\"} |= \"error\" [5m])\n"
           "Loki: high volume, multi-cloud / on-prem, one Grafana.  CloudWatch: small, zero-ops, AWS-managed sources.", size=11)
    return d


def shift_left():
    d = Diagram("55-shift-left", 1200, 380, "Q55 · Shift-left: catch it where it's cheapest to fix")
    stages = [("Developer machine\npre-commit hooks\ngitleaks, linters\nIDE security plugins", "green"),
              ("Pull request\nunit tests · SAST (Semgrep,\nCodeQL) · SCA (Dependabot,\ntrivy fs) · IaC (Checkov,\ntfsec) · hadolint · OPA", "green"),
              ("Build\nimage scan (Trivy, Grype)\nSBOM (Syft)\nsign (cosign)", "yellow"),
              ("Deploy\nadmission (Kyverno,\nGatekeeper): signed only,\nno root, no latest\nDAST (ZAP) on staging", "orange"),
              ("Runtime: \"shield right\"\nFalco · GuardDuty\nmonitoring\n(shift-left doesn't\nreplace this)", "red")]
    for i, (label, c) in enumerate(stages):
        d.box(f"s{i}", 20 + i * 235, 75, 220, 150, label, c, size=11)
        if i:
            d.edge(f"s{i - 1}", f"s{i}")
    d.text("arrow", 20, 45, 1160, 24, "← cheap to fix                                                             expensive to fix →",
           size=11, bold=True)
    d.box("ppl", 20, 255, 1160, 70, "Make it work for people\nfail on HIGH/CRITICAL with an exception process · keep scans fast · "
          "baseline existing issues so developers own only NEW ones · heavy scans nightly", "white", size=11)
    return d


def secret_leak():
    d = Diagram("57-secret-leak", 1200, 470, "Q57 · Secrets: how they leak, how to stop it, what to do now")
    d.group("lk", 20, 45, 370, 370, "How secrets leak", "red", size=12)
    for i, t in enumerate(["Git: history, forks; bots scan in minutes", "Image layers (ENV, .env), docker inspect",
                           "CI logs (echo, set -x)", "Env vars in /proc/<pid>/environ; args in ps",
                           "Shell history; world-readable keys (644)", "Backups, snapshots, AMIs, core dumps",
                           "Slack, tickets, wikis, error pages", "SSRF → IMDSv1 → instance role creds"]):
        d.box(f"l{i}", 35, 80 + i * 41, 340, 35, t, "white", size=11)
    d.group("pv", 410, 45, 380, 370, "Prevent a repeat", "green", size=12)
    for i, t in enumerate(["No long-lived secrets\nIAM roles, OIDC, IRSA / Pod Identity,\nIMDSv2, SSM instead of SSH keys",
                           "Store and rotate\nSecrets Manager, SSM Parameter Store,\nVault; fetch at runtime",
                           "Detect\ngitleaks / trufflehog pre-commit,\nGitHub push protection, image scans",
                           "Harden the OS\nchmod 600, secrets as tmpfs files,\nno core dumps, auditd, CIS"]):
        d.box(f"p{i}", 425, 80 + i * 82, 350, 74, t, "white", size=11)
    d.group("rs", 810, 45, 370, 370, "A key leaked: first 10 minutes", "orange", size=12)
    for i, (t, c) in enumerate([("1 · Revoke / rotate NOW\nassume it's compromised", "red"),
                                ("2 · CloudTrail and access logs:\nwas it used?", "orange"),
                                ("3 · Clean history (git filter-repo)\nrotation is what protects you", "yellow"),
                                ("4 · Blameless postmortem + guardrails\npush protection, hooks, SCPs", "green")]):
        d.box(f"r{i}", 825, 80 + i * 82, 340, 74, t, c, size=11)
    d.text("cap", 20, 425, 1160, 30, "\"It was in Git for 2 days and I deleted the commit. Safe?\" → NO. Rotate it and check CloudTrail.",
           size=12, bold=True)
    return d


ALL = [observability_stack, url_to_page, dns_hierarchy, private_ip_nat, tcp_tls_http, recv_send_q, path_debug, five_xx,
       build_once, db_scaling, pg_to_rds, loki, shift_left, secret_leak]

if __name__ == "__main__":
    force = "--force" in sys.argv
    warnings = []
    for build in ALL:
        diagram = build()
        warnings += diagram.warnings
        path = diagram.save(OUT, force=force)
        print(f"{'wrote  ' if path else 'skipped'} {diagram.name}.drawio.svg"
              f"{'' if path else '  (exists; use --force to overwrite)'}")
    for w in warnings:
        print("WARN", w)
