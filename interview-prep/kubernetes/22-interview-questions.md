# 22 · Kubernetes Interview Questions (Hemant style) ⭐

Answer each question **out loud in under 2 minutes**, then tick it. Expect a "why?" after every answer. The file number in brackets has the full explanation.

## Basics and architecture

- [ ] **1. What problem does Kubernetes solve? Would you use it everywhere?** → Scheduling, self-healing, scaling, service discovery and rollouts across many machines. Not everywhere: it's complex, and ECS or a VM fits small workloads. [01]
- [ ] **2. What is the reconciliation loop?** → Controllers observe → compare desired vs actual → act, forever. Self-healing is just this loop. [01]
- [ ] **3. Explain the architecture.** → API server (the only one that talks to etcd), etcd, scheduler, controller manager, cloud controller; kubelet, container runtime, kube-proxy, CNI; CoreDNS. [02]
- [ ] **4. What breaks if the API server is down? If the scheduler is down?** → No changes or self-healing, but running pods continue / new pods stay Pending. [02]
- [ ] **5. ⭐ What happens after `kubectl apply -f deployment.yaml`?** → Authentication → RBAC → admission → etcd → Deployment controller → ReplicaSet → scheduler → kubelet (sandbox → CNI IP → image → containers) → probes → endpoints → kube-proxy. [04]
- [ ] **6. spec vs status? Labels vs annotations?** → Desired vs actual; selectable vs informational. [03]
- [ ] **7. A namespace is stuck in Terminating. Why?** → Finalizers whose controller is gone. [03]

## Workloads and pods

- [ ] **8. Why pods and not containers? What do containers in a pod share?** → They're scheduled together and share the network (IP, localhost), IPC and volumes. [05]
- [ ] **9. Init container vs sidecar?** → Runs to completion before the app vs runs alongside it (native sidecar: `restartPolicy: Always`, stable in 1.33). [05]
- [ ] **10. ⭐ Users see errors during every deploy. Why, and how do you fix it?** → The endpoint-removal/SIGTERM race. Use a `preStop` sleep, SIGTERM handling, readiness probes, `maxUnavailable: 0`, and a PDB. [05, 07]
- [ ] **11. Liveness vs readiness vs startup. What if liveness checks the database?** → Restart vs traffic vs a grace period for slow starts; checking the database causes cascading restarts. [06]
- [ ] **12. Deployment vs StatefulSet vs DaemonSet vs Job?** → Stateless / stable identity and disk / one per node / run to completion. [07]
- [ ] **13. How does a rolling update work, and how do you roll back?** → A new ReplicaSet scales up and the old one down (maxSurge/maxUnavailable); `rollout undo`. [07]

## Networking

- [ ] **14. ⭐ ClusterIP vs NodePort vs LoadBalancer vs headless. How does a ClusterIP work?** → kube-proxy DNAT rules on every node; there's no real machine behind it, which is why (in iptables/nftables mode) you can't ping it. [08]
- [ ] **15. A Service has no endpoints. Why?** → The selector doesn't match the labels, the pods aren't Ready, or the namespace is wrong. [08]
- [ ] **16. How does DNS work in a pod? What is `ndots:5`?** → CoreDNS plus search domains; short names try the cluster domains first. [08]
- [ ] **17. Explain the Kubernetes networking model. How does pod A on node 1 reach pod B on node 2?** → 4 rules, implemented by the CNI: an overlay or VPC routing. [14]
- [ ] **18. ⭐ After a default-deny NetworkPolicy, nothing resolves. Why?** → Egress to CoreDNS on port 53 (UDP/TCP) is blocked. [14]
- [ ] **19. Ingress vs Gateway API? What's an Ingress controller?** → Ingress is frozen and ingress-nginx was retired in 2026; Gateway API is the role-based successor. The controller is what actually implements the rules. [09]

## Config, storage, resources, scheduling

- [ ] **20. ⭐ Are Secrets secure?** → Only base64-encoded. Use KMS encryption at rest, careful RBAC (list = read), and External Secrets with AWS Secrets Manager plus IRSA or Pod Identity. [10]
- [ ] **21. PV vs PVC vs StorageClass? Why can't two nodes write to one EBS volume?** → Storage vs request vs recipe; EBS is ReadWriteOnce and tied to one AZ. [11]
- [ ] **22. ⭐ Requests vs limits? OOMKilled vs throttling? Pods are Pending but the nodes look idle. Why?** → Scheduling uses requests, not usage. [12]
- [ ] **23. HPA vs VPA vs Cluster Autoscaler vs Karpenter? Why isn't the HPA scaling?** → No metrics-server, or no requests set. [12]
- [ ] **24. Taints vs affinity? How do you spread replicas across availability zones?** → Repel vs attract; topology spread constraints. [13]

## Security, troubleshooting, operations, EKS

- [ ] **25. ⭐🔥 How do you secure a cluster?** → The 7 layers: API access (authentication, RBAC, admission), identity, Pod Security, network, supply chain, secrets, detection. [15]
- [ ] **26. ⭐ A pod is in CrashLoopBackOff / Pending / Running but not Ready. Walk me through each.** → [17]
- [ ] **27. How do you upgrade EKS with no downtime?** → Deprecated APIs → control plane (one minor) → add-ons → nodes rolling with PDBs. [18, 20]
- [ ] **28. ⭐ How does a pod on EKS access S3 without keys?** → Pod Identity or IRSA, plus IMDSv2 hop limit 1. [20]
- [ ] **29. Pods are stuck in ContainerCreating on EKS with IP errors.** → VPC CNI IP exhaustion: prefix delegation, or a secondary CIDR. [20]
- [ ] **30. What is a CRD and an operator? Walk me through a GitOps deploy with ArgoCD.** → [19, 21]

## Scenario questions Hemant named ⭐🔥

These are in [Scenario deep dives](../hemant-scenario-deep-dives.md), with diagrams and follow-ups:
- [ ] **31. Helm drift:** someone edited a Helm release in the cluster. What happens on the next `helm upgrade`? [A1]
- [ ] **32. Two clusters, overlapping VPC CIDRs:** how do you connect them? [A2]
- [ ] **33. Nodes in 10.0.x.x, pods in 100.64.x.x:** how is it done, and why did One2N's NodeClass keep reverting? [A3]

## Live demo practice 🖥️ (on kind)

- [ ] Create a Deployment and Service, scale it, roll out a new image, roll it back.
- [ ] Delete a pod and watch it come back (reconciliation).
- [ ] Break it 3 ways (bad image, failing readiness, wrong selector) and debug each with `describe`, `logs` and `endpointslices`.
- [ ] Show that a Secret is only base64 (`kubectl get secret … | base64 -d`).
- [ ] `kubectl auth can-i` for a ServiceAccount, before and after a RoleBinding.
