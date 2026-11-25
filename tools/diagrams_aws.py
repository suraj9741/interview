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


# ---------------------------------------------------------------- S3 (09-s3.md)
def s3_big_picture():
    d = Diagram("s3-01-buckets-objects", 960, 600, "Amazon S3: buckets live in a Region, objects live in buckets")
    d.group("reg", 20, 46, 560, 330, "Region: eu-west-1 (a bucket is created in ONE Region)", "white", icon="region", align="left")
    d.box("b", 40, 92, 520, 52, "Bucket: my-bucket\nglobal-looking service, regional bucket", "green", size=11, icon="s3-bucket", icon_size=32)
    d.box("o1", 40, 160, 520, 44, "Key: my_file.txt   →   s3://my-bucket/my_file.txt", "white", size=11, icon="s3-object", icon_size=26)
    d.box("o2", 40, 214, 520, 62, "Key: my_folder/another_folder/my_file.txt\nprefix = my_folder/another_folder/  +  object name = my_file.txt\n(no real folders: the key is the FULL path)", "white", size=10, icon="s3-object", icon_size=26)
    d.text("ob", 40, 284, 520, 88, "Each object: value (body, max 50 TB since Dec 2025, was 5 TB) · metadata\n(system + user key/value) · tags (up to 10, Unicode) · version ID (if versioning on)\nSingle PUT up to 5 GB → bigger needs multipart upload (recommended > 100 MB)", size=10, align="left")
    d.group("nm", 600, 46, 340, 330, "Bucket names", "yellow")
    d.text("nmt", 610, 76, 320, 296, "Shared global namespace (default):\nunique across ALL accounts and Regions\n(in the partition)\n\nAccount regional namespace (Mar 2026):\nname ends -<accountId>-<region>-an,\nonly your account can create it, so the\nsame prefix can be \"reused\" per Region\n\n3-63 chars · lowercase, digits, . and -\nstart/end with letter or digit\nnot an IP · no uppercase, no underscore\nno prefix xn--, sthree-, amzn-s3-demo-\nno suffix -s3alias, --ol-s3, .mrap,\n--x-s3, --table-s3", size=10, align="left")
    d.text("uh", 20, 386, 920, 24, "Use cases", size=13, bold=True)
    uses = ["Backup and\nstorage", "Disaster\nrecovery", "Archive", "Hybrid cloud\nstorage", "Application\nhosting", "Media\nhosting",
            "Data lakes,\nanalytics", "Software\ndelivery", "Static\nwebsite"]
    for i, u in enumerate(uses):
        d.box(f"u{i}", 20 + i * 103, 414, 96, 52, u, "blue", size=10, bold_first=False)
    d.box("ex", 20, 482, 920, 100,
          "Exam reminders\n• \"One of the main building blocks of AWS\": object storage. Objects, not files or blocks (no mounting; you replace an object to change it).\n"
          "• Bucket names: lowercase, globally unique unless you choose the account regional namespace. The name cannot be changed later.\n"
          "• Max object 50 TB (older questions say 5 TB). Multipart: up to 10,000 parts, 5 MiB-5 GiB each (last part can be smaller).\n"
          "• Tags (10 per object, key 128 / value 256 Unicode chars) drive lifecycle rules and IAM conditions; metadata is set at upload.", "orange", size=11, align="left")
    return d


def s3_security():
    d = Diagram("s3-02-security", 960, 550, "S3 security: who can access an object?")
    d.group("ub", 20, 46, 300, 180, "User-based", "blue")
    d.box("iam", 40, 84, 260, 60, "IAM policies\nwhich API calls a user/role\nmay make", "white", size=10, icon="iam-permissions", icon_size=28)
    d.box("role", 40, 154, 260, 56, "EC2 instance → IAM role\n(the right way for AWS services)", "white", size=10, icon="iam-role", icon_size=28)
    d.group("rb", 340, 46, 600, 180, "Resource-based", "orange")
    d.box("bp", 360, 84, 270, 60, "Bucket policy (JSON)\nbucket-wide rules, allows\ncross-account and public", "white", size=10, icon="s3-bucket", icon_size=28)
    d.box("acl", 650, 84, 270, 60, "Object ACL / Bucket ACL\nfiner grain / less common\nDISABLED by default (Apr 2023)", "white", size=10)
    d.box("bpa", 360, 154, 560, 56, "Block Public Access: ON by default for new buckets (can be set at account level too).\nLeave it on unless the bucket must be public (e.g. static website).", "red", size=10, align="left")
    d.box("rule", 20, 240, 920, 76,
          "Decision rule (same account)\nAn IAM principal can access an object if (its IAM policy ALLOWS it  OR  the resource policy ALLOWS it)  AND  there is no explicit DENY.\n"
          "Cross-account: the bucket policy must allow the other account AND that account's IAM policy must allow its user.", "yellow", size=11, align="left")
    lines = ["{", "  \"Version\": \"2012-10-17\",", "  \"Statement\": [", "    {", "      \"Sid\": \"PublicRead\",",
             "      \"Effect\": \"Allow\",", "      \"Principal\": \"*\",", "      \"Action\": [\"s3:GetObject\"],",
             "      \"Resource\": [\"arn:aws:s3:::examplebucket/*\"]", "    }", "  ]", "}"]
    d.box("json", 20, 332, 460, 200, "\n".join(l.replace(" ", " ") for l in lines), "gray", size=11, align="left", bold_first=False)
    d.text("jt", 500, 332, 440, 200,
           "Bucket policy parts\n• Resource: bucket and/or objects (arn:aws:s3:::bucket/*)\n• Effect: Allow / Deny\n• Action: set of APIs to allow or deny\n"
           "• Principal: the account or user it applies to (\"*\" = anyone)\n\nUse a bucket policy to:\n• grant public access to the bucket\n• force objects to be encrypted at upload\n"
           "• grant access to another account (cross-account)\n\nYour notes had \"version\" and \"Principle\": the keys are\n\"Version\" and \"Principal\" (case and spelling matter).", size=11, align="left")
    return d


def s3_versioning_replication():
    d = Diagram("s3-03-versioning-replication", 960, 570, "Versioning and replication (CRR / SRR)")
    d.group("v", 20, 46, 420, 300, "Versioning (bucket level)", "green")
    for i, (lab, col) in enumerate([("version 1  (first upload)", "white"), ("version 2  (same key overwritten)", "white"), ("version 3  (latest)", "green")]):
        d.box(f"v{i}", 40, 84 + i * 48, 380, 40, f"my-file.docx  {lab}", col, size=10, icon="s3-object", icon_size=24)
    d.text("vt", 30, 232, 400, 112, "• Protects against unintended deletes (DELETE adds a\n  delete marker; old versions stay) · easy rollback\n• Objects from before versioning have version ID null\n• Suspending keeps old versions; you can never go back\n  to \"unversioned\" · best practice: turn it on", size=10, align="left")
    d.group("r", 460, 46, 480, 300, "Replication (asynchronous)", "blue")
    d.box("src", 480, 90, 170, 56, "Source bucket\neu-west-1", "white", size=10, icon="s3-bucket", icon_size=26)
    d.box("crr", 750, 82, 170, 56, "Target (CRR)\nus-east-2", "white", size=10, icon="s3-bucket", icon_size=26)
    d.box("srr", 750, 150, 170, 56, "Target (SRR)\neu-west-1", "white", size=10, icon="s3-bucket", icon_size=26)
    d.edge("src", "crr", "CRR")
    d.edge("src", "srr", "SRR")
    d.text("rt", 470, 214, 460, 130, "• Versioning ON in source AND destination · IAM role for S3\n• Buckets can be in different accounts\n• CRR: compliance, lower latency, cross-account copies\n• SRR: log aggregation, live prod → test replication\n• Only NEW objects after you enable it; existing and\n  failed ones → S3 Batch Replication", size=10, align="left")
    d.box("b1", 20, 366, 170, 50, "Bucket 1", "white", size=11, icon="s3-bucket", icon_size=26)
    d.box("b2", 260, 366, 170, 50, "Bucket 2", "white", size=11, icon="s3-bucket", icon_size=26)
    d.box("b3", 500, 366, 170, 50, "Bucket 3", "white", size=11, icon="s3-bucket", icon_size=26)
    d.edge("b1", "b2", "replicates")
    d.edge("b2", "b3", "replicates")
    d.text("ch", 680, 360, 260, 64, "No chaining: objects made in bucket 1\ndo NOT reach bucket 3 (replicas are\nnot replicated again by default)", size=10, align="left")
    d.box("del", 20, 436, 920, 116,
          "DELETE operations and replication\n• Delete markers: replicated only if you turn on the optional \"delete marker replication\" setting.\n"
          "• DELETE with a version ID (permanent delete of a version): never replicated, to avoid malicious deletes.\n"
          "• Types are CRR (different Regions) and SRR (same Region). \"Batch\" is not a third type: S3 Batch Replication is how you copy\n  objects that existed before the rule, objects that failed, or replicas (on demand, as a Batch Operations job).\n"
          "• SRR has no data transfer charge; CRR pays inter-Region transfer.", "orange", size=11, align="left")
    return d


def s3_storage_classes():
    d = Diagram("s3-04-storage-classes", 960, 600, "Storage classes: all 11 nines durable; they differ in availability, minimum days and retrieval")
    rows = [
        ("s3-bucket", "S3 Standard", "99.99%", "none", "ms", "frequent access · ≥3 AZs, survives an AZ loss", "green"),
        ("s3-intelligent-tiering", "Intelligent-Tiering", "99.9%", "none", "ms*", "unknown pattern · auto tiers · monitoring fee, no retrieval fee", "blue"),
        ("s3-standard-ia", "Standard-IA", "99.9%", "30 days", "ms", "infrequent but fast · DR, backups · retrieval fee", "blue"),
        ("s3-onezone-ia", "One Zone-IA", "99.5%", "30 days", "ms", "ONE AZ: data lost if the AZ is destroyed · re-creatable copies", "yellow"),
        ("s3-glacier-ir", "Glacier Instant Retrieval", "99.9%", "90 days", "ms", "archive read about once a quarter", "purple"),
        ("s3-glacier-fr", "Glacier Flexible Retrieval", "99.99%**", "90 days", "1 min-12 h", "Expedited 1-5 min · Standard 3-5 h · Bulk 5-12 h (free)", "purple"),
        ("s3-glacier-da", "Glacier Deep Archive", "99.99%**", "180 days", "12-48 h", "Standard within 12 h · Bulk within 48 h · cheapest, long-term", "gray"),
    ]
    hx = [20, 260, 360, 450, 550, 640]
    for x, h in zip(hx, ["Class", "Availability", "Min duration", "First byte", "Use / retrieval"]):
        d.text(f"h{x}", x, 46, 240 if x == 20 else (390 if x == 550 else 100), 24, h, size=12, bold=True, align="left")
    for i, (ic, name, av, mn, fb, use, col) in enumerate(rows):
        y = 74 + i * 56
        d.box(f"c{i}", 20, y, 230, 48, name, col, size=11, bold=True, icon=ic, icon_size=30)
        d.box(f"a{i}", 260, y, 90, 48, av, "white", size=11)
        d.box(f"m{i}", 360, y, 80, 48, mn, "white", size=11)
        d.box(f"f{i}", 450, y, 90, 48, fb, "white", size=11)
        d.box(f"u{i}", 550, y, 390, 48, use, "white", size=10, align="left")
    d.box("note", 20, 474, 920, 110,
          "Durability vs availability\n• Durability 99.999999999% (11 nines) for every class: store 10,000,000 objects → expect to lose one about every 10,000 years (course figure).\n"
          "• Availability = how readily the data can be read; it varies by class (table). * Intelligent-Tiering optional archive tiers take hours.\n"
          "• ** Glacier Flexible / Deep Archive: availability applies after you restore the object. Min billable size 128 KB (IA classes, Glacier IR).\n"
          "• Glacier classes = storage price + retrieval cost. Move between classes manually or with lifecycle rules.\n"
          "• Standard \"sustains 2 concurrent facility failures\" is the course wording; the docs say resilient to the loss of an entire AZ.", "orange", size=11, align="left")
    return d


def s3_lifecycle_it():
    d = Diagram("s3-05-lifecycle-tiering", 960, 490, "Lifecycle rules and S3 Intelligent-Tiering")
    d.text("lh", 20, 44, 920, 24, "Lifecycle rule example (filter by prefix, tags or object size)", size=13, bold=True, align="left")
    steps = [("s3-bucket", "Day 0\nS3 Standard", "green"), ("s3-standard-ia", "Day 60\nStandard-IA", "blue"),
             ("s3-glacier-fr", "Day 180\nGlacier Flexible", "purple"), ("s3-object", "Day 365\nexpire (delete)", "red")]
    for i, (ic, lab, col) in enumerate(steps):
        d.box(f"l{i}", 20 + i * 240, 74, 190, 56, lab, col, size=11, icon=ic, icon_size=30)
        if i:
            d.edge(f"l{i - 1}", f"l{i}", "transition" if i < 3 else "expiration")
    d.text("lt", 20, 136, 920, 80,
           "• Transition actions: move objects to another class (e.g. Standard-IA 60 days after creation, Glacier for archiving after 6 months).\n"
           "• Expiration actions: delete after a time (e.g. access log files after 365 days), plus old versions (noncurrent) and incomplete multipart uploads.\n"
           "• Rules can target a prefix, object tags, or object size. Since Jul 2026 objects can move to Standard-IA / One Zone-IA from day 0\n  (the old 30-day wait is gone). Objects under 128 KB don't transition by default.", size=11, align="left")
    d.group("it", 20, 226, 920, 250, "S3 Intelligent-Tiering: moves each object by its own access pattern", "blue", icon="s3-intelligent-tiering")
    tiers = [("Frequent Access", "default tier\n(automatic)", "green"), ("Infrequent Access", "not accessed\n30 days (auto)", "blue"),
             ("Archive Instant", "not accessed\n90 days (auto)", "purple"), ("Archive Access", "optional: 90 to\n730 days", "gray"),
             ("Deep Archive Access", "optional: 180 to\n730 days", "gray")]
    for i, (h, b, col) in enumerate(tiers):
        d.box(f"t{i}", 40 + i * 180, 266, 160, 70, f"{h}\n{b}", col, size=10)
        if i:
            d.edge(f"t{i - 1}", f"t{i}")
    d.text("itt", 40, 344, 880, 128,
           "• Small monthly monitoring and auto-tiering fee per object · NO retrieval charges · no minimum storage duration.\n"
           "• Accessing an object in an infrequent / archive-instant tier moves it back to Frequent Access automatically.\n"
           "• Archive Access (3-5 h) and Deep Archive Access (within 12 h) must be switched on (opt-in) and need a restore.\n"
           "• Your notes said \"700+ days\": the docs give a maximum of 730 days for both optional tiers.\n"
           "• Objects under 128 KB are not monitored and always stay in Frequent Access (no monitoring fee).", size=11, align="left")
    return d


def s3_events():
    d = Diagram("s3-06-event-notifications", 960, 510, "S3 event notifications: direct targets or EventBridge")
    d.box("s3", 20, 150, 170, 70, "S3 bucket\nevents: Created,\nRemoved, Restore,\nReplication...", "white", size=10, icon="s3", icon_size=30)
    tg = [("sns", "SNS topic", 60), ("sqs", "SQS queue\n(standard, not FIFO)", 130), ("lambda", "Lambda function", 200)]
    for ic, lab, y in tg:
        d.box(f"t-{ic}", 330, y, 210, 56, lab, "white", size=10, icon=ic, icon_size=30)
        d.edge("s3", f"t-{ic}")
    d.text("pol", 560, 60, 380, 200,
           "Permissions are RESOURCE policies on the target:\n• SNS resource (access) policy\n• SQS resource (access) policy\n• Lambda resource policy (permission to invoke)\n"
           "One policy per destination, allowing S3 to push.\nNot an IAM role on S3.\n\nFilter by name, e.g. suffix .jpg (prefix / suffix).\nAs many events as you want; typically delivered\nin seconds, sometimes a minute or longer.", size=10, align="left")
    d.box("eb", 330, 300, 210, 60, "Amazon EventBridge\nALL events → rules", "white", size=10, icon="eventbridge", icon_size=30)
    d.edge("s3", "eb", "all events")
    d.box("ebt", 640, 300, 300, 60, "Over 18 AWS services as targets\n(Step Functions, Kinesis Streams / Firehose...)", "purple", size=10)
    d.edge("eb", "ebt", "rules")
    d.box("ebx", 20, 390, 920, 100,
          "Why EventBridge\n• Advanced filtering with JSON rules (metadata, object size, name...).  • Multiple destinations per event.\n"
          "• EventBridge capabilities: archive, replay events, reliable delivery.\n"
          "• Turn it on once per bucket: every S3 event goes to EventBridge (you don't pick event types on the S3 side).\n"
          "• Direct S3 notifications: one destination type per notification configuration; SQS FIFO and SNS FIFO are NOT supported targets.", "yellow", size=11, align="left")
    return d


def s3_performance():
    d = Diagram("s3-07-performance-batch", 960, 640, "Performance, Batch Operations and Storage Lens")
    d.group("pf", 20, 46, 450, 310, "Baseline performance (per prefix)", "green")
    for i, p in enumerate(["bucket/folder1/sub1/file", "bucket/folder1/sub2/file", "bucket/1/file", "bucket/2/file"]):
        d.box(f"p{i}", 40, 84 + i * 42, 410, 34, p, "white", size=10, icon="s3-object", icon_size=22)
    d.text("pt", 30, 254, 430, 100, "Each prefix: at least 3,500 PUT/COPY/POST/DELETE and\n5,500 GET/HEAD per second (course) · docs now say\n11,000 GET/HEAD · latency ~100-200 ms · no limit on\nprefixes: 4 prefixes → 4 × the rate", size=10, align="left")
    d.group("up", 490, 46, 450, 310, "Faster uploads and downloads", "blue")
    d.box("mp", 510, 80, 410, 56, "Multipart upload\nrecommended > 100 MB, must > 5 GB · parallel parts", "white", size=10, icon="s3-bucket-objects", icon_size=28)
    d.box("ta", 510, 146, 410, 70, "Transfer Acceleration\nfile → nearby edge location → AWS private network\n→ bucket in the target Region · works with multipart", "white", size=10, icon="edge-location", icon_size=28)
    d.box("br", 510, 226, 410, 70, "Byte-range fetches\nparallel GETs of byte ranges · retry only a failed range\nspeed up downloads or read only part (file head)", "white", size=10, icon="s3-object", icon_size=28)
    d.group("bo", 20, 372, 450, 250, "S3 Batch Operations", "purple", icon="s3-batch-ops")
    d.box("inv", 40, 410, 120, 50, "S3 Inventory\n(object list)", "white", size=10)
    d.box("ath", 180, 410, 120, 50, "Athena\nquery, filter", "white", size=10, icon="athena", icon_size=24)
    d.box("job", 320, 410, 130, 50, "Batch job\n(one operation)", "white", size=10)
    d.edge("inv", "ath")
    d.edge("ath", "job")
    d.text("bot", 30, 466, 430, 154, "Job = list of objects (manifest) + action + optional params\nCopy · modify metadata/tags · replace ACLs · restore from\nGlacier · invoke Lambda per object · Object Lock settings\n(un-encrypted → encrypted: copy / update encryption)\nS3 manages retries, tracks progress, notifies, reports", size=10, align="left")
    d.group("sl", 490, 372, 450, 250, "S3 Storage Lens", "orange", icon="s3-storage-lens")
    d.text("slt", 500, 406, 430, 214, "Org-wide view: Organization, accounts, Regions,\nbuckets, prefixes · default or custom dashboards\ndaily export to a bucket (CSV / Parquet)\n\nFree: summary, cost-optimization, data-protection,\naccess-management, event, performance metrics,\nqueryable 14 days\nAdvanced (paid): + activity, detailed status codes,\nadvanced cost / protection, CloudWatch publishing,\nprefix aggregation, queryable 15 months", size=10, align="left")
    return d


def s3_encryption():
    d = Diagram("s3-08-encryption", 960, 610, "Object encryption: who holds the key, and which header")
    rows = [
        ("SSE-S3 (default)", "kms-data-key", "Key owned and managed by S3 · AES-256 (GCM)\nON by default for new objects since 5 Jan 2023", "x-amz-server-side-encryption: AES256", "green"),
        ("SSE-KMS", "kms", "Key in AWS KMS: you control it, CloudTrail audits use\nupload → GenerateDataKey, download → Decrypt (KMS quota!)", "x-amz-server-side-encryption: aws:kms", "blue"),
        ("DSSE-KMS", "kms", "Two layers: KMS data key, then a separate S3 AES-256 key\ncompliance needing multi-layer · more cost and latency", "x-amz-server-side-encryption: aws:kms:dsse", "purple"),
        ("SSE-C", "encrypted-data", "Customer key outside AWS · S3 never stores it\nkey sent in headers on EVERY request · HTTPS only", "x-amz-server-side-encryption-customer-*", "yellow"),
        ("Client-side", "user", "Client encrypts before upload, decrypts after download\nAmazon S3 Encryption Client · customer runs everything", "(none: S3 receives ciphertext)", "gray"),
    ]
    for i, (name, ic, desc, hdr, col) in enumerate(rows):
        y = 50 + i * 76
        d.box(f"n{i}", 20, y, 200, 66, name, col, size=12, bold=True, icon=ic, icon_size=30)
        d.box(f"d{i}", 230, y, 410, 66, desc, "white", size=10, align="left", bold_first=False)
        d.box(f"h{i}", 650, y, 290, 66, hdr, "white", size=10)
    d.box("tr", 20, 438, 450, 150,
          "In transit (SSL/TLS)\n• S3 has an HTTP endpoint (not encrypted) and an\n  HTTPS endpoint (encryption in flight)\n• HTTPS recommended; mandatory for SSE-C\n  (and for requests on SSE-KMS objects)\n"
          "• Force it: bucket policy Deny when\n  \"aws:SecureTransport\": \"false\"", "blue", size=11, align="left")
    d.box("pol", 490, 438, 450, 150,
          "Default encryption vs bucket policies\n• Default encryption (SSE-S3, or your choice of\n  SSE-KMS / DSSE-KMS) applies to new objects\n• A bucket policy can REFUSE any PutObject without\n  the right encryption header ('force encryption')\n"
          "• Bucket policies are evaluated before default encryption\n• SSE-C is disabled by default on new buckets (Apr 2026)", "orange", size=11, align="left")
    return d


def s3_protection():
    d = Diagram("s3-09-protect-share", 960, 600, "Protect and share: MFA Delete, access logs, pre-signed URLs, WORM locks")
    d.group("mfa", 20, 46, 450, 160, "MFA Delete", "red", icon="iam-mfa")
    d.text("mfat", 30, 74, 430, 130, "MFA code required to:\n• permanently delete an object version\n• change the versioning state (suspend versioning)\nNOT needed to: enable versioning, list deleted versions\n"
           "Versioning must be enabled · only the bucket owner\n(root account) can enable/disable it · CLI/API only,\nnot the console · can't be used with lifecycle rules", size=10, align="left")
    d.group("log", 490, 46, 450, 160, "S3 server access logs", "gray")
    d.box("mb", 510, 80, 170, 46, "Monitored bucket", "white", size=10, icon="s3-bucket", icon_size=26)
    d.box("lb", 750, 80, 170, 46, "Logging bucket", "white", size=10, icon="s3-bucket", icon_size=26)
    d.edge("mb", "lb", "every request")
    d.text("logt", 500, 130, 430, 74, "Any request, any account, allowed or denied · analyse with\nAthena etc. · logging bucket in the SAME Region (and account)\nbest-effort delivery\nNever log a bucket into itself: logging loop, grows forever", size=10, align="left")
    d.group("ps", 20, 222, 450, 176, "Pre-signed URLs", "blue")
    d.box("u", 40, 256, 120, 44, "Signed-in\nuser / app", "white", size=10, icon="user", icon_size=24)
    d.box("url", 190, 256, 120, 44, "pre-signed\nURL", "white", size=10)
    d.box("v", 340, 256, 110, 44, "any holder\nof the URL", "white", size=10, icon="users", icon_size=22)
    d.edge("u", "url")
    d.edge("url", "v")
    d.text("pst", 30, 304, 430, 90, "Console: 1 min to 720 min (12 h) · CLI --expires-in seconds\n(default 3600, max 604800 = 7 days) · never longer than the\nsigner's credentials · holder gets the SIGNER's rights for GET/PUT\ne.g. premium video download, ever-changing list of users", size=10, align="left")
    d.group("wl", 490, 222, 450, 360, "WORM: write once, read many", "purple")
    d.box("vl", 510, 256, 410, 66, "Glacier Vault Lock (legacy vaults)\nvault lock policy → lock it: can no longer be changed\nor deleted · compliance, retention", "white", size=10, icon="glacier-vault", icon_size=28)
    d.box("ol", 510, 332, 410, 236, "S3 Object Lock (versioning required)\nblocks deleting an object VERSION for a set time\n\nCompliance mode: nobody, not even root, can overwrite\nor delete; mode can't change, period can't be shortened\n\nGovernance mode: most users can't; users with\ns3:BypassGovernanceRetention can change or delete\n\nRetention period: fixed time, can be extended\nLegal hold: indefinite, independent of retention;\nplace/remove with s3:PutObjectLegalHold", "white", size=10, align="left", icon="s3-object-lock", icon_size=28, valign="top")
    d.box("rp", 20, 414, 450, 168,
          "Requester Pays\n• Normally the bucket owner pays storage + requests\n  + data transfer.\n• Requester Pays: the REQUESTER pays the request\n  and the download; the owner still pays storage.\n"
          "• Requester must be authenticated in AWS (no\n  anonymous access) and send x-amz-request-payer.", "yellow", size=11, align="left")
    return d


def s3_access_points():
    d = Diagram("s3-10-access-points-lambda", 960, 640, "Access points, Multi-Region Access Points and Object Lambda")
    d.group("ap", 20, 46, 450, 330, "S3 Access Points (one bucket, many doors)", "blue")
    d.box("bk", 40, 300, 410, 52, "Bucket: finance/ sales/ analytics/\nbucket policy delegates to access points", "white", size=10, icon="s3-bucket", icon_size=28)
    aps = [("Finance AP\nfinance/*", "s3-access-points"), ("Sales AP\nsales/*", "s3-access-points"), ("Analytics AP\nVPC origin", "s3-vpc-access-points")]
    for i, (lab, ic) in enumerate(aps):
        d.box(f"a{i}", 40 + i * 140, 200, 130, 60, lab, "white", size=10, icon=ic, icon_size=26)
        d.edge(f"a{i}", "bk")
    d.text("apt", 30, 80, 430, 116, "Each access point has its own DNS name (Internet or VPC\norigin) and its own access point policy (like a bucket\npolicy) → manage security at scale, per team / prefix.\nVPC origin: reachable only from that VPC, through a\nVPC endpoint (gateway or interface) whose endpoint\npolicy allows BOTH the access point and the bucket.", size=10, align="left")
    d.group("mr", 490, 46, 450, 330, "Multi-Region Access Point", "green", icon="s3-mrap")
    d.box("ge", 610, 86, 210, 44, "one global endpoint", "white", size=11)
    d.box("m1", 510, 200, 160, 52, "Bucket us-east-1", "white", size=10, icon="s3-bucket", icon_size=26)
    d.box("m2", 760, 200, 160, 52, "Bucket ap-south-1", "white", size=10, icon="s3-bucket", icon_size=26)
    d.edge("ge", "m1", "nearest")
    d.edge("ge", "m2")
    d.edge("m1", "m2", "two-way CRR", both=True)
    d.text("mrt", 500, 262, 430, 112, "Routes each request to the closest bucket (lowest latency)\nBi-directional replication rules keep data in sync\nFailover controls: shift traffic between Regions within\nminutes · active-active or active-passive", size=10, align="left")
    d.group("ol", 20, 392, 920, 228, "S3 Object Lambda (closed to new customers since 7 Nov 2025)", "orange", icon="s3-object-lambda")
    d.box("app", 40, 440, 150, 50, "Application", "white", size=10, icon="client", icon_size=24)
    d.box("olap", 240, 440, 200, 50, "Object Lambda\nAccess Point", "white", size=10, icon="s3-object-lambda-ap", icon_size=26)
    d.box("fn", 490, 440, 170, 50, "Lambda function\n(redact, convert)", "white", size=10, icon="lambda-fn", icon_size=26)
    d.box("sap", 710, 440, 210, 50, "S3 Access Point\n→ ONE bucket", "white", size=10, icon="s3-access-points", icon_size=26)
    d.edge("app", "olap", "GET")
    d.edge("olap", "fn")
    d.edge("fn", "sap", "original")
    d.text("olt", 30, 500, 900, 116, "Change the object before the caller gets it, without keeping a second copy. Use cases: redact PII for analytics / non-prod,\n"
           "convert XML → JSON, resize or watermark images per caller. Existing customers can keep using it; AWS adds no new features.\n"
           "For new designs you need another way (e.g. transform in your app or in a Lambda you call yourself).", size=10, align="left")
    return d


S3 = [s3_big_picture, s3_security, s3_versioning_replication, s3_storage_classes, s3_lifecycle_it, s3_events,
      s3_performance, s3_encryption, s3_protection, s3_access_points]


def cf_how_it_works():
    d = Diagram("cf-01-how-it-works", 960, 600, "Amazon CloudFront: a CDN that caches your content at the edge")
    d.box("u1", 20, 70, 150, 50, "User in Mumbai", "white", size=11, icon="users", icon_size=28)
    d.box("u2", 20, 150, 150, 50, "User in São Paulo", "white", size=10, icon="users", icon_size=28)
    d.box("e1", 240, 62, 210, 66, "Edge location (POP)\nMumbai · local cache\nHIT → answer at once", "blue", size=10, icon="edge-location", icon_size=30)
    d.box("e2", 240, 142, 210, 66, "Edge location (POP)\nSão Paulo · local cache\nMISS → ask the next layer", "blue", size=10, icon="edge-location", icon_size=30)
    d.box("rec", 520, 102, 190, 66, "Regional edge cache\n(15 RECs) bigger cache,\nbetween POPs and origin", "purple", size=10)
    d.box("org", 780, 92, 160, 86, "Origin\nS3, ALB, NLB,\nEC2, any HTTP\nserver", "green", size=10, icon="s3-bucket", icon_size=28)
    d.edge("u1", "e1", "GET /beach.jpg")
    d.edge("u2", "e2", "GET /beach.jpg")
    d.edge("e2", "rec", "miss")
    d.edge("rec", "org", "miss: fetch,\nthen cache")
    d.edge("e1", "rec", dashed=True)
    d.text("skip", 470, 190, 470, 44, "PUT, POST, PATCH, OPTIONS, DELETE and dynamic requests skip the REC\nand go from the POP straight to the origin (they are not cached).", size=10, align="left")
    d.box("ttl", 20, 246, 450, 120,
          "TTL: how long a file stays cached\nDefault 24 hours (86,400 s) · minimum 0 s · no maximum.\n"
          "After the TTL, the edge asks the origin again.\nCourse: \"cached for a TTL (maybe a day)\".\nIf you change the origin, CloudFront doesn't know until the TTL\nends → use an invalidation (diagram 5).", "yellow", size=10, align="left")
    d.box("num", 490, 246, 450, 120,
          "Size of the network (aws.amazon.com/cloudfront/features, Nov 2026)\n750+ POPs in 100+ cities, 50+ countries\n"
          "+ 1,140+ embedded POPs (inside ISP networks), 300+ cities\n15 regional edge caches\nCourse: \"hundreds of Points of Presence (edge locations, caches)\"", "white", size=10, align="left")
    d.box("shield", 20, 384, 300, 80, "AWS Shield Standard\nfree, automatic: layer 3/4 DDoS\nprotection on every distribution", "red", size=10, icon="shield", icon_size=30)
    d.box("waf", 340, 384, 300, 80, "AWS WAF (web ACL)\noptional: layer 7 rules\n(SQL injection, rate limits, geo)", "red", size=10, icon="waf", icon_size=30)
    d.box("cf", 660, 384, 280, 80, "Distribution\nxxxx.cloudfront.net or your\ndomain (Route 53 alias)", "blue", size=10, icon="cloudfront", icon_size=30)
    d.box("why", 20, 482, 920, 100,
          "Why use it\n• Improves READ performance: content is cached at the edge, close to users → better user experience, less load on the origin.\n"
          "• Works for static content (images, video, JS/CSS, downloads) AND dynamic content (APIs, whole sites, WebSocket) over HTTP/HTTPS.\n"
          "• DDoS protection because it is worldwide: attacks are absorbed at hundreds of edge locations, with Shield and WAF integration.", "orange", size=11, align="left")
    return d


def cf_origins():
    d = Diagram("cf-02-origins", 960, 620, "CloudFront origins: where the edge fetches content from")
    d.group("g1", 20, 46, 300, 330, "1. S3 bucket", "green")
    d.box("cf1", 40, 84, 260, 46, "CloudFront", "white", size=11, icon="cloudfront", icon_size=28)
    d.box("b1", 40, 190, 260, 50, "Private S3 bucket\n(Block Public Access ON)", "white", size=10, icon="s3-bucket", icon_size=28)
    d.edge("cf1", "b1", "OAC (signed\nrequests)")
    d.text("t1", 30, 246, 280, 126, "• Distribute files and cache them at the edge\n• Upload files to S3 THROUGH CloudFront\n  (PUT/DELETE, works with OAC)\n• Secured with Origin Access Control\n  + a bucket policy that allows\n  cloudfront.amazonaws.com for\n  this distribution ARN only", size=10, align="left")
    d.group("g2", 330, 46, 300, 330, "2. VPC origin (Nov 2024)", "purple")
    d.box("cf2", 350, 84, 260, 46, "CloudFront", "white", size=11, icon="cloudfront", icon_size=28)
    d.group("sub", 350, 160, 260, 110, "Private subnet", "white", icon="private-subnet", size=11)
    d.box("alb2", 360, 192, 76, 66, "ALB", "white", size=10, icon="alb", icon_size=26, valign="top")
    d.box("nlb2", 442, 192, 76, 66, "NLB", "white", size=10, icon="nlb", icon_size=26, valign="top")
    d.box("ec22", 524, 192, 76, 66, "EC2", "white", size=10, icon="ec2-instance", icon_size=26, valign="top")
    d.edge("cf2", "sub", "private path")
    d.text("t2", 340, 276, 280, 96, "• Apps in VPC private subnets: no need\n  to expose them on the internet\n• Private ALB / NLB / EC2 instances\n• No extra cost · cross-account (Nov 2025)\n• Dual-stack IPv6 (Oct 2026)", size=10, align="left")
    d.group("g3", 640, 46, 300, 330, "3. Custom origin (HTTP)", "orange")
    d.box("cf3", 660, 84, 260, 46, "CloudFront", "white", size=11, icon="cloudfront", icon_size=28)
    d.box("web", 660, 166, 125, 66, "S3 website\nendpoint", "white", size=10)
    d.box("pub", 795, 166, 125, 66, "Public ALB /\nEC2 / any\nHTTP server", "white", size=10)
    d.edge("cf3", "web")
    d.edge("cf3", "pub")
    d.text("t3", 650, 240, 280, 132, "• S3 website: first enable static\n  website hosting on the bucket;\n  it is a custom origin, so NO OAC\n  (bucket must be public)\n• Any public HTTP backend you want\n• Also: API Gateway, Lambda function\n  URL, MediaPackage, MediaStore", size=10, align="left")
    d.text("oh", 20, 386, 920, 24, "OAC vs OAI (how CloudFront proves itself to a private S3 bucket)", size=13, bold=True, align="left")
    rows = [("", "Origin Access Control (OAC)", "Origin Access Identity (OAI)"),
            ("Status", "recommended (current)", "legacy, not recommended"),
            ("SSE-KMS objects", "yes", "no"),
            ("All Regions (opt-in, after 2022)", "yes", "no"),
            ("Writes (PUT / DELETE)", "yes", "no"),
            ("Bucket policy Principal", "Service: cloudfront.amazonaws.com + AWS:SourceArn", "the OAI's IAM user ARN")]
    for i, (a, b, c) in enumerate(rows):
        y = 414 + i * 32
        hdr = i == 0
        d.box(f"oa{i}", 20, y, 260, 30, a, "gray", size=10, bold=True)
        d.box(f"ob{i}", 284, y, 380, 30, b, "green" if hdr else "white", size=10, bold=hdr)
        d.box(f"oc{i}", 668, y, 272, 30, c, "red" if hdr else "white", size=10, bold=hdr)
    return d


def cf_alb_ec2_origin():
    d = Diagram("cf-03-alb-ec2-origin", 960, 560, "ALB or EC2 as an origin: public network vs VPC origins")
    d.group("pub", 20, 46, 450, 380, "Old way: public network", "orange")
    d.box("u", 40, 86, 120, 46, "Users", "white", size=11, icon="users", icon_size=26)
    d.box("e", 190, 86, 260, 46, "Edge location (public IPs)", "white", size=10, icon="edge-location", icon_size=26)
    d.edge("u", "e")
    d.box("ec2p", 40, 180, 190, 70, "EC2 instance\nMUST be public\nSG: allow edge IPs", "white", size=10, icon="ec2-instance", icon_size=26)
    d.box("albp", 260, 180, 190, 70, "ALB\nMUST be public\nSG: allow edge IPs", "white", size=10, icon="alb", icon_size=26)
    d.edge("e", "ec2p", "internet")
    d.edge("e", "albp", "internet")
    d.box("ec2b", 260, 290, 190, 60, "EC2 behind ALB\ncan be private\nSG: allow ALB's SG", "white", size=10, icon="ec2-instance", icon_size=26)
    d.edge("albp", "ec2b")
    d.text("pt", 30, 356, 430, 66, "Edge IPs: AWS-managed prefix list\ncom.amazonaws.global.cloudfront.origin-facing (or ip-ranges.json).\nRisk: the origin still has a public address anyone can try.", size=10, align="left")
    d.group("vpc", 490, 46, 450, 380, "New way: VPC origins (recommended)", "purple")
    d.box("u2", 510, 86, 120, 46, "Users", "white", size=11, icon="users", icon_size=26)
    d.box("cf", 660, 86, 260, 46, "CloudFront + VPC origin", "white", size=10, icon="cloudfront", icon_size=26)
    d.edge("u2", "cf")
    d.group("ps", 510, 168, 410, 120, "VPC · private subnet only", "white", icon="private-subnet", size=11)
    d.box("a", 524, 204, 120, 64, "Private ALB", "white", size=10, icon="alb", icon_size=26)
    d.box("n", 652, 204, 120, 64, "Private NLB", "white", size=10, icon="nlb", icon_size=26)
    d.box("i", 780, 204, 128, 64, "Private EC2", "white", size=10, icon="ec2-instance", icon_size=26)
    d.edge("cf", "ps", "AWS private path")
    d.text("vt", 500, 296, 430, 126, "• No public IP on the origin: only CloudFront can reach it\n• CloudFront creates the security group\n  CloudFront-VPCOrigins-Service-SG (don't edit it)\n• The VPC still needs an internet gateway attached\n  (not used for this traffic)\n• Not supported: Gateway LB, NLB with TLS listener, gRPC", size=10, align="left")
    d.box("ex", 20, 440, 920, 100,
          "Exam pattern\n• \"Serve a private app in private subnets through CloudFront without exposing it\" → VPC origin.\n"
          "• Older questions (before VPC origins): public ALB/EC2 whose security group allows only CloudFront's IP ranges, or a custom header check.\n"
          "• S3 private content → OAC. Private ALB/NLB/EC2 → VPC origin. Public HTTP server → custom origin.", "yellow", size=11, align="left")
    return d


def cf_vs_crr():
    d = Diagram("cf-04-cloudfront-vs-crr", 960, 470, "CloudFront vs S3 Cross-Region Replication: both give low latency, in different ways")
    d.group("cf", 20, 46, 450, 300, "CloudFront (cache)", "blue", icon="cloudfront")
    d.box("o", 160, 86, 170, 46, "1 origin bucket", "white", size=11, icon="s3-bucket", icon_size=26)
    for i, c in enumerate(["Edge", "Edge", "Edge", "Edge"]):
        d.box(f"e{i}", 36 + i * 108, 176, 96, 44, f"{c} {i + 1}", "white", size=10, icon="edge-location", icon_size=22)
        d.edge("o", f"e{i}")
    d.text("ct", 30, 230, 430, 112, "• Global edge network (hundreds of locations)\n• Files are cached for a TTL (maybe a day):\n  users may see an old copy until it expires\n• Great for STATIC content that must be\n  available everywhere", size=11, align="left")
    d.group("cr", 490, 46, 450, 300, "S3 Cross-Region Replication (copy)", "green", icon="s3-replication")
    d.box("s", 520, 86, 170, 46, "Source bucket", "white", size=11, icon="s3-bucket", icon_size=26)
    d.box("t1", 740, 76, 180, 40, "Bucket eu-west-1", "white", size=10, icon="s3-bucket", icon_size=22)
    d.box("t2", 740, 126, 180, 40, "Bucket ap-south-1", "white", size=10, icon="s3-bucket", icon_size=22)
    d.edge("s", "t1")
    d.edge("s", "t2")
    d.text("rt", 500, 176, 430, 166, "• Must be set up for EACH Region you want\n• Files are updated in near real time\n  (asynchronous; with RTC 99.99% in 15 min)\n• Read only (replicas are for reading)\n• Great for DYNAMIC content that needs low\n  latency in a FEW Regions", size=11, align="left")
    d.box("rule", 20, 360, 920, 90,
          "How to choose\n• Everywhere + static + OK to be a bit stale → CloudFront.\n• A few Regions + must be fresh (near real time) → CRR (plus apps in those Regions).\n"
          "• They combine well: CloudFront in front of a bucket that is itself replicated (origin failover with an origin group).", "yellow", size=11, align="left")
    return d


def cf_geo_invalidation():
    d = Diagram("cf-05-geo-invalidation", 960, 600, "Geo restriction and cache invalidation")
    d.group("geo", 20, 46, 450, 330, "Geo restriction (country level)", "orange")
    d.box("al", 40, 84, 200, 70, "Allow list\nonly these countries\nmay access", "green", size=10)
    d.box("bl", 250, 84, 200, 70, "Block list\nthese countries are\nblocked", "red", size=10)
    d.box("v1", 40, 180, 200, 46, "Viewer in allowed country", "white", size=10)
    d.box("v2", 250, 180, 200, 46, "Viewer in blocked country", "white", size=10)
    d.box("ok", 40, 250, 200, 36, "200: content served", "green", size=10)
    d.box("no", 250, 250, 200, 36, "403 Forbidden", "red", size=10)
    d.edge("v1", "ok")
    d.edge("v2", "no")
    d.text("gt", 30, 292, 430, 80, "Country = third-party Geo-IP database (~99.8% accurate);\nunknown location → served. Use case: copyright /\nlicensing laws. Finer than country (city, ZIP)? Use a\nthird-party geolocation service or AWS WAF geo rules.", size=10, align="left")
    d.group("inv", 490, 46, 450, 330, "Cache invalidation", "blue")
    d.box("s3", 510, 84, 150, 50, "Origin: you\nupdate index.html", "white", size=10, icon="s3-bucket", icon_size=24)
    d.box("cf", 760, 84, 160, 50, "CloudFront", "white", size=10, icon="cloudfront", icon_size=24)
    d.edge("s3", "cf", "invalidate\n/index.html, /images/*")
    d.box("ed1", 510, 190, 190, 50, "Edge cache: old copy\nremoved", "white", size=10, icon="edge-location", icon_size=24)
    d.box("ed2", 730, 190, 190, 50, "Regional edge cache:\nold copy removed", "white", size=10)
    d.edge("cf", "ed1")
    d.edge("cf", "ed2")
    d.text("it", 500, 248, 430, 124, "Without it: new content only after the TTL ends.\nInvalidation = force a full or partial refresh,\nbypassing the TTL: all files /* or a path /images/*\n* must be the LAST character of the path\nNext request → edge fetches the fresh copy", size=10, align="left")
    d.box("cost", 20, 392, 920, 190,
          "Invalidation cost and limits (CloudFront docs)\n• First 1,000 invalidation PATHS per month are free (per AWS account, all distributions together); each path after that is charged.\n"
          "• A wildcard path (/images/* or /*) counts as ONE path, even if it removes thousands of files.\n"
          "• In progress at once: up to 3,000 files per distribution, or up to 15 wildcard paths.\n"
          "• Best practice for frequent updates: versioned file names (app.v2.js, logo_2026.png) + long TTL. New name = new cache key, no invalidation\n  needed, no charge, and users never get a mix of old and new files.\n"
          "• Exam: \"users still see the old file after a deploy\" → create an invalidation (or use versioned names).", "yellow", size=11, align="left")
    return d


def ga_anycast():
    d = Diagram("ga-01-anycast-flow", 960, 600, "AWS Global Accelerator: enter the AWS network at the nearest edge, via anycast IPs")
    d.group("old", 20, 46, 450, 250, "Without: public internet all the way", "red")
    d.box("c1", 40, 86, 120, 46, "User India", "white", size=10, icon="client", icon_size=24)
    d.box("h1", 190, 86, 80, 46, "hop", "white", size=10)
    d.box("h2", 280, 86, 80, 46, "hop", "white", size=10)
    d.box("alb1", 300, 150, 160, 60, "Public ALB\nus-east-1", "white", size=10, icon="alb", icon_size=26)
    d.edge("c1", "h1")
    d.edge("h1", "h2")
    d.edge("h2", "alb1", "many hops")
    d.text("ot", 30, 226, 430, 66, "Every ISP hop adds latency, jitter and packet loss.\nClient caches the DNS answer: after a failover it can\nkeep using a dead IP until the TTL ends.", size=10, align="left")
    d.group("ip", 490, 46, 450, 250, "Unicast vs anycast", "gray")
    d.box("uni", 510, 86, 410, 70, "Unicast IP\none server holds one IP address\n(12.34.56.78 → one machine)", "white", size=10)
    d.box("any", 510, 166, 410, 70, "Anycast IP\nALL servers hold the SAME IP address and the\nclient is routed to the NEAREST one", "green", size=10)
    d.text("ipt", 500, 244, 430, 48, "Global Accelerator announces its static IPs\nfrom many AWS edge locations at once.", size=10, align="left")
    d.group("new", 20, 310, 920, 270, "With Global Accelerator", "blue", icon="global-accelerator")
    d.box("c2", 40, 360, 140, 50, "User India", "white", size=10, icon="client", icon_size=24)
    d.box("ips", 220, 350, 200, 70, "2 static anycast IPv4\n(dual-stack: +2 IPv6 = 4)\nor your own IPs (BYOIP)", "yellow", size=10)
    d.box("edge", 480, 350, 170, 70, "Nearest edge\nlocation (Mumbai)\nTCP ends here", "white", size=10, icon="edge-location", icon_size=26)
    d.box("alb2", 720, 350, 200, 70, "ALB / NLB / EC2 / EIP\nus-east-1 (can be\ninternal / private)", "white", size=10, icon="alb", icon_size=26)
    d.edge("c2", "ips")
    d.edge("ips", "edge", "short hop")
    d.edge("edge", "alb2", "AWS private\nglobal network")
    d.text("nt", 40, 430, 880, 146,
           "• Uses the AWS internal network to reach your app: 2 anycast IPs are created → traffic goes to the nearest edge location → the edge sends it to your app.\n"
           "• The edge terminates the client's TCP connection and opens a new one to your endpoint almost at once (faster handshakes).\n"
           "• The IPs stay the same for the life of the accelerator (even if disabled); you lose them only when you delete it. DNS name: xxxx.awsglobalaccelerator.com.\n"
           "• The two IPv4 addresses come from two separate network zones (if one zone fails, the other IP still works).\n"
           "• AWS: up to 60% better performance for TCP and UDP traffic (FAQ). Pricing: fixed hourly fee per accelerator + Data Transfer-Premium per GB.", size=10, align="left")
    return d


def ga_components():
    d = Diagram("ga-02-components-failover", 960, 640, "Global Accelerator parts: listener → endpoint groups (one per Region) → endpoints")
    d.box("acc", 20, 50, 300, 70, "Accelerator (standard)\n2 static IPv4 (or 4 dual-stack)\nhealth checks + failover", "blue", size=10, icon="global-accelerator", icon_size=30)
    d.box("lis", 360, 50, 260, 70, "Listener\nTCP, UDP or both\nport or port range (e.g. 443, 80)", "yellow", size=10)
    d.box("aff", 660, 50, 280, 70, "Client affinity\nNone (default) or Source IP:\nsame user → same endpoint", "white", size=10)
    d.edge("acc", "lis")
    d.edge("lis", "aff", dashed=True)
    d.group("r1", 20, 150, 450, 250, "Endpoint group: us-east-1 · traffic dial 100%", "white", icon="region", align="left", size=11)
    d.box("a1", 40, 196, 200, 56, "ALB (internet-facing\nor internal) · weight 128", "white", size=10, icon="alb", icon_size=26)
    d.box("a2", 250, 196, 200, 56, "EC2 instance\nweight 128", "white", size=10, icon="ec2-instance", icon_size=26)
    d.box("hc1", 40, 266, 410, 50, "Healthy → gets new connections (closest Region, by weight)", "green", size=10)
    d.text("r1t", 40, 324, 410, 72, "Traffic dial 0-100%: share of this Region's traffic\n(e.g. 0% for maintenance, blue/green between Regions).\nWeight 0-255 (default 128): share inside the group.", size=10, align="left")
    d.group("r2", 490, 150, 450, 250, "Endpoint group: eu-west-1 · traffic dial 100%", "white", icon="region", align="left", size=11)
    d.box("b1", 510, 196, 200, 56, "NLB\nweight 128", "white", size=10, icon="nlb", icon_size=26)
    d.box("b2", 720, 196, 200, 56, "Elastic IP\nweight 128", "white", size=10, icon="ec2-eip", icon_size=26)
    d.box("hc2", 510, 266, 410, 50, "Unhealthy → new connections go to the next Region", "red", size=10)
    d.text("r2t", 510, 324, 410, 72, "Failover in under 1 minute (FAQ), no DNS change, so no\nclient DNS cache problem. Existing connections are\nnot moved. All unhealthy → it fails open (routes to all).", size=10, align="left")
    d.edge("lis", "r1")
    d.edge("lis", "r2")
    d.box("hc", 20, 414, 450, 106, "Health checks\nGA checks EC2 / Elastic IP endpoints itself (settings in GA).\nFor ALB / NLB it uses the load balancer's own health checks\n(set in the ELB console). Great for disaster recovery.", "white", size=10, align="left")
    d.box("ipp", 490, 414, 450, 106, "Client IP preservation\nSupported: ALB, EC2, NLB with security groups.\nNot supported: Elastic IP endpoints, NLB without SG.\nDual-stack accelerators need it on every endpoint.", "white", size=10, align="left")
    d.box("sec", 20, 534, 920, 86,
          "Security and types\n• Only 2 IPs for clients to allowlist (firewalls, corporate proxies) · AWS Shield DDoS protection · endpoints can stay internal.\n"
          "• Custom routing accelerator: maps each user to one specific EC2 instance + port in VPC subnets (game sessions); no health checks or failover.", "orange", size=11, align="left")
    return d


def cf_vs_ga():
    d = Diagram("cfga-01-comparison", 960, 640, "CloudFront vs Global Accelerator: same edge network, different jobs")
    d.box("both", 20, 46, 920, 64,
          "Both: use the AWS global network and its edge locations around the world · both integrate with AWS Shield for DDoS protection\n"
          "Both: help global users get low latency to an app in one or more AWS Regions", "gray", size=11, align="left", bold_first=False)
    d.box("hcf", 260, 124, 330, 50, "CloudFront", "blue", size=13, bold=True, icon="cloudfront", icon_size=32)
    d.box("hga", 610, 124, 330, 50, "Global Accelerator", "green", size=13, bold=True, icon="global-accelerator", icon_size=32)
    rows = [
        ("What it is", "CDN: caches content at the edge", "network-layer proxy: packets go over AWS backbone"),
        ("Protocols", "HTTP / HTTPS (and WebSocket)", "any TCP or UDP (HTTP too)"),
        ("Caching", "YES: content served FROM the edge", "NO caching: every request reaches your app"),
        ("Content", "cacheable (images, video) + dynamic (APIs, sites)", "non-HTTP: gaming (UDP), IoT (MQTT), VoIP"),
        ("Entry point", "DNS name (d123.cloudfront.net); IPs change", "2 static anycast IPs (4 dual-stack), BYOIP"),
        ("Failover", "origin groups (per request, origin failover)", "deterministic, fast Regional failover (<1 min)"),
        ("Origins / endpoints", "S3, VPC origins, ALB, NLB, EC2, any HTTP", "ALB, NLB, EC2, Elastic IP (can be internal)"),
        ("Extras", "WAF, geo restriction, OAC, signed URLs, invalid.", "traffic dials, endpoint weights, client affinity"),
        ("Pricing", "per GB out + per request (or flat-rate plan)", "fixed hourly fee + Data Transfer-Premium per GB"),
    ]
    for i, (k, a, b) in enumerate(rows):
        y = 182 + i * 38
        d.box(f"k{i}", 20, y, 230, 34, k, "gray", size=11, bold=True)
        d.box(f"a{i}", 260, y, 330, 34, a, "white", size=10)
        d.box(f"b{i}", 610, y, 330, 34, b, "white", size=10)
    d.box("pick", 20, 532, 920, 92,
          "Exam keyword → answer\n• \"cache\", \"static content\", \"images/videos worldwide\", \"S3 + edge\", \"geo-block\" → CloudFront.\n"
          "• \"static IP\", \"allowlist IPs\", \"UDP\", \"gaming\", \"IoT/MQTT\", \"VoIP\", \"fast Regional failover without DNS\" → Global Accelerator.\n"
          "• HTTP app that needs fixed IPs or deterministic failover → Global Accelerator (even though it is HTTP).", "yellow", size=11, align="left")
    return d


CLOUDFRONT = [cf_how_it_works, cf_origins, cf_alb_ec2_origin, cf_vs_crr, cf_geo_invalidation, ga_anycast, ga_components, cf_vs_ga]


def sx_comparison():
    d = Diagram("sx-01-storage-comparison", 960, 700, "AWS storage options: pick by data type and who mounts it")
    cols = [("Object", "green", 20), ("Block", "orange", 260), ("File", "blue", 500), ("Hybrid / move data", "purple", 740)]
    for name, col, x in cols:
        d.group(f"g{x}", x, 46, 200, 470, name, col)
    rows = {
        20: [("s3", "S3\nobject storage", "s3"), ("gl", "S3 Glacier classes\nobject archival", "glacier-service")],
        260: [("ebs", "EBS volume\nnetwork storage for ONE\nEC2 instance at a time\n(Multi-Attach: io1/io2)", "ebs"),
              ("is", "Instance store\nphysical disk on host\nhigh IOPS, lost on stop", "ec2-instance")],
        500: [("efs", "EFS\nNFS for Linux, POSIX\nmany instances", "efs"),
              ("fw", "FSx for Windows\nSMB / NTFS, Active Dir.", "fsx-windows"),
              ("fl", "FSx for Lustre\nHPC / ML Linux file\nsystem, S3 linked", "fsx-lustre"),
              ("fo", "FSx for NetApp ONTAP\nNFS+SMB+iSCSI: high\nOS compatibility", "fsx-ontap"),
              ("fz", "FSx for OpenZFS\nmanaged ZFS over NFS", "fsx-openzfs")],
        740: [("sg", "Storage Gateway\nS3 File, Volume\n(cached / stored), Tape\n(FSx File GW: closed\nto new customers)", "storage-gateway"),
              ("tf", "Transfer Family\nSFTP, FTPS, FTP, AS2 on\ntop of S3 or EFS", "transfer-family"),
              ("ds", "DataSync\nscheduled sync on-prem\n/ other cloud → AWS,\nor AWS → AWS", "datasync"),
              ("sn", "Snowball Edge\nphysical move\n(closed to new\ncustomers 7 Nov 2025)", "snowball-edge")],
    }
    for x, items in rows.items():
        h = 440 / len(items) - 10 if len(items) > 2 else 120
        for i, (bid, label, icon) in enumerate(items):
            d.box(bid, x + 8, 80 + i * (h + 10), 184, h, label, "white", size=10, icon=icon, icon_size=28)
    d.box("db", 20, 530, 920, 46, "Databases (RDS, Aurora, DynamoDB, ...): for specific workloads, usually with indexing and querying, not a place to keep files", "gray", size=11, bold_first=False)
    d.box("ex", 20, 590, 920, 94,
          "Exam keyword → answer\n• \"Windows / SMB / NTFS / Active Directory\" → FSx for Windows · \"HPC, ML, Lustre, read S3 as a file system\" → FSx for Lustre\n"
          "• \"NFS + SMB + iSCSI, move NetApp/NAS\" → FSx for ONTAP · \"move ZFS\" → FSx for OpenZFS · \"Linux NFS shared, POSIX\" → EFS\n"
          "• \"on-premises apps see S3 as files/volumes/tapes\" → Storage Gateway · \"partners send files over SFTP\" → Transfer Family · \"scheduled copy\" → DataSync", "yellow", size=10, align="left")
    return d


def sx_snowball():
    d = Diagram("sx-02-snowball", 960, 720, "AWS Snowball: move data physically, or compute at the edge")
    d.box("st", 20, 46, 920, 64,
          "Status (AWS docs, 2026): Snowball Edge closed to NEW customers on 7 Nov 2025 (existing customers keep using it).\n"
          "Snowcone discontinued 12 Nov 2024 · Snowmobile (100 PB truck) retired in 2024.\n"
          "Alternatives: DataSync (online), Data Transfer Terminal (bring your own disks), Outposts (edge compute).",
          "red", size=10, align="left")
    d.group("tt", 20, 124, 450, 220, "Time to transfer over the network (course)", "gray")
    rows = [("", "100 Mbps", "1 Gbps", "10 Gbps"), ("10 TB", "12 days", "30 hours", "3 hours"),
            ("100 TB", "124 days", "12 days", "30 hours"), ("1 PB", "3 years", "124 days", "12 days")]
    for i, r in enumerate(rows):
        for j, c in enumerate(r):
            d.box(f"t{i}{j}", 34 + j * 106, 158 + i * 34, 102, 30, c, "gray" if (i == 0 or j == 0) else "white", size=10, bold=(i == 0 or j == 0))
    d.text("tr", 30, 296, 430, 44, "Rule of thumb: more than a WEEK over the network\n→ use a Snowball device.", size=11, bold=True, align="left")
    d.group("ch", 490, 124, 450, 220, "Why offline? Network challenges", "gray")
    d.text("cht", 500, 158, 430, 180, "• Limited connectivity\n• Limited bandwidth\n• High network cost\n• Shared bandwidth (can't maximise the line)\n• Connection stability\n\nSnowball = highly secure, portable device to collect and\nprocess data at the edge and migrate data INTO and OUT of AWS\n(up to petabytes; 16-node cluster up to 2.6 PB).", size=10, align="left")
    d.group("fl", 20, 358, 920, 120, "Import flow", "green")
    d.box("c", 40, 396, 140, 60, "Data center\n(client)", "white", size=10, icon="corp-dc", icon_size=26)
    d.box("sb", 230, 396, 170, 60, "Snowball Edge\ncopy data locally", "white", size=10, icon="snowball-edge", icon_size=28)
    d.box("ship", 450, 396, 120, 60, "Ship to AWS", "white", size=10)
    d.box("imp", 620, 396, 120, 60, "AWS imports\ninto S3", "white", size=10)
    d.box("b", 790, 396, 130, 60, "S3 bucket", "white", size=10, icon="s3-bucket", icon_size=26)
    d.edge("c", "sb"); d.edge("sb", "ship"); d.edge("ship", "imp"); d.edge("imp", "b")
    d.group("gl", 20, 492, 450, 110, "Snowball into Glacier", "blue")
    d.box("g1", 34, 532, 110, 50, "Snowball", "white", size=10, icon="snowball", icon_size=24)
    d.box("g2", 184, 532, 110, 50, "S3", "white", size=10, icon="s3", icon_size=24)
    d.box("g3", 334, 532, 122, 50, "Glacier class", "white", size=10, icon="glacier-service", icon_size=24)
    d.edge("g1", "g2", "import"); d.edge("g2", "g3", "lifecycle")
    d.group("ed", 490, 492, 450, 110, "Edge computing", "orange")
    d.text("edt", 500, 520, 430, 80, "Process data where it is created: truck, ship, mine underground\n(limited internet, no compute). Run EC2 instances or Lambda\n(IoT Greengrass) on the device. Use: preprocess, ML, transcode.", size=10, align="left")
    rows2 = [("Device (current gen)", "vCPU", "Memory", "Storage"),
             ("Snowball Edge Storage Optimized", "104", "416 GB", "210 TB NVMe"),
             ("Snowball Edge Compute Optimized", "104", "416 GB", "28 TB NVMe")]
    for i, r in enumerate(rows2):
        for j, c in enumerate(r):
            w = 380 if j == 0 else 176
            x = 20 if j == 0 else 400 + (j - 1) * 180
            d.box(f"d{i}{j}", x, 616 + i * 32, w, 30, c, "gray" if i == 0 else "white", size=10, bold=(i == 0))
    return d


def sx_fsx_overview():
    d = Diagram("sx-03-fsx-overview", 960, 560, "Amazon FSx: fully managed third-party high-performance file systems")
    items = [
        ("w", 20, 46, "FSx for Windows File Server", "fsx-windows", "blue",
         "• SMB 2.0-3.1.1, native Windows (NTFS), ACLs, user quotas\n• Microsoft Active Directory integration\n• Linux EC2 can mount it too (cifs-utils)\n• DFS Namespaces: group many file systems\n• Up to 12 GB/s, 350,000 IOPS, 64 TB per FS;\n  hundreds of PB with DFS\n• SSD (latency sensitive: DBs, media, analytics)\n  or HDD (home dirs, CMS)\n• On-prem access over VPN / Direct Connect\n• Single-AZ or Multi-AZ (standby, ~30 s failover)\n• Automatic daily backups to S3 (7 days default)"),
        ("l", 490, 46, "FSx for Lustre", "fsx-lustre", "green",
         "• Parallel distributed FS (Linux + cluster)\n• ML, HPC, video, financial modelling, EDA\n• TB/s throughput, millions of IOPS, sub-ms\n• SSD (small random files) / HDD (large sequential,\n  Persistent 1 only) / Intelligent-Tiering (new)\n• Link S3 buckets: read S3 as files, write results\n  back (data repository associations)\n• On-prem over VPN / Direct Connect\n• Scratch vs Persistent: diagram 4"),
        ("o", 20, 300, "FSx for NetApp ONTAP", "fsx-ontap", "orange",
         "• NFS, SMB, iSCSI (+ NVMe/TCP): high OS compatibility\n• Move ONTAP or NAS workloads to AWS\n• Linux, Windows, macOS, VMware Cloud on AWS,\n  WorkSpaces, AppStream 2.0, EC2, ECS, EKS\n• SSD tier + capacity pool that grows/shrinks\n  automatically\n• Snapshots, SnapMirror replication, compression,\n  deduplication, instant point-in-time clones\n• Single-AZ or Multi-AZ"),
        ("z", 490, 300, "FSx for OpenZFS", "fsx-openzfs", "purple",
         "• Managed OpenZFS, NFS v3, v4.0, v4.1, v4.2 only\n• Move ZFS workloads to AWS\n• Same clients as ONTAP (Linux, Windows, macOS ...)\n• Course: up to 1,000,000 IOPS, < 0.5 ms latency\n  Docs now: up to 2M IOPS (cached), 21 GB/s,\n  hundreds of microseconds\n• Snapshots, compression (LZ4/Zstd), low cost,\n  instant point-in-time clones (test new workloads)\n• Single-AZ (non-HA / HA) or Multi-AZ"),
    ]
    for bid, x, y, title, icon, col, body in items:
        d.box(f"{bid}h", x, y, 450, 44, title, col, size=13, bold=True, icon=icon, icon_size=30)
        d.box(f"{bid}b", x, y + 48, 450, 196, body, "white", size=11, align="left", valign="top", bold_first=False)
    return d


def sx_lustre_deploy():
    d = Diagram("sx-04-fsx-lustre-deployment", 960, 520, "FSx for Lustre deployment options: Scratch vs Persistent")
    for gx, title, col, fs, notes in [
        (20, "Scratch file system", "orange", "FSx for Lustre\n(Scratch)",
         "• Temporary storage, short-term processing\n• Data is NOT replicated: if a file server fails,\n  data is lost (immediate I/O error)\n• High burst: up to 6x the 200 MB/s per TiB baseline\n• No backups · cheapest · Use: optimise costs"),
        (490, "Persistent file system", "green", "FSx for Lustre\n(Persistent 1 / 2)",
         "• Long-term storage and processing, sensitive data\n• SSD/HDD: data replicated within the SAME AZ\n  (Intelligent-Tiering: across AZs)\n• Failed file server replaced within minutes\n• Daily backups to S3 · Persistent 2 = latest gen"),
    ]:
        d.group(f"r{gx}", gx, 46, 450, 330, title, col, icon="region", size=12)
        d.box(f"az1{gx}", gx + 16, 86, 200, 64, "AZ 1: compute\ninstances", "white", size=10, icon="ec2-instances", icon_size=26)
        d.box(f"az2{gx}", gx + 234, 86, 200, 64, "AZ 2: compute\ninstances", "white", size=10, icon="ec2-instances", icon_size=26)
        d.box(f"fs{gx}", gx + 16, 186, 200, 64, fs, "white", size=10, icon="fsx-lustre", icon_size=28)
        d.box(f"s3{gx}", gx + 234, 186, 200, 64, "S3 bucket\n(optional data\nrepository)", "white", size=10, icon="s3-bucket", icon_size=26)
        d.edge(f"az1{gx}", f"fs{gx}", "ENI")
        d.edge(f"az2{gx}", f"fs{gx}")
        d.edge(f"fs{gx}", f"s3{gx}", both=True)
        d.text(f"n{gx}", gx + 10, 262, 430, 110, notes, size=10, align="left")
    d.box("s3i", 20, 390, 920, 110,
          "Seamless S3 integration (both types)\n• Link a bucket with a data repository association: objects appear as files; content is loaded from S3 the first time you open the file.\n"
          "• Write the output of computations back to S3 (automatic export or export tasks).\n"
          "• Throughput per TiB (docs): Scratch 200 · Persistent 2 SSD 125/250/500/1000 · Persistent 1 SSD 50/100/200 · Persistent 1 HDD 12/40 MB/s.\n"
          "• Exam: \"temporary, cheapest, short job\" → Scratch · \"long-running, must survive a server failure\" → Persistent.", "yellow", size=10, align="left")
    return d


def sx_storage_gateway():
    d = Diagram("sx-05-storage-gateway", 960, 700, "AWS Storage Gateway: bridge on-premises apps to cloud storage")
    d.box("why", 20, 46, 920, 60,
          "Hybrid cloud: part on-prem, part AWS (long migrations, security, compliance, IT strategy). S3 is proprietary (not NFS like EFS), so how do on-prem apps use it?\n"
          "Use cases: disaster recovery · backup & restore · tiered storage · on-premises cache & low-latency file access.", "gray", size=10, align="left", bold_first=False)
    d.group("on", 20, 120, 300, 470, "On-premises", "gray", icon=None)
    d.group("aws", 400, 120, 540, 470, "AWS Cloud (HTTPS, Internet or Direct Connect)", "white", icon="region", size=12)
    rows = [
        (150, "NFS / SMB\nfile shares", "S3 File Gateway\nlocal cache: most\nrecently used data", "s3-file-gateway",
         "S3 Standard, Standard-IA, One Zone-IA,\nIntelligent-Tiering (written directly)\n→ Glacier only via lifecycle policy\nIAM role per gateway · SMB + AD auth", "s3-bucket"),
        (290, "iSCSI\napp server", "Volume Gateway\ncached or\nstored volumes", "volume-gateway",
         "Block storage backed by S3, backups as EBS snapshots (restore on-prem or as EBS)\ncached: data in S3, most recent data cached locally (1 GiB-32 TiB, x32 = 1 PiB)\nstored: ALL data on-prem, scheduled backups to S3 (1 GiB-16 TiB, x32 = 512 TiB)", "ebs-snapshot"),
        (430, "iSCSI VTL\nbackup software", "Tape Gateway\n1 media changer\n+ 10 tape drives", "tape-gateway",
         "Virtual tapes (100 GiB-15 TiB) in S3\neject → archive to Glacier Flexible\nRetrieval or Glacier Deep Archive\nsame tape processes, leading backup apps", "vtl"),
    ]
    for i, (y, src, gw, gicon, aws, aicon) in enumerate(rows):
        d.box(f"s{i}", 34, y, 110, 110, src, "white", size=10)
        d.box(f"g{i}", 160, y, 150, 110, gw, "green", size=10, icon=gicon, icon_size=26, valign="top")
        d.box(f"a{i}", 414, y, 512, 110, aws, "white", size=10, icon=aicon, icon_size=30, align="left", bold_first=False)
        d.edge(f"s{i}", f"g{i}")
        d.edge(f"g{i}", f"a{i}", "HTTPS")
    d.box("ft", 20, 604, 455, 80, "FSx File Gateway: on-prem SMB cache in front of FSx for\nWindows. No longer available to NEW customers (AWS\nrecommends using FSx for Windows directly).", "red", size=10, align="left")
    d.box("dep", 485, 604, 455, 80, "Deploy as a VM (VMware ESXi, Hyper-V, Linux KVM,\nNutanix), an EC2 instance, VMware Cloud on AWS, or a\nhardware appliance. Data encrypted in transit (SSL/TLS).", "white", size=10, align="left", bold_first=False)
    return d


def sx_transfer_datasync():
    d = Diagram("sx-06-transfer-family-datasync", 960, 560, "AWS Transfer Family vs AWS DataSync")
    d.group("tf", 20, 46, 450, 370, "Transfer Family: managed file-transfer SERVER", "blue", icon=None)
    d.box("u", 34, 86, 120, 60, "Users\n(FTP client)", "white", size=10, icon="users", icon_size=24)
    d.box("ep", 184, 76, 156, 80, "Transfer Family\nSFTP, FTPS,\nFTP, AS2", "white", size=10, icon="transfer-family", icon_size=28)
    d.box("s3", 370, 76, 86, 36, "S3", "white", size=10, icon="s3", icon_size=22)
    d.box("efs", 370, 120, 86, 36, "EFS", "white", size=10, icon="efs", icon_size=22)
    d.edge("u", "ep")
    d.edge("ep", "s3")
    d.edge("ep", "efs")
    d.text("tft", 30, 166, 430, 246,
           "• Into and out of S3 or EFS, access via an IAM role\n• Endpoint: public or VPC hosted\n• Protocols: SFTP, FTPS, FTP, AS2 (+ browser web apps)\n• FTP is clear text: VPC (internal) endpoint only\n• Managed, scalable, reliable, highly available\n  (up to 3 AZs)\n• Pay per provisioned endpoint per hour + per GB\n• Users: stored in the service, or your existing\n  auth (Microsoft AD, LDAP, Okta, Cognito, custom)\n• Optional Route 53 name for the endpoint\n• Use: sharing files, public datasets, CRM, ERP", size=10, align="left")
    d.group("ds", 490, 46, 450, 370, "DataSync: scheduled COPY / sync job", "green", icon=None)
    d.box("src", 504, 86, 130, 80, "On-prem / other\ncloud: NFS, SMB,\nHDFS, object", "white", size=10)
    d.box("ag", 646, 86, 104, 80, "DataSync\nagent", "white", size=10, icon="datasync-agent", icon_size=24)
    d.box("dst", 776, 76, 150, 100, "S3 (all classes\nincl. Glacier)\nEFS · FSx (Win,\nLustre, ONTAP,\nOpenZFS)", "white", size=10)
    d.edge("src", "ag")
    d.edge("ag", "dst")
    d.text("dst2", 500, 176, 430, 236,
           "• Agent → AWS over TLS (encrypted in transit)\n• Needs an agent: on-prem storage, or EFS/FSx ↔ other clouds\n• No agent: AWS ↔ AWS (same or other account,\n  any Region), S3 ↔ other clouds' object storage\n• Schedule hourly, daily, weekly (or custom)\n• Preserves file permissions and metadata\n  (NFS POSIX, SMB ACLs, timestamps) + checksums\n• Per task: 10 Gbps with agent, 5 Gbps without;\n  set a bandwidth limit (throttle)\n• Basic vs Enhanced mode (Enhanced: virtually\n  unlimited files, faster)", size=10, align="left")
    d.box("pick", 20, 430, 920, 114,
          "How to choose (exam)\n• External partners PUSH or PULL files with an FTP/SFTP client → Transfer Family.\n"
          "• Copy or keep in sync large data sets on a schedule (migration, replication between AWS storage services) → DataSync.\n"
          "• Apps on-prem must keep using files / volumes / tapes with a local cache → Storage Gateway.\n"
          "• Too much data for the network (more than a week) → Snowball (existing customers) or Data Transfer Terminal / partner devices.\n"
          "• Hybrid pattern: DataSync for the initial migration, then Storage Gateway (S3 File Gateway) for ongoing on-prem access.", "yellow", size=10, align="left")
    return d


STORAGE_EXTRAS = [sx_comparison, sx_snowball, sx_fsx_overview, sx_lustre_deploy, sx_storage_gateway, sx_transfer_datasync]


def msg_decoupling():
    d = Diagram("msg-01-decoupling", 960, 560, "Application communication: synchronous vs asynchronous (decoupled)")
    d.group("sy", 20, 46, 450, 200, "1) Synchronous: application → application", "red")
    d.box("b1", 40, 96, 150, 64, "Buying service", "white", size=11, icon="generic-app", icon_size=26)
    d.box("s1", 300, 96, 150, 64, "Shipping service", "white", size=11, icon="generic-app", icon_size=26)
    d.edge("b1", "s1", "direct call")
    d.text("syt", 30, 172, 430, 70, "Problem: a sudden spike (1,000 videos to encode\ninstead of the usual 10) hits the receiver directly.\nIf it is slow or down, the caller fails too.", size=10, align="left")
    d.group("as", 490, 46, 450, 200, "2) Asynchronous / event based: app → queue → app", "green")
    d.box("b2", 504, 96, 130, 64, "Buying\nservice", "white", size=11, icon="generic-app", icon_size=24)
    d.box("q2", 654, 96, 130, 64, "Queue", "white", size=11, icon="sqs-queue", icon_size=28)
    d.box("s2", 804, 96, 126, 64, "Shipping\nservice", "white", size=11, icon="generic-app", icon_size=24)
    d.edge("b2", "q2"); d.edge("q2", "s2")
    d.text("ast", 500, 172, 430, 70, "The queue absorbs the spike. Each side scales\nindependently of the other: decoupled.", size=10, align="left")
    models = [("sqs", "SQS: queue model", "sqs", "Consumers PULL messages.\nOne message → one consumer.\nDeleted after processing."),
              ("sns", "SNS: pub/sub model", "sns", "Topic PUSHES to every\nsubscriber. One message →\nmany receivers."),
              ("kin", "Kinesis: real-time streaming", "kinesis-data-streams", "Ordered stream of records,\nkept for days, many readers,\nreplay possible."),
              ("mq", "Amazon MQ: managed broker", "mq", "ActiveMQ / RabbitMQ with\nopen protocols (MQTT, AMQP,\nSTOMP, OpenWire, WSS).")]
    for i, (bid, title, icon, body) in enumerate(models):
        x = 20 + i * 235
        d.box(f"{bid}h", x, 266, 220, 50, title, "blue", size=10, bold=True, icon=icon, icon_size=26)
        d.box(f"{bid}b", x, 320, 220, 80, body, "white", size=10, bold_first=False)
    d.box("sc", 20, 416, 920, 50, "These services scale independently from your application. SQS, SNS and Kinesis are \"cloud-native\" (AWS APIs);\nAmazon MQ is for apps that already speak open protocols (added: your notes skipped MQ).", "gray", size=10, bold_first=False)
    d.box("ex", 20, 480, 920, 64, "Exam keywords\n\"decouple tiers / buffer writes / absorb spikes\" → SQS · \"send one event to many\" → SNS (+ SQS fan-out)\n"
          "\"real-time big data, replay, ordering per key\" → Kinesis Data Streams · \"load stream into S3/Redshift\" → Data Firehose · \"lift-and-shift JMS/AMQP/MQTT\" → MQ", "yellow", size=10, align="left")
    return d


def msg_sqs_basics():
    d = Diagram("msg-02-sqs-standard", 960, 640, "SQS Standard queue: producers send, consumers poll, process, delete")
    d.box("p1", 20, 80, 150, 50, "Producer\n(SDK SendMessage)", "white", size=10, icon="generic-app", icon_size=22)
    d.box("p2", 20, 150, 150, 50, "Producer", "white", size=10, icon="generic-app", icon_size=22)
    d.box("p3", 20, 220, 150, 50, "Producer", "white", size=10, icon="generic-app", icon_size=22)
    d.box("q", 290, 120, 240, 110, "SQS Standard queue\nmessage persisted until a\nconsumer DELETES it\nretention 4 days (1 min-14 d)", "white", size=10, icon="sqs-queue", icon_size=36)
    for p in ("p1", "p2", "p3"):
        d.edge(p, "q")
    d.box("c1", 640, 80, 150, 50, "Consumer (EC2)", "white", size=10, icon="ec2-instance", icon_size=22)
    d.box("c2", 640, 150, 150, 50, "Consumer (Lambda)", "white", size=10, icon="lambda-fn", icon_size=22)
    d.box("c3", 640, 220, 150, 50, "Consumer (server)", "white", size=10, icon="server", icon_size=22)
    for c in ("c1", "c2", "c3"):
        d.edge("q", c, "poll")
    d.box("db", 820, 150, 120, 50, "RDS insert", "white", size=10, icon="rds", icon_size=22)
    d.edge("c2", "db")
    d.box("msg", 20, 292, 450, 130, "A message (example: an order to process)\n• order id, customer id, any attributes you want\n• max size 1 MiB (1,048,576 bytes); larger payloads: Extended\n  Client Library puts the body in S3 (up to 2 GB)\n• publish and receive latency < 10 ms (course)\n• unlimited throughput, unlimited messages in the queue", "white", size=10, align="left", icon="sqs-message", icon_size=26)
    d.box("con", 490, 292, 450, 130, "Consumer loop\n1. ReceiveMessage: up to 10 messages per call\n2. Process (example: insert into an RDS database)\n3. DeleteMessage (else the message comes back)\n• consumers work in parallel; scale them horizontally\n• at-least-once delivery, best-effort ordering", "white", size=10, align="left")
    d.group("asg", 20, 440, 920, 110, "SQS + Auto Scaling Group: scale consumers on queue length", "orange")
    d.box("aq", 40, 476, 150, 56, "SQS queue", "white", size=10, icon="sqs-queue", icon_size=24)
    d.box("am", 230, 476, 240, 56, "CloudWatch metric (queue length)\nApproximateNumberOfMessages", "white", size=10, icon="cloudwatch", icon_size=24)
    d.box("aa", 510, 476, 170, 56, "CloudWatch alarm\n(breach)", "white", size=10, icon="cw-alarm", icon_size=24)
    d.box("ag", 720, 476, 200, 56, "ASG adds / removes\nEC2 consumers", "white", size=10, icon="ec2-autoscaling", icon_size=24)
    d.edge("aq", "am"); d.edge("am", "aa"); d.edge("aa", "ag", "scale")
    d.box("buf", 20, 564, 920, 60, "Patterns: SQS as a BUFFER to database writes (front end enqueues, workers dequeue and insert, so no transaction is lost under load)\n"
          "and SQS to DECOUPLE tiers (web tier SendMessage → queue → back-end processing tier ReceiveMessage, each tier in its own ASG).", "yellow", size=10, align="left", bold_first=False)
    return d


def msg_sqs_visibility():
    d = Diagram("msg-03-sqs-visibility-polling-dlq", 960, 640, "SQS: visibility timeout, long polling, dead-letter queue")
    d.group("vt", 20, 46, 920, 230, "Message visibility timeout (default 30 s, 0 s-12 h)", "blue")
    d.box("tl", 40, 150, 880, 6, "", "gray")
    labels = [(40, "ReceiveMessage\nmessage returned"), (250, "ReceiveMessage\nNOT returned"), (460, "ReceiveMessage\nNOT returned"), (700, "ReceiveMessage\nreturned AGAIN")]
    for i, (x, lab) in enumerate(labels):
        d.box(f"r{i}", x, 84, 170, 48, lab, "green" if i in (0, 3) else "white", size=10, bold_first=False)
    d.box("win", 120, 160, 540, 30, "invisible to other consumers for the visibility timeout", "orange", size=10)
    d.text("tm", 860, 160, 70, 30, "time →", size=10)
    d.text("vtt", 40, 196, 880, 76, "• Not deleted before the timeout ends → visible again → processed TWICE.   • Need more time? call ChangeMessageVisibility.\n"
           "• Timeout too HIGH (hours) and the consumer crashes → re-processing waits a long time.   • Too LOW (seconds) → duplicates.\n"
           "• The 12 h maximum counts from the first receive; extending does not reset it.", size=10, align="left")
    d.group("lp", 20, 290, 450, 220, "Long polling", "green")
    d.box("lc", 40, 330, 130, 56, "Consumer", "white", size=10, icon="generic-app", icon_size=22)
    d.box("lq", 300, 330, 150, 56, "SQS queue", "white", size=10, icon="sqs-queue", icon_size=24)
    d.edge("lc", "lq", "wait up to 20 s")
    d.text("lpt", 30, 396, 430, 110, "• Empty queue? The receive call WAITS for a message\n  instead of returning empty at once (short polling).\n• Fewer API calls, lower cost, lower latency.\n• Wait 1-20 s (20 s preferable). Queue level:\n  ReceiveMessageWaitTimeSeconds · API level: WaitTimeSeconds\n• Preferable to short polling.", size=10, align="left")
    d.group("dl", 490, 290, 450, 220, "Dead-letter queue (added from docs)", "red")
    d.box("sq", 504, 330, 150, 56, "Source queue", "white", size=10, icon="sqs-queue", icon_size=24)
    d.box("dq", 774, 330, 150, 56, "DLQ", "white", size=10, icon="sqs-queue", icon_size=24)
    d.edge("sq", "dq", "after maxReceiveCount")
    d.edge("dq", "sq", "redrive", points=[(849, 400), (579, 400)])
    d.text("dlt", 500, 410, 430, 96, "• maxReceiveCount = receives allowed before the message\n  is moved to the DLQ (poison messages).\n• Same account, Region and TYPE (FIFO → FIFO DLQ).\n• Standard: expiry uses the ORIGINAL enqueue time, so\n  give the DLQ a longer retention. Redrive moves them back.", size=10, align="left")
    d.box("dly", 20, 524, 920, 100, "Also (docs): delay queues / message timers 0-15 min (default 0) · batches of up to 10 messages for send, receive, delete\n"
          "• Security: in flight HTTPS · at rest SSE-SQS (SQS-owned keys) or SSE-KMS · client-side encryption if the client encrypts/decrypts itself\n"
          "• Access: IAM policies for the SQS API · SQS access policies (like S3 bucket policies) for cross-account access and to let SNS, S3... write to the queue\n"
          "• About 120,000 in-flight (received, not deleted) messages per standard queue", "yellow", size=10, align="left", bold_first=False)
    return d


def msg_fifo():
    d = Diagram("msg-04-standard-vs-fifo", 960, 520, "SQS Standard vs SQS FIFO")
    d.group("st", 20, 46, 450, 330, "Standard queue", "blue")
    d.box("sp", 40, 86, 110, 50, "Producer", "white", size=10)
    d.box("sq", 180, 86, 140, 50, "4 1 3 2 2", "white", size=12, icon="sqs-queue", icon_size=26)
    d.box("sc", 350, 86, 100, 50, "Consumer", "white", size=10)
    d.edge("sp", "sq"); d.edge("sq", "sc")
    d.text("stt", 30, 150, 430, 220, "• Nearly unlimited API calls per second, per action\n• Unlimited number of messages\n• At-least-once delivery: duplicates can happen\n• Best-effort ordering: can arrive out of order\n• Any queue name\n• Use when throughput matters and the app\n  is idempotent (tolerates duplicates)", size=11, align="left")
    d.group("ff", 490, 46, 450, 330, "FIFO queue (name must end in .fifo)", "green")
    d.box("fp", 504, 86, 110, 50, "Producer", "white", size=10)
    d.box("fq", 644, 86, 140, 50, "4 3 2 1", "white", size=12, icon="sqs-queue", icon_size=26)
    d.box("fc", 814, 86, 110, 50, "Consumer", "white", size=10)
    d.edge("fp", "fq"); d.edge("fq", "fc")
    d.text("fft", 500, 150, 430, 220, "• First In First Out: processed in order\n• Ordering per Message Group ID (mandatory):\n  in order inside one group, groups in parallel\n• Exactly-once processing: duplicates removed by\n  Deduplication ID or content-based (SHA-256 of\n  body) within a 5-minute interval\n• 300 msg/s without batching, 3,000 msg/s with\n  batching (10 per call), per API action\n• High-throughput mode: tens of thousands TPS\n  (docs: up to 30,000; varies by Region)", size=11, align="left")
    d.box("ex", 20, 390, 920, 114, "Exam\n• \"Order must be kept\" or \"no duplicates\" → FIFO. \"Highest throughput, order not important\" → Standard.\n"
          "• Order per customer/user but scale → FIFO with Message Group ID = customer id (one consumer per group at a time).\n"
          "• You cannot convert a Standard queue to FIFO: create a new .fifo queue.\n"
          "• S3 event notifications can't target a FIFO queue (Standard queues only).", "yellow", size=10, align="left")
    return d


def msg_sns():
    d = Diagram("msg-05-sns-pubsub", 960, 660, "Amazon SNS: publish once to a topic, every subscriber gets it")
    d.group("pub", 20, 46, 220, 400, "Publishers (examples)", "gray")
    pubs = [("cw", "CloudWatch alarms", "cw-alarm"), ("asg", "ASG notifications", "ec2-autoscaling"), ("s3e", "S3 bucket events", "s3-bucket"),
            ("lam", "Lambda / your app", "lambda-fn"), ("ddb", "DynamoDB, RDS events", "dynamodb"), ("bud", "Budgets, CFN, DMS", "generic-app")]
    for i, (bid, lab, ic) in enumerate(pubs):
        d.box(bid, 34, 80 + i * 60, 192, 48, lab, "white", size=10, icon=ic, icon_size=24)
    d.box("t", 330, 210, 170, 80, "SNS topic\n(standard)", "white", size=12, icon="sns-topic", icon_size=36)
    for i, (bid, *_) in enumerate(pubs):
        d.edge(bid, "t", points=[(280, 104 + i * 60), (300, 250)])
    d.group("sub", 590, 46, 350, 400, "Subscribers (each gets ALL messages)", "green")
    subs = [("q", "SQS queue", "sqs-queue"), ("l", "Lambda", "lambda-fn"), ("f", "Data Firehose", "firehose"),
            ("h", "HTTP(S) endpoint", "http-notification"), ("e", "Email / email-JSON", "email-notification"), ("m", "SMS & mobile push", "mobile-client")]
    for i, (bid, lab, ic) in enumerate(subs):
        d.box(bid, 604, 80 + i * 60, 322, 48, lab, "white", size=10, icon=ic, icon_size=24)
        d.edge("t", bid, points=[(530, 250), (570, 104 + i * 60)])
    d.box("lim", 20, 460, 455, 100, "Limits (docs)\n• 12,500,000 subscriptions per standard topic\n• 100,000 standard topics per account\n• Message 256 KiB default, up to 1 MiB (topic setting);\n  bigger via Extended Client Library (S3, 2 GB)", "white", size=10, align="left")
    d.box("how", 485, 460, 455, 100, "How to publish\n• Topic publish (SDK): create topic → create subscription(s)\n  → publish to the topic\n• Direct publish (mobile apps SDK): create platform application\n  → platform endpoint → publish. FCM (ex-GCM), APNs, ADM, Baidu, WNS", "white", size=10, align="left")
    d.box("sec", 20, 574, 920, 70, "Security (same as SQS): in flight HTTPS · at rest KMS keys · client-side encryption\n"
          "Access: IAM policies for the SNS API · SNS access policies (like S3 bucket policies) for cross-account access and to let other services (S3...) publish", "yellow", size=10, align="left")
    return d


def msg_fanout():
    d = Diagram("msg-06-sns-sqs-fanout", 960, 700, "SNS + SQS fan-out, S3 events to many queues, SNS FIFO, filtering")
    d.group("fo", 20, 46, 450, 250, "Fan-out: push once to SNS, every SQS queue gets it", "green")
    d.box("bs", 34, 136, 110, 56, "Buying\nservice", "white", size=10)
    d.box("ft", 174, 136, 120, 56, "SNS topic", "white", size=10, icon="sns-topic", icon_size=26)
    d.box("fq1", 324, 86, 136, 50, "SQS → Fraud", "white", size=10, icon="sqs-queue", icon_size=22)
    d.box("fq2", 324, 190, 136, 50, "SQS → Shipping", "white", size=10, icon="sqs-queue", icon_size=22)
    d.edge("bs", "ft"); d.edge("ft", "fq1"); d.edge("ft", "fq2")
    d.text("fot", 30, 244, 430, 50, "Fully decoupled, no data loss; SQS adds persistence, delayed\nprocessing, retries; add queues any time; works cross-Region.", size=10, align="left")
    d.group("s3", 490, 46, 450, 250, "S3 event to multiple queues", "blue")
    d.box("b", 504, 136, 110, 56, "S3: object\ncreated", "white", size=10, icon="s3-bucket", icon_size=24)
    d.box("st", 644, 136, 120, 56, "SNS topic", "white", size=10, icon="sns-topic", icon_size=26)
    d.box("sq1", 794, 80, 132, 44, "SQS queue", "white", size=10, icon="sqs-queue", icon_size=20)
    d.box("sq2", 794, 142, 132, 44, "SQS queue", "white", size=10, icon="sqs-queue", icon_size=20)
    d.box("sl", 794, 204, 132, 44, "Lambda", "white", size=10, icon="lambda-fn", icon_size=20)
    d.edge("b", "st", "event"); d.edge("st", "sq1"); d.edge("st", "sq2"); d.edge("st", "sl")
    d.text("s3t", 500, 252, 430, 44, "One event type + prefix (e.g. object create, images/) = one\nS3 event rule. Many targets for the same event → fan-out.", size=10, align="left")
    d.group("kf", 20, 310, 450, 130, "SNS to S3 through Data Firehose", "orange")
    d.box("k1", 34, 350, 100, 56, "Buying\nservice", "white", size=10)
    d.box("k2", 160, 350, 90, 56, "SNS", "white", size=10, icon="sns-topic", icon_size=24)
    d.box("k3", 276, 350, 100, 56, "Data\nFirehose", "white", size=10, icon="firehose", icon_size=24)
    d.box("k4", 400, 340, 60, 76, "S3 or\nany\nKDF\ntarget", "white", size=9, bold_first=False)
    d.edge("k1", "k2"); d.edge("k2", "k3"); d.edge("k3", "k4")
    d.group("ff", 490, 310, 450, 130, "SNS FIFO topic (+ SQS FIFO = fan-out with order)", "purple")
    d.text("fft", 500, 340, 430, 96, "• Ordering by Message Group ID; dedup by Deduplication ID\n  or content-based, 5-minute window\n• Subscribers: SQS FIFO AND SQS Standard queues only\n• 3,000 msg/s or 20 MB/s per topic (300/s per group);\n  high-throughput mode for more (docs)", size=10, align="left")
    d.group("fl", 20, 454, 920, 230, "SNS message filtering (subscription filter policy, JSON)", "gray")
    d.box("ms", 34, 530, 190, 90, "New transaction\nOrder: 1036\nProduct: Pencil · Qty: 4\nState: Placed", "white", size=10)
    d.box("mt", 260, 545, 130, 60, "SNS topic", "white", size=10, icon="sns-topic", icon_size=26)
    d.edge("ms", "mt")
    rows = [("Filter State: Placed", "SQS (placed orders)", "green"), ("Filter State: Cancelled", "SQS (cancelled orders)", "white"),
            ("Filter State: Cancelled", "Email (cancelled orders)", "white"), ("Filter State: Declined", "SQS (declined orders)", "white"),
            ("No filter policy", "SQS (all) - gets EVERY message", "green")]
    for i, (f, s, col) in enumerate(rows):
        d.box(f"fp{i}", 440, 486 + i * 38, 190, 32, f, "yellow", size=10)
        d.box(f"sub{i}", 650, 486 + i * 38, 270, 32, s, col, size=10)
        d.edge("mt", f"fp{i}", points=[(415, 575), (420, 502 + i * 38)]); d.edge(f"fp{i}", f"sub{i}")
    d.text("flt", 34, 630, 390, 50, "Scope: message attributes (default) or message body.\nYour notes said \"SQS - Message Filtering\": it is SNS.", size=10, align="left")
    return d


def msg_kinesis():
    d = Diagram("msg-07-kinesis-data-streams", 960, 640, "Kinesis Data Streams: collect and store streaming data in real time")
    d.group("pr", 20, 46, 200, 300, "Producers", "gray")
    for i, (bid, lab, ic) in enumerate([("a", "Applications", "generic-app"), ("c", "Click streams", "users"), ("i", "IoT devices", "sensor"), ("m", "Metrics & logs\n(Kinesis Agent, KPL)", "server")]):
        d.box(bid, 30, 80 + i * 64, 180, 52, lab, "white", size=10, icon=ic, icon_size=22)
    d.group("ks", 260, 46, 420, 300, "Kinesis Data Stream", "purple", icon="kinesis-data-streams", icon_size=24)
    for i in range(3):
        d.box(f"sh{i}", 280, 90 + i * 58, 380, 46, f"Shard {i + 1}:  rec · rec · rec · rec  →", "white", size=11)
    d.text("kst", 270, 268, 400, 76, "record = partition key + data blob (up to 1 MiB, can raise\nto 10 MiB per stream since Oct 2025). Same partition key\n→ same shard → ORDERED. Retention 24 h - 365 days.", size=10, align="left")
    for bid, *_ in [("a",), ("c",), ("i",), ("m",)]:
        d.edge(bid, "sh1")
    d.group("co", 720, 46, 220, 300, "Consumers", "gray")
    for i, (bid, lab, ic) in enumerate([("ca", "Apps (KCL)", "generic-app"), ("cl", "Lambda", "lambda-fn"), ("cf", "Data Firehose", "firehose"), ("cm", "Managed Service\nfor Apache Flink", "flink")]):
        d.box(bid, 730, 80 + i * 64, 200, 52, lab, "white", size=10, icon=ic, icon_size=22)
        d.edge("sh1", bid)
    d.box("pv", 20, 360, 455, 160, "Provisioned mode\n• You choose the number of shards; scale manually\n  (split / merge shards)\n• Per shard: IN 1 MB/s or 1,000 records/s\n• Per shard: OUT 2 MB/s shared by all consumers\n  (enhanced fan-out: 2 MB/s per shard PER consumer)\n• Pay per shard provisioned per hour", "orange", size=10, align="left")
    d.box("od", 485, 360, 455, 160, "On-demand mode\n• No capacity to provision or manage\n• Default 4 MB/s or 4,000 records/s in\n• Scales automatically to 2x the peak write seen in\n  the last 30 days (up to 200 MB/s; 10 GB/s in\n  N. Virginia, Oregon, Ireland)\n• Pay per stream per hour + data in/out per GB", "green", size=10, align="left")
    d.box("fa", 20, 534, 920, 90, "Key facts\n• Consumers can REPROCESS (replay) data · data can't be deleted until it expires · at rest KMS, in flight HTTPS\n"
          "• KPL (Kinesis Producer Library) = optimized producer app · KCL (Kinesis Client Library) = optimized consumer app\n"
          "• Switch capacity mode at most twice per 24 h per stream", "yellow", size=10, align="left")
    return d


def msg_firehose():
    d = Diagram("msg-08-firehose-vs-streams", 960, 712, "Amazon Data Firehose (ex Kinesis Data Firehose), and how it differs from Data Streams")
    d.group("src", 20, 46, 200, 330, "Sources", "gray")
    for i, (bid, lab, ic) in enumerate([("ap", "Apps / SDK\n(Direct PUT)", "generic-app"), ("kds", "Kinesis Data\nStreams", "kinesis-data-streams"), ("msk", "Amazon MSK", "msk"), ("cwl", "CloudWatch Logs,\nSNS, IoT, agent", "cloudwatch")]):
        d.box(bid, 30, 80 + i * 72, 180, 60, lab, "white", size=10, icon=ic, icon_size=24)
    d.box("fh", 280, 150, 210, 110, "Data Firehose\nbuffer by size (1-128 MB)\nor time (0-900 s)\nthen batch write", "white", size=10, icon="firehose", icon_size=32, valign="top")
    for bid in ("ap", "kds", "msk", "cwl"):
        d.edge(bid, "fh")
    d.box("lt", 295, 290, 180, 60, "Lambda: optional\ntransform (CSV→JSON)", "white", size=10, icon="lambda-fn", icon_size=22)
    d.edge("fh", "lt", both=True)
    d.group("dst", 540, 46, 400, 330, "Destinations", "green")
    for i, (bid, lab, ic) in enumerate([("s3", "Amazon S3 (+ S3 Tables / Iceberg)", "s3-bucket"), ("rs", "Amazon Redshift (via S3 COPY)", "redshift"), ("os", "Amazon OpenSearch Service", "opensearch"),
                                         ("tp", "3rd party: Splunk, Snowflake, Datadog,\nMongoDB, New Relic, Dynatrace...", "generic-app"), ("he", "Custom HTTP endpoint", "http-notification")]):
        d.box(bid, 552, 78 + i * 58, 376, 48, lab, "white", size=10, icon=ic, icon_size=22)
        d.edge("fh", bid, points=[(515, 205), (530, 102 + i * 58)])
    d.box("bk", 552, 380, 376, 40, "S3 backup bucket: all data, or only failed data", "orange", size=10)
    d.edge("fh", "bk", dashed=True, points=[(515, 205), (515, 400)])
    d.box("ff", 20, 390, 480, 110, "Firehose facts\n• Fully managed, automatic scaling, pay for what you use\n• NEAR real-time (buffering; 0 s interval = within seconds)\n• Record up to 1,024 KB (Direct PUT / KDS); formats CSV, JSON,\n  Parquet, Avro, raw text, binary · JSON → Parquet/ORC · gzip/zip/snappy", "white", size=10, align="left")
    rows = [("", "Kinesis Data Streams", "Amazon Data Firehose"),
            ("Job", "streaming data COLLECTION", "LOAD streaming data into S3 / Redshift /\nOpenSearch / 3rd party / custom HTTP"),
            ("Code", "write producer & consumer code", "fully managed, no consumer code"),
            ("Speed", "real time", "near real time (buffered)"),
            ("Scaling", "provisioned or on-demand mode", "automatic"),
            ("Storage", "keeps data 24 h - 365 days", "no data storage"),
            ("Replay", "yes", "no")]
    for i, r in enumerate(rows):
        h = 40 if i == 1 else 24
        y = 514 + (0 if i == 0 else 24 + (i - 1) * 24 + (16 if i > 1 else 0))
        for j, c in enumerate(r):
            w = [120, 360, 440][j]
            x = [20, 140, 500][j]
            d.box(f"t{i}{j}", x, y, w, h, c, "gray" if (i == 0 or j == 0) else "white", size=10, bold=(i == 0 or j == 0), bold_first=False)
    return d


def msg_mq():
    d = Diagram("msg-09-amazon-mq", 960, 600, "Amazon MQ: managed ActiveMQ / RabbitMQ broker for open protocols (added: not in your notes)")
    d.box("why", 20, 46, 920, 76, "Why it exists\nSQS and SNS are cloud-native, proprietary AWS APIs. Apps from on-premises often use open protocols: MQTT, AMQP, STOMP, OpenWire, WSS (+ JMS APIs).\n"
          "Migrating them? Instead of re-engineering to SQS/SNS, use Amazon MQ: change the endpoint, keep the messaging code.", "gray", size=10, align="left")
    d.group("ha", 20, 136, 560, 300, "ActiveMQ active/standby (high availability)", "white", icon="region", size=12)
    d.box("cl", 40, 250, 110, 70, "Client\n(failover\nURL)", "white", size=10, icon=None)
    d.group("az1", 190, 172, 220, 110, "AZ us-east-1a: ACTIVE", "green", size=11)
    d.box("b1", 206, 206, 188, 60, "MQ broker", "white", size=10, icon="mq-broker", icon_size=28)
    d.group("az2", 190, 300, 220, 110, "AZ us-east-1b: STANDBY", "white", size=11, dashed=True)
    d.box("b2", 206, 334, 188, 60, "MQ broker", "white", size=10, icon="mq-broker", icon_size=28)
    d.box("efs", 440, 250, 124, 70, "Amazon EFS\n(shared\nstorage)", "white", size=10, icon="efs", icon_size=24)
    d.edge("cl", "b1"); d.edge("cl", "b2", "failover", dashed=True)
    d.edge("b1", "efs"); d.edge("b2", "efs", dashed=True)
    d.box("eng", 600, 136, 340, 300, "Engines and protocols (docs)\n• ActiveMQ: AMQP, MQTT, OpenWire, STOMP,\n  MQTT/STOMP over WebSocket (+ JMS)\n• RabbitMQ: AMQP 0-9-1\n\nDeployment\n• ActiveMQ: single-instance (1 AZ),\n  active/standby (2 AZs, EFS storage),\n  network of brokers (scale out)\n• RabbitMQ: single-instance or\n  3-node cluster across AZs\n• Storage: EFS (durable, multi-AZ) or\n  EBS (throughput, single-instance)", "white", size=10, align="left", valign="top")
    d.box("fa", 20, 450, 920, 134, "Exam facts\n• Has QUEUE features (~SQS) and TOPIC features (~SNS) in one broker.\n"
          "• Runs on broker instances (e.g. mq.m5.large): pay per instance hour + storage; it does NOT scale like SQS/SNS (scale = bigger instance or network of brokers).\n"
          "• Multi-AZ with failover: active/standby; the standby takes over the shared EFS storage if the active broker or its AZ fails.\n"
          "• Keyword: \"migrate an on-prem app that uses MQTT / AMQP / STOMP / JMS without code changes\" → Amazon MQ. \"New cloud app\" → SQS/SNS.", "yellow", size=10, align="left")
    return d


def msg_compare():
    d = Diagram("msg-10-sqs-sns-kinesis-mq", 960, 560, "Which one? SQS vs SNS vs Kinesis Data Streams vs Amazon MQ")
    rows = [("", "SQS", "SNS", "Kinesis Data Streams", "Amazon MQ"),
            ("Model", "queue: consumers PULL", "pub/sub: PUSH to\nmany subscribers", "stream: PULL (standard)\nor PUSH (enhanced fan-out)", "broker: queues +\ntopics"),
            ("After read", "deleted once\nconsumed", "not persisted: lost\nif not delivered", "kept until it expires\n(24 h - 365 days), replay", "kept until consumed\n(broker storage)"),
            ("Scale", "no provisioning,\nas many workers as\nyou want", "no provisioning,\n12.5M subs/topic,\n100k topics", "provisioned shards or\non-demand; 2 MB/s per\nshard (per consumer w/ EFO)", "instance size; does\nnot scale like\nSQS/SNS"),
            ("Ordering", "FIFO queues only", "FIFO topics\n(to SQS queues)", "per shard\n(partition key)", "per queue\n(engine-dependent)"),
            ("Extras", "per-message delay,\nDLQ, long polling", "fan-out with SQS,\nfilter policies", "real-time big data,\nanalytics, ETL", "open protocols:\nMQTT, AMQP, STOMP..."),
            ("Pick when", "decouple tiers,\nbuffer work", "notify many systems\nat once", "real-time analytics,\nreplay, ordered stream", "migrate existing\nbroker apps")]
    widths = [110, 200, 200, 230, 180]
    xs = [20, 130, 330, 530, 760]
    y = 46
    for i, r in enumerate(rows):
        h = 34 if i == 0 else 72
        for j, c in enumerate(r):
            col = "gray" if i == 0 or j == 0 else "white"
            if i == 0 and j > 0:
                col = ["blue", "purple", "orange", "green"][j - 1]
            d.box(f"c{i}{j}", xs[j], y, widths[j], h, c, col, size=10, bold=(i == 0 or j == 0), bold_first=False)
        y += h + 4
    return d


MESSAGING = [msg_decoupling, msg_sqs_basics, msg_sqs_visibility, msg_fifo, msg_sns, msg_fanout, msg_kinesis, msg_firehose, msg_mq, msg_compare]


ALL = [iam_big_picture, policy_anatomy, policy_evaluation, access_methods, role_assume, mfa_password,
       security_tools, shared_responsibility,
       global_infra,
       ec2_instance_types, ec2_security_groups, ec2_purchase_options, ec2_spot,
       ec2_ips, placement_groups, eni_hibernate,
       storage_compare, ebs_snapshots_ami, ebs_volume_types, efs_classes,
       elb_types, alb_flow, asg,
       rds_replicas_multiaz, aurora, rds_backup_proxy, elasticache] + ROUTE53 + S3 + CLOUDFRONT + STORAGE_EXTRAS + MESSAGING

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
