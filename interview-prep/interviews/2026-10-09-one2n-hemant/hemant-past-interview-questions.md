# Past Interview Questions: Hemant Kumar (One2N)

These 58 questions are from Hemant's last interview. Use them as your main question bank.

---

## What these questions tell us

- **Fundamentals come first.** 25 of the 58 questions are about DNS, IP addressing, TCP/HTTP and Linux.
- **He asks you to do it live.** Several questions (marked 🖥️) mean running a command or sharing your screen. Practise the commands, don't just read about them.
- **Every answer gets a "why?"** Questions come in chains (13 → 14 → 15 → 16, and 37 → 38 → 39). Know the reason behind each step.
- **Clarify before you debug.** Question 27 shows he expects you to ask what "not working" actually means before you start fixing.
- **Design at scale on a budget.** Questions 41–51 are open design problems: database scaling, a zero-downtime migration, observability and hybrid connectivity.
- **Closing feedback = known gaps.** Questions 55–58 (marked 🔥) were assigned as homework at the end. Treat them as top priority.

## How to use this file

- Tick a question only when you can answer it **out loud, in under 2 minutes, without notes**.
- 🖥️ = he may ask you to do it live.
- 🔥 = flagged in his closing feedback.

---

## 1. DNS and name resolution

- [ ] **1.** Walk me through everything that happens when you type mixy.com in the browser.
- [ ] **2.** What is the very first step? What does the browser do before anything else?
- [ ] **3.** 🖥️ What is `resolv.conf`? How does the system know which resolver to use?
- [ ] **4.** 🖥️ How would you find the name servers for google.com? Which command?
- [ ] **5.** 🖥️ Which DNS utility comes pre-installed on macOS?
- [ ] **6.** What is the difference between `google.com` and `google.com.` with a trailing dot?
- [ ] **7.** What does "non-authoritative answer" mean?
- [ ] **8.** What is the `Address` field in that output?
- [ ] **9.** Explain the hierarchy of root, TLD and authoritative name server. Who answers what?

## 2. IP addressing

- [ ] **10.** Is that a private or a public IP address? Why do you say so?
- [ ] **11.** If it is private, how is your laptop communicating with it?
- [ ] **12.** Which ranges are private? Class A, B and C, with the actual boundaries.

## 3. TCP, UDP and HTTP

- [ ] **13.** You have the IP address. What happens next?
- [ ] **14.** Why does it need to create a TCP connection?
- [ ] **15.** What is TCP? If not TCP, what else could you use, and what is the difference?
- [ ] **16.** 🖥️ Prove the notion that HTTP is built on top of TCP.
- [ ] **17.** 🖥️ Open the browser network tab and explain what the request is actually doing.

## 4. Linux: processes, memory, ports

- [ ] **18.** 🖥️ Run `top` and explain everything on the screen.
- [ ] **19.** What is load average? What is it actually measuring?
- [ ] **20.** Why do sleeping processes appear there? Why should they be there at all?
- [ ] **21.** What is PPID?
- [ ] **22.** What are threads in that output, and how do they relate to cores?
- [ ] **23.** 🖥️ Find which process is occupying port 8080 on a given machine.
- [ ] **24.** 🖥️ In `netstat` output, what are Recv-Q and Send-Q? How are they useful when debugging?
- [ ] **25.** The laptop has 8 GB but `free` shows 6 GB. Where did the other 2 GB go?

## 5. Debugging methodology

- [ ] **26.** `example.com/ABC` works but `example.com/DEF` does not. What is your debugging approach?
- [ ] **27.** What do you need to ask me first? Ask me what "not getting accessed" means.
- [ ] **28.** It returns 502. What do 501, 502 and 503 each mean?
- [ ] **29.** Given a 5xx, what do you check, and in what order?
- [ ] **30.** 🖥️ How do you check whether load balancer targets are healthy?

## 6. Ansible and configuration management

- [ ] **31.** How would you scale Ansible automation across cloud and on-prem, for stateful databases and stateless servers?
- [ ] **32.** How does Ansible work? What protocol does it use underneath?
- [ ] **33.** Your playbook takes five minutes but the server's SSH daemon timeout is three minutes, so it fails. How do you handle that?
- [ ] **34.** How do you safely change automation you are hesitant to touch?

## 7. CI/CD and delivery

- [ ] **35.** What is your suggestion around CI/CD overall?
- [ ] **36.** How do you maintain sanity between local development and the development environment?
- [ ] **37.** Every branch merge means a rebuild. How do you reduce lead time to production?
- [ ] **38.** So you are saying I do not rebuild. What happens instead?
- [ ] **39.** If the dev image is deployed to QA, GitHub shows a divergence between the branch and what is running. How do you solve that?
- [ ] **40.** What security would you put around CI/CD and the network footprint?

## 8. Database and migration

- [ ] **41.** The database will not scale. What would you propose?
- [ ] **42.** How would you migrate Postgres from EC2 to RDS with live customer data and no downtime?
- [ ] **43.** Why can't Postgres on EC2 just sync to RDS asynchronously? Why complicate it with dual writes?
- [ ] **44.** Ten queries are slow. How do you go about optimising them?

## 9. Observability

- [ ] **45.** We have zero observability. How would you build the stack, at our future scale, on a tight budget?
- [ ] **46.** 🖥️ Draw the flow architecture. How would it look?
- [ ] **47.** How would you monitor the on-premise services too?
- [ ] **48.** Exporters will not surface slow-query detail. How do you get deep database metrics?
- [ ] **49.** How does Loki actually work, and when would you choose it over CloudWatch?

## 10. Hybrid connectivity

- [ ] **50.** How do you establish connectivity between AWS and on-prem? What are the best practices?
- [ ] **51.** How would you scale that connectivity model as services grow?

## 11. Consulting and framing

- [ ] **52.** Introduce yourself.
- [ ] **53.** Do you have exposure to a customer like ours, social media, in the past?
- [ ] **54.** 🖥️ Share your screen and walk us through how you are thinking about requirements and the roadmap.

## 12. 🔥 Assigned in their closing feedback

- [ ] **55.** 🔥 What do shift-left principles actually mean in a pipeline?
- [ ] **56.** 🔥 CI/CD security and OWASP: the top risks and where each control sits.
- [ ] **57.** 🔥 OS security: how secrets leak, and how to prevent a repeat of the key incident.
- [ ] **58.** 🔥 Linux and networking fundamentals end to end.

---

## Commands to practise for the 🖥️ questions

**Use a Linux shell for the Linux questions.** `free` and `ss` don't exist on macOS, and macOS `top` looks different from Linux `top`. Start a throwaway Ubuntu container and install the tools inside it:

- `docker run -it --rm ubuntu bash`
- `apt update && apt install -y procps iproute2 net-tools dnsutils curl netcat-openbsd lsof tcpdump sysstat psmisc iputils-ping`
- `sysstat` gives `iostat`, and `psmisc` gives `pstree` and `fuser`. Inside the container you're already root, so leave out `sudo`.

| Topic | Commands |
|---|---|
| DNS (Q3–9) | `cat /etc/resolv.conf` · `scutil --dns` (macOS) · `dig google.com` · `dig NS google.com` · `dig +trace google.com` · `nslookup google.com` · `host google.com` |
| IP (Q10–11) | `ip addr` (Linux) · `ifconfig` (macOS) · `ip route` / `netstat -rn` |
| TCP/HTTP (Q16–17) | `curl -v http://example.com` · `nc example.com 80`, then type an HTTP request by hand · `sudo tcpdump -i any port 80` · browser DevTools → Network tab |
| Processes (Q18–22) | `top` · `uptime` · `nproc` · `ps -ef` · `ps -eLf` (threads) |
| Ports (Q23–24) | `ss -tlnp` · `netstat -tlnp` · `lsof -i :8080` · `ss -tn` (look at Recv-Q and Send-Q) |
| Memory (Q25) | `free -h` · `cat /proc/meminfo` |
| 5xx debugging (Q28–30) | `curl -I` · `curl -v` · `aws elbv2 describe-target-health --target-group-arn <arn>` |
