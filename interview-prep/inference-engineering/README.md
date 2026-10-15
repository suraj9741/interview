# 🧠 Inference Engineering Notes

My notes as I learn **inference engineering**: how to run generative AI (Artificial Intelligence) models in production so they're **fast, cheap and reliable**. The main source is the book *Inference Engineering* by Philip Kiely (Baseten); I add the details as I read, with links back to the DevOps topics I already know.

## How to use these notes

- Read one file at a time, then answer its **Check yourself** questions **out loud** (teach-back).
- ⭐ = core idea, must be able to explain without notes.
- **DevOps link** boxes connect each new idea to Kubernetes, AWS or networking, which I already know.

## Diagrams

All diagrams are in [diagrams/](diagrams/) as **`.drawio.svg`** files: a normal picture that also contains the editable draw.io diagram.

- **To view:** they appear inside the notes in the Markdown preview.
- **To edit:** open the `.drawio.svg` file in VS Code (the Draw.io Integration extension opens it as a diagram editor), or in draw.io / [app.diagrams.net](https://app.diagrams.net).
- **To practise:** redraw the inference stack (01) and prefill vs decode (02) from memory. If you can draw them and explain every box, you have the map of the whole subject.

## Contents

| # | File | What's inside |
|---|---|---|
| 01 | [Fundamentals](01-fundamentals.md) | Training vs inference, why generative AI inference is hard, the three layers (runtime, infrastructure, tooling), the full stack map ⭐ |
| 02 | [Runtime layer](02-runtime-layer.md) | Prefill vs decode, KV cache, why decode is memory-bound ⭐, throughput vs latency, CUDA → PyTorch → engines, GPU kernels and FlashAttention |
| 03 | [Model performance techniques](03-model-performance-techniques.md) | Batching, caching, quantization, speculation, parallelism, disaggregation ⭐, other modalities |

## Related files

- [Docker notes](../docker/README.md) and [networking notes](../networking/README.md): the infrastructure layer of inference runs on the same containers, Kubernetes and networks.
