# 03 · Model Performance Techniques

> **Source:** *Inference Engineering* by Philip Kiely (Baseten), the runtime layer section, in my own words. Read [02](02-runtime-layer.md) first: everything builds on **prefill vs decode**, the **KV cache** and **memory-bound decode**.

![The six techniques: which part each one attacks](diagrams/03-techniques-map.drawio.svg)

| Technique | Attacks | Improves | Costs |
|---|---|---|---|
| **Batching** | Idle GPU during decode | Throughput, cost per token | A bit of per-user speed; KV memory |
| **Caching** | Recomputing the same prefix | TTFT, GPU work | GPU memory; needs cache-aware routing |
| **Quantization** | Big weights | Speed, memory, GPUs needed | Possible quality loss: test it |
| **Speculation** | One token per pass | Decode speed | Extra work; weak under heavy load |
| **Parallelism** | Model too big/slow for one GPU | Fits big models; lower latency | GPU-to-GPU communication |
| **Disaggregation** | Prefill and decode fighting | Steadier speed at scale | KV cache transfer; complexity |

## 1. Batching ⭐

![Static batching wastes slots; continuous batching refills slots at every step](diagrams/03-continuous-batching.drawio.svg)

- Weights read **once** per pass, used for **every** request in the batch → many tokens per memory trip.
- **Continuous** (NVIDIA: **in-flight**) batching = the book's "weaving them together token by token": batch re-formed every decode step, no idle slots.
- Bigger batch = more total tokens/s, each user a bit slower (taxi vs bus). Capped by **KV cache memory** (vLLM `--max-num-seqs`).

> **DevOps link:** a CI runner pool that starts the next queued job the moment any runner is free.

## 2. Caching (prefix caching) ⭐

![Request 2 reuses the cached system prompt and only computes its own 10 tokens](diagrams/03-prefix-caching.drawio.svg)

- Shared prefixes are everywhere: **system prompts**, **multi-turn chat** (turn 5 = turns 1–4 + one message), **few-shot examples**, **document Q&A**, **agents** (tool definitions + growing history).
- ⚠️ Only an **exact match from token one** counts. A timestamp at the top of the system prompt breaks everything after it → **fixed part first, changing part last**.
- Cache lives on **one replica** and is evicted when full → infrastructure needs **cache-aware routing**. vLLM and SGLang (**RadixAttention**) do it automatically.

> **DevOps link:** watch the **hit rate**; like sticky sessions, it only works if related requests hit the same server.

## 3. Quantization ⭐

![Does a 70B model fit on one 80 GB H100?](diagrams/01-gpu-memory-fit.drawio.svg)

| Format | Bytes per weight | 70B model |
|---|---|---|
| FP16 / BF16 | 2 | ~140 GB |
| FP8 / INT8 | 1 | ~70 GB |
| FP4 / INT4 | 0.5 | ~35 GB |

- **More compute:** H100 does FP8 maths ~**2×** FP16; B200 adds FP4.
- **Less memory:** fewer bytes per decode pass, **fewer GPUs**, more room for **KV cache**.
- Choose what to quantize: **weights** (most common), **activations**, **KV cache**; keep sensitive parts higher precision.
- ⚠️ FP8 is usually close to original; 4-bit is riskier. **Run evals** before and after.

> **DevOps link:** like compressing website images: test whether users notice, don't guess.

## 4. Speculation (speculative decoding)

![The draft model guesses 4 tokens; the target model checks them in one pass](diagrams/03-speculative-decoding.drawio.svg)

- Checking 4 tokens ≈ cost of making 1: the pass is mostly **reading weights**, idle maths absorbs the rest (a tiny prefill).
- Guessers: a **small draft model** (1B for a 70B), **extra heads** (EAGLE, Medusa), **prompt lookup / n-gram** (great for code edits).
- Best at low–medium load; under big batches the gain shrinks or turns negative. Watch the **acceptance rate**. **Quality unchanged:** the big model has the final word.

## 5. Parallelism

![Tensor, pipeline and expert parallelism](diagrams/03-parallelism.drawio.svg)

| Type | Splits | GPUs talk | Use when |
|---|---|---|---|
| **Tensor** | Every layer into pieces | After **every** layer | Lower latency, GPUs in one machine |
| **Pipeline** | Layers into stages (a relay) | Per stage hand-over | Too big for one machine (risk of bubbles) |
| **Expert** | MoE experts over GPUs | When tokens go to experts | MoE models (DeepSeek) |

- New bottleneck = GPU-to-GPU traffic: **NVLink** ~900 GB/s per H100 in a machine vs **InfiniBand/Ethernet** ~50 GB/s between machines.
- **Keep tensor parallelism inside one machine.** vLLM: `--tensor-parallel-size`, `--pipeline-parallel-size`.
- Full **replicas** are scaling out: infrastructure's job, not this.

> **DevOps link:** database sharding: cross-shard traffic becomes the limit.

## 6. Disaggregation

![Prefill and decode workers in separate pools, joined by a fast network](diagrams/03-disaggregation.drawio.svg)

- Same GPU: a big prefill **pauses everyone's decode** (stutter), one setup can't suit both, can't scale them apart.
- Cost: the KV cache **moves between machines** (~1 GB for 8k tokens on 8B) → fast network, usually **RDMA**. Pays off at **large scale, long prompts**.
- Lighter first: **chunked prefill** (prefill in chunks between decode steps; vLLM does it).
- Tools: NVIDIA Dynamo, llm-d, newer vLLM and SGLang.

> **DevOps link:** a monolith split into two microservices, each with its own HPA on its own metric, paying for network calls.

## Other modalities

| Modality | What | Which techniques |
|---|---|---|
| **VLM** | Image + text → text | An LLM with an image reader: all six |
| **Embeddings** | Text → vector (search, RAG) | One pass, **no decode**: batching, quantization; no speculation |
| **ASR** (Whisper) | Speech → text | Token by token: decode techniques apply |
| **TTS** | Text → audio | Often token by token; time to first audio matters |
| **Image generation** | Text → image | Denoising steps, not tokens: adapted quantization, parallelism, caching |
| **Video generation** | Text/image → video | Very heavy: parallelism across many GPUs |

- Rule: generates step by step like an LLM → nearly all six apply; single pass → no decode-only tricks.

*(The book's passage continues here; I'll add the rest when I read it.)*

## Check yourself (say it out loud)

| Question | Answer |
|---|---|
| Continuous vs static batching? | Batch re-formed every decode step; static leaves slots idle until the longest request ends. |
| Prefix caching: helps when, breaks how? | Shared starts (system prompt, history, docs). Any early change breaks it; must reach the replica holding the cache. |
| Quantization gain and cost? | Faster maths, fewer bytes, fewer GPUs, more KV room. Possible quality loss: evals. |
| Speculation: >1 token per pass, same quality? | Draft cheaply; the big model checks all in one pass (≈ cost of one, memory-bound) and keeps what it agrees with. |
| Tensor vs pipeline? | Tensor splits every layer, talks every layer (NVLink, one machine). Pipeline splits into stages, talks less, can span machines. |
| Why disaggregate? | Compute-heavy vs memory-heavy work interferes; separate pools scale and tune apart. Cost: moving the KV cache. |
| Techniques for an embedding model? | Batching and quantization; no decode, so no speculation or disaggregation. |
