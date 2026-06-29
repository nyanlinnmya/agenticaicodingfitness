#!/usr/bin/env python3
"""PART 6 · Evaluate — before vs after domain adaptation  [ADVANCED]

The only honest measure of fine-tuning is behaviour on held-out questions. Since
we can't ship a real LoRA to your laptop, this demo demonstrates the EFFECT a
domain LoRA bakes in by contrasting the SAME base model with vs without the domain
system prompt — the steering a LoRA makes permanent. In REAL mode it's a live
local model; in SIM it's stubbed. Either way you see the before/after gap.

Run:  python demos/step06_evaluate.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import ftview  # noqa: E402

DOMAIN_SYSTEM = (
    "You are HotelHVAC-Assistant, fine-tuned on smart-hotel HVAC SOPs. Answer with "
    "SPECIFIC setpoints, thresholds (°C, Pa), and alarm priorities (CRITICAL/ROUTINE). "
    "Be terse and operational."
)
EVAL_QUESTIONS = [
    "Filter ΔP is 260 Pa — what alarm priority and what action?",
    "A guest room is stuck at 26 °C with the fan-coil maxed. First two moves?",
]


def main() -> None:
    ftview.banner("PART 6", "Evaluate — before vs after", "ADVANCED")
    ftview.mode_line()
    ftview.require_runtime()

    print("We contrast the SAME model with vs without the domain behaviour a LoRA")
    print("bakes in. The 'after' column is what fine-tuning makes permanent.\n")

    for i, q in enumerate(EVAL_QUESTIONS, 1):
        print(f"── Q{i}: {q}")
        print("\n  BEFORE (base model, no domain adaptation):")
        ftview.generate(
            [{"role": "system", "content": "You are a helpful assistant."},
             {"role": "user", "content": q}],
            max_tokens=160, label="(generic answer)")
        print("\n  AFTER (domain-adapted behaviour):")
        ftview.generate(
            [{"role": "system", "content": DOMAIN_SYSTEM},
             {"role": "user", "content": q}],
            max_tokens=160, label="(domain answer — specific setpoints + priority)")
        print()

    print("Scoring fine-tuning properly (what you'd automate in CI):")
    print("  • Build a golden set of domain Q&A held out from training.")
    print("  • Score with an LLM-judge or exact-match on key facts (setpoints, priorities).")
    print("  • Gate: tuned model must beat base by X% AND not regress on general questions.")
    print("  • (This is exactly the eval discipline from Weeks 10 & 15 — applied to FT.)")

    print("\nTakeaway: a LoRA makes the 'after' behaviour permanent and on-prem — no")
    print("system-prompt babysitting, no cloud. Next: export and serve it sovereignly.")


if __name__ == "__main__":
    main()
