# Kentik · Sr SRE Engineer · interview Thu 19 Nov, 2:30 PM IST (moved from 5:30)

**Two interviews in one day.** The AWS Admin L2 is at 10:30 AM ([its pack](https://github.com/suraj9741/interview/blob/main/interview-prep/interviews/2026-11-13-aws-admin/aws-admin-l2-prep.md)). **Tonight belongs to that one.** The gap between the two interviews is now only about 2.5 hours, so Python starts with 40 minutes **before** the AWS warm-up tomorrow morning. Don't open the rest of this file tonight.

**Read the JD carefully.** The title says "Sr SRE", but the text says "entry-level, suitable for fresh graduates". It's probably a copy-pasted template. **Prepare at senior level** (5+ years: you own things, you've handled incidents, you make decisions). If they turn out to be junior-level questions, you'll do well anyway.

**What the JD will test, and your matching resume story:**

| JD line | What they'll ask | Your real story (from your resume) |
|---|---|---|
| GitOps for continuous deployment | What GitOps is, how ArgoCD works, rollback, drift, secrets | **Jenkins → ArgoCD at Koko: deploy time 10 → 2 min** ([story 2](https://github.com/suraj9741/interview/blob/main/interview-prep/interviews/2026-11-13-aws-admin/aws-interview-stories.md), PR #12) |
| Kubernetes | Pod startup, troubleshooting statuses, Deployments, Services, HPA, probes | **Docker Swarm → EKS migration; EKS upgrades** (stories 1 and 5) |
| Terraform on AWS | State, locking, drift, modules, writing a resource | EKS and VPC with Terraform at Koko/Perfios |
| Grafana and monitoring | PromQL, RED/USE, alert rules, dashboards, what you'd recommend from the data | **Federated Prometheus + Grafana at Koko, lower MTTD** (story 3) |
| Bash and Python automation, **plus Python programming** (the recruiter asked) | **Live coding: small problems and a script** (section F) | Ansible setup 2 h → 20 min (story 7); your scripts. **Your resume says Python basic: don't claim more** |
| On-call and incident response | An incident you handled, RCA, SLOs | **SSL expiry incident** (L2 pack, Part 2) and the RDS secret-rotation problem |

## About Kentik (10 minutes; check kentik.com before the call)

[Likely] from training knowledge:
- Kentik is a **network observability** SaaS company (US-based). Customers are ISPs, telcos, cloud and digital businesses, and enterprises.
- It collects **network telemetry**: flow data (**NetFlow, sFlow, IPFIX**), **BGP** routing data, SNMP/streaming telemetry and **cloud flow logs** (e.g. AWS VPC Flow Logs). It also runs **synthetic tests** (pings, HTTP checks, traceroutes from agents around the world).
- Customers use it for traffic analytics, capacity planning, **DDoS detection**, cost of transit and peering, and troubleshooting.
- The SRE team keeps that platform running: it ingests huge volumes of data continuously, so reliability, Kubernetes, automation and monitoring matter a lot.

**Why that helps you:** tonight's networking prep for the AWS round (OSI, TCP, DNS, routing, VPC Flow Logs) is directly relevant here too. Mention it.

## Tomorrow's plan (between the two interviews)

| Time | What |
|---|---|
| **8:00–8:40** (before the AWS warm-up) | **Python drills 1–5** (section F) from a blank file, saying the approach out loud. Then breakfast and the AWS warm-up at 9:00 as planned |
| 11:30–11:40 | **L2 debrief:** jot every question they asked in 5 lines and send it in the thread. I'll mark it later, not now |
| 11:40–12:10 | Quick lunch, away from screens |
| 12:10–1:05 | **Python:** drills 6–9, then `log_report.py` (section D2) from a blank file. Say the approach before typing |
| 1:05–1:25 | **GitOps + Kubernetes:** say the ArgoCD 10 → 2 min story out loud; type A1, A4 and B2 |
| 1:25–1:45 | **Monitoring:** type C1 (PromQL) and C2 (alert rule); say the federated Prometheus story |
| 1:45–1:55 | "Why Kentik" out loud once; pick your 2 questions |
| 1:55–2:25 | Rest. Water. Laptop charged, link tested. **Nothing new** |
| 2:25 | Join |

Skipped because of the time change (only if they come up, answer from experience): Python drills 10–12 and concepts F2, Kubernetes B3–B7, Bash D1, Terraform (already covered in the morning AWS round), on-call E.

---

## A. GitOps (type first, then open)

<details><summary>A1. What is GitOps, in 4 principles?</summary>

1. **Declarative:** the whole desired state (manifests, Helm values) is described as code.
2. **Versioned in Git:** Git is the single source of truth; every change is a commit, reviewed in a PR, with history and easy rollback.
3. **Pulled automatically:** an agent in the cluster (ArgoCD, Flux) pulls the desired state from Git. CI never needs cluster credentials.
4. **Continuously reconciled:** the agent compares live state with Git and fixes drift.
</details>

<details><summary>A2. Push-based CD (Jenkins runs kubectl) vs pull-based GitOps (ArgoCD). Why did you move?</summary>

Push: the CI server holds cluster credentials and runs `kubectl apply`/`helm upgrade`. That's a security risk, there's no drift correction, and the cluster's state isn't visible from Git. Pull: ArgoCD inside the cluster watches Git; CI only builds, tests, pushes the image and updates the image tag in the Git repo. Benefits: no cluster credentials in CI, audit trail in Git, self-healing, rollback = `git revert`, one view of every app's sync and health status. **Your result: 10 → 2 minutes per deploy** (be ready to say what took the 10 minutes before: ⟨fill: manual steps / Jenkins jobs / approvals⟩).
</details>

<details><summary>A3. ArgoCD terms: Application, sync, OutOfSync, self-heal, prune, health.</summary>

**Application** = a CRD pointing to a Git repo/path/revision and a destination cluster/namespace. **Synced/OutOfSync** = live state matches Git or not. **Sync** = apply Git to the cluster (manual or automatic). **Self-heal** = automatically revert manual changes made in the cluster. **Prune** = delete resources that were removed from Git. **Health** = Healthy, Progressing, Degraded, Missing (based on resource status). **App of apps / ApplicationSets** = manage many apps or clusters from one definition.
</details>

<details><summary>A4. How do you roll back with GitOps? And how do you handle secrets?</summary>

**Rollback:** `git revert` the commit (or set the image tag back) and let ArgoCD sync; ArgoCD's history rollback works too, but Git must be updated or auto-sync will re-apply the bad version. **Secrets:** never plain in Git. Options: **External Secrets Operator** (pulls from AWS Secrets Manager/SSM), **Sealed Secrets** (encrypted in Git, decrypted by the in-cluster controller), **SOPS** (encrypted values, e.g. with KMS). ⟨fill: which one you used at Koko⟩.
</details>

<details><summary>A5. Promotion: how does a change go from dev to prod in GitOps?</summary>

Typical: one repo (or folder) per environment with Kustomize overlays or Helm values per env. CI builds the image once, then a PR bumps the tag in `dev`; after tests, a PR (manual approval) bumps it in `staging` and then `prod`. The same image digest moves through all environments. Progressive delivery with **Argo Rollouts** (canary, blue-green) if needed.
</details>

## B. Kubernetes (type first, then open)

<details><summary>B1. What happens when a pod starts? (control plane 3 steps + node 8 steps)</summary>

API server saves the Pod in etcd (Pending, no node) → scheduler filters, scores, binds → kubelet on that node: volumes/Secrets/ConfigMaps → pod sandbox (pause container) → CNI assigns the IP → image pull → init containers → app containers + postStart → probes → Ready → EndpointSlice + kube-proxy → traffic. Diagram: [05-pods.md](https://github.com/suraj9741/interview/blob/main/interview-prep/kubernetes/05-pods.md) (PR #13).
</details>

<details><summary>B2. Pending, ImagePullBackOff, CrashLoopBackOff, OOMKilled, Running 0/1: cause and first command for each.</summary>

Pending → scheduler can't place it (requests, taints, affinity, PVC zone): `kubectl describe pod` Events. ImagePullBackOff → wrong image/tag or registry auth: describe Events. CrashLoopBackOff → app exits on start: `kubectl logs <pod> --previous`. OOMKilled → exceeded memory limit (exit 137): `kubectl describe pod` (Last State), raise the limit or fix the leak. Running 0/1 → readiness probe failing: describe, check probe path/port.
</details>

<details><summary>B3. Requests vs limits, and what happens when you exceed each.</summary>

**Requests** = what the scheduler reserves (used for placement and for HPA percentages). **Limits** = the ceiling. Over the **CPU** limit → throttled (slower, not killed). Over the **memory** limit → OOMKilled. No requests = the scheduler packs pods blindly; set requests on everything.
</details>

<details><summary>B4. Liveness vs readiness vs startup probe.</summary>

**Readiness** fails → pod removed from Service endpoints (no traffic), not restarted. **Liveness** fails → container restarted. **Startup** → disables the other two until the app has started (for slow starters), so liveness doesn't kill it during boot. Classic mistake: a liveness probe that checks the database, so a DB blip restarts every pod.
</details>

<details><summary>B5. Rolling update: maxSurge and maxUnavailable; how do you roll back?</summary>

`maxSurge` = how many extra pods above the desired count during the rollout; `maxUnavailable` = how many can be down. With maxUnavailable 0 and maxSurge 1, capacity never drops. Watch: `kubectl rollout status deploy/web`. Roll back: `kubectl rollout undo deploy/web` (but in GitOps, revert in Git, or ArgoCD self-heal puts the bad version back).
</details>

<details><summary>B6. Service types and how traffic reaches a pod on EKS from the internet.</summary>

ClusterIP (internal virtual IP) · NodePort (port on every node) · LoadBalancer (cloud LB) · ExternalName (DNS alias). On EKS: Route 53 → ALB (created by the AWS Load Balancer Controller from an Ingress) → in IP mode, straight to **pod IPs** (VPC CNI gives pods real VPC IPs) → pod. kube-proxy handles ClusterIP traffic inside the cluster.
</details>

<details><summary>B7. HPA: how does it decide, and why might it not scale?</summary>

HPA reads metrics (metrics-server for CPU/memory, or custom/external metrics) every ~15 s and computes desired replicas = current × (current metric / target), within min/max. Doesn't scale when: no resource **requests** set (percent of what?), metrics-server missing, at maxReplicas, or new pods stay Pending because nodes are full (then Cluster Autoscaler/Karpenter must add nodes).
</details>

## C. Monitoring: Prometheus and Grafana (type first, then open)

<details><summary>C1. Write PromQL for: request rate, 5xx error ratio, p99 latency.</summary>

```promql
sum(rate(http_requests_total[5m]))                                         # requests per second
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))                                     # 5xx error ratio
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))   # p99 latency
```
`rate()` = per-second increase of a counter over the window (handles counter resets). Always `rate` a counter before `sum`. `histogram_quantile` needs the `le` label kept in the `sum by`.
</details>

<details><summary>C2. Write a Prometheus alert rule: 5xx ratio above 5% for 10 minutes.</summary>

```yaml
groups:
  - name: app-alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
            / sum(rate(http_requests_total[5m])) > 0.05
        for: 10m
        labels:
          severity: page
        annotations:
          summary: "5xx error ratio above 5% for 10 minutes"
          runbook: "https://wiki.example.com/runbooks/high-error-rate"
```
`for:` avoids paging on a short spike. Alertmanager then routes by labels (severity → PagerDuty vs Slack), groups, and silences.
</details>

<details><summary>C3. RED vs USE vs the 4 golden signals.</summary>

**RED** (for services): Rate, Errors, Duration. **USE** (for resources: CPU, memory, disk, network): Utilization, Saturation, Errors. **Golden signals** (Google SRE): latency, traffic, errors, saturation. Dashboards: RED per service on top, USE per node/cluster underneath.
</details>

<details><summary>C4. Prometheus pull model, federation, and long-term storage.</summary>

Prometheus **pulls** (scrapes) `/metrics` endpoints on a schedule; targets found by service discovery (Kubernetes SD). Short-lived jobs push to the **Pushgateway**. **Federation:** a global Prometheus scrapes selected, aggregated series from per-cluster Prometheus servers: **your Koko design** (⟨fill: how many clusters/environments⟩). Local storage is short (15 days by default); for long-term and global views, Thanos, Cortex/Mimir or a managed service.
</details>

<details><summary>C5. "Provide insights and recommendations from Grafana data" (JD line). Give an example.</summary>

Pick one real one: p99 latency rising with CPU throttling → raise CPU limits or requests; memory steadily climbing until OOMKilled → a leak, set alerts on growth; nodes at 20% utilization → right-size instances or use Karpenter consolidation (**your FinOps −30% EKS cost story** at One2N); alert noise → move to SLO burn-rate alerts. Structure: observation → evidence (panel, query) → recommendation → result.
</details>

## D. Scripting (the biggest risk: type these from a blank file)

Both scripts are in [labs/](labs/), tested on Ubuntu 24.04. **Don't read them first.** Try to write each from the description, then compare.

<details><summary>D1. Bash: alert when any filesystem is above a threshold (default 80%); exit 1 if any are.</summary>

See [labs/disk_alert.sh](labs/disk_alert.sh). Key lines:

```bash
#!/usr/bin/env bash
set -euo pipefail
THRESHOLD="${1:-80}"
status=0
while read -r fs size used avail pct mount; do
  usage="${pct%\%}"
  if (( usage >= THRESHOLD )); then
    echo "ALERT: ${mount} is at ${usage}% (${fs})"
    status=1
  fi
done < <(df -P -x tmpfs -x devtmpfs -x overlay | tail -n +2)
(( status == 0 )) && echo "OK: all filesystems below ${THRESHOLD}%"
exit "$status"
```
Explain: `set -euo pipefail` = stop on errors, on unset variables, and on failures inside pipes · `${1:-80}` = default value · `${pct%\%}` = strip the `%` · `(( ))` = arithmetic · `< <(...)` = feed the loop without a subshell, so `status` survives.
</details>

<details><summary>D2. Python: from app.log, count lines per level, ERROR lines per hour, and the top N users.</summary>

See [labs/log_report.py](labs/log_report.py). Core:

```python
import re
from collections import Counter

LINE = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}):\d{2}:\d{2} (\w+)\s+\[[^\]]+\] user=(\w+)")
levels, errors_per_hour, users = Counter(), Counter(), Counter()
with open("app.log") as f:
    for line in f:
        m = LINE.match(line)
        if not m:
            continue
        _date, hour, level, user = m.groups()
        levels[level] += 1
        users[user] += 1
        if level == "ERROR":
            errors_per_hour[hour] += 1
print(levels.most_common())
print(sorted(errors_per_hour.items()))
print(users.most_common(3))
```
Explain: `with open` closes the file automatically · `Counter` counts without `if key in dict` · `most_common(n)` sorts by count · compile the regex once outside the loop · the full script adds `argparse` and a `FileNotFoundError` handler.
</details>

<details><summary>D3. Python: check a list of URLs, print status and latency, exit non-zero if any fail (standard library only).</summary>

See [labs/health_check.py](labs/health_check.py): `urllib.request.urlopen(url, timeout=5)`, `time.monotonic()` for latency, catch `HTTPError` (server replied 4xx/5xx) separately from `URLError` (DNS failure, connection refused, timeout), and `sys.exit(0 if all(results) else 1)`. With `requests` installed it's `requests.get(url, timeout=5)` and `r.status_code`.
</details>

<details><summary>D4. Quick Bash: the top 5 IPs in an Nginx access log; and kill every process matching a name.</summary>

`awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -5` · `pkill -f name` (or `pgrep -f name | xargs kill`; SIGTERM first, `-9` only if it ignores it).
</details>

## E. On-call and reliability (type first, then open)

<details><summary>E1. SLI, SLO, SLA, error budget; how much downtime does 99.9% allow per 30 days?</summary>

**SLI** = the measurement (e.g. % of requests that succeed in under 300 ms). **SLO** = the internal target (99.9%). **SLA** = the contract with customers, with penalties, set looser than the SLO. **Error budget** = 100% − SLO = 0.1%. 30 days × 24 × 60 = 43,200 minutes × 0.001 = **43.2 minutes**. When the budget is spent: freeze risky releases, work on reliability.
</details>

<details><summary>E2. A good on-call practice list (what you'd bring to their team).</summary>

Alerts only on user-facing symptoms and with a **runbook link** · severity levels and an escalation path · handover notes between shifts · blameless postmortems with owned action items · track alert noise and delete alerts nobody acts on · MTTD/MTTR measured · game days for the scary failures.
</details>

<details><summary>E3. Networking for Kentik: NetFlow vs sFlow; what BGP does.</summary>

**NetFlow/IPFIX:** the router summarises each flow (source/destination IP and port, protocol, bytes, packets) and exports flow records. **sFlow:** samples 1 in N packets plus interface counters; lighter, statistical. **BGP:** the routing protocol between networks on the internet (autonomous systems, each with an ASN); **eBGP** between organisations, **iBGP** inside one. It picks paths using attributes such as AS path length and local preference. Kentik combines flow data with BGP to show where traffic goes and which networks it crosses. [Likely] level of depth for an SRE role: know the terms, don't pretend to be a network engineer.
</details>

## F. Python programming (the recruiter said to prepare it: expect live coding)

**Rules for a live coding round:**
- Say what you'll do before typing ("I'll loop over the lines, count with a dict, then sort").
- Write the simple version first and make it work. Then improve it.
- Test it out loud with a small example, including an edge case (empty input).
- If you forget a function name, say so and write the plain-loop version. That's fine. Freezing or saying "I didn't practise" isn't.

### F1. The 12 drills (type each from a blank file, then compare)

Solutions with self-tests: [labs/python_drills.py](labs/python_drills.py) (`python3 python_drills.py` prints "all 12 drills pass"). **Don't open it until you've tried.**

1. Reverse a string, two ways (slicing and a loop).
2. Palindrome check that ignores case and punctuation ("A man, a plan, a canal: Panama" → True).
3. Count words in a text and return the top 3 (with `Counter`, then again with a plain dict).
4. FizzBuzz from 1 to n.
5. Find the duplicates in a list.
6. Two-sum: indexes of two numbers that add up to a target, in one pass (use a dict).
7. Second-largest unique number in a list (`[5, 1, 5, 3]` → 3).
8. Flatten a nested list: one level with a comprehension, then fully with recursion.
9. Parse a JSON string of pods and return the names of pods that aren't Running.
10. From access-log lines, group client IPs by status code.
11. Count the vowels in a word; check whether two words are anagrams.
12. A small class `Service(name, port)` with a `restart()` method that counts restarts, and a `__repr__`.

Plus the two ops scripts from section D: `log_report.py` and `health_check.py`.

### F2. Concepts they ask (type first, then open)

<details><summary>F2.1 list vs tuple vs set vs dict: one line each, and which are mutable?</summary>

**list** `[1, 2]`: ordered, mutable, duplicates allowed. **tuple** `(1, 2)`: ordered, **immutable** (can be a dict key). **set** `{1, 2}`: unordered, unique items, fast `in` check. **dict** `{"a": 1}`: key → value, keys unique, insertion-ordered (Python 3.7+). Mutable: list, set, dict. Immutable: tuple, str, int.
</details>

<details><summary>F2.2 List comprehension: squares of even numbers from 1 to 10. Dict comprehension: word → length.</summary>

`[n * n for n in range(1, 11) if n % 2 == 0]` → `[4, 16, 36, 64, 100]` · `{w: len(w) for w in ["pod", "node"]}` → `{'pod': 3, 'node': 4}`
</details>

<details><summary>F2.3 What do *args and **kwargs mean?</summary>

`*args` collects extra positional arguments into a **tuple**; `**kwargs` collects extra keyword arguments into a **dict**. `def f(*args, **kwargs)` accepts anything; used for wrappers and decorators.
</details>

<details><summary>F2.4 try / except / else / finally: what runs when?</summary>

`try` block runs; if an exception matches, its `except` runs; `else` runs only if **no** exception happened; `finally` **always** runs (cleanup). Catch specific exceptions (`FileNotFoundError`, `KeyError`), not a bare `except:`.
</details>

<details><summary>F2.5 Why `with open(...) as f`?</summary>

It's a **context manager**: the file is closed automatically even if an error happens inside the block. Same pattern for locks and DB connections.
</details>

<details><summary>F2.6 `is` vs `==`; and the mutable default argument trap.</summary>

`==` compares values, `is` compares identity (same object); use `is` only for `None`. Trap: `def add(x, items=[])` reuses the **same list** across calls. Use `items=None` and create the list inside.
</details>

<details><summary>F2.7 Generator vs list: what's `yield` for?</summary>

A generator produces items one at a time, so it doesn't hold everything in memory: good for huge log files. `def read_errors(path): for line in open(path): if "ERROR" in line: yield line`. A generator expression: `(x for x in data)`.
</details>

<details><summary>F2.8 How do you run a shell command from Python and get its output?</summary>

`subprocess.run(["df", "-h"], capture_output=True, text=True, check=True).stdout`. Pass a **list** (no `shell=True` with user input, to avoid injection); `check=True` raises if the command fails.
</details>

<details><summary>F2.9 How would you call the AWS API from Python?</summary>

**boto3**: `boto3.client("ec2").describe_instances(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])`. Credentials come from the IAM role/instance profile or `~/.aws/credentials`, never hard-coded. Use paginators for large results.
</details>

<details><summary>F2.10 How do you read environment variables and command-line arguments?</summary>

`os.environ.get("DB_HOST", "localhost")` (with a default) · `sys.argv` for raw arguments, `argparse` for real options (`--top 3`, help text, types).
</details>

---

## Why Kentik (say it, don't read it)

"I've spent the last few years running production platforms on Kubernetes and AWS, and the part I enjoy most is observability and incident response: I built federated Prometheus and Grafana alerting at Koko and handled the incidents that came out of it. Kentik does observability as its product, for networks, and runs a platform that ingests a huge amount of data all the time. That's exactly the kind of system where SRE work matters most, and where I'd learn the networking side more deeply. The stack in the JD (GitOps, Kubernetes, Terraform, Grafana, Bash and Python) is what I use every day."

Don't mention the bench or job security. If asked why you're looking: "My current project ended, and I want SRE to be the core of my job."

## Questions to ask them (pick 2)

1. How is the platform deployed today: one GitOps repo across all clusters, or per team? What's the biggest reliability pain right now?
2. What does on-call look like: rotation size, pages per week, and how are postmortems run?
3. The JD mentions both "Sr" and "entry-level". What level is the role, and what would success look like in the first 90 days?
