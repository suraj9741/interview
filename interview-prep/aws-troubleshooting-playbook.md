# AWS Admin / troubleshooting interview playbook (13 Nov 2026)

The role: **AWS Admin Engineer, 4–8 years**. Troubleshooting AWS services, load balancers, security, connectivity and outages, with a working knowledge of Terraform. Expect **scenario questions**: "X is broken, what do you check?". Answer every one with the same habit: **scope → path → evidence → fix → prevent**.

![Connectivity check order](diagrams/a1-aws-connectivity-check-order.drawio.svg)

---

## 0. How to answer any troubleshooting question (say this structure out loud)

1. **Scope:** one user or all? One instance or all? Since when? **What changed?** (deploy, SG edit, certificate expiry, AWS Health event)
2. **Walk the path** from the client to the app (diagram above): DNS → route table → SG → NACL → OS → app.
3. **Evidence, not guesses:** VPC Flow Logs, ELB target health, CloudWatch metrics/logs, CloudTrail (who changed what), Reachability Analyzer, AWS Health Dashboard.
4. **Fix with the smallest safe change**, and verify it worked.
5. **Prevent it:** RCA, an alarm, Terraform so the change can't drift, a runbook.

**Opening line you can use:** "First I'd scope it and check what changed, then I'd walk the network path layer by layer and use Flow Logs and CloudTrail to prove where it breaks, instead of guessing."

**Background you should be able to draw** (from your 9 Oct review): ![VPC](diagrams/r1-vpc-subnets-nat-igw.drawio.svg) ![Route tables and traffic flows](diagrams/r5-traffic-flows-route-tables.drawio.svg)

---

## 1. The 13 scenarios

### S1. "I can't SSH into my EC2 instance"
| Check | Command / where | What's wrong if… |
|---|---|---|
| Instance state and status checks | EC2 console → Status checks (system vs instance) | System check failing = AWS host problem: stop/start (moves host). Instance check failing = OS problem (kernel, disk full, bad fstab) |
| Public IP / Elastic IP | Instance details | No public IP in a public subnet = can't reach from the internet |
| Route table of the subnet | VPC → Route tables | No `0.0.0.0/0 → igw-…` = not actually a public subnet |
| Security group | Inbound rule TCP 22 from **your IP** | Missing, or source is the wrong CIDR |
| NACL | Inbound 22 **and** outbound 1024–65535 | Stateless: the return traffic is blocked |
| Key and user | `ssh -i key.pem ec2-user@IP -v` | Wrong user (`ec2-user` Amazon Linux, `ubuntu` Ubuntu), key permissions must be `chmod 400` |
| OS | EC2 serial console / system log | sshd stopped, disk full, OS firewall |

- **Better answer for production:** "In production I'd use **SSM Session Manager** instead of SSH. No port 22 open, no keys, access through IAM, and sessions are logged. It needs the SSM agent, an instance role with `AmazonSSMManagedInstanceCore`, and a route to SSM (NAT or VPC endpoints)."

### S2. "My private EC2 can't reach the internet" (e.g. `yum update` hangs)
1. The private subnet's route table needs `0.0.0.0/0 → nat-…`.
2. The **NAT gateway must sit in a public subnet**, and that subnet's route table needs `0.0.0.0/0 → igw-…`. The NAT gateway needs an Elastic IP and status Available.
3. SG **outbound** allows 443/80 (the default allows everything).
4. NACLs on both subnets allow outbound 80/443 and **inbound ephemeral 1024–65535** for the replies.
5. DNS: `enableDnsSupport` on the VPC, and `/etc/resolv.conf` pointing at the VPC resolver (base + 2, e.g. 10.0.0.2).
- **If it only needs AWS services** (S3, ECR, SSM), use **VPC endpoints** instead. They're cheaper than NAT data processing and keep traffic private. S3/DynamoDB use free gateway endpoints; the others are interface endpoints, with a cost per hour.

### S3. "The website behind the ALB returns 502 / 503 / 504"
| Code | Meaning on an ALB | Check |
|---|---|---|
| **502 Bad Gateway** | Target sent an invalid response or closed the connection | App crashing/restarting, wrong target port, TLS mismatch (ALB → target on HTTPS but app speaks HTTP), target keep-alive timeout shorter than the ALB idle timeout |
| **503 Service Unavailable** | **No healthy targets** registered | Target group → Targets → health status and **reason** (`Target.FailedHealthChecks`, `Target.Timeout`); health check path/port/expected code (e.g. `/health` returns 200?); SG of targets must allow traffic **from the ALB's SG** |
| **504 Gateway Timeout** | Target didn't answer within the idle timeout (default 60 s) | Slow app/DB, target SG/NACL silently dropping, app overloaded |
| **4xx from the ALB itself** | 403 = WAF rule or listener rule; 460 = client closed early; 463 = too many IPs in X-Forwarded-For | WAF logs, listener rules |

- **Evidence:** ALB metrics `HTTPCode_ELB_5XX_Count` (the ALB generated the error) vs `HTTPCode_Target_5XX_Count` (the app returned it), `UnHealthyHostCount`, `TargetResponseTime`. Also **ALB access logs** in S3, which record each request and its target status code.
- **Say it:** "ELB 5xx means the load balancer couldn't get a good answer from the targets. Target 5xx means the app itself returned the error. That split tells me whether to look at the network and health checks, or at the application."

### S4. "Targets keep failing health checks"
- Is the app actually listening on the health check **port** and **path**? From another instance: `curl -v http://<target-ip>:8080/health`.
- The target SG must allow the health check port **from the ALB SG**.
- Does the expected success code match (200 vs 301 redirect to /login)?
- Healthy/unhealthy thresholds, timeout and interval. Is the app slow on startup? Add a grace period (ASG health check grace period, ECS `healthCheckGracePeriodSeconds`).
- NACL between the ALB subnets and the target subnets.

### S5. "S3 Access Denied"
Policy evaluation order: **an explicit Deny anywhere wins → otherwise you need an Allow → otherwise it's an implicit deny.**
1. **The IAM identity policy** of the user or role allows `s3:GetObject` on `arn:aws:s3:::bucket/*`. Note `bucket/*` for objects vs `bucket` for `ListBucket`, which is a common mistake.
2. **The bucket policy** has no Deny (e.g. `aws:SecureTransport`, `aws:SourceVpce`, IP conditions).
3. **Block Public Access** settings, if the access is meant to be public.
4. **KMS:** if the object is SSE-KMS encrypted, the caller also needs `kms:Decrypt` on the key, **and** the key policy must allow it.
5. **Object ownership / ACLs** for cross-account uploads (use "Bucket owner enforced").
6. **An SCP** from AWS Organizations, or a **permission boundary**, can deny it even when IAM allows it.
7. **A VPC endpoint policy**, if the traffic goes through an S3 gateway endpoint.
- **Tools:** `aws sts get-caller-identity` (am I who I think I am?), the **IAM Policy Simulator**, CloudTrail `errorCode: AccessDenied` events, and **IAM Access Analyzer**.

### S6. "The application can't connect to RDS"
1. **Endpoint and port:** use the RDS endpoint DNS name, not an IP. Check the port (3306 MySQL, 5432 Postgres). Test with `nc -zv mydb.xxxx.rds.amazonaws.com 5432`.
2. **RDS SG** inbound on the DB port **from the app's SG** (reference the SG, not IPs).
3. **Same VPC, or peering/TGW routes** in both directions. The DB subnet group sits in private subnets.
4. **Publicly accessible = No** is correct. Access from a laptop goes through a bastion, SSM port forwarding or a VPN.
5. **Credentials:** a wrong password, or a Secrets Manager rotation that changed the password while the app cached the old one.
6. **Max connections reached:** CloudWatch `DatabaseConnections`. Fixes: connection pooling, RDS Proxy.
7. **Status:** in maintenance, storage full (`FreeStorageSpace`), failover happening (Multi-AZ failover takes about 60–120 s; the endpoint stays the same, and the app must reconnect).

### S7. "The site is down after a change" / outage investigation
1. **AWS Health Dashboard:** is it an AWS regional issue?
2. **CloudTrail:** `Event history`, filtered on the time window. Who ran `AuthorizeSecurityGroupIngress` / `RevokeSecurityGroupIngress`, `ReplaceRoute`, `ModifyListener`, `DeleteTargetGroup`, `PutBucketPolicy`?
3. **Mitigate first:** roll back the change (Terraform revert + apply, or restore the previous SG rule).
4. **Then the RCA:** timeline, root cause, why it wasn't caught (no alarm? no review?), action items (Terraform-only changes, an AWS Config rule, an alarm).
- **Say it:** "Restore service first, keep the evidence, and write the RCA after. CloudTrail tells me exactly who changed what, so most 'it suddenly broke' outages are found in minutes."

### S8. "DNS isn't resolving / the domain points to the wrong place"
- `dig app.example.com` and `dig +trace app.example.com`. Check the answer, the TTL and which nameservers responded.
- **The registrar's NS records must match the Route 53 hosted zone's NS records.** A mismatch after recreating a zone is a classic problem.
- An **alias record** to the ALB (free, follows ALB IP changes) vs a CNAME (not allowed at the zone apex).
- **Private hosted zone:** associated with the VPC? The VPC has `enableDnsHostnames` and `enableDnsSupport` on?
- **TTL caching:** clients keep the old answer until the TTL expires. Lower the TTL before a migration.
- **Hybrid DNS:** Route 53 Resolver inbound/outbound endpoints and forwarding rules for on-prem domains.

### S9. "HTTPS certificate error / certificate expired"
- **ACM certificates** renew automatically only if DNS validation (the CNAME record) is still in place. Email validation needs someone to click the link.
- The certificate must be **in the same region as the ALB**. For CloudFront it must be in **us-east-1**.
- The domain names on the certificate must match the host (`*.example.com` doesn't cover `example.com` or `a.b.example.com`).
- Check from the client: `openssl s_client -connect app.example.com:443 -servername app.example.com | openssl x509 -noout -dates -subject`.
- **Prevent it:** CloudWatch alarm on the ACM `DaysToExpiry` metric, or AWS Config `acm-certificate-expiration-check`. Your Koko resume mentions SSL renewals, so tell that story.

### S10. "High CPU / instance slow / instance unreachable"
- CloudWatch `CPUUtilization`. For **T-series instances**, check `CPUCreditBalance`: at 0 the instance gets throttled to its baseline, so either switch to unlimited mode or a non-burstable type.
- **Memory and disk aren't default EC2 metrics.** You need the **CloudWatch agent** for `mem_used_percent` and `disk_used_percent`. Interviewers like this point.
- On the box: `top`, `free -h`, `df -h`, `iostat`, and EBS metrics (`VolumeQueueLength`, burst balance on gp2).
- Status check failing: system → stop/start; instance → check the system log and serial console.
- **Fix:** right-size, Auto Scaling, move to gp3, find the runaway process.

### S11. "Lambda / ECS / EKS can't reach something" (short answers)
- **Lambda in a VPC** has no internet unless its subnets route to a NAT gateway (Lambda never gets a public IP). Check the Lambda's SG and the execution role permissions.
- **ECS task stuck in PENDING / can't pull the image:** needs a route to ECR (NAT or the ECR API + DKR + S3 endpoints), and the **task execution role** must have ECR pull permissions.
- **EKS pod can't reach AWS APIs:** IRSA / Pod Identity role and trust policy; VPC CNI out of IPs (`InsufficientFreeAddressesInSubnet`).

### S12. "Two VPCs can't talk" (peering / Transit Gateway)
- **Overlapping CIDRs can't peer.** Plan non-overlapping ranges.
- The peering connection must be **accepted**.
- **Routes on both sides** pointing to `pcx-…` (or the TGW attachment, plus TGW route tables).
- SGs referencing the other VPC's CIDR (cross-VPC SG references work only for peering in the same region).
- **Peering isn't transitive:** A↔B and B↔C doesn't give A↔C. Use a Transit Gateway for hub-and-spoke.

### S13. "Unexpected cost spike" (bonus, your FinOps strength)
- Cost Explorer grouped by service, then usage type. Common causes: NAT gateway data processing, cross-AZ transfer, forgotten resources (unattached EBS volumes, old snapshots, idle load balancers, unused Elastic IPs), logs never expiring.
- **Prevent it:** AWS Budgets alerts, cost allocation tags, CUR + QuickSight dashboards (your resume), Cost Anomaly Detection.

---

## 2. Security group vs NACL (asked in almost every AWS interview)

| | Security group | NACL |
|---|---|---|
| Level | Instance / ENI | Subnet |
| State | **Stateful**: replies allowed automatically | **Stateless**: you must allow the return traffic (ephemeral 1024–65535) |
| Rules | Allow only | Allow **and** Deny |
| Evaluation | All rules together | In **number order**; the first match wins |
| Default | Deny all inbound, allow all outbound | Default NACL allows all; a custom NACL denies all until you add rules |
| Use | Main access control | Coarse subnet guardrail, e.g. block a bad IP range |

## 3. Logs and monitoring you'll be asked about

| Tool | Answers | Example |
|---|---|---|
| **CloudWatch metrics + alarms** | Is it healthy right now? | ALB `UnHealthyHostCount` > 0 for 2 min → SNS → on-call |
| **CloudWatch Logs + Logs Insights** | What did the app say? | `fields @timestamp, @message \| filter @message like /ERROR/ \| sort @timestamp desc \| limit 50` |
| **CloudTrail** | **Who** did **what**, **when**, from where (API calls) | Who deleted the SG rule at 14:02? |
| **VPC Flow Logs** | Did traffic reach the ENI, and was it ACCEPTed or REJECTed? | `REJECT` on port 5432 means an SG/NACL is blocking the DB |
| **ALB access logs** | Every request: client, target, status codes, latency | Find which target returns the 502s |
| **AWS Config** | What did this resource look like at any point; rule compliance | "SG allowed 0.0.0.0/0 on port 22" → non-compliant |
| **AWS Health Dashboard** | Is AWS itself having a problem? | Regional EC2 issue |
| **Reachability Analyzer** | Can A reach B, and which hop blocks it? | EC2 → RDS: blocked by the SG of RDS |

**Flow log line (default format), know how to read it:**
`2 123456789012 eni-0a1b 10.0.1.15 10.0.2.20 49152 5432 6 10 840 1699999999 1700000059 REJECT OK`
In order: version, account, ENI, **source IP**, **destination IP**, source port, **destination port**, protocol (6 = TCP), packets, bytes, start, end, **action**, log status. This line means 10.0.1.15 tried to reach Postgres on 10.0.2.20 and was blocked.

## 4. Networking protocols (the "good to have" line)

- **TCP 3-way handshake:** SYN → SYN-ACK → ACK. Closing uses FIN/ACK; RST means refused (port closed). "Connection refused" means you reached the host but nothing is listening. "Timeout" means something dropped the packets (SG/NACL/firewall/route).
- **DNS resolution:**
  1. Browser cache → OS cache → the resolver (in a VPC: base + 2).
  2. The root servers point to the TLD (.com), which points to the authoritative nameservers (Route 53), which return the A record.
  3. The answer is cached for its TTL.
  - Record types: A, AAAA, CNAME, MX, TXT, NS, SOA, plus alias (Route 53).
- **DHCP, the 4 steps "DORA":** **D**iscover (client broadcast) → **O**ffer (server offers an IP) → **R**equest (client asks for it) → **A**cknowledge (lease confirmed). **In AWS:** the VPC provides DHCP automatically, and a **DHCP option set** configures the domain name, DNS servers (e.g. on-prem AD DNS) and NTP for the VPC.
- **HTTP vs HTTPS:** HTTPS = HTTP over TLS on port 443. The TLS handshake:
  1. ClientHello
  2. ServerHello + certificate
  3. Key exchange
  4. Encrypted session
  - The certificate proves the server's identity: it's signed by a trusted CA, and the name must match.
- **Status codes:** 2xx success, 3xx redirect, 4xx client error (401 unauthenticated, 403 forbidden, 404 not found, 429 too many requests), 5xx server error (500, 502, 503, 504, as in S3).

## 5. Terraform (working knowledge, 30 min tomorrow morning)

- **Workflow:** `init` → `fmt`/`validate` → `plan` (review!) → `apply`; `destroy` only for test environments.
- **State:** maps your code to real resource IDs. Keep it **remote in S3 with versioning and encryption**, with **DynamoDB locking** (or S3 native locking with `use_lockfile` in newer versions), so two people can't apply at the same time and corrupt it. Never edit it by hand. Use `terraform state list/show/mv/rm`.
- **Drift:** someone changed a resource in the console. `terraform plan` shows the difference. Either revert it with apply, or update the code to match.
- **Import an existing resource:** an `import` block (Terraform 1.5+) or `terraform import aws_instance.web i-0abc…`, then write the matching code until `plan` shows no changes.
- **Modules, variables, outputs, `for_each` vs `count`,** data sources, and one directory or workspace per environment.
- **Troubleshooting:**
  - `Error acquiring the state lock`: someone else is running it, or a crash left the lock behind. Check first, then `terraform force-unlock <ID>`.
  - `AccessDenied` from the provider: check the role or profile with `aws sts get-caller-identity`.
  - Dependency problems: add a `depends_on`.
  - Set `TF_LOG=DEBUG` for detailed logs.
- **Your story:** "I provisioned EKS clusters and the AWS infrastructure (VPC, EC2, RDS, Route 53, ELB, ASG) with Terraform modules at Perfios and Koko."

## 6. Your answers for this role

- **Intro (AWS version):** "I'm an SRE with about five and a half years in AWS production operations. Day to day I troubleshoot and run AWS infrastructure: EKS, EC2, VPC networking, load balancers, RDS and IAM. I provision it with Terraform and monitor it with Prometheus, Grafana and CloudWatch. At Koko Networks I handled production incidents and RCAs, EKS upgrades, SSL renewals and a Docker Swarm to EKS migration. Before that, at Perfios, I built AWS infrastructure with Terraform and Ansible. Troubleshooting production issues is the part of the job I'm strongest at, which is why this role fits."
- **Ratings (be honest):** AWS 7, Linux 6–7, Terraform 7, networking 6. Windows: "mainly Linux; Windows only basics." It isn't on your resume, so don't claim it.
- **Certification question:** "I've completed AWS Cloud Practitioner Essentials training and AWS partner accreditations; I'm planning the Solutions Architect Associate." **Don't call the course a certification.**
- **Why this role:** "My strongest work has been troubleshooting AWS production issues: connectivity, load balancers, outages and RCAs. This role is exactly that, full-time, across many environments, so I'd learn faster and contribute from day one."
- **Prepare 2 real stories** (only real ones):
  1. An outage or connectivity issue you debugged at Koko or Perfios: the symptom, how you found the layer, the fix, and what you added afterwards.
  2. An SSL renewal or EKS upgrade that you planned or rescued.

## 7. Questions to ask them

1. What kinds of incidents take most of the team's time: networking, IAM, or application-level?
2. Is the environment managed with Terraform end to end, or is there console drift you're cleaning up?
3. How is on-call organised, and what does a typical escalation look like?

## 8. Morning self-test (say each answer out loud in under 2 minutes)

1. Private EC2 can't reach the internet. Walk me through it.
2. ALB returns 503. What does that mean, and what do you check?
3. ELB 5xx vs Target 5xx?
4. S3 Access Denied, but the IAM policy allows it. What else could deny it?
5. App can't connect to RDS. Your steps?
6. Security group vs NACL?
7. How do you find who changed a security group yesterday?
8. Read a VPC Flow Log line with REJECT on port 5432.
9. Connection refused vs connection timeout?
10. What is DHCP DORA, and what is a DHCP option set in AWS?
11. Why is Terraform state remote and locked? How do you fix a stuck lock?
12. How do you monitor memory on EC2?
