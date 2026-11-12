# 15-day plan: from "basics break under pressure" to interview-ready (12–26 Nov 2026)

Built after the [11 Nov NiCE interview review](../interview-review-nov-11-nice.md). Full days, for a slow learner.

## The honest goal

Nobody gains five years of experience in 15 days. What **is** possible in 15 days:

1. **Zero misses on basics.** Every grep/sed/find/awk, INSERT/UPDATE/DELETE/JOIN, pod-startup or VPC question that comes up, you answer from memory.
2. **Your real five years told well.** An intro, 5 STAR stories and every number on your resume, defended without notes.
3. **Deep understanding of 5 areas:** Linux, SQL, Kubernetes, AWS, observability/SRE. You'll be able to explain *why*, not only *what*.

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
| 16:00–17:00 | **SQL every day** | Your weakest skill, so it gets daily repetition |
| 17:00–17:30 | **Quiz with Claude** | Send "Day N quiz" in this thread. I ask 10 questions, you answer without notes, I mark them |
| 17:30–18:00 | **Own-words summary** | 5–10 lines in your own words: what you learned and what's still unclear |
| Evening | Rest | Optional 20 min: re-read `misses.md` |

## The 15 days

| Day | Date | Block 1 (main) | Block 2 | SQL (1 h) | End-of-day check |
|---|---|---|---|---|---|
| **1** | Thu 12 Nov | [Linux text tools I](day-01-linux-text-sql-basics.md): grep, find, sed basics, pipes, redirects | Files, permissions, users (`chmod`, `chown`, `ls -l` explained) | SQL command families, SELECT/WHERE/ORDER BY, INSERT/UPDATE/DELETE | 15 one-liners from memory |
| **2** | Fri 13 Nov | Linux text tools II: awk, sort, uniq, cut, wc, xargs, head/tail | Log analysis lab on real Nginx/app logs | GROUP BY, HAVING, COUNT/SUM/AVG, DISTINCT | Top IPs, status codes and errors per hour from a log |
| **3** | Sat 14 Nov | Processes: ps, top, kill/signals, systemd, journalctl | cron, logrotate, environment variables, package managers | JOINs: INNER, LEFT, RIGHT, self join | Explain SIGTERM vs SIGKILL; write a unit file |
| **4** | Sun 15 Nov | Resources: CPU, memory, disk, inodes (top, free, vmstat, iostat, df, du, lsof) | Break/fix: disk full, deleted-but-open file, OOM, high load | Subqueries, NULL handling, CASE, string/date functions | Solve 4 "server is slow" scenarios out loud |
| **5** | Mon 16 Nov | Networking: IP, ports, TCP handshake, DNS, HTTP status codes; ip, ss, curl, dig, traceroute | Nginx in a lab: reverse proxy, logs, 502/504, `nginx -t` | Window functions: ROW_NUMBER, RANK, LAG | Trace "what happens when I type a URL" end to end |
| **6** | Tue 17 Nov | Shell scripting: variables, if, loops, functions, `$?`, `set -euo pipefail` | Write 5 scripts: disk alert, log cleanup, health check + restart, backup, report | 10 LeetCode SQL 50 problems | Explain each script line by line |
| **7** | Wed 18 Nov | **Review + mock 1** (Linux, SQL, shell) | Redo every miss from days 1–6 | Python basics for ops: read a file, regex, count errors | Mock score ≥ 7/10 |
| **8** | Thu 19 Nov | Kubernetes internals: every component, pod startup flow, controllers, etcd | `kind` cluster lab: watch the flow with `kubectl get events -w` | 5 SQL problems | Draw the architecture and explain pod startup in 2 minutes, no notes |
| **9** | Fri 20 Nov | K8s workloads: Deployment, ReplicaSet, rollout/undo, probes, requests/limits, ConfigMap/Secret | K8s networking: Service types, endpoints, kube-proxy, CoreDNS, Ingress | 5 SQL problems | Explain why a Service can have empty endpoints |
| **10** | Sat 21 Nov | K8s troubleshooting: CrashLoopBackOff, Pending, ImagePullBackOff, OOMKilled, readiness, PVC (Killercoda) | HPA, RBAC, node NotReady, drain/cordon | 5 SQL problems | Fix 10 broken scenarios |
| **11** | Sun 22 Nov | AWS networking: VPC, subnets, route tables, IGW, NAT, SG vs NACL, ALB vs NLB (your 9 Oct gap) | EC2, IAM roles/policies, S3, RDS, CloudWatch, EKS specifics | 5 SQL problems | Draw a 3-tier VPC from memory |
| **12** | Mon 23 Nov | Observability + SRE: Prometheus pull/scrape, PromQL (`rate`, `histogram_quantile`), Grafana, alerting, SLI/SLO/error budget, MELT | Incident management: ITIL incident/problem/change, RCA, on-call, postmortems; CI/CD + GitOps (Jenkins vs ArgoCD), Docker multi-stage | 5 SQL problems | Explain how your federated Prometheus worked; do the error-budget maths |
| **13** | Tue 24 Nov | **Your story:** 60-second intro, 5 STAR stories from your real work | Defend every resume number; "why this role" for 3 company types | Light SQL review | Record yourself and listen back |
| **14** | Wed 25 Nov | **Mock 2:** app-support / SRE style (Claude as interviewer) | **Mock 3:** DevOps / Kubernetes style | Review | Score ≥ 8/10 on each |
| **15** | Thu 26 Nov | Repair weak spots from `misses.md` | Light review of all drills, rest early | n/a | Calm and rested |

## Resources (use only these, so you don't drift)

- **Linux practice:** your own terminal (Mac Terminal works; use Docker `ubuntu:24.04` for Linux-only commands) and [OverTheWire Bandit](https://overthewire.org/wargames/bandit/) levels 0–15.
- **SQL:** [SQLBolt](https://sqlbolt.com/) (days 1–3), then [LeetCode SQL 50](https://leetcode.com/studyplan/top-sql-50/). Local practice: `sqlite3`, which comes built into macOS.
- **Kubernetes:** `kind` on Docker Desktop, [Killercoda](https://killercoda.com/) scenarios, and your own repo notes in `../kubernetes/`.
- **AWS:** your repo notes and diagrams (`../diagrams/r1…r6`) from the 9 Oct review.
- **SRE:** Google SRE book, chapters 4 (SLOs) and 6 (Monitoring), free at sre.google/books.
- **This repo:** [NiCE cheat sheet](../nice-actimize-sre-cheatsheet.md) for reference tables. **Don't read it as study material.** Use it to look things up while doing labs.

## Track your progress

Create `misses.md` (in your notebook or this folder) and add a line for every question you miss: `date · question · the right answer in my words`. Re-test from it every morning. The list should get shorter each week. If it doesn't, tell me, and we'll slow down.
