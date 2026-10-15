# Interview Review · 9 Oct 2026 (Hemant, One2N)

Corrections to the diagrams drawn in the interview, from Hemant's feedback: **the corrected diagram first**, then what was wrong and what to say. The question-by-question review, subnetting worksheet and 4-week plan are in [interview-transcript-review-oct-9.md](interview-transcript-review-oct-9.md).

| # | Topic | Hemant's feedback |
|---|---|---|
| 1 | [VPC and subnets](#1--vpc-and-subnets-how-to-choose-them) | How to choose the VPC, and why that many subnets |
| 2 | [CIDR and IP addresses](#2--cidr-and-ip-addresses-what-was-wrong) | "The subnet CIDR / IP concept is wrong" |
| 3 | [NAT gateway and internet gateway](#3--nat-gateway-and-internet-gateway-where-they-fit) | "Where NAT and IG sit is wrong" |
| 4 | [Three-tier architecture](#4--three-tier-architecture-on-eks) | Tiers, services, DNS direction |
| 5 | [Central monitoring with SigNoz](#5--central-monitoring-with-signoz) | Metrics from many accounts into one place |
| 6 | [Dockerfile](#6--the-dockerfile-on-the-same-drawing) | The React Dockerfile notes |

---

## 1 · VPC and subnets: how to choose them

![Corrected VPC with 3 AZs and 3 subnet tiers](diagrams/r1-vpc-subnets-nat-igw.drawio.svg)

- **Drawn right:** the nesting account → region → VPC → AZ → subnet.
- **Choosing the VPC range:** private (RFC 1918: `10/8`, `172.16/12`, `192.168/16`) · a **`/16`** for EKS (every pod takes a VPC IP) · **unique** from an IPAM plan (dev-staging `10.20.0.0/16`, prod `10.30.0.0/16`). Avoid `10.0.0.0/16` (everyone uses it → overlap, scenario A2) and `172.17.0.0/16` (Docker's bridge). Leave room for a secondary range like `100.64.0.0/16` (scenario A3).
- **3 AZs:** survive one AZ failing; ALB and EKS need ≥2; RDS Multi-AZ standby; a majority if one is lost.

| Tier | What lives there | Size | Internet? |
|---|---|---|---|
| **Public** | ALB, NAT gateway | `/24` | Yes, via the internet gateway |
| **Private app** | EKS nodes and pods | **`/20`** (4,091 usable) | Outbound only, via NAT |
| **Private data** | RDS | `/24` | **No** |

| AZ | Public | Private app | Private data |
|---|---|---|---|
| a | `10.0.0.0/24` | `10.0.16.0/20` | `10.0.8.0/24` |
| b | `10.0.1.0/24` | `10.0.32.0/20` | `10.0.9.0/24` |
| c | `10.0.2.0/24` | `10.0.48.0/20` | `10.0.10.0/24` |

- `10.0.64.0`–`10.0.255.255` stays free. EKS tags: public `kubernetes.io/role/elb=1`, private `kubernetes.io/role/internal-elb=1`.

> **Say it:** "A unique /16 from our IPAM plan, never 10.0.0.0/16. 3 AZs for availability, 3 tiers per AZ: public only for the ALB and NAT gateways, big /20 private app subnets for EKS because every pod uses a VPC IP, and data subnets with no internet route. Each tier has its own route table and security groups."

---

## 2 · CIDR and IP addresses: what was wrong

![CIDR explained](diagrams/r2-cidr-explained.drawio.svg)

| Drawn | Problem | Correct |
|---|---|---|
| `10.0.1.0/24`, `10.0.2.0/24` in AZ a **and** AZ c | Subnets **never overlap**; one subnet = one AZ | Own range each (section 1) |
| `10.0.3.0/24` labelled `10.0.1.1 – 10.0.1.255` | Copied from another subnet | `10.0.3.0 – 10.0.3.255` |
| Usable `.1 – .255` | AWS reserves `.0` network, `.1` router, `.2` DNS, `.3` future, `.255` broadcast | **`.4 – .254` = 251** |
| `10.0.256.256` | Each octet is 8 bits: **0–255** | Highest `10.0.255.255` |
| `0000 0011.0000…` | `10` = `00001010` | `00001010.00000000.00000001.00000000` |
| `/24` subnets for EKS | Pods eat VPC IPs | `/20`+ for app subnets |

> **Say it:** "A /24 fixes the first 24 bits, leaving 8 host bits: 256 addresses. AWS reserves 5 in every subnet, so 251 are usable, .4 to .254. Subnets in a VPC never overlap, and each lives in one AZ."

---

## 3 · NAT gateway and internet gateway: where they fit

![Traffic flow and route tables](diagrams/r5-traffic-flows-route-tables.drawio.svg)

| | Drawn | Correct |
|---|---|---|
| **Internet gateway** | A box among the subnets | **One per VPC, at its edge**, in no AZ or subnet. A subnet is public because its **route table** says `0.0.0.0/0 → igw-…` |
| **NAT gateway** | Outside every AZ and subnet | **Inside a public subnet**, one AZ, with an **Elastic IP**. **One per AZ** (survives an AZ failure, no cross-AZ charges) |
| **Private subnets** | Arrows from NAT | Route table `0.0.0.0/0 → nat-…` **in the same AZ** |
| **Data subnets** | Like app subnets | **No internet route** |

| Route table | Routes |
|---|---|
| Public | `10.0.0.0/16 → local` · `0.0.0.0/0 → igw-…` |
| Private app (one per AZ) | `10.0.0.0/16 → local` · `0.0.0.0/0 → nat-…` (same AZ) |
| Private data | `10.0.0.0/16 → local` only |

- **Drawn right:** private → NAT → IG. NAT is **outbound only**: the internet can't start a connection in.
- Cost: one NAT for all AZs is fine in dev (but an AZ failure cuts everyone's internet); one per AZ in prod.

> **Say it:** "The internet gateway is one per VPC at its edge; a subnet is public because its route table points 0.0.0.0/0 at it. The NAT gateway sits inside a public subnet with an Elastic IP, one per AZ; each private route table points at the NAT in its own AZ. Data subnets get no internet route."

---

## 4 · Three-tier architecture on EKS

![Corrected three-tier architecture on EKS](diagrams/r3-three-tier-on-eks.drawio.svg)

| Drawn | Fix |
|---|---|
| Tiers not tied to the network | ALB in **public**, app pods in **private app**, DB in **private data** subnets; each reachable only from the one before |
| ALB → Route 53 | Wrong way: Route 53 holds an **alias** `shop.example.com → ALB`; the browser asks Route 53, then connects to the ALB |
| NodePort Services | Opens a port on every node. Use an **Ingress** + AWS Load Balancer Controller, `target-type: ip` (ALB → pod IPs). Services = **ClusterIP** |
| Front-end pod → backend pod | React runs **in the browser**: the browser calls `/api` through the same ALB. The pod only serves files (or S3 + CloudFront) |
| "Stateful deployment" for the DB | **StatefulSet** works, but you own backups and failover. Prod: **RDS Multi-AZ**. In-cluster: StatefulSet + headless Service + PVC per replica (EBS, one AZ) + NetworkPolicy |

- **Security chain:** internet → ALB SG `443` · ALB SG → app (only from the ALB SG) · app → DB SG `5432` only from the backend · NetworkPolicy does the same between pods.

> **Say it:** "Route 53 alias → ALB in public subnets, created by an Ingress: `/` to the frontend Service, `/api` to the backend Service, both ClusterIP, target-type ip into private app subnets. React runs in the browser, so the browser calls `/api`. Data tier is RDS Multi-AZ in data subnets. SGs chain ALB → app → DB; NetworkPolicy inside the cluster."

---

## 5 · Central monitoring with SigNoz

![Central monitoring with SigNoz for many accounts](diagrams/r4-central-monitoring-signoz.drawio.svg)

- **Drawn right:** SigNoz OTel Collector → **ClickHouse** → query service + UI + alerts.

| Missing or wrong | Fix |
|---|---|
| Apps send straight across accounts | An **OTel Collector per cluster**: DaemonSet (logs, node/pod metrics) + gateway (receives OTLP, **batches, labels, retries**). Only it leaves the account |
| Accounts B and C empty | Same set-up in every account |
| No network path between accounts | **PrivateLink**: an NLB endpoint service (4317 gRPC, 4318 HTTP) in the monitoring account; an interface endpoint per workload account. Overlapping CIDRs don't matter (A2) |
| Unlabelled data | Every collector adds `k8s.cluster.name`, `deployment.environment`, `cloud.account.id` |
| No outputs | Dashboards + **alerts** to Slack / PagerDuty |
| No scale or cost plan | Collector replicas behind the NLB, ClickHouse **TTL** + S3, trace **sampling** |

- **Simpler: SigNoz Cloud**: collectors export straight to it with an **ingestion key**. Self-host when data must stay in your accounts.

```yaml
# A workload cluster's collector (the important parts)
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
processors:
  memory_limiter:
    check_interval: 1s
    limit_percentage: 80
  resource:
    attributes:
      - key: k8s.cluster.name
        value: staging-eks
        action: upsert
      - key: deployment.environment
        value: staging
        action: upsert
      - key: cloud.account.id
        value: "222222222222"
        action: upsert
  batch: {}
exporters:
  otlp:
    endpoint: otel.monitoring.internal:4317   # private DNS of the PrivateLink interface endpoint
service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, resource, batch]
      exporters: [otlp]
```

> **Say it:** "Each cluster runs its own OpenTelemetry Collector, a DaemonSet plus a gateway that batches, labels with cluster, environment and account, and retries. Only collectors cross accounts, over PrivateLink to an NLB in front of SigNoz's collectors. ClickHouse stores it with retention and S3 tiering; the query service serves dashboards and alerts. SigNoz Cloud is the no-ops option."

---

## 6 · The Dockerfile on the same drawing

![Multi-stage build](docker/diagrams/06-multi-stage-build.drawio.svg)

| Written | Fix |
|---|---|
| `From reactjs` | No such image: **multi-stage**, build with `node`, serve with nginx |
| `COPY` before `WORKDIR` | `WORKDIR` first |
| Copy package, install, copy code | Right idea: `package.json` + lock → `npm ci` → code (cache) |
| `USER create user` | Use an image that **already runs non-root**: `nginxinc/nginx-unprivileged:1.27-alpine` (user `101`, port `8080`, tested) |
| `docker tag tagname` | Tag with the **git commit ID**, push to **ECR** |

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
```

```bash
# dist = Vite's output (Create React App uses build)
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-south-1.amazonaws.com
docker build -t 123456789012.dkr.ecr.ap-south-1.amazonaws.com/frontend:4f2a9c1 .
docker push 123456789012.dkr.ecr.ap-south-1.amazonaws.com/frontend:4f2a9c1
```

---

## Practise before the next round

1. Draw r1 from memory, with route tables (his main point: **where NAT and IG sit**).
2. Write a subnet table for a new VPC on paper; check no ranges overlap.
3. Say the three-tier path: browser → Route 53 → ALB → `/` or `/api` → pods → RDS.
4. Explain the SigNoz design in 1 minute: local collectors, labels, PrivateLink, ClickHouse, alerts.
