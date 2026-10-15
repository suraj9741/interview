# 02 · The Runtime Layer

> **Source:** *Inference Engineering* by Philip Kiely (Baseten), the runtime layer section, in my own words, plus the basics the book assumes.

- **Job:** make **one model fast on one GPU-backed instance** ([01](01-fundamentals.md)).
- Book in short: a **deep software stack** (CUDA → PyTorch → engine) · **low-level optimization** (kernels like **FlashAttention**) · **six techniques** ([03](03-model-performance-techniques.md)).

> **DevOps link:** runtime = everything **inside one GPU pod**; infrastructure = everything about **many pods**.

## 1. Forward pass

- One run of the input through **all layers** → a score for every possible next token → one is picked.
- Every pass **reads all the weights** from GPU memory. This explains almost everything below.

## 2. Prefill and decode ⭐

![Prefill reads the prompt in one pass; decode writes the answer one token per pass](diagrams/02-prefill-vs-decode.drawio.svg)

| | Prefill | Decode |
|---|---|---|
| Does | **Reads** the whole prompt | **Writes** the answer token by token |
| Passes | **1**, all prompt tokens in parallel | **1 per output token** |
| Bottleneck | Maths (**compute-bound**) | Memory reads (**memory-bound**) |
| User feels | **TTFT** (time to first token) | **TPOT** (time per output token) |

- Every chatbot: a short pause (prefill + queue), then text streams (decode).

## 3. KV cache ⭐

![KV cache: saves recomputation, costs GPU memory](diagrams/02-kv-cache.drawio.svg)

## 4. Memory-bound vs compute-bound: the big "aha" ⭐

![Why decode is memory-bound](diagrams/02-memory-bound.drawio.svg)

| H100 limit | Rough number |
|---|---|
| **Compute** (FLOPS) | ~1,000 trillion 16-bit ops/s |
| **Memory bandwidth** (HBM) | ~3.35 TB/s |

## Throughput vs latency

- **Latency** = speed for **one user** (TTFT, TPOT) · **Throughput** = total tokens/s for **all users**.
- **Taxi vs bus:** fastest for one person vs most people per hour.
- GPUs are paid **per hour** → more tokens per hour = **lower cost per token**.

## The software stack

| Layer | What it is | DevOps comparison |
|---|---|---|
| **Inference engine** (vLLM, SGLang, TensorRT-LLM) | Batching, KV cache management, fast kernels, HTTP API | App server (Tomcat, Gunicorn) |
| **PyTorch** | The framework; calls kernels for the maths | Language runtime (JVM) |
| **Kernels** | Small programs **on the GPU**, one per operation | Hot, tuned library functions |
| **CUDA** | NVIDIA's platform + maths libraries | Drivers + system libraries |
| **GPU** | H100, B200… | The server |

## Low-level optimization: FlashAttention

![FlashAttention: same maths, far fewer memory trips](diagrams/02-flashattention.drawio.svg)

- FlashAttention: Tri Dao et al., 2022. Engines use it (or similar kernels) by default.
- Lesson: **same maths + smarter memory use = big speed-up**.

## Inference engines

What an engine adds on top of PyTorch:
- a **scheduler** for continuous batching ([03](03-model-performance-techniques.md));
- a **KV cache manager**, e.g. vLLM's **PagedAttention** (fixed-size pages, like OS virtual memory: little waste);
- **fast kernels**, quantization, multi-GPU support;
- an **OpenAI-compatible HTTP API**, so apps can switch engines.

| Engine | From | Known for |
|---|---|---|
| **vLLM** | UC Berkeley, big community | PagedAttention, huge model support; the common default |
| **SGLang** | LMSYS | RadixAttention (automatic prefix caching), fast structured output |
| **TensorRT-LLM** | NVIDIA | Compiles a model into an engine for NVIDIA GPUs; very fast, more setup |

> **DevOps link:** to Kubernetes an engine is **just a container asking for a GPU** (sketch, not tested; pin a real version):
>
> ```yaml
> containers:
>   - name: vllm
>     image: vllm/vllm-openai:latest
>     command: ["/bin/sh", "-c"]
>     args: ["vllm serve Qwen/Qwen2.5-1.5B-Instruct"]
>     ports:
>       - containerPort: 8000          # OpenAI-compatible API
>     resources:
>       limits:
>         nvidia.com/gpu: 1            # from the NVIDIA device plugin
> ```

## Check yourself (say it out loud)

| Question | Answer |
|---|---|
| Prefill and decode? | Prefill reads the prompt in **one** pass (compute-bound, TTFT). Decode writes **one token per pass** (memory-bound, TPOT). |
| KV cache, why it matters? | Stored Keys/Values of earlier tokens, not recalculated. Saves compute, costs memory (~128 KB/token for 8B), which caps users per GPU. |
| Why is decode memory-bound? | Each pass reads all 16 GB of weights for little maths: ~5 ms on an H100 → ~200 tokens/s max, maths units idle. |
| Throughput vs latency? | Total tokens/s for all vs speed for one. Taxi vs bus. Throughput sets cost per token. |
| GPU kernel? | A function on the GPU across thousands of cores. Not the Linux kernel. |
| FlashAttention? | **Exact** attention in small tiles in on-chip SRAM; the big score table never goes to HBM. Faster, less memory. |
| Engine vs plain PyTorch? | Continuous-batching scheduler, KV cache manager (PagedAttention), fast kernels, quantization, multi-GPU, OpenAI-compatible API. |
