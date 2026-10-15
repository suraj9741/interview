# Interview Transcript Review · 9 Oct 2026 · Where I Went Wrong and How to Improve

From the 63-minute recording with Hemant Kumar (One2N). Corrected diagrams: [interview-review-oct-9.md](interview-review-oct-9.md). This file: **every question**, **his feedback**, and a **plan to close the gaps**.

## 1. Hemant's verdict

- **Good:** "Better than what you were a few weeks back." You connect the terms and talk like technical people talk.
- **His offer:** no more formal interview for now; ping him when stuck on something specific.

| # | Gap | His words (summarised) | Section |
|---|---|---|---|
| 1 | **Subnetting maths** | "Totally wrong. Bit and byte are very different. Calculate on pen and paper" | [3](#3-the-biggest-gap-ip-and-subnetting-maths) |
| 2 | **Placement and traffic flow** | "NAT gateway sits in a public subnet. Draw route tables and traffic flow. Recreate AWS diagrams" | [4](#4-placement-route-tables-and-traffic-flow) |
| 3 | **Dockerfile depth** | "You can write the syntax, but you need more depth" | [5](#5-dockerfile-depth) |
| 4 | **Kubernetes basics** | "Services, exposure, frontend ↔ backend. Run a 3-tier app yourself" | [6](#6-kubernetes-exposure-and-scaling) |
| 5 | **Expected level** | What One2N expects at 1.5–2 years | [9](#9-the-4-week-plan) |

---

## 2. Question by question

### Q1 · Dev and staging in one AWS account: where does it fail?

![One AWS account per environment](diagrams/r6-account-per-environment.drawio.svg)

- **You said:** complex policies; a privileged user could delete CloudTrail; "multiple private networks". **Gap:** good log point, no fix; vague scaling.

> **Say it:** "One account per environment under AWS Organizations: separate blast radius, quotas (e.g. 5 VPCs per region) and permissions, SCP guardrails, and CloudTrail centralised in a log-archive account. That's the Control Tower landing zone."

### Q2–Q9 · VPC, CIDR, subnets, IGW and NAT

![Corrected VPC](diagrams/r1-vpc-subnets-nat-igw.drawio.svg)

| Q | You said | Gap → correct answer |
|---|---|---|
| **Q2** Draw the VPC | Regions **inside** the VPC (fixed after his hint) | **Account → Region → VPC** (spans all AZs) **→ Subnet** (one AZ). IGW attaches to the **VPC** |
| **Q3** Which CIDR? Always big? | "/16 for more IPs; depends" | Size for growth and **EKS (every pod = a VPC IP)**; `/16`–`/28`; secondary CIDRs later; **unique** from IPAM or peering breaks (A2) |
| **Q4** /16, 10.0.1.0/24, first/last, how many? ("totally wrong") | "/16 is 128 bytes"; last IP `10.0.256.256`; "8 or 4 bits?"; "253/255/256" | IPv4 = **32 bits = 4 bytes** (128 bits is IPv6). Last = **`10.0.1.255`** (octets 0–255). **256** total, 254 usable normally, **251 on AWS**. Next `/24`: `10.0.2.0`; next `/20`: +16 |
| **Q5** Public vs private: where do workloads go? | Frontend in public | **Only load balancers and NAT** (maybe a bastion) in public. Frontend is private, reached through the ALB |
| **Q6** Why 6 subnets? | HA if a "**region**" fails | You meant **AZ**. "3 AZs × 2 tiers = 6; I'd use 3 tiers = 9 so the DB has no internet route. Count = AZs × tiers; size = IPs per tier" |
| **Q7** Where do databases go? | Private, only from backend ✅ | Add: **data subnets** with no internet route; DB subnet group in **≥2 AZs**; SG `5432` only from the backend SG |
| **Q8** Which subnet is public? IGW on subnets or VPC? | "Assign an IGW or NAT to each subnet"; "confused" | IGW = **one per VPC**. Public = **route table** `0.0.0.0/0 → IGW`; private = `→ NAT`. The route table decides, not the name |
| **Q9** What is NAT, where does it go? | SNAT/DNAT ✅; then "NAT in the subnet that wants internet" ❌ | NAT gateway **in a public subnet**, one per AZ, Elastic IP; private subnets **route to it**; its subnet routes to the IGW. Outbound only |

### Q10 · How does a developer connect to a private database?

![How a developer reaches a private database](diagrams/r7-private-db-access.drawio.svg)

- **You said:** VPN or bastion; couldn't recall site-to-site vs point-to-site.

### Q11–Q15 · Kubernetes on AWS

![Corrected three-tier architecture on EKS](diagrams/r3-three-tier-on-eks.drawio.svg)

| Q | You said | Gap → correct answer |
|---|---|---|
| **Q11** 3-tier on Kubernetes | DB in a "stateful deployment" ✅ idea | **StatefulSet**: stable names (`postgres-0`), **PVC per pod** (`volumeClaimTemplates`, EBS CSI), ordered start/stop, **headless Service**. Backups/failover: an operator (CloudNativePG) or RDS |
| **Q12** React Dockerfile | `FROM` a React image… forgot code, Docker Hub | No React image: **multi-stage** node → nginx; `WORKDIR` first; `package*.json` → `npm ci` → code; `.dockerignore`; **git SHA** tag; **ECR**. [Full Dockerfile](interview-review-oct-9.md#6--the-dockerfile-on-the-same-drawing) |
| **Q13** Expose the frontend; NodePort? | NodePort → target group → ALB → Route 53; 2 of the Service types | 4 types: **ClusterIP**, **NodePort** (30000–32767 on every node), **LoadBalancer** (NLB on EKS), **ExternalName**, + headless. EKS: **AWS Load Balancer Controller + Ingress** (`ingressClassName: alb`) creates the ALB, listeners, target groups; `target-type: ip` → pods; Services ClusterIP. Route 53 alias → ALB (ExternalDNS) |
| **Q14** Frontend ↔ backend | `service.namespace.svc.cluster.local` ✅; unsure of type | **ClusterIP**. And React runs **in the browser**: the browser calls `/api` via the ALB |
| **Q15** Scale apps and nodes | "node class, node pool… ASGs"; HPA "inside the Deployment"; StatefulSet "need to check" | **HPA is its own object** (`minReplicas`, `maxReplicas`, target 70% CPU; needs metrics-server + CPU requests). Nodes: **Cluster Autoscaler** → managed node groups (= ASGs); **Karpenter** (and EKS Auto Mode) → **NodePool + NodeClass**, launches EC2 **directly, no ASGs**. Databases don't scale by adding replicas: vertical, or read replicas via an operator |

![Pod and node autoscaling](kubernetes/diagrams/12-autoscaling.drawio.svg)

### Q16 · Centralised observability for many accounts

![Central monitoring with SigNoz](diagrams/r4-central-monitoring-signoz.drawio.svg)

- **You said:** collector, ClickHouse, UI and query ✅; then expose the central collector **on the internet** and apps push straight to it ❌.
- **Fix:** an **OTel Collector per cluster** (DaemonSet + gateway: batch, **label**, retry); only collectors leave, over **PrivateLink** (or TGW; internet only with TLS + auth). Keep **metrics, logs, traces** distinct (you said "logs" for metrics). Add retention, scaling, **alerts**.

---

## 3. The biggest gap: IP and subnetting maths

![Subnetting on paper: the block-size method](diagrams/r8-subnet-block-size.drawio.svg)

![CIDR explained](diagrams/r2-cidr-explained.drawio.svg)

### Worksheet: on paper, then check

1. Bits in an IPv4 address? In IPv6?
2. 168 in binary.
3. `10.0.1.0/24`: first, last, total, usable (normally and on AWS)?
4. `10.0.0.0/16`: first, last, total?
5. `10.0.16.0/20`: range and size?
6. `192.168.10.64/26`: range, total, next `/26`?
7. How many `/24`s fit in a `/16`?
8. Split `10.0.0.0/24` into 4 equal subnets.
9. Do `10.0.16.0/20` and `10.0.20.0/24` overlap?
10. Which `/20` contains `10.0.37.5`?
11. Masks for `/16`, `/20`, `/24`, `/26`.
12. Plan 3 public `/24`s and 3 private `/20`s in `10.0.0.0/16`, no overlaps.

<details>
<summary><b>Answers</b> (open only after trying)</summary>

1. IPv4 **32** bits (4 bytes). IPv6 **128** bits.
2. 128 + 32 + 8 = **`10101000`**.
3. `10.0.1.0` (network) to `10.0.1.255` (broadcast), **256**. Usable **254** (`.1`–`.254`), **251 on AWS** (`.4`–`.254`).
4. `10.0.0.0` to `10.0.255.255`: **65,536**.
5. Block 16 in octet 3 → **`10.0.16.0`–`10.0.31.255`**: **4,096** (4,091 on AWS).
6. Block 64 in octet 4 → **`192.168.10.64`–`192.168.10.127`**: **64**. Next **`192.168.10.128/26`**.
7. 2^(24 − 16) = **256**.
8. **`10.0.0.0/26`, `10.0.0.64/26`, `10.0.0.128/26`, `10.0.0.192/26`** (64 each).
9. **Yes**: 20 is inside 16–31.
10. 37 ÷ 16 = 2 r 5 → **`10.0.32.0/20`** (`10.0.32.0`–`10.0.47.255`).
11. `255.255.0.0` · `255.255.240.0` · `255.255.255.0` · `255.255.255.192`.
12. Public `10.0.0.0/24`, `10.0.1.0/24`, `10.0.2.0/24`; private `10.0.16.0/20`, `10.0.32.0/20`, `10.0.48.0/20`.

</details>

**Done when:** all 12 right on paper, no calculator, under 15 minutes.

**Videos:** [You SUCK at Subnetting EP 1](https://www.youtube.com/watch?v=5WfiTHiU4x8) · NetworkChuck · 18 min · [subnetting is simple](https://www.youtube.com/watch?v=ecCuyq-Wprc) · Sunny Classroom · 13 min · [Public vs Private IP Address](https://www.youtube.com/watch?v=po8ZFG0Xc4Q) · PowerCert · 7 min

---

## 4. Placement, route tables and traffic flow

![Traffic flow and route tables](diagrams/r5-traffic-flows-route-tables.drawio.svg)

Draw on paper, from memory:
1. r1: 3 AZs × 3 tiers, IGW, NAT gateways, all 3 route tables. **10 minutes.**
2. Trace ① a user opening the site and ② a pod downloading a package (as in r5).
3. Add ③ a developer reaching the DB with SSM port forwarding (r7).
4. Find "AWS VPC architecture diagram" images online and redraw one with a NAT gateway; check every element's place. Reference: AWS docs "Example: VPC with servers in private subnets and NAT".

---

## 5. Dockerfile depth

![CMD vs ENTRYPOINT](docker/diagrams/05-cmd-entrypoint.drawio.svg)

| Know | Why it matters |
|---|---|
| Multi-stage | Build tools stay behind: small image, fewer CVEs |
| Layer cache order | Dependencies first, code last: code changes don't reinstall |
| `CMD` vs `ENTRYPOINT`, exec form, PID 1 | Signals reach the app |
| Non-root `USER` (numeric UID 10001), port > 1024 | No root after an escape |
| `.dockerignore`, pinned base, **git SHA** tags | Small context, reproducible, traceable |
| ECR push | `aws ecr get-login-password \| docker login …`, `docker push` |

- Notes: [Docker 05](docker/05-dockerfile.md) · [06](docker/06-build-optimization.md). Practice: `npm create vite@latest`, multi-stage Dockerfile, run on 8080.

---

## 6. Kubernetes: exposure and scaling

Path by heart ([r3](diagrams/r3-three-tier-on-eks.drawio.svg)): browser → Route 53 (alias) → ALB (from an Ingress) → `/` → frontend Service (ClusterIP) → pods; browser → `/api` → backend Service → pods → DB (StatefulSet + headless Service + PVC, or RDS).

**Run it yourself** on the [practice cluster](helm-chart/README.md#your-own-practice-cluster-no-kind-needed-):
1. frontend Deployment + ClusterIP Service;
2. backend Deployment + ClusterIP Service;
3. Postgres StatefulSet + headless Service + PVC;
4. Ingress: `/` → frontend, `/api` → backend;
5. HPA on the backend; watch `kubectl get hpa -w`.

**Done when:** `curl` through the Ingress returns data from Postgres and you can explain every object. Notes: [08](kubernetes/08-services-and-dns.md) · [09](kubernetes/09-ingress-and-gateway-api.md) · [12](kubernetes/12-resources-and-autoscaling.md) · [20](kubernetes/20-eks.md). Video: [ClusterIP vs NodePort vs LoadBalancer](https://www.youtube.com/watch?v=T4Z7visMM4E) · Nana · 24 min.

---

## 7. How you answered: communication

| Problem | Fix |
|---|---|
| **Wrong terms:** region/AZ, logs/metrics, "stateful deployment", bytes/bits | One wrong word sounds like one wrong concept. Say the exact term |
| **Fillers:** "like", "means like", "I can say" | Shape: **one-line answer → why → example → trade-off** |
| **"I'm confused" with no plan** | "I'm not sure about X. I'd check Y; my best guess is Z, because…" (Hemant: *"If you don't know, say it out loud"*) |
| **Answer buried** | First sentence answers the exact question: "In a public subnet, one per AZ." |
| Practice | Record 3 × 60-second answers a day; listen for fillers and wrong terms |

## 8. What went well (keep doing it)

- DB in private subnets, only from the backend · NAT = private → shared IP, plus SNAT/DNAT · why non-root containers · `service.namespace.svc.cluster.local` · SigNoz components · audit-log deletion as an account risk.

---

## 9. The 4-week plan

~1 h on weekdays, 2–3 h at weekends. Videos → hands-on → explain out loud.

| Week | Focus | Do | Done when |
|---|---|---|---|
| **1** | IP and subnetting | Section 3 videos; the worksheet **every day**; [Networking 01](networking/01-basics.md) | 12/12 in under 15 min, no calculator |
| **2** | VPC design, traffic flow | [Server Gyan VPC video](https://www.youtube.com/watch?v=TuBA5maXFgc) (7 min); section 4 drawings; [Networking 02 NAT](networking/02-nat.md) | r1 + r5 from memory in 10 min, flows ①②③ explained |
| **3** | Kubernetes 3-tier, hands-on | Nana Services video; the section 6 lab | `curl` via Ingress returns Postgres data |
| **4** | Docker depth, EKS exposure, scaling, observability | React multi-stage; AWS LB Controller + Ingress; Karpenter vs Cluster Autoscaler; r4 | **Mock interview** of Q1–Q16 ("act as Hemant") |

- **Each week:** send Hemant **one specific question**, e.g. "I calculated `10.0.37.5` falls in `10.0.32.0/20`. Is my block-size method right?"
- ⚠️ **Cost:** NAT gateways and ALBs bill by the hour. Use your own account and delete them the same day, or practise locally.
