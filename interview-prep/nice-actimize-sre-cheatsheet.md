# NiCE Actimize · Application Support Engineer / SRE · F2F cheat sheet

**Interview:** 11 Nov 2026, 2:00 PM IST, face to face. R Systems is the employer and NiCE Actimize is the client, in Pune (Hinjawadi Phase 2).
**Rule from NiCE:** only mention tools that are on your resume. Expect them to dig into practical scenarios for every tool you list.

![Incident lifecycle and ITIL](diagrams/n1-incident-lifecycle.drawio.svg)

---

## 0. The rule that decides this interview

- Before you go in, mark every JD line as one of three:
  - **Used in production.** You need a story with numbers.
  - **Know the concept.** Say so plainly: "I know how it works, but I haven't run it in production."
  - **Never used.** Use the honest line below.
- **The honest line:** "I haven't used *Dynatrace* in production. I've used *[your tool]* for the same job: dashboards, alerts and log search. The concepts carry over, and I'd get productive in it quickly."
- **When you don't know:** "I'm not sure. Here's how I'd find out: logs first, then docs, then a test in a lower environment." NiCE's own instructions say an honest "I don't know" beats a guess.
### Your resume vs this JD

| JD asks for | On your resume? | How to play it |
|---|---|---|
| L2/L3 production support, incidents, RCA | Yes: Koko (incident response, RCA, 99.9% uptime, EKS upgrades, SSL renewals, release coordination), One2N (production support, troubleshooting) | Your main ground. Describe your DevOps work in support terms: detect, triage, mitigate, RCA, prevent |
| Linux + Shell scripting | Shell yes (BridgeLabz, daily ops) | Type section 5 commands tomorrow; they will test this |
| Python automation | "Python (Basic)" | Say "basic": you read and change scripts, your automation is mostly Shell, Jenkins, Ansible, Terraform. Don't oversell |
| SQL | Listed; MySQL, PostgreSQL, RDS | Expect live queries. Practise section 7 |
| Monitoring tools | Prometheus, Grafana, Nagios; ELK only as trainee (2020–21) | Lead with federated Prometheus + Grafana + alerting. ELK: say it was early-career. **Not** Dynatrace, AppDynamics, Datadog, Splunk, New Relic → honest line |
| Tomcat / Apache / Nginx / WebLogic / JBoss | **No** | Biggest gap. "My apps ran as containers on EKS behind load balancers, so I didn't run Tomcat directly. I know how it works:" then section 8 at concept level |
| ITIL, ServiceNow / JIRA / PagerDuty | **No** | Know the concepts (section 3). Describe the process you followed (alert → triage → fix → RCA → change via release coordination) without naming tools you didn't use |
| Git, deployment / release management | Yes, strong: GitLab CI, Jenkins → ArgoCD (10 → 2 min), Dev/UAT/Prod releases | Strong story |
| 24x7 / on-call | Not stated | Say what you actually did (on-call rotation? escalation?) and that you're fine with shifts |
| AWS, Docker, Kubernetes, CI/CD, Terraform, Ansible (good to have) | Yes, your strongest area | This is your differentiator. Bring answers back here when you can |
| SLI/SLO, error budgets | Partly: 99.9% uptime, MTTD | Know section 4 numbers cold, because you claim 99.9% |
| Kafka / RabbitMQ / Redis | **No** | Don't claim |
| Certifications | "AWS Cloud Practitioner **Essentials**" is the free training course, not the AWS Certified Cloud Practitioner exam. KodeKloud Docker is a course certificate | If they read it as the AWS certification, correct them yourself. Being caught later is far worse |

**Claims they will ask you to prove (have the numbers ready):**
- **99.9% uptime** (Koko and Perfios): measured how, over what period, on which services? What took the remaining 0.1%?
- **20–30% cost cut during the EKS migration** and **30% EKS cost cut at One2N**: compared with what, and how much from each lever?
- **Image size −30–40%**, **deploy time 10 → 2 min**, **setup 2 h → 20 min**: what changed exactly?
- **"Directed incident response and RCA"**: name one incident, its impact, and your role.
- **Dates:** your Oct 2026 interview notes describe One2N expectations for "1.5–2 years". If anyone asks about your One2N role or the Jan–Mar 2026 gap, answer plainly and consistently with the resume. Background verification will check dates.

- **Questions you should expect on your resume points:** what the 30% EKS saving was measured against and how it splits by lever (gp3, Graviton, cross-AZ), and why telemetry in a single AZ is acceptable. See the FinOps thread notes.

## 1. Your 60-second introduction (fill it in)

"I'm a ___ with ___ years of experience at ___. Day to day I ___ (support / monitor / deploy / automate) ___ (which apps, on what stack). I handle ___ (incidents, on-call, releases). One thing I'm proud of: ___ (a result with a number). I'm looking for an L2/L3 / SRE role where I own reliability end to end, and the financial-crime domain at Actimize is where reliability matters most."

**Draft from your resume (edit it into your own words):**
"I'm a Site Reliability Engineer with about five and a half years in production operations on AWS. I'm currently SRE II at One2N, where I support Kubernetes production environments and set up the Prometheus and Grafana stack for monitoring and alerting. Before that, at Koko Networks, I migrated applications from Docker Swarm to EKS, ran the production side (EKS upgrades, SSL renewals, release coordination, incident response and RCA), and held 99.9% uptime. I started at Perfios, building AWS infrastructure with Terraform and Ansible and supporting Dev, UAT and Prod releases. I want to move closer to the application side: owning the reliability of business-critical apps, and Actimize, in the fintech and compliance space I already know from Perfios, is a good fit for that."

- [Likely] Perfios builds financial data and analytics software for banks and lenders. That makes it your banking/financial-services link to the JD's preferred domains. Only use it if it's accurate for your work there.

## 2. STAR incident stories (prepare 3, 2 minutes each)

| Letter | What to say | Example prompt |
|---|---|---|
| **S**ituation | System, time, who was affected, business impact | "Payment API returned 5xx for 40 min, ~20% of requests" |
| **T**ask | Your role (L2 on-call, incident owner…) | "I was primary on-call" |
| **A**ction | What *you* did, in order: triage, mitigation, communication, evidence | "Checked dashboards, saw DB connection-pool exhaustion, restarted the pool, raised a bridge, updated stakeholders every 30 min" |
| **R**esult | Numbers + permanent fix + what changed after | "Restored in 25 min; RCA found a missing index; added alert on pool usage > 80%; no repeat in 3 months" |

Have these three kinds ready:
1. **A P1 or major incident** that you mitigated under pressure.
2. **An RCA** where the root cause wasn't obvious and you found it with logs or metrics.
3. **An automation** that removed toil, such as a script that cut a manual task from X min to Y min.

**Candidates from your resume.** Pick real incidents. Don't invent any details:

| Story type | Resume source | What to have ready |
|---|---|---|
| P1 / major incident | Koko: "Directed incident response and RCA" | The worst outage you handled: what alerted, the impact, your first 3 actions, who you pulled in, time to restore |
| RCA / detection | Koko: federated Prometheus, proactive alerting for infra and third-party services, MTTD reduced | An incident you caught earlier because of an alert you built. Before vs after detection time |
| Risky change done safely | Koko: Docker Swarm → EKS migration, EKS upgrades, SSL renewals | How you did cutover and rollback, what broke, how you validated. An expired or near-expired certificate story fits "proactive" well |
| Automation / toil | Perfios: Ansible setup 2 h → 20 min; Koko: Jenkins → ArgoCD (10 → 2 min), RDS backup automation via Jenkins | What was manual before, what the script/pipeline does, how you know it works (and that the backup restores!) |

**Likely follow-ups:** What would you do differently? How did you stop it from happening again? Who did you escalate to, and when?

## 3. Incident, problem, change (ITIL)

| | Incident | Problem | Change |
|---|---|---|---|
| Goal | Restore service fast | Find and remove the root cause | Apply changes safely |
| Trigger | Alert, user ticket | Recurring incidents, any P1 | Fix, release, config change |
| Output | Service restored, ticket closed | RCA, known error, workaround | Approved CR, implemented with rollback plan |
| Metric | MTTR, SLA breach count | Repeat incidents | Change success rate, change-caused incidents |

- **Priority = impact × urgency.** P1 means a critical service is down for many users with no workaround. P4 is a minor single-user issue.
- **Change types:**
  - **Standard** changes are pre-approved and low risk.
  - **Normal** changes go to CAB (Change Advisory Board) review.
  - **Emergency** changes are fast-tracked during an incident and reviewed afterwards.
- **Service request vs incident:** "Give me access" is a request. "It's broken" is an incident.
- **Known Error Database (KEDB):** records known problems and their workarounds, so L1/L2 can resolve repeats quickly.
- **Major incident handling:**
  1. Declare the major incident and open a bridge call.
  2. Assign roles: incident commander, communications lead, technical leads.
  3. Send stakeholder updates on a fixed cadence.
  4. Mitigate first.
  5. Write the RCA and hold a blameless post-mortem within 24–72 hours.
  6. Track action items to closure.
- **RCA techniques:**
  - **5 Whys:** keep asking why until you reach a process or design cause, not "human error".
  - **Timeline:** detection, response, mitigation, resolution.
  - **Fishbone:** people, process, technology, environment.

## 4. SLI, SLO, SLA, error budget

![SLI to SLO to error budget](diagrams/c3-slo-error-budget.drawio.svg)

- **SLI (Service Level Indicator)** is what you measure, for example the % of requests that succeed in under 500 ms.
- **SLO (Service Level Objective)** is the internal target, for example 99.9% over 30 days.
- **SLA (Service Level Agreement)** is the contract with the customer, with penalties. It is set looser than the SLO, so you get warned before you breach it.
- **Error budget** (no abbreviation) = 100% − SLO, the amount of failure the SLO allows. For 99.9% over 30 days, that's about 43 minutes. For 99.95%, about 21.6 minutes. For 99.99%, about 4.3 minutes.
- **When the budget is burnt:** freeze risky releases and spend the time on reliability work. When budget is left, ship faster.
- **Formulas:**
  - Availability SLI = good requests ÷ total valid requests × 100
  - Error budget (requests) = (1 − SLO) × total requests. Error budget (time) = (1 − SLO) × minutes in the window (30 days = 43,200 min)
  - Budget consumed % = actual bad ÷ allowed bad × 100
  - Burn rate = current error rate ÷ (1 − SLO). Google's SRE workbook pages at 14.4× over 1 h, which burns 2% of the 30-day budget in an hour
  - Availability = MTBF ÷ (MTBF + MTTR)
  - Serial dependencies: A × B (99.9% × 99.9% = 99.8%). Redundant pair: 1 − (1−A)(1−B) (two 99.9% replicas = 99.9999%)
- **Worked example:**
  - 10,000,000 requests in 30 days, 4,000 failed, so SLI = 99.96%.
  - The 99.9% SLO allows 10,000 failures, so 40% of the budget is used and 60% is left.
  - An error rate of 0.5% means a burn rate of 5×, so the budget is gone in 6 days.
- **Downtime allowed:**

  | SLO | Per 30 days | Per year |
  |---|---|---|
  | 99% | 7.2 h | 3.65 days |
  | 99.5% | 3.6 h | 1.83 days |
  | 99.9% | 43.2 min | 8.76 h |
  | 99.95% | 21.6 min | 4.38 h |
  | 99.99% | 4.32 min | 52.6 min |
- **PromQL availability:** `sum(rate(http_requests_total{code!~"5.."}[30d])) / sum(rate(http_requests_total[30d]))`
- **"Why not 100%?"** Each extra nine costs far more, users can't tell the difference because their own network fails more often, and a 100% target leaves no room to ship changes.
- **Golden signals:** latency, traffic, errors, saturation. RED (rate, errors, duration) is for services. USE (utilisation, saturation, errors) is for resources.
- **Other terms:**
  - **MTTD:** mean time to detect.
  - **MTTR:** mean time to restore.
  - **MTBF:** mean time between failures.
  - **Toil:** manual, repetitive work that should be automated.

## 5. Linux troubleshooting (type these, don't just read them)

![Linux triage order](diagrams/n2-linux-triage.drawio.svg)

| Symptom | Commands | What you're looking for |
|---|---|---|
| Service down | `systemctl status app`, `journalctl -u app --since "30 min ago"`, `ps -ef \| grep java` | Crashed? OOM-killed? Exit code? |
| Port not reachable | `ss -tlnp \| grep 8080`, `curl -v http://localhost:8080/health`, `nc -zv host 8080`, `firewall-cmd --list-all` / `iptables -L` | Listening only on 127.0.0.1? Firewall? |
| High CPU | `top` (press `P`), `ps aux --sort=-%cpu \| head`, `top -H -p <pid>` (threads), `jstack <pid>` | Which process/thread; Java busy thread → convert TID to hex, find in thread dump |
| High memory / OOM | `free -h`, `ps aux --sort=-%mem \| head`, `dmesg -T \| grep -i oom`, `jmap -heap <pid>` / heap dump | Leak? Heap too small? OOM killer? |
| Disk full | `df -h`, `du -sh /var/log/* \| sort -h \| tail`, `find / -size +1G 2>/dev/null` | Logs not rotated; check `logrotate` |
| Disk "full" but `df -h` is fine | `df -i` | Inodes exhausted (millions of tiny files) |
| Space not freed after delete | `lsof +L1` or `lsof \| grep deleted` | A process still holds the deleted file. Restart it, or truncate with `> file` next time |
| Load high, CPU low | `uptime`, `vmstat 1 5`, `iostat -x 1 5` | I/O wait (`wa`), slow disk/NFS |
| Network/DNS | `ping`, `traceroute`, `nslookup` / `dig host`, `telnet host port`, `curl -kv https://…` | DNS, routing, TLS cert expired? |
| Who changed what | `last`, `history`, `ls -lt /etc \| head`, `rpm -qa --last \| head` | Recent change = prime suspect |

**Log analysis one-liners**
```bash
grep -i "error\|exception" app.log | tail -50
grep -c "ERROR" app.log                                  # count errors
grep "11/Nov/2026:13:" access.log | awk '{print $9}' | sort | uniq -c | sort -rn   # HTTP status counts for one hour (nginx/apache)
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head    # top client IPs
awk '$NF > 2' access.log                                 # slow requests, if response time is the last field
sed -n '/13:00:00/,/13:15:00/p' app.log                  # lines between two times
zgrep "OutOfMemoryError" app.log.*.gz                   # search rotated logs
tail -f app.log | grep --line-buffered ERROR
```

**Permissions and processes:** `chmod 640 f`, `chown app:app f`, `kill -15 <pid>` (graceful) before `kill -9` (forced), `nohup cmd &`, `crontab -l` (`m h dom mon dow`).

## 6. Shell and Python automation (show you can write a small one)

```bash
#!/bin/bash
# disk_alert.sh: warn when any filesystem is above a threshold (run from cron every 10 min)
THRESHOLD=85
df -hP | awk 'NR>1 {gsub("%","",$5); print $5, $6}' | while read use mount; do
  if [ "$use" -ge "$THRESHOLD" ]; then
    echo "$(date '+%F %T') WARNING: $mount at ${use}%" | tee -a /var/log/disk_alert.log
  fi
done
```

```bash
# health check with retry, then restart
for i in 1 2 3; do
  curl -sf http://localhost:8080/health && exit 0
  sleep 10
done
systemctl restart app && echo "restarted app at $(date)" >> /var/log/app_restart.log
```

```python
# count errors per hour in a log
import re, collections
counts = collections.Counter()
with open("app.log") as f:
    for line in f:
        if "ERROR" in line:
            m = re.match(r"(\d{4}-\d{2}-\d{2} \d{2})", line)
            if m:
                counts[m.group(1)] += 1
for hour, n in sorted(counts.items()):
    print(hour, n)
```

**Say it:** "Whenever I do something manually a third time, I script it. Then I make it idempotent, log what it did, and alert when it fails."

## 7. SQL for data validation and troubleshooting

[Likely] Actimize runs on Oracle or SQL Server databases and processes data in batch (loading transactions, generating alerts). So expect questions like "the data didn't arrive" and "the counts don't match".

```sql
-- rows per day: did yesterday's load arrive?
SELECT CAST(created_at AS DATE) AS day, COUNT(*) FROM transactions
GROUP BY CAST(created_at AS DATE) ORDER BY day DESC;

-- duplicates
SELECT txn_id, COUNT(*) FROM transactions GROUP BY txn_id HAVING COUNT(*) > 1;

-- remove duplicates, keep the latest (window function)
WITH ranked AS (
  SELECT t.*, ROW_NUMBER() OVER (PARTITION BY txn_id ORDER BY updated_at DESC) AS rn
  FROM transactions t)
SELECT * FROM ranked WHERE rn = 1;

-- rows in source but missing in target (reconciliation)
SELECT s.txn_id FROM staging_txn s
LEFT JOIN transactions t ON t.txn_id = s.txn_id
WHERE t.txn_id IS NULL;

-- count mismatch between source and target
SELECT (SELECT COUNT(*) FROM staging_txn) AS src, (SELECT COUNT(*) FROM transactions) AS tgt;

-- NULLs in mandatory columns
SELECT COUNT(*) FROM customers WHERE account_no IS NULL OR TRIM(account_no) = '';

-- top 5 customers by amount in the last 7 days
SELECT customer_id, SUM(amount) AS total FROM transactions
WHERE created_at >= CURRENT_DATE - 7            -- Oracle: SYSDATE - 7
GROUP BY customer_id ORDER BY total DESC FETCH FIRST 5 ROWS ONLY;   -- MySQL/Postgres: LIMIT 5

-- second highest salary (classic)
SELECT MAX(salary) FROM emp WHERE salary < (SELECT MAX(salary) FROM emp);

-- failed batch jobs today
SELECT job_name, status, start_time, end_time FROM job_runs
WHERE status = 'FAILED' AND start_time >= CURRENT_DATE;
```

| Concept | One-liner |
|---|---|
| INNER vs LEFT JOIN | INNER = only matches; LEFT = all left rows, NULLs where no match (use for "missing" checks) |
| WHERE vs HAVING | WHERE filters rows before grouping; HAVING filters groups after |
| `COUNT(*)` vs `COUNT(col)` | `COUNT(col)` skips NULLs |
| `= NULL` | Never true: use `IS NULL` |
| DELETE vs TRUNCATE vs DROP | DELETE rows (can rollback, WHERE allowed); TRUNCATE all rows, fast, minimal logging; DROP removes the table |
| UNION vs UNION ALL | UNION removes duplicates (slower) |
| Index | Speeds reads on filtered/joined columns, slows writes; check with `EXPLAIN` / `EXPLAIN PLAN` |
| Slow query triage | Execution plan → full table scan? missing index? stale stats? locks (`v$session` / `sp_who2`)? |
| Transactions | `BEGIN … COMMIT / ROLLBACK`; in production run `SELECT` with the same `WHERE` before any `UPDATE/DELETE` |

## 8. Tomcat, Apache, Nginx basics

| | Tomcat | Nginx / Apache httpd |
|---|---|---|
| What | Java servlet container (runs `.war` apps) | Web server / reverse proxy / load balancer |
| Default port | 8080 (HTTP), 8005 (shutdown), 8443 (HTTPS) | 80 / 443 |
| Config | `conf/server.xml` (connectors, ports, threads), `conf/context.xml` (DB pools/JNDI), `bin/setenv.sh` (`JAVA_OPTS`, `-Xms -Xmx`) | `/etc/nginx/nginx.conf`, `conf.d/*.conf`; Apache `httpd.conf` |
| Logs | `logs/catalina.out`, `localhost_access_log.*.txt`, app logs | `/var/log/nginx/access.log`, `error.log` |
| Deploy | Drop `.war` in `webapps/` (auto-deploy) or Manager app | `nginx -t` then `systemctl reload nginx` (no downtime) |
| Start/stop | `bin/startup.sh`, `bin/shutdown.sh`, or `systemctl` | `systemctl start/stop/reload` |

> **Not on your resume.** Answer at concept level and say so: "I haven't administered Tomcat directly. Our services ran as containers on EKS behind load balancers. Here's how I'd troubleshoot it…" The 502/504 and thread-dump logic below applies just as much to pods behind an ingress or ALB, which you can speak to from experience.

**Common errors and what they mean**
- **502 Bad Gateway** (Nginx): the backend (Tomcat) is down or refusing connections. Check that Tomcat is up and listening, and check `proxy_pass`.
- **504 Gateway Timeout:** the backend is too slow. Look for a slow DB, thread exhaustion or GC pauses. Raise `proxy_read_timeout` only after you know the cause.
- **503:** the backend is overloaded or in maintenance, or the upstream has no healthy servers.
- **`java.lang.OutOfMemoryError: Java heap space`:** take a heap dump and check for a leak, then increase `-Xmx` if it's justified.
- **`Address already in use`:** the port is taken. Use `ss -tlnp | grep 8080` to see by what.
- **All threads busy / requests hang:** use `jstack <pid>` and look for threads that are BLOCKED or waiting on the DB. Check `maxThreads` in `server.xml` and the size of the DB connection pool.

**Thread dump routine:** take 3 `jstack` dumps about 10 seconds apart. If the same threads are stuck in the same place in all three, that's your bottleneck.

**Nginx reverse proxy snippet**
```nginx
upstream app { server 10.0.1.10:8080; server 10.0.1.11:8080; }
server {
  listen 443 ssl;
  server_name app.example.com;
  location / { proxy_pass http://app; proxy_set_header Host $host; proxy_read_timeout 60s; }
}
```

## 9. Monitoring and observability (only the tools you used)

- **The three signals:**
  - **Metrics** tell you *that* something is wrong (Prometheus, Grafana, CloudWatch).
  - **Logs** tell you *what* happened (ELK, Splunk, Loki).
  - **Traces** tell you *where* in the call chain (Jaeger, APM tools).
- **MELT** (the four telemetry types; New Relic popularised the term):

  | | What it is | Answers | Example | Your tool |
  |---|---|---|---|---|
  | **Metrics** | Numbers over time, cheap to store and aggregate | *Is* something wrong? | CPU 92%, 5xx rate 2%, p99 800 ms | Prometheus, Grafana |
  | **Events** | Discrete significant happenings at a point in time | *What changed?* | Deploy, config change, pod restart, scaling, alert fired | `kubectl get events`, ArgoCD sync history |
  | **Logs** | Detailed timestamped text records | *Why* did it break? | `ERROR Connection refused db:5432` | ELK (trainee), `kubectl logs` |
  | **Traces** | One request followed across services as spans | *Where* is it slow? | API 2 s = 50 ms auth + 1.9 s payment-db | Jaeger / APM (not on your resume) |

  **Say it:** "A metric alert tells me error rate is up. I check events for a deploy or config change at that time, logs give me the actual error, and traces show which downstream call is slow."
- **Good alerting:**
  - Alert on symptoms users feel, like error rate or latency SLO burn, not on every CPU spike.
  - Every alert needs an owner and a runbook.
  - Cut noise. Alert fatigue means real alerts get missed.
- **Proactive monitoring examples:** disk growth trend, certificate expiry (alert 30 days ahead), batch job not finishing by its expected time (an absence alert), queue depth, DB connection-pool usage.
- **Your tools, in order of strength:**
  - **Prometheus + Grafana:** federated Prometheus across multiple EKS clusters, dashboards, proactive alerting (Koko). The observability stack setup at One2N. Be ready for: what federation is (a central Prometheus scrapes selected series from per-cluster Prometheus via `/federate`); why (one view across clusters); its limits (the central server is a bottleneck, and long-term storage usually needs Thanos/Mimir); Alertmanager routing and grouping; a PromQL example such as `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))` for error rate.
  - **Nagios** (Perfios): host and service checks for EC2 health, with OK/WARNING/CRITICAL/UNKNOWN states from check plugins.
  - **ELK** (BridgeLabz trainee): Filebeat/Logstash → Elasticsearch → Kibana. Present it as early-career exposure.
- **APM tools** (Dynatrace, AppDynamics, New Relic, Datadog) auto-instrument the JVM and show response time per transaction, slow DB calls and errors. **If they aren't on your resume, use the honest line from section 0.**

## 10. Deployments, releases, Git

- **Release checklist:**
  1. Get CR approval.
  2. Take a backup (DB and config).
  3. Do a pre-check of health and baseline metrics.
  4. Deploy.
  5. Run smoke tests.
  6. Monitor for 30–60 minutes.
  7. Roll back if a criterion fails, with the rollback decided before you start.
- **Strategies:** rolling, blue-green (switch traffic, instant rollback) and canary (small % of traffic first).
- **Git basics:** `git log --oneline`, `git diff`, `git revert <sha>` (safe on shared branches) vs `git reset` (rewrites history), branches, PR review, tags for releases.
- **Config changes:** keep them version-controlled, peer-reviewed, and applied through a CR, not edited directly on the server.

## 11. On-call and 24x7

- **Handover notes** at the end of each shift: open incidents, ongoing changes, things to watch.
- **Escalation matrix:** L1 → L2 (you) → L3/dev → vendor. Escalate on a time box, for example after 30 minutes on a P1 with no progress, not when you're out of ideas.
- **Runbooks** for frequent alerts, so a 3 AM fix doesn't depend on memory.
- **Say it:** "I'm comfortable with rotational shifts and on-call. I keep runbooks current and write handover notes, and I treat repeat pages as problems to fix, not something to live with."

## 12. Actimize context (10 minutes, don't overclaim)

- [Certain] NiCE Actimize sells financial-crime, risk and compliance software to banks: anti-money laundering (AML), fraud detection, trade surveillance and customer due diligence.
- [Likely] Support work looks like this:
  - Batch jobs that load transactions and generate alerts.
  - Rules or analytics engines.
  - Large Oracle/SQL Server databases.
  - Java web apps on application servers.
  - Strict change control, because the customers are regulated banks.
- **Why it matters for you:** if a job fails at night, the bank's compliance team may miss suspicious activity. So data completeness checks (section 7) and on-time batch SLAs carry as much weight as uptime.

## 13. Questions to ask them

1. How is work split between your L2/L3 team and NiCE product engineering? What do I own end to end?
2. What were the top recurring incidents last quarter, and what does the on-call rotation look like?
3. Which SLOs or SLAs will I be measured on in my first 90 days?

## 14. Logistics checklist

- [ ] Original government ID. The gate pass is already requested, so show your ID at the tech park security desk.
- [ ] 3 printed copies of your resume, the same version you sent R Systems.
- [ ] Pen and a small notebook. Phone charged.
- [ ] Address: Embassy Tech Zone, Plot 3A, Hinjawadi Phase 2, Rajiv Gandhi Infotech Park, Pune 411057. NiCE office: Block Rhine, Wings A & B.
- [ ] **Order of steps:**
  1. Tech park gate (show ID).
  2. **Wing A, 8th floor** security desk for the temporary access ID.
  3. **Wing B, 3rd floor (3B)** reception: say you're there for the 2 PM interview.
- [ ] **Arrive at the gate by 1:20 PM** so you reach 3B by 1:45. Hinjawadi traffic at midday is unpredictable.
