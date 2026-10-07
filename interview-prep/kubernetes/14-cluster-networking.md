# 14 · Cluster Networking and NetworkPolicy ⭐

## The Kubernetes networking model (4 rules) ⭐

1. **Every pod gets its own IP address.**
2. **Every pod can reach every other pod**, on any node, **without NAT**.
3. Node agents (the kubelet) can reach every pod on their node.
4. The IP a pod sees for itself is the same IP others use to reach it.

Kubernetes **doesn't implement** this itself. A **CNI plugin** does.

## CNI plugins: how the rules are made true

| Plugin | How pods on different nodes talk | Notes |
|---|---|---|
| **AWS VPC CNI** (EKS default) | Pods get **real VPC IPs** from the node's network interfaces (ENIs); the VPC routes them | No overlay, so it's fast and pods are visible to VPC tools (Security Groups, Flow Logs). ⚠️ **Uses up subnet IPs** ([20](20-eks.md)) |
| **Calico** | BGP routing or an overlay (VXLAN/IP-in-IP) | Strong NetworkPolicy support |
| **Cilium** | eBPF in the kernel; overlay or native routing | Can **replace kube-proxy**; deep visibility (Hubble) |
| **Flannel** | Simple VXLAN overlay | **No** NetworkPolicy enforcement |

**Pod-to-pod across two nodes (overlay):** pod A's `eth0` → a veth pair → the node's network stack → the packet is **wrapped** (VXLAN) with node IPs → node B unwraps it → veth → pod B's `eth0`. With the VPC CNI there's no wrapping: the VPC routes pod IPs directly.

**Pod to the internet:** the node rewrites the pod's source IP to its own (SNAT), then the traffic goes out through a NAT Gateway or Internet Gateway (AWS model answers Q10–Q11).

**Pod to a Service:** kube-proxy's DNAT rules on the sending node ([08](08-services-and-dns.md)).

## NetworkPolicy: the pod firewall ⭐

![NetworkPolicy: allowed and blocked traffic](diagrams/14-networkpolicy.drawio.svg)

- **Default: everything is allowed.** Any pod can talk to any pod in any namespace.
- When a policy **selects** a pod (`podSelector`) for a direction (`Ingress` and/or `Egress`), that pod **only** allows traffic that some policy permits. Policies only **add** permissions together; there are no "deny" rules.
- Sources and destinations: `podSelector`, `namespaceSelector`, `ipBlock` (CIDR), plus ports.
- ⚠️ **AND vs OR:** `namespaceSelector` and `podSelector` in the **same** `from` item = **AND** (these pods in those namespaces). In **separate** items = **OR**. This is a common mistake.
- ⚠️ **Only enforced if the CNI supports it.** Calico, Cilium and the AWS VPC CNI (with network policy turned on) do; Flannel doesn't. Without support, policies are **silently ignored**.

```yaml
# 1. Default deny: no traffic in or out of any pod in the namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: shop
spec:
  podSelector: {}
  policyTypes: ["Ingress", "Egress"]
---
# 2. ⚠️ Allow DNS, or after a default deny NOTHING can resolve names
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: shop
spec:
  podSelector: {}
  policyTypes: ["Egress"]
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
---
# 3. Allow frontend → backend on 8080 (frontend also needs a matching egress rule)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-allow-frontend
  namespace: shop
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: ["Ingress"]
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

> **Docker link:** Docker's `docker0` bridge, veth pairs and iptables NAT ([Docker 08](../docker/08-networking.md)) are a single-host version of the same idea. In Kubernetes the CNI wires up the whole cluster, and **no port mapping is needed**, because every pod has its own IP.

## Interview angle

- ⭐ "Explain the Kubernetes networking model." → the 4 rules, implemented by a CNI plugin.
- ⭐ "How does a pod on node A reach a pod on node B?" → veth → node → overlay wrapping or VPC routing → node B → veth. Name your cluster's CNI.
- ⭐ "After adding a default-deny policy, the app can't resolve anything. Why?" → egress to CoreDNS on port 53 (UDP **and** TCP) is blocked. Add an allow-DNS policy.
- "Are pods isolated by namespace?" → no. Namespaces don't isolate network traffic; NetworkPolicy does.
- "We added a NetworkPolicy and nothing changed." → the CNI doesn't enforce policies (Flannel, or the VPC CNI's policy feature isn't on).

## Practice 🖥️

```bash
kubectl create namespace shop
kubectl -n shop create deployment backend --image=nginx:1.27
kubectl -n shop expose deployment backend --port=80
kubectl -n shop run client --rm -it --image=busybox:1.36 --restart=Never -- wget -qO- -T 3 backend
kubectl apply -f practice/networkpolicies.yaml
kubectl -n shop run client --rm -it --image=busybox:1.36 --restart=Never -- wget -qO- -T 3 backend
```

The last command should now fail. If it still works, your kind network plugin may not enforce NetworkPolicy; install Calico to test.
