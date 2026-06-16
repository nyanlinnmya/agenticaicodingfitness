"""Call the AltoTech LiteLLM proxy (DGX) chat completions API.

Usage:
    python call_alto_llm.py                  # default model + prompt
    python call_alto_llm.py qwen3 "Hi!"      # pick model and prompt

Equivalent curl:
    curl -X POST 'https://alto-llm.altotech.ai/chat/completions' \
      -H 'Content-Type: application/json' \
      -H 'Authorization: Bearer <key>' \
      -d '{"model": "qwen3", "messages": [{"role": "user", "content": "Hello!"}]}'
"""

import os
import sys

import requests

BASE_URL = os.getenv("ALTO_LLM_BASE_URL", "https://alto-llm.altotech.ai")
API_KEY = os.getenv("ALTO_LLM_API_KEY", "sk-u7V_MmTJpBioO-ydubi6kQ")

# Models available on this proxy (GET /v1/models):
#   qwen3-vl, qwen3, qwen3.6, nemotron, llama3.3, gemma4, gemma3
# NOTE: backends are shared/flaky — pick a healthy one. 'nemotron' has been
# returning 502/hanging (→ client timeout); 'qwen3' is the reliable default.
DEFAULT_MODEL = "qwen3"


def chat(prompt: str, model: str = DEFAULT_MODEL) -> str:
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Hello! Tell me in one sentence who you are."
    print(f"--- model: {model} ---")
    try:
        print(chat(prompt, model))
    except requests.exceptions.ReadTimeout:
        print(f"[timeout: the '{model}' backend didn't respond within 120s — it's "
              "likely overloaded/down. Try a healthy model, e.g. qwen3.]")
    except requests.exceptions.HTTPError as e:
        print(f"[gateway error {e.response.status_code} for model '{model}' — its "
              "backend is likely down. Try a healthy model, e.g. qwen3.]")
