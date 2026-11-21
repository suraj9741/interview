# NiCE AWS L2 · the 14 questions they actually asked (19 Nov)

**How to use this tab:** these are the real questions from your L2 round. For each one: type the answer you **gave** in the box first (be honest), then open the card and compare. Mark "Missed it" for anything you'd now answer differently. Those are your misses for the next interview. Send me what you answered and I'll score it.

## Kubernetes

<details><summary>1. A StatefulSet application has a PV attached. You change the name of the PV. What happens?</summary>

**Short answer:** you **can't rename** a Kubernetes object. `metadata.name` is its identity. If you change the name in the YAML and apply it, Kubernetes creates a **second, new PV** and leaves the old one untouched. Nothing happens to the running pod: its PVC is still bound to the **old** PV, and the data stays there.

**Why, step by step:**
- A PVC and a PV are bound to each other **by name**: the PVC's `spec.volumeName` names the PV, and the PV's `spec.claimRef` names the PVC.
- New name in the manifest → `kubectl apply` sees an object that doesn't exist → creates a new PV. It stays **Available** (unbound), because the PVC is already bound to the old one.
- If you then **delete the old PV** while it's in use, it gets stuck in **Terminating**: the `kubernetes.io/pv-protection` finalizer blocks deletion until the PVC stops using it.
- In a StatefulSet, the PVCs come from `volumeClaimTemplates`, named `<template>-<statefulset>-<ordinal>` (for example `data-mysql-0`). Changing the template name on a live StatefulSet is **rejected**: that field is immutable after creation.

**What happens to the data depends on the reclaim policy:** `Retain` keeps the disk after the PVC is deleted, while `Delete` (the default for dynamically created EBS volumes) deletes the disk too.

**How to really "move" a StatefulSet to a new volume:** snapshot the EBS volume (or back up with Velero), create a new PV/PVC from the snapshot, and point the pod at it. That's a planned migration, not a rename.

**30-second answer:** "A PV's name can't be changed. Applying a new name creates a second PV, while the PVC stays bound to the old one by name, so the pod keeps using the old data. Deleting the old PV in use gets it stuck in Terminating because of the protection finalizer, and a StatefulSet's volumeClaimTemplates are immutable. To move the data you'd snapshot and restore into a new PVC."
</details>

<details><summary>2. Node affinity vs taints and tolerations.</summary>

**The one-line difference:** **node affinity attracts** a pod to certain nodes (it's set on the **pod**). A **taint repels** pods from a node (it's set on the **node**), and a **toleration** lets a specific pod ignore that taint.

| | Node affinity | Taint + toleration |
|---|---|---|
| Set on | Pod spec | Taint on the node, toleration on the pod |
| Effect | "This pod wants or needs nodes with label X" | "Keep pods off this node unless they tolerate it" |
| Types | `requiredDuringScheduling…` (hard) and `preferredDuringScheduling…` (soft) | `NoSchedule`, `PreferNoSchedule`, `NoExecute` (also evicts running pods) |
| Forces placement? | Yes (required) | **No**: a toleration only *allows* the node, it doesn't send the pod there |

**Why you often need both:** for dedicated GPU nodes, taint them (`gpu=true:NoSchedule`) so ordinary pods stay away, **and** give GPU pods a toleration **plus** node affinity for `gpu=true`, so they go there and nowhere else.

```bash
kubectl taint nodes node1 gpu=true:NoSchedule
kubectl label nodes node1 gpu=true
```
```yaml
tolerations:
- key: "gpu"
  operator: "Equal"
  value: "true"
  effect: "NoSchedule"
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: gpu
          operator: In
          values: ["true"]
```

**Real-world example:** control-plane nodes carry `node-role.kubernetes.io/control-plane:NoSchedule`, which is why your app pods never land there.
</details>

<details><summary>4. A pod is Pending after deploy, but CPU and memory are fine. What do you check?</summary>

**First command:** `kubectl describe pod <name>` → read **Events** at the bottom. The scheduler writes the reason, for example `0/3 nodes are available: 1 node(s) had untolerated taint, 2 node(s) didn't match Pod's node affinity`.

**If it's not CPU or memory, it's one of these:**
1. **Taints** on the nodes that the pod doesn't tolerate.
2. **nodeSelector or node affinity** that matches no node (a typo in a label).
3. **PVC not bound**: no matching PV or StorageClass, or an **EBS volume in another AZ** than the free nodes (EBS can't cross AZs). Check `kubectl get pvc`.
4. **Pod anti-affinity or topology spread** rules that can't be satisfied (for example "one per node" but more replicas than nodes).
5. **Too many pods per node on EKS**: each instance type has a max pods / IP limit with the VPC CNI (a t3.medium allows 17 pods). The node shows free CPU but no free IPs or pod slots.
6. **Nodes NotReady or cordoned** (`kubectl get nodes`, look for `SchedulingDisabled`).
7. **hostPort** already used on every node.
8. **Requests too big for any single node**, even if the cluster total has room: 4 nodes with 2 free CPUs each can't fit a pod requesting 3 CPUs.

**Fix it at the source:** add the toleration or label, fix the PVC or StorageClass (`volumeBindingMode: WaitForFirstConsumer` avoids the AZ problem), relax the anti-affinity, or add nodes (Cluster Autoscaler or Karpenter only add nodes if a new node *would* fit the pod).

**30-second answer:** "Describe the pod and read the FailedScheduling event; it names the reason. If it's not resources, it's usually taints, a nodeSelector or affinity that matches nothing, an unbound PVC or an EBS volume in another AZ, anti-affinity rules, or on EKS the per-node pod and IP limit."
</details>

<details><summary>14. The cluster is on an older version (your note says 1.3x) and we want to upgrade to the latest. What process do you follow?</summary>

**Rule 1: one minor version at a time.** The control plane can't skip versions: 1.31 → 1.32 → 1.33, never 1.31 → 1.33. Each hop is a full cycle.

**The process (EKS, per hop):**
1. **Read the release notes and find removed APIs.** Use EKS **Upgrade insights** in the console, or `kubent` / `pluto` to scan manifests and Helm charts. Fix anything deprecated **before** upgrading (for example old `PodSecurityPolicy`, `v1beta1` APIs).
2. **Check add-on and tool compatibility:** VPC CNI, CoreDNS, kube-proxy, EBS CSI, AWS Load Balancer Controller, ingress, cert-manager, ArgoCD, Karpenter versions for the new Kubernetes version.
3. **Back up:** Velero backup of resources and volumes, and confirm Git (ArgoCD) holds everything.
4. **Upgrade a non-prod cluster first** and run the tests.
5. **Upgrade the control plane** (Terraform: change `cluster_version` / `version`, plan, apply; or `eksctl upgrade cluster`). Takes about 10–20 minutes; the API stays available.
6. **Upgrade the nodes:** managed node groups do a rolling replacement (cordon, drain, new AMI). With Karpenter, nodes are replaced by drift. **PodDisruptionBudgets** keep enough replicas up during the drain.
7. **Upgrade the add-ons** to the versions matching the new Kubernetes version.
8. **Verify:** `kubectl get nodes` (all on the new version), pods healthy, dashboards and error rates normal. Then repeat for the next minor version.

**Version skew rule:** nodes (kubelet) may be **older** than the control plane by up to 3 minor versions, but **never newer**. That's why the control plane goes first.

**30-second answer:** "One minor version at a time. Before each hop I check removed APIs with upgrade insights or pluto, check add-on compatibility, back up with Velero, and test in non-prod. Then control plane first through Terraform, then nodes as a rolling replacement with PDBs protecting the apps, then the add-ons, then verify, and repeat."
</details>

## AWS

<details><summary>3. In Route 53, how do you create a record pointing to an ALB? And the difference between Alias and CNAME.</summary>

**Steps (console):**
1. Route 53 → **Hosted zones** → your domain (for example `example.com`).
2. **Create record** → name: empty for the apex, or `www` / `app`.
3. Type **A**, turn **Alias** on.
4. Route traffic to: **Alias to Application and Classic Load Balancer** → region → choose the ALB.
5. Optional: **Evaluate target health** = yes. Add an **AAAA** alias too if the ALB is dual-stack (IPv6).
6. Create, then test: `dig app.example.com` returns the ALB's IPs.

**In Terraform:**
```hcl
resource "aws_route53_record" "app" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "app.example.com"
  type    = "A"

  alias {
    name                   = aws_lb.web.dns_name
    zone_id                = aws_lb.web.zone_id
    evaluate_target_health = true
  }
}
```

**Alias vs CNAME:**
| | Alias (Route 53 only) | CNAME |
|---|---|---|
| Points to | AWS resources (ALB, NLB, CloudFront, S3 website, API Gateway) or a record in the same zone | Any other DNS name |
| Zone apex (`example.com`) | **Allowed** | **Not allowed** (the apex has SOA/NS records, and a CNAME can't sit beside other records) |
| Record type | A / AAAA, answers with IPs directly | CNAME, the client must do a second lookup |
| Cost | Queries to AWS targets are **free** | Normal query price |
| TTL | Taken from the target (60 s for an ALB) | You set it |

**Why an Alias for an ALB:** the ALB's IP addresses change; AWS only gives you its DNS name. An Alias follows the current IPs automatically.
</details>

<details><summary>5. You have 100 EC2 instances and want to push some code and copy an image to all of them. What strategy do you use?</summary>

**First, ask one clarifying question:** "Is this a one-off change to running servers, or how we deploy from now on?" Then give both answers.

**A. Change the running servers (mutable): AWS Systems Manager.**
- **SSM Run Command** (`AWS-RunShellScript`) targeted **by tag** (`Role=web`), not by listing 100 IDs.
- Set **rate control**: max concurrency (for example 10%) and an error threshold (stop if 5% fail). That's a rolling deploy with a safety brake.
- The code or image comes from **S3** (`aws s3 cp`) or **ECR** (`docker pull`). The instances need an IAM role and the SSM agent; no SSH or open ports required, and every run is logged.
- Alternatives: **Ansible** with the dynamic EC2 inventory (`forks` and `serial` for batches), or **CodeDeploy** (rolling, health checks, automatic rollback).

**B. The better long-term strategy (immutable): bake a new AMI.**
- Build an AMI containing the new code with **Packer** or **EC2 Image Builder**.
- Update the **Auto Scaling group's launch template** to the new AMI, then run an **instance refresh** (rolling replacement, minimum healthy percentage, for example 90%).
- No drift between servers, rollback = previous launch template version.

**If "image" means a Docker image:** push once to **ECR**, then every instance runs `docker pull` through SSM. With 100 servers running containers, this is the point where you'd suggest ECS or EKS instead.

**30-second answer:** "For a one-off change I'd use SSM Run Command targeted by tag, pulling the code or image from S3 or ECR, with rate control so it rolls 10% at a time and stops on errors. Long term I'd bake a new AMI with Packer or Image Builder and roll it out through the Auto Scaling group's instance refresh, which keeps all 100 identical and makes rollback easy."
</details>

<details><summary>6. EC2 needs to read from S3. The role and all configuration are in place. Explain the full flow: how do EC2 and S3 actually connect?</summary>

**The flow, in order:**
1. **Instance profile:** the role is attached to the instance through an instance profile.
2. **Credentials from metadata:** the AWS SDK/CLI on the instance follows its **credential chain** and reaches the instance metadata service at `169.254.169.254`. With **IMDSv2** it first gets a session token (`PUT /latest/api/token`), then reads `/latest/meta-data/iam/security-credentials/<role-name>`.
3. **Temporary credentials:** metadata returns an access key, secret key and **session token** issued by **STS**, valid for a few hours and rotated automatically.
4. **Signed request:** the SDK signs the S3 request with those credentials (**Signature Version 4**) and sends it over **HTTPS**.
5. **Network path:**
   - Public subnet: instance → route table `0.0.0.0/0 → IGW` → S3's public endpoint.
   - Private subnet: either **NAT gateway** → IGW → S3, or better a **gateway VPC endpoint** for S3: the route table gets a route `pl-xxxx (S3 prefix list) → vpce-…`, traffic stays inside AWS, and it's free.
6. **Authorisation at S3:** S3 checks the role's **IAM policy**, the **bucket policy**, the **VPC endpoint policy** (if used), SCPs, and **KMS key policy** if the object is SSE-KMS encrypted. An explicit Deny anywhere wins.
7. **Response:** the object comes back over the same HTTPS connection.

**Prove each step on the instance:**
```bash
aws sts get-caller-identity          # which role am I? (steps 1-3)
aws s3 ls s3://my-bucket/            # list (needs s3:ListBucket on the bucket ARN)
aws s3 cp s3://my-bucket/file.txt .  # get (needs s3:GetObject on bucket/*)
```

**30-second answer:** "The role is attached through an instance profile. The SDK gets temporary STS credentials from the instance metadata service, IMDSv2 with a token, signs the request with SigV4 and sends it over HTTPS. From a private subnet it goes through a gateway VPC endpoint or the NAT, and S3 then evaluates the IAM policy, bucket policy, endpoint policy and KMS if encrypted before returning the object."
</details>

<details><summary>7. An EC2 instance in a private subnet needs to connect to RDS. What are the steps, and how does the connection work?</summary>

**Setup steps:**
1. **RDS in private DB subnets** in the same VPC: a **DB subnet group** with subnets in at least 2 AZs, `publicly_accessible = false`.
2. **Security groups:** RDS SG inbound **5432 (Postgres) / 3306 (MySQL) from the EC2's security group**, referenced by SG ID, not a CIDR. The EC2 SG allows outbound to it (default allow-all egress does).
3. **Routing:** nothing to add. Both are in the same VPC, so the **`local` route** carries the traffic. NACLs must allow the port and the return ephemeral ports.
4. **Credentials:** store them in **Secrets Manager** (RDS can manage and rotate them). The EC2 role is allowed `secretsmanager:GetSecretValue`, or use IAM database authentication.

**How a connection works:**
1. The app resolves the **RDS endpoint** (`mydb.xxxx.ap-south-1.rds.amazonaws.com`). Inside the VPC it resolves to the DB's **private IP**.
2. TCP connection from the EC2's ENI to the RDS ENI on 5432 over the local route.
3. The RDS SG allows it because the source carries the EC2's SG.
4. The database authenticates the user (password from Secrets Manager), ideally over **TLS**.

**Test from the EC2 (connect with SSM Session Manager, no SSH):**
```bash
dig +short mydb.xxxx.ap-south-1.rds.amazonaws.com    # private IP?
nc -zv mydb.xxxx.ap-south-1.rds.amazonaws.com 5432   # timeout = SG/NACL, refused = wrong port
psql -h mydb.xxxx... -U appuser -d appdb             # auth works?
```

**If RDS is in another VPC:** peering or Transit Gateway with routes on both sides, SG rules by CIDR, and DNS resolution over the peering.
</details>

<details><summary>9. Difference between a private and a public subnet.</summary>

**The only real difference is the route table.**
| | Public subnet | Private subnet |
|---|---|---|
| Default route | `0.0.0.0/0 → Internet Gateway` | `0.0.0.0/0 → NAT gateway` (or no default route at all) |
| Instances reachable from the internet? | Yes, if they also have a **public IP / Elastic IP** and the SG allows it | **No**: nothing on the internet can start a connection in |
| Outbound internet | Directly through the IGW | Through the NAT (outbound only) |
| Typical contents | ALB, NAT gateway, bastion | App servers, EKS nodes, RDS, caches |

**Common traps:**
- An instance in a public subnet **without** a public IP still can't reach or be reached from the internet.
- `map_public_ip_on_launch` doesn't make a subnet public; the route to the IGW does.
- The NAT gateway itself must live in a **public** subnet.
- Both have the `local` route, so they can always talk to each other inside the VPC (subject to SGs and NACLs).

**30-second answer:** "A subnet is public when its route table sends 0.0.0.0/0 to the internet gateway, and instances there with a public IP can be reached from the internet. A private subnet routes outbound traffic through a NAT gateway, so instances can reach out but nothing can connect in. The ALB and NAT go public; apps, nodes and databases go private."
</details>

<details><summary>12. How does a Network Load Balancer work, and where does it sit in the OSI model?</summary>

**OSI layer 4 (transport).** It routes on **IP address, protocol and port**; it never reads HTTP.

**How it works:**
- Listeners on **TCP, UDP, TCP_UDP or TLS** ports.
- For each new connection it picks a healthy target using a **flow hash** (protocol, source IP and port, destination IP and port), and the whole connection stays on that target.
- It gives you **one static IP per AZ**, or your own Elastic IPs, which customers can whitelist in their firewalls.
- **Preserves the client's source IP** for instance and IP targets (or sends it with Proxy Protocol v2).
- Handles millions of requests per second with very low latency.
- **Health checks** with TCP, HTTP or HTTPS.
- Target types: instance, IP (pods on EKS, on-prem servers), or an **ALB**.
- **Cross-zone load balancing is off by default** (data transfer charges if you turn it on). Security groups can be attached (supported since 2023).
- **TLS listener:** the NLB can terminate TLS with an ACM certificate, still without reading HTTP.

**NLB vs ALB:**
| NLB (layer 4) | ALB (layer 7) |
|---|---|
| TCP/UDP/TLS, any protocol | HTTP/HTTPS/gRPC only |
| Static IP per AZ | IPs change (use DNS) |
| Can't route by path or host | Routes by path, host, headers |
| Client IP preserved | Client IP in `X-Forwarded-For` |
| Databases, MQTT, gaming, static-IP needs | Web apps, microservices, WAF |

**30-second answer:** "The NLB is layer 4: it balances TCP, UDP and TLS connections by IP and port, using a flow hash so a connection sticks to one target. It gives a static IP per AZ, keeps the client IP, and scales to millions of requests per second. I'd use it for non-HTTP traffic or static IPs, and an ALB for HTTP routing."
</details>

## Terraform

<details><summary>8. Write the Terraform to create an EC2 instance. What resource block do you write?</summary>

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

data "aws_ami" "al2023" {            # look up the latest Amazon Linux 2023 AMI
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = "t3.micro"
  subnet_id              = var.subnet_id                   # which subnet (public or private)
  vpc_security_group_ids = [var.sg_id]                     # firewall
  iam_instance_profile   = var.instance_profile_name       # role (SSM, S3...)
  key_name               = var.key_name                    # optional, if you use SSH

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  metadata_options {
    http_tokens = "required"                               # IMDSv2
  }

  user_data = <<-EOT
    #!/bin/bash
    dnf install -y nginx
    systemctl enable --now nginx
  EOT

  tags = {
    Name = "web-1"
  }
}

output "instance_id" {
  value = aws_instance.web.id
}

output "private_ip" {
  value = aws_instance.web.private_ip
}
```

**Say the shape first:** "provider, a data source for the AMI, then `aws_instance` with ami, instance_type, subnet_id, security groups, IAM instance profile, disk, user_data and tags, then outputs." Required arguments are only **`ami`** and **`instance_type`**; everything else decides where it runs and how it's secured.

**Then the commands:** `terraform init` → `terraform plan -out=tfplan` → `terraform apply tfplan`.

The full network version (VPC, subnets, NAT, route tables, SGs, ALB) is card E3b on the AWS L2 tab.
</details>

## Linux and scripting

<details><summary>10. I want to run a script, but if someone already ran it within the last hour, it must not run again. How do you achieve that?</summary>

**Two problems to solve:** don't run if the **last run was less than an hour ago**, and don't run **twice at the same moment**. Use a **timestamp file** for the first and **`flock`** for the second.

```bash
#!/usr/bin/env bash
set -euo pipefail

STAMP=/var/tmp/myjob.last_run      # remembers when it last ran
LOCK=/var/tmp/myjob.lock           # prevents two copies at once
MIN_GAP=3600                        # seconds (1 hour)

exec 9>"$LOCK"
flock -n 9 || { echo "Already running, exiting."; exit 0; }

if [[ -f "$STAMP" ]]; then
  last=$(stat -c %Y "$STAMP")       # file modification time, in epoch seconds
  now=$(date +%s)
  if (( now - last < MIN_GAP )); then
    echo "Ran $(( (now - last) / 60 )) min ago; next run allowed after 60 min. Exiting."
    exit 0
  fi
fi

echo "Running the job..."
# ... real work here ...

touch "$STAMP"                      # record success only at the end
```

**Explain each part:**
- `exec 9>"$LOCK"` opens the lock file on file descriptor 9; `flock -n 9` takes the lock or fails immediately (`-n` = don't wait). The lock is released automatically when the script exits, even if it crashes.
- `stat -c %Y` gives the last-modified time of the stamp file in seconds since 1970; `date +%s` gives now. The difference is the age.
- `touch` at the **end** means a failed run doesn't count, so it can be retried.

**One-liner alternatives:** `find "$STAMP" -mmin -60 | grep -q . && exit 0` (the file was modified in the last 60 minutes). For a scheduled job: a systemd timer or cron combined with `flock -n /var/tmp/myjob.lock /path/script.sh`.

**30-second answer:** "I'd keep a timestamp file and compare its modification time with now; if it's under 3600 seconds, exit. I'd also wrap it with flock so two people can't run it at the same moment, and only touch the stamp at the end so a failed run can be retried."
</details>

<details><summary>11. A shell script hits an error at line 10, but it keeps running. I want it to stop at that point. How?</summary>

**By default bash ignores errors** and moves to the next line. Turn on strict mode at the top:

```bash
#!/usr/bin/env bash
set -euo pipefail
```
- `-e`: **exit immediately** if any command returns non-zero. This is the answer to the question.
- `-u`: treat unset variables as errors (catches typos like `$FIEL`).
- `-o pipefail`: a pipeline fails if **any** command in it fails, not just the last (`grep x missing.txt | sort` would otherwise "succeed").

**Report where it failed:**
```bash
trap 'echo "Error on line $LINENO: $BASH_COMMAND" >&2' ERR
```

**For one specific command only:**
```bash
cp /src/file /dst/ || { echo "copy failed"; exit 1; }
```

**Traps to mention (shows depth):**
- `set -e` does **not** trigger for commands in an `if` condition, or on the left of `&&` / `||`.
- If you **expect** a command might fail, allow it explicitly: `grep -q pattern file || true`.
- Check the exit code yourself with `$?` right after a command when you need custom handling.

**30-second answer:** "Add `set -euo pipefail` at the top: -e stops at the first failing command, -u catches unset variables, and pipefail makes pipelines fail if any part fails. I'd add `trap ... ERR` to print the failing line, and use `|| exit 1` or `|| true` where I want explicit handling."
</details>

## Git

<details><summary>13. Two developers changed the same file. One merged to master; the second gets a merge conflict. How do you resolve it?</summary>

**What's happening:** both changed the **same lines**, so Git can't decide whose version to keep. The second developer must combine them by hand.

**Steps (developer 2, on their feature branch):**
```bash
git fetch origin
git merge origin/master          # or: git rebase origin/master
# CONFLICT (content): Merge conflict in app/config.py
git status                       # lists the conflicted files
```
The file now contains markers:
```
<<<<<<< HEAD
timeout = 30          # your version
=======
timeout = 60          # version already on master
>>>>>>> origin/master
```
1. Edit the file: keep one side, or combine both, and **delete all three marker lines**.
2. Talk to developer 1 if unsure which change is right.
3. Test the code.
4. Mark it resolved and finish:
```bash
git add app/config.py
git commit                       # merge: completes the merge commit
# with rebase instead: git rebase --continue
git push                         # after a rebase: git push --force-with-lease
```
5. The pull request updates and can be merged.

**Escape hatch:** `git merge --abort` (or `git rebase --abort`) returns to the state before you started.

**Preventing conflicts:** small, short-lived branches, pull from master often, split large files, and agree on formatting (a formatter) so whitespace changes don't conflict.

**Merge vs rebase in one line:** merge keeps both histories with a merge commit; rebase replays your commits on top of master for a straight history. Never rebase a branch others are using.
</details>
