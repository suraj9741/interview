# 08 · Services and DNS ⭐

Every new pod gets a new IP. A Service gives a **stable virtual IP**, a **stable DNS name** and **load balancing** over the **ready** pods matching its label selector.

![How Service traffic flows](diagrams/08-service-traffic.drawio.svg)

- ⭐ The ClusterIP is **not a machine**: kube-proxy writes DNAT rules on every node, and the client node's kernel rewrites the packet.
- You **can't ping** it in iptables / nftables mode (rules exist only for its TCP/UDP ports). IPVS mode put it on a dummy interface, so ping answered. Cilium can replace kube-proxy with eBPF.

## Service types

![Service types](diagrams/08-service-types.drawio.svg)

| Setting | Effect |
|---|---|
| `sessionAffinity: ClientIP` | Same client → same pod |
| `externalTrafficPolicy: Local` | Keeps client source IP, no extra hop; only nodes with a local pod get traffic |
| `externalTrafficPolicy: Cluster` (default) | Spreads evenly, rewrites the source IP |
| No selector + your own EndpointSlice | Point a Service at IPs outside the cluster |

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  type: ClusterIP
  selector:
    app: web
  ports:
  - name: http
    port: 80
    targetPort: 8080
```

## DNS (CoreDNS) ⭐

![DNS lookup in a pod](diagrams/08-dns-lookup.drawio.svg)

- SRV records exist for named ports: `_http._tcp.web.shop.svc.cluster.local`.
- Model answers Q3 and Q6 go deeper on `ndots`.

> **Docker link:** Docker's DNS at `127.0.0.11` resolves names on one network ([Docker 08](../docker/08-networking.md)); Services + CoreDNS do it cluster-wide.

## Interview angle

| Question | Answer |
|---|---|
| ⭐ ClusterIP vs NodePort vs LoadBalancer vs headless? | Use the Service types diagram. |
| ⭐ How does a ClusterIP work if nothing listens? | kube-proxy DNAT rules on every node; the client node's kernel picks a ready pod. |
| ⭐ Service has no endpoints? | Selector ≠ labels, pods not Ready, or wrong namespace. |
| Headless Service for? | One DNS record per pod (StatefulSets) instead of one virtual IP. |
| Keep the client's real IP? | `externalTrafficPolicy: Local`, or proxy protocol / `X-Forwarded-For`. |

## Practice 🖥️

```bash
kubectl create deployment web --image=nginx:1.27 --replicas=3
kubectl expose deployment web --port=80 --target-port=80
kubectl get svc web
kubectl get endpointslices -l kubernetes.io/service-name=web
kubectl run tmp --rm -it --image=busybox:1.36 --restart=Never -- sh
# inside: nslookup web · wget -qO- web · cat /etc/resolv.conf
```
