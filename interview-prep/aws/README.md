# AWS notes

Notes written while studying for the **AWS Certified Solutions Architect – Associate (SAA-C03)** exam, kept interview-ready. One file per course section; each starts with a diagram and ends with a from-memory drill and a 30-second spoken answer.

| # | Note | Covers |
|---|---|---|
| 01 | [IAM cheat sheet](01-iam-cheat-sheet.md) | Users, groups, policies (JSON, identity vs resource-based, inline vs managed, explicit deny), MFA, password policy, access keys, CLI on Ubuntu, CloudShell, roles and STS, credential report, access advisor, shared responsibility, best practices, 29 exam traps |
| 02 | [Global infrastructure](02-global-infrastructure.md) | Course section 3: regions, AZs (usually 3, min 3, max 6), data centers, 400+ edge locations, choosing a region (compliance, proximity, services, price), global vs regional services |
| 03 | [EC2 fundamentals](03-ec2-fundamentals.md) | Section 5: instance types and naming, user data, security groups (timeout vs refused), ports, SSH from Ubuntu and Instance Connect, all purchasing options, Spot requests and Spot Fleets |
| 04 | [EC2 associate](04-ec2-associate.md) | Section 6: public/private/Elastic IP, placement groups (cluster, spread, partition, precision time), ENI, Hibernate |
| 05 | [EC2 instance storage](05-ec2-instance-storage.md) | Section 7: EBS, delete on termination, snapshots (Archive, Recycle Bin, FSR), AMI, instance store, volume types (gp3/gp2/io1/io2 BE/st1/sc1), Multi-Attach, encryption, EFS, EBS vs EFS vs instance store, mounting on Ubuntu |
| 06 | [ELB and ASG](06-elb-asg.md) | Section 8: scaling vs HA, ALB/NLB/GWLB/CLB, LB security groups, sticky sessions, cross-zone, SSL/SNI, deregistration delay, ASG, launch templates, scaling policies, cooldown, ALB 502/503/504 |
| 07 | [RDS, Aurora, ElastiCache](07-rds-aurora-elasticache.md) | Section 9: RDS, storage auto scaling, read replicas vs Multi-AZ, RDS Custom, Aurora (endpoints, Serverless, Global, ML, Babelfish), backups/restore/cloning, security, RDS Proxy, ElastiCache Redis vs Memcached, caching patterns, DB ports |

Course sections 1–2 (intro, code download) have no note; the IAM note is course section 4. Facts were checked against the course slides (v49).

Diagrams live in [diagrams/](diagrams/) as `.drawio.svg` (open them in draw.io to edit). They use the official AWS Architecture Icons, vendored in [tools/aws-icons/](../../tools/aws-icons/) and embedded in each file so GitHub shows them. They are generated once by `python3 tools/diagrams_aws.py`; existing files are skipped unless you pass `--force`.
