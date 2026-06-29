#!/usr/bin/env python3
"""Interactive, explainable tutorial for **Fine-tuning on a DGX**.

Serves a clickable web guide (static/guide.html). For each chapter you read the
CONCEPT, view the demo SOURCE, and RUN it. The training-loop demo is simulated
(you can't train a 70B on a laptop); dataset prep, recipe generation, and the
before/after eval run for real (eval uses a live model if one is reachable).

    .venv/bin/python week19/dgx_finetune/tutorial_server.py
    # → http://127.0.0.1:8093
"""
from __future__ import annotations

import asyncio
import os
import shutil
import socket
import sys
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
PY = str(ROOT / ".venv" / "bin" / "python")
if not Path(PY).exists():
    PY = sys.executable
DEMOS = PKG / "demos"
GUIDE_PORT = int(os.environ.get("FT_GUIDE_PORT", "8093"))


def _port_busy(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _pick_free_port(preferred: int, span: int = 40) -> int:
    for p in range(preferred, preferred + span):
        if not _port_busy(p):
            return p
    return preferred


STEPS = [
    {
        "id": "intro", "group": "Foundations", "kind": "concept",
        "title": "Ch 1 · Why fine-tune on a DGX", "level": "beginner",
        "desc": "Prompting and RAG steer a model from the OUTSIDE. Fine-tuning changes "
        "the WEIGHTS — it bakes your domain's vocabulary, format, and judgement into "
        "the model itself. On a DGX the whole cycle is sovereign: your proprietary "
        "training data never leaves the building.\n\n"
        "When to fine-tune (vs prompt / RAG):\n"
        "  • You need a consistent STYLE/FORMAT every time      → fine-tune\n"
        "  • The model must know niche domain facts/jargon       → fine-tune (or RAG)\n"
        "  • Facts change daily / need citations                → RAG, not fine-tune\n"
        "  • One-off behaviour tweak                            → just prompt\n\n"
        "The sovereign fine-tuning loop (this whole app):\n"
        "  data (on-prem) → recipe → train on DGX → eval → merge → GGUF/NVFP4 → serve\n\n"
        "Techniques you'll meet: full SFT (all weights), LoRA (tiny adapters), QLoRA "
        "(LoRA on a 4-bit base — fits a 70B on ONE Spark). Frameworks: NVIDIA NeMo "
        "AutoModel (enterprise) and Unsloth (2x faster, GGUF export).\n\n"
        "The heavy training step runs in a faithful SIMULATOR so you can learn it with "
        "no GPU; the real launch commands are always shown. Click through Ch 2–8.",
    },
    {"id": "step01", "group": "Data", "kind": "run", "demo": "step01_dataset_prep.py",
     "title": "Ch 2 · Build a domain SFT dataset", "level": "beginner",
     "desc": "Turn domain documents into a real instruction dataset (OpenAI chat "
     "messages format) with train/val splits, written to .sandbox/. The sovereignty "
     "win: your data never leaves the box. Domain = smart-hotel HVAC."},
    {"id": "step02", "group": "Method", "kind": "run", "demo": "step02_methods.py",
     "title": "Ch 3 · LoRA vs QLoRA vs full SFT", "level": "intermediate",
     "desc": "Three adaptation methods, very different memory. See the training-VRAM "
     "math across model sizes and what a single 128 GB Spark can train (QLoRA → 70B)."},
    {"id": "step03", "group": "Method", "kind": "run", "demo": "step03_nemo_recipe.py",
     "title": "Ch 4 · The NeMo AutoModel recipe", "level": "intermediate",
     "desc": "NVIDIA's enterprise fine-tuning path. Generates a REAL QLoRA YAML for "
     "the HVAC dataset and prints the exact nemo-automodel container launch command."},
    {"id": "step04", "group": "Method", "kind": "run", "demo": "step04_unsloth.py",
     "title": "Ch 5 · The Unsloth fast path", "level": "intermediate",
     "desc": "The rapid-iteration path: ~2x faster Triton kernels and direct GGUF "
     "export into Ollama. Writes a real Unsloth training script + the NeMo-vs-Unsloth "
     "trade-offs."},
    {"id": "step05", "group": "Train", "kind": "run", "demo": "step05_train_run.py",
     "title": "Ch 6 · Watch the training run", "level": "advanced",
     "desc": "A simulated QLoRA run on a DGX Spark: decaying loss curve, warmup→cosine "
     "LR, throughput, checkpoints. Learn to read a training run and spot overfitting."},
    {"id": "step06", "group": "Evaluate", "kind": "run", "demo": "step06_evaluate.py",
     "title": "Ch 7 · Evaluate — before vs after", "level": "advanced",
     "desc": "The honest test: behaviour on held-out questions. Contrasts the base "
     "model with vs without the domain behaviour a LoRA bakes in — live (REAL) or "
     "stubbed (SIM) — plus how to gate fine-tuning quality in CI."},
    {"id": "step07", "group": "Serve", "kind": "run", "demo": "step07_export_serve.py",
     "title": "Ch 8 · Export, quantize & serve", "level": "advanced",
     "desc": "The last mile, all on-prem: merge the adapter, export to GGUF or "
     "quantize to NVFP4, register with Ollama, and serve the SAME OpenAI API your "
     "apps already use."},
    {
        "id": "outro", "group": "Serve", "kind": "concept",
        "title": "Appendix · The full sovereign loop", "level": "all levels",
        "desc": "You closed the loop:\n\n"
        "  data (on-prem) → recipe → train on DGX → eval → merge → GGUF/NVFP4 → serve\n\n"
        "…and not one training example or weight ever left the building.\n\n"
        "Pick-your-path cheat sheet:\n"
        "  • Fast iteration on one Spark        → Unsloth (QLoRA → GGUF → Ollama)\n"
        "  • Enterprise / multi-node            → NeMo AutoModel\n"
        "  • Need max quality, have the memory  → full SFT (8B on a Spark; 70B on a Station)\n"
        "  • Serve fastest on Blackwell         → quantize the merged model to NVFP4\n\n"
        "Where this sits in Week 19:\n"
        "  App 1 sovereign_dgx → run/serve models · App 2 (THIS) → adapt them to your domain\n"
        "  App 3 dgx_observability → trace agents (Phoenix + NeMo Agent Toolkit)\n"
        "  App 4 self_evolving_agent_v2 → the Week 18 agent, driven by your DGX model\n\n"
        "Your fine-tuned, domain-expert model is now a first-class citizen of the "
        "sovereign stack — ready for the agents in the next apps to call.",
    },
]
STEP_BY_ID = {s["id"]: s for s in STEPS}

app = FastAPI(title="Fine-tuning on a DGX — interactive tutorial")
_run_lock = asyncio.Lock()


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(PKG / "static" / "guide.html")


@app.get("/api/steps")
async def steps() -> dict:
    def public(s):
        return {k: s.get(k) for k in ("id", "group", "title", "desc", "kind", "level")} | \
               {"demo": s.get("demo")}
    return {"steps": [public(s) for s in STEPS], "mode": config.MODE,
            "conn": config.CONN, "conn_human": config.conn_human(),
            "model": config.MODEL, "base_url": config.BASE_URL,
            "base_model": config.BASE_MODEL, "domain": config.DOMAIN}


@app.get("/api/source/{step_id}")
async def source(step_id: str) -> dict:
    step = STEP_BY_ID.get(step_id)
    if not step or not step.get("demo"):
        return {"source": "(no source for this step)"}
    path = DEMOS / step["demo"]
    if not path.exists():
        return {"source": f"(missing file: {step['demo']})"}
    return {"source": path.read_text(), "filename": step["demo"]}


def _stream_demo(demo: str, timeout: float):
    async def gen():
        start = time.time()
        env = {**os.environ, "PYTHONUNBUFFERED": "1"}
        proc = await asyncio.create_subprocess_exec(
            PY, str(DEMOS / demo), cwd=str(PKG), env=env,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        try:
            while True:
                try:
                    line = await asyncio.wait_for(
                        proc.stdout.readline(),
                        timeout=max(1, start + timeout - time.time()))
                except asyncio.TimeoutError:
                    proc.kill()
                    yield (f"\n⏱  step exceeded {timeout:.0f}s — killed.\n"
                           f"__EXIT__ 124 {time.time()-start:.1f}\n")
                    return
                if not line:
                    break
                yield line.decode(errors="replace")
            await proc.wait()
            yield f"__EXIT__ {proc.returncode} {time.time()-start:.1f}\n"
        finally:
            if proc.returncode is None:
                proc.kill()
    return gen()


class RunRequest(BaseModel):
    step_id: str


@app.post("/api/run")
async def run_step(req: RunRequest):
    step = STEP_BY_ID.get(req.step_id)
    if step is None or step.get("kind") != "run":
        async def err():
            yield f"step {req.step_id!r} is not runnable\n__EXIT__ 1 0\n"
        return StreamingResponse(err(), media_type="text/plain")
    timeout = 300.0 if (config.MODE == "real" and req.step_id == "step06") else 120.0

    async def body():
        if _run_lock.locked():
            yield "⚠  another demo is already running — wait for it to finish.\n__EXIT__ 1 0\n"
            return
        async with _run_lock:
            yield f"$ {Path(PY).name} demos/{step['demo']}\n\n"
            async for chunk in _stream_demo(step["demo"], timeout):
                yield chunk
    return StreamingResponse(body(), media_type="text/plain")


@app.post("/api/cleanup")
async def cleanup() -> dict:
    removed = []
    sb = PKG / ".sandbox"
    if sb.exists():
        shutil.rmtree(sb); removed.append(".sandbox/")
    for pyc in PKG.rglob("__pycache__"):
        shutil.rmtree(pyc, ignore_errors=True)
    removed.append("__pycache__")
    return {"messages": [f"removed: {removed}"]}


if __name__ == "__main__":
    import uvicorn

    port = _pick_free_port(GUIDE_PORT)
    banner = ["", "  ▣  Fine-tuning on a DGX — interactive, explainable tutorial"]
    if config.MODE == "real":
        banner += [f"      ✓ REAL eval endpoint: {config.MODEL} @ {config.BASE_URL}",
                   "        (training loop is simulated unless run on a real DGX.)"]
    else:
        banner += ["      ◈ SIM mode — eval + training simulated, no GPU needed.",
                   "        go REAL for eval:  ollama run qwen3.6:35b-a3b-q8_0"]
    if port != GUIDE_PORT:
        banner += [f"      ⚠ port {GUIDE_PORT} busy — using {port} (set FT_GUIDE_PORT)."]
    banner += [f"      open  →  http://127.0.0.1:{port}", ""]
    print("\n".join(banner), flush=True)
    uvicorn.run(app, host="127.0.0.1", port=port)
