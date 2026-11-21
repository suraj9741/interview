# DevOps / SRE interview questions with answers (real rounds, Nov 2026)

These questions were asked in four real interview rounds in November 2026 for DevOps, SRE and AWS admin roles (4–8 years of experience). They're grouped by topic. Each answer is short enough to say in about 30 to 60 seconds.

**Rounds:** SRE face-to-face (11 Nov) · AWS Admin round 1 (13 Nov) · AWS Admin L2 "DevOps Networking" (19 Nov) · Senior SRE, Kentik (19 Nov).

**How to use it:** cover the answer, say or type yours first, then check. Reading alone doesn't stick.

---

## Contents
1. [Linux and shell scripting](#1-linux-and-shell-scripting)
2. [SQL](#2-sql)
3. [Networking](#3-networking)
4. [AWS](#4-aws)
5. [Kubernetes](#5-kubernetes)
6. [Docker](#6-docker)
7. [Terraform](#7-terraform)
8. [Monitoring and observability](#8-monitoring-and-observability)
9. [CI/CD, GitOps and Git](#9-cicd-gitops-and-git)
10. [Incidents and behavioural](#10-incidents-and-behavioural)

---

## 1. Linux and shell scripting

**1.1 Name some Linux commands you use daily.** *(11 Nov)*
Group them so it sounds organised:
- **files:** `ls cd cp mv rm find`
- **text:** `cat less grep sed awk sort uniq wc head tail`
- **processes:** `ps top kill systemctl journalctl`
- **disk:** `df du lsof`
- **network:** `ss curl dig ping traceroute`
- **permissions:** `chmod chown`

**1.2 Find lines containing "error" or "info" in a log file.** *(11 Nov)*
```bash
grep -Ei 'error|info' app.log
```
`-E` is needed for `|` (alternation), and `-i` ignores case. Useful extras: `-c` counts, `-n` shows line numbers, `-v` excludes.

**1.3 Replace "error" with "success" in a file.** *(11 Nov)*
```bash
sed -i 's/error/success/g' app.log      # -i.bak keeps a backup
```
`s` = substitute, `g` = every match on the line. Run it without `-i` first to preview the result.

**1.4 Find files in a folder older than 60 days (and delete them).** *(11 Nov)*
```bash
find /var/log/app -type f -mtime +60            # list
find /var/log/app -type f -mtime +60 -delete    # delete
```
`-mtime +60` = modified more than 60 days ago; `-mtime -1` = within the last day.

**1.5 How do you list all processes running on the system?** *(Kentik, 19 Nov)*
`ps aux` or `ps -ef` for everything; `top` / `htop` for a live view sorted by CPU or memory; `pgrep -a nginx` to find one by name.

**1.6 Run a script, but if someone already ran it within the last hour, it must not run again.** *(L2, 19 Nov)*
Use a timestamp file for "less than an hour ago" and `flock` so two copies can't run at the same time:
```bash
#!/usr/bin/env bash
set -euo pipefail
STAMP=/var/tmp/myjob.last_run
LOCK=/var/tmp/myjob.lock

exec 9>"$LOCK"
flock -n 9 || { echo "Already running"; exit 0; }

if [[ -f "$STAMP" ]] && (( $(date +%s) - $(stat -c %Y "$STAMP") < 3600 )); then
  echo "Ran less than an hour ago, exiting"; exit 0
fi

echo "Running the job..."     # real work here
touch "$STAMP"                # record success only at the end
```

**1.7 A shell script fails at line 10 but keeps running. How do you make it stop there?** *(L2, 19 Nov)*
```bash
set -euo pipefail
trap 'echo "Error on line $LINENO: $BASH_COMMAND" >&2' ERR
```
- `-e`: exit on the first failing command.
- `-u`: an unset variable is an error.
- `pipefail`: a pipeline fails if any part of it fails.

For a single command: `cmd || exit 1`. Note that `set -e` doesn't trigger inside `if` conditions or on the left side of `&&` / `||`.

**1.8 Write a script that alerts when any filesystem is above 80% full.** *(practice question, not asked in these rounds)*
```bash
#!/usr/bin/env bash
set -euo pipefail
THRESHOLD="${1:-80}"; status=0
while read -r fs size used avail pct mount; do
  usage="${pct%\%}"
  if (( usage >= THRESHOLD )); then echo "ALERT: $mount at ${usage}%"; status=1; fi
done < <(df -P -x tmpfs -x devtmpfs | tail -n +2)
exit $status
```
`< <(...)` feeds the loop without a pipe. With a pipe, the loop runs in a subshell and `status=1` would be lost.

**1.9 Describe a shell automation you've written.** *(Kentik, 19 Nov)*
Example answer: "A daily RDS backup script, run from Jenkins, that uses the AWS CLI to take a snapshot (`aws rds create-db-snapshot`) and deletes snapshots older than 7 days." Mention scheduling, logging and alerting on failure.

---

## 2. SQL

**2.1 What are DML commands?** *(11 Nov)*

| Family | Commands |
|---|---|
| DDL (definition) | `CREATE ALTER DROP TRUNCATE` |
| **DML (manipulation)** | **`INSERT UPDATE DELETE MERGE`** |
| DQL (query) | `SELECT` |
| DCL (control) | `GRANT REVOKE` |
| TCL (transactions) | `COMMIT ROLLBACK SAVEPOINT` |

**2.2 Write an INSERT and a DELETE.** *(11 Nov)*
```sql
INSERT INTO users (id, name, city) VALUES (1, 'Asha', 'Pune');
DELETE FROM users WHERE id = 1;   -- without WHERE it deletes every row
```
In production, run a `SELECT` with the same `WHERE` first, inside a transaction, so you can `ROLLBACK`.

**2.3 DELETE vs TRUNCATE vs DROP.**
- `DELETE` removes chosen rows (DML, can be rolled back).
- `TRUNCATE` removes all rows quickly and keeps the table.
- `DROP` removes the table itself.

---

## 3. Networking

**3.1 Explain the TCP 3-way handshake.** *(13 Nov)*
- **Open:** SYN → SYN-ACK → ACK. Each side sends its starting sequence number and confirms the other's.
- **Close:** FIN/ACK in each direction (4 packets). The side that closes first waits in TIME_WAIT.
- **Troubleshooting:** "connection refused" = RST (the host was reached, but the port is closed). "Timed out" = no reply (a firewall or SG dropped it, or a routing problem).

**3.2 What checks do you do for a DNS resolution problem? What does `dig` show vs `traceroute`?** *(13 Nov)*
- `dig name` shows the DNS answer: records, **TTL**, status (NOERROR / NXDOMAIN / SERVFAIL) and which server answered.
- `dig @8.8.8.8 name` asks a specific resolver.
- `dig +trace name` shows the chain: root → TLD → authoritative servers.
- `traceroute` shows the **network hops** to an IP. It has nothing to do with DNS.

Also check: the NS records at the registrar, a public vs private hosted zone, TTL caching, and `/etc/hosts`.

**3.3 Difference between `dig www.google.com` and `dig www.google.com.` (trailing dot).**
The trailing dot makes it a fully qualified name ending at the DNS root, so no search domains are appended. `dig` ignores the search list anyway, so the output is the same. It matters in Kubernetes: with `ndots:5`, a name without the dot tries every cluster search domain first.

**3.4 traceroute shows `* * *` for many hops and runs to 30. Why?**
Those routers don't reply to probes (they drop or rate-limit ICMP "time exceeded"), or a firewall drops Linux traceroute's default **UDP probes (ports 33434+)**. That isn't packet loss. Use `traceroute -T -p 443` (TCP probes), `mtr`, and `curl` / `nc` to test the actual service.

**3.5 OSI layers, and where does a Network Load Balancer sit?** *(L2, 19 Nov)*

| Layer | Example |
|---|---|
| 7 Application | HTTP, DNS → **ALB**, WAF |
| 4 Transport | TCP/UDP ports → **NLB**, SG/NACL port rules |
| 3 Network | IP, routing, route tables |
| 2 Data link | Ethernet, ARP, MAC |

The NLB is **layer 4**: it balances TCP/UDP/TLS by IP and port using a flow hash, gives a **static IP per AZ**, preserves the client IP, and handles millions of requests per second. It can't route by URL path; that needs an ALB (layer 7).

**3.6 CIDR: AWS reserved IPs vs a normal network.**
- A normal subnet reserves 2 addresses (network and broadcast), so a /24 has 254 usable.
- AWS reserves 5: network, .1 the VPC router, .2 DNS, .3 future use, and the last address. So a /24 has **251** usable and a /28 has 11.
- Formula: 2^(32 − prefix).

---

## 4. AWS

**4.1 Explain your VPC architecture.** *(13 Nov)*
One public and one private subnet **per AZ**, across at least 2 AZs. The ALB and NAT gateways go in the public subnets; apps and EKS nodes in the private subnets; RDS in private DB subnets. **An ALB needs subnets in at least 2 AZs**, so "one public subnet with an ALB" is wrong. Use one NAT per AZ for high availability.

**4.2 Difference between a private and a public subnet.** *(L2, 19 Nov)*
Only the **route table**: public = `0.0.0.0/0 → Internet Gateway` (and instances need a public IP to be reachable); private = `0.0.0.0/0 → NAT gateway` (outbound only, nothing can connect in).

**4.3 Security group vs NACL.** *(13 Nov)*

| | Security group | NACL |
|---|---|---|
| Level | Instance / ENI | Subnet |
| State | **Stateful** (replies allowed automatically) | **Stateless** (allow ephemeral ports 1024–65535 for replies) |
| Rules | Allow only | Allow and deny, evaluated in rule-number order |
| References | Other SGs | CIDRs only |

**4.4 A private EC2 instance can't reach the internet. What do you check?** *(13 Nov)*
This is **outbound** traffic, so follow the path out:
1. The private route table has `0.0.0.0/0 → NAT gateway`.
2. The NAT sits in a **public** subnet whose route table points to the IGW, has an Elastic IP, and is Available.
3. SG outbound rules.
4. NACLs (outbound 80/443, inbound ephemeral ports).
5. DNS.

Prove it with VPC Flow Logs (REJECT = SG/NACL) and Reachability Analyzer. For S3 only, a gateway endpoint is cheaper than NAT.

**4.5 An EC2 instance can't connect to RDS. What do you check?** *(13 Nov)* / **A private EC2 needs to connect to RDS: what are the steps?** *(L2, 19 Nov)*
- **Setup:** RDS in private DB subnets (2+ AZs, not public); RDS SG allows 5432/3306 **from the EC2's security group**; same VPC so the `local` route works; credentials in Secrets Manager.
- **Debug:** `nc -zv <endpoint> 5432`. Timeout = network (SG, NACL, routing, DNS resolving to the wrong IP); connects but login fails = auth (password, IAM auth, SSL). Also check `max_connections`.

**4.6 The ALB returns 502 / 503 / 504. What does each mean, and what do you check?** *(13 Nov)*
- **502:** the target sent an invalid response or reset the connection (app crashed, wrong port, keep-alive timeout shorter than the ALB's).
- **503:** **no registered targets** in the target group. If targets are registered but all unhealthy, the ALB fails open, so you usually see 502/504 instead.
- **504:** the target didn't answer within the idle timeout (60 s): slow app or DB, or an SG silently dropping traffic.
- **Split the cause** with `HTTPCode_ELB_5XX` vs `HTTPCode_Target_5XX`, and ALB access logs (`target_status_code`).

**4.7 The application is running slow. How do you troubleshoot?** *(13 Nov)*
1. **Scope it:** who, where, since when. Check what changed (deploys, CloudTrail).
2. **Find the slow layer** with `curl -w` timings: DNS / connect / TLS / server.
3. **Look at RED metrics** (rate, errors, p95/p99 latency) and **traces** to find the slow service.
4. **Database:** slow queries, connection pool, locks.
5. **Infrastructure:** CPU / memory / disk I/O, CPU throttling in Kubernetes.
6. **Mitigate first** (scale out, roll back), then fix the root cause.

**4.8 How do you create a Route 53 record for an ALB? Alias vs CNAME?** *(L2, 19 Nov)*
- **Steps:** hosted zone → Create record → type **A**, Alias on → "Alias to Application and Classic Load Balancer" → region → the ALB.
- **Alias vs CNAME:** an Alias works at the zone apex (`example.com`), follows the ALB's changing IPs, and queries to AWS targets are free. A CNAME can't be used at the apex.

**4.9 EC2 reads from S3 with the role already configured. Explain the full flow.** *(L2, 19 Nov)*
1. The role is attached through an **instance profile**.
2. The SDK gets **temporary STS credentials** from instance metadata (IMDSv2: get a token, then read the credentials).
3. The request is signed (SigV4) and sent over HTTPS.
4. From a private subnet it goes via a **gateway VPC endpoint** (or NAT).
5. S3 checks the IAM policy, bucket policy, endpoint policy and KMS key policy. An explicit Deny wins.

**4.10 You have 100 EC2 instances and need to push code or copy an image to all of them. What strategy?** *(L2, 19 Nov)*
- **One-off:** **SSM Run Command** targeted by tag, with rate control (for example 10% at a time, stop on errors), pulling from S3/ECR. Alternatives: Ansible or CodeDeploy.
- **Long term (immutable):** bake a new **AMI** (Packer / EC2 Image Builder) and roll it out with an Auto Scaling group **instance refresh**.

**4.11 How do you add an SSL certificate to a WordPress site with ACM?**
Standard ACM certificates can't be installed on the server itself. Put the site behind an **ALB**:
1. Request the ACM certificate with DNS validation.
2. Add an HTTPS 443 listener with the certificate, and redirect 80 to 443.
3. Point an Alias record at the ALB.
4. In `wp-config.php`, trust `X-Forwarded-Proto` and set the site URL to https.

ACM then renews automatically. Imported (paid) certificates **don't** auto-renew.

---

## 5. Kubernetes

**5.1 Explain the Kubernetes architecture / components.** *(11 Nov, Kentik 19 Nov)*
- **Control plane:**
  - **kube-apiserver:** the front door; the only component that talks to etcd.
  - **etcd:** cluster state.
  - **scheduler:** filters, then scores nodes.
  - **controller-manager:** control loops for Deployments, ReplicaSets, nodes, jobs.
  - **cloud-controller-manager:** load balancers and nodes in the cloud.
- **Worker node:**
  - **kubelet:** runs pods and reports their status.
  - **kube-proxy:** Service rules.
  - **containerd:** the container runtime.
  - **CNI:** gives pods their IPs.

**5.2 What happens when a pod starts?** *(11 Nov)*
1. The API server validates the pod and saves it to etcd (Pending).
2. The scheduler filters, scores and binds it to a node.
3. The kubelet then:
   - mounts volumes and Secrets
   - creates the pause sandbox
   - gets an IP from CNI
   - pulls the image
   - runs init containers, then the app containers
4. Probes run.
5. Once **Ready**, the pod is added to the Service's EndpointSlice and starts getting traffic.

**5.3 A pod isn't running. How do you debug it?** *(Kentik, 19 Nov)*
`kubectl get pods` → `kubectl describe pod` (read the **Events**) → `kubectl logs <pod> --previous`.

| Status | Usual cause |
|---|---|
| Pending | Scheduling problem |
| ImagePullBackOff | Wrong image tag or registry auth |
| CrashLoopBackOff | The app exits on start (check the logs) |
| OOMKilled (exit 137) | Memory limit exceeded |
| Running 0/1 | Readiness probe failing |

**5.4 A pod is Pending even though CPU and memory are fine. What do you check?** *(L2, 19 Nov)*
Run `kubectl describe pod` and read the FailedScheduling event. If it isn't resources, it's usually one of these:
- taints the pod doesn't tolerate
- a nodeSelector or affinity that matches no node
- an **unbound PVC**, or an EBS volume in another AZ
- anti-affinity or topology spread rules that can't be met
- the **per-node pod/IP limit on EKS**
- nodes cordoned or NotReady

**5.5 Pods can't be scheduled because of insufficient resources. What's the fix?** *(Kentik, 19 Nov)*
- Check requests against node allocatable: `kubectl describe node`.
- Right-size the requests.
- Make sure **Cluster Autoscaler / Karpenter** adds nodes (it only reacts to Pending pods) and the ASG max isn't reached.
- Look for a memory leak or a traffic spike behind runaway HPA scaling.

**5.6 Node affinity vs taints and tolerations.** *(L2, 19 Nov)*
- **Affinity** is set on the pod and **attracts** it to labelled nodes (required or preferred).
- A **taint** is set on the node and **repels** pods; a **toleration** lets a pod ignore that taint.
- A toleration *allows* placement on the node but doesn't *force* it. For dedicated nodes, use both.

**5.7 Liveness vs readiness probe.** *(Kentik, 19 Nov)*
- **Readiness fails** → the pod is removed from Service endpoints (no traffic), **not restarted**.
- **Liveness fails** → the container is **restarted**.
- A **startup** probe protects slow-booting apps from being killed during startup.
- Never check the database in a liveness probe.

**5.8 Deployment vs StatefulSet vs DaemonSet.** *(Kentik, 19 Nov)*
- **Deployment:** stateless apps, random pod names.
- **StatefulSet:** stable names (`db-0`, `db-1`), ordered start, **its own PVC per pod** via volumeClaimTemplates. Used for databases, Kafka, Redis.
- **DaemonSet:** one pod on every node. Used for log agents, node exporters, CNI.

**5.9 Replicas = 3 and you delete one pod. What happens?** *(Kentik, 19 Nov)*
The **ReplicaSet immediately creates a replacement** to get back to the desired count. HPA only changes what the desired count is; a deleted pod is always replaced.

**5.10 How do you update an app's image (for example to 1.7)?** *(Kentik, 19 Nov)*
- **GitOps:** a PR changes the image tag in Git, ArgoCD syncs it, test in dev first.
- **Plain kubectl:** `kubectl set image deploy/web web=app:1.7`, then `kubectl rollout status`, and `kubectl rollout undo` to roll back.

**5.11 What is a rolling update?** *(Kentik, 19 Nov)*
New pods start and must pass readiness before old ones are removed. `maxSurge` = extra pods allowed during the rollout; `maxUnavailable` = pods allowed to be down. `maxUnavailable: 0` means capacity never drops.

**5.12 ConfigMap vs Secret, and how do you use them?** *(Kentik, 19 Nov)*
- A ConfigMap holds non-secret config; a Secret holds credentials. **Secrets are only base64-encoded, not encrypted.** Use External Secrets with AWS Secrets Manager.
- Use either as **environment variables** (`envFrom` / `valueFrom`) **or** as mounted files (volumes).

**5.13 What is a PV / PVC and why use it?** *(Kentik, 19 Nov)*
- A pod's filesystem is lost when the pod is deleted. A **PVC** requests storage; a **PV** is the actual disk (for example EBS), often created dynamically by a StorageClass. The data survives pod restarts.
- **Expanding a volume:** the StorageClass needs `allowVolumeExpansion: true`; then raise `spec.resources.requests.storage` on the PVC. The EBS CSI driver grows it online. You can't shrink a volume.

**5.14 A StatefulSet has a PV attached and you change the PV's name. What happens?** *(L2, 19 Nov)*
A PV **can't be renamed**: applying a new name creates a **second** PV, which stays Available, while the PVC stays bound to the old PV by name and the pod keeps the old data. Deleting the old PV while it's in use leaves it stuck in Terminating (protection finalizer). A StatefulSet's `volumeClaimTemplates` are immutable. To really move data: snapshot, then restore into a new PVC.

**5.15 How do worker nodes autoscale?** *(Kentik, 19 Nov)*
The ASG (desired / min / max) alone doesn't react to pods. **Cluster Autoscaler** (adjusts the ASG) or **Karpenter** (launches the best-fit instance directly) adds nodes when pods are Pending, and removes underused nodes.

**5.16 Upgrade Kubernetes from an older version to the latest. What's the process?** *(L2, 19 Nov)*
- **One minor version at a time.** For each hop:
  1. Find removed APIs (EKS upgrade insights, `pluto` / `kubent`).
  2. Check add-on compatibility.
  3. Back up (Velero).
  4. Test in non-prod.
  5. Upgrade the **control plane**, then the **nodes** (rolling, with PodDisruptionBudgets), then the **add-ons** (VPC CNI, CoreDNS, kube-proxy).
  6. Verify.
- Nodes can be up to 3 minor versions older than the control plane, but never newer.

**5.17 How do you see the logs of an application running in a pod?** *(Kentik, 19 Nov)*
```bash
kubectl logs <pod> -n <ns>
kubectl logs <pod> -n <ns> -f                # follow live
kubectl logs <pod> -n <ns> --previous        # logs from the crashed container
kubectl logs <pod> -n <ns> -c <container>    # pick one container in the pod
```

---

## 6. Docker

**6.1 You have a running image and want to add updated files on top, then test it. How?** *(Kentik, 19 Nov)*
```dockerfile
FROM myapp:1.0
COPY ./updated/ /app/
RUN pip install -r /app/requirements.txt     # if needed
CMD ["python", "/app/main.py"]
```
Then `docker build -t myapp:1.1 .` and `docker run --rm -p 8080:8080 myapp:1.1`, and test.

**6.2 How did you make Docker images smaller and more secure?** *(Kentik, 19 Nov)*
- A **multi-stage build:** build in a full image, then copy only the app and its dependencies into a slim runtime image (python-slim, distroless, alpine). Example: 1 GB → about 100 MB.
- A **`.dockerignore`** keeps `.git` and test files out.
- Run as a non-root user, pin versions, and scan the image (Trivy).

---

## 7. Terraform

**7.1 What is the state file, and why remote and locked?** *(13 Nov)*
- **State** maps your code to real resource IDs, so `plan` can compute the difference.
- **Remote** (an S3 bucket with versioning and encryption) so the team shares one copy.
- **Locked** (`use_lockfile = true`, or DynamoDB) so two `apply` runs can't corrupt it.

**7.2 plan vs apply.** *(13 Nov)*
- `plan` refreshes and shows what will change, but changes nothing. Save it with `-out=tfplan`.
- `apply` makes the changes. `apply tfplan` applies exactly the reviewed plan.

**7.3 Write the Terraform for an EC2 instance.** *(L2, 19 Nov)*
```hcl
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = "t3.micro"
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.sg_id]
  iam_instance_profile   = var.instance_profile_name
  metadata_options { http_tokens = "required" }   # IMDSv2
  tags = { Name = "web-1" }
}
```

**7.4 Write an S3 bucket with versioning, plus the S3 backend.** *(13 Nov)*
```hcl
terraform {
  backend "s3" {
    bucket       = "my-tf-state"
    key          = "prod/app/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true
  }
}
resource "aws_s3_bucket" "logs" { bucket = "my-logs-2026" }
resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration { status = "Enabled" }
}
```
Since AWS provider v4, versioning is its own resource.

**7.5 Which parameters do you set when creating RDS with Terraform?** *(Kentik, 19 Nov)*
- **Core:** `engine`, `engine_version`, `instance_class`, `allocated_storage` / `storage_type`.
- **Network:** `db_subnet_group_name`, `vpc_security_group_ids`, `multi_az`, `publicly_accessible = false`.
- **Safety:** `storage_encrypted`, `backup_retention_period`, `deletion_protection`.
- **Credentials:** `manage_master_user_password = true` (stored in Secrets Manager).
- **Observability:** `enabled_cloudwatch_logs_exports`, `performance_insights_enabled`.

---

## 8. Monitoring and observability

**8.1 What metric types does Prometheus have?** *(Kentik, 19 Nov)*
**Counter** (only goes up: requests), **gauge** (up and down: memory), **histogram** (buckets: latency), **summary**. Metrics, logs and traces are telemetry *signals*, not Prometheus metric types.

**8.2 What have you actually implemented with Prometheus?** *(Kentik, 19 Nov)*
Example answer: "The blackbox exporter probing third-party payment APIs every 30 seconds, with alerts through Alertmanager when they're down, and Grafana dashboards with p50/p90/p99 latency per service."

**8.3 How do you avoid repeated or flapping alerts?** *(Kentik, 19 Nov)*
- `for: 5m` in the rule, so the alert fires only if the condition holds.
- In Alertmanager: `group_by`, `group_wait`, `group_interval` and **`repeat_interval`** (for example 10 min for critical, 30 min for warning).
- Inhibition rules and silences.

**8.4 What do p50 / p90 / p99 mean?** *(Kentik, 19 Nov)*
p99 = **99% of requests finished within this time**, so 1 in 100 was slower. p50 is the median. Percentiles show the slow tail that averages hide.

**8.5 Which logs do you check in a P1 incident?** *(13 Nov)*
- App logs (CloudWatch Logs / Loki)
- ALB access logs (S3)
- CloudTrail (who changed what)
- VPC Flow Logs (network)

Use metrics for scope, logs for detail, and traces to find the slow service.

---

## 9. CI/CD, GitOps and Git

**9.1 How do you deploy with Helm, and is it part of a pipeline?** *(Kentik, 19 Nov)*
A chart with templates (Deployment, Service, HPA, Ingress) plus one values file per service and environment. CI builds and pushes the image and updates the tag in Git; **ArgoCD** syncs the chart to the cluster (GitOps). By hand it's `helm upgrade --install app ./chart -f values-prod.yaml`.

**9.2 Two developers changed the same file. One merged to master; the other gets a merge conflict. How do you resolve it?** *(L2, 19 Nov)*
1. `git fetch origin && git merge origin/master` (or `rebase`).
2. Open the conflicted file, choose or combine between `<<<<<<<` / `=======` / `>>>>>>>`, and delete the markers.
3. Test.
4. `git add <file>`, then `git commit` (or `git rebase --continue`).
5. `git push` (after a rebase, `--force-with-lease`).

`git merge --abort` undoes the attempt. Prevent conflicts with small, short-lived branches.

---

## 10. Incidents and behavioural

**10.1 Introduce yourself / your responsibilities.** *(all rounds)*
Lead with what **you** own, not the company's business: "SRE with X years on AWS; I run production EKS, incidents and RCA, Prometheus/Grafana monitoring, CI/CD." Then 2 or 3 achievements with real numbers.

**10.2 Tell me about a recent high-severity incident you handled.** *(13 Nov)*
Structure: situation → impact (who, how long) → what *you* did step by step → root cause (a process, not "human error") → prevention (alert, automation, runbook) → what you learned. Pick a technical incident, not a billing top-up.

**10.3 Rate yourself out of 10 in X.** *(11 Nov)*
Rate at the level where you can take 10 minutes of follow-up questions without notes. A 9 invites expert-level questions.

**10.4 This is a support role. Why do you want to join?** *(11 Nov)*
Talk about what you bring and why this domain matters ("production reliability is what I enjoy, and here it has real consequences"), never about your own problems (bench, job security).

**10.5 What goes into an RCA / postmortem?**
Impact, a timeline with timestamps, root cause via 5 Whys, what went well and badly, action items with owners and dates, and a blameless tone. Track MTTD and MTTR.
