# R1 Q1 · Explain your project architecture and CI/CD pipeline ⭐

![My project: CI builds once, GitOps deploys, EKS runs it, Prometheus watches it](../diagrams/r1-01-project-pipeline.drawio.svg)

> **This answer is built from your resume.** The facts that are on it (Koko Networks: Docker Swarm → EKS migration, Terraform-provisioned EKS, four environments Dev/UAT/Prod-Int/Production, Jenkins → ArgoCD GitOps with deploy time 10 → 2 minutes, SonarCloud, AWS Secrets Manager synced to Kubernetes, federated Prometheus + Grafana, 99.9% uptime, 20–30% cost reduction) are stated as facts. Anything marked **⟨fill: …⟩** is a detail only you know: fill it with the real value before the interview. Anything marked *(suggested)* is a typical setup, **not** something your resume proves: only say it if it's true for you.

## Say this first (2 minutes, in this order: business → architecture → pipeline → my part → result)

"At Koko Networks I was an SRE in a DevOps team of 6–7 *(⟨fill: confirm the team size⟩)*. The platform was ⟨fill: what the product did, e.g. the backend for Koko's fuel ATMs and customer app⟩, running as ⟨fill: ~N⟩ microservices on **Amazon EKS**.

**Architecture:** each environment, Dev, UAT, Prod-Int and Production, had its own EKS cluster ⟨fill: one AWS account per env, or shared non-prod⟩, all provisioned with **Terraform** modules: VPC across ⟨2–3⟩ AZs, private subnets for nodes, public subnets for the ALB, NAT gateway, EKS with managed node groups, IAM roles. Traffic came in through **Route 53 → an ALB** created by the AWS Load Balancer Controller *(suggested: or ingress-nginx behind an NLB; say what you really had)* → Ingress → Service → pods. Data was in **RDS** ⟨fill: Postgres/MySQL, Multi-AZ?⟩. Secrets lived in **AWS Secrets Manager** and were synced into Kubernetes, never in Git.

**CI/CD:** CI and CD are split. CI (⟨fill: GitLab CI or Jenkins⟩) runs on every merge request: lint and unit tests, **SonarCloud** quality gate, docker build tagged with the git SHA, image scan, push to **ECR**. Then it updates the image tag in the GitOps repo. **ArgoCD** runs inside each cluster, watches that repo and syncs the change. Dev and UAT auto-sync; Prod-Int and Production need approval. Rollback is a git revert.

**My part:** I migrated the services from Docker Swarm to EKS and moved deployments from Jenkins to ArgoCD. That cut deploy time from about **10 minutes to 2**, and right-sizing during the migration cut infra cost by **20–30%**. I also built federated Prometheus with Grafana dashboards and Alertmanager alerts, which helped us hold **99.9% uptime**."

## The architecture, layer by layer (know each box in the diagram)

| Layer | What we used | Why (the follow-up they'll ask) |
|---|---|---|
| Accounts / environments | Dev, UAT, Prod-Int, Production ⟨fill: separate AWS accounts?⟩ | Isolation and blast radius; Prod-Int is the production-like integration environment |
| Provisioning | Terraform modules (vpc, eks, rds, iam), remote state in S3 with locking, one state per env | Same code, different variables per env; reviewable plans; no click-ops |
| Configuration of non-K8s hosts | Ansible | Idempotent config of EC2/bastion/legacy hosts (on resume) |
| Network | VPC across ⟨2–3⟩ AZs; public subnets: ALB + NAT GW; private: nodes, pods (VPC CNI), RDS | Nothing but the load balancer is reachable from the internet |
| Entry | Route 53 → ALB (2+ AZs) → Ingress | TLS at the ALB with an ACM certificate |
| Compute | EKS, managed node groups ⟨fill: Cluster Autoscaler/Karpenter?⟩, HPA on services | Autoscaling, standard tooling, replaced Swarm |
| Data | RDS ⟨fill⟩ in private DB subnets | Managed backups, Multi-AZ failover |
| Secrets | AWS Secrets Manager → ⟨fill: External Secrets Operator / CSI driver⟩ → K8s Secret | Nothing secret in Git or images |
| Observability | Prometheus per cluster, a central Prometheus federating them, Grafana, Alertmanager → ⟨fill: Slack/PagerDuty⟩; CloudWatch for AWS-managed services | One view across clusters, alert before users notice |

## The pipeline, stage by stage

```text
MR opened ──► lint + unit tests ──► SonarCloud quality gate ──► docker build (tag = $CI_COMMIT_SHORT_SHA)
         ──► image scan (Trivy/ECR, suggested) ──► push to ECR ──► bump tag in GitOps repo (dev values)
ArgoCD (in cluster) sees the commit ──► syncs dev ──► smoke tests
Promotion: MR that copies the same tag into uat → prod-int → prod values ──► approval ──► ArgoCD sync
Rollback: git revert the tag bump ──► ArgoCD syncs the previous version
```

A minimal `.gitlab-ci.yml` that matches this *(suggested shape: be able to write it, not claim it's your exact file)*:

```yaml
stages: [test, build, deploy]

test:
  stage: test
  image: python:3.12
  script:
    - pip install -r requirements.txt
    - pytest

build:
  stage: build
  image: docker:27
  services: [docker:27-dind]
  script:
    - aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
    - docker build -t $ECR_REGISTRY/app:$CI_COMMIT_SHORT_SHA .
    - docker push $ECR_REGISTRY/app:$CI_COMMIT_SHORT_SHA
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

update-gitops:
  stage: deploy
  script:
    - git clone https://gitlab-ci-token:${GITOPS_TOKEN}@gitlab.example.com/platform/gitops.git
    - cd gitops && yq -i ".image.tag = \"$CI_COMMIT_SHORT_SHA\"" apps/app/values-dev.yaml
    - git commit -am "app: deploy $CI_COMMIT_SHORT_SHA to dev" && git push
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

## Why this design (have one line ready for each)

- **Build once, promote the same image:** what was tested in UAT is byte-for-byte what reaches prod. No rebuild per environment.
- **Pull-based GitOps (ArgoCD) over push (Jenkins running kubectl):** CI never holds cluster-admin credentials; Git history is the audit log; drift shows as OutOfSync; rollback is a revert.
- **Why 10 → 2 minutes:** ⟨fill: the real reasons⟩. Typical: the deploy stage no longer waited for Jenkins agents and ran helm/kubectl from outside; ArgoCD applies only the diff from inside the cluster; build and deploy are separate.
- **Where 20–30% came from:** right-sizing requests/limits from real usage, better bin-packing than over-provisioned Swarm nodes, fewer idle instances. ⟨fill: before/after node count or bill if you know it⟩.

## Follow-up questions

| Question | Answer |
|---|---|
| How do you handle a failed deployment? | Readiness probes stop bad pods getting traffic; the rolling update stalls instead of finishing; ArgoCD shows Degraded; rollback = git revert (or ArgoCD history, then fix Git so auto-sync doesn't re-apply it) |
| How are DB migrations handled? | ⟨fill⟩. Typical: a Kubernetes Job / ArgoCD PreSync hook runs migrations; migrations are backward compatible (expand → migrate → contract) so old and new pods both work |
| How do secrets reach the pod? | Secrets Manager → ⟨External Secrets / CSI driver⟩ → Kubernetes Secret → env var or mounted file; the pod's IAM role (IRSA/Pod Identity) can read only its own paths |
| How do you make the pipeline secure? | Protected branches, MR approval, masked/protected CI variables or OIDC to AWS (no static keys), SonarCloud + image scanning gates, signed/immutable image tags. See [R2 Q2](../round-2/02-secure-container-images.md) and [R2 Q12](../round-2/12-secrets-across-environments.md) |
| How do you monitor a deployment? | Grafana dashboards for error rate and latency per version, Alertmanager alerts, ArgoCD health status. See [R1 Q11](11-production-monitoring.md) |
| What would you improve? | Canary releases with Argo Rollouts and automatic analysis on Prometheus metrics; image signing + admission policy; ⟨fill: something you actually wanted to do⟩ |

## Where this is covered in more depth

- Full STAR stories with blanks for the Swarm → EKS migration, Jenkins → ArgoCD and federated Prometheus: `interview-prep/aws-interview-stories.md` in draft PR #12 (stories 1–3).
- Build once, promote: [hemant-model-answers.md Q37–Q39](../../hemant-model-answers.md#q37-every-branch-merge-means-a-rebuild-how-do-you-reduce-lead-time-to-production) and the diagram [38-build-once-promote](../../diagrams/38-build-once-promote.drawio.svg).
- GitOps flow: [kubernetes/21-helm-kustomize-gitops.md](../../kubernetes/21-helm-kustomize-gitops.md).
- EKS: [kubernetes/20-eks.md](../../kubernetes/20-eks.md).

## 🎯 Drill: say it from memory, then check

Draw the diagram on paper from memory (boxes and arrows only), then say the 2-minute answer out loud. Then answer:

1. What are the four environments?
2. Name the CI stages in order.
3. What does CI change at the end, and who deploys?
4. How do you roll back?
5. Two numbers from your resume and where each came from.

<details><summary>Check your answers</summary>

1. Dev, UAT, Prod-Int, Production.
2. Lint + unit tests → SonarCloud quality gate → docker build (tag = git SHA) → image scan → push to ECR → bump the tag in the GitOps repo.
3. It only updates the image tag in the GitOps repo; ArgoCD inside the cluster pulls and syncs it (pull-based, CI has no cluster credentials).
4. `git revert` the tag bump; ArgoCD syncs the previous version.
5. Deploy time 10 → 2 minutes (Jenkins → ArgoCD); 20–30% cost reduction (right-sizing during Swarm → EKS). Also 99.9% uptime.

</details>

## 🗣️ 30-second spoken answer

"At Koko Networks our microservices ran on EKS, with four environments, Dev, UAT, Prod-Int and Production, all built with Terraform: VPC across AZs, private nodes, an ALB in front, RDS behind. CI runs tests, a SonarCloud gate, builds the image tagged with the commit SHA, scans it and pushes it to ECR, then bumps the tag in a GitOps repo. ArgoCD in the cluster syncs it; prod needs approval and rollback is a git revert. I led the move from Swarm to EKS and from Jenkins to ArgoCD, which took deploys from 10 minutes to 2."
