# PTC Senior DevOps · self-test (no answers on this page)

**How to use it:** cover everything except one question. Set a 2-minute timer. **Say** the answer out loud (or record yourself on your phone), then open the answer file and score it honestly:

- **2** = said the key points in order without stopping
- **1** = got there, but hesitated or missed a key point
- **0** = blank, or said something wrong

Redo every 0 and 1 the same evening, then again next morning. You're ready when two days in a row are all 2s. Reading the answer is not practice; saying it is.

| Date → | | | | |
|---|---|---|---|---|

## Round 1

| # | Question (say it in ≤ 2 min) | Score | Answer |
|---|---|---|---|
| 1 | Explain your project architecture and CI/CD pipeline. (Draw it first.) | | [R1 Q1](round-1/01-project-architecture-cicd.md) |
| 2 | What is Docker? Difference between image and container? | | [R1 Q2](round-1/02-docker-image-vs-container.md) |
| 3 | What is Kubernetes? Explain its architecture. (Draw it.) | | [R1 Q3](round-1/03-kubernetes-architecture.md) |
| 4 | What is a Pod, Service, and Deployment? (Type the YAML.) | | [R1 Q4](round-1/04-pod-service-deployment.md) |
| 5 | Difference between Rolling, Blue-Green, and Canary deployments. | | [R1 Q5](round-1/05-rolling-blue-green-canary.md) |
| 6 | What is Terraform? What is a state file? (Type the backend block.) | | [R1 Q6](round-1/06-terraform-and-state.md) |
| 7 | Difference between public and private subnets in AWS. (Write both route tables.) | | [R1 Q7](round-1/07-public-vs-private-subnets.md) |
| 8 | What is IAM? Difference between role and policy? (Write a trust policy.) | | [R1 Q8](round-1/08-iam-role-vs-policy.md) |
| 9 | What is a Load Balancer and how does it work? (502 vs 503 vs 504.) | | [R1 Q9](round-1/09-load-balancer.md) |
| 10 | What is a Git branching strategy? | | [R1 Q10](round-1/10-git-branching-strategy.md) |
| 11 | How do you monitor applications in production? (Write two PromQL queries.) | | [R1 Q11](round-1/11-production-monitoring.md) |
| 12 | What is DNS and how does it work? | | [R1 Q12](round-1/12-dns.md) |

## Round 2

| # | Question (say it in ≤ 2 min) | Score | Answer |
|---|---|---|---|
| 1 | How do you scale an application in Kubernetes? (Type the HPA.) | | [R2 Q1](round-2/01-scale-app-in-kubernetes.md) |
| 2 | How do you secure container images in Kubernetes? | | [R2 Q2](round-2/02-secure-container-images.md) |
| 3 | What is the role of Amazon CloudFront in an architecture? | | [R2 Q3](round-2/03-cloudfront-role.md) |
| 4 | How do you design disaster recovery for Amazon RDS? (RPO/RTO per option.) | | [R2 Q4](round-2/04-rds-disaster-recovery.md) |
| 5 | A developer cannot access an S3 bucket. What will you check? | | [R2 Q5](round-2/05-s3-access-denied.md) |
| 6 | You are facing latency issues in an EKS cluster. How do you troubleshoot? | | [R2 Q6](round-2/06-eks-latency.md) |
| 7 | AWS Lambda is failing internally. What are your debugging steps? | | [R2 Q7](round-2/07-lambda-failing.md) |
| 8 | CI/CD pipeline is not able to connect to GitLab. What will you check? | | [R2 Q8](round-2/08-cicd-cannot-connect-to-gitlab.md) |
| 9 | Kubernetes is not able to expose a pod. What could be the issue? | | [R2 Q9](round-2/09-cannot-expose-pod.md) |
| 10 | Pods are running but users are getting 503 errors. How do you debug? | | [R2 Q10](round-2/10-pods-running-users-get-503.md) |
| 11 | Terraform apply failed midway: how do you recover safely? | | [R2 Q11](round-2/11-terraform-apply-failed-midway.md) |
| 12 | How do you handle secrets securely across multiple environments? | | [R2 Q12](round-2/12-secrets-across-environments.md) |

## Rapid-fire (one line each, 10 seconds, no notes)

1. A subnet is public because of ______.
2. An ALB needs subnets in at least ___ AZs.
3. 502 / 503 / 504 from an ALB mean ______ / ______ / ______.
4. `dig` shows ______; `traceroute` shows ______.
5. The HPA CPU percentage is a percentage of the container's ______.
6. Pods Running but not ______ get no traffic.
7. Terraform state locking in S3: `______ = true`.
8. IAM evaluation: an explicit ______ always wins.
9. `s3:ListBucket` goes on the ______ ARN; `s3:GetObject` on ______.
10. Lambda async invocations retry ___ times.
11. CloudFront's ACM certificate must be in region ______.
12. Multi-AZ does not protect against ______ or ______.
13. Endpoints empty: ______ or ______.
14. Terraform failed apply: never restore an ______.
15. CI to AWS without static keys: ______.

<details><summary>Rapid-fire answers (only after saying all 15)</summary>

1. Its route table: `0.0.0.0/0 → internet gateway`.
2. Two.
3. Bad response from the target / no registered targets / target timed out.
4. The DNS answer (records, TTL, which server answered); the network hops.
5. CPU request.
6. Ready (readiness probe passing).
7. `use_lockfile` (Terraform 1.10+; older: `dynamodb_table`).
8. Deny.
9. Bucket (`arn:aws:s3:::bucket`); objects (`arn:aws:s3:::bucket/*`).
10. Two.
11. us-east-1.
12. Logical errors (bad deletes, corruption) and region failure.
13. Selector doesn't match pod labels, or no pod is Ready.
14. Old state file to "roll back".
15. OIDC federation: assume an IAM role with the pipeline's ID token.

</details>
