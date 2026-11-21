# Restart recall test · Tue 17 Nov (20 minutes, typed, no notes)

Take this before you open any lesson. It covers what you studied on 12 Nov (Day 1 Part A) plus the questions you missed in the 11 Nov (NiCE) and 13 Nov (AWS Admin) interviews.

**Rules**
- Type every answer in a blank file (`restart-test.txt`). Don't write answers in your head: what you can't type, you don't know.
- No notes, no Google, no scrolling down. Set a 20-minute timer.
- When the timer ends, open each answer and mark yourself: 1 point if it's correct and complete, 0 if not. "Almost" counts as 0.
- Write every 0 into `misses.md` as `17 Nov · question · right answer in my own words`.

**What your score means**
- **Linux section (Q1–7) below 5:** spend 9:30–10:30 redoing the Day 1 Part A labs, then start Part B.
- **Total 15 or more out of 19:** go straight to Day 1 Part B.
- **Total below 10:** don't panic and don't re-plan. You'll still do Day 1 Parts B and C today. The misses come back in tomorrow's 9 AM test.

---

## A. Linux (Day 1 Part A)

Run `bash make-logs.sh` again first if your `lab/` folder is gone. `lab/app.log` has lines like `2026-11-12 10:01:02 ERROR [txn-0061] user=ravi Connection refused db:5432`.

1. Print the lines in `app.log` that contain ERROR **or** WARN.
2. Count the ERROR lines. Then: when do `grep -c ERROR app.log` and `grep ERROR app.log | wc -l` give different answers? Do they ever?
3. Print the top 3 users by number of lines, with their counts. Why must `sort` come before `uniq`?
4. Replace every `http://` with `https://` in `configs/app.properties`, in place, keeping a backup.
5. Find `.log` files under `old/` older than 60 days and delete them. What do you run first, before deleting?
6. Run `./deploy.sh` and send both normal output and errors to `deploy.log`.
7. Which grep flags do these: ignore case · show line numbers · show lines that do NOT match · count · print only the matched part?

## B. SQL (the NiCE misses)

8. What is the family name for INSERT, UPDATE and DELETE? Name all five families, with one command each.
9. Insert one row into `users(id, name, city)`: id 7, name Ravi, city Pune.
10. Delete the user with id 7, written so that you can undo it if you made a mistake.

## C. AWS and networking (the 13 Nov misses)

11. A private EC2 instance can't reach the internet (`yum update` hangs). List your checks in order.
12. In the interview you said "3 private subnets and 1 public subnet, ALB in front". What's wrong with that?
13. ALB returns 502, 503 or 504. Give one typical cause for each.
14. The TCP 3-way handshake: name the three packets in order.
15. What does `dig` show? What does `traceroute` show? What does `dig +trace` show?

## D. Terraform (you said "I didn't practise")

16. Type a resource block for an S3 bucket named `suraj-logs-2026` with a tag `env = "dev"`.
17. In a team, where does the state file live, and what stops two people from running `apply` at the same time? Type the backend block.

## E. Kubernetes (the NiCE miss)

18. A pod starts. Name the 3 control-plane steps and the 8 steps on the node, in order.
19. Which step failed for each of these: `Pending`, `ImagePullBackOff`, `CrashLoopBackOff`, `Running 0/1 Ready`?

## F. Spoken (not scored, but do it)

20. Record a 60-second phone answer to "A private EC2 can't reach the internet. What do you check?" Play it back and count every "like" and "means like". Write the count in `misses.md`. The target is under 5.

---

## Answers (open only after the timer ends)

<details><summary>1. ERROR or WARN</summary>

```bash
grep -E "ERROR|WARN" app.log
# same thing: grep -e ERROR -e WARN app.log
```
Plain `grep "ERROR|WARN"` searches for the literal text `ERROR|WARN`. You need `-E` (extended regex) for `|` to mean OR.
</details>

<details><summary>2. grep -c vs grep | wc -l</summary>

```bash
grep -c ERROR app.log
grep ERROR app.log | wc -l
```
Both count **lines** that match, so for one file they print the same number. They differ when:
- **Several files:** `grep -c ERROR *.log` prints one count per file, but `grep ERROR *.log | wc -l` prints one total.
- **Counting matches, not lines:** if a line has ERROR twice, both still count 1. To count every match, use `grep -o ERROR app.log | wc -l` (`-o` prints each match on its own line).

`wc` alone prints lines, words and bytes; `wc -l` prints lines only.
</details>

<details><summary>3. Top 3 users</summary>

```bash
grep -o "user=[a-z]*" app.log | sort | uniq -c | sort -rn | head -3
```
`uniq` only merges **adjacent** identical lines. Without `sort` first, `ravi, amit, ravi` stays three separate lines. `uniq -c` adds the count. Then `sort -rn` orders by that count: `-n` compares as numbers (so 10 comes after 9, not before 2), and `-r` puts the biggest first.
</details>

<details><summary>4. sed in place with backup</summary>

```bash
sed -i.bak 's#http://#https://#g' configs/app.properties
```
`-i.bak` edits the file and keeps the original as `configs/app.properties.bak`. Using `#` as the delimiter avoids escaping every `/`. `g` replaces every match on the line, not just the first. On a Mac (BSD sed), `-i.bak` works too; plain `-i` needs `-i ''`.
</details>

<details><summary>5. find older than 60 days</summary>

```bash
find old/ -name "*.log" -type f -mtime +60          # first: look at the list (70, 90, 120 days)
find old/ -name "*.log" -type f -mtime +60 -delete  # then delete
```
`-mtime +60` means modified more than 60 days ago. `-mtime -60` means less than 60 days ago. Always run it without `-delete` first.
</details>

<details><summary>6. stdout and stderr to one file</summary>

```bash
./deploy.sh > deploy.log 2>&1
```
`>` sends stdout (1) to the file, then `2>&1` sends stderr (2) to wherever 1 now points. The order matters: `2>&1 > deploy.log` leaves stderr on the screen. Bash shortcut: `&> deploy.log`.
</details>

<details><summary>7. grep flags</summary>

`-i` ignore case · `-n` line numbers · `-v` invert (non-matching lines) · `-c` count lines · `-o` only the matched part. More in [grep-every-flag.md](grep-every-flag.md).
</details>

<details><summary>8. SQL families</summary>

INSERT, UPDATE and DELETE are **DML** (Data Manipulation Language).
- **DDL** (Definition): CREATE, ALTER, DROP, TRUNCATE
- **DML** (Manipulation): INSERT, UPDATE, DELETE
- **DQL** (Query): SELECT
- **DCL** (Control): GRANT, REVOKE
- **TCL** (Transaction Control): COMMIT, ROLLBACK, SAVEPOINT
</details>

<details><summary>9. INSERT</summary>

```sql
INSERT INTO users (id, name, city) VALUES (7, 'Ravi', 'Pune');
```
Text goes in single quotes. Always list the columns.
</details>

<details><summary>10. Safe DELETE</summary>

```sql
BEGIN;
SELECT * FROM users WHERE id = 7;   -- check exactly what will go
DELETE FROM users WHERE id = 7;
-- check the row count it reports; if wrong: ROLLBACK;
COMMIT;
```
A DELETE without WHERE deletes **every row**. Running the SELECT with the same WHERE first is the habit interviewers want to hear.
</details>

<details><summary>11. Private EC2, no internet</summary>

1. **Route table** of the private subnet: `0.0.0.0/0 → nat-xxxx` (a NAT gateway).
2. **NAT gateway**: it's in a **public** subnet, its state is Available, and it has an Elastic IP.
3. **Public subnet route table**: `0.0.0.0/0 → igw-xxxx` (the internet gateway is attached to the VPC).
4. **Security group outbound** on the instance allows 443/80 (default SG outbound allows all).
5. **NACL** on both subnets: outbound 443/80 allowed, **and inbound ephemeral ports 1024–65535** for the replies (NACLs are stateless).
6. **DNS**: `enableDnsSupport` on the VPC; `dig amazon.com` works from the instance.
7. **Proof:** VPC Flow Logs (REJECT = SG/NACL), Reachability Analyzer; test with `curl -I https://aws.amazon.com`.

In the interview you answered how to SSH **into** the instance. This question is about traffic going **out**.
</details>

<details><summary>12. One public subnet with an ALB</summary>

An ALB needs **at least two subnets in two different Availability Zones**, so "1 public subnet" with an ALB isn't possible. A real setup has one public subnet per AZ (3 public + 3 private across 3 AZs), with a NAT gateway per AZ for high availability, or one NAT to save cost (one NAT is a single point of failure).
</details>

<details><summary>13. 502 / 503 / 504</summary>

- **502 Bad Gateway:** the target sent a bad response or closed the connection. Causes: app crashed mid-request, the app's keep-alive timeout is shorter than the ALB idle timeout, or HTTP vs HTTPS mismatch on the target port.
- **503 Service Unavailable:** the target group has **no registered targets** (empty, or every target deregistered). Precise detail: if targets are registered but **all** fail health checks, the ALB **fails open** and keeps sending traffic to all of them, so you usually see 502/504 from the broken app instead of 503.
- **504 Gateway Timeout:** the target didn't answer within the ALB **idle timeout** (60 s by default). Usually a slow app or a slow DB query.

In the interview you blamed 502 on unhealthy targets. Unhealthy targets mean the ALB stops routing to them (or fails open if all are unhealthy); a 502 is about a **bad response** from a target that did receive the request.
</details>

<details><summary>14. TCP handshake</summary>

**SYN** (client → server), **SYN-ACK** (server → client), **ACK** (client → server). Then data flows. Closing uses FIN and ACK in both directions. You gave only two steps in the interview.
</details>

<details><summary>15. dig vs traceroute</summary>

- `dig example.com`: the **DNS answer**: records, TTL, which resolver answered, and the status (NOERROR, NXDOMAIN, SERVFAIL).
- `traceroute example.com`: the **network hops** (routers) on the way to the IP.
- `dig +trace example.com`: the **DNS delegation chain**: root servers → `.com` servers → the domain's authoritative name servers.

"dig shows hops" was wrong in the interview; that's traceroute.
</details>

<details><summary>16. Terraform S3 bucket</summary>

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "suraj-logs-2026"

  tags = {
    env = "dev"
  }
}
```
Shape: `resource "<TYPE>" "<LOCAL_NAME>" { arguments }`. You refer to it elsewhere as `aws_s3_bucket.logs.arn`.
</details>

<details><summary>17. Remote state and locking</summary>

```hcl
terraform {
  backend "s3" {
    bucket         = "suraj-tf-state"
    key            = "prod/vpc/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    use_lockfile   = true            # S3 native locking, Terraform 1.10+
    # dynamodb_table = "tf-locks"    # older way; now deprecated
  }
}
```
State lives in a **versioned, encrypted S3 bucket**, not on a laptop. **Locking** (an S3 lock file, or a DynamoDB table on older setups) makes the second `apply` wait with "Error acquiring the state lock" instead of both writing at once and corrupting state. State can hold secrets, so the bucket must be private and encrypted.
</details>

<details><summary>18. Pod startup</summary>

**Control plane:** (1) API server saves the Pod in etcd, `Pending`, no node. (2) The scheduler filters → scores → binds (sets `nodeName`). (3) The kubelet on that node sees the pod.

**On the node:** (1) volumes, Secrets, ConfigMaps mounted. (2) Pod sandbox ("pause" container) through containerd/CRI. (3) CNI gives the pod IP. (4) Image pulled. (5) Init containers, one by one. (6) App containers start, then the postStart hook. (7) Probes: startup → liveness/readiness. (8) Ready → EndpointSlice → kube-proxy → traffic.

Diagram: [05-pods.md, "What happens when a pod starts"](https://github.com/suraj9741/interview/blob/main/interview-prep/kubernetes/05-pods.md#what-happens-when-a-pod-starts--the-question-missed-on-11-nov) (in PR #13 until it's merged).
</details>

<details><summary>19. Status → step</summary>

- `Pending`: scheduler (no node fits: requests too big, taint, affinity, PVC zone).
- `ImagePullBackOff`: image pull (wrong name/tag, registry auth, ECR permissions).
- `CrashLoopBackOff`: the app container starts and then exits (`kubectl logs --previous`; exit code 137 = OOMKilled).
- `Running 0/1 Ready`: readiness probe failing.
</details>
