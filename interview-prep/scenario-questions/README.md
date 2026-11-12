# 🎯 Scenario Questions: AWS, Docker, Kubernetes, Terraform, Prometheus

A real first-round question list someone else was asked (shared 12 Nov 2026), answered one question per file in the same format as the [Terraform](../terraform/README.md), [Kubernetes](../kubernetes/README.md) and [Docker](../docker/README.md) notes. These are **scenario** questions: "X broke / you need Y, what do you do?" The interviewer wants a **structured method**, not a definition.

## How to use these notes (read this first)

On 11 Nov the basics were known but **couldn't be typed or said under pressure**. Reading these files will not fix that. For each file:

1. Read the **Say this first** box once.
2. Close the file. Say the **🗣️ 30-second spoken answer** out loud, timed, without looking. Record yourself if you can.
3. Do the **🎯 Drill**: type every command / YAML / HCL block in it into an empty editor or terminal **from memory**, then diff against the note.
4. Only then read the detail sections for the follow-up questions.
5. Next day: repeat steps 2–3 for yesterday's files before starting new ones.

- ⭐ = very likely in a DevOps/SRE interview, or very close to your resume.
- **Resume check** in every file says which tools match your resume (AWS, EKS, Terraform, Ansible, GitLab CI, Jenkins, Argo CD, Prometheus, Grafana, Nagios, MySQL/Postgres) and which **don't** (for example Lambda, multi-cloud, Kyverno/OPA, Karpenter, KEDA, Velero, Splunk, Kafka, Redis, PagerDuty). Name those as "what I'd use", never as "what I ran".
- **Real-world example** sections are **suggested stories**. Tell only the parts that match what you really did and swap in your own details. Where you have no experience (Lambda, multi-cloud), the note says so and gives a transferable story instead.
- Nothing here was run against a real AWS account or cluster (no AWS/kubectl access in the environment where these were written); commands and YAML/HCL are real syntax and the YAML/JSON blocks were parse-checked, but snippets marked *(illustrative)* weren't applied anywhere. Check versions (Kubernetes, Terraform, AWS provider) before quoting a version number in an interview.

## Contents

### AWS

| # | File | Question |
|---|---|---|
| 01 ⭐ | [HA EC2 across AZs](aws/01-ha-ec2-multi-az.md) | Design a highly available EC2 architecture across multiple AZs for a web application. |
| 02 ⭐ | [Migrate EC2 to another region](aws/02-migrate-ec2-to-another-region.md) | Migrate a running EC2 instance to another region with minimal downtime. |
| 03 ⭐ | [SSH not reachable](aws/03-ec2-ssh-not-reachable.md) | EC2 instance not reachable via SSH: troubleshooting steps. |
| 04 ⭐ | [Auto scaling for spikes](aws/04-auto-scaling-spiky-traffic.md) | Unpredictable traffic spikes: scaling policies while optimizing cost. |
| 05 | [Scheduled vs dynamic scaling](aws/05-scheduled-vs-dynamic-scaling.md) | When is scheduled scaling more appropriate than dynamic scaling? |
| 06 | [S3 backup bucket unavailable](aws/06-s3-backup-bucket-unavailable.md) | Your S3 bucket storing critical backups becomes unavailable. How do you recover? |
| 07 ⭐ | [IAM audit](aws/07-audit-iam-for-compliance.md) | Audit all IAM users and roles for compliance. |
| 08 ⭐ | [Cross-account partner access](aws/08-cross-account-access-for-partner.md) | Grant cross-account access to a partner. |
| 09 ⭐ | [S3 in transit and at rest](aws/09-secure-s3-in-transit-and-at-rest.md) | Secure S3 data in transit and at rest for compliance. |
| 10 | [Lambda across environments](aws/10-lambda-multi-environment.md) | Deploy Lambda functions across multiple environments securely. |

### Docker

| # | File | Question |
|---|---|---|
| 01 | [Multi-cloud with compliance](docker/01-multi-cloud-with-compliance.md) | Multi-cloud Docker deployments with compliance restrictions. |
| 02 | [Live-patch the host kernel](docker/02-live-patch-host-kernel.md) | Live-patching the Docker host kernel without downtime. |
| 03 ⭐ | [Container DNS failures](docker/03-container-dns-failures.md) | Troubleshoot container DNS resolution failures. |
| 04 | [Policy-as-code](docker/04-policy-as-code-docker-security.md) | Enforce policy-as-code for Docker security. |

### Kubernetes

| # | File | Question |
|---|---|---|
| 01 ⭐ | [Ingress controller crashing](kubernetes/01-ingress-controller-crashing.md) | Ingress controller crashes repeatedly under heavy load. How do you stabilize it? |
| 02 ⭐ | [Region failover](kubernetes/02-region-failover.md) | An entire Kubernetes region goes down. How do you fail over workloads? |
| 03 ⭐ | [Namespace readiness failures](kubernetes/03-namespace-readiness-failures.md) | All pods in one namespace suddenly fail readiness checks. |
| 04 ⭐ | [HPA too slow](kubernetes/04-hpa-too-slow.md) | Massive traffic surge and HPA can't scale pods fast enough. |
| 05 ⭐ | [Node crashes permanently](kubernetes/05-node-crashes-permanently.md) | A node hosting critical workloads crashes permanently. |

### Terraform

These sit next to the 10 concept notes in [`../terraform/`](../terraform/README.md) (draft PR #9; links into that folder work once it's merged). Terraform 06 builds on [08 · Rollback](../terraform/08-rollback.md) instead of repeating it.

| # | File | Question |
|---|---|---|
| 01 ⭐ | [Apply succeeded but broken](terraform/01-apply-succeeded-but-broken.md) | Apply succeeded, but some resources are not behaving as expected. How do you debug? |
| 02 ⭐ | [Terraform in CI/CD](terraform/02-terraform-in-ci-cd.md) | How do you run Terraform safely in CI/CD pipelines? |
| 03 ⭐ | [State too large](terraform/03-state-too-large.md) | Your Terraform state file is getting too large. How do you manage it? |
| 04 | [10 regions at once](terraform/04-ten-regions.md) | Provision infra in 10 AWS regions simultaneously. How do you structure it? |
| 05 | [Faster runs](terraform/05-faster-terraform-runs.md) | Faster Terraform runs in large projects: what optimizations? |
| 06 ⭐ | [Failed halfway](terraform/06-failed-halfway-recovery.md) | A production deployment failed halfway. How do you recover? |

### Prometheus & Grafana

| # | File | Question |
|---|---|---|
| 01 ⭐ | [Cluster monitoring with Prometheus](monitoring/01-k8s-cluster-monitoring-prometheus.md) | Implement Kubernetes cluster-level monitoring using Prometheus. |
| 02 ⭐ | [Alertmanager + Slack](monitoring/02-alertmanager-slack.md) | Integrate Prometheus with Alertmanager and Slack for real-time notifications. |

## A method that fits almost every scenario question

1. **Clarify / scope** in one sentence ("unavailable how: deleted, access denied, or region down?").
2. **Stabilise first** if users are affected (roll back, scale up, shift traffic).
3. **Diagnose outside-in** with named commands (`describe`, `logs --previous`, `get events`, `plan`, CloudTrail).
4. **Fix**, then **prevent** (guardrail, alert, test, runbook).
5. Close with **one real example**, only if it's true.

## Diagrams

The 27 diagrams are in [diagrams/](diagrams/) as editable **`.drawio.svg`** files: open one in VS Code (Draw.io Integration) or [app.diagrams.net](https://app.diagrams.net) to edit it. They were generated once by [`tools/diagrams_scenario_qa.py`](../../tools/diagrams_scenario_qa.py), which skips files that already exist (so your edits in draw.io are safe); `--force` regenerates them.
