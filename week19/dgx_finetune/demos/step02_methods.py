#!/usr/bin/env python3
"""PART 2 · LoRA vs QLoRA vs full SFT — what fits the DGX  [INTERMEDIATE]

Three ways to adapt a model, very different memory + quality trade-offs:

    full SFT — update every weight. Best quality, biggest memory (weights + Adam).
    LoRA     — freeze the base, train tiny low-rank adapters. ~0.1% of params.
    QLoRA    — LoRA on top of a 4-bit-quantized frozen base. Fits the biggest models.

This demo does the VRAM math for each method across model sizes and shows what a
single 128 GB DGX Spark can train.

Run:  python demos/step02_methods.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ftsim  # noqa: E402
import ftview  # noqa: E402


def main() -> None:
    ftview.banner("PART 2", "LoRA vs QLoRA vs full SFT — what fits", "INTERMEDIATE")
    ftview.mode_line()

    print("Why the methods differ in memory:")
    print("  • full SFT — bf16 weights + grads + Adam m/v ≈ 16 bytes/param. Huge.")
    print("  • LoRA     — frozen bf16 base (2 B/param) + a tiny trainable adapter.")
    print("  • QLoRA    — frozen 4-bit base (0.5 B/param) + adapter. The memory winner.\n")

    print("Training VRAM on a DGX Spark (128 GB) — fits if under ~118 GB usable:\n")
    print(f"  {'Model':>8}  {'full-SFT':>12}  {'LoRA':>10}  {'QLoRA':>10}")
    print("  " + "─" * 48)
    for p in (8, 13, 34, 70):
        row = {m: ftsim.vram_gb(ftsim.TrainConfig(base_model="x", method=m, params_b=p))
               for m in ("full-SFT", "LoRA", "QLoRA")}
        def cell(g):
            return f"{g:>7.0f} GB" + (" ✓" if g < 118 else " ✗")
        print(f"  {str(p)+'B':>8}  {cell(row['full-SFT']):>12}  "
              f"{cell(row['LoRA']):>10}  {cell(row['QLoRA']):>10}")
    print()

    print("Reading the table:")
    print("  • A Spark can FULL-fine-tune up to ~8B, LoRA up to ~34B, QLoRA a 70B.")
    print("  • QLoRA is the default on a single Spark: 70B domain adaptation, on a desk.")
    print("  • Quality order is full > LoRA ≳ QLoRA, but for DOMAIN style/format the")
    print("    gap is small — LoRA/QLoRA capture 'how we answer' very well.")
    print("  • Bigger jobs (full-SFT 70B) → link two Sparks or use a DGX Station.")

    print("\nTakeaway: pick the smallest method that hits your quality bar. For most")
    print("domain work on one Spark, that's QLoRA. Next: the real NeMo recipe.")


if __name__ == "__main__":
    main()
