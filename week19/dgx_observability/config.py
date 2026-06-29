#!/usr/bin/env python3
"""Shared config for Week 19 **Observability on a DGX** (Phoenix + NeMo Agent Toolkit).

You can't manage what you can't see. This app instruments a SOVEREIGN agent — one
whose model runs on your DGX — with OpenTelemetry-style spans, views them the way
Arize Phoenix does, evaluates traces, and then shows the NVIDIA NeMo Agent Toolkit
(NAT) running a config-driven workflow against the same local model.

Two modes, auto-detected:
  • REAL — a live OpenAI-compatible endpoint (Ollama / vLLM on this box or a DGX).
    The agent makes genuine local calls; spans wrap real latency + token counts.
    If `arize-phoenix` is installed AND running, traces can export to it for real.
  • SIM  — no endpoint → the agent loop is simulated; spans + the Phoenix-style
    span tree are rendered from the simulation. Real commands always shown.

Cloud cost is always $0.

Env overrides::  DGX_BASE_URL · DGX_MODEL · DGX_MODE=sim|real · PHOENIX_ENDPOINT
"""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


# ── connection switch: local DGX · tunnel (ngrok/cloudflared) · cloud provider ─
def _resolve_connection() -> tuple[str, str, str]:
    conn = os.environ.get("DGX_CONN", "").strip().lower()
    explicit = os.environ.get("DGX_BASE_URL") or os.environ.get("EDGE_BASE_URL")
    key = os.environ.get("DGX_API_KEY") or os.environ.get("EDGE_API_KEY")

    def _infer(url: str) -> str:
        h = (urlparse(url).hostname or "").lower()
        if h in ("localhost", "127.0.0.1", "::1") or h.endswith(".local") \
                or h.startswith(("192.168.", "10.", "172.")):
            return "local"
        if any(t in h for t in ("ngrok", "trycloudflare", "loca.lt", "ts.net", "tunnel")):
            return "tunnel"
        return "cloud"

    if explicit:
        return (conn or _infer(explicit)), explicit, (key or "dgx")
    if conn == "tunnel":
        return "tunnel", os.environ.get("DGX_TUNNEL_URL", ""), (key or os.environ.get("DGX_TUNNEL_KEY", "dgx"))
    if conn == "cloud":
        return "cloud", os.environ.get("DGX_CLOUD_URL", "https://ollama.com/v1"), (key or os.environ.get("DGX_CLOUD_KEY", ""))
    return "local", "http://localhost:11434/v1", (key or "dgx")


CONN, BASE_URL, API_KEY = _resolve_connection()


def conn_human() -> str:
    return {"local": "local DGX / localhost", "tunnel": "DGX over a tunnel",
            "cloud": "cloud provider"}.get(CONN, CONN)


def _open(url: str, timeout: float = 4):
    headers = {}
    if API_KEY and CONN != "local":
        headers["Authorization"] = f"Bearer {API_KEY}"
    return urlopen(Request(url, headers=headers), timeout=timeout)

_PREFERRED = [
    "qwen3.6:35b-a3b-q8_0", "qwen3.6", "gemma4:12b", "gemma4", "llama3.1:8b", "qwen2.5",
]

DEFAULT_MAX_TOKENS = 512
PKG = Path(__file__).resolve().parent
SANDBOX = PKG / ".sandbox"

# Where a real Phoenix collector would listen (OTLP). Used only if Phoenix is up.
PHOENIX_ENDPOINT = os.environ.get("PHOENIX_ENDPOINT", "http://localhost:6006")


def _native_base() -> str:
    return BASE_URL.rstrip("/").removesuffix("/v1") + "/api"


def list_local_models() -> list[str]:
    if not BASE_URL:
        return []
    import json
    try:
        with _open(_native_base() + "/tags", timeout=3) as r:
            return [m["name"] for m in json.loads(r.read().decode()).get("models", [])]
    except Exception:
        pass
    try:
        with _open(BASE_URL.rstrip("/") + "/models", timeout=3) as r:
            return [m["id"] for m in json.loads(r.read().decode()).get("data", [])]
    except Exception:
        return []


def endpoint_up() -> bool:
    if not BASE_URL:
        return False
    try:
        with _open(_native_base() + "/tags", timeout=4):
            return True
    except Exception:
        try:
            with _open(BASE_URL.rstrip("/") + "/models", timeout=4):
                return True
        except Exception:
            return False


def phoenix_up() -> bool:
    try:
        with urlopen(PHOENIX_ENDPOINT, timeout=2):
            return True
    except Exception:
        return False


def mode() -> str:
    forced = os.environ.get("DGX_MODE", "auto").lower()
    if forced in ("sim", "real"):
        return forced
    return "real" if endpoint_up() else "sim"


def pick_model(available: list[str] | None = None) -> str:
    pinned = os.environ.get("DGX_MODEL")
    if pinned:
        return pinned
    available = available if available is not None else list_local_models()
    for want in _PREFERRED:
        for have in available:
            if have == want or have.startswith(want):
                return have
    return available[0] if available else "qwen3.6:35b-a3b-q8_0"


MODE = mode()
MODEL = pick_model()


def ensure_sandbox() -> Path:
    SANDBOX.mkdir(parents=True, exist_ok=True)
    return SANDBOX
