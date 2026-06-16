"""Call the AltoTech LiteLLM proxy (DGX) chat completions API with streaming.

Usage:
    python call_alto_llm_streaming.py                  # default model + prompt
    python call_alto_llm_streaming.py qwen3 "Hi!"      # pick model and prompt

With "stream": true the proxy returns Server-Sent Events — one
`data: {json}` line per token chunk, terminated by `data: [DONE]`.
"""

import json
import os
import sys
from collections.abc import Iterator

import requests

BASE_URL = os.getenv("ALTO_LLM_BASE_URL", "https://alto-llm.altotech.ai")
API_KEY = os.getenv("ALTO_LLM_API_KEY", "sk-u7V_MmTJpBioO-ydubi6kQ")

# Models available on this proxy (GET /v1/models):
#   qwen3-vl, qwen3, qwen3.6, nemotron, llama3.3, gemma4, gemma3
# NOTE: backends are shared/flaky — pick a healthy one. 'nemotron' has been
# returning 502/hanging (→ client timeout); 'qwen3' is the reliable default.
DEFAULT_MODEL = "qwen3"


def chat_stream(prompt: str, model: str = DEFAULT_MODEL) -> Iterator[str]:
    """Yield response text chunks as they arrive from the server."""
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        },
        stream=True,
        timeout=120,
    )
    response.raise_for_status()

    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        payload = line[len("data: "):]
        if payload == "[DONE]":
            break
        chunk = json.loads(payload)
        delta = chunk["choices"][0]["delta"]
        content = delta.get("content")
        if content:
            yield content


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
    prompt = sys.argv[2] if len(sys.argv) > 2 else "tell me who is altotech global in one sentence"
    print(f"--- model: {model} (streaming) ---")
    try:
        for chunk in chat_stream(prompt, model):
            print(chunk, end="", flush=True)
        print()
    except requests.exceptions.ReadTimeout:
        print(f"\n[timeout: the '{model}' backend didn't respond within 120s — it's "
              "likely overloaded/down. Try a healthy model, e.g. qwen3.]")
    except requests.exceptions.HTTPError as e:
        print(f"\n[gateway error {e.response.status_code} for model '{model}' — its "
              "backend is likely down. Try a healthy model, e.g. qwen3.]")
