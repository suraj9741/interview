# 15-day plan: from "basics break under pressure" to interview-ready (12–26 Nov 2026)

Built after the [11 Nov NiCE interview review](../interview-review-nov-11-nice.md). Full days, for a slow learner.

## The honest goal

Nobody gains five years of experience in 15 days. What **is** possible in 15 days:

1. **Zero misses on basics.** Every grep/sed/find/awk, INSERT/UPDATE/DELETE/JOIN, pod-startup or VPC question that comes up, you answer from memory.
2. **Your real five years told well.** An intro, 5 STAR stories and every number on your resume, defended without notes.
3. **Deep understanding of your 10 topics:** Linux, networking, scripting, Python, Git, Docker, Kubernetes, CI/CD, Terraform, monitoring, plus daily SQL. You'll be able to explain *why*, not only *what*.

Interviewers judge "5+ years" by depth on basics and by how clearly you explain real incidents. Both can be trained.

**Rule for anything you learn in a lab:** say "I practised this in a lab" and never "in production". It's still worth saying, because it shows you learn.

## How you study (built for a slow learner)

- **One topic per block, no topic jumping.** Don't open YouTube rabbit holes or "one more blog".
- **Learn 25% of the time, type 50%, explain 25%.** Reading alone is what failed on 11 Nov.
- **Explain it in your own words:** first in Hinglish, then in English, out loud, as if teaching a junior. If you get stuck, that's the gap. Go back to it.
- **Spaced repetition:** every morning starts by re-testing yesterday's material. Each day's topics come back on day +1, +3 and +7.
- **Write commands by hand or type them, never copy-paste.**
- **No new topics after Day 12.** Days 13–15 are for stories, mocks and repairing weak spots.
- **Sleep 7+ hours.** Memory gets fixed during sleep, and cutting it undoes the day.

## Daily timetable (about 8 hours)

| Time | Block | What you do |
|---|---|---|
| 9:00–9:30 | **Recall test** | Yesterday's drill with answers hidden. Write misses in `misses.md` |
| 9:30–12:30 | **Block 1: main topic** | Read the lesson (45 min) → type every lab (2 h) → explain out loud (15 min) |
| 12:30–13:30 | Lunch, walk | No screens |
| 13:30–16:00 | **Block 2: second topic or more labs** | Same pattern |
| 16:00–17:00 | **SQL (45 min) + review (15 min)** | SQL was your weakest area, so it gets daily repetition. Then re-test yesterday's topic |
| 17:00–17:30 | **Quiz with Claude** | Send "Day N quiz" in this thread. I ask 10 questions, you answer without notes, I mark them |
| 17:30–18:00 | **Own-words summary** | 5–10 lines in your own words: what you learned and what's still unclear |
| Evening | Rest | Optional 20 min: re-read `misses.md` |

## The 15 days (your 10 topics)

Every day has one **main topic** (Block 1 + Block 2) and the same **4 PM slot**: 45 min of SQL plus 15 min of review on yesterday's topic. SQL stays daily because it was your weakest area on 11 Nov and app-support/SRE interviews keep asking it.

| Day | Date | Topic | Block 1 (9:30–12:30) | Block 2 (13:30–16:00) | Lab / output | End-of-day check |
|---|---|---|---|---|---|---|
| **1** | Thu 12 Nov | **Linux I** | [grep, find, sed, pipes, redirects](day-01-linux-text-sql-basics.md) | Files, permissions, users | `lab/` log files | 15 one-liners from memory |
| **2** | Fri 13 Nov | **Linux II** | Processes and services: ps, top, signals, systemd, journalctl, cron, logrotate | Resources: CPU, memory, disk, inodes (free, vmstat, iostat, df, du, lsof), awk/sort/uniq for logs | Break/fix: disk full, deleted-but-open file, OOM, high load | Solve 4 "server is slow" scenarios out loud |
| **3** | Sat 14 Nov | **Networking I** | OSI and TCP/IP layers, IP addresses, **CIDR/subnet maths on paper** (your 9 Oct gap), ports, TCP vs UDP, 3-way handshake | DNS (records, resolution flow), HTTP methods and status codes, HTTPS/TLS handshake; ip, ss, curl -v, dig, traceroute, tcpdump basics | "What happens when I type a URL" | Split a /16 into /20s by hand; explain the URL flow in 3 minutes |
| **4** | Sun 15 Nov | **Networking II (+ AWS)** | Load balancers L4 vs L7, reverse proxy, NAT, firewalls; **AWS VPC**: subnets, route tables, IGW, NAT GW, SG vs NACL, ALB vs NLB, VPC endpoints | Nginx lab in Docker: reverse proxy, upstreams, logs, reproduce 502/504, `nginx -t` | Nginx config that load-balances 2 backends | Draw a 3-tier VPC from memory, with traffic flow |
| **5** | Mon 16 Nov | **Scripting & automation (Bash)** | Variables, quoting, if/case, loops, functions, arguments, exit codes, `set -euo pipefail`, reading files | Write 5 real scripts: disk alert, old-log cleanup, health check + restart, DB backup with rotation, server report; schedule with cron | 5 scripts in your repo | Explain each script line by line |
| **6** | Tue 17 Nov | **Python for automation** | Basics you need: types, lists/dicts, loops, functions, files, exceptions, `re`, `json`, `argparse` | Ops scripts: parse a log and count errors per hour, call an API with `requests`, run commands with `subprocess`, intro to `boto3` (list EC2/S3) | Rewrite 2 Bash scripts in Python | Write a log parser from a blank file |
| **7** | Wed 18 Nov | **Git** + **mock 1** | Git internals: commit, branch, HEAD; merge vs rebase, conflicts, reset vs revert, cherry-pick, stash, tags, `.gitignore`; branching strategies (GitFlow, trunk-based); PR flow | **Mock 1** (Linux, networking, scripting, Python) with Claude, then redo misses | Resolve 3 merge conflicts in a practice repo | Mock score ≥ 7/10 |
| **8** | Thu 19 Nov | **Docker** | Images vs containers, layers and cache, Dockerfile instructions, CMD vs ENTRYPOINT, **multi-stage builds**, image size and security (your resume says −30–40%) | Networking (bridge, host, user-defined), volumes vs bind mounts, docker compose, troubleshooting (`logs`, `inspect`, `exec`, exit codes) | Containerise the Day 6 Python app, multi-stage, non-root | Explain how you cut image size 30–40% |
| **9** | Fri 20 Nov | **Kubernetes I** | Architecture: every component; **pod startup flow** (the 11 Nov question); controllers, etcd | `kind` cluster: deploy the Day 8 image, watch `kubectl get events -w`; Deployments, ReplicaSets, rollout/undo | App running on kind | Draw the architecture and explain pod startup in 2 minutes, no notes |
| **10** | Sat 21 Nov | **Kubernetes II** | Services (ClusterIP, NodePort, LoadBalancer), endpoints, kube-proxy, CoreDNS, Ingress | ConfigMaps/Secrets, probes, requests/limits, HPA, RBAC, PV/PVC/StorageClass; EKS specifics (IRSA, VPC CNI, ALB controller) | Expose the app through Ingress | Explain why a Service can have empty endpoints |
| **11** | Sun 22 Nov | **Kubernetes III: troubleshooting** | Break/fix on Killercoda: CrashLoopBackOff, Pending, ImagePullBackOff, OOMKilled, readiness, PVC Pending, node NotReady | Helm basics (chart, values, install/upgrade/rollback); how you migrated Swarm → EKS (prepare the story) | Fix 10 broken scenarios | Talk through your migration story |
| **12** | Mon 23 Nov | **CI/CD** | CI vs CD vs continuous deployment; pipeline stages (build, test, scan, push, deploy); Jenkins (Jenkinsfile, agents), GitLab CI, GitHub Actions | GitOps with ArgoCD (your Jenkins → ArgoCD story, 10 → 2 min); deployment strategies (rolling, blue-green, canary); secrets in pipelines | GitHub Actions pipeline: test → build → push the Day 8 image | Draw your Koko pipeline before and after ArgoCD |
| **13** | Tue 24 Nov | **Terraform (+ AWS)** | HCL, providers, resources, variables/outputs, **state** (what it is, remote backend in S3 with DynamoDB locking), plan/apply/destroy, `terraform import`, drift | Modules, workspaces vs separate directories per environment, `count`/`for_each`, data sources; how you built EKS with Terraform | Write a VPC + EC2 module and run plan (apply only if you accept the small AWS cost) | Explain what happens if two people run apply at once |
| **14** | Wed 25 Nov | **Monitoring & tools** | Prometheus (pull, scrape, exporters, **federation**: your Koko story), PromQL (`rate`, `histogram_quantile`), Grafana, Alertmanager routing | Logs (ELK, Loki), MELT, golden signals, SLI/SLO/error budget maths, incident management (ITIL, RCA, on-call); write your 5 STAR stories | Prometheus + Grafana in docker compose with one alert rule | Explain your federated Prometheus design; do the error-budget maths |
| **15** | Thu 26 Nov | **Mocks + repair** | **Mock 2:** SRE/app-support style. **Mock 3:** DevOps/Kubernetes style (Claude as interviewer) | Repair weak spots from `misses.md`; rehearse intro + stories; rest early | n/a | Score ≥ 8/10 on each mock |

**Why this order:** Linux and networking come first because everything else runs on them. Scripting and Python build on Linux. Git comes before Docker, Kubernetes and CI/CD because pipelines start from Git. Kubernetes gets 3 days because it's your strongest claim on the resume and where you rated yourself highest. Terraform and monitoring come late but are your resume's home ground, so they need recall, not first-time learning.

## Resources (use only these, so you don't drift)

- **Linux practice:** your own terminal (Mac Terminal works; use Docker `ubuntu:24.04` for Linux-only commands) and [OverTheWire Bandit](https://overthewire.org/wargames/bandit/) levels 0–15.
- **SQL:** [SQLBolt](https://sqlbolt.com/) (days 1–3), then [LeetCode SQL 50](https://leetcode.com/studyplan/top-sql-50/). Local practice: `sqlite3`, which comes built into macOS.
- **Git:** [Learn Git Branching](https://learngitbranching.js.org/) (visual, great for merge/rebase).
- **Docker:** Docker docs, the "Dockerfile best practices" and "multi-stage builds" pages; your repo notes in `../docker/`.
- **Terraform:** HashiCorp tutorials "Get Started - AWS" and "State".
- **Python:** your own scripts. Use only the docs for `re`, `json`, `subprocess`, `argparse`.
- **Kubernetes:** `kind` on Docker Desktop, [Killercoda](https://killercoda.com/) scenarios, and your own repo notes in `../kubernetes/`.
- **AWS:** your repo notes and diagrams (`../diagrams/r1…r6`) from the 9 Oct review.
- **SRE:** Google SRE book, chapters 4 (SLOs) and 6 (Monitoring), free at sre.google/books.
- **This repo:** [NiCE cheat sheet](../nice-actimize-sre-cheatsheet.md) for reference tables. **Don't read it as study material.** Use it to look things up while doing labs.

## Track your progress

Create `misses.md` (in your notebook or this folder) and add a line for every question you miss: `date · question · the right answer in my words`. Re-test from it every morning. The list should get shorter each week. If it doesn't, tell me, and we'll slow down.
