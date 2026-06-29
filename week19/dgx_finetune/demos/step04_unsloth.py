#!/usr/bin/env python3
"""PART 4 · The Unsloth fast path (2x faster, GGUF export)  [INTERMEDIATE]

NeMo is the enterprise path; Unsloth is the rapid-iteration path. Its custom
Triton kernels train ~2x faster with less memory, and it exports straight to GGUF
so the tuned model drops into Ollama/llama.cpp. This demo writes a REAL Unsloth
training script into .sandbox/ and explains the moving parts.

Run:  python demos/step04_unsloth.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import ftview  # noqa: E402

SCRIPT = '''\
# train_hvac_unsloth.py  — run inside nvcr.io/nvidia/pytorch:25.11-py3 on the DGX
#   pip install unsloth "datasets>=3.0" trl peft
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig

model, tok = FastLanguageModel.from_pretrained(
    "{base_model}", max_seq_length=1024, load_in_4bit=True)   # QLoRA
model = FastLanguageModel.get_peft_model(
    model, r=16, lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])

ds = load_dataset("json", data_files={{"train": ".sandbox/train.jsonl"}})["train"]

SFTTrainer(
    model=model, tokenizer=tok, train_dataset=ds,
    args=SFTConfig(max_steps=60, learning_rate=2e-4, warmup_steps=6,
                   per_device_train_batch_size=2, output_dir="out"),
).train()

# export for sovereign serving — straight into Ollama / llama.cpp:
model.save_pretrained_gguf("hvac-model", tok, quantization_method="q4_k_m")
'''


def main() -> None:
    ftview.banner("PART 4", "The Unsloth fast path", "INTERMEDIATE")
    ftview.mode_line()

    sb = config.ensure_sandbox()
    script = SCRIPT.format(base_model=config.BASE_MODEL)
    (sb / "train_hvac_unsloth.py").write_text(script)
    print("Wrote real script → .sandbox/train_hvac_unsloth.py\n")
    print(script)

    print("NeMo vs Unsloth — when to use which:")
    print(f"  {'':<14}{'NeMo AutoModel':<22}Unsloth")
    print("  " + "─" * 52)
    for k, a, b in [
        ("speed",     "baseline",            "~2x faster (Triton kernels)"),
        ("scale",     "multi-GPU/multi-node", "single-GPU focused"),
        ("export",    "HF / NeMo ckpt",      "direct GGUF (Ollama-ready)"),
        ("best for",  "production pipelines", "fast iteration on one Spark"),
    ]:
        print(f"  {k:<14}{a:<22}{b}")

    print("\nThe export line is the sovereign payoff: save_pretrained_gguf() writes a")
    print("Q4_K_M GGUF you can `ollama create` and serve immediately — no cloud round-trip.")

    print("\nTakeaway: Unsloth = fastest path from dataset → served GGUF on one Spark.")
    print("Next: watch a (simulated) training run with a real loss curve.")


if __name__ == "__main__":
    main()
