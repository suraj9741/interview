# 17 · Kubernetes Troubleshooting ⭐

![Troubleshooting flowchart](diagrams/17-troubleshooting-flowchart.drawio.svg)

**The method, in this order:** `get pods -o wide` → `describe pod` (events, exit code) → `logs --previous` → `get events` → `exec` / `debug` → traffic (`svc`, `endpointslices`, NetworkPolicy, Ingress) → node (`describe node`, `top`).

## Every common problem ⭐

| You see | Usual causes | Check / fix |
|---|---|---|
| `Pending` | Requests too big, taints, affinity, PVC, quota | `describe pod` events ([13](13-scheduling.md)) |
| `ContainerCreating` (stuck) | Volume attach, no IPs (EKS VPC CNI), missing ConfigMap/Secret, CNI | `describe pod` events |
| `ImagePullBackOff` | Name/tag typo, no registry creds or IAM, rate limit, wrong arch | Events show the pull error |
| `CrashLoopBackOff` | App error, bad config/env, DB down, **OOMKilled**, harsh liveness | `logs --previous`, exit code |
| `CreateContainerConfigError` | ConfigMap / Secret / key in `env` missing | `describe` names it |
| `OOMKilled` (137) | Leak or limit too low | Raise limit or fix leak; `kubectl top` |
| `Running`, `0/1` READY | Probe path/port, app not ready, dependency | `describe` probe failures ([06](06-probes.md)) |
| `Completed` in a Deployment | Process exited 0 (a script, not a server) | Keep it in the foreground |
| `Evicted` | Node low on memory/disk | `describe node`, set requests ([12](12-resources-and-autoscaling.md)) |
| `Terminating` (stuck) | Finalizers; node gone | Fix the controller; last resort `--grace-period=0 --force` |
| Node `NotReady` | kubelet / runtime down, disk full, network | `describe node`, kubelet on the node |
| Service **no endpoints** | Selector ≠ labels, not Ready, wrong ns | `get endpointslices` ([08](08-services-and-dns.md)) |
| **Connection refused** | `targetPort` ≠ container port; app on `127.0.0.1` | `exec`, test `localhost:<port>` |
| DNS fails | CoreDNS down, policy blocks 53, `ndots` | `nslookup` from a debug pod |
| Ingress 503 / 502 / 504 / 404 | No endpoints / reset / timeout / no rule | [09](09-ingress-and-gateway-api.md) |
| `Forbidden` | Missing Role or Binding | `kubectl auth can-i … --as=…` ([15](15-security.md)) |
| `violates PodSecurity` | Root, privileged, no securityContext | Fix securityContext |

**Exit codes** ([Docker 04](../docker/04-containers.md)): `0` done · `1` app error · `127` command not found · `137` SIGKILL (often OOM) · `143` SIGTERM.

## `kubectl debug`

```bash
kubectl debug -it <pod> --image=busybox:1.36 --target=<container>          # add a debug container; sees app processes
kubectl debug <pod> -it --copy-to=<pod>-debug --container=<container> -- sh # copy the pod with a shell
kubectl debug node/<node> -it --image=busybox:1.36                         # pod on the node, host FS at /host
kubectl run tmp --rm -it --image=nicolaka/netshoot --restart=Never -- bash # all the network tools
```

## Interview angle (say these out loud)

| Question | Answer |
|---|---|
| ⭐ CrashLoopBackOff? | `describe` (exit code, OOMKilled?) → `logs --previous` → config/env → liveness → fix, roll out. |
| ⭐ Pending? | `describe` events → resources, taints, affinity, PVC, quota. |
| ⭐ Running but unreachable? | Readiness → endpoints (selector) → `targetPort` → NetworkPolicy → DNS → Ingress/LB. |
| Node NotReady? | Conditions, kubelet + runtime, disk, network. Pods evicted after ~5 min. |

## Practice 🖥️ (more in the [old plan, Day 2](../devops-interview-prep-plan.md))

```bash
kubectl create deployment broken --image=nginx:does-not-exist   # ImagePullBackOff on purpose
kubectl get pods -w
kubectl describe pod -l app=broken
kubectl set image deployment/broken nginx=nginx:1.27
```
