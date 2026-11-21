#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/scenario-questions/**/*.md.

Run once:  python3 tools/diagrams_scenario_qa.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "scenario-questions" / "diagrams"
W = 1100


def row(d, prefix, y, items, *, h=90, x0=20, width=1060, gap=24, chain=True, size=11, labels=None):
    """Evenly spaced boxes in one row. items = [(text, colour), ...]. Returns the ids."""
    n = len(items)
    bw = (width - gap * (n - 1)) / n
    ids = []
    for i, (text, colour) in enumerate(items):
        ids.append(d.box(f"{prefix}{i}", x0 + i * (bw + gap), y, bw, h, text, colour, size=size))
        if chain and i:
            d.edge(ids[i - 1], ids[i], labels[i - 1] if labels else None)
    return ids


def caption(d, y, text, h=70, size=11, align="center"):
    d.text("cap", 20, y, W - 40, h, text, size=size, align=align)


# ----------------------------------------------------------------------------- AWS
def aws_01():
    d = Diagram("aws-01-ha-ec2", W, 560, "Multi-AZ web tier: no single point of failure in one region")
    d.box("dns", 380, 50, 340, 50, "Route 53 alias → ALB (optional CloudFront + WAF)", "purple", size=11)
    d.box("alb", 380, 125, 340, 55, "Application Load Balancer\npublic subnets in 3 AZs · health check /health", "blue", size=11)
    d.edge("dns", "alb")
    for i, az in enumerate(["AZ a", "AZ b", "AZ c"]):
        x = 20 + i * 360
        d.group(f"g{i}", x, 205, 340, 230, f"{az}", "gray", dashed=True)
        d.box(f"nat{i}", x + 20, 375, 300, 45, "public subnet: NAT gateway (one per AZ)", "white", size=11)
        d.box(f"ec2{i}", x + 20, 240, 300, 55, "private subnet: EC2 from launch template\n(ASG member, no public IP)", "green", size=11)
        d.box(f"db{i}", x + 20, 310, 300, 50, ["RDS primary (writer)", "RDS standby (sync copy)", "Aurora replica / spare"][i], "orange", size=11)
        d.edge("alb", f"ec2{i}")
    d.text("asg", 20, 440, W - 40, 30, "Auto Scaling group spans all three private subnets · health_check_type = ELB · instance refresh for deploys", size=12, bold=True)
    caption(d, 470, "Stateless instances: sessions in ElastiCache/DynamoDB/DB, files in S3. Over-provision per AZ: losing 1 of 3 AZs removes a third\n"
                    "of capacity at once. Prove it: terminate an instance, force an RDS failover, run an AZ fault-injection test.", h=70)
    return d


def aws_02():
    d = Diagram("aws-02-region-migration", W, 470, "Moving EC2 to another region = build a copy, sync data, cut over DNS")
    row(d, "s", 60, [("1 · Prepare target\nVPC, SG, IAM, KMS key,\nkey pair (Terraform)", "gray"),
                     ("2 · Lower DNS TTL\n300 s → 60 s\na day before", "yellow"),
                     ("3 · create-image\n(AMI of the instance)\nsource region", "blue"),
                     ("4 · copy-image\nto target region\n--kms-key-id", "blue"),
                     ("5 · Launch + test\nnew EIP if needed\n(EIPs don't move)", "green")], h=100)
    row(d, "c", 200, [("6 · Sync changed data\nrsync / DB replica /\nS3 CRR / AWS MGN", "orange"),
                      ("7 · Cutover\nstop writes, final sync,\nswitch Route 53 record", "red"),
                      ("8 · Keep old one\nrollback window,\nthen delete it", "purple")], h=100)
    d.edge("s4", "c0", points=[(990, 180), (190, 180)])
    caption(d, 330, "Regional things that DON'T move: AMI, EBS snapshot, security group, key pair, Elastic IP, subnet IDs, ARNs.\n"
                    "Stateless server → AMI or rebuild from launch template (≈0 downtime). Changing data → continuous replication (MGN,\n"
                    "DB replica, promote) so the cutover is minutes. Check instance-type availability and quotas in the new region.", h=100)
    return d


def aws_03():
    d = Diagram("aws-03-ssh-debug", W, 520, "SSH not working? Read the error, then go from the outside in")
    row(d, "e", 50, [("Connection timed out\n→ network path", "red"), ("Connection refused\n→ sshd / host firewall", "orange"),
                     ("Permission denied (publickey)\n→ key or user name", "yellow")], h=60, chain=False, size=12)
    row(d, "s", 140, [("1 · Instance\nrunning?\n2/2 status checks?", "blue"), ("2 · Public IP /\nEIP? changed\nafter stop/start?", "blue"),
                      ("3 · Route table\n0.0.0.0/0 → IGW\n(public subnet)", "blue"), ("4 · Security group\ninbound 22 from\nmy IP (stateful)", "blue"),
                      ("5 · NACL\n22 in AND\n1024-65535 out", "blue"), ("6 · OS\ndisk full, sshd,\nfirewall, keys", "green")], h=100, gap=16)
    d.box("ra", 20, 270, 520, 50, "Reachability Analyzer: which component blocks the path?", "white", size=11)
    d.box("log", 560, 270, 520, 50, "get-console-output / screenshot: kernel panic, fsck, disk full", "white", size=11)
    row(d, "d", 350, [("SSM Session Manager\nno port 22 needed", "purple"), ("EC2 Instance Connect\n(+ EIC Endpoint)", "purple"),
                      ("EC2 Serial Console\nNitro, boot problems", "purple"), ("Rescue instance\ndetach root volume, fix", "red")], h=65, chain=False)
    caption(d, 430, "Side doors when SSH is dead (bottom row). Inside: df -h; df -i; systemctl status sshd; sshd -t; ss -tlnp | grep :22;\n"
                    "ls -ld ~/.ssh (700) and authorized_keys (600). System check failed = AWS host → stop/start. Instance check failed = your OS.", h=70)
    return d


def aws_04():
    d = Diagram("aws-04-auto-scaling", W, 500, "Spiky traffic: react fast, keep capacity cheap")
    d.group("gf", 20, 50, 520, 300, "React fast", "blue")
    d.box("tt", 40, 90, 480, 55, "Target tracking: ALBRequestCountPerTarget = 1000\n(or CPU 50-60%), set and forget", "blue", size=11)
    d.box("st", 40, 155, 480, 55, "Step scaling: +2 at 70%, +6 at 90%\nbig jumps for big breaches", "blue", size=11)
    d.box("wp", 40, 220, 480, 55, "Warm pool (stopped, pre-initialised) + baked AMI\n+ default instance warmup", "green", size=11)
    d.box("bf", 40, 285, 480, 50, "Buffers in front: CloudFront cache, SQS queue, WAF rate limit", "white", size=11)
    d.group("gc", 560, 50, 520, 300, "Keep it cheap", "green")
    d.box("od", 580, 270, 480, 60, "On-Demand base (min capacity)\ncovered by Savings Plans", "orange", size=11)
    d.box("sp", 580, 90, 480, 160, "Spot above the base: mixed instances policy\non_demand_percentage_above_base_capacity = 20\n"
          "price-capacity-optimized across 6-10 types, all AZs\ncapacity rebalancing\nscale out fast, scale in slow", "yellow", size=11)
    caption(d, 370, "Policies: target tracking (default) · step (big spikes) · simple (legacy) · scheduled (known times) · predictive (repeating patterns).\n"
                    "Leading metric beats CPU. Raise max_size and vCPU quotas before you need them. Spot gives a 2-minute warning:\n"
                    "never put stateful or non-interruptible work there.", h=100)
    return d


def aws_05():
    d = Diagram("aws-05-scheduled-scaling", W, 470, "Dynamic scaling reacts AFTER the spike; scheduled scaling is ready BEFORE it")
    d.group("gd", 20, 50, 520, 250, "Dynamic only (09:00 login spike)", "red")
    row(d, "a", 95, [("09:00\ntraffic 5×", "red"), ("09:01\nalarm fires", "orange"), ("09:05\nnew instances\nin service", "yellow")],
        x0=40, width=480, h=80, gap=20)
    d.box("ab", 40, 200, 480, 80, "Users get slow responses / 5xx\nfor the first ~5 minutes every morning", "white", size=11)
    d.group("gs", 560, 50, 520, 250, "Scheduled + dynamic", "green")
    row(d, "b", 95, [("08:45\nmin 2 → 10", "green"), ("09:00\ntraffic 5×\ncapacity ready", "green"), ("19:00\nmin 10 → 2", "blue")],
        x0=580, width=480, h=80, gap=20)
    d.box("bb", 580, 200, 480, 80, "Target tracking still on top\nfor anything bigger than planned", "white", size=11)
    caption(d, 320, "Use scheduled when you KNOW the time: office-hours spikes, flash sales / launches, month-end batch, dev/QA to zero at night.\n"
                    "put-scheduled-update-group-action --recurrence \"45 8 * * MON-FRI\" --time-zone Asia/Kolkata --min-size 10\n"
                    "Predictive scaling = AWS learns repeating daily/weekly patterns; it can't predict a one-off launch.", h=100)
    return d


def aws_06():
    d = Diagram("aws-06-s3-recovery", W, 520, "S3 backups unavailable: first find WHICH kind of unavailable")
    d.box("q", 400, 50, 300, 50, "Error message + CloudTrail: what happened?", "purple", size=12)
    causes = [("Objects deleted /\noverwritten", "remove delete markers /\ncopy old version back\n(needs versioning)", "green"),
              ("AccessDenied:\nbucket policy", "root user can always\ndelete-bucket-policy,\nthen fix it", "yellow"),
              ("KMS key disabled /\npending deletion", "cancel-key-deletion +\nenable-key (within\n7-30 day window)", "orange"),
              ("Bucket deleted", "restore from CRR replica\n(other account) or\nAWS Backup", "red"),
              ("Region outage", "point apps at the\nreplica / Multi-Region\nAccess Point", "blue")]
    for i, (c, fix, col) in enumerate(causes):
        x = 20 + i * 216
        d.box(f"c{i}", x, 140, 200, 60, c, "white", size=11)
        d.box(f"f{i}", x, 230, 200, 80, fix, col, size=11)
        d.edge("q", f"c{i}")
        d.edge(f"c{i}", f"f{i}")
    d.box("prev", 20, 340, 1060, 80, "Set up BEFORE: versioning · MFA Delete · Object Lock (compliance mode) · Cross-Region Replication to a separate backup account\n"
          "· AWS Backup for S3 with vault lock · reviewed lifecycle rules · KMS deletion window 30 days + alarm · alarms on PutBucketPolicy / DeleteBucket\n"
          "· monthly restore tests", "gray", size=11, align="left")
    caption(d, 440, "Delete markers are not replicated by default, so a replica survives accidental deletes. After a KMS key is really deleted,\n"
                    "data encrypted with it can never be decrypted. Glacier tiers need restore-object first (minutes to 48 h).", h=60)
    return d


def aws_07():
    d = Diagram("aws-07-iam-audit", W, 480, "IAM audit: inventory → usage → exposure → continuous rules → fix")
    row(d, "s", 60, [("Credential report\nusers, MFA, passwords,\nkey age + last used,\nroot keys", "blue"),
                     ("Last accessed\n(Access Advisor)\nunused services /\nroles", "blue"),
                     ("Access Analyzer\nexternal access,\nunused access,\npolicy validation", "purple"),
                     ("Authorization details\nevery user, role,\ngroup, policy\n(wildcards, trusts)", "blue"),
                     ("Config + Security Hub\nCIS / FSBP rules\nCloudTrail org trail", "orange")], h=110)
    d.box("fix", 20, 210, 1060, 90, "Fix: delete unused users/keys/roles · enforce MFA · IAM Identity Center (SSO) for humans · OIDC roles for CI\n"
          "· remove * actions/resources · ExternalId on third-party trusts · SCPs + permission boundaries · policies generated from CloudTrail\n"
          "· quarterly access review with owners", "green", size=11, align="left")
    d.edge("s2", "fix")
    caption(d, 320, "aws iam generate-credential-report → get-credential-report --query Content --output text | base64 -d\n"
                    "aws iam generate-service-last-accessed-details --arn <role>  ·  aws iam get-account-authorization-details\n"
                    "Many accounts: Organizations + delegated admin for Security Hub, Access Analyzer and a Config aggregator.", h=100)
    return d


def aws_08():
    d = Diagram("aws-08-cross-account", W, 500, "Partner access: they assume a role in OUR account (no IAM users, no keys)")
    d.group("gp", 20, 50, 380, 300, "Partner account 444455556666", "gray")
    d.box("pr", 50, 100, 320, 70, "role/acme-integration\nidentity policy: allow sts:AssumeRole\non our role ARN", "blue", size=11)
    d.box("call", 50, 220, 320, 90, "aws sts assume-role\n--role-arn …partner-acme-readonly\n--external-id acme-7f3c9a\n→ temporary creds (1 h default)", "white", size=11)
    d.edge("pr", "call")
    d.group("go", 440, 50, 640, 300, "Our account 111122223333", "gray")
    d.box("trust", 470, 90, 280, 110, "Trust policy (WHO)\nPrincipal: partner role ARN\nCondition: sts:ExternalId\n(stops confused deputy)", "purple", size=11)
    d.box("perm", 780, 90, 280, 110, "Permissions policy (WHAT)\ns3:ListBucket prefix acme/*\ns3:GetObject acme/*\n(+ KMS key policy decrypt)", "green", size=11)
    d.box("s3", 470, 240, 590, 80, "s3://our-exports/acme/  ·  CloudTrail logs every call as the role session\n"
          "tags: owner, partner, expires=2027-03-31  ·  Access Analyzer shows it as external access", "orange", size=11)
    d.edge("call", "trust", "AssumeRole")
    d.edge("trust", "perm")
    d.edge("perm", "s3")
    caption(d, 370, "Both sides must allow it: our trust policy AND their identity policy. Alternatives: resource policy (bucket / KMS / SQS),\n"
                    "AWS RAM (subnets, TGW), S3 Access Points, pre-signed URLs, IAM Roles Anywhere (workload outside AWS).\n"
                    "Never Principal \"*\" with only an ExternalId. MaxSessionDuration 1-12 h; role chaining caps it at 1 h.", h=100)
    return d


def aws_09():
    d = Diagram("aws-09-s3-security", W, 520, "S3 for compliance: secure the path, the bytes, the access, and prove it")
    d.group("gt", 20, 50, 520, 210, "In transit", "blue")
    d.box("t1", 40, 90, 480, 50, "Bucket policy: Deny if aws:SecureTransport = false", "blue", size=11)
    d.box("t2", 40, 150, 480, 40, "Deny if s3:TlsVersion < 1.2", "blue", size=11)
    d.box("t3", 40, 200, 480, 45, "VPC gateway endpoint + aws:SourceVpce condition", "white", size=11)
    d.group("gr", 560, 50, 520, 210, "At rest", "green")
    d.box("r1", 580, 90, 480, 50, "SSE-KMS with a customer managed key + Bucket Key\n(SSE-S3 is only the default since Jan 2023)", "green", size=11)
    d.box("r2", 580, 150, 480, 40, "Key rotation, deletion window 30 days, tight key policy", "green", size=11)
    d.box("r3", 580, 200, 480, 45, "DSSE-KMS / client-side if rules demand it", "white", size=11)
    row(d, "a", 285, [("Block Public Access\n+ ACLs disabled", "orange"), ("Least privilege on\nS3 AND KMS", "orange"),
                      ("Versioning + Object Lock\n(WORM retention)", "purple"), ("CloudTrail data events\n+ Macie (PII)", "yellow"),
                      ("Config rules\nssl-requests-only,\nsse-enabled", "yellow")], h=80, chain=False, gap=16)
    caption(d, 390, "Changing default encryption doesn't re-encrypt old objects: copy in place or S3 Batch Operations.\n"
                    "Force YOUR key with a Deny on s3:PutObject when s3:x-amz-server-side-encryption-aws-kms-key-id isn't your key ARN.\n"
                    "Bucket Key = far fewer KMS requests, much lower cost.", h=100)
    return d


def aws_10():
    d = Diagram("aws-10-lambda-envs", W, 500, "Lambda across environments: one artifact, separate accounts, alias-based rollout")
    d.box("ci", 20, 60, 230, 90, "CI builds ONCE\norders/<git_sha>.zip\nsigned (AWS Signer)", "purple", size=11)
    envs = [("dev account", "auto deploy", "green"), ("staging account", "auto deploy + tests", "yellow"), ("prod account", "manual approval", "red")]
    for i, (e, how, col) in enumerate(envs):
        x = 300 + i * 265
        d.box(f"e{i}", x, 60, 245, 90, f"{e}\nOIDC deploy role\n{how}", col, size=11)
        d.edge("ci" if i == 0 else f"e{i - 1}", f"e{i}", "promote" if i else None)
    d.box("alias", 300, 190, 510, 90, "alias live → version 7 (90%) + version 8 (10%)\nCodeDeploy canary 10% for 5 min, alarm → auto rollback\nrollback = point the alias back", "blue", size=11)
    d.edge("e2", "alias")
    d.box("sec", 830, 190, 250, 90, "Secrets Manager / SSM\nenv var holds only the ARN\n(params & secrets extension)", "orange", size=11)
    d.box("role", 20, 190, 260, 90, "Execution role per function\nleast privilege\nreserved concurrency", "green", size=11)
    caption(d, 310, "$LATEST is mutable; versions are immutable; triggers point at the alias. Environment variables are encrypted at rest but visible\n"
                    "to anyone with GetFunctionConfiguration, so no secrets there. Code signing config rejects unsigned code.\n"
                    "Lambda is NOT on your resume: transfer the pattern from EKS (build once, promote the same artifact, OIDC, manual prod gate).", h=100)
    return d


# -------------------------------------------------------------------------- Docker
def docker_01():
    d = Diagram("docker-01-multi-cloud", W, 520, "Multi-cloud with compliance: build once, sign, keep data in-region, enforce at admission")
    row(d, "p", 55, [("Approved base image\n(golden list)", "gray"), ("docker buildx build\npush by digest", "blue"),
                     ("trivy image\n--exit-code 1\nCRITICAL,HIGH", "orange"), ("SBOM (syft)\n+ cosign sign\nthe digest", "purple")], h=80)
    regs = [("AWS eu-west-1\nECR → EKS", "yellow"), ("GCP europe-west1\nArtifact Registry → GKE", "green"), ("Azure westeurope\nACR → AKS", "blue")]
    for i, (r, col) in enumerate(regs):
        x = 20 + i * 360
        d.box(f"r{i}", x, 190, 340, 70, r, col, size=11)
        d.box(f"k{i}", x, 285, 340, 70, "Kyverno / Gatekeeper: signed images from\nthis registry only, non-root, no privileged", "white", size=11)
        d.edge("p3", f"r{i}", "replicate" if i == 1 else None)
        d.edge(f"r{i}", f"k{i}")
    caption(d, 375, "Same Helm chart + Argo CD ApplicationSet everywhere; Terraform per cloud with the same module layout.\n"
                    "Secrets from each cloud's store (or Vault) via External Secrets; logs and metrics stay in-region; deploy by digest, not tag.\n"
                    "Multi-cloud, Kyverno, cosign, Harbor are NOT on your resume: present the design, transfer your AWS/EKS experience.", h=100)
    return d


def docker_02():
    d = Diagram("docker-02-live-patch", W, 500, "One host kernel under all containers: patch it live, or make reboots not matter")
    d.box("k", 20, 50, 1060, 50, "Host kernel (shared by every container on the host: patch it once = patched for all; reboot it = all stop)", "red", size=12)
    d.group("ga", 20, 120, 520, 240, "A · Live patch (no reboot)", "orange")
    d.box("a1", 40, 160, 480, 70, "kpatch (RHEL, Amazon Linux) · Canonical Livepatch (Ubuntu)\nSUSE Live Patching · Oracle Ksplice", "orange", size=11)
    d.box("a2", 40, 245, 480, 95, "Patched functions redirected in memory\ncheck: kpatch list · /sys/kernel/livepatch\nonly critical CVEs, not every change\nstill reboot into the new kernel later", "white", size=11)
    d.group("gb", 560, 120, 520, 240, "B · Rolling host replacement (preferred at scale)", "green")
    row(d, "b", 160, [("cordon", "green"), ("drain\n(PDBs hold)", "green"), ("patch/reboot\nor replace", "green"), ("uncordon", "green")],
        x0=580, width=480, h=70, gap=14)
    d.box("b4", 580, 245, 480, 95, "Immutable: new patched AMI → ASG instance refresh\n/ EKS managed node group update; kured automates\nreboots one node at a time. Service stays up because\nreplicas run on other hosts", "white", size=11)
    caption(d, 380, "daemon.json \"live-restore\": true keeps containers running while dockerd restarts. It does NOT survive a kernel reboot.\n"
                    "uname -r still shows the old version after a live patch; that's expected.", h=60)
    return d


def docker_03():
    d = Diagram("docker-03-container-dns", W, 540, "Where a container's DNS query goes")
    d.box("app", 20, 60, 220, 60, "App in container\ngetaddrinfo(\"db\")", "blue", size=11)
    d.box("rc", 280, 60, 240, 60, "/etc/resolv.conf\n(inside the container)", "gray", size=11)
    d.edge("app", "rc")
    d.box("emb", 580, 40, 500, 70, "User-defined network: nameserver 127.0.0.11\nDocker embedded DNS answers container names,\nforwards the rest upstream", "green", size=11)
    d.box("def", 580, 125, 500, 70, "Default bridge: copy of the HOST resolv.conf, no name DNS\nhost has only 127.0.0.53? → Docker falls back to\n8.8.8.8 / 8.8.4.4 (often blocked by corporate firewalls)", "orange", size=11)
    d.edge("rc", "emb")
    d.edge("rc", "def")
    d.box("up", 580, 215, 500, 45, "Upstream: VPC resolver (CIDR base +2) / corporate DNS", "white", size=11)
    d.edge("emb", "up", points=[(1095, 75), (1095, 237)])
    d.box("k8s", 20, 160, 500, 100, "Kubernetes: nameserver = kube-dns ClusterIP → CoreDNS\nsearch <ns>.svc.cluster.local svc.cluster.local …  ndots:5\ncheck CoreDNS pods/logs, NetworkPolicy egress UDP/TCP 53,\nNodeLocal DNSCache, conntrack race", "purple", size=11)
    d.box("steps", 20, 290, 1060, 80, "Steps: cat /etc/resolv.conf → nslookup name vs ping IP → docker run --network container:<c> nicolaka/netshoot dig …\n"
          "→ compare with host (dig, resolvectl) → firewall/iptables, MTU, ip_forward → fix with --dns / daemon.json \"dns\" / user-defined network", "yellow", size=11, align="left")
    caption(d, 390, "Containers copy resolv.conf at start: restart them after host DNS changes. MTU mismatch (VPN, overlay) breaks large UDP answers.\n"
                    "kubectl run dnstest --rm -it --image=busybox:1.36 --restart=Never -- nslookup kubernetes.default", h=60)
    return d


def docker_04():
    d = Diagram("docker-04-policy-as-code", W, 470, "Policy-as-code: the same rules, checked automatically at every stage")
    row(d, "s", 60, [("1 · Dockerfile (CI)\nhadolint\nconftest (Rego)\ntrivy config", "blue"),
                     ("2 · Image (CI)\ntrivy image gate\ncosign sign\nSBOM", "orange"),
                     ("3 · Registry\nscan on push\nimmutable tags", "gray"),
                     ("4 · Admission (K8s)\nKyverno / Gatekeeper\nPod Security Admission", "purple"),
                     ("5 · Runtime\nFalco alerts\nCIS Docker Bench", "red")], h=110)
    d.box("rules", 20, 200, 1060, 80, "Example rules: no :latest base · non-root USER · no secrets in ENV · no CRITICAL CVEs · signed images only ·\n"
          "approved registry only · no privileged / hostPath / hostNetwork · runAsNonRoot · readOnlyRootFilesystem · resource limits", "green", size=11, align="left")
    caption(d, 300, "Policies live in Git, reviewed and unit-tested (kyverno apply / conftest test). Roll out: Audit → fix / record exceptions with expiry → Enforce.\n"
                    "Kyverno = YAML, can mutate/generate/verify images. Gatekeeper = Rego, same language reused by conftest outside K8s.\n"
                    "OPA, Kyverno, Gatekeeper, Falco, cosign, hadolint are NOT on your resume: describe, don't claim.", h=100)
    return d


# ---------------------------------------------------------------------- Kubernetes
def k8s_01():
    d = Diagram("k8s-01-ingress-crash", W, 520, "Ingress controller keeps crashing under load: find why, stabilise, protect")
    d.group("gw", 20, 50, 340, 300, "1 · Why does it die?", "red")
    for i, t in enumerate(["OOMKilled (exit 137)\nmemory limit too low", "Liveness probe fails\nwhen busy → killed → cascade",
                           "CPU throttling\n→ slow → probe timeouts", "Reload storm / fd limits\nworker_connections"]):
        d.box(f"w{i}", 40, 85 + i * 64, 300, 54, t, "white", size=11)
    d.group("gs", 380, 50, 340, 300, "2 · Stabilise now", "orange")
    for i, t in enumerate(["More memory, CPU request\n(drop CPU limit)", "replicas 4 + HPA on CPU", "Lenient liveness,\nstrict readiness",
                           "Spread over AZs, PDB,\ndedicated nodes, priority"]):
        d.box(f"s{i}", 400, 85 + i * 64, 300, 54, t, "yellow", size=11)
    d.group("gp", 740, 50, 340, 300, "3 · Protect it", "green")
    for i, t in enumerate(["Rate limits per client\n(limit-rps annotation)", "CDN + WAF in front", "NLB, externalTraffic\nPolicy: Local",
                           "Alerts on restarts,\nmemory %, p99, 5xx"]):
        d.box(f"p{i}", 760, 85 + i * 64, 300, 54, t, "green", size=11)
    d.edge("gw", "gs")
    d.edge("gs", "gp")
    caption(d, 370, "kubectl describe pod → Last State / Reason / Exit Code · kubectl logs <pod> --previous · kubectl get events --sort-by=.lastTimestamp\n"
                    "Readiness failing just removes a pod from rotation; liveness failing kills it and makes overload worse.\n"
                    "ingress-nginx was announced for retirement (Nov 2025, maintenance to Mar 2026): plan for Gateway API. Check current status.", h=100)
    return d


def k8s_02():
    d = Diagram("k8s-02-region-failover", W, 540, "Region failover only works if region B was built before region A died")
    d.box("r53", 380, 45, 340, 60, "Route 53 failover / latency records\n+ health checks (or Global Accelerator)", "purple", size=11)
    d.group("ga", 20, 125, 500, 230, "Region A (primary) — DOWN", "red", dashed=True)
    d.box("ca", 40, 165, 460, 50, "EKS cluster A (same Terraform modules)", "white", size=11)
    d.box("da", 40, 230, 460, 50, "Aurora writer / RDS primary · S3 · ECR", "white", size=11)
    d.box("argo", 40, 295, 460, 45, "Argo CD + CI must NOT live only here", "orange", size=11)
    d.group("gb", 580, 125, 500, 230, "Region B (standby → active)", "green")
    d.box("cb", 600, 165, 460, 50, "EKS cluster B, synced from the same Git (ApplicationSet)", "green", size=11)
    d.box("db", 600, 230, 460, 50, "Aurora Global secondary → promote / failover", "green", size=11)
    d.box("rb", 600, 295, 460, 45, "ECR replica · S3 CRR · replica secrets · Velero backups", "green", size=11)
    d.edge("r53", "ca", dashed=True)
    d.edge("r53", "cb", "on health-check failure")
    d.edge("da", "db", "replication")
    caption(d, 375, "Runbook: confirm it's the region → freeze deploys → promote the database (accept RPO) → scale up B → DNS shifts → verify → plan fail-back.\n"
                    "Strategy by RTO/RPO: backup & restore (hours) · pilot light · warm standby (minutes) · active-active (~0, hardest data design).\n"
                    "Don't stretch one cluster across regions (etcd latency). Practise with game days.", h=100)
    return d


def k8s_03():
    d = Diagram("k8s-03-namespace-readiness", W, 520, "Every pod in ONE namespace not ready at once? Look at what they SHARE")
    d.box("ns", 380, 50, 340, 80, "namespace payments\nall pods Running, READY 0/1\nService has no endpoints", "red", size=11)
    shared = [("Recent change\nhelm / argocd history,\nrollout history", "purple"), ("Downstream dep\nDB / cache / API down,\npassword rotated", "orange"),
              ("NetworkPolicy\nnew default-deny,\nno egress to DB / 53", "yellow"), ("DNS\nCoreDNS overloaded\nor crashing", "blue"),
              ("Config / Secret\nwrong value,\nexpired TLS cert", "green"), ("Quota / LimitRange\nnew CPU limit →\nthrottling → timeouts", "gray")]
    for i, (t, col) in enumerate(shared):
        x = 20 + i * 178
        d.box(f"s{i}", x, 190, 166, 90, t, col, size=11)
        d.edge("ns", f"s{i}")
    d.box("how", 20, 310, 1060, 70, "How does it fail? describe pod events: HTTP 503 = app says not ready (dependency) · timeout = slow / throttled · refused = not listening\n"
          "Then exec in: wget localhost:8080/ready · nslookup <dep> · nc -zv <dep> 5432 · compare with other namespaces (fine = namespace-scoped cause)", "white", size=11, align="left")
    caption(d, 400, "Fix: roll back the change (helm rollback / argocd / kubectl rollout undo) or fix the dependency.\n"
                    "Lesson: readiness should check what THIS pod needs, not every dependency deeply. Liveness never checks dependencies.", h=60)
    return d


def k8s_04():
    d = Diagram("k8s-04-hpa-too-slow", W, 520, "Time to new capacity is a chain of delays: shorten every link")
    row(d, "c", 55, [("Metrics\nmetrics-server\n15-60 s", "blue"), ("HPA loop\nevery 15 s +\nscale-up policy", "blue"),
                     ("Schedule\nPending if\nno free node", "orange"), ("New node\nCA + ASG\n2-5 min", "red"),
                     ("Image pull\nbig image\n30-90 s", "orange"), ("App startup\nwarm-up until\nreadiness", "yellow")], h=90, gap=16)
    row(d, "f", 175, [("Leading metric:\nRPS / queue\n(KEDA, adapter)", "green"), ("behavior.scaleUp\n300% / 15 s\ntarget 55%", "green"),
                      ("Over-provisioning\npause pods,\npriority -10", "green"), ("Karpenter /\nwarm pools /\nbigger nodes", "green"),
                      ("Small images,\npre-pulled,\nsame region", "green"), ("Faster start,\nright startupProbe", "green")], h=90, gap=16, chain=False)
    for i in range(6):
        d.edge(f"c{i}", f"f{i}", dashed=True)
    d.box("now", 20, 300, 1060, 60, "During the surge: kubectl patch hpa web -p '{\"spec\":{\"minReplicas\":40}}' · check maxReplicas · rate-limit / shed load at ingress · CDN cache · queue writes",
          "red", size=11)
    caption(d, 380, "Known events: pre-scale on a schedule (KEDA cron / CronJob / ASG schedule). HPA adds pods, not nodes.\n"
                    "HPA <unknown> CPU = metrics-server down or pods without CPU requests. More pods don't help a saturated database.\n"
                    "KEDA, Karpenter, Prometheus Adapter are NOT on your resume.", h=100)
    return d


def k8s_05():
    d = Diagram("k8s-05-node-crash", W, 520, "A node dies: what Kubernetes does by itself, and what you must design")
    row(d, "t", 55, [("0 s\nnode dies,\nLease not renewed", "red"), ("~40 s\nNotReady + taint\nunreachable:NoExecute", "orange"),
                     ("NotReady\npods removed from\nService endpoints", "yellow"), ("~340 s\ntolerationSeconds 300\n→ pods evicted", "yellow"),
                     ("ReplicaSet\nrecreates pods\non other nodes", "green"), ("Minutes\nCA / Karpenter / ASG\nreplaces the node", "green")], h=95, gap=14)
    d.group("gd", 20, 180, 520, 200, "Design so it recovers", "green")
    d.box("d1", 40, 215, 480, 150, "replicas ≥ 2-3, topologySpread over zones + hosts\nresource requests + headroom (over-provisioning)\n"
          "PriorityClass for critical pods\ntolerationSeconds: 30 for critical apps\nPDB (protects drains, not crashes)\nalert: node Ready == 0", "white", size=11)
    d.group("gs", 560, 180, 520, 200, "StatefulSet + EBS: needs a push", "red")
    d.box("s1", 580, 215, 480, 150, "won't start a 2nd db-0 while the old pod object exists\nEBS is AZ-bound, attaches to one node\n"
          "confirm instance is gone → kubectl delete node <node>\nor taint out-of-service=nodeshutdown:NoExecute (GA 1.28)\n"
          "last resort: delete pod --grace-period=0 --force\nbetter: RDS / replicated DB operator", "white", size=11)
    caption(d, 400, "DaemonSets come back on the replacement node by themselves. Default 300 s tolerations come from the DefaultTolerationSeconds\n"
                    "admission plugin, so a short network blip doesn't evict everything.", h=60)
    return d


# ----------------------------------------------------------------------- Terraform
def tf_01():
    d = Diagram("tf-01-apply-ok-but-broken", W, 500, "Green apply = the API accepted it, not \"it works\"")
    row(d, "s", 55, [("1 · plan again\nNo changes?\nperpetual diff?", "blue"), ("2 · Right target?\nworkspace, var file,\nregion, alias, account", "yellow"),
                     ("3 · Intent vs state\nvs real: state show,\nconsole, defaults", "orange"), ("4 · Behaviour\nSG/NACL, routes, IAM,\nDNS, user_data", "green"),
                     ("5 · Guard it\ncheck blocks,\npostconditions, tests", "purple")], h=100)
    d.box("gaps", 20, 190, 1060, 110, "Usual gaps: provider defaults you didn't set (target group health path \"/\") · ignore_changes hiding a field ·\n"
          "user_data runs only at first boot · missing dependency (IAM attached after the instance started) · IAM eventual consistency ·\n"
          "lookup() default used silently · two resources managing the same thing (inline SG rules + separate rule resources) ·\n"
          "someone changed it in the console after apply", "white", size=11, align="left")
    caption(d, 320, "TF_LOG=DEBUG TF_LOG_PATH=./tf.log terraform apply shows every API request/response (may contain secrets).\n"
                    "terraform console evaluates expressions · aws iam simulate-principal-policy tests permissions · Reachability Analyzer tests paths.\n"
                    "check { data \"http\" … assert { … } } runs on every plan/apply (1.5+).", h=100)
    return d


def tf_02():
    d = Diagram("tf-02-ci-cd", W, 520, "Terraform in CI/CD: plan on every MR, apply the SAME reviewed plan on main")
    d.group("gm", 20, 50, 1060, 140, "Merge request pipeline (plan role: read-only, via OIDC)", "blue")
    row(d, "m", 90, [("fmt -check\nvalidate", "white"), ("tflint", "white"), ("checkov / trivy\nconftest on plan JSON", "white"),
                     ("plan -out=tfplan\n-lock-timeout=5m", "yellow"), ("plan posted to MR\ntfplan = artifact", "yellow")], x0=40, width=1020, h=80, gap=18)
    d.group("ga", 20, 210, 1060, 140, "main pipeline (apply role: only ref=main, protected)", "green")
    row(d, "a", 250, [("plan again\n(fresh state)", "yellow"), ("manual approval\nprotected environment", "orange"),
                      ("apply tfplan\n(saved file, exact plan)", "green"), ("resource_group:\none run per state", "purple")], x0=40, width=1020, h=80, gap=18)
    d.edge("m4", "a0", "merge", points=[(960, 200), (160, 200)])
    caption(d, 370, "No static keys: GitLab id_tokens → AssumeRoleWithWebIdentity. Remote state with locking + encryption + versioning.\n"
                    "Pin required_version, providers, module ?ref= tags, commit .terraform.lock.hcl. Plan artifacts can hold secrets: short expiry.\n"
                    "Scheduled drift job: plan -detailed-exitcode (0 none · 1 error · 2 changes). Humans have read-only prod access.", h=100)
    return d


def tf_03():
    d = Diagram("tf-03-split-state", W, 520, "One giant state → small states by env / region / layer")
    d.box("big", 20, 60, 300, 150, "prod/terraform.tfstate\n~2,000 resources\nVPC + EKS + RDS + IAM + apps\n8-minute plans · one lock\nhuge blast radius", "red", size=11)
    layers = [("network", "VPC, subnets, NAT", "blue"), ("eks", "cluster, node groups", "green"),
              ("data", "RDS, S3, KMS", "orange"), ("iam", "roles, policies", "purple")]
    for i, (n, t, col) in enumerate(layers):
        d.box(f"l{i}", 420, 50 + i * 45, 300, 38, f"prod/ap-south-1/{n}: {t}", col, size=11)
        d.edge("big", f"l{i}")
    d.box("ssm", 780, 60, 300, 140, "Connect layers with outputs:\nSSM parameters (loose coupling)\nor terraform_remote_state\nor data sources by tag", "yellow", size=11)
    d.edge("l0", "ssm")
    d.box("mv", 20, 240, 1060, 100, "Move without recreating (1.7+): old stack  removed { from = aws_db_instance.app  lifecycle { destroy = false } }\n"
          "new stack  import { to = aws_db_instance.app  id = \"app-prod\" }  → both plans: 0 to destroy\n"
          "older: terraform state pull → state mv -state=old.tfstate -state-out=new.tfstate → state push · within one state: moved { from to }",
          "white", size=11, align="left")
    caption(d, 360, "Back up both states first (terraform state pull > backup.tfstate). Take out what doesn't belong (K8s apps → Argo CD).\n"
                    "Rule of thumb: one state = what one team changes together, plan finishes in a minute or two. -target is not a fix.", h=60)
    return d


def tf_04():
    d = Diagram("tf-04-ten-regions", W, 520, "10 regions: one module, one state per region, parallel runs, canary first")
    d.box("mod", 380, 50, 340, 60, "modules/region (VPC, EKS, RDS…)\nversioned: ?ref=v2.3.0", "purple", size=11)
    d.box("glob", 20, 50, 320, 60, "global/ stack, applied FIRST\nIAM · Route 53 · CloudFront + ACM us-east-1", "orange", size=11)
    regs = ["ap-south-1\n(canary)", "us-east-1", "eu-west-1", "…7 more"]
    for i, r in enumerate(regs):
        x = 20 + i * 270
        d.box(f"r{i}", x, 160, 250, 60, f"regions/{r}", "red" if i == 0 else "green", size=11)
        d.box(f"st{i}", x, 245, 250, 50, "state key prod/<region>/…\nown lock", "white", size=11)
        d.edge("mod", f"r{i}")
        d.edge(f"r{i}", f"st{i}")
    d.box("ci", 20, 320, 1060, 60, "GitLab parallel: matrix REGION=[…10] → 10 plan jobs at once · apply canary → wait → apply the other 9 (or terragrunt run --all)",
          "blue", size=11)
    caption(d, 400, "Region differences via data sources (AZs, AMI from SSM) + per-region vars (non-overlapping CIDRs). Check quotas & instance types per region.\n"
                    "Not 10 provider aliases in one state: slow, one lock, one region's API problem fails all. Terraform can't for_each providers\n"
                    "(OpenTofu 1.9+ can); AWS provider v6 adds a per-resource region argument for a few cross-region resources.", h=100)
    return d


def tf_05():
    d = Diagram("tf-05-faster-runs", W, 480, "Where a Terraform run spends time, and how to cut it")
    row(d, "p", 55, [("init\ndownloads providers\n+ modules", "blue"), ("refresh\nAPI read per resource\nin state", "red"),
                     ("graph walk\nparallelism = 10\nrate limits", "orange"), ("apply\nslow resources\n(RDS, EKS)", "yellow")], h=90)
    row(d, "f", 175, [("TF_PLUGIN_CACHE_DIR\n+ CI cache keyed on\n.terraform.lock.hcl", "green"),
                      ("split states (biggest win)\n-refresh=false for quick\nplans + nightly full plan", "green"),
                      ("-parallelism=20-30\nwatch Rate exceeded;\nno module-level depends_on", "green"),
                      ("only run changed stacks\n(rules: changes:)\nno sleeps / big lookups", "green")], h=90, chain=False)
    for i in range(4):
        d.edge(f"p{i}", f"f{i}", dashed=True)
    d.box("no", 20, 295, 1060, 50, "Don't: -target as a habit (partial state) · -lock=false (state corruption) · huge -parallelism against AWS (throttling)", "red", size=11)
    caption(d, 365, "Measure first: time terraform init / plan · terraform state list | wc -l · TF_LOG=TRACE for slow or throttled calls.\n"
                    "Also: upgrade Terraform/providers, bigger runner in the same region as the state bucket and APIs.", h=60)
    return d


def tf_06():
    d = Diagram("tf-06-partial-apply", W, 520, "Apply failed halfway: repair state, read the plan, then fix forward or revert")
    row(d, "s", 55, [("1 · State healthy?\nforce-unlock (killed job)\nstate push errored.tfstate\nstate pull > backup", "orange"),
                     ("2 · terraform plan\nsee what exists now", "blue"),
                     ("3 · Fix forward\n(permission, quota, value)\nor git revert the MR", "green"),
                     ("4 · plan -out → apply\nonly remaining work\nis done", "green")], h=110)
    rows = [("no change", "succeeded, in state: nothing to do", "white"),
            ("is tainted, so must be replaced", "failed mid-create: let it replace, or untaint if verified OK", "yellow"),
            ("+ create, but it exists in AWS", "orphan (crash before state write): import it", "red"),
            ("+ create, never attempted", "remaining work: next apply does it", "blue")]
    for i, (a, b, col) in enumerate(rows):
        d.box(f"a{i}", 20, 200 + i * 48, 360, 40, a, col, size=11)
        d.box(f"b{i}", 400, 200 + i * 48, 680, 40, b, "white", size=11)
        d.edge(f"a{i}", f"b{i}")
    caption(d, 400, "Terraform isn't transactional but saves each success to state. Never restore an old state file to \"roll back\": it changes Terraform's\n"
                    "memory, not AWS. Full roll-forward procedure + what can't be undone: interview-prep/terraform/08-rollback.md.\n"
                    "Prevent: quotas checked, apply role tested in staging, small MRs and states, keep errored.tfstate as a CI artifact.", h=100)
    return d


# ---------------------------------------------------------------------- Monitoring
def mon_01():
    d = Diagram("mon-01-k8s-prometheus", W, 540, "kube-prometheus-stack: what scrapes what")
    srcs = [("node-exporter\nDaemonSet\nnode CPU, mem, disk", "green"), ("kubelet / cAdvisor\nper-container CPU,\nmemory, throttling", "green"),
            ("kube-state-metrics\nobject state: replicas,\nphase, restarts", "green"), ("API server, CoreDNS\n(EKS: no etcd /\nscheduler / KCM)", "yellow"),
            ("Your apps /metrics\nvia ServiceMonitor /\nPodMonitor", "blue")]
    for i, (t, col) in enumerate(srcs):
        d.box(f"s{i}", 20 + i * 216, 50, 200, 85, t, col, size=11)
    d.box("op", 20, 165, 300, 80, "Prometheus Operator\nturns ServiceMonitor / PodMonitor /\nPrometheusRule CRDs into config", "purple", size=11)
    d.box("prom", 380, 165, 340, 80, "Prometheus (2 replicas, PVC gp3 50Gi)\nretention 15d · externalLabels.cluster", "orange", size=11)
    d.edge("op", "prom")
    for i in range(5):
        d.edge("prom", f"s{i}", "scrape" if i == 2 else None)
    d.box("graf", 20, 290, 330, 70, "Grafana\ndashboards: USE (nodes), RED (services)", "blue", size=11)
    d.box("am", 385, 290, 330, 70, "Alertmanager (2 replicas)\n→ Slack / on-call", "red", size=11)
    d.box("lt", 750, 290, 330, 70, "remote_write → Thanos / Mimir /\nAmazon Managed Prometheus (long term)", "gray", size=11)
    d.edge("prom", "graf")
    d.edge("prom", "am")
    d.edge("prom", "lt")
    caption(d, 385, "helm upgrade --install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace -f values.yaml\n"
                    "Target missing? ServiceMonitor lacks the release label (or set *SelectorNilUsesHelmValues: false), port NAME mismatch, wrong selector.\n"
                    "metrics-server is only for kubectl top / HPA, not history. Watch cardinality: prometheus_tsdb_head_series.", h=100)
    return d


def mon_02():
    d = Diagram("mon-02-alertmanager-slack", W, 520, "From PromQL to a Slack message")
    row(d, "f", 55, [("PrometheusRule\nexpr + for: 5m\nlabels.severity\nannotations.runbook", "blue"),
                     ("Prometheus\nevaluates every 30 s\npending → firing", "orange"),
                     ("Alertmanager\ndedupe · group ·\ninhibit · silence", "red"),
                     ("route by labels\nmatchers:\nseverity / team", "purple")], h=100)
    rec = [("#alerts-critical\n(+ on-call pager)", "red"), ("#team-payments", "yellow"), ("#alerts (default)", "white"), ("Watchdog →\ndead man's switch", "gray")]
    for i, (t, col) in enumerate(rec):
        d.box(f"r{i}", 20 + i * 270, 200, 250, 60, t, col, size=11)
        d.edge("f3", f"r{i}")
    d.box("tim", 20, 290, 520, 80, "group_wait 30s: batch the first alerts of a group\ngroup_interval 5m: new alerts in an existing group\nrepeat_interval 4h: re-send while still firing",
          "white", size=11, align="left")
    d.box("slk", 560, 290, 520, 80, "slack_configs: api_url_file (webhook URL in a Secret),\nchannel, send_resolved: true, title/text templates\ninhibit: critical mutes matching warnings (equal labels)",
          "green", size=11, align="left")
    caption(d, 390, "Test: amtool check-config · amtool config routes test severity=critical · amtool alert add TestAlert …\n"
                    "or curl -XPOST localhost:9093/api/v2/alerts. Silence maintenance: amtool silence add … --duration=2h.\n"
                    "Alert on symptoms, every alert has severity + owner + runbook; critical → pager, warning → Slack.", h=100)
    return d


ALL = [aws_01, aws_02, aws_03, aws_04, aws_05, aws_06, aws_07, aws_08, aws_09, aws_10,
       docker_01, docker_02, docker_03, docker_04,
       k8s_01, k8s_02, k8s_03, k8s_04, k8s_05,
       tf_01, tf_02, tf_03, tf_04, tf_05, tf_06,
       mon_01, mon_02]

if __name__ == "__main__":
    force = "--force" in sys.argv
    warnings = []
    for build in ALL:
        diagram = build()
        warnings += diagram.warnings
        path = diagram.save(OUT, force=force)
        print(f"{'wrote  ' if path else 'skipped'} {diagram.name}.drawio.svg"
              f"{'' if path else '  (exists; use --force to overwrite)'}")
    for w in warnings:
        print("WARN", w)
