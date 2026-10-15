#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/interview-review-oct-9.md.

Corrected versions of the diagrams drawn in the 9 Oct 2026 interview.
Run once:  python3 tools/diagrams_review.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "diagrams"

AZS = [  # (AZ name, public, app, data, app usable range)
    ("AZ a · ap-south-1a", "10.0.0.0/24", "10.0.16.0/20", "10.0.8.0/24"),
    ("AZ b · ap-south-1b", "10.0.1.0/24", "10.0.32.0/20", "10.0.9.0/24"),
    ("AZ c · ap-south-1c", "10.0.2.0/24", "10.0.48.0/20", "10.0.10.0/24"),
]


def vpc_subnets():
    d = Diagram("r1-vpc-subnets-nat-igw", 1220, 1230,
                "Corrected: account → region → VPC → 3 AZs × 3 subnet tiers, with the NAT gateway INSIDE a public subnet")
    d.box("inet", 505, 40, 210, 50, "Internet", "gray", shape="ellipse", size=12)
    d.group("acct", 20, 110, 1180, 905, "AWS account: dev-staging", "white", size=13, align="left")
    d.group("region", 40, 150, 1140, 850, "Region: ap-south-1 (Mumbai)", "gray", size=12, align="left")
    d.group("vpc", 60, 235, 1100, 750, "VPC (Virtual Private Cloud) 10.0.0.0/16 · 65,536 IPs", "blue", size=12, align="left")
    d.box("igw", 510, 205, 200, 60, "Internet gateway\none per VPC, at its edge", "purple", size=11)
    d.edge("inet", "igw", both=True)
    for i, (az, pub, app, data) in enumerate(AZS):
        x = 80 + i * 365
        d.group(f"az{i}", x, 300, 340, 670, az, "white", dashed=True, size=12)
        d.group(f"pub{i}", x + 15, 345, 310, 170, f"PUBLIC subnet {pub}\nusable .4 – .254 = 251 IPs", "green", size=11)
        d.box(f"nat{i}", x + 30, 410, 135, 80, "NAT gateway\n+ Elastic IP", "orange", size=11)
        d.box(f"alb{i}", x + 180, 410, 130, 80, "ALB node\n(load balancer)", "orange", size=11)
        d.group(f"app{i}", x + 15, 535, 310, 230, f"PRIVATE app subnet {app}\n4,091 usable IPs · EKS nodes + pods", "yellow", size=11)
        d.box(f"pods{i}", x + 30, 620, 280, 120, "EKS nodes and pods\n(every pod uses a VPC IP,\nso this subnet is big)", "white", size=11)
        d.group(f"data{i}", x + 15, 785, 310, 170, f"PRIVATE data subnet {data}\nusable .4 – .254 · no internet route", "red", size=11)
        d.box(f"db{i}", x + 30, 850, 280, 80, "Amazon RDS (Relational\nDatabase Service) instance", "white", size=11)
        d.edge(f"pods{i}", f"nat{i}")
        d.edge(f"nat{i}", "igw")
        d.edge(f"pods{i}", f"db{i}")
    d.box("rt", 20, 1035, 1180, 125,
          "Route tables: what makes a subnet public or private\n"
          "PUBLIC:            10.0.0.0/16 → local · 0.0.0.0/0 → Internet gateway\n"
          "PRIVATE app (one per AZ):   10.0.0.0/16 → local · 0.0.0.0/0 → the NAT gateway in the SAME AZ\n"
          "PRIVATE data:        10.0.0.0/16 → local only (a database needs no internet)",
          "white", size=12, align="left")
    d.text("cap", 20, 1170, 1180, 50,
           "Subnets never overlap: each one has its own range and lives in exactly one AZ (Availability Zone). "
           "Free space is left for growth (10.0.64.0 – 10.0.255.255).\n"
           "In real life take a unique VPC range from IPAM (IP Address Manager), never the default 10.0.0.0/16 everyone uses.",
           size=11, italic=True)
    return d


def cidr_explained():
    d = Diagram("r2-cidr-explained", 1200, 760, "CIDR (Classless Inter-Domain Routing): what 10.0.1.0/24 really means")
    octets = [("10", "00001010"), ("0", "00000000"), ("1", "00000001"), ("0", "00000000")]
    for i, (dec, binary) in enumerate(octets):
        colour = "blue" if i < 3 else "green"
        d.box(f"o{i}", 40 + i * 285, 60, 260, 80, f"{dec}\n{binary}", colour, size=14)
    d.box("net", 40, 160, 830, 60, "Network part: the first 24 bits are FIXED (that's what /24 means)\n→ every address in this subnet starts with 10.0.1.", "blue", size=12)
    d.box("host", 895, 160, 260, 60, "Host part: 8 free bits\n2⁸ = 256 addresses", "green", size=12)
    d.text("range-h", 40, 245, 1120, 24, "10.0.1.0/24 = 10.0.1.0 to 10.0.1.255 (256 addresses). AWS keeps 5 of them:", size=13, bold=True, align="left")
    reserved = [(".0", "network address"), (".1", "VPC router"), (".2", "Amazon DNS"), (".3", "reserved for later"), (".255", "broadcast")]
    for i, (ip, what) in enumerate(reserved):
        d.box(f"r{i}", 40 + i * 226, 280, 210, 60, f"10.0.1{ip}\n{what}", "red", size=11)
    d.box("usable", 40, 360, 1120, 50, "Usable for your servers and pods: 10.0.1.4 to 10.0.1.254 = 251 addresses", "green", size=13)
    d.text("sizes-h", 40, 430, 540, 24, "Sizes (each /1 smaller doubles the addresses)", size=13, bold=True, align="left")
    sizes = [("/16", "65,536", "a whole VPC"), ("/20", "4,096", "an EKS app subnet"), ("/24", "256", "a public or data subnet"),
             ("/28", "16", "the smallest AWS subnet")]
    for i, (p, n, use) in enumerate(sizes):
        d.box(f"s{i}", 40, 465 + i * 62, 540, 52, f"{p} = {n} addresses\n{use}", "white", size=11)
    d.box("wrong", 620, 430, 540, 300,
          "What was wrong in the drawing\n"
          "1 · 10.0.1.0/24 and 10.0.2.0/24 were used in AZ a AND AZ c.\n"
          "     Subnets in one VPC can never overlap.\n"
          "2 · Subnet 10.0.3.0/24 was labelled 10.0.1.1 – 10.0.1.255\n"
          "     (copied from another subnet).\n"
          "3 · The usable range was written as .1 – .255.\n"
          "     On AWS it is .4 – .254 (.255 is broadcast).\n"
          "4 · 10.0.256.256 can't exist: each part is 8 bits, 0 – 255.\n"
          "5 · /24 is too small for EKS pods: every pod takes a VPC IP.\n"
          "     Use /20 or bigger for app subnets.",
          "orange", size=11, align="left")
    return d


def three_tier():
    d = Diagram("r3-three-tier-on-eks", 1300, 800, "Corrected three-tier architecture on EKS: each tier in its own subnets")
    d.box("user", 20, 330, 160, 80, "User's browser\n(runs the React app)", "gray", shape="ellipse", size=11)
    d.box("r53", 210, 110, 230, 80, "Route 53 (DNS)\nshop.example.com → ALB\n(alias record)", "purple", size=11)
    d.group("pub", 480, 60, 240, 560, "PUBLIC tier\npublic subnets, 2–3 AZs", "green", size=12)
    d.box("alb", 500, 300, 200, 150,
          "ALB (Application Load\nBalancer), made by an\nIngress + the AWS Load\nBalancer Controller\nHTTPS 443 · ACM cert", "orange", size=11)
    d.group("app", 760, 60, 300, 560, "APP tier\nprivate app subnets (EKS)", "yellow", size=12)
    d.box("fe", 780, 150, 260, 110, "frontend pods\nnginx serving the built React files\nService: ClusterIP\nHPA (autoscaling)", "white", size=11)
    d.box("be", 780, 380, 260, 110, "backend (API) pods\nService: ClusterIP\nHPA (autoscaling)", "white", size=11)
    d.group("data", 1100, 60, 180, 560, "DATA tier\nprivate data subnets", "red", size=12)
    d.box("rds", 1115, 375, 150, 120, "Amazon RDS\nPostgreSQL\nMulti-AZ\nport 5432", "white", shape="cylinder", size=11)
    d.edge("user", "r53", "1 · DNS lookup")
    d.edge("user", "alb", "2 · HTTPS")
    d.edge("alb", "fe", "path /")
    d.edge("alb", "be", "path /api")
    d.edge("be", "rds", "5432")
    d.box("n1", 20, 645, 620, 135,
          "Security groups form a chain\nInternet → ALB SG: 443 only\nALB SG → app SG: only from the ALB's security group\n"
          "app SG → DB SG: 5432 only from the backend\nInside the cluster, NetworkPolicy does the same between pods.",
          "yellow", size=11, align="left")
    d.box("n2", 660, 645, 620, 135,
          "What changed from the drawing\nNo NodePort: the Ingress sends ALB traffic straight to pod IPs (target-type ip).\n"
          "The React code runs in the BROWSER, so the browser calls /api through the ALB.\n"
          "DNS points TO the ALB (the arrow went the other way).\n"
          "Database: managed RDS, not a StatefulSet you must back up yourself.",
          "gray", size=11, align="left")
    return d


def central_monitoring():
    d = Diagram("r4-central-monitoring-signoz", 1400, 860,
                "Corrected: central monitoring with SigNoz for many AWS accounts")
    accounts = [("A · dev", 60), ("B · staging", 300), ("C · prod", 540)]
    for i, (name, y) in enumerate(accounts):
        d.group(f"acc{i}", 20, y, 540, 210, f"Workload account {name} · EKS cluster", "blue", size=12, align="left")
        d.box(f"apps{i}", 35, y + 60, 140, 110, "Apps\nOTel SDK\n(OpenTelemetry)\nsend OTLP", "white", size=11)
        d.box(f"col{i}", 190, y + 45, 180, 140,
              "OTel Collector\nDaemonSet: logs, node\nand pod metrics\nGateway: batch, add\nlabels, retry", "green", size=11)
        d.box(f"ep{i}", 385, y + 70, 160, 90, "Interface endpoint\n(PrivateLink)", "orange", size=11)
        d.edge(f"apps{i}", f"col{i}")
        d.edge(f"col{i}", f"ep{i}")
    d.group("mon", 620, 60, 760, 690, "Central monitoring account · SigNoz", "purple", size=13, align="left")
    d.box("nlb", 645, 345, 150, 110, "Internal NLB\n= endpoint\nservice\nOTLP 4317 / 4318", "orange", size=11)
    d.box("ingest", 825, 330, 170, 140, "SigNoz OTel\nCollectors\n(several replicas)\nreceive + process", "green", size=11)
    d.box("ch", 1020, 320, 160, 160, "ClickHouse\nstores metrics,\nlogs and traces\n(TTL, S3 for\nold data)", "white", shape="cylinder", size=11)
    d.box("sig", 1205, 330, 160, 140, "SigNoz\nquery service\n+ UI\n+ alert rules", "purple", size=11)
    d.box("eng", 1205, 120, 160, 80, "Engineers\ndashboards", "gray", size=11)
    d.box("alert", 1205, 600, 160, 80, "Alerts →\nSlack, PagerDuty", "red", size=11)
    for i in range(3):
        d.edge(f"ep{i}", "nlb")
    d.edge("nlb", "ingest")
    d.edge("ingest", "ch")
    d.edge("ch", "sig")
    d.edge("eng", "sig")
    d.edge("sig", "alert")
    d.box("rules", 20, 775, 1360, 75,
          "Every cluster's collector adds labels: k8s.cluster.name, deployment.environment, cloud.account.id → one SigNoz, filter by source.\n"
          "Only collectors cross accounts, in one direction, through PrivateLink (overlapping CIDRs don't matter). Apps never send across accounts.\n"
          "Simpler option: SigNoz Cloud. Each collector exports straight to SigNoz's endpoint with an ingestion key, and there's nothing central to run.",
          "yellow", size=11, align="left")
    return d


def traffic_flows():
    d = Diagram("r5-traffic-flows-route-tables", 1260, 900,
                "Traffic flow: which route table each packet uses (one AZ shown; the others are the same)")
    d.box("inet", 470, 40, 220, 50, "Internet (users, apt repos, APIs)", "gray", shape="ellipse", size=11)
    d.group("vpc", 40, 160, 1180, 560, "VPC 10.0.0.0/16", "blue", size=12, align="left")
    d.box("igw", 480, 132, 200, 56, "Internet gateway\n(attached to the VPC)", "purple", size=11)
    d.group("pub", 70, 220, 600, 150, "PUBLIC subnet 10.0.0.0/24", "green", size=11, align="left")
    d.box("nat", 100, 270, 200, 70, "NAT gateway\n+ Elastic IP", "orange", size=11)
    d.box("alb", 440, 270, 200, 70, "ALB\n(load balancer)", "orange", size=11)
    d.box("rt-pub", 700, 225, 490, 110, "Public route table\n10.0.0.0/16 → local\n0.0.0.0/0 → internet gateway",
          "white", size=12, align="left")
    d.group("app", 70, 400, 600, 150, "PRIVATE app subnet 10.0.16.0/20", "yellow", size=11, align="left")
    d.box("pod", 440, 450, 200, 70, "Pod 10.0.16.25", "white", size=11)
    d.box("rt-app", 700, 405, 490, 110, "Private app route table\n10.0.0.0/16 → local\n0.0.0.0/0 → NAT gateway (same AZ)",
          "white", size=12, align="left")
    d.group("data", 70, 575, 600, 125, "PRIVATE data subnet 10.0.8.0/24", "red", size=11, align="left")
    d.box("rds", 440, 620, 200, 60, "RDS database", "white", size=11)
    d.box("rt-data", 700, 585, 490, 100, "Data route table\n10.0.0.0/16 → local\n(no 0.0.0.0/0: no internet at all)",
          "white", size=12, align="left")
    d.edge("inet", "igw", "①")
    d.edge("igw", "alb", "①")
    d.edge("alb", "pod", "① local")
    d.edge("pod", "rds", "local")
    d.edge("pod", "nat", "② 0.0.0.0/0")
    d.edge("nat", "igw", "②")
    d.box("f1", 40, 740, 590, 145,
          "① A user opens the site\nInternet → internet gateway → ALB (in the public subnet)\n"
          "→ pod: 10.0.16.25 matches 10.0.0.0/16 → local, so it stays inside the VPC\n"
          "The reply returns the same way. The pod is never reachable directly.",
          "green", size=11, align="left")
    d.box("f2", 650, 740, 570, 145,
          "② A pod downloads a package\nPod → app route table: 0.0.0.0/0 → NAT gateway\n"
          "NAT (public subnet) swaps the source IP for its Elastic IP\n→ public route table: 0.0.0.0/0 → internet gateway → internet\n"
          "Replies come back through the NAT. Nobody outside can start a connection in.",
          "yellow", size=11, align="left")
    return d


def account_per_env():
    d = Diagram("r6-account-per-environment", 1100, 430, "One AWS account per environment, under AWS Organizations")
    d.box("mgmt", 380, 55, 340, 70, "Management account\nAWS Organizations · SCPs · Control Tower", "purple", size=12)
    d.group("sec", 20, 170, 360, 170, "Security OU", "gray", size=12)
    d.box("log", 40, 205, 320, 64, "Log archive account\norganization CloudTrail from EVERY account\nnobody in a workload account can delete it",
          "orange", size=11)
    d.box("audit", 40, 282, 320, 44, "Audit / security tooling account", "white", size=11)
    d.group("wl", 420, 170, 660, 170, "Workloads OU (SCP guardrails per environment)", "blue", size=12)
    for i, env in enumerate(["dev", "staging", "prod"]):
        d.box(f"e{i}", 440 + i * 210, 210, 200, 110, f"{env}\nown VPCs and quotas\nown IAM\nown bill", "white", size=11)
    d.edge("mgmt", "sec")
    d.edge("mgmt", "wl")
    d.text("cap", 20, 355, 1060, 60,
           "Why: blast radius (the account is AWS's strongest wall) · quotas are per account and region (e.g. 5 VPCs)\n"
           "· simple IAM plus SCPs per environment · audit logs safe in log-archive · the bill splits per account", size=11)
    return d


def db_access():
    d = Diagram("r7-private-db-access", 1100, 400, "How a developer reaches a private database (best first)")
    d.box("lap", 20, 60, 180, 64, "Developer laptop\n(IAM identity)", "white", size=11)
    d.box("ssm", 260, 60, 220, 64, "SSM Session Manager\nAWS API over HTTPS", "green", size=11)
    d.box("inst", 540, 55, 220, 74, "Instance in a private\napp subnet (SSM agent)\nno inbound ports", "blue", size=11)
    d.box("db", 820, 50, 260, 84, "RDS in a private\ndata subnet :5432", "orange", shape="cylinder", size=11)
    d.edge("lap", "ssm")
    d.edge("ssm", "inst")
    d.edge("inst", "db")
    opts = [("1 · SSM port forwarding ✅\nno SSH port, no public IP\nIAM decides who, every\nsession logged", "green"),
            ("2 · AWS Client VPN\n= point-to-site\na laptop joins the\nVPC network", "blue"),
            ("3 · Site-to-Site VPN\n= network-to-network\noffice network ↔ VPC", "yellow"),
            ("4 · Bastion host (older)\npublic subnet,\nSSH only from office IP", "gray")]
    for i, (label, c) in enumerate(opts):
        d.box(f"o{i}", 20 + i * 268, 175, 252, 110, label, c, size=11)
    d.text("cap", 20, 305, 1060, 70,
           "SSM document: AWS-StartPortForwardingSessionToRemoteHost (forwards localhost:5432 to the RDS endpoint).\n"
           "Also: read-only DB users for developers, and no direct production access.", size=11)
    return d


def subnet_block_size():
    d = Diagram("r8-subnet-block-size", 1100, 390, "Subnetting on paper: which /20 contains 10.0.37.5?")
    steps = [("1 · /20 = 20 fixed bits\n8 + 8 + 4\n→ boundary in octet 3", "blue"),
             ("2 · Host bits in octet 3\n8 − 4 = 4\n→ block = 2⁴ = 16", "purple"),
             ("3 · Subnets start at\n0, 16, 32, 48 …\nin octet 3", "yellow"),
             ("4 · 37 ÷ 16 = 2 r 5\n2 × 16 = 32\n→ 10.0.32.0/20", "orange"),
             ("5 · Range\n10.0.32.0 – 10.0.47.255\n4,096 (4,091 on AWS)", "green")]
    for i, (label, c) in enumerate(steps):
        d.box(f"s{i}", 20 + i * 215, 60, 200, 90, label, c, size=11)
        if i:
            d.edge(f"s{i - 1}", f"s{i}")
    d.text("bh", 20, 180, 640, 24, "Bit values in one octet (add up the 1s)", size=13, bold=True, align="left")
    for i, v in enumerate([128, 64, 32, 16, 8, 4, 2, 1]):
        d.box(f"b{i}", 20 + i * 80, 212, 70, 44, str(v), "white", size=12)
    d.box("ex", 680, 180, 400, 90, "10 = 00001010 = 8 + 2\n172 = 10101100 = 128 + 32 + 8 + 4\n255 = 11111111 (the maximum)",
          "gray", size=11, bold_first=False)
    d.text("cap", 20, 295, 1060, 70,
           "Addresses = 2^(32 − N).  /24 → block 1 in octet 3: 10.0.1.0, 10.0.2.0 …  /26 → block 64 in octet 4: .0 .64 .128 .192\n"
           "1 byte = 8 bits · IPv4 = 4 bytes = 32 bits · IPv6 = 128 bits", size=11)
    return d


ALL = [vpc_subnets, cidr_explained, three_tier, central_monitoring, traffic_flows, account_per_env, db_access,
       subnet_block_size]

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
