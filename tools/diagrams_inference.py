#!/usr/bin/env python3
"""Create the draw.io diagrams used by interview-prep/inference-engineering/*.md.

Run once:  python3 tools/diagrams_inference.py
Existing .drawio.svg files are skipped (they may have been edited in draw.io);
pass --force to regenerate them from this script anyway.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drawio_svg import Diagram  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "interview-prep" / "inference-engineering" / "diagrams"


def training_vs_inference():
    d = Diagram("01-training-vs-inference", 960, 340, "The two phases in a generative AI model's life")
    d.group("train", 20, 50, 360, 200, "Phase 1 · TRAINING\nlearn the weights from data", "orange")
    d.box("data", 35, 104, 140, 76, "Training data\ntext · code · images", "white", shape="cylinder", size=11)
    d.box("job", 230, 110, 130, 60, "Training job\nmany GPUs, weeks", "white", size=11)
    d.text("train-note", 30, 196, 340, 44, "Done once (or now and then)\nOffline · slow · very costly", size=11)
    d.box("weights", 410, 104, 150, 76, "Model weights\nbillions of numbers", "yellow", shape="cylinder", size=11)
    d.group("serve", 590, 50, 350, 200, "Phase 2 · INFERENCE\nserve the model in production", "green")
    d.box("server", 610, 110, 140, 60, "Inference server\nGPUs, always on", "white", size=11)
    d.box("users", 800, 110, 125, 60, "Users and apps\nprompt → answer", "white", size=11)
    d.text("serve-note", 600, 196, 330, 44, "Runs all the time, for every request\nOnline · must be fast and reliable",
           size=11)
    d.edge("data", "job")
    d.edge("job", "weights")
    d.edge("weights", "server")
    d.edge("users", "server", both=True)
    d.text("bottom", 0, 270, 960, 50,
           "Training creates the weights. Inference uses them to answer real users, millions of times.\n"
           "Inference engineering = making phase 2 fast, cheap and reliable.", size=13, bold=True)
    return d


def inference_stack():
    d = Diagram("01-inference-stack", 820, 760, "A complete inference stack: three layers that work together")
    # Tooling (named in the text; the book's Figure 0.1 draws only runtime and infrastructure)
    d.group("tooling", 30, 48, 760, 84, "TOOLING: how engineers work with the stack", "purple")
    d.box("tool", 50, 78, 720, 44, "The right level of abstraction\nenough control to tune things, without losing productivity",
          "white", size=11)
    # Runtime
    d.group("runtime", 30, 146, 760, 310, "RUNTIME: make one model fast on one GPU-backed instance", "green")
    d.group("perf", 50, 176, 720, 122, "Model performance techniques", "outline", dashed=True, size=12)
    techniques = [
        ("batching", "Batching\nmany requests per GPU pass"),
        ("caching", "Caching\nreuse past work (KV cache)"),
        ("quant", "Quantization\nfewer bits per weight"),
        ("spec", "Speculation\nguess tokens ahead, then check"),
        ("parallel", "Parallelism\nsplit one model over GPUs"),
        ("disagg", "Disaggregation\nprefill and decode apart"),
    ]
    for i, (id_, label) in enumerate(techniques):
        d.box(id_, 65 + (i % 3) * 235, 200 + (i // 3) * 48, 220, 40, label, "yellow", size=11)
    for i, (id_, label) in enumerate([("vllm", "vLLM\nopen-source engine"),
                                      ("sglang", "SGLang\nopen-source engine"),
                                      ("trt", "TensorRT-LLM\nNVIDIA's engine")]):
        d.box(id_, 50 + i * 245, 308, 230, 40, label, "white", size=11)
    d.box("pytorch", 50, 356, 720, 40, "PyTorch\nthe deep-learning framework: the model's code and maths", "white", size=11)
    d.box("cuda", 50, 404, 720, 40, "CUDA (Compute Unified Device Architecture)\nNVIDIA's platform for running code on GPUs",
          "white", size=11)
    # Infrastructure
    d.group("infra", 30, 470, 760, 226, "INFRASTRUCTURE: scale across clusters, regions and clouds", "blue")
    d.box("routing", 50, 500, 352, 40, "Routing\nsend each request to the right replica", "white", size=11)
    d.box("lb", 418, 500, 352, 40, "Load balancing\nspread traffic evenly over replicas", "white", size=11)
    d.box("autoscale", 50, 548, 720, 40, "Autoscaling\nadd or remove GPU replicas as traffic goes up and down",
          "white", size=11)
    d.box("capacity", 50, 596, 720, 40, "Multi-cloud capacity management\nfind and use GPUs across clouds and regions, with no silos",
          "white", size=11)
    for i, (id_, label) in enumerate([("gpus", "GPUs\nthe hardware that runs the model"),
                                      ("storage", "Storage\nwhere the model weights live"),
                                      ("network", "Networking\nmoves requests, weights, data")]):
        d.box(id_, 50 + i * 245, 644, 230, 40, label, "white", size=11)
    d.text("bottom", 0, 706, 820, 44,
           "Runtime makes ONE copy of the model fast · Infrastructure runs MANY copies reliably\n"
           "Tooling lets engineers use both · weak in any one layer = weak inference", size=12, bold=True)
    return d


def prefill_vs_decode():
    d = Diagram("02-prefill-vs-decode", 920, 440, "How an LLM answers: one prefill, then many decode passes")
    d.group("pre", 20, 50, 430, 300, "PREFILL: read the whole prompt (once)", "orange")
    d.group("prompt", 30, 88, 410, 56, "", "outline", dashed=True)
    for i, tok in enumerate(["What", "is", "the", "capital", "of", "France", "?"]):
        d.box(f"p{i}", 38 + i * 57, 96, 53, 40, tok, "white", size=11)
    d.box("prepass", 110, 172, 250, 48, "1 forward pass\nall 7 prompt tokens in parallel", "white", size=11)
    d.box("first", 34, 248, 170, 48, "First answer token\n'The'", "green", size=11)
    d.box("kv1", 250, 240, 180, 64, "KV cache\nfor the 7 prompt tokens", "yellow", shape="cylinder", size=11)
    d.text("pre-note", 30, 306, 410, 40, "Compute-bound: lots of maths at once\nSets TTFT (Time To First Token)", size=11)
    d.group("dec", 470, 50, 430, 300, "DECODE: write the answer, one token per pass", "blue")
    d.group("passes", 478, 88, 414, 72, "", "outline", dashed=True)
    for i, tok in enumerate(["capital", "is", "Paris", "."]):
        d.box(f"d{i}", 487 + i * 102, 98, 86, 52, f"Pass {i + 1}\n→ '{tok}'", "white", size=11)
        if i:
            d.edge(f"d{i - 1}", f"d{i}")
    d.box("kv2", 560, 215, 250, 64, "KV cache\ngrows by one token every pass", "yellow", shape="cylinder", size=11)
    d.text("dec-note", 480, 306, 410, 40,
           "Memory-bound: every pass re-reads all the weights\nSets the streaming speed (time per output token)", size=11)
    d.edge("prompt", "prepass")
    d.edge("prepass", "first")
    d.edge("prepass", "kv1")
    d.edge("kv1", "kv2", "carried over")
    d.edge("passes", "kv2", "read all, add 1", both=True, dashed=True)
    d.text("bottom", 0, 366, 920, 56,
           "Prefill = read the question, all at once (fast). Decode = write the answer one token at a time (the slow part).\n"
           "A 500-token answer = 1 prefill + about 500 decode passes.", size=12, bold=True)
    return d


def continuous_batching():
    d = Diagram("03-continuous-batching", 940, 480, "Static vs continuous batching: 4 GPU slots, 10 decode steps")
    colors = dict(A="blue", B="green", C="orange", D="purple", E="red", F="yellow",
                  G="blue", H="green", I="orange", J="purple", K="red", L="yellow")
    x0, cw = 140, 62

    def panel(tag, y, title, rows, note):
        d.text(f"{tag}-t", 20, y, 900, 24, title, size=13, bold=True, align="left")
        for s in range(10):
            d.text(f"{tag}-h{s}", x0 + s * cw, y + 26, cw - 2, 18, f"step {s + 1}", size=10)
        for r, spans in enumerate(rows):
            ry = y + 48 + r * 30
            d.text(f"{tag}-s{r}", 20, ry, 110, 26, f"GPU slot {r + 1}", size=11, align="left")
            for name, start, end in spans:
                idle = name == "idle"
                d.box(f"{tag}-{r}-{start}", x0 + (start - 1) * cw, ry, (end - start + 1) * cw - 2, 26,
                      "idle (wasted)" if idle else name, "gray" if idle else colors[name[0]],
                      size=11, dashed=idle, italic=idle)
        d.text(f"{tag}-n", 775, y + 48, 150, 116, note, size=11, align="left")

    panel("st", 46, "Static batching: the batch is fixed until its LONGEST request (B) finishes",
          [[("A", 1, 3), ("idle", 4, 8), ("E…", 9, 10)],
           [("B", 1, 8), ("F…", 9, 10)],
           [("C", 1, 4), ("idle", 5, 8), ("G", 9, 10)],
           [("D", 1, 6), ("idle", 7, 8), ("H…", 9, 10)]],
          "Finished after\n10 steps: 5\n(A B C D G)\n\nNew requests\nwait in a queue")
    panel("ct", 230, "Continuous batching: a waiting request joins the moment a slot frees up",
          [[("A", 1, 3), ("E", 4, 6), ("G", 7, 8), ("I", 9, 10)],
           [("B", 1, 8), ("J", 9, 10)],
           [("C", 1, 4), ("F", 5, 8), ("K", 9, 10)],
           [("D", 1, 6), ("H", 7, 9), ("L…", 10, 10)]],
          "Finished after\n10 steps: 11\n(A to K)\n\nSame GPU,\nno idle slots")
    d.text("legend", 20, 400, 900, 20,
           "Tokens each request needs: A 3 · B 8 · C 4 · D 6 · E 3 · F 4 · G 2 · H 3 · I 2 · J 2 · K 2 · L more   (… = still running)",
           size=11, italic=True)
    d.text("bottom", 0, 426, 940, 44,
           "Continuous batching re-forms the batch at EVERY decode step: finished requests leave, waiting ones join.\n"
           "That's the book's \"weaving requests together token by token\". Result: much higher throughput.",
           size=12, bold=True)
    return d


def prefix_caching():
    d = Diagram("03-prefix-caching", 940, 400, "Prefix caching: reuse the KV cache when prompts start the same way")
    d.text("r1", 20, 70, 90, 40, "Request 1", size=12, bold=True, align="left")
    d.box("pre1", 115, 62, 330, 56, "System prompt (2,000 tokens)\n'You are a support bot for ShopCo…'", "white", size=11)
    d.box("u1", 455, 62, 190, 56, "User question (10 tokens)\n'Reset my password?'", "blue", size=11)
    d.box("res1", 690, 62, 230, 56, "Prefill computes all\n2,010 tokens (slow)", "orange", size=11)
    d.box("cache", 150, 152, 260, 70, "KV cache of the prefix\nkept in GPU memory after request 1", "yellow",
          shape="cylinder", size=11)
    d.text("r2", 20, 262, 90, 40, "Request 2", size=12, bold=True, align="left")
    d.box("pre2", 115, 254, 330, 56, "Same system prompt\nfound in the cache: skip the work", "gray", size=11, dashed=True)
    d.box("u2", 455, 254, 190, 56, "User question (10 tokens)\n'Cancel my order'", "blue", size=11)
    d.box("res2", 690, 254, 230, 56, "Prefill computes only\nthe 10 new tokens (fast)", "green", size=11)
    d.edge("u1", "res1")
    d.edge("u2", "res2")
    d.edge("pre1", "cache", "saved")
    d.edge("cache", "pre2", "reused")
    d.text("bottom", 0, 334, 940, 56,
           "Only an exact match from the very first token counts, so put the fixed part first and the changing part last.\n"
           "Common shared prefixes: system prompts, chat history, few-shot examples, one long document asked many questions.",
           size=12, bold=True)
    return d


def speculative_decoding():
    d = Diagram("03-speculative-decoding", 940, 390, "Speculative decoding: guess cheaply, check in one pass")
    d.text("ctx", 20, 42, 900, 22, "Text so far: \"France's capital …\"", size=12, italic=True, align="left")
    d.box("draft", 20, 76, 190, 56, "1 · Draft model\nsmall and fast", "purple", size=11)
    d.group("guesses", 240, 70, 470, 68, "", "outline", dashed=True)
    for i, tok in enumerate(["is", "Paris", "and", "has"]):
        d.box(f"g{i}", 250 + i * 115, 82, 105, 44, f"guess {i + 1}\n'{tok}'", "white", size=11)
    d.text("draft-note", 730, 76, 190, 56, "4 tokens guessed\n(cheap to make)", size=11, align="left")
    d.box("target", 20, 168, 190, 56, "2 · Target model\nthe big, real model", "blue", size=11)
    d.box("check", 240, 168, 470, 56, "ONE forward pass checks all 4 guesses together\ncosts about the same as making 1 token (memory-bound)",
          "orange", size=11)
    d.box("result", 20, 260, 190, 56, "3 · Result", "green", size=11)
    d.group("results", 240, 256, 470, 64, "", "outline", dashed=True)
    for i, (label, color) in enumerate([("'is' ✓", "green"), ("'Paris' ✓", "green"),
                                        ("'and' ✓", "green"), ("'has' ✗ → 'it'", "red")]):
        d.box(f"r{i}", 250 + i * 115, 266, 105, 44, label, color, size=11)
    d.text("res-note", 730, 254, 190, 70, "4 tokens from 1 big\npass instead of 1\n(3 accepted + 1 fixed)",
           size=11, align="left")
    d.edge("draft", "guesses")
    d.edge("guesses", "check")
    d.edge("target", "check")
    d.edge("check", "results")
    d.text("bottom", 0, 332, 940, 50,
           "A wrong guess costs nothing extra: the big model's own token is used instead. Same output quality, only faster.\n"
           "Works best when the text is predictable: code, JSON, repeated phrases.", size=12, bold=True)
    return d


def parallelism():
    d = Diagram("03-parallelism", 940, 440, "Three ways to split one model across GPUs")
    d.group("tp", 20, 46, 290, 320, "Tensor parallelism\nsplit EVERY layer", "white")
    d.text("tp-g0", 35, 96, 125, 18, "GPU 0", size=11, bold=True)
    d.text("tp-g1", 170, 96, 125, 18, "GPU 1", size=11, bold=True)
    for i in range(4):
        d.box(f"tp-a{i}", 35, 118 + i * 38, 125, 32, f"Layer {i + 1} · half A", "blue", size=11)
        d.box(f"tp-b{i}", 170, 118 + i * 38, 125, 32, f"Layer {i + 1} · half B", "green", size=11)
    d.text("tp-n", 30, 284, 270, 76,
           "GPUs talk after EVERY layer\n→ needs very fast links (NVLink)\n→ usually inside one machine\nBest for: lower latency",
           size=11, align="left")
    d.group("pp", 325, 46, 290, 320, "Pipeline parallelism\nsplit the layers into stages", "white")
    d.box("pp0", 365, 110, 210, 58, "GPU 0\nLayers 1–2", "blue", size=12)
    d.box("pp1", 365, 218, 210, 58, "GPU 1\nLayers 3–4", "green", size=12)
    d.edge("pp0", "pp1", "hand over the results")
    d.text("pp-n", 335, 284, 270, 76,
           "GPUs pass work along like a relay\n→ less talking, can span machines\n→ risk: GPUs waiting ('bubbles')\nBest for: models too big for 1 machine",
           size=11, align="left")
    d.group("ep", 630, 46, 290, 320, "Expert parallelism\nfor Mixture-of-Experts models", "white")
    d.box("router", 650, 110, 250, 40, "Router: picks 2 experts per token", "gray", size=11)
    for i in range(4):
        d.box(f"ex{i}", 650 + i * 64, 210, 58, 48, f"Expert {i + 1}\nGPU {i}", ["blue", "green", "orange", "purple"][i],
              size=10)
    d.edge("router", "ex0")
    d.edge("router", "ex2")
    d.text("ep-n", 640, 284, 270, 76,
           "Each token uses only a few experts\n→ spread the experts over GPUs\n→ risk: one 'popular' expert overloaded\nBest for: MoE models (e.g. DeepSeek)",
           size=11, align="left")
    d.text("bottom", 0, 380, 940, 50,
           "The new bottleneck to avoid: GPU-to-GPU communication.\n"
           "Split too much, or over slow links, and the GPUs spend their time waiting instead of computing.",
           size=12, bold=True)
    return d


def disaggregation():
    d = Diagram("03-disaggregation", 940, 420, "Disaggregation: prefill and decode on separate, independently scaled workers")
    d.group("before", 20, 46, 900, 92, "Before: one worker does both", "gray", align="left")
    d.box("mixed", 40, 76, 280, 50, "GPU worker\nprefill + decode share the GPU", "white", size=11)
    d.text("before-n", 340, 76, 570, 50,
           "A big prompt's prefill pauses everyone's decode → answers stutter\n"
           "Can't give the two jobs different GPUs or scale them separately", size=11, align="left")
    d.group("after", 20, 152, 900, 196, "After: disaggregated", "white", align="left")
    d.box("user", 32, 222, 100, 54, "User\nrequest", "blue", size=11)
    d.group("ppool", 160, 186, 240, 150, "Prefill workers", "orange", size=12)
    for i in range(3):
        d.box(f"pw{i}", 175 + i * 76, 218, 62, 40, f"P{i + 1}", "white", size=11)
    d.text("ppool-n", 165, 266, 230, 60, "compute-heavy\nscale on prompt load\n(e.g. 3 GPUs)", size=11)
    d.group("dpool", 560, 186, 240, 150, "Decode workers", "blue", size=12)
    for i in range(4):
        d.box(f"dw{i}", 572 + i * 56, 218, 48, 40, f"D{i + 1}", "white", size=11)
    d.text("dpool-n", 565, 266, 230, 60, "memory-heavy\nscale on answers in progress\n(e.g. 4 GPUs)", size=11)
    d.box("out", 820, 222, 94, 54, "Tokens\nstreamed back", "green", size=11)
    d.edge("user", "ppool")
    d.edge("ppool", "dpool", "KV cache\n(fast network)")
    d.edge("dpool", "out")
    d.text("bottom", 0, 360, 940, 50,
           "Each pool gets its own GPU count and tuning → steadier speed and better GPU use.\n"
           "The cost: the KV cache must move between machines, so this needs a fast network and more moving parts.",
           size=12, bold=True)
    return d


if __name__ == "__main__":
    force = "--force" in sys.argv
    warnings = []
    for build in (training_vs_inference, inference_stack, prefill_vs_decode, continuous_batching,
                  prefix_caching, speculative_decoding, parallelism, disaggregation):
        diagram = build()
        warnings += diagram.warnings
        path = diagram.save(OUT, force=force)
        print(f"wrote {path}" if path else f"skipped {diagram.name} (exists; use --force)")
    for w in warnings:
        print("WARN", w)
