# 15 days, day by day: tick as you go

Every day has the same shape. Open today's section only, work top to bottom, and tick each box. **Don't read ahead.** Each day lists its **study material**: 📖 read, 🎥 watch, 🛠 practise, 🗄 SQL. Watch **at most one video per day**, inside Block 1. Videos are named by title and channel. Search the exact title on YouTube; I haven't pasted video URLs because I can't check them from here. Hinglish options are from Abhishek Veeramalla and Kunal Kushwaha. The full lesson for each day (with labs and a drill) is written the evening before. Ask in the thread: "Day N lesson".

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

**Study material**
- 📖 Read: [Linux Journey](https://linuxjourney.com/): the "Text-Fu" and "Permissions" lessons · [The Linux Command Line (free book)](https://linuxcommand.org/tlcl.php): chapters 9 (Permissions), 17 (Searching for Files), 19 (Regular Expressions), 20 (Text Processing: sed)
- 🎥 Watch (Block 1, first 45 min only): search YouTube for *"grep sed awk tutorial"* by **Abhishek Veeramalla** (Hinglish) or *"Linux Crash Course - The grep Command"* by **Learn Linux TV**
- 🛠 Practise: [grep: one example per flag](grep-every-flag.md) · [OverTheWire Bandit](https://overthewire.org/wargames/bandit/) levels 0–6 (in the evening, optional)
- 🗄 SQL: [SQLBolt](https://sqlbolt.com/) lessons 1–5 · [Day 1 lesson, Part C](day-01-linux-text-sql-basics.md)

- [ ] Setup: Ubuntu container, `bash make-logs.sh`
- [ ] **Block 1:** grep (all flags, `-E` for OR), pipes and redirects (`|`, `>`, `>>`, `2>`, `&&`), find (`-name`, `-mtime +N`, `-size`, `-exec`, `-delete`), sed (`s///g`, `-i.bak`, `-n 'p'`, `/d`)
- [ ] **Block 2:** reading `ls -l`, chmod numbers (644/755/600/640), chown, users and groups (`usermod -aG`), the permission break/fix lab
- [ ] **SQL:** command families, SELECT/WHERE/ORDER BY/LIMIT/LIKE/IN/BETWEEN, NULL trap, safe INSERT/UPDATE/DELETE, DELETE vs TRUNCATE vs DROP
- [ ] **Quiz** + summary
- **Done when:** you can write the 25 drill answers from memory

## Day 2 · Fri 13 Nov · Linux II

**Study material**
- 📖 Read: The Linux Command Line, chapters 10 (Processes) and 16 (Storage Media) · `man systemctl`, `man journalctl` (only the EXAMPLES sections) · [Brendan Gregg: USE method](https://www.brendangregg.com/usemethod.html) · [awk in 20 minutes](https://ferd.ca/awk-in-20-minutes.html)
- 🎥 Watch: search *"Linux Crash Course - systemd"* and *"Linux Crash Course - Managing Processes"* (**Learn Linux TV**) · *"Linux troubleshooting high CPU memory disk"* (**Abhishek Veeramalla**)
- 🛠 Practise: Bandit levels 7–12
- 🗄 SQL: SQLBolt lessons 10–12 (aggregates, GROUP BY, HAVING)

- [ ] Recall test: Day 1 drill
- [ ] **Block 1:** processes (`ps aux`, `ps -ef`, `top`, `htop`, `pgrep`), signals (`kill -15` vs `-9`, SIGHUP), foreground/background (`&`, `nohup`, `jobs`), systemd (`systemctl status/start/enable`, unit files), `journalctl -u … --since`, cron syntax, logrotate
- [ ] **Block 2:** resources: `uptime` and load average, `free -h`, `vmstat`, `iostat`, `df -h`, `df -i`, `du -sh`, `lsof +L1`, OOM killer (`dmesg`); awk, sort, uniq, cut, wc, xargs for log analysis
- [ ] **Lab:** break/fix: fill the disk, delete an open file, start a CPU hog, find and fix each one
- [ ] **SQL:** COUNT/SUM/AVG/MIN/MAX, DISTINCT, GROUP BY, HAVING, WHERE vs HAVING
- [ ] **Quiz** + summary
- **Done when:** you can talk through "the server is slow" step by step, and write top-IPs and errors-per-hour one-liners

## Day 3 · Sat 14 Nov · Networking I

**Study material**
- 📖 Read: [Cloudflare Learning Center](https://www.cloudflare.com/learning/): "What is DNS?", "What is the OSI model?", "What happens in a TLS handshake?", "What is TCP/IP?" · [MDN: HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) · your repo: `../networking/` levels 1–3
- 🎥 Watch: search *"Computer Networking Full Course"* (**Kunal Kushwaha**, watch the OSI, TCP/IP, DNS parts) · *"Subnetting Mastery"* (**Practical Networking**, first 2 videos) · *"What happens when you type a URL into your browser"* (**ByteByteGo**)
- 🛠 Practise: [subnettingpractice.com](https://subnettingpractice.com/), 20 questions **on paper first**
- 🗄 SQL: SQLBolt lessons 6–9 (JOINs)

- [ ] Recall test: Day 2 (+ Day 1 misses)
- [ ] **Block 1:** OSI vs TCP/IP layers (with an example protocol per layer), IPv4, private ranges, **CIDR and subnet maths on paper** (/16, /20, /24, /28: hosts, network and broadcast addresses), TCP vs UDP, the 3-way handshake, common ports (22, 53, 80, 443, 3306, 5432, 6443)
- [ ] **Block 2:** DNS (A, AAAA, CNAME, MX, TXT, NS; recursive resolution, TTL), HTTP methods and status codes (2xx/3xx/4xx/5xx; what 502/503/504 mean), HTTPS/TLS handshake and certificates; commands: `ip a`, `ip route`, `ss -tlnp`, `curl -v`, `dig`, `nslookup`, `traceroute`, `ping`, `tcpdump -i any port 80`
- [ ] **Lab:** `dig +trace google.com`, `curl -v https://…` (read every line), capture a handshake with tcpdump
- [ ] **SQL:** JOINs (INNER, LEFT, RIGHT, self join), finding rows missing in the other table
- [ ] **Quiz** + summary
- **Done when:** you can split 10.0.0.0/16 into /20s by hand, and explain "what happens when I type a URL" in 3 minutes

## Day 4 · Sun 15 Nov · Networking II + AWS networking

**Study material**
- 📖 Read: [AWS VPC: how Amazon VPC works](https://docs.aws.amazon.com/vpc/latest/userguide/how-it-works.html) · [Security groups vs NACLs (AWS docs)](https://docs.aws.amazon.com/vpc/latest/userguide/infrastructure-security.html) · [Elastic Load Balancing: ALB vs NLB](https://aws.amazon.com/elasticloadbalancing/features/) · [Route 53 routing policies](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html) · [NGINX beginner's guide](https://nginx.org/en/docs/beginners_guide.html) · your repo diagrams `../diagrams/r1…r6` (9 Oct review)
- 🎥 Watch: search *"AWS VPC tutorial"* (**Abhishek Veeramalla**, from his AWS Zero to Hero series) · *"NGINX Explained in 100 Seconds"* (**Fireship**) then *"NGINX tutorial for beginners"* (**TechWorld with Nana**)
- 🗄 SQL: [Mode SQL tutorial: subqueries and CASE](https://mode.com/sql-tutorial/sql-sub-queries/) · 5 LeetCode SQL 50

- [ ] Recall test: Day 3
- [ ] **Block 1:** L4 vs L7 load balancing, reverse proxy vs forward proxy, NAT, stateful vs stateless firewalls
- [ ] **AWS:** VPC, public vs private subnets, route tables, IGW, NAT gateway, **security group vs NACL**, VPC endpoints, peering vs Transit Gateway, ALB vs NLB, Route 53 routing policies
- [ ] **Block 2 lab:** Nginx in Docker as a reverse proxy for 2 backends; read the access and error logs; stop a backend and reproduce a 502; `nginx -t` and reload
- [ ] **SQL:** subqueries (IN, EXISTS, correlated), CASE, string and date functions
- [ ] **Quiz** + summary
- **Done when:** you can draw a 3-tier VPC with traffic flow from memory, and explain 502 vs 504

## Day 5 · Mon 16 Nov · Bash scripting & automation

**Study material**
- 📖 Read: [BashGuide (Greg's wiki)](https://mywiki.wooledge.org/BashGuide): sections on parameters, tests and conditionals, loops · [Bash pitfalls](https://mywiki.wooledge.org/BashPitfalls) (first 15) · check every script with [ShellCheck](https://www.shellcheck.net/) · [crontab.guru](https://crontab.guru/)
- 🎥 Watch: search *"Bash Scripting Full Course"* (**freeCodeCamp**, watch at 1.25×, first 90 min) or *"Shell scripting for DevOps"* (**Abhishek Veeramalla**, Hinglish)
- 🗄 SQL: [SQLBolt lessons 16–18](https://sqlbolt.com/lesson/creating_tables) (CREATE, ALTER, DROP) · [W3Schools SQL constraints](https://www.w3schools.com/sql/sql_constraints.asp)

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

**Study material**
- 📖 Read: [Automate the Boring Stuff with Python (free)](https://automatetheboringstuff.com/): chapters 1–6, 7 (regex), 9 (files) · [Python `subprocess` docs](https://docs.python.org/3/library/subprocess.html) (examples only) · [boto3 quickstart](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) · [IAM policy elements](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html)
- 🎥 Watch: search *"Python for DevOps"* (**Abhishek Veeramalla**) · *"Python Tutorial for Beginners"* (**Corey Schafer**, only the files, dicts and exceptions videos)
- 🗄 SQL: search YouTube *"SQL Window Functions RANK DENSE_RANK ROW_NUMBER LEAD LAG"* (**techTFQ**) · [Mode: window functions](https://mode.com/sql-tutorial/sql-window-functions/)

- [ ] Recall test: Day 5
- [ ] **Block 1:** types, lists, dicts, loops, functions, reading and writing files, exceptions (try/except), modules: `re`, `json`, `os`, `sys`, `argparse`, `datetime`
- [ ] **AWS:** IAM (users, groups, roles, policies; JSON policy structure, least privilege, instance profiles, AssumeRole); `boto3` to list EC2 instances and S3 buckets (read-only)
- [ ] **Block 2 lab:** log parser that counts errors per hour; an API call with `requests` and its JSON parsed; `subprocess.run` to check a service; rewrite the disk-alert and cleanup scripts in Python
- [ ] **SQL:** window functions: ROW_NUMBER, RANK, DENSE_RANK, LAG/LEAD; dedupe; Nth highest salary
- [ ] **Quiz** + summary
- **Done when:** you can write the log parser from a blank file, and read an IAM policy out loud

## Day 7 · Wed 18 Nov · Git + Mock 1

**Study material**
- 📖 Read: [Pro Git book (free)](https://git-scm.com/book/en/v2): chapters 2 (Basics) and 3 (Branching), plus 7.7 (Reset demystified) · [Atlassian: merging vs rebasing](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
- 🛠 Practise: [Learn Git Branching](https://learngitbranching.js.org/): "Main" levels 1–8 and "Remote" 1–4
- 🎥 Watch: search *"Complete Git and GitHub Tutorial"* (**Kunal Kushwaha**) or *"Git Tutorial for Beginners"* (**TechWorld with Nana**)
- 🎤 Mock 1: send "Mock 1" in the thread at 13:30

- [ ] Recall test: Day 6
- [ ] **Block 1:** what a commit, branch and HEAD are; working dir, staging, repo; merge vs rebase (with a diagram); resolving conflicts; reset (`--soft`/`--mixed`/`--hard`) vs revert; cherry-pick; stash; tags; `.gitignore`; GitFlow vs trunk-based; the PR/code review flow; [Learn Git Branching](https://learngitbranching.js.org/)
- [ ] **Lab:** create 3 merge conflicts on purpose and resolve them; undo a bad commit with revert
- [ ] **Block 2: Mock 1** with Claude: Linux, networking, Bash, Python, SQL (45 min). Then redo every miss
- [ ] **SQL:** covered in the mock
- [ ] Summary + update `misses.md`
- **Done when:** mock score ≥ 7/10, and you can explain when to use revert instead of reset

## Day 8 · Thu 19 Nov · Docker

**Study material**
- 📖 Read: [Docker: Dockerfile best practices](https://docs.docker.com/build/building/best-practices/) · [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/) · [Docker networking overview](https://docs.docker.com/engine/network/) · [Julia Evans: what even is a container](https://jvns.ca/blog/2016/10/10/what-even-is-a-container/) · [Amazon ECR getting started](https://docs.aws.amazon.com/AmazonECR/latest/userguide/getting-started-cli.html) · your repo `../docker/`
- 🎥 Watch: search *"Docker Tutorial for Beginners [FULL COURSE]"* (**TechWorld with Nana**) or *"Docker Zero to Hero"* (**Abhishek Veeramalla**)
- 🗄 SQL: [PostgreSQL docs: transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html) (read the table only) · search *"ACID properties explained"* (**ByteByteGo**)

- [ ] Recall test: Day 7 misses
- [ ] **Block 1:** container vs VM (namespaces, cgroups), image vs container, layers and cache order, Dockerfile instructions, CMD vs ENTRYPOINT, COPY vs ADD, **multi-stage builds**, non-root user, slim/distroless bases, `.dockerignore`, image scanning (Trivy)
- [ ] **AWS:** ECR: login, push/pull, lifecycle policies, scan on push
- [ ] **Block 2 lab:** containerise your Day 6 Python app (multi-stage, non-root) and compare image sizes; docker networking (bridge, host, user-defined), volumes vs bind mounts, docker compose with app + DB; troubleshoot with `logs`, `inspect`, `exec` and exit codes
- [ ] **SQL:** transactions, ACID, isolation levels, locks and deadlocks
- [ ] **Quiz** + summary
- **Done when:** you can explain how you cut image size by 30–40% (your resume claim) with your own example

## Day 9 · Fri 20 Nov · Kubernetes I

**Study material**
- 📖 Read: [Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/) · [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) · [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) · your repo `../kubernetes/` notes 01–05 and the `04-kubectl-apply-flow` diagram · [kind quick start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- 🎥 Watch: search *"Kubernetes Tutorial for Beginners [FULL COURSE in 4 Hours]"* (**TechWorld with Nana**, first 90 min) · *"Kubernetes architecture explained"* (**Abhishek Veeramalla**)
- 🗄 SQL: [Use The Index, Luke](https://use-the-index-luke.com/): chapter 1 (Anatomy of an index) · [SQLite EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html)

- [ ] Recall test: Day 8
- [ ] **Block 1:** architecture: kube-apiserver, etcd, scheduler, controller-manager, cloud-controller-manager, kubelet, kube-proxy, container runtime, CNI; **the pod startup flow** (the 11 Nov question); pod phases
- [ ] **Block 2 lab:** `kind` cluster; deploy your Day 8 image as a Deployment; watch `kubectl get events -w` during a rollout; scale, `rollout status`, `rollout undo`, `rollout history`
- [ ] **SQL:** indexes, `EXPLAIN`, slow-query troubleshooting
- [ ] **Quiz** + summary
- **Done when:** you can draw the architecture and explain pod startup in 2 minutes with no notes

## Day 10 · Sat 21 Nov · Kubernetes II

**Study material**
- 📖 Read: [Services](https://kubernetes.io/docs/concepts/services-networking/service/) · [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) · [Configure liveness, readiness and startup probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) · [Resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) · [HPA walkthrough](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/) · [EKS Best Practices Guide](https://docs.aws.amazon.com/eks/latest/best-practices/introduction.html) (networking + security sections)
- 🎥 Watch: Nana's 4-hour course, the Services, Ingress, ConfigMap/Secret parts · search *"EKS IRSA explained"*
- 🗄 SQL: NiCE cheat sheet section 7 (data-validation queries): type each one

- [ ] Recall test: Day 9
- [ ] **Block 1:** Services (ClusterIP, NodePort, LoadBalancer, headless), endpoints, kube-proxy, CoreDNS names, Ingress and IngressClass; ConfigMaps and Secrets; liveness/readiness/startup probes; requests vs limits and QoS classes; HPA
- [ ] **AWS:** EKS: managed node groups vs Karpenter, VPC CNI and IP exhaustion, IRSA / Pod Identity, AWS Load Balancer Controller, EBS CSI driver
- [ ] **Block 2 lab:** expose your app through a Service and Ingress; add probes and limits; mount a ConfigMap; set up an HPA; a simple RBAC Role + RoleBinding, checked with `kubectl auth can-i`
- [ ] **SQL:** data-validation queries (duplicates, NULLs, source vs target counts, missing rows)
- [ ] **Quiz** + summary
- **Done when:** you can explain why a Service can have empty endpoints, and how a pod gets S3 access without keys

## Day 11 · Sun 22 Nov · Kubernetes III: troubleshooting + Helm

**Study material**
- 📖 Read: [learnk8s: A visual guide on troubleshooting Kubernetes deployments](https://learnk8s.io/troubleshooting-deployments) (print the flowchart) · NiCE cheat sheet, the Kubernetes troubleshooting table · [Helm quickstart](https://helm.sh/docs/intro/quickstart/)
- 🛠 Practise: [Killercoda Kubernetes scenarios](https://killercoda.com/playgrounds/scenario/kubernetes) and the CKA scenarios (troubleshooting ones)
- 🎥 Watch: search *"Helm Explained"* (**TechWorld with Nana**)
- 🗄 SQL: [MySQL: mysqldump](https://dev.mysql.com/doc/refman/8.0/en/mysqldump.html) (examples) · [RDS backups and point-in-time recovery](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html)

- [ ] Recall test: Day 10
- [ ] **Block 1:** break/fix on Killercoda: CrashLoopBackOff, Pending, ImagePullBackOff, OOMKilled, readiness failing, CreateContainerConfigError, PVC Pending, node NotReady, stuck rollout
- [ ] **Block 2:** Helm (chart structure, values, install/upgrade/rollback, `helm template`); prepare your **Docker Swarm → EKS migration** story (why, how, environments, cutover, problems, results)
- [ ] **SQL:** GRANT/REVOKE, backups (`mysqldump`, `pg_dump`), restore, RDS snapshots and point-in-time recovery
- [ ] **Quiz** + summary
- **Done when:** you've fixed 10 broken scenarios and can tell the migration story in 3 minutes

## Day 12 · Mon 23 Nov · CI/CD

**Study material**
- 📖 Read: [GitHub Actions quickstart](https://docs.github.com/en/actions/writing-workflows/quickstart) · [Jenkins pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/) · [GitLab CI quick start](https://docs.gitlab.com/ci/quick_start/) · [Argo CD: core concepts](https://argo-cd.readthedocs.io/en/stable/core_concepts/) · NiCE cheat sheet, section 10 (deployment strategies)
- 🎥 Watch: search *"GitHub Actions Tutorial"* (**TechWorld with Nana**) · *"ArgoCD Tutorial for Beginners"* (**TechWorld with Nana**) · *"CI/CD explained"* (**ByteByteGo**)
- 🗄 SQL: [AWS: Multi-AZ vs read replicas](https://aws.amazon.com/rds/features/read-replicas/) · search *"Database replication explained"* (**ByteByteGo**)

- [ ] Recall test: Day 11
- [ ] **Block 1:** CI vs continuous delivery vs continuous deployment; pipeline stages (build, test, scan, push, deploy); Jenkins (Jenkinsfile, declarative pipeline, agents, credentials), GitLab CI (`.gitlab-ci.yml`, stages, runners), GitHub Actions (workflows, jobs, runners, secrets)
- [ ] **AWS:** CodePipeline/CodeDeploy at concept level; Secrets Manager and Parameter Store in pipelines
- [ ] **Block 2:** GitOps with ArgoCD (sync, self-heal, rollback by `git revert`); deployment strategies (rolling, blue-green, canary); your Jenkins → ArgoCD story (10 → 2 minutes)
- [ ] **Lab:** a GitHub Actions pipeline that tests, builds and pushes your Day 8 image
- [ ] **SQL:** MySQL vs PostgreSQL basics, connection pooling, replication, RDS Multi-AZ vs read replicas
- [ ] **Quiz** + summary
- **Done when:** you can draw your Koko pipeline before and after ArgoCD, and explain canary vs blue-green

## Day 13 · Tue 24 Nov · Terraform + AWS

**Study material**
- 📖 Read: [HashiCorp tutorials: Get started on AWS](https://developer.hashicorp.com/terraform/tutorials/aws-get-started) (all of them) · [State](https://developer.hashicorp.com/terraform/language/state) · [S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3) · [Modules](https://developer.hashicorp.com/terraform/language/modules) · [EC2 Auto Scaling groups](https://docs.aws.amazon.com/autoscaling/ec2/userguide/auto-scaling-groups.html) · [S3 storage classes](https://aws.amazon.com/s3/storage-classes/)
- 🎥 Watch: search *"Terraform Zero to Hero"* (**Abhishek Veeramalla**) or *"Terraform Course - Automate your AWS cloud infrastructure"* (**freeCodeCamp**)
- 🗄 SQL: 5 LeetCode SQL 50 mediums

- [ ] Recall test: Day 12
- [ ] **Block 1:** HCL, providers, resources, variables/outputs/locals, data sources, `count` vs `for_each`; **state** (what's in it, why remote, S3 backend + DynamoDB locking); plan/apply/destroy; `terraform import`; drift; `-target` and why to avoid it
- [ ] **AWS:** EC2 (instance types, AMI, user data, launch templates, Auto Scaling groups), S3 (storage classes, lifecycle, versioning, bucket policies, encryption), RDS (Multi-AZ, read replicas, backups), IAM Identity Center
- [ ] **Block 2 lab:** write a VPC + EC2 module with variables and outputs; run `plan` (apply only if you accept the small AWS cost, then destroy); modules vs workspaces vs separate directories per environment; how you built EKS with Terraform
- [ ] **SQL:** 5 LeetCode mediums
- [ ] **Quiz** + summary
- **Done when:** you can explain what happens if two people run apply at once, and how you'd recover a corrupted state file

## Day 14 · Wed 25 Nov · Monitoring & tools + your stories

**Study material**
- 📖 Read: [Prometheus overview](https://prometheus.io/docs/introduction/overview/) · [Querying basics](https://prometheus.io/docs/prometheus/latest/querying/basics/) · [Histograms and summaries](https://prometheus.io/docs/practices/histograms/) · [Federation](https://prometheus.io/docs/prometheus/latest/federation/) · [Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/) · [Google SRE book](https://sre.google/sre-book/table-of-contents/): chapters 4 (SLOs), 6 (Monitoring), 14 (Managing incidents), 15 (Postmortems) · NiCE cheat sheet sections 3, 4, 9
- 🎥 Watch: search *"How Prometheus Monitoring works"* (**TechWorld with Nana**) · *"Prometheus and Grafana"* (**Abhishek Veeramalla**)
- 🗄 SQL: 5 LeetCode mediums, explained out loud

- [ ] Recall test: Day 13
- [ ] **Block 1:** Prometheus (pull model, exporters, scrape config, service discovery, **federation**: your Koko design), PromQL (`rate`, `sum by`, `histogram_quantile`), Grafana dashboards, Alertmanager routing, grouping and inhibition; logs: ELK, Loki; MELT, golden signals, RED/USE
- [ ] **AWS:** CloudWatch (metrics, logs, alarms, Logs Insights), CloudTrail, Cost Explorer / CUR / QuickSight (your FinOps story)
- [ ] **Block 2:** SLI/SLO/SLA and error-budget maths; incident management (ITIL incident/problem/change, RCA, postmortems, on-call); **write your intro and 5 STAR stories** from your real work
- [ ] **Lab:** Prometheus + Grafana + node-exporter in docker compose, with one alert rule firing
- [ ] **SQL:** 5 LeetCode mediums, explained out loud
- [ ] **Quiz** + summary
- **Done when:** you can explain your federated Prometheus design, calculate an error budget, and tell 5 stories without notes

## Day 15 · Thu 26 Nov · Mock interviews + repair

**Study material**
- No new material. Use `misses.md`, your own-words summaries, the [11 Nov review](../interview-review-nov-11-nice.md) and the [NiCE cheat sheet](../nice-actimize-sre-cheatsheet.md) to repair weak spots.
- 🎤 Send "Mock 2" at 9:30 and "Mock 3" at 14:00 in the thread.

- [ ] **Mock 2 (morning):** SRE / application-support style, including SQL and Linux rapid-fire
- [ ] **Mock 3 (afternoon):** DevOps / Kubernetes / AWS style
- [ ] Repair the top 10 items in `misses.md`
- [ ] Rehearse the intro, 5 stories and "why this role" once more, out loud
- [ ] Prepare your interview kit: resume copies, ID, questions to ask
- [ ] Sleep early
- **Done when:** both mocks are ≥ 8/10
