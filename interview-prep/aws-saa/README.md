# AWS Solutions Architect – Associate in 10 days (17–27 Nov 2026)

**Target exam day: Fri 27 Nov 2026.** Book it today, for 27 Nov, and use the go/no-go gate on Thu 26 Nov (below) to decide whether to sit or reschedule.

**The honest picture.**
- You have real AWS experience (EKS, VPC, RDS, IAM, CloudWatch, cost work), so this is possible in 10 full days.
- It's tight for a slow learner. The course alone is roughly 25–30 hours of video, and the exam also covers services you've never used (Kinesis, Storage Gateway, Snow family, Redshift, Cognito and others).
- **Passing practice exams is the only evidence that counts.** "I finished the course" isn't.
- This certificate tests **recognition** (pick the best of 4 options). It does **not** fix the interview misses (Linux, SQL, Kubernetes, Terraform, typing commands from memory). That's why a 30-minute interview-recall slot stays in every day.

## The exam (check before booking)

Facts as I know them for **SAA-C03**. Confirm the current version, price and rules on the official AWS Certification page before you pay; AWS updates exams.

| Item | Value |
|---|---|
| Questions | 65 (50 scored + 15 unscored, and you can't tell which) |
| Time | 130 minutes (about 2 minutes per question) |
| Passing score | 720 out of 1000 (scaled) |
| Price | 150 USD |
| Format | Multiple choice (1 right) and multiple response (2+ right), scenario-based |
| Where | Pearson VUE test centre, or online from home (needs a clean desk, webcam, ID) |
| Rescheduling | Allowed without a fee if you do it well before the slot (Pearson VUE: at least 24 hours before). **Check this when you book.** |

**Domains and weights:**

| Domain | Weight | What it really asks |
|---|---|---|
| 1. Design secure architectures | 30% | IAM policies and roles, SCPs, KMS, Secrets Manager, SG vs NACL, private subnets, VPC endpoints, S3 bucket policies and encryption, WAF/Shield, Cognito |
| 2. Design resilient architectures | 26% | Multi-AZ, Auto Scaling, ELB, decoupling with SQS/SNS/EventBridge, RDS Multi-AZ vs read replicas, Aurora, backup and DR (RPO/RTO), Route 53 failover |
| 3. Design high-performing architectures | 24% | Choosing storage (EBS types, EFS, FSx, S3 classes), caching (ElastiCache, CloudFront, DAX), DynamoDB, Kinesis, Lambda, right instance family |
| 4. Design cost-optimized architectures | 20% | Purchase options (On-Demand, Savings Plans, Reserved, Spot), S3 lifecycle and storage classes, NAT Gateway vs VPC endpoint cost, right-sizing, data transfer cost |

## How to use the Udemy course

- Watch at **1.25x**. Speed up to 1.5x for services you use at work (EC2, EKS, IAM basics, CloudWatch).
- **Skip the hands-on demos** for services you already know. **Do the demos** for VPC (subnets, NAT, endpoints, NACL), S3 policies, and anything you've never touched.
- After each section, do its **end-of-section quiz**. Score under 70% = re-watch only the parts you got wrong, not the whole section.
- Use the course's PDF slides as your revision material. Don't make long notes. **Write one line per service: "use it when …"**. Exam questions are "which service fits this scenario".
- Course sections are named differently in each course. Match the topics below to your course's sections; the order below follows the usual course order.

## Daily timetable

| Time | What |
|---|---|
| 9:00–9:30 | Recall: yesterday's "use it when" lines and quiz misses, **typed from memory** |
| 9:30–12:30 | Course videos (Block 1) |
| 12:30–13:30 | Lunch, no screens |
| 13:30–16:00 | Course videos (Block 2) + section quizzes |
| 16:00–16:30 | **Interview recall (don't skip):** 3 items from `misses.md`, typed. Linux, TCP, pod startup, Terraform block, 502/503/504 |
| 16:30–17:00 | Revise today's weak spots from the slides |
| 17:00–17:30 | Send **"SAA day N quiz"** in the thread: I ask 10 exam-style scenario questions on today's topics, you answer without notes |
| 17:30 | Stop. Sleep 7+ hours. Memory consolidates during sleep, and the night before the exam matters most |

SQL and the 15-day plan are **paused** during these 10 days (see the note in [../15-day-plan/README.md](../15-day-plan/README.md)).

## Day by day

| Day | Date | Topics (match them to your course sections) | Done when |
|---|---|---|---|
| 0 | Tue 17 Nov (afternoon) | Book the exam for 27 Nov. Take the free **official practice question set** on AWS Skill Builder as a baseline (don't worry about the score). Course: intro, **IAM** (users, groups, roles, policies, MFA, access keys) | Exam booked; baseline score written down |
| 1 | Wed 18 Nov | **EC2** basics, instance families, purchase options (On-Demand, Reserved, Savings Plans, Spot, Dedicated), security groups, placement groups, ENI, hibernate; **EC2 storage**: EBS volume types (gp3, io2, st1, sc1), snapshots, AMI, instance store, **EFS** | Name the cheapest way to run a fault-tolerant batch job (Spot) and the EBS type for a database (io2/gp3) |
| 2 | Thu 19 Nov | **High availability and scaling**: ALB vs NLB vs GWLB, target groups, health checks, sticky sessions, cross-zone, SSL/SNI, connection draining; **Auto Scaling** (policies, cooldowns); **RDS, Aurora, ElastiCache** (Multi-AZ vs read replicas, Aurora Serverless, Global Database, RDS Proxy, Redis vs Memcached) | Explain Multi-AZ vs read replica and when you'd use each |
| 3 | Fri 20 Nov | **Route 53** (record types, alias vs CNAME, routing policies: simple, weighted, latency, failover, geolocation, geoproximity, multi-value; health checks); **S3** basics, storage classes, lifecycle, versioning, replication, **S3 security** (bucket policy vs IAM, encryption SSE-S3/SSE-KMS/SSE-C, Block Public Access, presigned URLs, Object Lock) | Pick the S3 class for "rarely accessed, needed within milliseconds" (Standard-IA / Glacier Instant Retrieval) |
| 4 | Sat 21 Nov | **CloudFront** (origins, OAC, caching, geo restriction) and **Global Accelerator**; **storage extras**: Snow family, FSx (Windows, Lustre, NetApp ONTAP), Storage Gateway, DataSync, Transfer Family; **decoupling**: SQS (standard vs FIFO, visibility timeout, DLQ), SNS (fan-out), Kinesis Data Streams vs Firehose, Amazon MQ | CloudFront vs Global Accelerator in one line; SQS vs SNS vs Kinesis in one line each |
| 5 | Sun 22 Nov | **Containers**: ECS (EC2 vs Fargate launch type), EKS, ECR, App Runner; **serverless**: Lambda (limits, concurrency, SnapStart), DynamoDB (capacity modes, GSI/LSI, DAX, streams, global tables), API Gateway, Step Functions, Cognito (user pools vs identity pools) | Design a serverless API with auth, from memory |
| 6 | Mon 23 Nov | **Databases summary** (which DB for which need); **data and analytics**: Athena, Redshift, OpenSearch, EMR, Glue, Lake Formation, QuickSight, MSK; **ML services** (names and one use each: Rekognition, Transcribe, Polly, Translate, Comprehend, SageMaker, Textract, Kendra) | Match 10 services to 10 one-line needs |
| 7 | Tue 24 Nov | **Monitoring and audit**: CloudWatch (metrics, logs, alarms), EventBridge, CloudTrail, Config; **advanced IAM**: Organizations, SCPs, IAM Identity Center, permission boundaries, policy evaluation; **security**: KMS (key types, rotation), Secrets Manager vs Parameter Store, ACM, WAF, Shield, GuardDuty, Inspector, Macie, Security Hub | CloudTrail vs Config vs CloudWatch in one line each |
| 8 | Wed 25 Nov | **VPC** in full (your 13 Nov weak spot): CIDR, subnets, IGW, NAT Gateway vs NAT instance, route tables, SG vs NACL (stateful vs stateless, ephemeral ports), VPC endpoints (gateway vs interface), peering, Transit Gateway, Site-to-Site VPN, Direct Connect, Flow Logs, PrivateLink; **disaster recovery** (backup and restore, pilot light, warm standby, multi-site; RPO/RTO), **migration** (DMS, SCT, Application Migration Service, the 7 Rs), Well-Architected pillars | Draw a 3-tier VPC with NAT and endpoints from memory; the 4 DR strategies from cheapest to fastest |
| 9 | Thu 26 Nov | **Practice exam 1** (65 questions, timed, 130 min) in the morning. Review **every** question in the afternoon, including the ones you guessed right. Evening: **practice exam 2** if your score was 75%+ | **Go/no-go gate** (below) |
| 10 | **Fri 27 Nov** | **Exam.** Morning: only your one-line "use it when" list, no new material | |

### Go/no-go gate (Thu 26 Nov evening)

- **Sit the exam on 27 Nov** if you score **75% or more on two full timed practice exams** (most course and practice-test authors make theirs a bit harder than the real exam).
- **Reschedule** (more than 24 hours before the slot) if you're under 70%. Move the exam 5–7 days later. Spend those days on your weakest domain plus one practice exam every other day.
- **Between 70% and 75%:** sit only if your misses are spread across domains. If they cluster in one domain, reschedule and fix that domain.

Rescheduling isn't failing. Failing costs another 150 USD and a retake wait.

## Practice exams

- Use the practice exams that come with your Udemy course (or the instructor's separate practice-test course), plus the free official practice question set on AWS Skill Builder.
- Tutorials Dojo (Jon Bonso) practice exams are a widely used extra set if you want more questions.
- **Review method for each question:** why the right answer is right, **and why each wrong option is wrong**. That second half is where most of the learning happens.

## Exam-day technique

- Read the **last line first**: "MOST cost-effective", "LEAST operational overhead", "MOST secure", "highest availability". That phrase decides between two otherwise-correct answers.
- Keyword hints:
  - "least operational overhead" → managed or serverless.
  - "decouple" → SQS/SNS/EventBridge.
  - "real-time streaming" → Kinesis.
  - "millisecond reads, key-value" → DynamoDB (microseconds → DAX).
  - "on-premises file share, low latency" → Storage Gateway / FSx.
  - "static content globally" → S3 + CloudFront.
- Eliminate 2 wrong options first, then choose between the last 2.
- Flag and move on after 2 minutes. Come back at the end. **Never leave a question blank**; there's no penalty for guessing.

## Where this helps your interviews

VPC/NAT, ELB, RDS Multi-AZ, IAM roles, S3 policies and CloudWatch come up in AWS admin and SRE interviews. When you study them, also say the troubleshooting angle out loud (`interview-prep/aws-troubleshooting-playbook.md`, in PR #12 until it is merged). The exam asks "which service"; interviewers ask "it's broken, what do you check".
