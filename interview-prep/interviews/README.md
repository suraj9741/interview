# Interviews: questions, answers and prep notes

Everything from real interviews in one place: what they asked, the answers, the reviews of what went wrong, and the prep packs used before each round. One folder per interview, newest last. Topic notes (networking, Docker, Kubernetes, Helm, Terraform, AWS SAA) stay in their own folders under [interview-prep/](../).

> **How to use this folder.** Don't re-read it. Pick an interview folder, open the questions, and **type your answer before you open the model answer**. Every interview so far went wrong the same way: the notes existed, but the answer couldn't be recalled under pressure.

## Interviews

| Date | Company / round | Folder | What's inside |
|---|---|---|---|
| 9 Oct 2026 | One2N (Hemant Kumar), DevOps/SRE | [2026-10-09-one2n-hemant/](2026-10-09-one2n-hemant/) | [58 past questions](2026-10-09-one2n-hemant/hemant-past-interview-questions.md) and [model answers](2026-10-09-one2n-hemant/hemant-model-answers.md), [scenario deep dives](2026-10-09-one2n-hemant/hemant-scenario-deep-dives.md) (Helm drift, overlapping CIDRs, pod CIDR), [diagram review](2026-10-09-one2n-hemant/interview-review-oct-9.md) and [transcript review](2026-10-09-one2n-hemant/interview-transcript-review-oct-9.md), [CTO-level SRE discussion guide](2026-10-09-one2n-hemant/cto-sre-discussion-guide.md), prep plans ([5–9 Oct](2026-10-09-one2n-hemant/study-plan-oct-5-9.md), [3-day](2026-10-09-one2n-hemant/devops-interview-prep-plan.md)) |
| 11 Nov 2026 | NiCE Actimize (R Systems), App Support Engineer / SRE | [2026-11-11-nice-actimize-sre/](2026-11-11-nice-actimize-sre/) | [Cheat sheet](2026-11-11-nice-actimize-sre/nice-actimize-sre-cheatsheet.md) used before the round, [interview review](2026-11-11-nice-actimize-sre/interview-review-nov-11-nice.md) with corrected answers (SQL DML, grep -E, sed -i, find -mtime, pod startup) and a drill |
| 13 Nov 2026 (round 1), 19 Nov 2026 (L2) | AWS Admin Engineer | [2026-11-13-aws-admin/](2026-11-13-aws-admin/) | [AWS troubleshooting playbook](2026-11-13-aws-admin/aws-troubleshooting-playbook.md) (13 scenarios), [interview stories](2026-11-13-aws-admin/aws-interview-stories.md) from the resume, [L2 prep pack](2026-11-13-aws-admin/aws-admin-l2-prep.md) (round-1 misses, SSL incident story, deep dives), [the 14 questions asked in L2 with answers](2026-11-13-aws-admin/l2-asked-19nov-answers.md), [Replicate third-party incident story](2026-11-13-aws-admin/incident-story-replicate.md), [full VPC/NAT/ALB Terraform](2026-11-13-aws-admin/terraform-vpc/main.tf) (`terraform validate` passed) |
| 14 Nov 2026 | PTC, Senior DevOps Engineer | [2026-11-14-ptc-devops/](2026-11-14-ptc-devops/) | Answers to all 24 questions ([round 1](2026-11-14-ptc-devops/round-1/), [round 2](2026-11-14-ptc-devops/round-2/)), [self-test](2026-11-14-ptc-devops/self-test.md), 17 diagrams |
| 19 Nov 2026 | Kentik, Sr SRE | [2026-11-19-kentik-sre/](2026-11-19-kentik-sre/) | [Prep pack](2026-11-19-kentik-sre/README.md): JD mapping, GitOps/K8s/monitoring/Terraform/Python drills, and tested [lab scripts](2026-11-19-kentik-sre/labs/) |

## Question bank (shareable)

[question-bank/](question-bank/): the questions from the Nov 2026 rounds, by topic, with answers and no personal details.

- [DevOps/SRE questions](question-bank/devops-sre-interview-questions-nov-2026.md) ([PDF](question-bank/devops-sre-interview-questions-nov-2026.pdf)): 45 questions over 10 topics.
- [Linux questions](question-bank/linux-interview-questions-nov-2026.md) ([PDF](question-bank/linux-interview-questions-nov-2026.pdf)).

## Preparation

[preparation/](preparation/): study plans and practice material that isn't tied to one interview.

- [15-day SRE plan](preparation/15-day-plan/README.md): day-by-day lessons with labs (Ubuntu), the restart recall test and the grep reference. Paused for the AWS SAA exam.
- [Scenario questions](preparation/scenario-questions/README.md): 27 scenario answers (AWS, Docker, Kubernetes, Terraform, Prometheus), each with a diagram and a from-memory drill.
- [AWS SAA plan](preparation/aws-saa-plan.md): the exam plan (course sections, practice exams, go/no-go gate). The SAA cheat sheets themselves are in [interview-prep/aws/](../aws/) once that PR merges.

## Diagrams

Shared interview diagrams are in [diagrams/](diagrams/) (`.drawio.svg`, editable in draw.io). PTC, the 15-day plan and the scenario questions keep their own `diagrams/` folders. The generators are in [tools/](../../tools/): `diagrams_review.py`, `diagrams_model_answers.py`, `diagrams_scenarios.py`, `diagrams_guides.py`, `diagrams_nice.py`, `diagrams_aws_admin.py`, `diagrams_ptc.py`, `diagrams_plan.py`, `diagrams_scenario_qa.py`.
