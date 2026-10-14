# 01 · Inference Fundamentals

> **Source:** *Inference Engineering* by Philip Kiely (Baseten), introduction and Figure 0.1. Written in my own words, plus explanations added to make each idea clear.

## What is inference? ⭐

A generative AI (Artificial Intelligence) model has **two phases** in its life:

| | Training | Inference |
|---|---|---|
| What it is | **Learning** the model weights from data | **Serving** the model in production |
| Input | Huge dataset (text, code, images) | One user's prompt |
| Output | Model weights (billions of numbers) | An answer (text, image, audio) |
| How often | Once, or now and then | All the time, for every request |
| Speed needed | Can take weeks | Must answer in seconds or less |
| Who waits | Researchers | Real users, live |
| Main goal | Make the model **smart** | Make the model **fast, cheap and reliable** |

![The two phases: training creates the weights, inference serves them](diagrams/01-training-vs-inference.drawio.svg)

**Analogy:** training is a chef **learning recipes** in cooking school: once, slow and expensive. Inference is the chef **cooking orders** in a busy restaurant every day: fast, again and again, for real customers who are waiting. Inference engineering is running that restaurant well.

**Weights**, in one line: the numbers the model learned during training. The model's "knowledge" is stored in them. At inference time you load these weights onto GPUs (Graphics Processing Units) and run the user's input through them.

## Classic ML inference vs generative AI inference ⭐

In the last decade's ML (Machine Learning) boom, lots of data scientists and ML engineers learned the full lifecycle, training **and** inference. But inference for those **classic** models was easy. Baseten's early customers ran models built with tools like XGBoost (eXtreme Gradient Boosting) on small CPUs (Central Processing Units) with a simple software stack.

Generative AI inference is **much harder**:

| | Classic ML (for example XGBoost) | Generative AI (for example an LLM, Large Language Model) |
|---|---|---|
| Model size | KBs to MBs | GBs to hundreds of GBs |
| Hardware | Cheap CPUs | Expensive, scarce GPUs |
| One request does | One quick calculation → one answer (for example "fraud: yes/no") | Generates the answer **one token at a time**; each new token is another pass through the whole model |
| Request cost | Every request costs about the same | Varies hugely: a 10-word answer vs a 2,000-word answer |
| Serving it | Like any small web API | Needs special engines, GPU memory tricks and careful scaling |

**Token**, in one line: a small piece of text, roughly ¾ of an English word. An LLM writes its answer token by token, like typing one piece at a time.

**A real example of "too big":** a 70-billion-parameter model (like Llama 3 70B) stored in 16-bit numbers needs about **140 GB** just for its weights (70 billion × 2 bytes). One NVIDIA H100 GPU has **80 GB** of memory. So the model **doesn't even fit on one GPU**; you must split it over at least two, before you've served a single user.

**The key sentence from the book (in my words):** you can't just take model weights, get some GPUs, and expect inference to be **fast and reliable enough** for large-scale production. It needs engineering.

## The three layers of good inference ⭐

Doing inference well needs **three layers**:

| Layer | Question it answers | Scope |
|---|---|---|
| **1. Runtime** | How fast can **one copy** of the model run? | One model on one GPU-backed instance (one machine with GPUs) |
| **2. Infrastructure** | How do we run **many copies** everywhere, without breaking? | Across clusters, regions and clouds, with no silos and excellent uptime |
| **3. Tooling** | How do engineers work with all this **without drowning in detail**? | The right level of abstraction: enough control, without losing productivity |

These three layers must **work together**. Then you get a system that can handle **mission-critical inference at scale**: inference the product depends on, where "the model is down" means "the product is down".

![The complete inference stack: tooling, runtime and infrastructure](diagrams/01-inference-stack.drawio.svg)

### 1. Runtime: make one copy fast

- Focus: **a single model on a single GPU-backed instance**.
- Goal: squeeze the most speed (and the most users served) out of that one machine.
- Example questions: How many requests can share the GPU at once? Can we use smaller numbers for the weights? Can we skip work we've already done?
- If the runtime is slow, scaling just gives you **many slow copies** and a huge GPU bill.

### 2. Infrastructure: run many copies reliably

- Focus: **scaling across clusters, regions and clouds**.
- Two hard parts the book names:
  - **No silos.** A silo is GPU capacity locked into one cluster or one cloud. Then one region sits idle while another is overloaded. Good infrastructure treats all GPUs as **one shared pool**.
  - **Excellent uptime.** Users and products depend on the model being available all the time.
- This is the layer closest to my DevOps work (see the DevOps link below).

### 3. Tooling: the right level of abstraction

- Focus: the **engineers** who build and run inference.
- **Abstraction** means hiding detail. Too little and too much are both bad:
  - **Too low:** you control everything (raw CUDA code, hand-written config for every GPU node), but every change is slow and risky.
  - **Too high:** a black box that's quick to start, but you can't tune batching, quantization or scaling when you need to.
  - **Right level:** sensible defaults, with a way to reach in and change things when it matters.

> **DevOps link:** it's the same choice as raw Kubernetes YAML (full control, lots of work) vs Helm charts (a reusable layer with values you can override) vs a fully managed platform (easy, but little control). Good tooling is the "Helm" level: productive by default, controllable when needed.

## The stack map, box by box (Figure 0.1)

Read the picture **bottom to top** inside each layer. Each box gets its own deep dive later; for now, one line each.

### Runtime layer

| Box | What it is, simply |
|---|---|
| **CUDA** (Compute Unified Device Architecture) | NVIDIA's platform for running code on GPUs. Everything above it ends up as CUDA work on the GPU. |
| **PyTorch** | The most popular deep-learning framework. The model's code and maths are written in it. |
| **vLLM** | Open-source inference engine for LLMs. Takes a model and serves it fast. |
| **SGLang** | Open-source inference engine, a strong alternative to vLLM. |
| **TensorRT-LLM** | NVIDIA's inference engine for LLMs, tuned closely to NVIDIA GPUs. |

**Model performance techniques** (the six tricks the engines use to go fast; full deep dive in [03](03-model-performance-techniques.md)):

| Technique | The idea in one line |
|---|---|
| **Batching** | Run many users' requests through the GPU **together**, so the expensive hardware is never half-idle. |
| **Caching** | **Don't redo work.** The KV (Key-Value) cache keeps what the model already worked out for earlier tokens, so each new token is cheaper. |
| **Quantization** | Store weights with **fewer bits** (for example 8 or 4 bits instead of 16). Less memory, faster, small quality cost. |
| **Speculation** | A small, fast "draft" model **guesses** the next few tokens; the big model **checks** them all in one pass. Right guesses = free speed. |
| **Parallelism** | **Split** one model across several GPUs when it's too big or too slow for one (remember the 140 GB example). |
| **Disaggregation** | Run the two stages of a request on **separate** GPUs: **prefill** (read the whole prompt) and **decode** (write the answer token by token). They need different things, so they're tuned separately. |

### Infrastructure layer

| Box | What it is, simply |
|---|---|
| **GPUs** | The hardware that runs the model. Expensive and often hard to get. |
| **Storage** | Where the model weights live. Weights are GBs to hundreds of GBs, so loading them quickly matters. |
| **Networking** | Moves user requests in and answers out, and moves data **between GPUs** when one model is split across them. |
| **Multi-cloud capacity management** | Find and use GPUs across several clouds and regions, as one pool (no silos). |
| **Autoscaling** | Add GPU replicas (copies of the model) when traffic rises, remove them when it falls. |
| **Routing** | Send each request to the **right** replica (the right model, region, or a replica that already has useful cache). |
| **Load balancing** | Spread requests so no replica is overloaded while another is idle. |

> **DevOps link: the infrastructure layer is home ground, with twists.**
>
> | Inference box | What I already know | The GPU twist |
> |---|---|---|
> | Autoscaling | Kubernetes HPA (Horizontal Pod Autoscaler), Karpenter | A new GPU replica can take **minutes** to start (big container image + loading GBs of weights), so you can't scale only when it's already too late. CPU % is the wrong signal; queue length or requests in flight is better. |
> | Load balancing | ALB (Application Load Balancer), NGINX | Requests vary hugely in cost, so plain round-robin can pile long requests on one replica. "Least outstanding requests" style is better. |
> | Routing | Ingress rules, path-based routing | Also route to the replica that **already has this prompt's start in its cache**, to skip work. |
> | Multi-cloud capacity | Multi-region, multi-AZ (Availability Zone) setups | GPUs are scarce and quota-limited, so you take capacity wherever it exists. |
> | Storage | S3 (Simple Storage Service), EBS (Elastic Block Store), PVCs (PersistentVolumeClaims) | Pulling 140 GB from S3 on every cold start is slow; weights are cached close to the GPU. |
> | Networking | VPC (Virtual Private Cloud), DNS (Domain Name System), NAT (Network Address Translation) | Inside one split model, GPUs talk over special fast links (NVLink inside a machine, InfiniBand between machines). |

## One-line summary

**Training makes the weights; inference serves them to real users. Generative AI inference is hard because the models are huge, run on scarce GPUs and generate token by token, so doing it well needs three layers working together: a fast runtime, reliable infrastructure, and tooling with the right level of abstraction.**

## Check yourself (say it out loud)

- "What's the difference between training and inference?" → Training **learns** the weights from data, once, offline. Inference **serves** the model to real users, all the time, and must be fast and reliable.
- "Why was classic ML inference easy, and why is generative AI inference hard?" → Classic models are small, run on CPUs and answer in one quick step. Generative models are GBs to hundreds of GBs, need GPUs, and generate the answer token by token, with very different cost per request.
- "Can you just put the weights on a GPU and serve them?" → Not at production scale. Example: a 70B model at 16-bit is about 140 GB, and an H100 has 80 GB, so it doesn't even fit on one GPU.
- "What are the three layers?" → **Runtime** (one model, one GPU machine, fast), **Infrastructure** (many copies across clusters, regions and clouds, no silos, high uptime), **Tooling** (the right abstraction for engineers: control vs productivity).
- "What's a silo, and why is it bad?" → GPU capacity stuck in one cluster or cloud. One place sits idle while another is overloaded, and you pay for both.
- "Draw the stack." → Redraw the diagram above from memory and explain each box in one line.
