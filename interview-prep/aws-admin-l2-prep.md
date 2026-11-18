# AWS Admin Engineer · L2 prep pack (tonight + tomorrow 9:00 warm-up) · interview Thu 19 Nov, 10:30 AM

**What L2 will do:** they've seen round 1, so expect them to **re-ask the weak spots** (private EC2 internet, 502/503/504, TCP, DNS, Terraform code) and to go **deeper**: "walk me through an outage you owned", "debug this live", "write this Terraform", "why this role". Round 1 shows what they liked: SG vs NACL, the slow-app answer, the RDS secret rotation story. Keep those and fix the rest.

**How to use this file:** for every question, **type** your answer in a blank file first (`l2.txt`), then open the hidden answer and mark it 1 or 0. Every 0 goes into `misses.md` and gets re-typed at 10 PM and again at 9 AM. **Reading the answers without typing first doesn't count.** That's exactly what failed on 11 and 13 Nov.

Deep reference (look things up there, don't read it end to end): [AWS troubleshooting playbook](aws-troubleshooting-playbook.md) · [your interview stories](aws-interview-stories.md) · IAM cheat sheet `interview-prep/aws/01-iam-cheat-sheet.md` (PR #15).

---

## Tonight's schedule (Wed 18 Nov)

The SAA schedule is paused tonight and tomorrow morning. It resumes tomorrow afternoon.

| Time | What |
|---|---|
| 5:30–6:15 | **Part 1:** the 7 round-1 misses. Type each, check, fix |
| 6:15–6:45 | **Say** each Part 1 answer out loud and **record** it. Count the "like" / "means like". Target: under 5 per answer. Redo any answer over 5 |
| 6:45–7:15 | **Part 2:** fill the blanks in your incident story and rehearse it in 2 minutes, out loud, twice |
| 7:15–8:00 | Dinner, no screens |
| 8:00–9:00 | **Part 3:** deep dives A–C (outage RCA, VPC/SG/NACL debugging, IAM) |
| 9:00–9:45 | **Part 3:** deep dives D–F (CloudWatch/logging, Terraform state/drift + **write code**, DNS/TCP/HTTP) |
| 9:45–10:15 | **Mock:** send "L2 mock" in the thread. I ask 8 questions the way an L2 interviewer would; you answer without notes |
| 10:15–10:30 | Re-type every miss from tonight once. Then **stop**. Lay out ID, charger, water. Sleep by 11 |

## Tomorrow morning (Thu 19 Nov)

| Time | What |
|---|---|
| 8:30 | Breakfast. No new material today |
| 9:00–9:30 | **Warm-up:** the 10-question morning test at the end of this file, typed, then say your intro and incident story out loud once |
| 9:30–10:00 | Logistics: laptop charged, earphones, quiet room, test the call link and camera, close every other tab. Have a notepad and pen |
| 10:00–10:25 | Walk, water, nothing to read. Re-read only your "why this role" and your 3 questions for them |
| 10:25 | Join 5 minutes early |

**During the interview:** slow down. When a question comes, pause 2 seconds, say the **structure** first ("I'd check this in layers: DNS, routing, security groups, NACL, the OS, then the app"), then go layer by layer. A clear structure with 80% of the details beats every detail delivered in a rush with "like" every few words.

---

## Part 1: the round-1 misses (type first, then open)

<details><summary>1. A private EC2 instance can't reach the internet (`yum update` hangs). What do you check, in order?</summary>

**30-second spoken answer:** "This is outbound traffic, so I follow the path out. First the private subnet's route table: it needs `0.0.0.0/0` to a NAT gateway. The NAT gateway must sit in a public subnet whose route table sends `0.0.0.0/0` to the internet gateway, and it needs an Elastic IP and state Available. Then the security group's outbound rules, and the NACLs on both subnets: outbound 443 and 80, plus inbound ephemeral ports 1024 to 65535 for the replies, because NACLs are stateless. Then DNS from the instance. To prove where it breaks I use VPC Flow Logs, where REJECT means SG or NACL, and Reachability Analyzer. If it only needs S3 or other AWS services, a VPC endpoint is cheaper than NAT."

**What went wrong on 13 Nov:** you explained how to SSH **into** the instance. Listen for direction: "reach the internet" = outbound.
</details>

<details><summary>2. You said "3 private subnets and 1 public subnet, ALB in front". What's wrong with that, and what's the correct design?</summary>

**30 seconds:** "An ALB needs at least two subnets in two different Availability Zones, so one public subnet can't host it. The correct layout is one public and one private subnet per AZ, so with 3 AZs, 3 public and 3 private. ALB and NAT gateways go in the public subnets, app and EKS nodes in private subnets, and RDS in private database subnets. For high availability, one NAT gateway per AZ; to save cost some teams use one, but that's a single point of failure and adds cross-AZ data charges."

If they ask about **your** architecture: describe what was really there, and if you're unsure about the subnet count, say "I'd need to check the exact subnet count, but the ALB spanned at least two AZs, because it has to."
</details>

<details><summary>3. ALB returns 502, 503 and 504. One cause and one check for each.</summary>

- **502 Bad Gateway:** the target got the request but sent back an invalid response or closed the connection. Causes: app crashed or restarting, wrong target port, HTTPS/HTTP mismatch between ALB and target, app keep-alive timeout shorter than the ALB idle timeout. Check: app logs, target port, ALB access logs (`target_status_code`).
- **503 Service Unavailable:** the target group has **no registered targets** (empty, or all deregistered, e.g. a failed deployment or an ASG at 0). Precise detail: if targets are registered but **all** fail health checks, the ALB **fails open** and still sends traffic to them, so you usually see 502/504 instead.
- **504 Gateway Timeout:** the target didn't respond within the ALB **idle timeout** (60 s default): slow app, slow DB query, or an SG/NACL silently dropping traffic.

**Evidence that splits it:** CloudWatch `HTTPCode_ELB_5XX_Count` (the ALB made the error) vs `HTTPCode_Target_5XX_Count` (the app returned it), plus `UnHealthyHostCount` and `TargetResponseTime`.

**What went wrong on 13 Nov:** you blamed 502 on unhealthy targets, mentioned "authentication issues", and forgot 503.
</details>

<details><summary>4. The TCP 3-way handshake, and how a connection closes.</summary>

**Open:** client sends **SYN** → server replies **SYN-ACK** → client sends **ACK**. Now data flows.
**Close:** each side sends **FIN** and the other answers **ACK** (4 packets; the side that closes first sits in TIME_WAIT for a while).
**Why it matters for troubleshooting:** SYN sent but no SYN-ACK = something drops it (SG, NACL, firewall, nothing listening returns RST instead). "Connection refused" = RST (host reached, port closed). "Timed out" = no answer at all (filtered or routing).

**13 Nov:** you gave two steps.
</details>

<details><summary>5. What does `dig` show? What does `traceroute` show? What does `nslookup` add? Which do you use for what?</summary>

- `dig app.example.com`: the **DNS answer**: record type, value, **TTL**, which server answered, status (NOERROR, NXDOMAIN, SERVFAIL). `dig @8.8.8.8 app.example.com` asks a specific resolver; `dig +trace` shows the delegation chain root → `.com` → the authoritative name servers.
- `nslookup`: an older, simpler DNS lookup tool. Same purpose, less detail.
- `traceroute` / `mtr`: the **network hops** (routers) on the path to an IP. Use it for routing and latency, not DNS.

**13 Nov:** you said dig shows hops. That's traceroute.
</details>

<details><summary>6. Write a Terraform resource for an S3 bucket with versioning, and the S3 backend block with locking. (Type it, don't describe it.)</summary>

```hcl
terraform {
  backend "s3" {
    bucket       = "suraj-tf-state"
    key          = "prod/app/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true          # S3 native lock (Terraform 1.10+); older setups: dynamodb_table = "tf-locks"
  }
}

resource "aws_s3_bucket" "logs" {
  bucket = "suraj-logs-2026"
  tags   = { env = "dev" }
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration {
    status = "Enabled"
  }
}
```
Shape to remember: `resource "<TYPE>" "<NAME>" { ... }`, referenced as `<TYPE>.<NAME>.<attribute>`. Since AWS provider v4, versioning is its **own resource**, not a block inside the bucket.

**13 Nov:** "I didn't practise." In L2, even a rough block written calmly is worth far more than refusing.
</details>

<details><summary>7. "Tell me about a recent high-severity incident you handled." (Replace the Replicate billing story.)</summary>

Use **Part 2** below: the SSL expiry incident. The Replicate balance story is a billing/monitoring gap, not an engineering incident. Only use it if they ask "a time a third-party dependency failed", and then tell it as: "provider credit hit zero, video generation failed, we had no balance alert, we topped up, then added a low-balance alert and a runbook."
</details>

---

## Part 2: your incident story (real, from what you said on 13 Nov)

You already told this in round 1, but buried at the end. **Lead with it in L2.** Fill every ⟨…⟩ with the real value. If you don't remember a number, say "roughly" and how you know. **Never invent one.**

**SSL certificate expiry on a site outside ACM**

- **S (20 s):** "At ⟨Koko / One2N, month-year⟩, our main sites used ACM certificates on the ALB, which renew automatically. But one site, our ⟨WordPress marketing site⟩, was hosted ⟨where: separate EC2 / Lightsail / outside AWS⟩ with its own certificate. Nobody tracked it, and it expired."
- **T (10 s):** "I was ⟨on call / the SRE who picked it up⟩, and I had to restore HTTPS and make sure it couldn't happen again."
- **A (60 s):**
  1. "It was reported by ⟨users / the marketing team / a browser warning⟩ at ⟨time⟩."
  2. "I confirmed with `openssl s_client -connect site:443 -servername site` and `curl -v`: the certificate's notAfter date had passed."
  3. "I renewed it with ⟨certbot / the provider / moved it behind ACM⟩ and restarted ⟨nginx / Apache⟩. HTTPS was back in ⟨N⟩ minutes."
  4. "Then I listed **every** public domain we owned, from ⟨Route 53 hosted zones / DNS records⟩, to find any other certificate outside ACM."
- **R (20 s):** "I added certificate-expiry monitoring for all sites: ⟨Prometheus blackbox exporter `probe_ssl_earliest_cert_expiry` / CloudWatch / an uptime tool⟩, alerting ⟨30⟩ days before expiry. It hasn't happened again."
- **Learning (10 s):** "Automating renewal isn't enough; you need an inventory of every certificate, and monitoring on the ones you don't control."

**Follow-ups to expect:**

| Question | Answer |
|---|---|
| How does ACM renewal work? | DNS-validated ACM certs renew automatically while the validation CNAME stays in DNS. Email-validated ones need someone to click approve. Standard ACM certs are attached to integrated services (ALB, CloudFront, API Gateway); you don't install them on an EC2 web server, which is why a site served directly from EC2/WordPress needs its own cert (e.g. certbot) and its own monitoring |
| How do you check a cert's expiry from the CLI? | `echo \| openssl s_client -connect site:443 -servername site 2>/dev/null \| openssl x509 -noout -dates` |
| What's the Prometheus metric? | `probe_ssl_earliest_cert_expiry - time() < 30*86400` (blackbox exporter): alert if under 30 days |
| Blameless? What was the process fix? | Yes. The cause wasn't a person; it was a missing inventory. Action items: inventory, alerting, an owner per domain |

**Second story, if they ask "a difficult problem you solved":** the **RDS password rotation with Secrets Manager** you told in round 1 (it was your best answer). Tighten the ending: "Rotation now runs automatically every ⟨N⟩ days, the app reads the secret at connection time, and there's no manual password change any more."

---

## Part 3: L2 deep dives (type first, then open)

### A. Outage and RCA

<details><summary>A1. Production is down and you're paged. Walk me through the first 15 minutes.</summary>

1. **Acknowledge** and declare severity (P1 if customers are impacted). Open a bridge/channel; post a first update ("investigating, next update in 15 min").
2. **Scope:** what's broken, for whom, since when? Dashboards: ALB 5xx, latency, error rate.
3. **What changed?** Recent deploys (ArgoCD/Jenkins history), CloudTrail for infra changes (SG, route table, listener, IAM), AWS Health Dashboard for a regional issue.
4. **Mitigate before you root-cause:** roll back the deploy, revert the change, scale up, fail over. Restore service first.
5. **Keep evidence:** don't delete logs or pods; note timestamps.
6. **Communicate** on a fixed rhythm until resolved, then hand over to the RCA.
</details>

<details><summary>A2. What goes into an RCA / postmortem?</summary>

Summary and impact (who, how long, how much) · **timeline** with timestamps (detected, acknowledged, mitigated, resolved) · **root cause** found with 5 Whys until you reach a process cause, not "human error" · what went well / what didn't · **action items with owners and dates** (alert, runbook, automation, Terraform guardrail) · blameless tone. Metrics to quote: **MTTD** (time to detect) and **MTTR** (time to restore).
</details>

<details><summary>A3. Someone changed a security group and the site went down. How do you find who, when and what?</summary>

**CloudTrail** → Event history, filter on the time window and event names such as `RevokeSecurityGroupIngress`, `AuthorizeSecurityGroupIngress`, `ModifySecurityGroupRules`. It shows the IAM identity, source IP, time and request parameters. **AWS Config** shows the resource's configuration timeline (before/after). Fix: restore the rule (ideally by re-applying Terraform). Prevent: changes only through Terraform + PR review, Config rule or alarm on SG changes.
</details>

### B. VPC, security group vs NACL debugging

<details><summary>B1. Security group vs NACL: 6 differences.</summary>

| | Security group | NACL |
|---|---|---|
| Attached to | ENI / instance (ALB, RDS, Lambda in VPC) | Subnet (each subnet has exactly one) |
| State | **Stateful**: replies allowed automatically | **Stateless**: allow the reply direction too (ephemeral 1024–65535) |
| Rules | Allow only | Allow **and deny** |
| Evaluation | All rules together | In **rule-number order**, first match wins |
| Default | New SG: no inbound, all outbound | Default NACL allows all; a **custom** NACL denies all until you add rules |
| Can reference | Other security groups (e.g. allow from the ALB's SG) | Only CIDR ranges |

Use NACLs for broad subnet-level blocks (e.g. deny a bad IP range); use SGs for everything else.
</details>

<details><summary>B2. EC2 can't connect to RDS. Your checks, and the one command that splits network from auth.</summary>

From the EC2: `nc -zv mydb.xxxx.ap-south-1.rds.amazonaws.com 5432` (or 3306).
- **Timeout** = network: RDS security group must allow 5432 **from the EC2's security group**; NACLs; same VPC or peering/TGW routes; DB subnet group; DNS resolves to a private IP (`dig` the endpoint).
- **Connects but login fails** = auth: username/password (Secrets Manager value), IAM DB auth token, `pg_hba`/user grants, SSL required.
- Also: RDS status Available, `max_connections` reached (`DatabaseConnections` metric).
</details>

<details><summary>B3. How do you prove where packets are dropped in a VPC?</summary>

**VPC Flow Logs** (to CloudWatch Logs or S3): `REJECT` = SG or NACL blocked it; `ACCEPT` but no reply = the OS/app or a NACL on the return path; no record at all = routing or DNS sent it elsewhere. **Reachability Analyzer** tests the path between two resources without sending traffic and names the blocking component.
</details>

<details><summary>B4. Two VPCs are peered but can't talk. Checks?</summary>

Peering status Active (accepted) · **route tables on both sides** have the other VPC's CIDR → `pcx-…` · SGs allow the other VPC's CIDR (or the peer SG, same region) · NACLs · **CIDRs don't overlap** · peering isn't transitive (A–B and B–C doesn't give A–C; use Transit Gateway) · DNS resolution over peering enabled if using private DNS names.
</details>

### C. IAM

<details><summary>C1. How does AWS decide allow or deny for a request?</summary>

Start with an **implicit deny**. Gather every policy that applies (identity policies, resource policy, permission boundary, SCP from Organizations, session policy). **An explicit Deny anywhere wins.** Otherwise there must be an **Allow**, and it must also be allowed by every boundary that applies (SCP and permission boundary limit what's possible; they never grant on their own).
</details>

<details><summary>C2. An EC2 app needs to read one S3 bucket. How do you give access, and why not access keys?</summary>

Create an **IAM role** with a policy allowing `s3:GetObject` on `arn:aws:s3:::bucket-name/*` (and `s3:ListBucket` on `arn:aws:s3:::bucket-name` if it lists), attach it to the instance through an **instance profile**. The app gets **temporary credentials** from the instance metadata service, rotated automatically. Access keys on a server are long-lived secrets that leak (git, AMIs, logs). On EKS the same idea is IRSA or EKS Pod Identity.
</details>

<details><summary>C3. A user gets AccessDenied on S3 even though their IAM policy allows it. Where else do you look?</summary>

Bucket policy with an explicit Deny (e.g. require TLS, a specific VPC endpoint or source IP) · SCP in the organization · permission boundary on the user/role · **KMS key policy** if the object is SSE-KMS encrypted (needs `kms:Decrypt`) · object owned by another account (Object Ownership / ACLs) · Block Public Access (for public access) · wrong ARN (bucket vs `bucket/*`). Use the error message, CloudTrail and the IAM policy simulator.
</details>

### D. CloudWatch and logging

<details><summary>D1. Which CloudWatch metrics and alarms would you set up for a web app behind an ALB on EC2/EKS with RDS?</summary>

- **ALB:** `HTTPCode_ELB_5XX_Count`, `HTTPCode_Target_5XX_Count`, `TargetResponseTime` (p95/p99), `UnHealthyHostCount`, `RequestCount`.
- **EC2:** `CPUUtilization`, `StatusCheckFailed`. Memory and disk need the **CloudWatch agent** (not collected by default).
- **RDS:** `CPUUtilization`, `FreeStorageSpace`, `DatabaseConnections`, `ReadLatency`/`WriteLatency`, `FreeableMemory`, replica lag.
- **Alarms** → SNS → email/Slack/PagerDuty. Alarm on symptoms users feel (5xx rate, latency) first, causes second.
</details>

<details><summary>D2. Where do you find logs for: the app, ALB requests, API calls in the account, network traffic?</summary>

App → **CloudWatch Logs** (agent or Fluent Bit on EKS) or your Loki/ELK · ALB → **ALB access logs** to S3 (enable them; query with Athena) · API calls → **CloudTrail** (90 days of event history free; a trail to S3 for longer) · network → **VPC Flow Logs**. Search CloudWatch Logs with **Logs Insights**, e.g. `fields @timestamp, @message | filter @message like /ERROR/ | stats count() by bin(5m)`.
</details>

<details><summary>D3. Default retention of CloudWatch Logs, and why you change it.</summary>

**Never expire** by default, so storage cost grows forever. Set a retention per log group (e.g. 30 days for app logs, longer for audit) and archive to S3 with lifecycle rules if needed.
</details>

### E. Terraform state, drift, and writing code

<details><summary>E1. What is the state file, why remote, why locked?</summary>

State maps your config to real resource IDs and stores their attributes, so Terraform can compute the diff in `plan`. **Remote** (S3, versioned, encrypted) so the team shares one copy and you can recover old versions. **Locked** (S3 lockfile or DynamoDB) so two `apply` runs can't write at once and corrupt it. It can contain secrets, so restrict access. Never edit it by hand; use `terraform state mv/rm`, `import`, or `moved` blocks.
</details>

<details><summary>E2. Someone changed a security group in the console. How does Terraform find it, and what do you do?</summary>

`terraform plan` refreshes state from AWS and shows the difference (**drift**). `terraform plan -refresh-only` shows only drift without proposing config changes. Then decide: **revert** (apply the code, which puts it back) or **keep** it (update the code to match, then plan shows no changes). Prevent: console read-only for most users, all changes via PR, scheduled drift-detection plans in CI.
</details>

<details><summary>E3. Write a security group allowing 443 from anywhere and 22 only from 10.0.0.0/16, with the VPC ID as a variable.</summary>

```hcl
variable "vpc_id" {
  type = string
}

resource "aws_security_group" "web" {
  name   = "web-sg"
  vpc_id = var.vpc_id

  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH from inside the VPC"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "web_sg_id" {
  value = aws_security_group.web.id
}
```
Note: Terraform removes AWS's default allow-all egress rule unless you declare it, which is why the `egress` block is there.
</details>

<details><summary>E4. plan vs apply vs refresh-only; count vs for_each; what `terraform import` does.</summary>

`plan` = refresh + diff, changes nothing (save it with `-out=tfplan`, then `apply tfplan` applies exactly that). `apply` = makes the changes. `-refresh-only` = update state to match reality, no infra changes. `count` = N copies by index (removing one in the middle shifts the others and recreates them); `for_each` = keyed by name, stable. `import` = bring an existing resource under Terraform (an `import` block or `terraform import`), then write matching config until plan is clean.
</details>

### F. DNS, TCP, HTTP

<details><summary>F1. A user says the site doesn't load. Walk through DNS → TCP → TLS → HTTP with one command each.</summary>

DNS: `dig app.example.com` (right IP? TTL?) → TCP: `nc -zv app.example.com 443` (open/refused/timeout) → TLS: `openssl s_client -connect app.example.com:443 -servername app.example.com` (valid cert? chain? expiry?) → HTTP: `curl -v https://app.example.com/health` (status code, headers, time: `curl -o /dev/null -s -w "%{time_namelookup} %{time_connect} %{time_appconnect} %{time_total}\n" URL` shows where the time goes).
</details>

<details><summary>F2. DNS changed in Route 53, but some users still reach the old IP. Why?</summary>

**TTL caching**: resolvers and clients keep the old answer until the TTL expires. Lower the TTL (e.g. to 60 s) a day before a planned change. Also check: the registrar's NS records point to the right hosted zone, you edited the right zone (public vs private), and no local `/etc/hosts` override.
</details>

<details><summary>F3. Alias record vs CNAME in Route 53.</summary>

Alias points to AWS resources (ALB, CloudFront, S3 website, another record), works at the **zone apex** (`example.com`), follows IP changes automatically, and queries are free. A CNAME can't be used at the apex and costs normal query charges.
</details>

<details><summary>F4. TCP vs UDP; 3 HTTP status classes you see most in ops.</summary>

TCP: connection-oriented, ordered, retransmits (HTTP, SSH, databases). UDP: no connection, no delivery guarantee, low overhead (DNS queries, NTP, streaming). Status codes: **4xx** client side (400 bad request, 401 not authenticated, 403 forbidden, 404 not found, 429 rate limited), **5xx** server side (500 app error, 502/503/504 gateway errors above), **3xx** redirects (301 permanent, 302 temporary).
</details>

---

## Why this role (say it, don't read it)

"Most of my best work has been troubleshooting AWS production issues: connectivity problems, load balancer errors, outages and the RCAs after them. This role is that work full-time, across many customer environments, which means I'd see far more kinds of failures than in one product team and get better faster. I also like that it's both hands-on and process-driven: fixing the issue, then making sure it doesn't come back with monitoring, Terraform and runbooks. That's exactly what I did with the certificate monitoring at ⟨company⟩."

**Don't mention** bench, job security or "any opportunity". If asked why you're looking: "My current project ended, and I want a role where AWS operations is the core of the job, not a side task."

## Questions to ask them (pick 2)

1. What kinds of incidents take most of the team's time: networking, IAM, or application-level?
2. Is the infrastructure managed in Terraform end to end, or is there console drift you're still cleaning up?
3. How is on-call organised, and what does a good first 90 days look like in this role?

---

## Morning warm-up (Thu 9:00, 10 questions, typed, 20 minutes)

1. Private EC2, no internet: 5 checks in order.
2. 502 vs 503 vs 504 on an ALB, one cause each (including the 503 fail-open detail).
3. TCP open and close.
4. dig vs traceroute vs `dig +trace`.
5. SG vs NACL: stateful/stateless, allow/deny, attached to.
6. EC2 can't reach RDS: the one command that splits network from auth.
7. IAM evaluation: what wins?
8. Terraform: S3 backend block with locking, from memory.
9. Drift: how you detect it and the two ways to resolve it.
10. Your incident story's first sentence and last sentence.

Then say your intro (60 seconds) and the incident story (2 minutes) out loud once. Then close the laptop.
