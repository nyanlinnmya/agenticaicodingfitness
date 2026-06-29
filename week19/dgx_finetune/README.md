# ▣ Week 19 · App 2 — Fine-tuning on a DGX

An **interactive, explainable web app + runnable demos** for adapting an
open-weight model to **your own domain** — entirely on a DGX, $0 to the cloud,
and your proprietary training data never leaves the building.

```
data (on-prem) → recipe → train on DGX → eval → merge → GGUF/NVFP4 → serve
                                  ⛔ nothing leaves the box
```

## Two modes — auto-detected

| Mode | Training loop | Dataset / recipe | Before/after eval |
|------|---------------|------------------|-------------------|
| **REAL** | simulated* | real files written to `.sandbox/` | live model on this box / your DGX |
| **SIM**  | simulated  | real files written to `.sandbox/` | stubbed |

\* You can't train a 70B on a laptop, so the training **loop** always runs in a
faithful simulator (real loss curve, LR schedule, throughput, checkpoints) — the
**real launch commands** (NeMo / Unsloth) are always printed so you run them on a
DGX. Everything else is real.

---

## Quick start

```bash
uv pip install -r week19/dgx_finetune/requirements.txt

# optional: a live model makes the Ch-7 eval real
ollama run qwen3.6:35b-a3b-q8_0     # DGX / Ubuntu GPU   (gemma4:12b on a Mac)

# the interactive web app
.venv/bin/python week19/dgx_finetune/tutorial_server.py
# → open http://127.0.0.1:8093

# or a single demo
.venv/bin/python week19/dgx_finetune/demos/step01_dataset_prep.py
```

Env overrides: `DGX_BASE_URL`, `DGX_MODEL`, `DGX_MODE=sim|real`, `FT_BASE_MODEL`.

---

## Layout

```
week19/dgx_finetune/
├── README.md · requirements.txt · config.py
├── ftsim.py            → the fine-tune simulator (loss curve, VRAM, checkpoints)
├── ftview.py           → framing + the before/after eval engine (real+sim)
├── tutorial_server.py  → FastAPI control plane
├── static/guide.html   → the clickable, streaming tutorial UI
└── demos/
    ├── step01_dataset_prep.py    Ch 2 · build a domain SFT dataset (→ .sandbox/)
    ├── step02_methods.py         Ch 3 · LoRA vs QLoRA vs full SFT — VRAM math
    ├── step03_nemo_recipe.py     Ch 4 · real NeMo AutoModel QLoRA YAML + launch
    ├── step04_unsloth.py         Ch 5 · the Unsloth fast path (2x, GGUF export)
    ├── step05_train_run.py       Ch 6 · watch a simulated training run
    ├── step06_evaluate.py        Ch 7 · before vs after domain adaptation
    └── step07_export_serve.py    Ch 8 · merge → GGUF/NVFP4 → serve on the OpenAI API
```

---

## The 8 chapters

| Ch | Demo | The one thing to notice |
|----|------|--------------------------|
| 1  | *(concept)* | Fine-tune changes the **weights**; on a DGX the whole loop is sovereign. |
| 2  | `step01` | Domain adaptation is a **data** problem — real JSONL, your data stays local. |
| 3  | `step02` | **QLoRA** fits a 70B fine-tune on ONE 128 GB Spark; full-SFT only ~8B. |
| 4  | `step03` | The **recipe is the experiment** — a real NeMo YAML you version in git. |
| 5  | `step04` | **Unsloth** → 2x faster, exports straight to **GGUF** for Ollama. |
| 6  | `step05` | A healthy run = **loss decays then flattens**; watch for overfitting. |
| 7  | `step06` | Only the **held-out eval** proves the model works — gate it in CI. |
| 8  | `step07` | Merge → GGUF/NVFP4 → Ollama; your app changes **only the model name**. |

---

## Where this sits in Week 19

```
App 1 sovereign_dgx → run/serve models   ·   App 2 (THIS) → adapt them to your domain
App 3 dgx_observability → trace agents (Phoenix + NeMo Agent Toolkit)
App 4 self_evolving_agent_v2 → the Week 18 agent, driven by your DGX model
```

App 1 gave you a served model; App 2 makes it a **domain expert** — without a
single example or weight leaving the building. The fine-tuned model is now ready
for the agents in Apps 3–4 to call.
