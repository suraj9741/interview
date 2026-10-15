# 11 · Storage

A container's filesystem disappears when it's recreated. **Volumes** outlive the container, or the pod.

![PVC to PV to cloud disk](diagrams/11-storage-flow.drawio.svg)

| Object | Scope | What it is |
|---|---|---|
| **PV** | Cluster | A real disk or share (EBS, NFS) |
| **PVC** | Namespace | A **request**: size + access mode + class |
| **StorageClass** | Cluster | **How** to create storage: provisioner + parameters |

- **Dynamic** (normal): PVC → CSI driver creates a disk → PV bound to the PVC. **Static:** admin makes PVs first.
- PVC: `Pending` → `Bound`. **`reclaimPolicy`:** `Delete` (default) or `Retain` (keep disk + data).
- **`WaitForFirstConsumer`:** create the disk after scheduling, **in the pod's AZ**. Essential for EBS.
- `allowVolumeExpansion: true` lets you grow a PVC.

## Volume types

| Type | Lives as long as | Use |
|---|---|---|
| `emptyDir` | The pod | Scratch, sharing between containers; `medium: Memory` = RAM |
| `configMap` / `secret` / `projected` | The pod | Config as files ([10](10-configmaps-and-secrets.md)) |
| `hostPath` | The node | ⚠️ Avoid; system agents only |
| `persistentVolumeClaim` | **Independent** | Databases, anything that must persist |
| Generic ephemeral | The pod | Big scratch on real disks |

## Access modes

| Mode | Meaning | Example |
|---|---|---|
| `ReadWriteOnce` (RWO) | One **node** writes | **EBS** |
| `ReadOnlyMany` (ROX) | Many nodes read | Reference data |
| `ReadWriteMany` (RWX) | Many nodes write | **EFS**, NFS |
| `ReadWriteOncePod` (RWOP) | One **pod** writes | Strict single writer |

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: gp3
  resources:
    requests:
      storage: 10Gi
```

- **CSI** drivers: EBS CSI, EFS CSI (EKS add-ons, [20](20-eks.md)). **VolumeSnapshots** for backups.
- StatefulSet `volumeClaimTemplates`: one PVC per pod (`data-db-0`), **kept** after scale-down.

## Classic problems

| Symptom | Cause / fix |
|---|---|
| Pod `Pending`: "volume node affinity conflict" | Disk in AZ-a, pod in AZ-b → `WaitForFirstConsumer`, nodes in every AZ |
| PVC stuck `Pending` | No default StorageClass, CSI driver missing or no IAM, RWX on EBS |
| PVC stuck `Terminating` | Still mounted: `pvc-protection` finalizer ([03](03-objects-and-api.md)) |

> **Docker link:** volume ≈ **PVC**, bind mount ≈ **hostPath**, tmpfs ≈ **emptyDir `medium: Memory`** ([Docker 07](../docker/07-storage.md)).

## Interview angle

| Question | Answer |
|---|---|
| ⭐ PV vs PVC vs StorageClass? | Storage vs request vs recipe. |
| ⭐ Two nodes writing one EBS volume? | Can't: RWO and one AZ. Use EFS (RWX). |
| Data when the pod / PVC is deleted? | Pod: nothing happens. PVC: depends on `reclaimPolicy`. |
| StatefulSet storage? | `volumeClaimTemplates`: one PVC per pod that follows it. |

## Practice 🖥️ (kind has a default StorageClass `standard`)

```bash
kubectl get storageclass
kubectl apply -f practice/pvc-and-pod.yaml
kubectl get pvc,pv
kubectl exec storage-demo -- sh -c 'echo hello > /data/test.txt'
kubectl delete pod storage-demo
kubectl apply -f practice/pvc-and-pod.yaml
kubectl exec storage-demo -- cat /data/test.txt   # survives: it's on the PVC
```
