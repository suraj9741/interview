# 3-Day DevOps Interview Prep Plan

> **Replaced by the new plan:** [study-plan-oct-5-9.md](study-plan-oct-5-9.md) (5–9 Oct, built around your working hours, with videos). This file is kept as reading material; the new plan links to sections of it.

**Topics:** Docker · Kubernetes · AWS · CI/CD · Security
**Interviewer:** Hemant Kumar, Platform Engineering & DevOps lead at One2N (Pune), ~11 years of experience

---

## About the interviewer

- One2N publishes a free [SRE bootcamp](https://one2n.io/sre-bootcamp) that shows how they think. Its milestones:
  REST API → Docker → one-command local setup (Makefile) → CI pipeline (GitHub Actions) → deploy on a server → Kubernetes → Helm → ArgoCD → Prometheus/Loki/Grafana → dashboards and alerts.
- They teach **"problem-first, not technology-first"**. Expect **"why"** questions, **"how would you debug this"** scenarios and **end-to-end flows**, more than definitions.
- His public projects include a **VPC Flow Logs network analyzer** (AWS networking) and an **MLOps project on Kubernetes**.

## Priority

| # | Topic | Share | Why |
|---|---|---|---|
| 1 | **Kubernetes** | 35% | Central to One2N's work; troubleshooting questions are very likely |
| 2 | **CI/CD** (GitHub Actions, Helm, ArgoCD) | 20% | Half of their bootcamp is about this |
| 3 | **AWS** (VPC networking + IAM first) | 20% | His VPC Flow Logs project suggests he goes deep on networking |
| 4 | **Docker** | 15% | Quick to cover, and everything else builds on it |
| 5 | **Security** | 10% | Learn the security side of each topic above, not on its own |

## How to use this plan

- **Daily rhythm:** read for about 1 hour, practise for 2–3 hours, then answer the self-test questions **out loud** without notes.
- ⭐ = must read. Everything else is optional or for skimming.
- **Tools to install first:** Docker Desktop, `kind`, `kubectl`, `helm`.
- If a link has moved, search for the page title.

---

# Day 1: Docker + Kubernetes basics

## Morning (3h): Docker

### Points to learn

- **Container vs VM:** a container is a normal Linux process.
  - **Namespaces** limit what it can see: processes, network, files, hostname.
  - **cgroups** limit what it can use: CPU and memory.
  - It shares the host's kernel, while a VM runs its own kernel. So containers are lighter and faster, but less isolated.
- **Layers:** each `RUN`, `COPY` or `ADD` line creates a layer. The cache breaks at the first changed line, and everything after it rebuilds. So copy the dependency file (`requirements.txt`, `package.json`) and install first, and copy your code last.
- **Multi-stage build:** build in a large image that has the compilers, then copy only the result into a small runtime image.
- **CMD vs ENTRYPOINT:** `ENTRYPOINT` is the fixed program, and `CMD` gives default arguments that are easy to override. Use the exec form `["app"]` so your app is PID 1 and receives stop signals.
- **COPY vs ADD:** `ADD` can also unpack tar files and download URLs. Prefer `COPY`.
- **Volumes vs bind mounts:** Docker manages volumes, so use them for data. A bind mount is a folder from the host, which suits development.
- **Networks:**
  - **bridge** is the default: a private network plus port mapping with `-p`.
  - **host** shares the host's network with no isolation.
  - On a user-defined bridge, containers can find each other by name.
- **Security:** set `USER` to a non-root user, use slim or distroless base images, keep secrets out of `ENV` and layers, add a `.dockerignore`, and scan images with Trivy.

### Reading (~1h)

- [ ] ⭐ [What even is a container (Julia Evans)](https://jvns.ca/blog/2016/10/10/what-even-is-a-container/): 10 min, explains namespaces and cgroups clearly
- [ ] ⭐ [Dockerfile best practices](https://docs.docker.com/build/building/best-practices/)
- [ ] ⭐ [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [ ] [Dockerfile reference](https://docs.docker.com/reference/dockerfile/): read only the CMD and ENTRYPOINT sections
- [ ] [Volumes](https://docs.docker.com/engine/storage/volumes/) · [Networking](https://docs.docker.com/engine/network/): skim
- [ ] [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html): read the rule headings

### Practice (~2h)

- [ ] Write a tiny API in Python or Go (whichever you know).
- [ ] Build a single-stage image with a full base image and note its size with `docker images`.
- [ ] Rebuild it as multi-stage with a slim or distroless base and a non-root user, and compare sizes.
- [ ] Change one line of code, rebuild, and watch which layers come from the cache.
- [ ] Look inside with `docker history <image>`, `docker inspect`, and `docker exec -it <id> sh`.

### Self-test

- [ ] "I changed one line of code and the whole build is slow. Why?"
- [ ] "What is a container, and how is it different from a VM?"
- [ ] "What happens to data when a container is deleted?"
- [ ] "Why doesn't my container stop gracefully?" (shell form, PID 1)

## Afternoon/evening (5h): Kubernetes basics

### Points to learn

- **Control plane:**
  - **API server:** the front door; it checks who you are, what you're allowed to do, and validates requests.
  - **etcd:** stores all cluster state.
  - **scheduler:** chooses a node for each pod.
  - **controller manager:** runs loops that keep comparing desired state with actual state.
- **Each node:**
  - **kubelet:** starts pods using containerd.
  - **kube-proxy:** routes Service traffic.
  - **CNI plugin:** gives each pod its IP address.
- **What happens after `kubectl apply`**, step by step:
  1. API server checks: authentication → RBAC → admission
  2. The object is saved in etcd
  3. Deployment controller creates a ReplicaSet
  4. ReplicaSet controller creates the Pods
  5. Scheduler assigns each pod to a node
  6. kubelet creates the pod sandbox, and the CNI plugin gives the pod its IP
  7. kubelet pulls the image and starts the containers
  8. Readiness probe passes, the pod is added to the Service's endpoints, and traffic flows
- **Workloads:**
  - **Deployment:** stateless apps.
  - **StatefulSet:** stable names and its own disk per pod (databases, Kafka).
  - **DaemonSet:** one pod per node (log or monitoring agents).
  - **Job / CronJob:** tasks that run to completion.
  - **ReplicaSet:** never used directly; Deployments manage it.
- **Services:**
  - **ClusterIP:** reachable only inside the cluster.
  - **NodePort:** opens a port from 30000–32767 on every node.
  - **LoadBalancer:** creates a cloud load balancer.
  - **DNS:** a Service is reachable at `my-svc.my-ns.svc.cluster.local` via CoreDNS.
  - **Ingress:** routes HTTP traffic by host or path, and needs an ingress controller.
- **ConfigMap vs Secret:** Secrets are only base64-encoded. Protect them with RBAC and encryption at rest, or keep them outside the cluster in AWS Secrets Manager.
- **Probes:**
  - **liveness:** restarts the container if it fails.
  - **readiness:** removes the pod from the Service until it's ready.
  - **startup:** gives slow-starting apps time before the other probes begin.
- **Requests vs limits:**
  - **Requests** are what the scheduler reserves for the pod.
  - Going over the **CPU limit** gets the container slowed down (throttled).
  - Going over the **memory limit** gets it killed (OOMKilled).

### Reading (~1.5h)

- [ ] ⭐ [Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/)
- [ ] ⭐ [What happens when… (k8s)](https://github.com/jamiehannaford/what-happens-when-k8s): read the overview, not every line
- [ ] ⭐ [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/): include the rolling update and rollback sections
- [ ] ⭐ [Service](https://kubernetes.io/docs/concepts/services-networking/service/) · [Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) · [Requests and limits](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [ ] [Workloads](https://kubernetes.io/docs/concepts/workloads/) · [DNS](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/) · [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) · [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/): skim
- [ ] [kind quick start](https://kind.sigs.k8s.io/docs/user/quick-start/)

### Practice (~3h)

- [ ] Create a cluster with `kind create cluster`, then load your image with `kind load docker-image myapi:v1`.
- [ ] Write a Deployment with 3 replicas, probes, requests and limits, and environment values from a ConfigMap and a Secret. Add a Service.
- [ ] Run `kubectl apply -f .`, then reach the app with `kubectl port-forward svc/myapi 8080:80`.
- [ ] Scale with `kubectl scale deploy myapi --replicas=5`.
- [ ] Build v2, then `kubectl set image …`, watch `kubectl rollout status`, and roll back with `kubectl rollout undo`.
- [ ] Delete a pod and watch it come back. That's the controller loop at work.
- [ ] Decode your Secret with `base64 -d` to see why base64 isn't security.

### Self-test

- [ ] Explain everything that happens from `kubectl apply` to a running pod.
- [ ] "Deployment vs StatefulSet?"
- [ ] "What goes wrong if the liveness probe checks the database?" (When the database slows down, every pod restarts at once.)
- [ ] "How does one pod reach another Service by name?"

---

# Day 2: Troubleshooting + CI/CD

## Morning (4h): Break things on purpose and fix them

### Debugging order (say this in the interview)

1. `kubectl get pods`
2. `kubectl describe pod` (read the Events at the bottom)
3. `kubectl logs` / `kubectl logs --previous`
4. `kubectl get events --sort-by=.lastTimestamp`
5. `kubectl get endpoints`
6. `kubectl exec` into a pod and try `curl` / `nslookup`
7. `kubectl describe node` / `kubectl top`

### Practice: break it, then fix it

| Done | Break it like this | What you'll see | Find it with |
|---|---|---|---|
| [ ] | Wrong image tag | `ImagePullBackOff` | `describe pod` |
| [ ] | Bad start command | `CrashLoopBackOff` | `logs --previous` |
| [ ] | Memory limit too low | `OOMKilled` | `describe pod` |
| [ ] | CPU request too high | `Pending` | events, `describe node` |
| [ ] | Wrong Service selector | Service gets no traffic | `get endpoints` (empty) |
| [ ] | Wrong readiness path | Pod shows `0/1` ready, gets no traffic | probe failures in `describe` |
| [ ] | Missing ConfigMap used as env vars | `CreateContainerConfigError` (used as a volume instead: stuck in `ContainerCreating`) | `describe pod` |

### Then learn

- **HPA vs Cluster Autoscaler:**
  - **HPA** adds pods. It needs metrics-server, and requests must be set.
  - **Cluster Autoscaler** (or Karpenter on EKS) adds nodes.
- **RBAC:** a Role (one namespace) or ClusterRole (cluster-wide) grants permissions; a RoleBinding or ClusterRoleBinding gives them to a user, group or ServiceAccount. Test access with `kubectl auth can-i`.
- **NetworkPolicy:** start with default-deny and allow only what's needed. It only works if the network plugin enforces it, such as Calico or Cilium.
- **Pod Security Standards:** three levels (privileged, baseline, restricted), turned on with a namespace label.

### Reading

- [ ] ⭐ [learnk8s troubleshooting flowchart](https://learnk8s.io/troubleshooting-deployments): the best single page for this, so study it
- [ ] ⭐ [Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/) · [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)
- [ ] [HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) · [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) · [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) · [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)

### Self-test

- [ ] "A pod is Pending. Give 4 reasons." (not enough resources, taints/affinity, PVC not bound, quota)
- [ ] "Why does a pod go into CrashLoopBackOff?"
- [ ] "The Service isn't working. What do you check?" (selector and labels, targetPort, readiness, NetworkPolicy, DNS)

## Afternoon/evening (4h): CI/CD

### Points to learn

- **CI vs CD:**
  - **CI** builds and tests every commit.
  - **Continuous Delivery** means always ready to release, with a manual approval for production.
  - **Continuous Deployment** releases to production automatically.
- **Pipeline stages:**
  1. Test
  2. Build the image, tagged with the git commit ID (not `latest`)
  3. Trivy scan; fail on HIGH or CRITICAL findings
  4. Push to the registry
  5. Update the Helm values in Git
  6. ArgoCD syncs the change to the cluster
  7. Smoke test
- **Push vs pull (GitOps):**
  - **Push:** the CI system holds cluster credentials and runs `kubectl` or `helm` itself.
  - **Pull:** ArgoCD runs inside the cluster and pulls changes from Git. CI needs no cluster credentials, drift is detected and fixed, and `git revert` is your rollback.
- **Helm:** a chart is templates plus `values.yaml`. Use `helm install`, `helm upgrade` and `helm rollback`.
- **Deployment strategies:**
  - **Rolling:** the default, controlled by `maxSurge` and `maxUnavailable`.
  - **Blue/green:** two full environments; switch traffic over. Rollback is instant, but it costs double.
  - **Canary:** send a small percentage of traffic first and watch the metrics (Argo Rollouts).
- **Security:**
  - **GitHub OIDC:** gets short-lived AWS credentials, so no access keys are stored.
  - Set a minimal `permissions:` block in the workflow.
  - Pin actions to a full commit SHA, not a tag (tags can be moved).
  - Use branch protection.

### Reading

- [ ] ⭐ [GitHub Actions docs](https://docs.github.com/en/actions): the Quickstart and the workflow syntax page
- [ ] ⭐ READMEs of [docker/build-push-action](https://github.com/docker/build-push-action), [trivy-action](https://github.com/aquasecurity/trivy-action), and [configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials) (its OIDC section)
- [ ] ⭐ [Helm: getting started with charts](https://helm.sh/docs/chart_template_guide/getting_started/)
- [ ] ⭐ [ArgoCD getting started](https://argo-cd.readthedocs.io/en/stable/getting_started/) · [ArgoCD core concepts](https://argo-cd.readthedocs.io/en/stable/core_concepts/)
- [ ] [Argo Rollouts concepts](https://argoproj.github.io/argo-rollouts/concepts/): clearest explanation of blue/green vs canary

### Practice

- [ ] Push your app to GitHub. Write a workflow that tests, builds, runs a Trivy scan, and pushes to GHCR (GitHub's free registry, so no AWS needed).
- [ ] Run `helm create myapi` and move your Kubernetes files into the chart. Then `helm install`, `helm upgrade` and `helm rollback`.
- [ ] Install ArgoCD in kind and point an Application at your chart. Change the replica count in Git and watch it sync.

### Self-test

- [ ] "Design CI/CD from commit to production, including rollback."
- [ ] "Someone ran `kubectl edit` in production. What happens with GitOps?" (With automated sync and self-heal turned on, ArgoCD reverts it; otherwise ArgoCD only marks the app OutOfSync.)
- [ ] "How do you avoid storing AWS keys in GitHub?"
- [ ] "Blue/green vs canary: when do you use each?"

---

# Day 3: AWS + security + practice interview

## Morning (4h): AWS

### Points to learn

- **VPC:**
  - **Public subnet:** its route table sends `0.0.0.0/0` to the Internet Gateway.
  - **Private subnet:** sends `0.0.0.0/0` to a NAT Gateway, which sits in a public subnet and allows outbound traffic only.
  - Use one NAT Gateway per AZ for high availability; mention the cost.
  - **VPC endpoints** let you reach S3 without going through NAT.
- **Security Groups vs NACLs:**
  - **Security Group:** attached to the instance, allow rules only, **stateful** (return traffic is allowed automatically).
  - **NACL:** attached to the subnet, allow and deny rules, **stateless** (you must open ephemeral ports for return traffic), rules checked in number order.
- **VPC Flow Logs:** record source, destination, port, protocol and ACCEPT/REJECT for traffic. They answer "why can't A reach B?" ⚠️ Your interviewer built a Flow Logs analyzer, so know the record fields well.
- **Peering vs Transit Gateway:**
  - **Peering:** one-to-one, not transitive, and the IP ranges can't overlap.
  - **Transit Gateway:** a hub that connects many VPCs plus VPN.
- **IAM:**
  - **Users vs roles:** users have long-term keys, so avoid them. Roles give temporary credentials through STS.
  - **Trust policy vs permission policy:** the trust policy says who can assume the role; the permission policy says what it can do.
  - **Evaluation:** an explicit deny beats an allow, and anything not allowed is denied.
- **IRSA / EKS Pod Identity:** gives each pod its own IAM role. Never give app permissions through the node's role.
- **Other services:**
  - **ALB vs NLB:** ALB works at layer 7 (HTTP, path routing, WAF); NLB works at layer 4 (TCP, static IP, very fast).
  - **ASG:** a launch template plus min, max and desired counts.
  - **S3 + KMS:** block public access and encrypt with KMS.
  - **EKS:** the VPC CNI gives each pod a VPC IP address, which can run out.

### Reading

- [ ] ⭐ [How Amazon VPC works](https://docs.aws.amazon.com/vpc/latest/userguide/how-it-works.html) · [NAT gateways](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)
- [ ] ⭐ [Security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html) · [Network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [ ] ⭐ [VPC Flow Logs](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html): read the flow log records section carefully
- [ ] ⭐ [IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) · [IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)
- [ ] [IRSA](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html) · [EKS Pod Identity](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html)
- [ ] [Transit Gateway](https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html) · [Load balancer comparison](https://aws.amazon.com/elasticloadbalancing/features/): skim

### Practice

- [ ] In draw.io, draw a VPC across 2 availability zones:
  - **Public subnets:** the ALB and the NAT Gateway.
  - **Private app subnets:** EKS nodes or EC2 instances.
  - **Private DB subnets:** RDS.
  - **Security groups in a chain:** ALB SG → app SG → DB SG.
- [ ] Explain the drawing out loud in 3 minutes.

### Self-test

- [ ] "A private EC2 instance can't reach the internet. What do you check?" (route to NAT, NAT's route to the IGW, SG outbound rules, NACL ephemeral ports)
- [ ] "Security Group vs NACL?"
- [ ] "How does a pod on EKS get access to S3 securely?"

## Afternoon (2h): Security review by layer

- **CI:** dependency and secret scanning, OIDC, minimal token permissions
- **Image:** small base image, non-root user, Trivy scan, no secrets
- **Kubernetes:** least-privilege RBAC, default-deny NetworkPolicy, restricted Pod Security Standards, Secrets kept outside the cluster
- **AWS:** least-privilege IAM, no long-lived keys, private subnets, KMS encryption, TLS, CloudTrail, GuardDuty

### Reading

- [ ] [Kubernetes security checklist](https://kubernetes.io/docs/concepts/security/security-checklist/)
- [ ] [OWASP Kubernetes Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html)
- [ ] [AWS Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html): design principles only

## Evening (2h): Practice interview

- [ ] Go through the [One2N SRE bootcamp milestones](https://one2n.io/sre-bootcamp/sre-bootcamp-exercises). For each one, can you explain **how** you'd do it and **why**? This is the closest thing to the interviewer's own question list.
- [ ] Prepare 2–3 resume projects using STAR (Situation, Task, Action, Result).
- [ ] Be ready for "why did you choose X over Y?" about every tool on your resume.
- [ ] Do a mock interview, out loud.

---

# Scenarios to practise out loud

- [ ] A user opens your URL. Trace it: DNS (Route 53) → load balancer → Pod. Know both common paths:
  - **AWS Load Balancer Controller:** the Ingress *configures* an ALB, which sends traffic straight to pod IPs (IP mode).
  - **ingress-nginx:** a load balancer sends traffic to the nginx pods, which forward it to your Service's pods.
- [ ] A pod is in `CrashLoopBackOff`. How do you debug it?
- [ ] A private EC2 instance can't reach the internet. Why?
- [ ] Design CI/CD for a microservice, from commit to production, including rollback.
- [ ] How do you handle secrets from end to end?
- [ ] The site is slow at 2 AM. What do you check first? (metrics → logs → recent deploys)

# Tips for this interviewer

- Explain from basic principles (for example, containers = namespaces + cgroups).
- Think out loud and debug step by step.
- Mention trade-offs: every choice has a cost.
- If you don't know something, say so and reason your way to an answer.
- **The night before:** only reread the self-test questions, then sleep.
