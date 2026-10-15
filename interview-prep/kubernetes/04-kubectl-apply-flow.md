# 04 · What Happens on `kubectl apply` ⭐ (Hemant's favourite kind of question)

The full flow for `kubectl apply -f deployment.yaml` (3 replicas behind a Service). The Instagram handbook skips etcd, the controllers and the network.

![kubectl apply flow](diagrams/04-kubectl-apply-flow.drawio.svg)

Steps 2–5 in detail (the API server pipeline, [02](02-architecture.md)):

![API request pipeline](diagrams/02-api-request-pipeline.drawio.svg)

## The 11 steps, one line each

1. **kubectl** reads kubeconfig, sends HTTPS to the API server.
2. **Authentication:** cert, token, OIDC; on EKS your IAM identity via **access entries**.
3. **RBAC:** may you `create` / `patch` Deployments here? No → `Forbidden`.
4. **Admission:** mutating → schema → validating (Pod Security, quota, Kyverno). Any can reject.
5. **etcd** saves it. kubectl prints "created". **Nothing runs yet.**
6. **Deployment controller** creates a ReplicaSet.
7. **ReplicaSet controller** creates 3 Pods with no node (`Pending`).
8. **Scheduler** filters → scores → binds (`spec.nodeName`).
9. **kubelet:** sandbox (pause) → **CNI gives the IP** → pull images → init containers → app containers.
10. **Probes** run; status reported.
11. **Ready** → EndpointSlice gets the IP → kube-proxy updates every node → traffic flows.

## Where it gets stuck ⭐

| You see | Step | Typical cause |
|---|---|---|
| `Forbidden` | 3 | User or ServiceAccount lacks RBAC |
| `admission webhook … denied` / `violates PodSecurity` | 4 | Policy, Pod Security level, quota |
| Deployment exists, no pods | 6–7 | Quota blocks pod creation (ReplicaSet events) |
| `Pending` | 8 | Requests too big, taints, affinity, PVC zone |
| `ContainerCreating` for long | 9 | No pod IPs left (EKS), volume attach, CNI |
| `ImagePullBackOff` | 9 | Wrong name/tag, no registry creds, rate limit |
| `CrashLoopBackOff` | 9 | App exits: config, env, OOM → `logs --previous` |
| `Running`, `0/1` ready | 10 | Readiness path/port wrong, dependency down |
| Ready, but no traffic | 11 | Selector ≠ labels, wrong `targetPort`, NetworkPolicy |

> **Docker link:** step 9 is `docker run` underneath: containerd → runc → namespaces + cgroups ([Docker 02](../docker/02-architecture-internals.md)).

## Interview angle

| Question | Answer |
|---|---|
| ⭐ Walk me through `kubectl apply`. | Tell the 11 steps as a story, from authentication to kube-proxy. |
| When does a pod get its IP? | Step 9: sandbox + CNI, **before** app containers start. |
| Does apply succeeding mean it runs? | No, only that it's **saved**. Use `kubectl rollout status`. |
| Who picks the node? | The scheduler, from **requests** (not usage), taints and affinity. |

## Practice 🖥️

```bash
kubectl get events --sort-by=.lastTimestamp -w   # run this first, in a second terminal
kubectl apply -f practice/deploy.yaml
kubectl get deploy,rs,pods -o wide
kubectl rollout status deployment/web
kubectl get endpointslices -l kubernetes.io/service-name=web
```
