# AWS Solutions Architect – Associate: re-plan from Fri 20 Nov 2026

**Updated Fri 20 Nov, 11:30 AM.** The course is Stephane Maarek's *Ultimate AWS Certified Solutions Architect Associate SAA-C03* on Udemy. **Sections 1–7 are done** (intro, IAM and CLI, EC2 basics, EC2 at associate level, EC2 instance storage).

**Recommendation: move the exam from Fri 27 Nov to Wed 2 Dec.** The go/no-go gate is now Tue 1 Dec.
- Two interview days (18 and 19 Nov) went to prep. About 25% of the course is done, and roughly 20 hours of video remain, including the two heaviest sections (S3 and VPC).
- Keeping 27 Nov would mean about 4 sections a day with **no full practice exam before the gate**. For someone who calls himself a slow learner, that's a plan to fail and pay 150 USD again.
- Wed 2 Dec gives the course 8 days and leaves 3 days for practice exams. **If you already booked 27 Nov, reschedule it today**: Pearson VUE allows it free if done at least 24 hours before the slot (check this in your booking).
- If a practice exam on Sun 29 or Mon 30 already scores 80%+, you can pull the exam earlier. Never push it later than the gate allows.

**Still true:** passing timed practice exams is the only evidence that counts. And the certificate doesn't fix the interview gaps (Linux, Kubernetes, typed recall), so the 4 PM interview-recall slot stays.

**Section numbers below follow the usual order of this course.** Udemy sometimes renumbers sections, so match them by **title** in your course list. If a title differs, keep the same order.

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
| 9:00–9:30 | Recall (today Fri 20: start at 11:30 with S8, skip this slot): yesterday's "use it when" lines and quiz misses, **typed from memory** |
| 9:30–12:30 | Course videos (Block 1) |
| 12:30–13:30 | Lunch, no screens |
| 13:30–16:00 | Course videos (Block 2) + section quizzes |
| 16:00–16:30 | **Interview recall (don't skip):** 3 items from `misses.md`, typed. Linux, TCP, pod startup, Terraform block, 502/503/504 |
| 16:30–17:00 | Revise today's weak spots from the slides |
| 17:00–17:30 | Send **"SAA day N quiz"** in the thread: I ask 10 exam-style scenario questions on today's topics, you answer without notes |
| 17:30 | Stop. Sleep 7+ hours. Memory consolidates during sleep, and the night before the exam matters most |

SQL and the 15-day plan stay **paused** until the day after the exam (see the note in [../15-day-plan/README.md](15-day-plan/README.md)).

## Day by day (from Fri 20 Nov)

| Day | Date | Course sections (match by title) | Done when |
|---|---|---|---|
| 1 | **Fri 20 Nov** (from 11:30) | **S8 High availability and scalability: ELB and ASG** (ALB/NLB/GWLB, target groups, health checks, sticky sessions, cross-zone, SSL/SNI, deregistration delay, ASG policies and cooldowns) · **S9 RDS, Aurora and ElastiCache** (Multi-AZ vs read replicas, Aurora Serverless and Global Database, RDS Proxy, backups, Redis vs Memcached) | Multi-AZ vs read replica in one line each; ALB vs NLB vs GWLB in one line each |
| 2 | Sat 21 Nov | **S10 Route 53** (record types, alias vs CNAME, all routing policies, health checks) · **S11 Classic solutions architecture discussions** · **S12 Amazon S3 introduction** (buckets, versioning, replication, storage classes) | Pick the routing policy for "send users to the lowest-latency region" (latency) and "active/passive" (failover) |
| 3 | Sun 22 Nov | **S13 Advanced S3** (lifecycle, Intelligent-Tiering, requester pays, event notifications, performance: multipart, Transfer Acceleration, byte-range) · **S14 S3 security** (SSE-S3/SSE-KMS/SSE-C, bucket policy vs IAM, Block Public Access, presigned URLs, CORS, MFA Delete, Object Lock, Access Points) · **S15 CloudFront and Global Accelerator** | The S3 class for "rarely accessed, needed in milliseconds" (Standard-IA / Glacier Instant Retrieval); CloudFront vs Global Accelerator in one line |
| 4 | Mon 23 Nov | **S16 AWS storage extras** (Snow family, FSx Windows/Lustre/NetApp/OpenZFS, Storage Gateway types, DataSync, Transfer Family) · **S17 Decoupling: SQS, SNS, Kinesis, Amazon MQ** (standard vs FIFO, visibility timeout, DLQ, fan-out, Data Streams vs Firehose) | SQS vs SNS vs Kinesis vs EventBridge in one line each; which Storage Gateway for an on-prem file share |
| 5 | Tue 24 Nov | **S18 Containers: ECS, Fargate, ECR, EKS** (launch types, task roles, App Runner) · **S19 Serverless overview** (Lambda limits and concurrency, DynamoDB capacity modes, DAX, streams, global tables, API Gateway, Step Functions, Cognito user vs identity pools) · **S20 Serverless solution architectures** | Draw a serverless API with auth from memory |
| 6 | Wed 25 Nov | **S21 Databases in AWS** (which DB for which need) · **S22 Data and analytics** (Athena, Redshift, OpenSearch, EMR, Glue, Lake Formation, QuickSight, MSK) · **S23 Machine learning** (names plus one use each) | Match 10 services to 10 one-line needs |
| 7 | Thu 26 Nov | **S24 Monitoring and audit: CloudWatch, EventBridge, CloudTrail, Config** · **S25 IAM advanced** (Organizations, SCPs, IAM Identity Center, permission boundaries, policy evaluation) · **S26 Security and encryption** (KMS, SSM Parameter Store vs Secrets Manager, ACM, WAF, Shield, GuardDuty, Inspector, Macie) | CloudTrail vs Config vs CloudWatch in one line each; Parameter Store vs Secrets Manager |
| 8 | Fri 27 Nov | **S27 Networking: VPC**, the whole day, **do the demos** (CIDR, subnets, IGW, NAT GW vs instance, route tables, SG vs NACL, endpoints gateway vs interface, peering, Transit Gateway, VPN, Direct Connect, Flow Logs, PrivateLink, egress costs). It's your interview weak spot too | Draw a 3-tier VPC with NAT and an S3 endpoint from memory |
| 9 | Sat 28 Nov | **S28 Disaster recovery and migrations** (4 DR strategies, RPO/RTO, DMS, Application Migration Service, the 7 Rs) · **S29 More solutions architectures** · **S30 Other services** · **S31 Whitepapers / Well-Architected**, then the **free official practice question set** on AWS Skill Builder | Course finished. The 4 DR strategies from cheapest to fastest |
| 10 | Sun 29 Nov | **Practice exam 1** (65 questions, timed, 130 min) in the morning. Afternoon: review **every** question, including lucky guesses. Write each miss as a "use it when" line | Score and weak domain written down |
| 11 | Mon 30 Nov | Morning: re-watch only the lectures behind yesterday's misses. Afternoon: **practice exam 2**, timed, then review | Second score |
| 12 | Tue 1 Dec | **Practice exam 3** (the course's last one, or Tutorials Dojo) in the morning, review in the afternoon. **Go/no-go gate at 6 PM** | Decision made |
| 13 | **Wed 2 Dec** | **Exam.** Morning: only your one-line "use it when" list, no new material | |

**If you fall behind:** don't skip the practice exams to finish videos. Drop S23 (ML) and S30 (other services) to slide speed (read the slides, no video). They're a small share of the exam.

### Go/no-go gate (Tue 1 Dec, 6 PM)

- **Sit on Wed 2 Dec** if **two** timed practice exams are at **75% or more** (course practice exams are a bit harder than the real one).
- **Reschedule** (more than 24 hours before the slot) if you're **under 70%**. Move 5–7 days, work on the weakest domain, one practice exam every other day.
- **70–75%:** sit only if the misses are spread across domains. If they cluster in one domain, reschedule and fix it.

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

VPC/NAT, ELB, RDS Multi-AZ, IAM roles, S3 policies and CloudWatch come up in AWS admin and SRE interviews. When you study them, also say the troubleshooting angle out loud ([aws-troubleshooting-playbook.md](../2026-11-13-aws-admin/aws-troubleshooting-playbook.md)). The exam asks "which service"; interviewers ask "it's broken, what do you check".
