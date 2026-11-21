# Interview stories: built from your resume, with follow-up questions

**How this file works:**
- Every story uses the **facts already on your resume**. Where a detail only you know is needed (a count, a date, a tool name), there's a blank: **⟨fill: …⟩**. Fill it with the real value, or a range you can defend ("around 15 services").
- **Never invent a number.** If you can't remember, say "roughly", and explain how it was measured. Interviewers check numbers by asking *how*, and a made-up number breaks on the second follow-up.
- The **follow-up answers** explain *how the technology works*. That part is general knowledge, so it's safe to say. Combine it with your real details.
- **Rehearse each story out loud in 2 minutes:** Situation 20 s → Task 10 s → Action 60 s → Result 20 s → Learning 10 s.

---

## Story 1 · Docker Swarm → EKS migration (Koko Networks)

**Resume line:** migrated applications from Docker Swarm to Kubernetes (EKS) with standardised multi-environment deployments (Dev, UAT, Prod-Int, Production), EKS provisioned with Terraform; 20–30% infrastructure cost reduction during the migration.

**S:** "At Koko, our applications ran on Docker Swarm across ⟨fill: how many⟩ EC2 instances. We had ⟨fill: number of services, e.g. ~15 microservices⟩. Swarm was hard to scale and to keep consistent: ⟨fill: the real pain, e.g. manual scaling, no autoscaling, config drift between environments, limited ecosystem⟩."

**T:** "In a DevOps team of 6–7, I was responsible for ⟨fill: your part, e.g. designing the EKS platform and migrating the services⟩."

**A:**
1. "Provisioned EKS clusters with **Terraform** modules (VPC, subnets across AZs, node groups, IAM roles), one per ⟨fill: per environment, or shared non-prod and separate prod⟩."
2. "Converted the Swarm stack files into Kubernetes manifests / ⟨fill: Helm charts or Kustomize⟩: Deployments, Services, Ingress, ConfigMaps, and Secrets from AWS Secrets Manager."
3. "Standardised four environments, Dev, UAT, Prod-Int and Production, with the same templates and different values."
4. "Set resource requests and limits from real usage, which is where the **right-sizing** came from."
5. "Migrated in stages: ⟨fill: e.g. low-risk services first, ran both platforms in parallel, switched DNS/traffic per service, kept Swarm as the rollback path for ⟨N⟩ days⟩."

**R:** "All ⟨N⟩ services moved with ⟨fill: no / minimal downtime⟩. Infrastructure cost dropped **20–30%**, mainly from right-sizing and better bin-packing. Deployments became consistent across all four environments."

**Learning:** "Measure resource usage *before* migrating; requests and limits based on guesses caused ⟨fill: a real problem you hit, e.g. OOMKills or pending pods⟩."

**Follow-up questions:**

| Question | How to answer |
|---|---|
| Why Kubernetes over staying on Swarm or moving to ECS? | Swarm: smaller ecosystem, weak autoscaling, limited community and tools. EKS: autoscaling (HPA + Cluster Autoscaler/Karpenter), the Helm/ArgoCD ecosystem, standard skills. ECS is simpler but AWS-only and has less tooling. ⟨fill: the reason your team actually gave⟩ |
| How did you migrate without downtime? | Run both side by side, move traffic per service (DNS weight or LB switch), keep the old one as the rollback path, migrate stateless services first and databases are external (RDS) |
| Where did the 20–30% come from exactly? | Right-sizing from real usage (Swarm nodes were over-provisioned), bin-packing many pods per node, fewer idle instances. ⟨fill: before/after node count or monthly bill, if you know it⟩ |
| How did you handle secrets and config? | ConfigMaps for config, AWS Secrets Manager synced to Kubernetes (on your resume), never in Git |
| What went wrong during the migration? | Pick a **real** problem: e.g. a service that assumed a fixed IP or hostname, a missing env var, wrong resource limits, DNS differences (Swarm service names vs `svc.cluster.local`) |
| How were the EKS clusters networked? | VPC across ⟨2–3⟩ AZs, private subnets for nodes, public subnets for the ALB, NAT gateway, VPC CNI: pods get VPC IPs, so subnets need to be large |
| How did traffic reach the apps? | AWS Load Balancer Controller: an Ingress creates an ALB, with subnet tags. Or ⟨fill: what you really used, e.g. ingress-nginx behind an NLB⟩ |
| How many environments and clusters, and why separate them? | Dev, UAT, Prod-Int, Production: isolation and blast radius; Prod-Int is the production-like integration environment |

---

## Story 2 · Jenkins → ArgoCD GitOps, deploy time 10 → 2 minutes (Koko)

**Resume line:** migrated deployment pipelines from Jenkins to ArgoCD, implementing GitOps; reduced deployment time from 10 to 2 minutes with one-click deployments.

**S:** "Deployments were Jenkins jobs that ⟨fill: what they did, e.g. built the image, then ran kubectl/helm against the cluster⟩. Each deploy took about **10 minutes** and ⟨fill: problems, e.g. needed cluster credentials in Jenkins, drift when people ran kubectl by hand, rollbacks were manual⟩."

**T:** "Move deployments to GitOps so Git is the source of truth, and make deploys fast and repeatable."

**A:**
1. "Split CI and CD: Jenkins/⟨fill⟩ still builds, tests and pushes the image to ECR. It then **updates the image tag** in the deployment repo."
2. "Installed ArgoCD in the cluster. Each app is an ArgoCD `Application` pointing at the Git path for its environment, with auto-sync (and self-heal ⟨fill: on/off⟩)."
3. "One-click deploy: ⟨fill: how it worked, e.g. a parameterised job that bumps the tag, or a PR merge⟩."
4. "Rollback = revert the Git commit, or roll back in ArgoCD's history."

**R:** "Deploy time dropped from **10 to 2 minutes**. Jenkins no longer needed cluster-admin credentials, since ArgoCD pulls from Git inside the cluster. Every change is in Git history, and drift is visible as OutOfSync."

**Follow-up questions:**

| Question | How to answer |
|---|---|
| Push vs pull deployment? | Jenkins **pushes** into the cluster (it needs credentials outside the cluster). ArgoCD **pulls**: it runs inside, watches Git, and syncs. More secure, and drift gets detected |
| What exactly made it 10 → 2 minutes? | ⟨fill: the real reasons⟩. Typical: no separate kubectl/helm stage running on Jenkins agents, no queue waiting for agents, ArgoCD applies only the diff, the build is separate from the deploy |
| How do you roll back? | `git revert` the tag change and ArgoCD syncs it, or use ArgoCD's history and rollback (then fix Git, otherwise auto-sync will re-apply it) |
| What are OutOfSync / self-heal / prune? | OutOfSync: the live state differs from Git. Self-heal: ArgoCD reverts manual changes. Prune: deletes resources that were removed from Git |
| How did you handle secrets in GitOps? | They're not in Git: Secrets Manager plus External Secrets / CSI driver ⟨fill: what you used⟩, or Sealed Secrets |
| How do you promote dev → UAT → prod? | Separate paths or branches per environment; promotion = a PR that changes the prod values; ⟨fill: manual sync for prod?⟩ |
| How does the CI pipeline look end to end? | Commit → build → unit tests → SonarCloud scan (on your resume) → docker build → push to ECR → update the tag in the GitOps repo → ArgoCD syncs → health checks |

---

## Story 3 · Federated Prometheus + Grafana alerting, lower MTTD (Koko)

**Resume line:** designed and deployed a federated Prometheus architecture across multiple EKS clusters; Grafana dashboards; proactive alerting for infrastructure and third-party services; reduced MTTD.

**S:** "We had ⟨fill: N⟩ EKS clusters, and each had its own Prometheus. There was no single view, and we often heard about problems from ⟨fill: users / developers / support⟩ before monitoring caught them."

**T:** "Build one central view and alerting across clusters, so we detect issues before users do."

**A:**
1. "Each cluster ran a local Prometheus (⟨fill: kube-prometheus-stack via Helm?⟩) scraping node-exporter, kube-state-metrics and app metrics."
2. "A **central Prometheus scraped the `/federate` endpoint** of each cluster's Prometheus, using `match[]` to pull only the aggregated series we needed, not everything."
3. "Built Grafana dashboards: cluster health, node CPU/memory/disk, pod restarts, ⟨fill: app dashboards⟩."
4. "Set up Alertmanager alerts: node down, pod CrashLoop, high error rate, disk > 80%, certificate expiry, and **third-party checks** (⟨fill: e.g. payment gateway / SMS provider health⟩), routed to ⟨fill: Slack / email / PagerDuty⟩."

**R:** "Most issues were now detected by alerts first. MTTD went from ⟨fill: before, e.g. ~30 min / user-reported⟩ to ⟨fill: after, e.g. under 5 min⟩. ⟨If you don't have numbers: 'we went from mostly user-reported incidents to mostly alert-detected ones'⟩."

**Follow-up questions:**

| Question | How to answer |
|---|---|
| How does federation work? | The central Prometheus scrapes `/federate?match[]=…` on each child Prometheus. It's pull-based; use `honor_labels: true` and add a `cluster` label per source |
| Limits of federation? | The central server can become a bottleneck, data is at scrape resolution only, no long-term storage. At larger scale, use Thanos/Mimir (sidecar or remote_write to S3) |
| Why not just CloudWatch? | Prometheus is richer for Kubernetes and app metrics, PromQL is more flexible, it's open source and cheaper at high cardinality. CloudWatch is still used for AWS-managed services (RDS, ALB) |
| Give a PromQL query you used. | Error rate: `sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))`. Restarts: `increase(kube_pod_container_status_restarts_total[15m]) > 3` |
| How did you avoid alert fatigue? | Alert on symptoms, `for:` durations, severity routing, grouping in Alertmanager, a runbook link per alert, and regular review of noisy alerts |
| How did you monitor third-party services? | ⟨fill: e.g. blackbox exporter probing their endpoints, or app metrics on outbound call errors/latency⟩ |
| How did you measure MTTD? | From incident tickets: time between start of impact and the first alert or ticket. ⟨fill: honestly, how you knew⟩ |

---

## Story 4 · A production incident and its RCA (Koko or Perfios)

**Resume line:** directed incident response and root cause analysis; 99.9% uptime.

**This story must be real, and only you know it.** To help you remember, here are typical EKS/AWS incidents. **Pick the one that actually happened to you**, not one from the list:
- Pods CrashLooping after a deploy (bad config or secret) → rolled back
- A node or subnet ran out of IPs, so pods were stuck Pending
- An SSL certificate expired, or almost did
- RDS connections maxed out / slow queries during peak
- Disk full on a node or volume (logs not rotated)
- A third-party API down, causing failures in your service
- An ALB returning 5xx after a security group / target group change

**Template (fill every line from memory):**
- **S:** "On ⟨month/year⟩, ⟨service⟩ started ⟨symptom: 5xx / timeouts / down⟩ for ⟨who: all users / X%⟩ around ⟨time⟩."
- **T:** "I was ⟨on-call / incident lead⟩."
- **A (in order):**
  1. "Detected via ⟨alert / user report⟩."
  2. "First checked ⟨dashboard / kubectl get pods / ALB target health⟩ and saw ⟨evidence⟩."
  3. "Mitigated by ⟨rollback / restart / scaling / freeing disk⟩ within ⟨N⟩ minutes."
  4. "Communicated on ⟨Slack/bridge⟩ to ⟨who⟩."
  5. "Root cause was ⟨the real cause⟩, found with ⟨logs / CloudTrail / metrics⟩."
- **R:** "Service restored in ⟨N⟩ minutes. Prevention: ⟨alert added / runbook / Terraform change / PodDisruptionBudget / limits⟩. It hasn't happened again since."

**Follow-up questions:**

| Question | How to answer |
|---|---|
| What would you do differently? | Something honest: detect earlier (an alert that was missing), a faster rollback path, better communication |
| How did you find the root cause? | Timeline, then evidence (logs, metrics, CloudTrail "what changed"), then 5 Whys until you reach a process cause, not "human error" |
| How was 99.9% measured? | ⟨fill: uptime checks / SLO dashboard / incident minutes per month⟩. 99.9% = about 43 minutes of downtime allowed per 30 days. If it's an estimate, say "based on incident downtime per month" |
| Who did you escalate to? | ⟨fill: dev team lead / vendor / AWS support⟩, and when (time-box, e.g. after 30 minutes without progress on a P1) |
| Was there a postmortem? | Yes: blameless, with timeline, impact, root cause and action items with owners. ⟨fill: where it was documented⟩ |

---

## Story 5 · EKS upgrades and SSL renewals (Koko)

**Resume line:** directed SRE activities such as EKS upgrades, SSL renewals, cluster migrations and production release coordination.

**S/T:** "I owned EKS version upgrades across ⟨N⟩ clusters, e.g. from ⟨1.xx⟩ to ⟨1.yy⟩, because EKS versions go out of standard support after about 14 months."

**A:**
1. "Checked the release notes and **deprecated APIs** with ⟨fill: pluto / kubent / kubectl deprecations⟩, and fixed the manifests and Helm charts first."
2. "Upgraded **one minor version at a time**, in dev, then UAT, then Prod-Int, then prod."
3. "Order: control plane (⟨fill: Terraform `cluster_version` change⟩) → add-ons (VPC CNI, CoreDNS, kube-proxy, EBS CSI) → node groups (rolling update, with PodDisruptionBudgets so apps stayed up)."
4. "Validated: nodes Ready, pods healthy, smoke tests, dashboards."

**R:** "Upgrades with ⟨fill: zero / minimal⟩ downtime; clusters stayed in standard support."

**SSL:** "Certificates were ⟨fill: ACM on ALBs / cert-manager with Let's Encrypt / manual⟩. I ⟨fill: renewed them / automated renewal / added expiry alerts⟩." Good addition if true: "added an alert 30 days before expiry, so renewals stopped being emergencies."

**Follow-up questions:**

| Question | How to answer |
|---|---|
| Why one minor version at a time? | EKS (and Kubernetes) only supports upgrading the control plane one minor version per step. The kubelet can lag the API server by a limited number of versions, so nodes follow |
| What breaks most often in upgrades? | Removed APIs (e.g. old `extensions/v1beta1` Ingress, PodSecurityPolicy removed in 1.25), add-on versions that don't match, Helm charts using old APIs |
| How do you keep apps up while nodes rotate? | PodDisruptionBudgets, multiple replicas spread across AZs, readiness probes, graceful shutdown (`terminationGracePeriodSeconds`, preStop hook) |
| Can you roll back an EKS control-plane upgrade? | **No.** That's why you test in lower environments first, and why some teams do blue/green clusters |
| How does ACM auto-renewal work? | DNS-validated certificates renew automatically as long as the validation CNAME stays in Route 53. Email-validated ones need someone to approve |

---

## Story 6 · Docker image size −30–40% (Koko)

**A:** "Moved to **multi-stage builds** (build tools only in the build stage) and **minimal base images** (⟨fill: e.g. alpine / slim / distroless⟩), ordered layers so dependencies are cached (copy the dependency file → install → copy code), added `.dockerignore`, and ran as a non-root user. Example: ⟨fill: one real image, before ⟨X⟩ MB → after ⟨Y⟩ MB⟩."
**R:** "30–40% smaller images, so faster pulls and faster deployments and scale-up, and fewer vulnerabilities in scans."

**Follow-ups:** What's in the final image of a multi-stage build? Why does layer order matter for the cache? Alpine pitfalls (musl vs glibc)? How do you scan images (ECR scan on push / Trivy)?

---

## Story 7 · Ansible: environment setup 2 h → 20 min (Perfios)

**A:** "Wrote Ansible playbooks/roles for ⟨fill: OS hardening, packages, users, SSH config, agents (monitoring/logging), app runtime⟩, run against new EC2 instances ⟨fill: after Terraform creates them / via dynamic inventory⟩."
**R:** "Setup dropped from ~2 hours of manual steps to ~20 minutes (~80%), and every server was configured identically."

**Follow-ups:**

| Question | How to answer |
|---|---|
| Idempotency? | Running the playbook twice changes nothing the second time, because modules check the state first |
| Terraform vs Ansible? | Terraform *provisions* infrastructure (declarative, with state). Ansible *configures* what's inside the servers (procedural/declarative tasks, agentless over SSH) |
| How did you manage inventory? | ⟨fill: static file / AWS dynamic inventory plugin by tags⟩ |
| Secrets in Ansible? | Ansible Vault, or a lookup from SSM/Secrets Manager |

---

## Story 8 · FinOps: −30% EKS cost (One2N)

Already prepared in the FinOps thread. The short version:
- **Levers:** gp3 (about 20% cheaper than gp2 with a flat 3000 IOPS baseline), Graviton (about 20% cheaper per hour, needs arm64/multi-arch images), keeping telemetry in one AZ (cross-AZ data costs $0.01/GB in each direction).
- **Be ready to explain:** what the 30% is measured against, and that single-AZ telemetry was a deliberate trade-off (it isn't on the customer request path).
- **Dashboards:** CUR to S3, then Athena/Glue, then QuickSight for product management.

---

## Final rehearsal checklist (tonight)

- [ ] Fill every ⟨fill⟩ in stories 1–5 with real values or honest ranges
- [ ] Say each story out loud in 2 minutes (use a timer)
- [ ] For each story, answer 3 follow-ups out loud without reading
- [ ] Pick the **one incident** for Story 4 and write its timeline in 5 lines
