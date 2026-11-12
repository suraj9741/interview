# 15 days, day by day: tick as you go

Every day has the same shape. Open today's section only, work top to bottom, and tick each box. **Don't read ahead.** The full lesson for each day (with labs and a drill) is written the evening before. Ask in the thread: "Day N lesson".

**Daily shape:**

| Time | Slot |
|---|---|
| 9:00–9:30 | Recall test: yesterday's drill, answers hidden |
| 9:30–12:30 | Block 1 |
| 12:30–13:30 | Lunch, no screens |
| 13:30–16:00 | Block 2 + lab |
| 16:00–16:45 | SQL |
| 16:45–17:00 | AWS slot (on days that have one) or review |
| 17:00–17:30 | Send "Day N quiz" in the thread |
| 17:30–18:00 | Own-words summary + add misses to `misses.md` |

---

## Day 1 · Thu 12 Nov · Linux I

Lesson: [day-01-linux-text-sql-basics.md](day-01-linux-text-sql-basics.md)

- [ ] Setup: Ubuntu container, `bash make-logs.sh`
- [ ] **Block 1:** grep (all flags, `-E` for OR), pipes and redirects (`|`, `>`, `>>`, `2>`, `&&`), find (`-name`, `-mtime +N`, `-size`, `-exec`, `-delete`), sed (`s///g`, `-i.bak`, `-n 'p'`, `/d`)
- [ ] **Block 2:** reading `ls -l`, chmod numbers (644/755/600/640), chown, users and groups (`usermod -aG`), the permission break/fix lab
- [ ] **SQL:** command families, SELECT/WHERE/ORDER BY/LIMIT/LIKE/IN/BETWEEN, NULL trap, safe INSERT/UPDATE/DELETE, DELETE vs TRUNCATE vs DROP
- [ ] **Quiz** + summary
- **Done when:** you can write the 25 drill answers from memory

## Day 2 · Fri 13 Nov · Linux II

- [ ] Recall test: Day 1 drill
- [ ] **Block 1:** processes (`ps aux`, `ps -ef`, `top`, `htop`, `pgrep`), signals (`kill -15` vs `-9`, SIGHUP), foreground/background (`&`, `nohup`, `jobs`), systemd (`systemctl status/start/enable`, unit files), `journalctl -u … --since`, cron syntax, logrotate
- [ ] **Block 2:** resources: `uptime` and load average, `free -h`, `vmstat`, `iostat`, `df -h`, `df -i`, `du -sh`, `lsof +L1`, OOM killer (`dmesg`); awk, sort, uniq, cut, wc, xargs for log analysis
- [ ] **Lab:** break/fix: fill the disk, delete an open file, start a CPU hog, find and fix each one
- [ ] **SQL:** COUNT/SUM/AVG/MIN/MAX, DISTINCT, GROUP BY, HAVING, WHERE vs HAVING
- [ ] **Quiz** + summary
- **Done when:** you can talk through "the server is slow" step by step, and write top-IPs and errors-per-hour one-liners

## Day 3 · Sat 14 Nov · Networking I

- [ ] Recall test: Day 2 (+ Day 1 misses)
- [ ] **Block 1:** OSI vs TCP/IP layers (with an example protocol per layer), IPv4, private ranges, **CIDR and subnet maths on paper** (/16, /20, /24, /28: hosts, network and broadcast addresses), TCP vs UDP, the 3-way handshake, common ports (22, 53, 80, 443, 3306, 5432, 6443)
- [ ] **Block 2:** DNS (A, AAAA, CNAME, MX, TXT, NS; recursive resolution, TTL), HTTP methods and status codes (2xx/3xx/4xx/5xx; what 502/503/504 mean), HTTPS/TLS handshake and certificates; commands: `ip a`, `ip route`, `ss -tlnp`, `curl -v`, `dig`, `nslookup`, `traceroute`, `ping`, `tcpdump -i any port 80`
- [ ] **Lab:** `dig +trace google.com`, `curl -v https://…` (read every line), capture a handshake with tcpdump
- [ ] **SQL:** JOINs (INNER, LEFT, RIGHT, self join), finding rows missing in the other table
- [ ] **Quiz** + summary
- **Done when:** you can split 10.0.0.0/16 into /20s by hand, and explain "what happens when I type a URL" in 3 minutes

## Day 4 · Sun 15 Nov · Networking II + AWS networking

- [ ] Recall test: Day 3
- [ ] **Block 1:** L4 vs L7 load balancing, reverse proxy vs forward proxy, NAT, stateful vs stateless firewalls
- [ ] **AWS:** VPC, public vs private subnets, route tables, IGW, NAT gateway, **security group vs NACL**, VPC endpoints, peering vs Transit Gateway, ALB vs NLB, Route 53 routing policies
- [ ] **Block 2 lab:** Nginx in Docker as a reverse proxy for 2 backends; read the access and error logs; stop a backend and reproduce a 502; `nginx -t` and reload
- [ ] **SQL:** subqueries (IN, EXISTS, correlated), CASE, string and date functions
- [ ] **Quiz** + summary
- **Done when:** you can draw a 3-tier VPC with traffic flow from memory, and explain 502 vs 504

## Day 5 · Mon 16 Nov · Bash scripting & automation

- [ ] Recall test: Day 4
- [ ] **Block 1:** shebang, variables and quoting (`"$var"`), `$1 $# $@ $?`, if/elif, `[[ ]]` tests (`-f -d -z -eq -gt`), case, for/while loops, functions, `read`, reading a file line by line, `set -euo pipefail`, exit codes
- [ ] **Block 2 lab:** write 5 scripts yourself:
  1. Disk usage alert above a threshold
  2. Delete logs older than N days (dry-run flag)
  3. Health check with retry and restart
  4. Database backup with date in the name and keep-last-7 rotation
  5. Server report (CPU, memory, disk, top processes)
- [ ] Schedule two of them with cron and check that they ran
- [ ] **SQL:** DDL: CREATE/ALTER/DROP, constraints (PK, FK, UNIQUE, NOT NULL, CHECK); build a 3-table schema
- [ ] **Quiz** + summary
- **Done when:** you can explain each script line by line, and write the disk-alert script from a blank file

## Day 6 · Tue 17 Nov · Python for automation

- [ ] Recall test: Day 5
- [ ] **Block 1:** types, lists, dicts, loops, functions, reading and writing files, exceptions (try/except), modules: `re`, `json`, `os`, `sys`, `argparse`, `datetime`
- [ ] **AWS:** IAM (users, groups, roles, policies; JSON policy structure, least privilege, instance profiles, AssumeRole); `boto3` to list EC2 instances and S3 buckets (read-only)
- [ ] **Block 2 lab:** log parser that counts errors per hour; an API call with `requests` and its JSON parsed; `subprocess.run` to check a service; rewrite the disk-alert and cleanup scripts in Python
- [ ] **SQL:** window functions: ROW_NUMBER, RANK, DENSE_RANK, LAG/LEAD; dedupe; Nth highest salary
- [ ] **Quiz** + summary
- **Done when:** you can write the log parser from a blank file, and read an IAM policy out loud

## Day 7 · Wed 18 Nov · Git + Mock 1

- [ ] Recall test: Day 6
- [ ] **Block 1:** what a commit, branch and HEAD are; working dir, staging, repo; merge vs rebase (with a diagram); resolving conflicts; reset (`--soft`/`--mixed`/`--hard`) vs revert; cherry-pick; stash; tags; `.gitignore`; GitFlow vs trunk-based; the PR/code review flow; [Learn Git Branching](https://learngitbranching.js.org/)
- [ ] **Lab:** create 3 merge conflicts on purpose and resolve them; undo a bad commit with revert
- [ ] **Block 2: Mock 1** with Claude: Linux, networking, Bash, Python, SQL (45 min). Then redo every miss
- [ ] **SQL:** covered in the mock
- [ ] Summary + update `misses.md`
- **Done when:** mock score ≥ 7/10, and you can explain when to use revert instead of reset

## Day 8 · Thu 19 Nov · Docker

- [ ] Recall test: Day 7 misses
- [ ] **Block 1:** container vs VM (namespaces, cgroups), image vs container, layers and cache order, Dockerfile instructions, CMD vs ENTRYPOINT, COPY vs ADD, **multi-stage builds**, non-root user, slim/distroless bases, `.dockerignore`, image scanning (Trivy)
- [ ] **AWS:** ECR: login, push/pull, lifecycle policies, scan on push
- [ ] **Block 2 lab:** containerise your Day 6 Python app (multi-stage, non-root) and compare image sizes; docker networking (bridge, host, user-defined), volumes vs bind mounts, docker compose with app + DB; troubleshoot with `logs`, `inspect`, `exec` and exit codes
- [ ] **SQL:** transactions, ACID, isolation levels, locks and deadlocks
- [ ] **Quiz** + summary
- **Done when:** you can explain how you cut image size by 30–40% (your resume claim) with your own example

## Day 9 · Fri 20 Nov · Kubernetes I

- [ ] Recall test: Day 8
- [ ] **Block 1:** architecture: kube-apiserver, etcd, scheduler, controller-manager, cloud-controller-manager, kubelet, kube-proxy, container runtime, CNI; **the pod startup flow** (the 11 Nov question); pod phases
- [ ] **Block 2 lab:** `kind` cluster; deploy your Day 8 image as a Deployment; watch `kubectl get events -w` during a rollout; scale, `rollout status`, `rollout undo`, `rollout history`
- [ ] **SQL:** indexes, `EXPLAIN`, slow-query troubleshooting
- [ ] **Quiz** + summary
- **Done when:** you can draw the architecture and explain pod startup in 2 minutes with no notes

## Day 10 · Sat 21 Nov · Kubernetes II

- [ ] Recall test: Day 9
- [ ] **Block 1:** Services (ClusterIP, NodePort, LoadBalancer, headless), endpoints, kube-proxy, CoreDNS names, Ingress and IngressClass; ConfigMaps and Secrets; liveness/readiness/startup probes; requests vs limits and QoS classes; HPA
- [ ] **AWS:** EKS: managed node groups vs Karpenter, VPC CNI and IP exhaustion, IRSA / Pod Identity, AWS Load Balancer Controller, EBS CSI driver
- [ ] **Block 2 lab:** expose your app through a Service and Ingress; add probes and limits; mount a ConfigMap; set up an HPA; a simple RBAC Role + RoleBinding, checked with `kubectl auth can-i`
- [ ] **SQL:** data-validation queries (duplicates, NULLs, source vs target counts, missing rows)
- [ ] **Quiz** + summary
- **Done when:** you can explain why a Service can have empty endpoints, and how a pod gets S3 access without keys

## Day 11 · Sun 22 Nov · Kubernetes III: troubleshooting + Helm

- [ ] Recall test: Day 10
- [ ] **Block 1:** break/fix on Killercoda: CrashLoopBackOff, Pending, ImagePullBackOff, OOMKilled, readiness failing, CreateContainerConfigError, PVC Pending, node NotReady, stuck rollout
- [ ] **Block 2:** Helm (chart structure, values, install/upgrade/rollback, `helm template`); prepare your **Docker Swarm → EKS migration** story (why, how, environments, cutover, problems, results)
- [ ] **SQL:** GRANT/REVOKE, backups (`mysqldump`, `pg_dump`), restore, RDS snapshots and point-in-time recovery
- [ ] **Quiz** + summary
- **Done when:** you've fixed 10 broken scenarios and can tell the migration story in 3 minutes

## Day 12 · Mon 23 Nov · CI/CD

- [ ] Recall test: Day 11
- [ ] **Block 1:** CI vs continuous delivery vs continuous deployment; pipeline stages (build, test, scan, push, deploy); Jenkins (Jenkinsfile, declarative pipeline, agents, credentials), GitLab CI (`.gitlab-ci.yml`, stages, runners), GitHub Actions (workflows, jobs, runners, secrets)
- [ ] **AWS:** CodePipeline/CodeDeploy at concept level; Secrets Manager and Parameter Store in pipelines
- [ ] **Block 2:** GitOps with ArgoCD (sync, self-heal, rollback by `git revert`); deployment strategies (rolling, blue-green, canary); your Jenkins → ArgoCD story (10 → 2 minutes)
- [ ] **Lab:** a GitHub Actions pipeline that tests, builds and pushes your Day 8 image
- [ ] **SQL:** MySQL vs PostgreSQL basics, connection pooling, replication, RDS Multi-AZ vs read replicas
- [ ] **Quiz** + summary
- **Done when:** you can draw your Koko pipeline before and after ArgoCD, and explain canary vs blue-green

## Day 13 · Tue 24 Nov · Terraform + AWS

- [ ] Recall test: Day 12
- [ ] **Block 1:** HCL, providers, resources, variables/outputs/locals, data sources, `count` vs `for_each`; **state** (what's in it, why remote, S3 backend + DynamoDB locking); plan/apply/destroy; `terraform import`; drift; `-target` and why to avoid it
- [ ] **AWS:** EC2 (instance types, AMI, user data, launch templates, Auto Scaling groups), S3 (storage classes, lifecycle, versioning, bucket policies, encryption), RDS (Multi-AZ, read replicas, backups), IAM Identity Center
- [ ] **Block 2 lab:** write a VPC + EC2 module with variables and outputs; run `plan` (apply only if you accept the small AWS cost, then destroy); modules vs workspaces vs separate directories per environment; how you built EKS with Terraform
- [ ] **SQL:** 5 LeetCode mediums
- [ ] **Quiz** + summary
- **Done when:** you can explain what happens if two people run apply at once, and how you'd recover a corrupted state file

## Day 14 · Wed 25 Nov · Monitoring & tools + your stories

- [ ] Recall test: Day 13
- [ ] **Block 1:** Prometheus (pull model, exporters, scrape config, service discovery, **federation**: your Koko design), PromQL (`rate`, `sum by`, `histogram_quantile`), Grafana dashboards, Alertmanager routing, grouping and inhibition; logs: ELK, Loki; MELT, golden signals, RED/USE
- [ ] **AWS:** CloudWatch (metrics, logs, alarms, Logs Insights), CloudTrail, Cost Explorer / CUR / QuickSight (your FinOps story)
- [ ] **Block 2:** SLI/SLO/SLA and error-budget maths; incident management (ITIL incident/problem/change, RCA, postmortems, on-call); **write your intro and 5 STAR stories** from your real work
- [ ] **Lab:** Prometheus + Grafana + node-exporter in docker compose, with one alert rule firing
- [ ] **SQL:** 5 LeetCode mediums, explained out loud
- [ ] **Quiz** + summary
- **Done when:** you can explain your federated Prometheus design, calculate an error budget, and tell 5 stories without notes

## Day 15 · Thu 26 Nov · Mock interviews + repair

- [ ] **Mock 2 (morning):** SRE / application-support style, including SQL and Linux rapid-fire
- [ ] **Mock 3 (afternoon):** DevOps / Kubernetes / AWS style
- [ ] Repair the top 10 items in `misses.md`
- [ ] Rehearse the intro, 5 stories and "why this role" once more, out loud
- [ ] Prepare your interview kit: resume copies, ID, questions to ask
- [ ] Sleep early
- **Done when:** both mocks are ≥ 8/10
