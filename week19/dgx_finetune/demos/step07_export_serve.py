#!/usr/bin/env python3
"""PART 7 · Export, quantize & serve the tuned model  [ADVANCED]

A trained adapter is useless until apps can call it. This is the last mile, all
on-prem: merge the LoRA into the base, export to GGUF (or quantize to NVFP4),
register it with Ollama, and serve the SAME OpenAI API your apps already use.

Run:  python demos/step07_export_serve.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
import ftview  # noqa: E402

MERGE = """\
# 1) merge the LoRA adapter into the base weights (NeMo or PEFT)
python -m peft.utils.merge_adapter \\
  --base {base} --adapter .sandbox/checkpoints/step_60 \\
  --output .sandbox/hvac-merged
"""

GGUF = """\
# 2a) export to GGUF for Ollama / llama.cpp (sovereign, single file)
python llama.cpp/convert_hf_to_gguf.py .sandbox/hvac-merged \\
  --outfile .sandbox/hvac-q4_k_m.gguf --outtype q4_k_m
"""

NVFP4 = """\
# 2b) …or quantize to NVFP4 for native Blackwell speed on the DGX
docker run --rm --gpus all -v "$PWD/.sandbox:/w" nvcr.io/nvidia/vllm:26.01-py3 \\
  bash -c 'cd /app/TensorRT-Model-Optimizer && \\
    examples/llm_ptq/scripts/huggingface_example.sh \\
      --model /w/hvac-merged --quant nvfp4 --output /w/hvac-nvfp4'
"""

OLLAMA = """\
# 3) register + serve with Ollama — your apps just change the model name
printf 'FROM ./.sandbox/hvac-q4_k_m.gguf\\nSYSTEM "You are HotelHVAC-Assistant."\\n' > Modelfile
ollama create hvac-assistant -f Modelfile
ollama run hvac-assistant         # now on the OpenAI API at :11434
"""


def main() -> None:
    ftview.banner("PART 7", "Export, quantize & serve the tuned model", "ADVANCED")
    ftview.mode_line()

    print("The sovereign last mile — every step stays on the DGX:\n")
    print(MERGE.format(base=config.BASE_MODEL))
    print(GGUF)
    print(NVFP4)
    print(OLLAMA)

    print("Then your existing app code is unchanged — only the model name moves:\n")
    print("    from openai import OpenAI")
    print(f'    client = OpenAI(base_url="{config.BASE_URL}", api_key="…")')
    print('    client.chat.completions.create(model="hvac-assistant", messages=[...])\n')

    print("The full sovereign fine-tuning loop you just walked:")
    print("  data (on-prem)  →  recipe  →  train (DGX)  →  eval  →  merge")
    print("  →  GGUF/NVFP4  →  Ollama/vLLM  →  served on the SAME OpenAI API")
    print("  …and not one training example or weight ever left the building.")

    print("\nTakeaway: fine-tuning on a DGX closes the loop — your data shapes your")
    print("model, your model serves your apps, and the whole cycle is sovereign.")


if __name__ == "__main__":
    main()
