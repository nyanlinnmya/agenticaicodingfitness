#!/usr/bin/env python3
"""PART 1 · Build a domain SFT dataset (on-prem)  [BEGINNER]

Fine-tuning starts with data — and the sovereignty win is that your proprietary
data NEVER leaves the building. This demo turns a few "domain documents" into a
real instruction-tuning dataset in the OpenAI/ShareGPT messages format and writes
train/val JSONL splits into .sandbox/ so the later steps can use them.

Domain: smart-hotel HVAC operations (ties back to the Week 18 hotel agent).

Run:  python demos/step01_dataset_prep.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import ftview  # noqa: E402

SYSTEM = ("You are HotelHVAC-Assistant, an expert in smart-hotel HVAC operations. "
          "Answer with specific setpoints, thresholds, and alarm priorities.")

# A handful of domain (instruction, response) pairs — in reality you'd generate
# hundreds of these from your manuals, tickets, and SOPs.
PAIRS = [
    ("A guest room reads 26 °C with the fan-coil at max. What do I do?",
     "Drop chilled-water supply to 6.5 °C and stage the second compressor. If the "
     "room doesn't fall below 24 °C in 20 min, raise a CRITICAL alarm (guest-impacting)."),
    ("Filter differential pressure is 260 Pa. Alarm priority?",
     "ΔP > 250 Pa means a fouled filter: dispatch ROUTINE maintenance, not CRITICAL. "
     "Schedule replacement within 48h; log the run-hours."),
    ("What's the night setback for unoccupied rooms?",
     "Set unoccupied rooms to 25.5 °C cooling / 20 °C heating with the fan on AUTO; "
     "resume comfort band 30 min before check-in based on the PMS occupancy feed."),
    ("Chiller COP dropped from 5.1 to 3.8. Cause?",
     "A 25% COP drop usually means condenser fouling or low refrigerant charge. "
     "Check approach temperature first; dispatch ROUTINE inspection, trend for 24h."),
]


def to_record(instr: str, resp: str) -> dict:
    return {"messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": instr},
        {"role": "assistant", "content": resp},
    ]}


def main() -> None:
    ftview.banner("PART 1", "Build a domain SFT dataset (on-prem)", "BEGINNER")
    ftview.mode_line()

    sb = config.ensure_sandbox()
    records = [to_record(i, r) for i, r in PAIRS]
    # tiny but real train/val split
    train, val = records[:3], records[3:]
    (sb / "train.jsonl").write_text("\n".join(json.dumps(r) for r in train) + "\n")
    (sb / "val.jsonl").write_text("\n".join(json.dumps(r) for r in val) + "\n")

    print(f"Domain: {config.DOMAIN}")
    print(f"Format: OpenAI/ShareGPT chat messages (NeMo, Unsloth, LLaMA-Factory all read this)\n")
    print("Wrote real files into .sandbox/:")
    print(f"  • train.jsonl  ({len(train)} examples)")
    print(f"  • val.jsonl    ({len(val)} examples)\n")
    print("One record (pretty-printed):\n")
    print(json.dumps(records[0], indent=2))

    print("\nData-prep rules that matter for quality:")
    print("  • Consistent SYSTEM prompt → the behaviour you want baked in.")
    print("  • Diverse, REAL examples > many near-duplicates (avoid overfitting).")
    print("  • Hold out a val split you NEVER train on — that's your honesty check.")
    print("  • 50–500 good examples already move a base model a lot with LoRA.")
    print("  • Your data stays local: this is why you fine-tune on a DGX, not a cloud.")

    print("\nTakeaway: domain adaptation is mostly a DATA problem. Next: pick the")
    print("training METHOD (LoRA / QLoRA / full SFT) that fits your DGX.")


if __name__ == "__main__":
    main()
