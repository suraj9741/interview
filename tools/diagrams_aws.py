#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/aws/*.md.

Run once:  python3 tools/diagrams_aws.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "aws" / "diagrams"


def iam_big_picture():
    d = Diagram("iam-01-big-picture", 960, 600, "IAM in one picture: WHO (identities) gets WHAT (policies)")
    d.group("acct", 20, 44, 920, 540, "One AWS account · IAM is GLOBAL (no region to pick)", "gray", align="left")
    d.box("root", 40, 84, 270, 92,
          "Root user\nemail + password used to create the account\nall power, cannot be limited by IAM\n"
          "MFA on, NO access keys, lock it away", "red", size=11)
    d.box("why", 330, 84, 590, 92,
          "IAM = Identity and Access Management\nAuthentication: who are you? (password + MFA, or access keys)\n"
          "Authorization: what may you do? (policies; everything is DENIED by default)\n"
          "Free service · least privilege: give only the permissions a job needs", "white", size=11, align="left")
    d.text("h-id", 40, 192, 520, 24, "IDENTITIES (principals)", size=13, bold=True)
    d.group("g-dev", 40, 220, 250, 150, "Group: Developers", "green", dashed=True, size=12)
    d.box("u-alice", 60, 252, 100, 40, "User: alice", "white", size=11)
    d.box("u-bob", 172, 252, 100, 40, "User: bob", "white", size=11)
    d.text("g-note", 50, 300, 230, 64, "users only, no nested groups\na user can be in many groups\n(max 10)", size=10)
    d.group("g-ops", 310, 220, 250, 150, "Group: Operations", "green", dashed=True, size=12)
    d.box("u-bob2", 330, 252, 100, 40, "User: bob", "white", size=11)
    d.box("u-carl", 442, 252, 100, 40, "User: carl", "white", size=11)
    d.text("g-note2", 320, 300, 230, 64, "bob is in BOTH groups:\nhe gets the union of both\ngroups' permissions", size=10)
    d.box("u-dave", 40, 392, 250, 56, "User: dave (in no group)\nallowed, but not best practice", "white", size=11)
    d.box("role", 310, 392, 250, 56, "Role: ec2-s3-read\nassumed by EC2 / Lambda / another account", "purple", size=11)
    d.text("h-pol", 600, 192, 320, 24, "POLICIES (JSON permission documents)", size=13, bold=True)
    d.box("p-aws", 600, 222, 320, 52, "AWS managed policy\ne.g. AdministratorAccess, ReadOnlyAccess", "blue", size=11)
    d.box("p-cust", 600, 286, 320, 52, "Customer managed policy\nyou write it, reuse it on many identities", "blue", size=11)
    d.box("p-inline", 600, 350, 320, 52, "Inline policy\nembedded in ONE user/group/role, deleted with it", "yellow", size=11)
    d.box("p-res", 600, 414, 320, 52, "Resource-based policy (has \"Principal\")\non the resource: S3 bucket policy, role trust policy", "orange", size=11)
    d.edge("p-aws", "g-dev", "attach", points=[(580, 248), (580, 184), (165, 184)])
    d.edge("p-cust", "role", "attach", points=[(580, 312), (580, 420)])
    d.box("rule", 40, 474, 880, 94,
          "How permissions add up\nEffective permissions = user's own policies + every group's policies (union).\n"
          "No policy that allows it = implicit DENY.   Any policy that says \"Effect\": \"Deny\" = explicit DENY, and it ALWAYS wins.\n"
          "Best practice: attach policies to GROUPS (not users), give each person their own user, use ROLES for AWS services.",
          "yellow", size=11, align="left")
    return d


def policy_anatomy():
    d = Diagram("iam-02-policy-anatomy", 960, 640, "Anatomy of an IAM policy (JSON)")
    json_lines = [
        "{",
        "  \"Version\": \"2012-10-17\",",
        "  \"Id\": \"S3ReadOnlyPolicy\",",
        "  \"Statement\": [",
        "    {",
        "      \"Sid\": \"ReadReports\",",
        "      \"Effect\": \"Allow\",",
        "      \"Action\": [",
        "        \"s3:GetObject\",",
        "        \"s3:ListBucket\"",
        "      ],",
        "      \"Resource\": [",
        "        \"arn:aws:s3:::reports\",",
        "        \"arn:aws:s3:::reports/*\"",
        "      ],",
        "      \"Condition\": {",
        "        \"IpAddress\": {",
        "          \"aws:SourceIp\": \"203.0.113.0/24\"",
        "        }",
        "      }",
        "    }",
        "  ]",
        "}",
    ]
    # non-breaking spaces keep the indentation (SVG collapses normal spaces)
    body = "\n".join(line.replace("  ", "\u00a0\u00a0") for line in json_lines)
    d.box("json", 20, 50, 360, 520, body, "white", size=12, align="left", bold_first=False)
    rows = [
        ("Version", "policy language version · always \"2012-10-17\"\n(a fixed string, NOT today's date)", "gray"),
        ("Id (optional)", "a name for the whole policy", "gray"),
        ("Statement", "list of one or more statements (required)", "blue"),
        ("Sid (optional)", "a label for one statement", "gray"),
        ("Effect", "Allow or Deny", "green"),
        ("Principal", "WHO · only in resource-based policies (bucket\npolicy, trust policy); never in a policy attached\nto a user, group or role", "orange"),
        ("Action", "WHAT API calls: service:Operation\nwildcards are fine (s3:Get*, s3:*)", "blue"),
        ("Resource", "ON WHAT: ARNs · bucket ARN (reports) is not\nthe object ARN (reports/*)", "blue"),
        ("Condition", "WHEN (optional): source IP, region, MFA present,\ntags, time …", "purple"),
    ]
    y = 50
    for i, (k, v, c) in enumerate(rows):
        n = v.count("\n") + 1
        h = {1: 44, 2: 56, 3: 70}[n]
        d.box(f"k{i}", 400, y, 140, h, k, c, size=12, bold=True)
        d.box(f"v{i}", 546, y, 394, h, v, "white", size=11, align="left", bold_first=False)
        y += h + 6
    d.text("tip", 20, 586, 920, 40, "Memory hook: E-P-A-R-C = Effect, Principal, Action, Resource, Condition", size=14, bold=True)
    return d


def policy_evaluation():
    d = Diagram("iam-03-policy-evaluation", 960, 560, "Allowed or denied? How AWS decides every API call (one account)")
    d.box("req", 360, 46, 240, 50, "Request arrives\nprincipal + action + resource", "gray", size=11)
    d.box("start", 360, 120, 240, 44, "Start: DENY by default", "red", size=12, bold=True)
    d.box("q1", 340, 192, 280, 60, "Is there an explicit \"Deny\" in\nANY applicable policy?", "yellow", size=11)
    d.box("d1", 700, 192, 230, 60, "DENIED (explicit deny)\nnothing can override it", "red", size=11)
    d.box("q2", 340, 290, 280, 60, "Is there an \"Allow\" in an identity\nOR resource-based policy?", "yellow", size=11)
    d.box("d2", 30, 290, 230, 60, "DENIED (implicit deny)\nnobody said Allow", "red", size=11)
    d.box("q3", 340, 388, 280, 60, "SCP, permissions boundary, session\npolicy also allow it? (if any exist)", "yellow", size=11)
    d.box("d3", 700, 388, 230, 60, "DENIED\nthese only LIMIT, never grant", "red", size=11)
    d.box("ok", 380, 478, 200, 50, "ALLOWED", "green", size=14, bold=True)
    d.edge("req", "start")
    d.edge("start", "q1")
    d.edge("q1", "d1", "yes")
    d.edge("q1", "q2", "no")
    d.edge("q2", "d2", "no")
    d.edge("q2", "q3", "yes")
    d.edge("q3", "d3", "no")
    d.edge("q3", "ok", "yes")
    d.box("n1", 30, 388, 290, 140,
          "Exam one-liners\nExplicit DENY > explicit ALLOW > implicit deny.\n"
          "Root user ignores IAM policies\n(but not SCPs in an Organization).\n"
          "Cross-account: BOTH sides must allow\n(identity policy in your account AND\nresource policy in theirs).",
          "white", size=10, align="left")
    d.box("n2", 30, 60, 290, 110,
          "Example\nGroup Developers: Allow s3:*\nalice's inline policy: Deny s3:DeleteBucket\n"
          "→ alice can do everything in S3\n   EXCEPT delete buckets.", "white", size=10, align="left")
    return d


def access_methods():
    d = Diagram("iam-04-access-methods", 960, 520, "Three ways to talk to AWS, and which credentials each one uses")
    d.box("you", 20, 200, 150, 70, "You\n(IAM user)", "gray", shape="ellipse", size=12)
    d.box("console", 230, 60, 300, 100,
          "1. AWS Management Console\nbrowser · sign in with\naccount ID/alias + username + password\n+ MFA code", "blue", size=11)
    d.box("cli", 230, 186, 300, 100,
          "2. AWS CLI (terminal) / SDK (code)\nAccess key ID (AKIA…) + Secret access key\nset with: aws configure\nstored in ~/.aws/credentials", "green", size=11)
    d.box("shell", 230, 312, 300, 100,
          "3. AWS CloudShell\nterminal INSIDE the console (>_ icon)\nuses your console login, NO keys needed\nCLI v2 pre-installed, 1 GB $HOME per region", "purple", size=11)
    d.box("api", 620, 186, 140, 100, "AWS APIs\n(HTTPS)\nevery click and\nevery command\nis an API call", "orange", size=11)
    d.box("iam", 800, 186, 140, 100, "IAM checks\nwho? (authN)\nallowed? (authZ)", "red", size=11)
    d.edge("you", "console")
    d.edge("you", "cli")
    d.edge("you", "shell")
    d.edge("console", "api")
    d.edge("cli", "api")
    d.edge("shell", "api")
    d.edge("api", "iam")
    d.box("n", 20, 432, 920, 72,
          "Access keys = a password for the CLI. The secret is shown ONCE at creation; max 2 keys per user (so you can rotate).\n"
          "Never share them, never commit them to Git, never put them on EC2 (use a role). If leaked: deactivate → create new → delete old.\n"
          "CloudShell and EC2 roles give TEMPORARY credentials instead (key IDs start with ASIA, plus a session token).",
          "yellow", size=11, align="left", bold_first=False)
    return d


def role_assume():
    d = Diagram("iam-05-role-assume", 960, 620, "IAM role: temporary permissions for an AWS service (EC2 → S3 example)")
    d.box("ec2", 20, 90, 200, 90, "EC2 instance\napp runs: aws s3 ls\n(no keys on disk!)", "orange", size=11)
    d.box("prof", 20, 220, 200, 70, "Instance profile\ncontainer that attaches\nthe role to EC2", "gray", size=11)
    d.box("imds", 20, 330, 200, 80, "Instance metadata (IMDS)\n169.254.169.254\nSDK/CLI read creds here", "gray", size=10)
    d.group("rolebox", 290, 60, 360, 350, "Role: ec2-s3-read", "purple")
    d.box("trust", 310, 96, 320, 130,
          "Trust policy (WHO may assume)\n\"Effect\": \"Allow\",\n\"Principal\": {\"Service\": \"ec2.amazonaws.com\"},\n"
          "\"Action\": \"sts:AssumeRole\"\n\nresource-based policy on the role", "white", size=10, align="left")
    d.box("perm", 310, 244, 320, 150,
          "Permissions policy (WHAT it may do)\n\"Effect\": \"Allow\",\n\"Action\": [\"s3:GetObject\", \"s3:ListBucket\"],\n"
          "\"Resource\": \"arn:aws:s3:::reports*\"\n\ne.g. AmazonS3ReadOnlyAccess\n(identity-based, managed or inline)", "white", size=10, align="left")
    d.box("sts", 720, 90, 220, 110, "AWS STS\n(Security Token Service)\nsts:AssumeRole returns\ntemporary credentials", "blue", size=11)
    d.box("creds", 720, 230, 220, 120, "Temporary credentials\nAccessKeyId (ASIA…)\nSecretAccessKey\nSessionToken\nexpire (15 min – 12 h;\nEC2 rotates them for you)", "green", size=10)
    d.box("s3", 720, 380, 220, 60, "S3 bucket: reports\nrequest allowed", "orange", size=11)
    d.edge("ec2", "prof", "has")
    d.edge("prof", "rolebox", "points to")
    d.edge("rolebox", "sts", "AssumeRole")
    d.edge("sts", "creds")
    d.edge("creds", "imds", "delivered to the instance", points=[(690, 330), (690, 436), (120, 436)])
    d.edge("imds", "ec2", points=[(8, 370), (8, 135)])
    d.edge("creds", "s3", "sign request")
    d.box("n", 20, 470, 920, 130,
          "User vs role\nUser = one person, long-term credentials (password / access keys).   Role = no long-term credentials, anyone TRUSTED can wear it for a while.\n"
          "Common roles: EC2 instance role · Lambda execution role · ECS task role · cross-account access · federation / SSO (IAM Identity Center).\n"
          "To attach a role to EC2 you need iam:PassRole.  A role has TWO policies: trust (who) + permissions (what).\n"
          "Trap: a role does NOT need access keys, and you never store keys on an instance; you can swap the role on a running instance.",
          "yellow", size=11, align="left")
    return d


def mfa_password():
    d = Diagram("iam-06-mfa-password", 960, 470, "Protecting sign-in: password policy + MFA")
    d.box("pw", 20, 50, 440, 260,
          "Password policy (account settings, for IAM users)\n"
          "• minimum length (default 8, can set 6–128)\n"
          "• require uppercase / lowercase / numbers /\n   non-alphanumeric characters (! @ # …)\n"
          "• allow users to change their own password\n"
          "• password expiry (e.g. every 90 days)\n"
          "• prevent password re-use (remember last 1–24)\n"
          "• require admin reset after expiry\n"
          "Does NOT apply to the root user or to access keys", "blue", size=11, align="left")
    d.box("eq", 480, 50, 460, 70, "MFA = something you KNOW (password)\n+ something you HAVE (a device)", "green", size=13)
    d.box("m1", 480, 136, 148, 120, "Virtual MFA\nphone app:\nGoogle Authenticator,\nAuthy, Microsoft\nAuthenticator", "white", size=10)
    d.box("m2", 636, 136, 148, 120, "FIDO2 security key\n/ passkey\nYubiKey, Touch ID,\nWindows Hello\n(phishing-resistant)", "white", size=10)
    d.box("m3", 792, 136, 148, 120, "Hardware TOTP\ntoken\nkey-fob that shows\na 6-digit code\n(third-party, e.g. Thales)", "white", size=10)
    d.box("why", 480, 270, 460, 40, "Password stolen? Attacker still needs your device.", "yellow", size=11)
    d.box("n", 20, 330, 920, 120,
          "Remember for the exam\nTurn on MFA for the ROOT user first, then for every IAM user. Up to 8 MFA devices per user (any mix).\n"
          "MFA protects console sign-in. For the CLI, use sts get-session-token with --serial-number and --token-code, and require it in policies\n"
          "with the condition \"aws:MultiFactorAuthPresent\": \"true\".  S3 MFA Delete can be enabled only by the root user.\n"
          "Lost MFA device: an admin removes (deactivates) it from the user, then the user registers a new one.",
          "yellow", size=11, align="left")
    return d


def security_tools():
    d = Diagram("iam-07-security-tools", 960, 470, "IAM security tools: credential report vs access advisor")
    d.box("cr", 20, 50, 450, 270,
          "IAM Credential Report  (ACCOUNT level)\n"
          "One CSV listing EVERY user in the account and the\nstatus of their credentials:\n"
          "• password enabled? last used? last changed?\n"
          "• MFA active?\n"
          "• access key 1 / 2 active? last rotated? last used?\n"
          "Use it to find: users without MFA, old keys (>90 days),\nunused passwords / keys → audits, compliance\n"
          "Console: IAM → Credential report → Download\n"
          "New report at most every 4 hours", "blue", size=11, align="left")
    d.box("aa", 490, 50, 450, 270,
          "IAM Access Advisor  (USER level)\n"
          "Tab on a user, group, role or policy:\n"
          "• which SERVICES its policies allow\n"
          "• when each service was LAST ACCESSED\n"
          "Use it to find permissions that are never used,\nthen remove them → least privilege\n"
          "Console: IAM → Users → <user> → Last accessed\n"
          "(this tab is what the course calls Access Advisor)\n"
          "History shown for up to 400 days", "green", size=11, align="left")
    d.box("hook", 20, 336, 920, 50,
          "Hook: Credential report = Census of the whole Country (account).   Access Advisor = Audit of one person (user).",
          "yellow", size=12, bold=True)
    d.box("aan", 20, 400, 920, 52,
          "Don't confuse with IAM Access ANALYZER: finds resources shared OUTSIDE your account (public S3 bucket, cross-account role),\n"
          "unused access, and can validate or generate policies from CloudTrail activity.",
          "orange", size=11, align="left", bold_first=False)
    return d


def shared_responsibility():
    d = Diagram("iam-08-shared-responsibility", 960, 400, "Shared responsibility model, applied to IAM")
    d.box("aws", 20, 50, 450, 230,
          "AWS is responsible for (security OF the cloud)\n"
          "• the infrastructure: global network security\n"
          "• the IAM service itself running and secure\n"
          "• configuration and vulnerability analysis\n   of its own systems\n"
          "• compliance validation (audits, certifications)",
          "orange", size=12, align="left")
    d.box("you", 490, 50, 450, 230,
          "YOU are responsible for (security IN the cloud)\n"
          "• users, groups, roles, policies: create, manage, monitor\n"
          "• enable and enforce MFA on all accounts\n"
          "• rotate access keys often\n"
          "• use IAM tools to apply the right permissions\n"
          "• analyse access patterns and review permissions\n   (credential report, access advisor, CloudTrail)",
          "blue", size=12, align="left")
    d.box("n", 20, 296, 920, 84,
          "If your access key leaks on GitHub, or a user has AdministratorAccess they don't need, that is YOUR fault, not AWS's.\n"
          "Exam phrase: \"who is responsible for managing IAM users and MFA?\" → the customer.",
          "yellow", size=12, align="left", bold_first=False)
    return d


# ---------------------------------------------------------------- 02 global infrastructure
def global_infra():
    d = Diagram("infra-01-regions-azs-edge", 960, 560, "AWS global infrastructure: region → AZs → data centers, plus edge locations")
    d.group("reg", 20, 44, 600, 330, "Region: ap-south-1 (Mumbai) · a cluster of data centers in one geographic area", "blue", align="left", size=12, icon="region")
    for i, (az, x) in enumerate([("ap-south-1a", 40), ("ap-south-1b", 236), ("ap-south-1c", 432)]):
        d.group(f"az{i}", x, 80, 172, 200, f"AZ {az}", "green", dashed=True, size=12)
        d.box(f"dc{i}a", x + 16, 112, 140, 40, "data center", "white", size=11, icon="server", icon_size=24)
        d.box(f"dc{i}b", x + 16, 162, 140, 40, "data center", "white", size=11, icon="server", icon_size=24)
        d.text(f"azn{i}", x + 6, 210, 160, 64, "own power, network\nand cooling; separate\nfrom the other AZs", size=10)
    d.edge("az0", "az1", both=True)
    d.edge("az1", "az2", both=True)
    d.box("azrule", 40, 294, 560, 66,
          "AZ facts: usually 3 per region (min 3, max 6) · each AZ = one or more discrete data centers\n"
          "far enough apart to survive a disaster, close enough for fast links · HA = run in ≥ 2 AZs",
          "yellow", size=11, align="left", bold_first=False)
    d.group("edge", 640, 44, 300, 330, "Edge locations / points of presence", "orange", align="left", size=12, icon="edge-location")
    d.box("e1", 660, 84, 260, 110,
          "400+ points of presence\n(edge locations + regional caches)\nin 90+ cities, 40+ countries\n"
          "content reaches users with\nlower latency", "white", size=11)
    d.box("e2", 660, 210, 260, 150,
          "Used by\n• CloudFront (CDN cache)\n• Route 53 (DNS)\n• Global Accelerator\n• S3 Transfer Acceleration\n"
          "• WAF / Shield at the edge", "white", size=11, align="left")
    d.box("choose", 20, 390, 450, 154,
          "How to choose a region (4 factors)\n1. Compliance: data governance and legal rules\n    (data may have to stay in a country)\n"
          "2. Proximity to customers: lower latency\n3. Available services: not every service or\n    feature is in every region\n"
          "4. Pricing: varies region to region", "purple", size=11, align="left")
    d.box("scope", 490, 390, 450, 154,
          "Global vs regional services\nGLOBAL: IAM · Route 53 · CloudFront · WAF\n"
          "REGIONAL (most services): EC2, VPC, EBS, RDS,\n    Lambda, Elastic Beanstalk, Rekognition …\n"
          "The console's region menu says \"Global\" for global ones.\n"
          "Region names: code (ap-south-1) + name (Mumbai)", "gray", size=11, align="left")
    return d


# ---------------------------------------------------------------- 03 EC2 fundamentals
def ec2_instance_types():
    d = Diagram("ec2-01-instance-types", 960, 520, "EC2 instance types: read the name, pick the family")
    d.box("name", 20, 50, 920, 100,
          "How to read  m5.2xlarge\nm = instance class (family)  ·  5 = generation (higher is newer)  ·  2xlarge = size inside the class\n"
          "Size: nano < micro < small < medium < large < xlarge < 2xlarge … (more vCPU, RAM, network)\n"
          "Suffixes you will see: g = AWS Graviton (ARM), a = AMD, i = Intel, d = local NVMe instance store, n = more network",
          "white", size=12, align="left", icon="ec2", icon_size=48)
    fams = [
        ("General purpose\nT, M, Mac", "balance of compute,\nmemory, network\n\nweb servers,\ncode repositories\nt2/t3.micro =\nfree tier", "blue"),
        ("Compute optimized\nC", "many fast CPUs\n\nbatch processing,\nmedia transcoding,\nHPC, ML inference,\ngaming servers,\nscientific modelling", "green"),
        ("Memory optimized\nR, X, z", "lots of RAM\n\nin-memory DBs\n(Redis), relational\nDBs, real-time big\ndata, BI", "orange"),
        ("Storage optimized\nI, D, H", "fast local storage,\nhigh IOPS\n\nOLTP DBs, NoSQL,\nRedis cache, data\nwarehousing,\ndistributed FS", "purple"),
        ("Accelerated\nP, G, Inf, Trn", "GPUs / ML chips\n\nML training and\ninference, graphics,\nvideo rendering", "yellow"),
    ]
    for i, (head, body, col) in enumerate(fams):
        x = 20 + i * 186
        d.box(f"fh{i}", x, 170, 174, 56, head, col, size=12)
        d.box(f"fb{i}", x, 232, 174, 190, body, "white", size=11, bold_first=False)
    d.box("hint", 20, 438, 920, 66,
          "Exam hook: \"R\" = RAM (memory), \"C\" = compute, \"I\" = I/O (storage), \"G\"/\"P\" = graphics/GPU, \"T\" = turbo/burstable.\n"
          "There is also an HPC Optimized family (Hpc). Compare all types on instances.vantage.sh (community site, not AWS).",
          "yellow", size=11, align="left", bold_first=False)
    return d


def ec2_security_groups():
    d = Diagram("ec2-02-security-groups", 960, 600, "Security groups: a stateful firewall around each instance (allow rules only)")
    d.box("you", 20, 100, 150, 60, "Your laptop\n203.0.113.10", "white", size=11, icon="client")
    d.box("web", 20, 230, 150, 60, "Internet users\n0.0.0.0/0", "white", size=11, icon="users")
    d.group("sg", 260, 50, 340, 300, "Security group  sg-web (attached to the instance)", "red", align="left", size=12)
    d.box("in", 280, 84, 300, 110,
          "Inbound rules\nSSH   TCP 22    203.0.113.10/32\nHTTP  TCP 80    0.0.0.0/0\nHTTPS TCP 443   0.0.0.0/0\n"
          "default: ALL inbound blocked", "green", size=11, align="left")
    d.box("ec2", 330, 210, 200, 54, "EC2 instance", "orange", size=12, icon="ec2-instance")
    d.box("out", 280, 276, 300, 60, "Outbound rules\ndefault: ALL outbound allowed", "blue", size=11, align="left")
    d.edge("you", "in", "ssh :22")
    d.edge("web", "in", "http/https", points=[(220, 260), (220, 160)])
    d.box("app", 700, 84, 240, 110, "EC2 in sg-app\ninbound: TCP 8080\nsource = sg-web\n(a security group, not an IP)", "orange", size=11, icon="ec2-instance")
    d.edge("ec2", "app", "allowed because the\nsource is sg-web", points=[(610, 237), (610, 139)])
    d.box("facts", 620, 210, 320, 140,
          "Facts\n• only ALLOW rules (no deny)\n• stateful: reply traffic is allowed back\n• rules reference IP/CIDR or another SG\n"
          "• locked to one region + VPC\n• many instances ↔ many SGs", "white", size=11, align="left")
    d.box("dbg", 20, 370, 440, 110,
          "Debugging rule\nTimeout (hangs) → security group / NACL / route problem\n\"Connection refused\" → SG let you in; the app\n"
          "is down or not listening on that port", "yellow", size=11, align="left")
    d.box("ports", 480, 370, 460, 110,
          "Ports to know\n22 SSH (and SFTP) · 21 FTP · 80 HTTP · 443 HTTPS\n3389 RDP (Windows) · 3306 MySQL/MariaDB/Aurora MySQL\n"
          "5432 PostgreSQL · 1521 Oracle · 1433 SQL Server", "purple", size=11, align="left")
    d.box("tip", 20, 496, 920, 88,
          "Good practice: keep a separate SG just for SSH access. A SG lives outside the instance: if traffic is blocked,\n"
          "the instance never sees it. In a VPC a SG works at the instance (ENI) level; a NACL works at the subnet level and is stateless.",
          "gray", size=11, align="left", bold_first=False)
    return d


def ec2_purchase_options():
    d = Diagram("ec2-03-purchase-options", 960, 640, "EC2 purchasing options (think of a hotel)")
    rows = [
        ("On-Demand", "walk in, pay full price", "pay per second (Linux/Windows, after the 1st minute),\nper hour for others · no commitment · highest cost",
         "short, unpredictable workloads", "blue"),
        ("Reserved Instances\n(1 or 3 years)", "book a room long in advance", "up to ~72% off · fixed instance type, region, tenancy, OS\nAll/Partial/No upfront · Regional or Zonal scope\nConvertible RI: change type, ~66% off · resell on RI Marketplace",
         "steady-state apps, databases", "green"),
        ("Savings Plans\n(1 or 3 years)", "promise to spend $X per hour", "up to ~72% off · commit to $/hour of usage\nEC2 Instance SP: locked to family + region, flexible size/OS/tenancy\nusage above the commitment = On-Demand price",
         "long workloads that change size", "green"),
        ("Spot Instances", "last-minute empty room, can be\nkicked out", "up to ~90% off · AWS can take it back with a\n2-minute warning when your max price < spot price",
         "batch, data analysis, image processing,\nCI, any fault-tolerant job (NOT databases)", "orange"),
        ("Dedicated Host", "rent a whole building", "a physical server just for you; you see sockets/cores\nOn-Demand or Reserved · most expensive",
         "BYOL (per-socket/core licences),\nstrict compliance", "red"),
        ("Dedicated Instance", "rooms in a building only\nyour company uses", "hardware not shared with other AWS accounts;\nmay share with your own instances; no control of placement",
         "isolation without host control", "purple"),
        ("Capacity Reservation", "book a room, pay even if\nyou never come", "reserve capacity in one AZ for any duration\nNO discount by itself (combine with RI/SP) · billed running or not",
         "short events that MUST get capacity", "gray"),
    ]
    d.text("h1", 20, 44, 170, 22, "Option", size=12, bold=True)
    d.text("h2", 196, 44, 190, 22, "Hotel analogy", size=12, bold=True)
    d.text("h3", 392, 44, 340, 22, "Key facts", size=12, bold=True)
    d.text("h4", 738, 44, 202, 22, "Use it for", size=12, bold=True)
    for i, (opt, hotel, facts, use, col) in enumerate(rows):
        y = 70 + i * 80
        d.box(f"o{i}", 20, y, 170, 72, opt, col, size=12)
        d.box(f"ho{i}", 196, y, 190, 72, hotel, "white", size=11, bold_first=False)
        d.box(f"f{i}", 392, y, 340, 72, facts, "white", size=10, align="left", bold_first=False)
        d.box(f"u{i}", 738, y, 202, 72, use, "white", size=10, bold_first=False)
    return d


def ec2_spot():
    d = Diagram("ec2-04-spot", 960, 420, "Spot requests and Spot Fleets")
    d.box("req", 20, 50, 300, 150,
          "Spot request\nyou set: max price, number of instances,\nlaunch spec, type: one-time or persistent,\nvalid from / until\n"
          "if spot price > your max price: you get a\n2-minute notice, then stop or terminate", "orange", size=11, align="left")
    d.icon("spot-ic", 276, 54, "ec2-spot", 36)
    d.box("one", 360, 50, 260, 66, "One-time request\nfulfilled once, then the request closes", "white", size=11)
    d.box("per", 360, 134, 260, 66, "Persistent request\nrelaunches instances when they are stopped", "white", size=11)
    d.edge("req", "one")
    d.edge("req", "per")
    d.box("cancel", 650, 50, 290, 150,
          "Trap: to stop spot instances for good\n1. CANCEL the spot request first\n(only open, active or disabled\nrequests can be cancelled)\n"
          "2. then TERMINATE the instances\nIf you terminate first, a persistent\nrequest just launches new ones.", "red", size=11, align="left")
    d.box("fleet", 20, 220, 920, 180,
          "Spot Fleet = a set of Spot Instances + (optional) On-Demand Instances, from several launch pools\n"
          "(pools = instance type + OS + AZ). It tries to meet the target capacity within your price limit.\n"
          "Allocation strategies:\n"
          "• lowestPrice: cheapest pool (cost optimisation, short workloads)\n"
          "• diversified: spread across all pools (great for availability and long workloads)\n"
          "• capacityOptimized: pools with the most spare capacity (fewer interruptions)\n"
          "• priceCapacityOptimized (recommended): most capacity first, then the lowest price among those",
          "blue", size=11, align="left")
    d.icon("fleet-ic", 892, 228, "spot-fleet", 36)
    return d


# ---------------------------------------------------------------- 04 EC2 associate
def ec2_ips():
    d = Diagram("ec2-05-ip-addresses", 960, 520, "Private IP, public IP and Elastic IP on EC2")
    d.box("inet", 20, 60, 180, 60, "Internet", "white", size=12, icon="internet")
    d.group("vpc", 240, 44, 700, 300, "VPC 10.0.0.0/16 (private network)", "gray", align="left", size=12, icon="vpc")
    d.box("a", 270, 90, 300, 110,
          "Instance A\nprivate IP 10.0.1.15 (fixed for its life)\npublic IP 13.233.x.x\n(CHANGES after stop → start)", "orange", size=11, icon="ec2-instance")
    d.box("b", 610, 90, 300, 110,
          "Instance B\nprivate IP 10.0.2.20\nElastic IP 52.66.x.x\n(fixed until you release it)", "orange", size=11, icon="ec2-instance")
    d.box("c", 440, 240, 300, 80, "Instance C\nprivate IP only (no public IP)\nreachable only inside the VPC", "orange", size=11, icon="ec2-instance")
    d.edge("inet", "a", "public IP")
    d.edge("a", "c", "private IPs talk\ninside the VPC", points=[(420, 280)])
    d.box("t1", 20, 360, 300, 144,
          "Public IP\nunique on the whole internet\nreachable from anywhere\nassigned from AWS's pool\nlost on stop/start", "blue", size=11)
    d.box("t2", 330, 360, 300, 144,
          "Private IP\nunique only inside its network\ntwo networks can reuse the same\nranges; leaves via NAT / proxy\nkept on stop/start", "green", size=11)
    d.box("t3", 640, 360, 300, 144,
          "Elastic IP\nstatic public IPv4 you own until released\nattach to one instance at a time; remap\non failure · max 5 per account (soft limit)\n"
          "all public IPv4 is billed (since Feb 2024)\nAvoid: use DNS or a load balancer", "yellow", size=11, icon="ec2-eip", icon_size=28, valign="top")
    return d


def placement_groups():
    d = Diagram("ec2-06-placement-groups", 960, 520, "Placement groups: cluster, spread, partition")
    d.group("cl", 20, 44, 290, 300, "Cluster", "red", size=13)
    d.group("rack", 40, 80, 250, 120, "one rack, one AZ", "white", dashed=True, size=11)
    for i in range(4):
        d.icon(f"c{i}", 58 + i * 58, 112, "ec2-instance", 40)
    d.text("cn", 30, 206, 270, 134,
           "same hardware, same AZ\n+ lowest latency, 10 Gbps+\n  between instances (enhanced\n  networking)\n"
           "− rack fails = ALL fail\nUse: HPC, big data jobs that\nmust finish fast", size=11, align="left")
    d.group("sp", 335, 44, 290, 300, "Spread", "green", size=13)
    for i in range(3):
        d.box(f"r{i}", 350 + i * 92, 80, 80, 92, f"rack {i + 1}", "white", size=11, valign="top")
        d.icon(f"ri{i}", 370 + i * 92, 110, "ec2-instance", 40)
    d.text("sn", 345, 180, 270, 160,
           "each instance on different hardware\n+ can span AZs; one failure hits\n  only one instance\n"
           "− max 7 instances per AZ\n  per group\nUse: a few critical instances\nthat must not fail together", size=11, align="left")
    d.group("pt", 650, 44, 290, 300, "Partition", "blue", size=13)
    for i in range(3):
        d.group(f"p{i}", 662 + i * 92, 80, 84, 112, f"partition {i + 1}", "white", dashed=True, size=10)
        d.icon(f"pe{i}a", 688 + i * 92, 104, "ec2-instance", 34)
        d.icon(f"pe{i}b", 688 + i * 92, 148, "ec2-instance", 34)
    d.text("pn", 660, 196, 270, 144,
           "partitions = separate racks\n+ up to 7 partitions per AZ, many\n  AZs, 100s of instances\n"
           "+ failure stays in one partition;\n  instance metadata tells the app\nUse: HDFS, HBase, Cassandra, Kafka", size=11, align="left")
    d.box("hook", 20, 360, 920, 144,
          "Exam hooks\n• \"lowest latency / highest network throughput between instances\" → Cluster\n"
          "• \"maximise availability, small number of critical instances\" → Spread\n"
          "• \"big distributed, partition-aware system (Hadoop, Cassandra, Kafka)\" → Partition\n"
          "• \"high-precision time, PTP clock (distributed DBs, financial timestamps)\" → Precision time (new 4th type)",
          "yellow", size=11, align="left")
    return d


def eni_hibernate():
    d = Diagram("ec2-07-eni-hibernate", 960, 540, "Elastic Network Interfaces (ENI) and EC2 Hibernate")
    d.group("az", 20, 44, 460, 300, "One AZ (an ENI is bound to its AZ)", "green", dashed=True, align="left", size=12)
    d.box("i1", 40, 84, 180, 60, "EC2 #1 (primary)", "orange", size=12, icon="ec2-instance")
    d.box("i2", 280, 84, 180, 60, "EC2 #2 (standby)", "orange", size=12, icon="ec2-instance")
    d.box("eth0", 40, 180, 180, 60, "eth0 (primary ENI)\n10.0.0.10", "blue", size=11, icon="eni")
    d.box("eth1", 160, 264, 180, 66, "eth1 (secondary ENI)\n10.0.0.50", "blue", size=11, icon="eni")
    d.edge("eth0", "i1")
    d.edge("eth1", "i1", "attached now")
    d.edge("eth1", "i2", "move on failover", dashed=True)
    d.box("enif", 500, 44, 440, 300,
          "An ENI is a virtual network card. It can have:\n• one primary private IPv4, plus secondary ones\n"
          "• one Elastic IP per private IPv4\n• one public IPv4\n• one or more security groups\n• a MAC address\n\n"
          "You can create ENIs on their own and attach or move\nthem between instances (in the same AZ) for failover:\n"
          "the private IP moves with the ENI.", "white", size=11, align="left")
    d.box("hib", 20, 360, 460, 164,
          "Hibernate\nstop → the RAM is written to the root EBS volume\nstart → the RAM is loaded back: processes keep\n"
          "running, the OS does not reboot (fast start)\nUse: long-running processes, apps slow to warm up", "purple", size=11, align="left")
    d.box("hibr", 500, 360, 440, 164,
          "Hibernate rules\n• root volume must be EBS, ENCRYPTED, and big\n  enough to hold the RAM\n"
          "• RAM must be < 150 GB · not for bare metal\n• On-Demand, Reserved and Spot instances\n"
          "• an instance cannot stay hibernated > 60 days", "yellow", size=11, align="left")
    return d


# ---------------------------------------------------------------- 05 EC2 storage
def storage_compare():
    d = Diagram("storage-01-ebs-instance-store-efs", 960, 580, "EC2 storage: EBS vs instance store vs EFS")
    d.group("az1", 20, 44, 450, 330, "AZ a", "green", dashed=True, align="left", size=12)
    d.group("az2", 490, 44, 450, 330, "AZ b", "green", dashed=True, align="left", size=12)
    d.box("e1", 50, 84, 150, 54, "EC2 #1", "orange", size=12, icon="ec2-instance")
    d.box("e2", 280, 84, 150, 54, "EC2 #2", "orange", size=12, icon="ec2-instance")
    d.box("e3", 520, 84, 150, 54, "EC2 #3", "orange", size=12, icon="ec2-instance")
    d.box("ebs1", 40, 190, 170, 64, "EBS volume\nnetwork drive, this AZ", "blue", size=11, icon="ebs-volume")
    d.box("is", 270, 190, 170, 64, "Instance store\ndisk on the host", "red", size=11, icon="server")
    d.edge("ebs1", "e1", "network")
    d.edge("is", "e2", "physical")
    d.box("ebs2", 510, 190, 170, 64, "EBS snapshot → new\nvolume in AZ b", "blue", size=11, dashed=True)
    d.edge("ebs1", "ebs2", "snapshot to move\nacross AZs", dashed=True, points=[(125, 290), (595, 290)])
    d.box("efs", 700, 190, 220, 64, "EFS file system\n(NFS, multi-AZ)\nmounted by many EC2s", "purple", size=11, icon="efs-fs")
    d.edge("efs", "e3", "mount")
    d.text("note", 40, 310, 880, 56,
           "EBS: one instance at a time (except io1/io2 Multi-Attach) and locked to its AZ.  Instance store: fastest, but data is lost on stop/terminate.\n"
           "EFS: hundreds of instances in many AZs share one file system.", size=11, align="left")
    d.box("c1", 20, 390, 300, 174,
          "EBS\n• network drive: some latency\n• persists after the instance stops\n• provisioned size + IOPS, billed for it\n"
          "• root volume deleted on terminate by\n  default; extra volumes kept\n• snapshots for backup", "blue", size=11, align="left")
    d.box("c2", 330, 390, 300, 174,
          "Instance store\n• physical disk on the host: best I/O\n  (millions of IOPS)\n• ephemeral: gone on stop/terminate\n  or hardware failure\n"
          "• use for buffer, cache, scratch,\n  temp data; back up yourself", "red", size=11, align="left")
    d.box("c3", 640, 390, 300, 174,
          "EFS\n• managed NFS (v4.1), Linux only (POSIX)\n• grows automatically, pay per GB used\n• about 3× the price of gp2\n"
          "• access controlled by a security group\n• use: content management, web\n  serving, shared data, WordPress", "purple", size=11, align="left")
    return d


def ebs_snapshots_ami():
    d = Diagram("storage-02-snapshots-ami", 960, 560, "EBS snapshots and AMIs")
    d.box("vol", 20, 60, 170, 60, "EBS volume\n(AZ a)", "blue", size=12, icon="ebs-volume")
    d.box("snap", 250, 60, 190, 60, "Snapshot\n(point in time,\nstored by AWS)", "yellow", size=11, icon="ebs-snapshot")
    d.box("vol2", 500, 30, 190, 54, "new volume in AZ b", "blue", size=11, icon="ebs-volume", icon_size=28)
    d.box("snap2", 500, 100, 190, 54, "copy in another region", "yellow", size=11, icon="ebs-snapshot", icon_size=28)
    d.edge("vol", "snap", "create\n(detach not needed,\nbut recommended)")
    d.edge("snap", "vol2", "restore")
    d.edge("snap", "snap2", "copy")
    d.box("feat", 720, 30, 220, 240,
          "Snapshot features\n• Snapshot Archive: ~75%\n  cheaper; restore takes\n  24–72 hours\n"
          "• Recycle Bin: rules keep\n  deleted snapshots/AMIs\n  1 day – 1 year\n• Fast Snapshot Restore:\n"
          "  full speed from the first\n  read; costs a lot", "white", size=11, align="left")
    d.text("hami", 20, 186, 680, 24, "Building and using an AMI (Amazon Machine Image)", size=13, bold=True)
    steps = [("1. launch EC2\nfrom an AMI", "orange"), ("2. install and\ncustomise", "orange"),
             ("3. STOP it\n(data integrity)", "red"), ("4. create AMI\n(makes EBS snapshots)", "yellow"),
             ("5. launch new\ninstances from it", "green")]
    for i, (s, col) in enumerate(steps):
        d.box(f"s{i}", 20 + i * 140, 216, 124, 64, s, col, size=11, bold_first=False)
        if i:
            d.edge(f"s{i - 1}", f"s{i}")
    d.box("ami", 20, 300, 450, 244,
          "AMI facts\n• a customised image: OS, software, config,\n  monitoring agents → faster boot\n"
          "• built for ONE region; copy it to use in\n  another region\n• sources: public AMIs (AWS), your own AMIs,\n"
          "  AWS Marketplace AMIs (someone sells them)\n• behind an EBS-backed AMI are EBS snapshots", "blue", size=11, align="left")
    d.icon("ami-ic", 418, 308, "ec2-ami", 44)
    d.box("trap", 490, 300, 450, 244,
          "Exam traps\n• move a volume to another AZ → snapshot,\n  then restore in the new AZ\n"
          "• encrypt an unencrypted volume → snapshot →\n  copy the snapshot with encryption on → create\n  a volume from it → attach (or restore with\n  encryption on)\n"
          "• golden AMI = pre-installed software, faster\n  ASG scale-out", "red", size=11, align="left")
    return d


def ebs_volume_types():
    d = Diagram("storage-03-ebs-volume-types", 960, 520, "EBS volume types: SSD for IOPS, HDD for throughput")
    cols = [
        ("gp3 / gp2\nGeneral Purpose SSD", "boot volumes, dev/test,\nvirtual desktops, medium DBs\n\ngp3: 1 GiB – 64 TiB, baseline\n3,000 IOPS + 125 MiB/s, raise\nindependently up to 80,000\nIOPS and 2,000 MiB/s\ngp2: 1 GiB – 16 TiB, IOPS tied\nto size (3 per GiB, burst 3,000,\nmax 16,000 at 5,334 GiB)", "blue"),
        ("io2 Block Express / io1\nProvisioned IOPS SSD", "critical DBs, sustained IOPS,\nor more than 80,000 IOPS\n\nio1: 4 GiB – 16 TiB, 64,000\nIOPS (Nitro; 32,000 others),\n50 IOPS per GiB\nio2 Block Express: 4 GiB –\n64 TiB, 256,000 IOPS, sub-ms,\n1,000 IOPS per GiB\nMulti-Attach supported", "green"),
        ("st1\nThroughput Optimized HDD", "big data, data warehouse,\nlog processing\n(large sequential reads)\n\n125 GiB – 16 TiB\nmax 500 MiB/s, 500 IOPS\nCANNOT be a boot volume", "orange"),
        ("sc1\nCold HDD", "data accessed rarely,\nlowest cost\n\n125 GiB – 16 TiB\nmax 250 MiB/s, 250 IOPS\nCANNOT be a boot volume", "gray"),
    ]
    for i, (h, b, col) in enumerate(cols):
        x = 20 + i * 232
        d.box(f"h{i}", x, 50, 220, 60, h, col, size=12, icon="ebs-gp3" if i == 0 else "ebs-volume", icon_size=26)
        d.box(f"b{i}", x, 116, 220, 220, b, "white", size=11, bold_first=False)
    d.box("ma", 20, 352, 450, 152,
          "Multi-Attach (io1/io2 only)\n• one volume attached to up to 16 instances\n  in the SAME AZ, each with read + write\n"
          "• needs a cluster-aware file system\n  (not ext4 or XFS)\n• use: clustered Linux apps (e.g. Teradata)", "green", size=11, align="left")
    d.box("enc", 490, 352, 450, 152,
          "EBS encryption (KMS, AES-256)\n• encrypts: data at rest, data moving between\n  the instance and the volume, all snapshots,\n"
          "  all volumes made from those snapshots\n• handled transparently, tiny latency impact\n• can be on by default per region (account setting)", "purple", size=11, align="left")
    return d


def efs_classes():
    d = Diagram("storage-04-efs", 960, 480, "EFS: modes, storage classes and availability")
    d.box("perf", 20, 50, 300, 180,
          "Performance mode (set at creation)\n• General Purpose (default):\n  latency-sensitive (web server, CMS)\n"
          "• Max I/O: higher latency, more\n  throughput, highly parallel\n  (big data, media processing)", "blue", size=11, align="left")
    d.box("thr", 330, 50, 300, 180,
          "Throughput mode\n• Bursting: throughput grows with\n  the size of the file system\n"
          "• Provisioned: set throughput apart\n  from storage size\n• Elastic: scales up and down with\n  the workload (unpredictable load)", "green", size=11, align="left")
    d.box("tier", 640, 50, 300, 180,
          "Storage classes (lifecycle policy\nmoves files after N days)\n• Standard: frequently accessed\n"
          "• Infrequent Access (EFS-IA): cheaper\n  storage, fee per read\n• Archive: read a few times a year,\n  ~50% cheaper than IA", "orange", size=11, align="left")
    d.box("std", 20, 250, 450, 110,
          "Regional (Standard) availability\ndata stored across multiple AZs\nuse for production", "purple", size=11, icon="efs-standard", icon_size=48)
    d.box("one", 490, 250, 450, 110,
          "One Zone\none AZ, backup on by default, works with IA\n(EFS One Zone-IA) · use for dev/test, backups", "gray", size=11, icon="efs-onezone", icon_size=48)
    d.box("save", 20, 376, 920, 88,
          "Cost: use the right storage class + lifecycle policy for up to ~90% savings.  Encryption at rest with KMS.\n"
          "EFS vs EBS in one line: EBS = one instance, one AZ, block disk.  EFS = many instances, many AZs, shared NFS, Linux only.",
          "yellow", size=11, align="left", bold_first=False)
    return d


# ---------------------------------------------------------------- 06 ELB + ASG
def elb_types():
    d = Diagram("elb-01-types", 960, 520, "Elastic Load Balancer types")
    cols = [
        ("Application LB\n(ALB, 2016)", "Layer 7\nHTTP, HTTPS, WebSocket,\nHTTP/2, gRPC\n\nroutes by path, host,\nheader, query string\ntargets: EC2, ECS tasks,\nLambda, private IPs\nfixed DNS name\nclient IP in X-Forwarded-For", "blue"),
        ("Network LB\n(NLB, 2017)", "Layer 4\nTCP, TLS, UDP\n\nmillions of requests/sec,\nultra-low latency\nONE static IP per AZ\n(can use Elastic IPs)\ntargets: EC2, private IPs,\nan ALB\nkeeps the client IP", "green"),
        ("Gateway LB\n(GWLB, 2020)", "Layer 3 (IP packets)\nGENEVE, port 6081\n\nsends all traffic through\na fleet of 3rd-party\nappliances: firewalls,\nIDS/IPS, deep packet\ninspection, then back\ntargets: EC2, private IPs", "purple"),
        ("Classic LB\n(CLB, 2009)", "Layer 4 + 7 (old gen)\nHTTP, HTTPS, TCP, SSL\n\nlegacy: do not use for\nnew work\none SSL certificate only\nhealth check TCP or HTTP", "gray"),
    ]
    for i, (h, b, col) in enumerate(cols):
        x = 20 + i * 232
        d.box(f"h{i}", x, 50, 220, 56, h, col, size=12, icon=["alb", "nlb", "gwlb", "clb"][i], icon_size=36)
        d.box(f"b{i}", x, 112, 220, 230, b, "white", size=11, bold_first=False)
    d.box("why", 20, 358, 450, 146,
          "Why a load balancer\n• one DNS name for the app; spreads load\n• health checks, stops sending to bad targets\n"
          "• SSL/TLS termination · stickiness\n• HA across AZs · public front, private back\n• managed: AWS patches and scales it", "yellow", size=11, align="left")
    d.box("pick", 490, 358, 450, 146,
          "Exam picks\n• HTTP routing, microservices, containers → ALB\n• extreme performance, TCP/UDP, static IP → NLB\n"
          "• inspect all traffic with appliances → GWLB\n• \"internet-facing\" or \"internal\": all types\n• health check: protocol + port + path, 200 OK", "red", size=11, align="left")
    return d


def alb_flow():
    d = Diagram("elb-02-alb-flow", 960, 600, "ALB request flow: listener → rules → target groups")
    d.box("user", 20, 70, 140, 60, "Users\n0.0.0.0/0", "white", size=11, icon="users")
    d.group("lbsg", 200, 44, 250, 320, "ALB (SG: 80/443 from anywhere)", "blue", size=12, icon="alb")
    d.box("lis", 220, 80, 210, 54, "Listener HTTPS :443\ncert from ACM (SNI)", "white", size=11)
    d.box("rules", 220, 150, 210, 140,
          "Rules (in order)\npath /api/* → tg-api\nhost img.example.com\n   → tg-img\nquery ?Platform=Mobile\n   → tg-mobile\ndefault → tg-web", "white", size=10, align="left")
    d.edge("user", "lis", "https")
    d.edge("lis", "rules")
    d.group("az", 500, 44, 440, 320, "Targets (SG: app port from the ALB's SG only)", "orange", size=12)
    d.box("tg1", 520, 84, 190, 60, "tg-web\nEC2 in an ASG", "white", size=11, icon="ec2-instances", icon_size=28)
    d.box("tg2", 730, 84, 190, 60, "tg-api\nECS tasks (dynamic ports)", "white", size=11)
    d.box("tg3", 520, 170, 190, 60, "tg-img\nLambda (request\n→ JSON event)", "white", size=11, icon="lambda-fn", icon_size=28)
    d.box("tg4", 730, 170, 190, 60, "tg-mobile\nprivate IPs (on-prem)", "white", size=11, icon="corp-dc", icon_size=28)
    d.edge("rules", "tg1")
    d.edge("rules", "tg3")
    d.text("hc", 520, 244, 400, 110,
           "Health checks are set per target group.\nThe app sees the ALB's IP as the source; the real client\n"
           "is in the headers X-Forwarded-For (IP),\nX-Forwarded-Port and X-Forwarded-Proto.", size=11, align="left")
    d.box("st", 20, 380, 300, 204,
          "Sticky sessions (CLB, ALB, NLB)\nsame client → same target\n• duration-based cookie made by\n  the LB: AWSALB (ALB), AWSELB (CLB)\n"
          "• application-based: custom cookie\n  from the app, or AWSALBAPP\n• reserved names: AWSALB,\n  AWSALBAPP, AWSALBTG\n• can unbalance the load", "purple", size=11, align="left")
    d.box("cz", 330, 380, 300, 204,
          "Cross-zone load balancing\nspread evenly over ALL targets\nin all AZs, not per AZ\n"
          "• ALB: on by default (can turn off\n  per target group), no inter-AZ fee\n• NLB, GWLB: off by default;\n  inter-AZ data billed if on\n"
          "• CLB: off by default, free if on", "green", size=11, align="left")
    d.box("ssl", 640, 380, 300, 204,
          "SSL/TLS and draining\n• certs from ACM or uploaded\n• SNI: many certs on one listener,\n  one per hostname (ALB, NLB,\n  CloudFront only; CLB = 1 cert)\n"
          "• deregistration delay (CLB:\n  connection draining) lets requests\n  finish: 1–3,600 s, default 300 s,\n  0 = off", "yellow", size=11, align="left")
    return d


def asg():
    d = Diagram("elb-03-asg", 960, 600, "Auto Scaling Group: keep the right number of healthy instances")
    d.box("cw", 20, 60, 200, 80, "CloudWatch alarm\ne.g. average CPU > 70%\nfor 5 minutes", "red", size=11, icon="cw-alarm")
    d.box("pol", 20, 180, 200, 80, "Scaling policy\nscale out: +2 instances\nscale in: −1 instance", "purple", size=11)
    d.edge("cw", "pol", "triggers")
    d.group("asg", 260, 44, 480, 250, "ASG across 2 AZs · min 2 · desired 3 · max 6", "orange", size=12, icon="asg-group")
    for i in range(3):
        d.box(f"e{i}", 290 + i * 150, 90, 120, 50, "EC2", "white", size=12, icon="ec2-instance")
    for i in range(3):
        d.box(f"n{i}", 290 + i * 150, 160, 120, 50, "new EC2", "white", size=11, dashed=True)
    d.text("nn", 280, 222, 450, 64,
           "scale out adds instances (up to max), scale in removes them (down to min).\nUnhealthy instances are terminated and replaced.", size=11)
    d.edge("pol", "asg", "changes desired")
    d.box("elb", 780, 90, 160, 80, "ELB\nnew instances\nare registered\nautomatically", "blue", size=11, icon="elb", icon_size=28)
    d.edge("elb", "e2", "health checks", both=True)
    d.box("lt", 20, 310, 300, 270,
          "Launch template (what to launch)\n• AMI + instance type\n• EC2 user data\n• EBS volumes\n• security groups\n• SSH key pair\n• IAM role (instance profile)\n"
          "• network + subnets\n• load balancer info\n(launch configurations are the old,\nretired way)", "blue", size=11, align="left")
    d.box("pols", 330, 310, 330, 270,
          "Scaling policy types\n• Target tracking: keep average CPU\n  at 40% (easiest)\n• Simple / step: alarm → add or remove\n  N units\n"
          "• Scheduled: known pattern (+10 at\n  5 PM Friday)\n• Predictive: forecasts load from\n  history and scales ahead\nGood metrics: CPUUtilization,\nRequestCountPerTarget, network in/out,\ncustom CloudWatch metrics", "green", size=11, align="left")
    d.box("cool", 670, 310, 270, 270,
          "Cooldown and facts\n• after a scaling action, a cooldown\n  (default 300 s) stops new launches/\n  terminations while metrics settle\n"
          "• use a ready-made (golden) AMI so\n  new instances serve faster\n• ASG is free: you pay for EC2\n• health checks: EC2 status or ELB", "yellow", size=11, align="left")
    return d


# ---------------------------------------------------------------- 07 RDS / Aurora / ElastiCache
def rds_replicas_multiaz():
    d = Diagram("rds-01-read-replicas-vs-multi-az", 960, 600, "RDS read replicas (scale reads) vs Multi-AZ (survive failure)")
    d.group("rr", 20, 44, 450, 330, "Read replicas: for READ SCALING", "green", size=13)
    d.box("app1", 40, 80, 410, 44, "App: writes to main, reports read from replicas", "white", size=11)
    d.box("m1", 40, 160, 130, 60, "Main DB\nread + write", "blue", size=11, icon="rds")
    d.box("r1", 220, 140, 110, 50, "replica\nsame AZ", "green", size=11)
    d.box("r2", 220, 200, 110, 50, "replica\nother AZ", "green", size=11)
    d.box("r3", 340, 170, 110, 50, "replica\nother region", "green", size=11)
    d.edge("m1", "r1", "ASYNC")
    d.edge("m1", "r2", "ASYNC")
    d.text("rrn", 30, 262, 430, 108,
           "• up to 15 replicas; same AZ, cross-AZ or cross-region\n• async = eventually consistent; SELECT only\n"
           "• a replica can be PROMOTED to its own DB\n• app needs each replica's connection string\n"
           "• cross-AZ replication in one region: no data fee", size=11, align="left")
    d.group("ma", 490, 44, 450, 330, "Multi-AZ: for DISASTER RECOVERY", "red", size=13)
    d.box("app2", 510, 80, 410, 44, "App uses ONE DNS name: mydb.xxxx.rds.amazonaws.com", "white", size=11)
    d.box("m2", 520, 170, 150, 60, "Primary\nAZ a", "blue", size=11, icon="rds")
    d.box("sb", 770, 170, 150, 60, "Standby\nAZ b\n(no traffic)", "gray", size=11, icon="rds")
    d.edge("m2", "sb", "SYNC")
    d.text("man", 500, 250, 430, 120,
           "• standby is not readable, not for scaling\n• automatic failover (DNS moves) on AZ, network,\n  instance or storage failure; no app change\n"
           "• a read replica CAN be set up as Multi-AZ\n• single-AZ → Multi-AZ: no downtime (snapshot,\n  restore in the new AZ, then sync)", size=11, align="left")
    d.box("cmp", 20, 390, 920, 194,
          "One-line picks\n\"Reporting/analytics slows the production DB\" → read replica, point the reports at it.\n"
          "\"DB must survive an AZ outage automatically\" → Multi-AZ.\n\"Read traffic in another region, and DR there\" → cross-region read replica (data transfer is billed).\n"
          "RDS engines: PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, IBM Db2, Aurora.  Managed: patching, backups, PITR, monitoring,\n"
          "scaling, maintenance windows; storage on EBS; NO SSH (except RDS Custom).",
          "yellow", size=11, align="left")
    return d


def aurora():
    d = Diagram("rds-02-aurora", 960, 620, "Aurora: one shared, self-healing storage volume across 3 AZs")
    d.box("app", 20, 50, 920, 40, "Application", "white", size=12)
    d.box("we", 120, 110, 260, 50, "Writer endpoint\n(always points to the primary)", "blue", size=11)
    d.box("re", 580, 110, 260, 50, "Reader endpoint\n(load balances across replicas)", "green", size=11)
    d.box("w", 120, 190, 200, 54, "Primary (writer)", "blue", size=12, icon="aurora-instance")
    d.box("ra", 460, 190, 140, 54, "Replica 1", "green", size=11, icon="aurora-instance")
    d.box("rb", 620, 190, 140, 54, "Replica 2", "green", size=11, icon="aurora-instance")
    d.box("rc", 780, 190, 140, 54, "… up to 15", "green", size=11, icon="aurora-instance")
    d.edge("we", "w")
    d.edge("re", "rb")
    d.group("vol", 20, 270, 920, 130, "Shared storage volume: auto-expands in 10 GB steps, up to 256 TB", "orange", size=12)
    for i, az in enumerate(["AZ a", "AZ b", "AZ c"]):
        d.group(f"az{i}", 40 + i * 300, 300, 280, 90, az, "white", dashed=True, size=11)
        d.box(f"c{i}a", 60 + i * 300, 326, 110, 50, "copy", "yellow", size=11)
        d.box(f"c{i}b", 190 + i * 300, 326, 110, 50, "copy", "yellow", size=11)
    d.box("f1", 20, 416, 450, 188,
          "Facts\n• MySQL- and PostgreSQL-compatible, AWS-built\n• ~5× MySQL / ~3× PostgreSQL on RDS speed\n"
          "• 6 copies in 3 AZs: 4 of 6 needed to write,\n  3 of 6 to read; self-healing\n• replica lag in milliseconds; failover < 30 s\n"
          "• costs ~20% more than RDS, but more efficient\n• custom endpoints: a subset of replicas", "blue", size=11, align="left")
    d.box("f2", 490, 416, 450, 188,
          "Flavours\n• Replica auto scaling: add replicas on load\n• Serverless: capacity scales with use, pay per\n  second; infrequent or unpredictable load\n"
          "• Global Database: 1 primary + up to 10 read-only\n  regions, lag < 1 s, promote (DR) RTO < 1 min\n• Aurora ML: call SageMaker / Comprehend in SQL\n"
          "• Babelfish (PostgreSQL): understands T-SQL", "purple", size=11, align="left")
    return d


def rds_backup_proxy():
    d = Diagram("rds-03-backups-security-proxy", 960, 560, "RDS / Aurora backups, security and RDS Proxy")
    d.box("bk", 20, 50, 300, 230,
          "Backups\n• automated: daily full backup in the\n  backup window + transaction logs\n  every 5 min → point-in-time restore\n"
          "  (oldest backup … 5 min ago)\n• retention 1–35 days (RDS: 0 = off;\n  Aurora: cannot turn off)\n• manual snapshots: kept until you\n  delete them", "blue", size=11, align="left")
    d.box("rs", 330, 50, 300, 230,
          "Restore and clone\n• any restore creates a NEW DB\n• RDS MySQL from S3: DB backup file\n  → S3 → new RDS instance\n"
          "• Aurora MySQL from S3: Percona\n  XtraBackup → S3 → new cluster\n• Aurora clone: copy-on-write, faster\n  than snapshot+restore (staging DB)\n"
          "• stopped DB still pays storage:\n  snapshot + delete to save", "green", size=11, align="left")
    d.box("sec", 640, 50, 300, 230,
          "Security\n• at rest: KMS, chosen at launch;\n  unencrypted primary → replicas\n  can't be encrypted\n"
          "• encrypt existing DB: snapshot →\n  copy encrypted → restore\n• in flight: TLS by default\n• IAM database authentication\n• security groups · audit logs →\n  CloudWatch Logs", "red", size=11, align="left")
    d.box("lam", 20, 310, 180, 160, "Many Lambda\nfunctions / apps\nopening and\nclosing\nconnections", "orange", size=11, icon="lambda-fn")
    d.box("px", 290, 330, 200, 120, "RDS Proxy\npools and shares\nconnections\n(VPC only,\nnever public)", "purple", size=11, icon="rds-proxy")
    d.box("db", 580, 350, 160, 80, "RDS / Aurora", "blue", size=12, icon="rds")
    d.edge("lam", "px", "100s of\nconnections")
    d.edge("px", "db", "few pooled\nconnections")
    d.box("pxf", 760, 310, 180, 234,
          "RDS Proxy facts\n• less CPU/RAM\n  stress on the DB\n• failover up to\n  66% faster\n• serverless, multi-AZ\n"
          "• no code change\n  (new endpoint)\n• enforces IAM auth;\n  creds in Secrets\n  Manager", "yellow", size=11, align="left")
    d.box("st", 20, 490, 720, 54,
          "Storage auto scaling: grows when free space < 10%, low for ≥ 5 min, and 6 h since the last change; set a max threshold.",
          "gray", size=11, align="left", bold_first=False)
    return d


def elasticache():
    d = Diagram("rds-04-elasticache", 960, 600, "ElastiCache: an in-memory cache in front of the database")
    d.box("app", 20, 120, 160, 70, "Application", "orange", size=12, icon="ec2-instance")
    d.box("cache", 330, 60, 200, 70, "ElastiCache\nRedis / Memcached\n/ Valkey", "red", size=11, icon="elasticache")
    d.box("db", 330, 200, 200, 70, "RDS database", "blue", size=12, icon="rds")
    d.edge("app", "cache", "1. read: hit?")
    d.edge("app", "db", "2. miss: read DB")
    d.edge("db", "cache", "3. write result\nto cache", dashed=True, points=[(600, 235), (600, 95)])
    d.box("pat", 640, 50, 300, 230,
          "Caching patterns\n• Lazy loading (cache-aside): fill\n  the cache on a miss; data can be\n  stale; only requested data cached\n"
          "• Write-through: update the cache\n  whenever the DB is written; never\n  stale; writes are slower\n• TTL on keys: limit staleness\n"
          "• Session store: user sessions in\n  the cache → app becomes stateless", "white", size=11, align="left")
    d.text("why", 20, 290, 600, 44,
           "Why: very low latency, takes read load off the DB, makes the app stateless. Cost: you must change app code.", size=11, align="left")
    d.box("redis", 20, 344, 450, 172,
          "Redis (and Valkey)\n• Multi-AZ with automatic failover\n• read replicas to scale reads, HA\n• durable: AOF persistence\n"
          "• backup and restore\n• data types: sets, sorted sets\n  (sorted set = gaming leaderboard)", "red", size=11, align="left", icon="redis", icon_size=40, valign="top")
    d.box("mem", 490, 344, 450, 172,
          "Memcached\n• multi-node partitioning (sharding)\n• NO replication, no high availability\n• not persistent (data lost on failure)\n"
          "• backup and restore only in serverless\n• multi-threaded\n• pick it for a simple, disposable cache", "gray", size=11, align="left", icon="memcached", icon_size=40, valign="top")
    d.box("sec", 20, 530, 920, 54,
          "Security: IAM policies for the AWS API · Redis AUTH (password/token) + TLS in flight · IAM auth for Redis · Memcached: SASL · security groups.",
          "yellow", size=11, align="left", bold_first=False)
    return d



# ---------------------------------------------------------------- Route 53 (course section 10)

def r53_dns_resolution():
    d = Diagram("r53-01-dns-resolution", 960, 600, "How a DNS query reaches Route 53 (the authoritative name server)")
    d.box("br", 20, 60, 170, 70, "Browser / client\nwants example.com", "white", size=11, icon="client")
    d.box("res", 260, 60, 220, 70, "DNS resolver (recursive)\nyour ISP or company,\ncaches answers for the TTL", "yellow", size=11)
    d.edge("br", "res", "1 example.com?")
    d.box("root", 560, 50, 380, 52, "Root name server (managed by IANA, part of ICANN)\nanswer: ask the .com servers", "gray", size=11)
    d.box("tld", 560, 116, 380, 52, "TLD name server (.com, run by the registry)\nanswer: NS records for example.com", "gray", size=11)
    d.box("r53", 560, 182, 380, 64, "Route 53 = AUTHORITATIVE name server\nfor example.com (your hosted zone)\nanswer: A 9.10.11.12, TTL 300", "orange", size=11, icon="route53", icon_size=36)
    d.edge("res", "root", "2", points=[(510, 95), (510, 76)])
    d.edge("res", "tld", "3", points=[(510, 95), (510, 142)])
    d.edge("res", "r53", "4", points=[(510, 95), (510, 214)])
    d.box("web", 260, 180, 220, 60, "Web server\n9.10.11.12", "white", size=11, icon="ec2-instance", icon_size=28)
    d.edge("br", "web", "5 HTTP to the IP", points=[(105, 210)])
    d.text("fq", 20, 262, 920, 26, "Anatomy of a name:  http :// api . www . example . com .", size=13, bold=True)
    d.box("f1", 20, 292, 180, 62, "Protocol\nhttp", "white", size=11)
    d.box("f2", 210, 292, 180, 62, "Subdomain\napi.www", "white", size=11)
    d.box("f3", 400, 292, 180, 62, "Second-level domain (SLD)\nexample", "white", size=11)
    d.box("f4", 590, 292, 170, 62, "Top-level domain (TLD)\n.com .us .in .gov .org", "white", size=10)
    d.box("f5", 770, 292, 170, 62, "Root\nthe final dot \".\"", "white", size=11)
    d.text("fqdn", 20, 358, 920, 22, "FQDN (fully qualified domain name) = api.www.example.com.  (every label up to the root)", size=11, italic=True)
    d.box("jobs", 20, 392, 460, 192,
          "Route 53 does three jobs (any combination)\n1. Domain registration (it is a registrar)\n2. DNS routing: authoritative DNS for your\n   hosted zones; you update the records\n"
          "3. Health checking of your resources\nGlobal service · name = DNS port 53\n100% availability SLA (course; see section 1)", "blue", size=11, align="left")
    d.box("terms", 500, 392, 440, 192,
          "Terms\n• Registrar: sells names (Route 53, GoDaddy, Cloudflare)\n• Registry: owns a TLD, keeps its database\n• Zone file / hosted zone: holds the DNS records\n"
          "• Name server: answers DNS queries; either\n  authoritative (Route 53) or recursive (resolver)\n• Records: A, AAAA, CNAME, NS, MX, TXT, ...", "white", size=11, align="left")
    return d


def r53_records_zones():
    d = Diagram("r53-02-records-hosted-zones", 960, 600, "Records, hosted zones and TTL")
    d.box("rec", 20, 50, 440, 170,
          "A record has 5 parts\n• Name: example.com or app.example.com\n• Type: A, AAAA, CNAME, NS, ...\n• Value: 12.34.56.78\n"
          "• Routing policy: how Route 53 answers queries\n• TTL (time to live): seconds a resolver may cache it", "white", size=11, align="left")
    d.box("types", 480, 50, 460, 170,
          "Record types to know\nA → IPv4 · AAAA → IPv6\nCNAME → another hostname (never at the zone apex)\nNS → name servers of the hosted zone\n"
          "Also: CAA DS HTTPS MX NAPTR PTR SOA SPF\nSRV SSHFP SVCB TLSA TXT (SPF: use TXT now)", "blue", size=11, align="left")
    d.group("pub", 20, 236, 440, 180, "Public hosted zone: answers the internet", "green", icon="r53-hosted-zone")
    d.box("pq", 40, 276, 180, 50, "Client on internet\napp.example.com?", "white", size=10, icon="users", icon_size=24)
    d.box("pa", 250, 276, 190, 50, "Public IP / ALB /\nCloudFront / S3", "white", size=10)
    d.edge("pq", "pa", "54.22.33.44")
    d.text("pn", 40, 336, 400, 74, "e.g. application1.mypublicdomain.com\nRoute 53 gives 4 name servers; put them at\nyour registrar (any registrar works)", size=10)
    d.group("pri", 480, 236, 460, 180, "Private hosted zone: answers only inside VPCs", "purple", icon="vpc")
    d.box("vq", 500, 276, 190, 50, "EC2 in the VPC\ndb.example.internal?", "white", size=10, icon="ec2-instance", icon_size=24)
    d.box("va", 720, 276, 200, 50, "Private IP\n10.0.0.35", "white", size=10)
    d.edge("vq", "va")
    d.text("vn", 500, 336, 420, 74, "e.g. application1.company.internal\none or more VPCs; VPC needs enableDnsHostnames\nand enableDnsSupport = true · $0.50/month per zone", size=10)
    d.box("hi", 20, 432, 300, 150, "High TTL (e.g. 24 h)\n• less traffic to Route 53 (cheaper)\n• records may be out of date longer", "yellow", size=11, align="left")
    d.box("lo", 330, 432, 300, 150, "Low TTL (e.g. 60 s)\n• more traffic to Route 53 ($$)\n• records out of date for less time\n• easy to change records", "orange", size=11, align="left")
    d.box("ttl", 640, 432, 300, 150, "TTL rules\n• mandatory on every non-alias\n  record (no default)\n• alias: you can't set it\n• lower it before a change, wait\n  the old TTL, then change", "red", size=11, align="left")
    return d


def r53_cname_alias():
    d = Diagram("r53-03-cname-vs-alias", 960, 600, "CNAME vs Alias: pointing a name at an AWS resource")
    d.box("cn", 20, 50, 450, 200,
          "CNAME (standard DNS)\n• hostname → ANY other hostname\n  app.mydomain.com → blabla.anything.com\n• NOT at the zone apex (root, mydomain.com)\n"
          "• no other record may share its name\n• target must resolve (A/AAAA) · you set the TTL\n• queries are charged", "white", size=11, align="left")
    d.box("al", 490, 50, 450, 200,
          "Alias (Route 53 extension to DNS)\n• hostname → AWS resource or a record\n  in the same hosted zone\n• works at the ROOT and on subdomains\n"
          "• type A/AAAA for AWS resources\n• follows the resource's IP changes itself\n• no TTL to set · free queries to AWS resources\n• health: Evaluate Target Health", "green", size=11, align="left")
    d.box("ex", 20, 266, 920, 54,
          "example.com   A   ALIAS → MyALB-123456789.us-east-1.elb.amazonaws.com   (AWS-managed; its IPs change, the alias keeps up)", "yellow", size=11)
    d.text("tg", 20, 330, 920, 24, "Alias targets (AWS docs list)", size=13, bold=True)
    targets = [("elb", "Elastic Load\nBalancer"), ("cloudfront", "CloudFront\ndistribution"), ("api-gateway", "API Gateway\nAPI"),
               ("beanstalk", "Beanstalk\nenvironment"), ("s3", "S3 static\nwebsite bucket"), ("vpc-endpoints", "VPC interface\nendpoint"),
               ("global-accelerator", "Global\nAccelerator"), ("route53", "Record in same\nhosted zone"), ("app-runner", "App Runner\nservice"),
               ("appsync", "AppSync\ndomain name"), ("opensearch", "OpenSearch\nService")]
    for i, (ic, lab) in enumerate(targets):
        x = 20 + (i % 6) * 154
        y = 360 + (i // 6) * 70
        d.box(f"t{i}", x, y, 146, 60, lab, "blue", size=10, bold_first=False, icon=ic, icon_size=30)
    d.box("no", 790, 430, 150, 60, "NOT an EC2\npublic DNS name", "red", size=11)
    d.box("rule", 20, 506, 920, 78,
          "Exam rule of thumb\nRoot domain (example.com) → AWS resource: Alias (CNAME is impossible at the apex).\n"
          "Subdomain → non-AWS hostname: CNAME.   Subdomain → AWS resource: Alias preferred (free, auto-updates).", "orange", size=11, align="left")
    return d


def r53_health_checks():
    d = Diagram("r53-04-health-checks", 960, 640, "Route 53 health checks: endpoint, calculated, CloudWatch alarm")
    d.group("ep", 20, 46, 450, 330, "1. Endpoint health check (public endpoints)", "green")
    for i, reg in enumerate(["us-east-1", "eu-west-1", "sa-east-1"]):
        d.box(f"hc{i}", 40 + i * 140, 84, 130, 44, f"Health checker\n{reg}", "white", size=10)
    d.box("alb", 150, 176, 190, 50, "Your endpoint\nALB / IP / domain", "white", size=11, icon="alb", icon_size=28)
    for i in range(3):
        d.edge(f"hc{i}", "alb")
    d.text("ept", 30, 230, 430, 144,
           "• checkers in many locations (course: about 15);\n  custom list = at least 3 Regions\n• interval 30 s, or 10 s (fast, extra cost)\n"
           "• failure threshold: 3 by default\n• HTTP, HTTPS, TCP · healthy = 2xx or 3xx\n• connect in 4 s, respond in 2 s after connect\n"
           "• optional string match in first 5,120 bytes\n• > 18% of checkers say healthy → HEALTHY", size=10, align="left")
    d.group("calc", 490, 46, 450, 200, "2. Calculated health check", "blue")
    d.box("par", 620, 80, 190, 40, "Parent health check", "white", size=11)
    for i in range(3):
        d.box(f"ch{i}", 510 + i * 145, 140, 130, 40, f"Child check {i + 1}", "white", size=10)
        d.edge("par", f"ch{i}")
    d.text("calct", 500, 186, 430, 58, "healthy if ALL (AND), ONE OR MORE (OR) or at least x of y\nchildren are healthy · up to 255/256 children\nuse: maintenance without failing every check", size=10, align="left")
    d.group("cw", 490, 262, 450, 200, "3. CloudWatch alarm health check", "purple")
    d.box("vpc", 510, 300, 170, 60, "Private resource\n(VPC / on-premises)", "white", size=10, icon="vpc", icon_size=28)
    d.box("alarm", 720, 300, 200, 60, "CloudWatch metric\n+ alarm", "white", size=10, icon="cw-alarm", icon_size=28)
    d.edge("vpc", "alarm", "metric")
    d.text("cwt", 500, 366, 430, 94, "Health check watches the alarm's data stream:\nOK = healthy, ALARM = unhealthy (insufficient\ndata: choose healthy / unhealthy / last known)\nUse for private resources: checkers are outside the VPC", size=10, align="left")
    d.box("fw", 20, 392, 450, 70, "Firewall: allow inbound from Route 53 health checker IPs\nip-ranges.json, service ROUTE53_HEALTHCHECKS\n(or prefix list com.amazonaws.<region>.route53-healthchecks)", "yellow", size=10, align="left")
    d.box("use", 20, 478, 920, 146,
          "How health checks drive DNS failover\n• Attach a health check to records (failover, weighted, latency, geolocation, geoproximity, multivalue...): unhealthy ones are left out.\n"
          "• A record with no health check is always treated as healthy. If every record in the group is unhealthy, Route 53 treats them all as healthy.\n"
          "• Alias records: set Evaluate Target Health = Yes so the alias follows the health of the ELB / records it points to.\n"
          "• HTTPS checks don't validate the TLS certificate. Health checks run on a schedule, not when a query arrives. They publish CloudWatch metrics.", "orange", size=11, align="left")
    return d


def r53_policies_overview():
    d = Diagram("r53-05-routing-policies", 960, 640, "Routing policies: how Route 53 chooses the answer (DNS answers, it does not route traffic)")
    pols = [
        ("Simple", "one record, one or many values\nall values in random order;\nclient picks one · values not\nhealth checked", "white"),
        ("Weighted", "share = weight / sum of weights\nweights 0-255 · 0 = stop\nall 0 = all equal · health checks\nA/B tests, region split", "blue"),
        ("Failover", "active-passive: primary +\nsecondary · primary needs a\nhealth check (or Evaluate\nTarget Health on an alias)", "red"),
        ("Latency", "lowest latency between user\nand AWS Region (measured, not\ndistance) · health checks", "green"),
        ("Geolocation", "user's continent / country /\nUS state · most specific wins\nadd a Default record or get\n\"no answer\" · health checks", "yellow"),
        ("Geoproximity", "distance user ↔ resource,\nshifted by bias -99..+99\nAWS Region / Local Zone or\nlat-long · Traffic Flow not\nneeded since Jan 2024", "orange"),
        ("IP-based", "client IP CIDR → location\n(CIDR collection) · ISP\nrouting, cut transit cost\nnot in private hosted zones", "purple"),
        ("Multivalue answer", "up to 8 healthy records,\nrandom · health checks\nnot a substitute for an ELB\nno alias multivalue", "gray"),
        ("AZ-affinity (newer)", "prefer resources in the same\nAZ / Zone Group / Region as\nthe caller (in the AWS docs,\nnot in the course)", "white"),
    ]
    for i, (h, b, col) in enumerate(pols):
        x = 20 + (i % 3) * 312
        y = 50 + (i // 3) * 150
        d.box(f"p{i}", x, y, 300, 138, f"{h}\n{b}", col, size=11)
    d.box("note", 20, 506, 920, 118,
          "Exam picks\n• Send 10% to the new version → Weighted · DR site only when primary fails → Failover · fastest Region → Latency\n"
          "• Show French site / respect distribution rights by country → Geolocation · move more users to one Region → Geoproximity bias\n"
          "• Users from a known ISP / IP range → IP-based · several healthy IPs, client-side → Multivalue · one server → Simple\n"
          "• Weighted, failover, latency, geolocation, geoproximity, multivalue: records share the same name and type", "yellow", size=11, align="left")
    return d


def r53_routing_examples_1():
    d = Diagram("r53-06-weighted-failover-latency", 960, 600, "Weighted, failover and latency routing in pictures")
    d.box("r1", 20, 60, 130, 60, "Route 53", "white", size=12, icon="route53", icon_size=30)
    for i, (w, pct) in enumerate([(70, "70%"), (20, "20%"), (10, "10%")]):
        d.box(f"w{i}", 260, 46 + i * 52, 180, 44, f"EC2 weight {w} → {pct}", "blue", size=11)
        d.edge("r1", f"w{i}")
    d.text("wt", 450, 46, 490, 150, "Weighted: traffic = 70 / (70+20+10).\nWeights need not add to 100. Max 100 weighted\nrecords with the same name and type.\nWeight 0 = no traffic (used only if every\nnonzero record is unhealthy); all 0 = equal.", size=11, align="left")
    d.box("r2", 20, 236, 130, 60, "Route 53", "white", size=12, icon="route53", icon_size=30)
    d.box("pri", 260, 220, 200, 44, "Primary (EC2)", "green", size=11, icon="ec2-instance", icon_size=26)
    d.box("sec", 260, 280, 200, 44, "Secondary (DR)", "gray", size=11, icon="ec2-instance", icon_size=26)
    d.edge("r2", "pri", "healthy?")
    d.edge("r2", "sec", "if primary\nunhealthy", dashed=True)
    d.text("ft", 480, 220, 460, 110, "Failover (active-passive): one primary and one\nsecondary record. Give the primary a health check\n(or Evaluate Target Health on an alias); without it\nRoute 53 assumes it is healthy and never fails over.\nWorks in private hosted zones too.", size=11, align="left")
    d.box("u1", 20, 400, 150, 50, "User in Germany", "white", size=11, icon="users", icon_size=24)
    d.box("u2", 20, 480, 150, 50, "User in India", "white", size=11, icon="users", icon_size=24)
    d.box("ra", 300, 390, 200, 50, "ALB us-east-1", "green", size=11, icon="alb", icon_size=26)
    d.box("rb", 300, 490, 200, 50, "ALB ap-southeast-1", "green", size=11, icon="alb", icon_size=26)
    d.edge("u1", "ra", "lowest latency")
    d.edge("u2", "rb")
    d.text("lt", 520, 380, 420, 180, "Latency: Route 53 picks the Region with the\nlowest measured latency between the user and AWS\nRegions, not the nearest one. A German user can\nget a US Region. Latency data changes over time.\nAdd health checks for failover.", size=11, align="left")
    return d


def r53_routing_examples_2():
    d = Diagram("r53-07-geo-ip-multivalue", 960, 620, "Geolocation, geoproximity, IP-based and multivalue routing")
    d.group("geo", 20, 46, 450, 270, "Geolocation (where the USER is)", "yellow")
    d.box("g1", 40, 84, 200, 44, "Country: Germany\nA 11.22.33.44", "white", size=10)
    d.box("g2", 250, 84, 200, 44, "Continent: Europe\nA 55.66.77.88", "white", size=10)
    d.box("g3", 40, 138, 200, 44, "US state: California\nA 22.33.44.55", "white", size=10)
    d.box("g4", 250, 138, 200, 44, "Default (*)\nA 99.11.22.33", "white", size=10)
    d.text("gt", 30, 190, 430, 124, "German user → Germany record (smallest region wins\nover Europe). No match and no Default → \"no answer\".\nDefault also catches IPs not mapped to a location.\nUse: localization, distribution rights, sticky\nper-location load balancing. Public + private zones.", size=10, align="left")
    d.group("gp", 490, 46, 450, 270, "Geoproximity (distance user ↔ RESOURCE)", "orange")
    d.box("gp1", 510, 84, 200, 50, "us-west-1\nbias 0", "white", size=10, icon="region", icon_size=26)
    d.box("gp2", 720, 84, 200, 50, "us-east-1\nbias +50 (bigger area)", "white", size=10, icon="region", icon_size=26)
    d.text("gpt", 500, 140, 430, 174, "Bias 1 to 99 expands a resource's area (more\ntraffic); -1 to -99 shrinks it (less traffic).\nbiased distance = distance × (1 - bias/100)\nAWS resource: Region or Local Zone Group.\nNon-AWS: latitude and longitude.\nSince Jan 2024: in the normal console/API;\nTraffic Flow needed only for the visual maps.", size=10, align="left")
    d.group("ip", 20, 332, 450, 270, "IP-based (the client's IP range)", "purple")
    d.box("cidr", 40, 370, 410, 70, "CIDR collection\nlocation-1: 203.0.113.0/24 → record 1.2.3.4\nlocation-2: 200.5.4.0/24 → record 5.6.7.8", "white", size=10, align="left")
    d.text("ipt", 30, 446, 430, 154, "User 203.0.113.56 → 1.2.3.4; user 200.5.4.100 → 5.6.7.8.\nIPv4 prefixes /1-/24, IPv6 /1-/48; \"*\" = default\nlocation (0.0.0.0/0, ::/0). Use: send an ISP's users\nto one endpoint, optimise performance, cut network\ntransit cost, override geolocation.\nNot allowed in private hosted zones.", size=10, align="left")
    d.group("mv", 490, 332, 450, 270, "Multivalue answer", "gray")
    d.box("mv0", 510, 370, 120, 50, "Route 53", "white", size=11, icon="route53", icon_size=26)
    for i in range(3):
        d.box(f"mv{i + 1}", 700, 364 + i * 40, 220, 34, f"A 10.0.0.{i + 1}  + health check", "white", size=10)
        d.edge("mv0", f"mv{i + 1}")
    d.text("mvt", 500, 486, 430, 114, "Returns up to 8 healthy records, picked at random;\nclient chooses one. No health check = always healthy.\nAll unhealthy → up to 8 unhealthy records returned.\nNot a substitute for an ELB · no alias records.", size=10, align="left")
    return d


ROUTE53 = [r53_dns_resolution, r53_records_zones, r53_cname_alias, r53_health_checks,
           r53_policies_overview, r53_routing_examples_1, r53_routing_examples_2]


ALL = [iam_big_picture, policy_anatomy, policy_evaluation, access_methods, role_assume, mfa_password,
       security_tools, shared_responsibility,
       global_infra,
       ec2_instance_types, ec2_security_groups, ec2_purchase_options, ec2_spot,
       ec2_ips, placement_groups, eni_hibernate,
       storage_compare, ebs_snapshots_ami, ebs_volume_types, efs_classes,
       elb_types, alb_flow, asg,
       rds_replicas_multiaz, aurora, rds_backup_proxy, elasticache] + ROUTE53

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
