#!/usr/bin/env python3
"""PART 4 · vLLM on DGX — throughput serving  [INTERMEDIATE]

When you have 2+ concurrent users, vLLM is the production serving choice. Its
PagedAttention + continuous batching keep the GB10 busy, giving far higher
aggregate throughput than single-stream Ollama. It serves the SAME OpenAI API,
so client code is unchanged. NVIDIA ships a Blackwell-ready container.

This demo prints the real DGX container commands, explains the batching win,
and (REAL mode) measures TTFT + decode throughput on the live endpoint.

Run:  python demos/step04_vllm_on_dgx.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import dgxview  # noqa: E402

COMMANDS = """\
# DGX Spark — vLLM via NVIDIA's Blackwell container (NGC)
export HF_TOKEN=...                 # for gated weights
export MODEL=nvidia/Qwen3-235B-A22B-NVFP4   # NVFP4 fits across the unified mem

docker run -d --name vllm --gpus all --ipc host \\
  -p 8000:8000 \\
  -e HF_TOKEN="$HF_TOKEN" \\
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \\
  nvcr.io/nvidia/vllm:26.01-py3 \\
  vllm serve "$MODEL" --max-model-len 8192 --gpu-memory-utilization 0.9

# OpenAI-compatible endpoint now on :8000  — point your app at it
export DGX_BASE_URL=http://localhost:8000/v1
"""


def _measure(model: str, prompt: str):
    client = dgxview._client()
    start = time.time(); ttft = None; chars = 0
    stream = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}],
        max_tokens=300, temperature=0.3, stream=True)
    for chunk in stream:
        if not chunk.choices:
            continue
        d = chunk.choices[0].delta
        piece = (d.content or "") + (dgxview._extract_reasoning(d) or "")
        if piece:
            if ttft is None:
                ttft = time.time() - start
            chars += len(piece)
    elapsed = time.time() - start
    toks = max(1, round(chars / 4))
    return (ttft or elapsed), toks / elapsed, toks


def main() -> None:
    dgxview.banner("PART 4", "vLLM on DGX — throughput serving", "INTERMEDIATE")
    dgxview.mode_line()

    print("Run vLLM on the DGX with NVIDIA's container:\n")
    print(COMMANDS)

    print("Why vLLM for serving (vs Ollama):")
    print("  • PagedAttention   — kv-cache in non-contiguous pages → less waste, more")
    print("                       requests resident at once")
    print("  • Continuous batch — new requests join the running batch every step, so")
    print("                       the GPU never idles between users")
    print("  • Result           — single-user tok/s is similar, but AGGREGATE")
    print("                       throughput scales ~linearly with concurrency\n")

    if dgxview.is_sim():
        print("SIM mode — showing representative DGX Spark serving numbers:")
        print("  ◆ time-to-first-token:  ~120 ms")
        print("  ◆ single-stream decode: ~46 tok/s   (qwen3.6 35B MoE, Q8)")
        print("  ◆ 8 concurrent users:   ~310 tok/s aggregate (PagedAttention win)")
        print("  ◆ network hops to cloud: 0")
    else:
        dgxview.sovereignty_line()
        print(f"Measuring the live endpoint serving {config.MODEL}:\n")
        ttft, tps, toks = _measure(config.MODEL,
                                   "Explain PagedAttention in 2 sentences.")
        print(f"  ◆ time-to-first-token:  {ttft*1000:.0f} ms")
        print(f"  ◆ single-stream decode: ~{tps:.1f} tok/s ({toks} tokens)")
        print("  ◆ network hops to cloud: 0  (served from your hardware)")

    print("\nTakeaway: same OpenAI API, served by vLLM for many users. Ollama for")
    print("convenience; vLLM when throughput and concurrency matter.")


if __name__ == "__main__":
    main()
