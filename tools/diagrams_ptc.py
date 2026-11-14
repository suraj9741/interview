#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/ptc-devops-interview/ (PTC Senior DevOps questions).

Run once:  python3 tools/diagrams_ptc.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "ptc-devops-interview" / "diagrams"


def chain(d, ids):
    for a, b in zip(ids, ids[1:]):
        d.edge(a, b)


# ---------------------------------------------------------------- round 1
def project_pipeline():
    d = Diagram("r1-01-project-pipeline", 1000, 600, "My project: CI builds once, GitOps deploys, EKS runs it, Prometheus watches it")
    d.group("ci", 20, 50, 460, 250, "CI: GitLab CI / Jenkins (build once)", "gray")
    steps = [("dev", "1. Developer\nMR / merge to main", "white"),
             ("test", "2. Lint + unit tests", "blue"),
             ("scan", "3. SonarCloud + image scan", "blue"),
             ("build", "4. docker build\ntag = git SHA", "blue"),
             ("ecr", "5. Push to ECR", "orange"),
             ("bump", "6. Update image tag\nin GitOps repo", "yellow")]
    for i, (sid, label, col) in enumerate(steps):
        d.box(sid, 40 + (i % 2) * 220, 85 + (i // 2) * 70, 200, 52, label, col, size=11)
    chain(d, [s[0] for s in steps])
    d.group("cd", 520, 50, 460, 250, "CD: ArgoCD (pull-based GitOps)", "gray")
    d.box("git", 540, 90, 200, 60, "GitOps repo\nvalues per env:\ndev · uat · prod-int · prod", "yellow", size=10)
    d.box("argo", 760, 90, 200, 60, "ArgoCD in cluster\nwatches Git, applies diff\nfrom inside; OutOfSync=drift", "green", size=10)
    d.box("promote", 540, 175, 300, 110, "Promotion = MR changing env values\n"
          "dev, uat: auto-sync\nprod-int, prod: approval, then sync\n"
          "Rollback = git revert the tag bump\n(ArgoCD re-syncs)", "white", size=11, align="left")
    d.edge("bump", "git")
    d.edge("git", "argo")
    d.group("aws", 20, 320, 960, 260, "AWS account per environment (Terraform-provisioned: VPC, EKS, RDS, IAM)", "blue")
    d.box("users", 40, 360, 120, 50, "Users", "white")
    d.box("r53", 180, 360, 120, 50, "Route 53", "purple")
    d.box("alb", 320, 360, 160, 50, "ALB (2+ AZs)\nAWS LB Controller", "purple", size=11)
    d.group("eks", 500, 350, 460, 140, "EKS: private subnets, managed node groups", "green")
    d.box("ing", 520, 385, 120, 40, "Ingress", "white", size=11)
    d.box("svc", 660, 385, 120, 40, "Service", "white", size=11)
    d.box("pods", 800, 385, 140, 40, "Pods (Deployment)\nHPA", "white", size=10)
    d.box("sec", 520, 440, 420, 36, "Secrets Manager → External Secrets → K8s Secret", "yellow", size=11)
    d.box("rds", 500, 505, 200, 55, "RDS Multi-AZ\n(private DB subnets)", "orange", size=11)
    d.box("mon", 720, 505, 240, 55, "Prometheus + Grafana\nAlertmanager → Slack", "red", size=11)
    d.box("tf", 40, 440, 440, 120, "Terraform (remote state: S3 + locking)\n"
          "modules: vpc, eks, rds, iam · one state per env\n"
          "plan on MR, apply after approval\n"
          "Ansible: config of non-K8s hosts", "white", size=11, align="left")
    chain(d, ["users", "r53", "alb", "ing", "svc", "pods"])
    d.edge("argo", "pods", points=[(860, 320)])
    return d


def pod_service_deployment():
    d = Diagram("r1-04-pod-service-deployment", 900, 470, "Deployment manages ReplicaSets, ReplicaSets keep Pods running, a Service finds Pods by label")
    d.box("dep", 30, 60, 250, 90, "Deployment  web\nreplicas: 3 · strategy: RollingUpdate\nkeeps rollout history (undo)", "blue", size=11)
    d.box("rs", 30, 200, 250, 80, "ReplicaSet  web-7d9f\n\"keep exactly 3 pods\nwith app=web\"", "purple", size=11)
    d.group("pods", 330, 60, 280, 380, "Pods (own IP each, replaceable)", "gray", size=11)
    for i in range(3):
        d.box(f"p{i}", 350, 100 + i * 110, 240, 90,
              f"Pod web-7d9f-{'abc'[i]}\nlabels: app=web\nIP 10.0.{i + 1}.{11 + i}\ncontainer(s) + volumes", "green", size=11)
    d.box("svc", 650, 60, 230, 110, "Service  web (ClusterIP)\nselector: app=web\nstable IP + DNS name\nweb.default.svc.cluster.local", "orange", size=11)
    d.box("eps", 650, 210, 230, 90, "EndpointSlice\nlist of READY pod IPs\n(only pods passing readiness)", "yellow", size=11)
    d.box("client", 650, 350, 230, 70, "Client pod / Ingress\ncalls web:80", "white", size=11)
    d.edge("dep", "rs", "creates / scales")
    for i in range(3):
        d.edge("rs", f"p{i}")
    d.edge("svc", "eps", "selector → IPs")
    d.edge("client", "eps", "kube-proxy rules\npick a ready IP", dashed=True)
    d.box("note", 30, 320, 270, 120, "Pod = smallest unit; ephemeral\nReplicaSet = count; you never\ncreate it by hand\nDeployment = rollouts + rollback\nService = stable address + LB", "white", size=11, align="left")
    return d


def deployment_strategies():
    d = Diagram("r1-05-deployment-strategies", 960, 540, "Rolling vs blue-green vs canary: how traffic moves from v1 to v2")
    cols = [("Rolling update", "blue", ["v1 v1 v1 v1", "v2 v1 v1 v1", "v2 v2 v1 v1", "v2 v2 v2 v2"],
             "Replace pods a few at a time\nmaxSurge / maxUnavailable\n+ no extra env, K8s default\n- v1 and v2 serve together\n- rollback = roll again (slow)"),
            ("Blue-green", "green", ["blue v1: 100%  green v2: 0%", "test green privately", "switch: v2 100%", "keep blue for rollback"],
             "Two full environments\nswitch traffic all at once\n+ instant rollback (switch back)\n+ test v2 before users\n- 2x capacity while both run\n- DB schema must suit both"),
            ("Canary", "orange", ["v1 95%  v2 5%", "watch errors, latency", "v2 25% → 50%", "v2 100% (or abort)"],
             "Send a small % to v2 first\npromote in steps on metrics\n+ smallest blast radius\n+ real-user validation\n- needs traffic splitting +\n  good metrics (Argo Rollouts)")]
    for c, (title, col, steps, notes) in enumerate(cols):
        x = 20 + c * 315
        d.box(f"h{c}", x, 50, 295, 40, title, col, bold=True, size=14)
        prev = f"h{c}"
        for s, label in enumerate(steps):
            sid = f"s{c}{s}"
            d.box(sid, x + 20, 105 + s * 62, 255, 44, label, "white", size=11)
            d.edge(prev, sid)
            prev = sid
        d.box(f"n{c}", x, 360, 295, 160, notes, col, size=11, align="left")
    return d


def terraform_state():
    d = Diagram("r1-06-terraform-state", 900, 470, "Terraform compares three things: your code, the state file, and real AWS")
    d.box("code", 30, 70, 240, 110, "1. Code (.tf)\nwhat you WANT\nresource \"aws_s3_bucket\" \"logs\"", "blue", size=11)
    d.box("state", 330, 70, 240, 110, "2. State (terraform.tfstate)\nwhat Terraform MANAGES\naddress ↔ real ID + attributes\n(JSON, can hold secrets)", "yellow", size=11)
    d.box("real", 630, 70, 240, 110, "3. Real infrastructure\nwhat EXISTS in AWS\nbucket my-logs-prod", "green", size=11)
    d.box("plan", 180, 230, 540, 70, "terraform plan = refresh state from AWS, then diff code vs state\n→ + create   ~ update in place   -/+ replace   - destroy", "purple", size=11)
    d.edge("code", "plan")
    d.edge("state", "plan")
    d.edge("real", "plan", "refresh")
    d.box("backend", 30, 340, 400, 110, "Remote backend (team use)\nS3 bucket: versioning + encryption\nlocking: use_lockfile = true (S3 native, 1.10+)\nor DynamoDB table (older way)", "orange", size=11, align="left")
    d.box("rules", 470, 340, 400, 110, "State rules\nnever edit by hand; use terraform state mv / rm\nnever commit it to Git (secrets inside)\none state per env/component (small blast radius)\nterraform import adopts existing resources", "red", size=11, align="left")
    return d


def iam_role_policy():
    d = Diagram("r1-08-iam-role-policy", 920, 500, "IAM: a policy is the permission document; a role is an assumable identity holding policies")
    d.box("who", 20, 70, 240, 170, "Who needs access\nIAM user (person, long-term keys)\nEC2 instance (instance profile)\nEKS pod (IRSA / Pod Identity)\nLambda function\nanother AWS account\nSSO user", "white", size=11, align="left")
    d.box("trust", 310, 60, 280, 90, "Role: trust policy\nWHO may assume me\n\"Principal\": ec2.amazonaws.com", "purple", size=11)
    d.box("role", 310, 170, 280, 80, "IAM Role  app-prod-role\nno password / keys\nsts:AssumeRole → temporary creds", "purple", size=11)
    d.box("perm", 640, 60, 260, 190, "Permission policy (JSON)\nWHAT is allowed\nEffect: Allow / Deny\nAction: s3:GetObject\nResource: arn:aws:s3:::bucket/*\nCondition: (optional)\nattached to role/user/group", "green", size=11, align="left")
    d.edge("who", "trust", "assume")
    d.edge("trust", "role")
    d.edge("perm", "role")
    d.box("eval", 20, 290, 880, 190, "How AWS decides (policy evaluation)\n"
          "1. Default: everything is DENIED (implicit deny)\n"
          "2. Any explicit Deny anywhere (identity, resource, SCP, boundary) → DENIED, always wins\n"
          "3. Organizations SCP, permissions boundary, session policy: must ALSO allow (they only limit, never grant)\n"
          "4. An Allow in an identity policy or a resource policy (e.g. S3 bucket policy) → ALLOWED\n"
          "Cross-account: BOTH sides must allow (role/user policy in A + resource policy or trust in B)\n"
          "Policy types: AWS managed · customer managed · inline · resource-based (bucket policy, KMS key policy)",
          "yellow", size=12, align="left")
    return d


def load_balancer():
    d = Diagram("r1-09-load-balancer", 960, 520, "Application Load Balancer: listener → rules → target group → healthy targets in 2+ AZs")
    d.box("client", 20, 70, 140, 60, "Client\napp.example.com", "white", size=10)
    d.box("dns", 20, 170, 140, 60, "DNS (Route 53)\nalias → ALB", "purple", size=11)
    d.group("alb", 200, 50, 330, 300, "ALB (public subnets, 2+ AZs)", "orange")
    d.box("l443", 220, 90, 290, 50, "Listener HTTPS :443\nACM certificate, TLS ends here", "white", size=11)
    d.box("rules", 220, 160, 290, 70, "Rules (L7)\nhost: api.* → tg-api\npath: /static/* → tg-web", "white", size=11)
    d.box("l80", 220, 250, 290, 40, "Listener :80 → redirect to 443", "white", size=11)
    d.box("hc", 220, 300, 290, 40, "Health check: GET /health every 30 s", "white", size=11)
    d.group("tg", 570, 50, 370, 300, "Target group tg-api (private subnets)", "green")
    for i, az in enumerate(["AZ-a", "AZ-b", "AZ-a"]):
        ok = i < 2
        d.box(f"t{i}", 590, 90 + i * 80, 330, 60,
              f"Target {i + 1} ({az}) {'healthy' if ok else 'UNHEALTHY'}\n{'gets traffic' if ok else 'taken out of rotation'}",
              "white" if ok else "red", size=11)
    d.edge("client", "dns")
    d.edge("dns", "l443", points=[(180, 200), (180, 115)])
    d.edge("l443", "rules")
    d.edge("rules", "t0")
    d.edge("rules", "t1")
    d.edge("hc", "t2", dashed=True)
    d.box("types", 20, 370, 450, 130, "Types\nALB: L7 HTTP/HTTPS, host/path routing, WAF, gRPC\n"
          "NLB: L4 TCP/UDP/TLS, static IPs, millions of rps, low latency\n"
          "GWLB: inline firewalls/appliances (GENEVE)\n"
          "Algorithms: round robin (default), least outstanding requests", "blue", size=11, align="left")
    d.box("errs", 490, 370, 450, 130, "Errors the LB itself returns\n502: target sent a bad/closed response (crash, reset)\n"
          "503: no registered targets in the target group\n"
          "504: target too slow (> idle timeout, default 60 s)\n"
          "ALB fails open: if ALL targets are unhealthy, it sends to all", "red", size=11, align="left")
    return d


def git_branching():
    d = Diagram("r1-10-git-branching", 960, 460, "Branching strategies: trunk-based (what I'd pick for CI/CD) vs GitFlow")
    d.box("h1", 20, 50, 440, 36, "Trunk-based development (+ short-lived feature branches)", "green", bold=True, size=12)
    d.box("main1", 20, 165, 440, 36, "main: protected, always deployable (merge = MR + CI + review)", "green", size=11)
    d.box("f1", 40, 95, 180, 32, "feature/login (1-2 days)", "white", size=10)
    d.box("f2", 260, 95, 180, 32, "fix/JIRA-42", "white", size=10)
    d.edge("f1", "main1")
    d.edge("f2", "main1")
    d.box("tag", 20, 215, 440, 85, "Release = tag v1.4.0 on main (build once)\nsame image promoted dev → uat → prod\nunfinished work hidden behind feature flags\nhotfix: branch from main (or the tag), MR, tag again", "white", size=11, align="left")
    d.box("h2", 500, 50, 440, 36, "GitFlow", "orange", bold=True, size=12)
    rows = [("gmain", "main: production releases only (tags)"), ("rel", "release/1.4: stabilise, then merge to main + develop"),
            ("devl", "develop: integration branch"), ("feat", "feature/*: from develop, back to develop"),
            ("hot", "hotfix/*: from main, merged to main + develop")]
    for i, (sid, label) in enumerate(rows):
        d.box(sid, 500, 95 + i * 40, 440, 32, label, "white", size=11)
    d.box("cmp", 20, 310, 920, 130, "How to answer: \"We used trunk-based with short-lived feature branches and merge requests into a protected main.\n"
          "Every MR runs the pipeline; merge needs 1 approval + green CI. Images are tagged with the commit SHA and promoted\n"
          "through environments by GitOps, so we never rebuild per branch. GitFlow suits versioned products with scheduled\n"
          "releases; it slows continuous delivery (long-lived branches, painful merges).\"\n"
          "Protect main: no direct push, required review, required pipeline, squash or merge commits, signed commits optional", "yellow", size=11, align="left")
    return d


# ---------------------------------------------------------------- round 2
def image_security():
    d = Diagram("r2-02-image-security", 960, 480, "Securing container images: build → scan → sign → store → admit → run")
    steps = [("b", "1. Build\nsmall base (distroless,\nalpine, chainguard)\nmulti-stage, no secrets\nnon-root USER,\npin base digest", "blue"),
             ("s", "2. Scan in CI\nTrivy/Grype/ECR scan\nfail on CRITICAL/HIGH\nwith a fix available\n+ SBOM (Syft)", "orange"),
             ("g", "3. Sign\ncosign sign (keyless\nor KMS key)\nattest SBOM +\nprovenance (SLSA)", "purple"),
             ("r", "4. Store\nprivate ECR, immutable\ntags, scan on push,\nlifecycle rules\ndeploy by digest", "yellow"),
             ("a", "5. Admit (cluster)\nKyverno / Gatekeeper:\nonly our registry,\nsigned, no :latest,\nno privileged", "green"),
             ("x", "6. Run\nPodSecurity: restricted\nrunAsNonRoot, read-only\nrootfs, drop ALL caps\n+ Falco at runtime", "red")]
    for i, (sid, label, col) in enumerate(steps):
        d.box(sid, 20 + i * 158, 60, 145, 150, label, col, size=10)
    chain(d, [s[0] for s in steps])
    d.box("cont", 20, 240, 920, 70, "Continuous: rescan images already running (new CVEs appear daily) · Inspector / Trivy Operator reports\n"
          "rebuild on base-image updates (Renovate/Dependabot) · NetworkPolicy + least-privilege RBAC/IRSA limit damage", "white", size=11, align="left")
    d.box("say", 20, 330, 920, 130, "30-second version\n"
          "\"Security starts in the Dockerfile: small base, multi-stage, non-root, no secrets in layers. CI scans every image with\n"
          "Trivy and fails the build on fixable critical CVEs; we push to private ECR with immutable tags and deploy by digest.\n"
          "Images are signed with cosign, and an admission controller like Kyverno only lets signed images from our registry run.\n"
          "At runtime Pod Security Standards (restricted) block root and privileged pods, and we keep rescanning what's running.\"",
          "gray", size=11, align="left")
    return d


def cloudfront():
    d = Diagram("r2-03-cloudfront", 960, 500, "CloudFront: a CDN in front of your origin; edge locations cache and protect")
    d.box("u1", 20, 70, 130, 50, "User (Mumbai)", "white", size=11)
    d.box("u2", 20, 170, 130, 50, "User (London)", "white", size=11)
    d.box("e1", 200, 60, 220, 70, "Edge location (BOM)\ncache HIT → served in ms", "green", size=11)
    d.box("e2", 200, 160, 220, 70, "Edge location (LHR)\ncache MISS → ask origin", "orange", size=11)
    d.box("rec", 470, 110, 190, 70, "Regional edge cache\n(bigger, mid-tier)\nOrigin Shield optional", "yellow", size=10)
    d.group("orig", 710, 50, 230, 230, "Origins (behaviours by path)", "blue", size=11)
    d.box("s3", 725, 85, 200, 50, "/static/* → S3 bucket\n(private, OAC only)", "white", size=10)
    d.box("alb", 725, 150, 200, 50, "/api/* → ALB / EC2\n(no cache or short TTL)", "white", size=10)
    d.box("other", 725, 215, 200, 50, "any HTTP origin\n(on-prem, API GW)", "white", size=10)
    d.edge("u1", "e1")
    d.edge("u2", "e2")
    d.edge("e2", "rec")
    d.edge("rec", "s3")
    d.edge("rec", "alb")
    d.box("roles", 20, 300, 920, 180, "Its roles in an architecture\n"
          "1. Performance: content cached near users (hundreds of edge locations worldwide); lower latency, less load and cost on the origin\n"
          "2. Security: TLS at the edge (ACM cert in us-east-1), AWS WAF + Shield Standard (DDoS), geo-blocking, signed URLs/cookies,\n"
          "    Origin Access Control so the S3 bucket is never public; the origin can accept only CloudFront traffic\n"
          "3. Single entry point: one domain routing /static to S3 and /api to ALB by cache behaviour\n"
          "4. Edge logic: CloudFront Functions (headers, redirects) and Lambda@Edge (heavier logic)\n"
          "Ops: cache key + TTLs (Cache-Control headers), invalidation /* after a deploy (or versioned file names), access logs, 4xx/5xx metrics",
          "gray", size=11, align="left")
    return d


def rds_dr():
    d = Diagram("r2-04-rds-dr", 960, 520, "RDS disaster recovery: pick the option that meets RPO (data loss) and RTO (downtime)")
    d.group("pr", 20, 50, 440, 270, "Primary region (ap-south-1)", "blue")
    d.box("pri", 40, 90, 190, 70, "Primary DB (AZ-a)\nreads + writes", "green", size=11)
    d.box("stb", 250, 90, 190, 70, "Multi-AZ standby (AZ-b)\nsync replication\nauto failover ~1-2 min", "yellow", size=10)
    d.box("snap", 40, 190, 400, 110, "Backups\nautomated: daily snapshot + transaction logs\n→ point-in-time restore (PITR), retention 1-35 days\nmanual snapshots: kept until deleted\nAWS Backup: policies, vault lock, copies", "white", size=10, align="left")
    d.edge("pri", "stb", "sync")
    d.group("dr", 500, 50, 440, 270, "DR region (ap-southeast-1)", "orange")
    d.box("rr", 520, 90, 400, 70, "Cross-region read replica (async, seconds of lag)\npromote it to standalone primary in a disaster", "white", size=11)
    d.box("csnap", 520, 190, 400, 110, "Cross-region snapshot / backup copies\nrestore when needed (slowest, cheapest)\nAurora: Global Database (<1 s lag,\nmanaged failover/switchover)", "white", size=10, align="left")
    d.edge("pri", "rr", "async", points=[(240, 75), (720, 75)])
    d.edge("snap", "csnap", "copy")
    rows = "Option → RPO / RTO / cost\n" \
           "Multi-AZ → 0 / 1-2 min / 2x instance; protects against AZ or instance failure ONLY (same region, not against bad deletes)\n" \
           "PITR in same region → ~5 min / tens of minutes to hours (new instance) / low; protects against bad data, deletes\n" \
           "Cross-region snapshot copy → hours / hours / lowest; region loss on a budget\n" \
           "Cross-region read replica → seconds / minutes (promote + repoint app) / 2x; region loss\n" \
           "Aurora Global Database → ~1 s / ~1 min / highest; critical apps\n" \
           "Always: app connects via a DNS name (Route 53 CNAME) so failover = repoint · test the DR drill · encrypt + copy KMS keys"
    d.box("tbl", 20, 340, 920, 160, rows, "gray", size=11, align="left")
    return d


def s3_denied():
    d = Diagram("r2-05-s3-access-denied", 960, 520, "\"Developer gets AccessDenied on S3\": check these layers in order")
    steps = [("id", "1. Who are they really?\naws sts get-caller-identity\n(wrong profile/role/account?)", "white"),
             ("idp", "2. Identity policy\nuser/role allows s3:GetObject /\nListBucket on the right ARN?\nbucket ARN vs bucket/* ARN", "blue"),
             ("bp", "3. Bucket policy\nexplicit Deny? (aws:SourceVpce,\nSourceIp, SecureTransport,\nPrincipalOrgID conditions)", "purple"),
             ("kms", "4. KMS key (SSE-KMS)\nkey policy + kms:Decrypt /\nGenerateDataKey for the role", "orange"),
             ("bpa", "5. Block Public Access /\nObject Ownership / ACLs\n(object owned by another account?)", "yellow"),
             ("org", "6. SCP / permissions boundary /\nsession policy limiting the role", "red"),
             ("net", "7. Network path\nVPC endpoint policy, endpoint\nroute, proxy, wrong region", "green"),
             ("obj", "8. The request itself\nobject exists? key typo? 403 also\nmeans 'not found' without ListBucket", "gray")]
    for i, (sid, label, col) in enumerate(steps):
        col_ = i % 4 if (i // 4) % 2 == 0 else 3 - i % 4
        d.box(sid, 20 + col_ * 235, 60 + (i // 4) * 140, 215, 115, label, col, size=10)
    chain(d, [s[0] for s in steps])
    d.box("tools", 20, 350, 920, 150, "Tools that tell you which layer\n"
          "CloudTrail: the exact denied API call, principal ARN and errorCode (S3 data events must be enabled for object calls)\n"
          "IAM Policy Simulator: test the principal + action + resource · IAM Access Analyzer for unused/external access\n"
          "Newer AccessDenied messages name the policy type that denied it (\"... with an explicit deny in a resource-based policy\")\n"
          "aws s3api get-bucket-policy / get-bucket-encryption / get-public-access-block · aws s3 ls s3://bucket --debug\n"
          "Fix with least privilege: add the missing action/ARN to the role, never \"s3:*\" or a public bucket",
          "white", size=11, align="left")
    return d


def eks_latency():
    d = Diagram("r2-06-eks-latency", 960, 540, "EKS latency: first find WHERE the time goes, then go one layer deeper")
    d.box("scope", 20, 55, 920, 60, "0. Scope it: all services or one? all users or one region/AZ? since when (deploy, traffic spike, scaling event)?\n"
          "Look at p50 vs p99 latency, error rate, traffic (Grafana / CloudWatch Container Insights / traces)", "white", size=11, align="left")
    layers = [("edge", "1. Edge / LB\nALB TargetResponseTime\nvs client time\nCloudFront, DNS", "purple"),
              ("ing", "2. Ingress\ningress-nginx p99,\nrequest_time vs\nupstream_response_time", "blue"),
              ("svc", "3. Service network\nCoreDNS latency/errors,\nndots:5 lookups,\nkube-proxy/conntrack,\ncross-AZ hops", "orange"),
              ("pod", "4. Pod\nCPU throttling (limit)\nmemory/GC, OOMKills,\nreadiness flapping,\nthread/conn pools", "green"),
              ("node", "5. Node\nCPU/mem pressure,\nnoisy neighbours,\ndisk IO, ENI/IP limits,\nnetwork bandwidth", "yellow"),
              ("dep", "6. Dependencies\nRDS slow queries,\nconnections maxed,\nRedis, 3rd-party APIs,\nNAT gateway limits", "red")]
    for i, (sid, label, col) in enumerate(layers):
        d.box(sid, 20 + i * 155, 140, 145, 130, label, col, size=10)
    chain(d, [s[0] for s in layers])
    d.box("cmd", 20, 290, 920, 230, "Commands / signals\n"
          "kubectl top pods/nodes · kubectl describe pod (restarts, events) · kubectl get hpa (maxed out?)\n"
          "PromQL: rate(container_cpu_cfs_throttled_periods_total[5m]) / rate(container_cpu_cfs_periods_total[5m])  → throttling ratio\n"
          "histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))  → p99\n"
          "CoreDNS: coredns_dns_request_duration_seconds, SERVFAIL rate; test: kubectl exec ... -- time nslookup svc\n"
          "Traces (X-Ray / Jaeger / Tempo) show which hop is slow · RDS Performance Insights for the DB\n"
          "Common fixes: raise/remove CPU limits that throttle, scale out (HPA, more nodes), NodeLocal DNSCache or ndots:2 / FQDN,\n"
          "topology-aware routing to stay in-AZ, connection pooling (PgBouncer/RDS Proxy), fix the slow query, bigger instance types",
          "gray", size=11, align="left")
    return d


def lambda_debug():
    d = Diagram("r2-07-lambda-debug", 960, 500, "Lambda failing: read the error, then match it to a cause")
    d.box("start", 20, 55, 280, 90, "1. Find the error\nCloudWatch Logs /aws/lambda/<fn>\nMetrics: Errors, Throttles,\nDuration, ConcurrentExecutions", "blue", size=11)
    d.box("inv", 330, 55, 280, 90, "2. How was it invoked?\nsync (API GW): error to caller\nasync (S3/SNS/EventBridge): retries 2x\nstream/SQS: retries until success", "purple", size=10)
    d.box("rep", 640, 55, 300, 90, "3. Reproduce\naws lambda invoke --payload ...\ntest event in console\nX-Ray trace for downstream calls", "green", size=10)
    chain(d, ["start", "inv", "rep"])
    rows = [("Task timed out after N seconds", "Timeout too low or a call hangs: VPC Lambda without NAT/endpoint, slow DB"),
            ("Runtime exited / signal: killed, Max Memory Used = Memory Size", "Out of memory: raise memory (also gives more CPU)"),
            ("AccessDeniedException / not authorized", "Execution role missing a permission (or KMS key policy)"),
            ("Rate exceeded / TooManyRequestsException", "Throttled: account/reserved concurrency limit"),
            ("ImportModuleError / handler not found", "Bad package, wrong handler name, missing layer or dependency, wrong architecture"),
            ("Errors right after a deploy", "Code bug or missing env variable: roll back to the previous version/alias"),
            ("ENI / subnet errors, can't reach RDS", "Security group, subnet IPs exhausted, RDS SG not allowing the Lambda SG")]
    d.box("th", 20, 170, 920, 30, "Error message → likely cause", "gray", bold=True, size=12)
    for i, (err, cause) in enumerate(rows):
        d.box(f"e{i}", 20, 205 + i * 40, 380, 36, err, "red", size=10)
        d.box(f"c{i}", 410, 205 + i * 40, 530, 36, cause, "white", size=10, align="left")
    return d


def ci_gitlab():
    d = Diagram("r2-08-ci-gitlab-connect", 960, 520, "\"Pipeline can't connect to GitLab\": runner → network → auth, in that order")
    d.box("q", 20, 55, 920, 50, "First read the exact error: no jobs picked up? \"Could not resolve host\"? \"Connection timed out\"? \"SSL certificate problem\"?\n"
          "\"HTTP Basic: Access denied\" / 403? Each one points to a different layer.", "white", size=11, align="left")
    steps = [("run", "1. Runner itself\ngitlab-runner status / verify\nrunner online in Settings > CI/CD?\ntags match the job? token valid?", "blue"),
             ("dns", "2. DNS\nnslookup gitlab.example.com\nfrom the runner (and inside\nthe job container)", "purple"),
             ("net", "3. Network\ncurl -v https://gitlab... :443\nSG / NACL / firewall, NAT route\nproxy env vars, IP allowlist", "orange"),
             ("tls", "4. TLS\nself-signed / internal CA?\ntls-ca-file in config.toml,\nclock skew, expired cert", "yellow"),
             ("auth", "5. Auth\nCI_JOB_TOKEN scope (allowlist),\ndeploy key / token expired,\nproject access, SSH vs HTTPS", "green"),
             ("gl", "6. GitLab side\nstatus page / instance down?\nrate limits, maintenance,\nURL changed, runner paused", "red")]
    for i, (sid, label, col) in enumerate(steps):
        col_ = i % 3 if (i // 3) % 2 == 0 else 2 - i % 3
        d.box(sid, 20 + col_ * 315, 130 + (i // 3) * 130, 290, 110, label, col, size=10)
    chain(d, [s[0] for s in steps])
    d.box("cmds", 20, 400, 920, 100, "Useful commands\n"
          "gitlab-runner verify · journalctl -u gitlab-runner · gitlab-runner --debug run\n"
          "curl -v https://gitlab.example.com/api/v4/version · git ls-remote https://gitlab-ci-token:${CI_JOB_TOKEN}@gitlab.example.com/grp/repo.git\n"
          "openssl s_client -connect gitlab.example.com:443 -showcerts · ssh -T git@gitlab.example.com", "gray", size=11, align="left")
    return d


def expose_pod():
    d = Diagram("r2-09-expose-pod", 960, 520, "\"Can't expose the pod\": follow the chain from outside in; it breaks at one link")
    chainl = [("lb", "Load balancer / DNS\nkubectl get svc: EXTERNAL-IP\n<pending>? LB controller\nlogs, subnet tags, quota", "purple"),
              ("ing", "Ingress\ningressClassName set?\ncontroller running?\nhost/path, backend svc+port", "blue"),
              ("svc", "Service\nselector = pod labels?\nport → targetPort right?\ntype NodePort/LB if outside", "orange"),
              ("ep", "Endpoints\nkubectl get endpointslices\nEMPTY = selector wrong\nor pods not Ready", "yellow"),
              ("pod", "Pod\nRunning AND Ready?\nreadiness probe passing?\napp listens on 0.0.0.0:port", "green")]
    for i, (sid, label, col) in enumerate(chainl):
        d.box(sid, 20 + i * 188, 60, 175, 120, label, col, size=10)
    chain(d, [s[0] for s in chainl])
    d.box("np", 20, 200, 920, 50, "Also: NetworkPolicy denying ingress · security group on nodes/pods (NodePort 30000-32767) · kube-proxy / CNI unhealthy", "red", size=11, align="left")
    d.box("cmd", 20, 270, 920, 230, "Commands, in order\n"
          "kubectl get pod -l app=web -o wide --show-labels      # Running? READY 1/1? labels?\n"
          "kubectl get svc web -o yaml | grep -A3 selector        # does selector match those labels?\n"
          "kubectl get endpointslices -l kubernetes.io/service-name=web   # pod IPs listed?\n"
          "kubectl port-forward pod/web-xxx 8080:8080 ; curl localhost:8080   # app OK directly?\n"
          "kubectl run t --rm -it --image=busybox -- wget -qO- http://web:80   # Service OK inside the cluster?\n"
          "kubectl describe ingress web ; kubectl logs -n ingress-nginx deploy/ingress-nginx-controller\n"
          "kubectl describe svc web   # events: e.g. 'Failed to build model' / subnet tags for an LB\n"
          "Classic causes: label typo, targetPort ≠ containerPort, app bound to 127.0.0.1, readiness failing, ClusterIP used from outside",
          "gray", size=11, align="left")
    return d


def tf_partial_apply():
    d = Diagram("r2-11-tf-partial-apply", 960, 460, "Terraform apply failed midway: stabilise state, read the plan, then fix forward")
    steps = [("stop", "1. Stop\nno re-runs, no console\nfixes; read the error;\nusers impacted?", "red"),
             ("lock", "2. Lock\nheld after a killed job?\ncheck nothing runs, then\nforce-unlock LOCK_ID", "orange"),
             ("save", "3. State saved?\nerrored.tfstate exists?\nterraform state push it\nbackup: state pull > f", "yellow"),
             ("plan", "4. terraform plan\ndone = no change\ntainted = will replace\nin AWS, not in state\n→ terraform import", "blue"),
             ("fix", "5. Fix the cause\nIAM permission, quota,\nname clash, timeout,\ndependency order", "purple"),
             ("apply", "6. Fix forward\nMR → plan → apply;\nonly the rest is done\n(or git revert + apply)", "green")]
    for i, (sid, label, col) in enumerate(steps):
        d.box(sid, 20 + i * 157, 60, 145, 140, label, col, size=10)
    chain(d, [s[0] for s in steps])
    d.box("why", 20, 225, 920, 215, "Key facts\n"
          "Terraform is NOT transactional: no automatic rollback. Whatever succeeded stays, and is recorded in state as each resource completes.\n"
          "Never: restore an older state file to 'roll back', delete resources by hand, or edit the JSON. Use state rm / mv / import, untaint.\n"
          "Resources that failed during creation are marked tainted and replaced next apply (terraform untaint if verified healthy).\n"
          "Orphan = created in AWS but the run died before writing state → 'AlreadyExists' next time → import it (import block, 1.5+).\n"
          "Prevent: S3 backend with versioning + locking, CI keeps errored.tfstate as an artifact, one runner per state (resource_group),\n"
          "small states and small changes, staging first, check quotas and permissions with the same role that applies.",
          "gray", size=11, align="left")
    return d


def secrets_envs():
    d = Diagram("r2-12-secrets-envs", 960, 520, "Secrets across environments: one store per env account, synced into the cluster, never in Git")
    envs = [("dev", "dev account", "green"), ("uat", "uat account", "yellow"), ("prod", "prod account", "red")]
    for i, (sid, label, col) in enumerate(envs):
        x = 20 + i * 315
        d.group(f"g{sid}", x, 50, 295, 250, label, col, size=12)
        d.box(f"sm{sid}", x + 15, 85, 265, 60, f"Secrets Manager / SSM\n/{sid}/payments/db-password\nencrypted with {sid} KMS key", "white", size=10)
        d.box(f"eso{sid}", x + 15, 160, 265, 50, "External Secrets Operator\n(IRSA role: read /" + sid + "/* only)", "white", size=10)
        d.box(f"k{sid}", x + 15, 225, 265, 60, "K8s Secret → pod env / volume\n(etcd encrypted with KMS,\nRBAC: no get secrets for devs)", "white", size=10)
        d.edge(f"sm{sid}", f"eso{sid}")
        d.edge(f"eso{sid}", f"k{sid}")
    d.box("git", 20, 320, 450, 180, "In Git (safe)\nExternalSecret manifests: names/paths only, no values\nper-env values file picks /dev/ vs /prod/ path\nor SOPS/Sealed Secrets: encrypted values\nCI secrets: GitLab CI variables (masked, protected,\nenvironment-scoped) or OIDC → AWS role, no static keys", "blue", size=11, align="left")
    d.box("rules", 490, 320, 450, 180, "Rules\nseparate account + KMS key per env: dev can't read prod\nleast privilege per app (path-scoped IAM)\nrotation (Secrets Manager rotation Lambda / RDS-managed)\naudit: CloudTrail on GetSecretValue\nscan for leaks: gitleaks / pre-commit, GitLab secret detection\nnever: plain env in Dockerfile, values in Helm values, logs", "orange", size=11, align="left")
    return d


ALL = [project_pipeline, pod_service_deployment, deployment_strategies, terraform_state, iam_role_policy,
       load_balancer, git_branching, image_security, cloudfront, rds_dr, s3_denied, eks_latency, lambda_debug,
       ci_gitlab, expose_pod, tf_partial_apply, secrets_envs]

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
