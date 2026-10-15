# How to Handle the "General Discussion" with a CTO-Level SRE

They're not checking commands (Hemant did that). They want **how you think**, **whether they can trust you with production**, and **whether you can talk to clients and teams**.

![How a CTO-level SRE call usually flows](diagrams/c1-call-flow.drawio.svg)

## 1. What they're really checking

| They ask themselves… | You show it by… |
|---|---|
| Understands *why*, not just *how*? | The reason behind every tool or step |
| Trust them with production? | Incident stories: calm, fix first, then root cause |
| Connects tech to business? | Impact: downtime, users, cost, delivery speed |
| Sees trade-offs? | "A gives X but costs Y", never "always use Kubernetes" |
| Honest? | "I haven't done that in production, but here's how I'd approach it" |
| Learns fast? | What you're learning now, and how |
| Can talk to clients? | Clear, brief answers; questions; no jargon to show off |

> A senior spots bluffing in 10 seconds. Honesty + clear thinking beats a fake "expert" answer.

## 2. Your intro (60–90 seconds, practise 5× out loud)

1. **Now:** "I'm a DevOps engineer with __ years, at __, working on __."
2. **Day to day:** "AWS, Kubernetes/EKS, Docker, CI/CD with __, Terraform."
3. **1–2 achievements with a number:** "cut deploy time from __ to __ minutes by __" · "set up __, which cut alert noise / cost / incidents by __".
4. **Why this role:** "deeper into reliability and platform engineering; One2N solves these for many clients; I like your problem-first approach (the SRE bootcamp)."

⚠️ Every word in your intro becomes a follow-up. Say only what you can defend.

## 3. How to answer any open question

![Two shapes for any open question](diagrams/c2-answer-frameworks.drawio.svg)

## 4. Story bank (fill tonight, bullets only, 2 minutes each)

| Story | Your example | Number / result |
|---|---|---|
| 🔥 Production incident (detect → mitigate → root cause → prevent) | | |
| ⚙️ Toil you automated | | |
| 💰 Cost or performance win | | |
| 😬 Your mistake: own it, the fix, the guardrail added. Never blame | | |
| 🤝 Disagreement with a dev / lead, and how it was solved | | |

## 5. Questions they often ask (know the direction)

![SLI, SLO and error budget](diagrams/c3-slo-error-budget.drawio.svg)

| Question | Direction of a good answer |
|---|---|
| What does reliability mean? | Users can do what they need, when they need it. Measured with **SLIs/SLOs**, not just uptime. |
| 100% reliable? | No: too expensive, slows features. Pick an SLO (99.9%); the gap is the **error budget**. |
| SRE vs DevOps? | DevOps = culture (dev + ops together). SRE = one concrete way: software engineering, SLOs, error budgets, less toil. |
| Speed vs stability? | Error budget: left → ship; burnt → fix reliability. Data, not a fight. |
| Alert fatigue? | Alert on **symptoms users feel** (errors, latency); every alert actionable; remove noisy ones. |
| In an outage? | Communicate, **mitigate first** (rollback, failover, scale), root cause, **blameless postmortem**. |
| What is toil? | Manual, repetitive, no lasting value. Automate, self-service or remove it; give a real example. |
| Measure a DevOps team? | **DORA:** deploy frequency, lead time, change failure rate, time to restore. |
| First 30 days at a client? | Listen and map; secure obvious risks (secrets, backups that restore, basic alerts); one visible quick win. |
| Learning now? | Specific and honest: "Kubernetes internals and security; this week I practised __." |
| Why leave / why One2N? | Positive only: growth, harder problems, many clients, strong engineers. |

## 6. Phrases

| When | Say |
|---|---|
| Starting | "Can I ask a clarifying question first?" · "Let me think for a second." · "High level first, then deeper if you want." |
| Trade-offs | "It depends on __. If __, I'd choose __." · "The trade-off is cost vs speed." |
| Don't know | "I haven't used that in production. My understanding is __; I'd confirm by __." |
| Ending | "Does that answer it, or should I go deeper into __?" |
| **Avoid** | Bluffing, made-up numbers, blaming people, 3-minute monologues, "always / never / best tool", buzzwords you can't explain |

## 7. Questions to ask them (pick 2–3)

- "What reliability problems do you see most when you first join a client?"
- "Do clients usually work with SLOs, or does One2N help them adopt them?"
- "What separates a good SRE from a great one?"
- "What would success look like after 3–6 months in this role?"
- "How do engineers keep learning across so many client setups?"
- "How are on-call and incidents handled on client projects?"

Listen and react ("I've seen something similar when…"): it becomes a real conversation.

## 8. Checklist

| When | Do |
|---|---|
| Night before | [ ] Intro 5× out loud · [ ] fill the story bank, say each once · [ ] read section 5 once · [ ] 10 min on One2N's site and blog, one thing to mention |
| 30 min before | [ ] Laptop charged, internet, camera at eye level, quiet, good light · [ ] water, notepad, pen · [ ] Slack off; terminal and draw.io ready · [ ] 3 slow breaths |
| During | [ ] Smile, use their name once · [ ] look at the camera · [ ] wrong answer? "Actually, let me correct that…" |
| End | [ ] "Thank you, I enjoyed this, especially the part about __." |
