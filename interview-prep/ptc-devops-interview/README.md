# PTC · Senior DevOps Engineer interview (24 questions, 2 rounds)

Answers to the 24 questions from a shared PTC Senior DevOps interview experience. One file per question, each with:

1. **A draw.io diagram first** (17 new ones in [diagrams/](diagrams/), made by `tools/diagrams_ptc.py`; 7 reused from the Docker, Kubernetes, networking and model-answer notes).
2. **"Say this first"**: the answer as you'd say it in the interview (about 1–2 minutes).
3. Details, commands and YAML, tables, follow-up questions.
4. Links to the deeper notes already in this repo (some live in draft PRs #9, #11, #12; those links work once the PRs merge).
5. **🎯 Drill:** questions to answer from memory, with the answer hidden in a fold.
6. **🗣️ 30-second spoken answer.**

**Start with the [self-test](self-test.md)**, not with reading. In the NiCE (11 Nov) and AWS Admin (13 Nov) interviews you had the notes but couldn't say the answers. Reading feels like progress but isn't; saying the answer aloud from memory and checking it is.

## Questions → answers

### Round 1 (fundamentals)

| # | Question | Diagram | Answer |
|---|---|---|---|
| 1 | Explain your project architecture and CI/CD pipeline | new | [01-project-architecture-cicd.md](round-1/01-project-architecture-cicd.md) ⭐ built from your resume, fill the ⟨blanks⟩ |
| 2 | What is Docker? Image vs container | reused (Docker notes) | [02-docker-image-vs-container.md](round-1/02-docker-image-vs-container.md) |
| 3 | What is Kubernetes? Architecture | reused (Kubernetes notes) | [03-kubernetes-architecture.md](round-1/03-kubernetes-architecture.md) |
| 4 | Pod, Service, Deployment | new | [04-pod-service-deployment.md](round-1/04-pod-service-deployment.md) |
| 5 | Rolling vs blue-green vs canary | new | [05-rolling-blue-green-canary.md](round-1/05-rolling-blue-green-canary.md) |
| 6 | Terraform and the state file | new | [06-terraform-and-state.md](round-1/06-terraform-and-state.md) |
| 7 | Public vs private subnets | reused (Oct 9 review) | [07-public-vs-private-subnets.md](round-1/07-public-vs-private-subnets.md) ⚠️ missed on 13 Nov |
| 8 | IAM: role vs policy | new | [08-iam-role-vs-policy.md](round-1/08-iam-role-vs-policy.md) |
| 9 | Load balancer: how it works | new | [09-load-balancer.md](round-1/09-load-balancer.md) ⚠️ missed on 13 Nov |
| 10 | Git branching strategy | new | [10-git-branching-strategy.md](round-1/10-git-branching-strategy.md) |
| 11 | Monitoring applications in production | reused (model answers) | [11-production-monitoring.md](round-1/11-production-monitoring.md) |
| 12 | DNS: what and how | reused (model answers) | [12-dns.md](round-1/12-dns.md) |

### Round 2 (scenarios and design)

| # | Question | Diagram | Answer |
|---|---|---|---|
| 1 | Scaling an application in Kubernetes | reused (Kubernetes notes) | [01-scale-app-in-kubernetes.md](round-2/01-scale-app-in-kubernetes.md) |
| 2 | Securing container images | new | [02-secure-container-images.md](round-2/02-secure-container-images.md) |
| 3 | Role of CloudFront | new | [03-cloudfront-role.md](round-2/03-cloudfront-role.md) |
| 4 | Disaster recovery for RDS | new | [04-rds-disaster-recovery.md](round-2/04-rds-disaster-recovery.md) |
| 5 | Developer can't access an S3 bucket | new | [05-s3-access-denied.md](round-2/05-s3-access-denied.md) |
| 6 | Latency in an EKS cluster | new | [06-eks-latency.md](round-2/06-eks-latency.md) |
| 7 | Lambda failing internally | new | [07-lambda-failing.md](round-2/07-lambda-failing.md) |
| 8 | CI/CD can't connect to GitLab | new | [08-cicd-cannot-connect-to-gitlab.md](round-2/08-cicd-cannot-connect-to-gitlab.md) |
| 9 | Kubernetes can't expose a pod | new | [09-cannot-expose-pod.md](round-2/09-cannot-expose-pod.md) |
| 10 | Pods running, users get 503 | reused (networking notes) | [10-pods-running-users-get-503.md](round-2/10-pods-running-users-get-503.md) |
| 11 | Terraform apply failed midway | new | [11-terraform-apply-failed-midway.md](round-2/11-terraform-apply-failed-midway.md) |
| 12 | Secrets across environments | new | [12-secrets-across-environments.md](round-2/12-secrets-across-environments.md) |

## The pattern behind round 2

Seven of the twelve round-2 questions are **"X is broken, what do you check?"** They all have the same answer shape, so learn the shape once:

1. **Clarify and scope:** exact error, since when, what changed, who is affected.
2. **Follow the path layer by layer** (identity → network → service → app → dependency), naming the command or metric that proves each layer.
3. **Fix the layer you found**, then **prevent** it (alert, policy, automation).

## Resume honesty notes

- R1 Q1 uses the facts on your resume (Koko: Swarm → EKS, Terraform, Dev/UAT/Prod-Int/Production, Jenkins → ArgoCD 10 → 2 min, SonarCloud, Secrets Manager → K8s, federated Prometheus, 99.9% uptime, 20–30% cost saving). Fill each **⟨fill: …⟩** with the real value; anything marked *(suggested)* is a typical setup, not proven by your resume.
- Not on your resume, so don't claim hands-on use: image signing (cosign), Kyverno/Gatekeeper, Argo Rollouts canaries, APM tools (Datadog/New Relic/Splunk), Aurora Global Database. Present them as "what I'd do" or "what I know".
- ELK is from the BridgeLabz traineeship only: say "basic".

## Regenerating diagrams

```bash
python3 tools/diagrams_ptc.py          # skips existing files (they may be edited in draw.io)
python3 tools/diagrams_ptc.py --force  # overwrite from the script
```
