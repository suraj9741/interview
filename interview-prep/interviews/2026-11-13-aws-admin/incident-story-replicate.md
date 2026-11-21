# Incident story: third-party dependency failure (Replicate AI balance)

Second incident story for the AWS Admin L2 round (19 Nov 2026), added to the drill on 18 Nov. Lead with the SSL expiry story for "your most serious incident"; use this one for "a third-party service failed" or "a monitoring gap you found".

**Question:** "Tell me about a time a third-party service your product depends on failed." (Your Replicate AI balance story, told properly.)

**When to use it:** for "a third-party / external dependency failure", "a monitoring gap you found", or as a **second** incident if they ask for another one. For "your most serious incident", lead with the SSL expiry story ([Part 2 of the L2 prep](aws-admin-l2-prep.md#part-2-your-incident-story-real-from-what-you-said-on-13-nov)), because that one shows you debugging a technical problem.

**The story (about 2 minutes). Fill every ⟨…⟩ with the real detail. If you don't remember one, say "roughly" or "I don't remember exactly". Never invent a number.**

- **Situation (20 s):** "At ⟨company⟩ we ran a social media platform where users create videos with AI. The video generation called **Replicate**, an external AI model API that we pay for with prepaid credit."
- **Trigger and impact (20 s):** "One ⟨day / time⟩, video generation started failing in production. Users ⟨saw errors / their videos never finished⟩. We found out from ⟨user complaints / the team / failed jobs⟩, not from an alert, and that was the first problem."
- **Actions (50 s):**
    1. "I checked our service logs for the failing requests. The calls to the Replicate API were coming back with ⟨the exact error you saw, e.g. a payment / insufficient credit error⟩."
    2. "That ruled out our own infrastructure: our pods, database and network were fine. The external dependency was rejecting us."
    3. "In the Replicate dashboard I confirmed the **account balance was exhausted**."
    4. "We ⟨who: I / my manager / finance⟩ topped up the balance, and I confirmed new video jobs succeeded again. It was down for about ⟨duration⟩."
- **Root cause (15 s):** "The real cause wasn't the balance. Nobody owned it and nothing watched it. We had monitoring on our own systems, but nothing on an external dependency we pay for in advance."
- **Prevention (20 s):** "I added a **low-balance alert** for Replicate ⟨how: their usage/billing alert setting / a scheduled check / a script⟩ that notifies ⟨channel / people⟩ before the credit runs out, so the team tops up early. ⟨Add only if true: we also wrote a short runbook / named an owner / turned on auto-recharge⟩."
- **Learning (10 s):** "Every external dependency needs two kinds of monitoring: its **errors** in our logs and metrics, and its **limits**, like balance, quota and rate limits. Our own dashboards being green doesn't mean the product works."

**What went wrong on 13 Nov:** you told it as "the balance is exhausted, we don't know what is happening, we top up". No impact, no detection, no steps, no root cause. The interviewer couldn't hear any engineering. The facts are the same; the structure is what makes it an incident story.

## Understand it

**Why this story is weaker than SSL expiry, and how to make it strong.** The interviewer is listening for **how you debug and what you change**. "We topped up" is a 1-minute fix with no debugging, so on its own it sounds like a billing task. What makes it worth telling is the **method**: you went from "videos fail" → logs → "the external API rejects us" → "our infrastructure is fine" → the dashboard → the balance. And the **lesson**: you monitored your own systems but not the things you depend on.

**Say the phrase "external dependency" out loud.** It turns "billing" into an SRE topic. Every system has dependencies outside its control: payment gateways, SMS providers, AI APIs, DNS providers. Good SREs monitor them like their own services.

**The two kinds of monitoring for any external API.**
- **Errors (what users feel):** the error rate and latency of calls to that API, from your app's logs or metrics. For example, alert if more than 5% of Replicate calls fail for 5 minutes. This would have caught the outage **whatever** the cause: balance, an API outage, an expired API key or a rate limit.
- **Limits (what's about to break):** balance, quota, rate limit and certificate expiry. A low-balance alert catches it **before** users notice.

The error-rate alert is the stronger answer, because it's general. If you only added the balance alert, say so honestly, and add "the next thing I'd add is an error-rate alert on the Replicate calls", which shows you understand the bigger picture.

**Graceful degradation (a senior touch).** When the dependency fails, what should users see? A clear message ("Video generation is busy, we'll notify you when it's ready"), with jobs queued and retried later, instead of a spinner forever. Mention it as "something we could improve", unless you really built it.

**Keep it honest.** Only claim what really happened. "I'd add" is a perfectly good answer for the parts you didn't do; interviewers respect that far more than a story that falls apart on the second question.

**Remember:** *Videos failed → logs → external API rejecting us → balance exhausted → topped up → low-balance alert. Lesson: monitor dependencies' errors and limits.*

## Follow-up questions they may ask

Answer each one out loud first, then open it.

<details><summary>How long were users affected, and how many?</summary>

Give only the real figures you know. If you don't know them: "I don't remember the exact duration; it was roughly ⟨x⟩, from the first complaint to the top-up." Never guess a precise number.

</details>

<details><summary>Why did nobody notice before users did?</summary>

"We monitored our own infrastructure (pods, ALB, database) but not the external API's errors or its balance. So everything looked green while the feature was broken. That's the gap we fixed."

</details>

<details><summary>How exactly did you set up the alert?</summary>

Describe what you really did (Replicate's billing alert, a scheduled script calling their API, or a manual reminder). If it was a simple email alert, say so, then add: "Better would be an error-rate alert on our side too, so any failure of the API pages us, not just the balance."

</details>

<details><summary>What if Replicate itself goes down?</summary>

"The balance alert wouldn't catch that, which is why the error-rate alert on our calls matters. Beyond that: retries with backoff, a queue so jobs aren't lost, a clear message to users, and a status-page check. For a critical feature, a second provider as a fallback."

</details>

<details><summary>How would you monitor any third-party API in general?</summary>

"Track every call's status code and latency as metrics (for example a Prometheus counter by provider and status), alert on error ratio and latency, watch quotas and rate-limit responses (429), keep API keys in Secrets Manager with expiry reminders, and keep a runbook with the provider's status page and support contact."

</details>

<details><summary>Who should own the balance, engineering or finance?</summary>

"Both, with a clear owner. Finance owns the budget, engineering owns the alert and the runbook, and the alert goes to both so a top-up can't fall between teams. Auto-recharge with a spend cap removes most of the risk."

</details>
