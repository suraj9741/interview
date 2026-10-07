# 09 · Ingress and Gateway API

## The problem they solve

- A `LoadBalancer` Service for **every** app means a separate cloud load balancer per app: expensive, and only layer 4 (TCP).
- You usually want **one entry point** with **layer 7 (HTTP) routing**: by host (`api.shop.com`) and path (`/api`), plus **TLS** termination.

## Ingress

Ingress has **two parts** (the Instagram handbook blurs them):
1. The **Ingress object**: just routing **rules** in YAML.
2. An **Ingress controller**: the software that **reads the rules and actually routes traffic**. Without a controller, an Ingress does **nothing**.

| Field | Meaning |
|---|---|
| `ingressClassName` | Which controller should handle this Ingress (for example `alb`, `nginx`) |
| `rules[].host` | Match the hostname |
| `paths[].pathType` | `Prefix` (`/api` matches `/api/x`), `Exact`, or `ImplementationSpecific` |
| `backend.service` | Which Service and port receive the traffic |
| `tls` | Hosts and certificate for HTTPS |
| Annotations | Controller-specific extras (rewrites, timeouts, ALB settings) |

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shop
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  ingressClassName: alb
  tls:
  - hosts:
    - shop.example.com
  rules:
  - host: shop.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
```

## The two common paths on AWS ⭐

![Ingress paths on AWS, and Gateway API](diagrams/09-ingress-paths.drawio.svg)

| | AWS Load Balancer Controller | An in-cluster controller (NGINX, Traefik, Envoy-based) |
|---|---|---|
| What the Ingress becomes | A real **ALB** in your VPC | Routing config inside controller pods |
| Traffic path | Internet → **ALB → pod IPs directly** (`target-type: ip`), or ALB → NodePort (`instance`) | Internet → **NLB → controller pods → Service's pods** |
| TLS | **ACM** certificate on the ALB | cert-manager + Let's Encrypt, or a Secret |
| Load balancers | One ALB per Ingress, or shared with `group.name` | One NLB in front of the controller |

## ⚠️ Current status (2026), worth saying in an interview

- The **Ingress API** is still stable and supported, but **feature-frozen**: no new features.
- The community **ingress-nginx** controller was **retired**. Retirement was announced in November 2025, and maintenance ended in **March 2026**. Teams are migrating, often with the `ingress2gateway` tool.
- **Gateway API** (stable since v1.0 in October 2023) is the **successor**.

## Gateway API

It splits responsibility between **roles**, instead of one object plus vendor annotations:

| Resource | Owned by | Purpose |
|---|---|---|
| **GatewayClass** | Infrastructure provider | Which implementation (AWS, Envoy Gateway, Istio, Cilium…) |
| **Gateway** | Platform / cluster team | Listeners: ports, protocols, hostnames, TLS |
| **HTTPRoute** / GRPCRoute / TCPRoute | App teams | Routing rules → Services |

What it adds over Ingress: header and query matching, **weighted traffic splitting** (built-in canary), request mirroring, cross-namespace routing (with `ReferenceGrant`), and a standard API instead of annotations. Gateway API resources are **CRDs** that you install ([19](19-extending-kubernetes.md)).

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: shop-api
spec:
  parentRefs:
  - name: public-gateway
  hostnames:
  - shop.example.com
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /api
    backendRefs:
    - name: api-v1
      port: 80
      weight: 90
    - name: api-v2          # canary: 10% of traffic
      port: 80
      weight: 10
```

## 5xx errors at the Ingress (links to model answers Q28–Q29)

| Status | Usual cause |
|---|---|
| **503** | The Service has **no ready endpoints** (selector mismatch or failing readiness), or an ALB target group with no healthy targets |
| **502** | The pod **reset or closed the connection**, wrong `targetPort` or protocol, the app crashed, or the app's keep-alive timeout is **shorter** than the load balancer's idle timeout |
| **504** | The app is too slow; the load balancer or controller timed out |
| **404** | No rule matched: wrong host, `pathType` or path, or the wrong `ingressClassName` |

## Interview angle

- ⭐ "Ingress vs LoadBalancer Service?" → layer 7 routing for many services behind one entry point vs one layer 4 load balancer per service.
- ⭐ "What is an Ingress controller?" → the component that implements Ingress rules; without one, an Ingress does nothing.
- ⭐ "Ingress vs Gateway API?" → Gateway API is the role-based, more powerful successor (traffic splitting, header matching); Ingress is frozen, and ingress-nginx was retired in 2026.
- "How does traffic reach a pod with the AWS Load Balancer Controller?" → ALB → pod IP directly (IP mode), using VPC CNI pod IPs ([20](20-eks.md)).
- "`/api` works but `/api/v2` returns 404." → check `pathType` (Exact vs Prefix), rewrite annotations, and rule order.

## Practice 🖥️ (read-only commands; work on any cluster with an Ingress)

```bash
kubectl get ingressclass
kubectl get ingress -A
kubectl describe ingress shop
kubectl get endpointslices -l kubernetes.io/service-name=api
curl -v -H "Host: shop.example.com" http://<load-balancer-address>/api
```
