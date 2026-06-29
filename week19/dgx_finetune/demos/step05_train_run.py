#!/usr/bin/env python3
"""PART 5 · Watch the training run (loss curve + checkpoints)  [ADVANCED]

This is the heavy step you can't do on a laptop — so it runs in the simulator:
a realistic QLoRA run on a DGX Spark with a decaying loss curve, a warmup→cosine
LR schedule, throughput, and periodic checkpoint writes. Every number is marked
simulated; the REAL launch command is printed so you can run it on a DGX.

Run:  python demos/step05_train_run.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import ftsim  # noqa: E402
import ftview  # noqa: E402


def main() -> None:
    ftview.banner("PART 5", "Watch the training run", "ADVANCED")
    ftview.mode_line()

    if not (config.SANDBOX / "train.jsonl").exists():
        print("⚠  no dataset — run step01_dataset_prep.py first.\n")

    print("Simulating a QLoRA fine-tune on a DGX Spark (the real run uses the same")
    print("loop via NeMo/Unsloth — see steps 3–4 for the launch commands):\n")

    cfg = ftsim.TrainConfig(base_model=config.BASE_MODEL, method="QLoRA",
                            steps=60, params_b=8.0)
    final = ftsim.run(cfg, emit=lambda ln: print(ln, flush=True), fast=True)

    print("\nHow to read a training run:")
    print("  • Loss should fall fast then flatten — a smooth decay = healthy run.")
    print("  • Loss NOT falling → bad LR, broken data format, or frozen weights.")
    print("  • Loss → ~0 on train but val loss RISING → overfitting (fewer steps / more data).")
    print("  • Checkpoints let you resume and let you pick the best (not always the last).")
    print(f"  • Final train loss here: {final:.4f}.  The honest test is the EVAL → next step.")

    print("\nTakeaway: the loss curve tells you the run worked; only the EVAL on held-out")
    print("data tells you the MODEL works. On to the before/after eval.")


if __name__ == "__main__":
    main()
