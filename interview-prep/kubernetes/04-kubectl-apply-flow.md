# 04 · What Happens on `kubectl apply` ⭐ (Hemant's favourite kind of question)

The Instagram handbook's version skips etcd, the controllers and the network setup. This is the **complete** flow for `kubectl apply -f deployment.yaml` with 3 replicas behind a Service.

![kubectl apply flow](diagrams/04-kubectl-apply-flow.drawio.svg)

## The steps

1. **kubectl:** reads your **kubeconfig** (which cluster, which user, which context), turns the YAML into JSON, and sends an **HTTPS request** to the API server.
2. **API server: authentication.** Who are you? A client certificate, a token, or OIDC. On EKS, your IAM identity is mapped through **access entries**.
3. **API server: authorization (RBAC).** May this user `create` or `patch` Deployments in this namespace? If not, `Forbidden`.
4. **API server: admission.**
   - **Mutating** admission first: it sets defaults and may change the object (for example, inject a sidecar).
   - Then **schema validation**.
   - Then **validating** admission: Pod Security, ResourceQuota, policy engines like Kyverno.
   - Any of these can reject the request.
5. **etcd:** the Deployment is **saved**. kubectl gets "created/configured". **Nothing is running yet.**
6. **Deployment controller** (in the controller manager) sees the new Deployment and creates a **ReplicaSet**.
7. **ReplicaSet controller** sees "3 wanted, 0 exist" and creates **3 Pod objects**. They have **no node** yet, so they show as `Pending`.
8. **Scheduler** sees unscheduled pods. For each one it **filters** nodes (enough requested CPU and memory? taints? affinity? volume zone?), **scores** the rest, and **binds** the pod to the best node by setting `spec.nodeName`.
9. **kubelet** on that node sees a pod assigned to it, and through the **CRI** asks containerd to:
   1. create the **pod sandbox** (a tiny "pause" container that holds the pod's network namespace);
   2. call the **CNI plugin**, which **assigns the pod IP** and connects the network;
   3. **pull the image(s)**;
   4. run the **init containers** in order, then start the **app containers** (and sidecars).
10. **kubelet** runs the **startup, liveness and readiness probes**, and reports the pod's status to the API server.
11. **When the pod is Ready:** the EndpointSlice controller adds its IP to the Service's **EndpointSlice**, and **kube-proxy** on every node updates its rules. **Traffic now reaches the pod.**

Each step records **events**. Watch them with `kubectl get events --sort-by=.lastTimestamp -w`.

## Where it gets stuck, and which step is to blame ⭐

| What you see | Stuck at step | Typical cause |
|---|---|---|
| `Error from server (Forbidden)` | 3 (RBAC) | Your user or ServiceAccount lacks permission |
| `admission webhook … denied` or `violates PodSecurity` | 4 (admission) | Policy, Pod Security level, or quota exceeded |
| Deployment exists but no pods | 6–7 (controllers) | Quota blocks pod creation (see the ReplicaSet's events) |
| `Pending` | 8 (scheduler) | No node fits: requests too big, taints, affinity, PVC in another zone |
| `ContainerCreating` for a long time | 9 (sandbox, CNI, volumes) | No pod IPs left (EKS VPC CNI), volume can't attach, CNI broken |
| `ImagePullBackOff` / `ErrImagePull` | 9.3 (image pull) | Wrong name or tag, private registry without credentials, rate limit |
| `CrashLoopBackOff` | 9.4 (container start) | App crashes on start: bad config, missing env, OOM. Check `logs --previous`. |
| `Running` but `0/1` ready | 10 (readiness probe) | Wrong probe path or port, app not ready, dependency down |
| Ready, but the Service gets no traffic | 11 (endpoints) | Selector doesn't match the labels, wrong `targetPort`, NetworkPolicy |

> **Docker link:** step 9 is `docker run` under the hood: containerd → runc → namespaces and cgroups ([Docker 02](../docker/02-architecture-internals.md)). The difference is that Kubernetes decides **which machine** and keeps reconciling afterwards.

## Interview angle

- ⭐ "Walk me through what happens after `kubectl apply`." → tell the 11 steps as a story: authentication → RBAC → admission → etcd → Deployment controller → ReplicaSet controller → scheduler → kubelet (sandbox → CNI → image → containers) → probes → endpoints → kube-proxy.
- "When does the pod get its IP?" → in step 9, when the kubelet creates the pod sandbox and calls the CNI plugin, **before** the app containers start.
- "Does `kubectl apply` returning success mean the app is running?" → no; it only means the object was **saved**. Check `kubectl rollout status`.
- "Which component decides which node a pod runs on?" → the scheduler, using **requests** (not actual usage), taints and affinity.

## Practice 🖥️

```bash
kubectl apply -f practice/deploy.yaml
kubectl get events --sort-by=.lastTimestamp -w
kubectl get deploy,rs,pods -o wide
kubectl rollout status deployment/web
kubectl get endpointslices -l kubernetes.io/service-name=web
```

Run the events command in a second terminal before applying, and read the story as it happens.
