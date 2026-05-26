---
name: llm-fundamentals
description: "Teach the absolute basics of talking to an LLM programmatically — single message, streaming, multi-turn conversation memory, and token counting. Use when someone is new to the Claude/Anthropic API, asks 'how do I call the model from Python?', wants to understand messages/roles/tokens, or is reviewing Week 2 of the Agentic Coding Fitness course."
when_to_use: "Beginner is starting out, asks how to call an LLM from code, doesn't understand messages/roles/streaming/tokens, or is catching up on Week 2."
---

# LLM Fundamentals — Talking to the Model (Week 2)

> **The one idea:** An LLM call is just *text in → text out*. Everything else (agents, tools, multi-agent swarms) is built on top of this single primitive. Master this first.

## What you'll understand after this skill
1. How to send one message and read the reply.
2. What "tokens" are and why you count them (cost + limits).
3. **Streaming** — printing the answer word-by-word for a better feel.
4. **Multi-turn memory** — how a chatbot "remembers" earlier messages (spoiler: *you* resend them).

---

## Setup (one time)

```bash
pip install anthropic python-dotenv
```

Create a `.env` file next to your script:

```ini
ANTHROPIC_API_KEY="sk-ant-api03-...your key..."
```

`anthropic.Anthropic()` reads that key from the environment automatically — never hard-code keys in your file.

---

## 1. The single call — the atom of everything

```python
import os
from dotenv import load_dotenv
load_dotenv()
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain agentic AI in 3 sentences."}
    ],
)
print(response.content[0].text)
print(f"\nTokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out")
```

**Read it line by line:**
- `messages` is a list of turns. Each turn has a `role` (`"user"` or `"assistant"`) and `content`.
- `max_tokens` caps how long the *reply* can be (1 token ≈ ¾ of a word).
- `response.content` is a **list of blocks** — text is at `response.content[0].text`. (Later, tool calls show up as other block types — see the `tool-use` skill.)
- `response.usage` tells you exactly what you paid: input tokens (your prompt) + output tokens (the reply).

> 📁 Class repo: `week2/claudeapicall.py`

---

## 2. Streaming — answers that appear as they're written

A single `create()` call makes you wait for the whole answer. Streaming prints each chunk as it arrives — the difference between a frozen screen and a chat that feels alive.

```python
with client.messages.stream(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a haiku about debugging."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
print()
```

> 📁 Class repo: `week2/claudestreamingapi.py`

---

## 3. Multi-turn memory — how a chatbot "remembers"

**Key insight that trips everyone up:** the API is *stateless*. The model remembers nothing between calls. A conversation only continues because **you keep a list and resend the whole history every time.** That list IS the chatbot's short-term memory.

```python
messages = []  # <-- this list is the memory

def chat(text):
    messages.append({"role": "user", "content": text})
    reply = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1000,
        messages=messages,        # resend EVERYTHING each time
    ).content[0].text
    messages.append({"role": "assistant", "content": reply})  # remember the reply too
    return reply

print(chat("My name is Aom."))
print(chat("What's my name?"))   # it knows — because "Aom" is still in `messages`
```

If you forget to append the assistant's reply back into `messages`, the model gets amnesia on the next turn. Try it and watch it break — that's the lesson.

> 📁 Class repo: `week2/claudemulti_turn.py` and the interactive loop in `week7/agent.py`

---

## Mental model to carry forward

```
[ messages list ]  →  client.messages.create()  →  response.content
       ↑__________________________________________________|
              (you append the reply to keep the memory)
```

Every agent in this course is this loop with extras bolted on: **tools** (next skill), a **goal + iteration limit** (agent loops), or **many of these running together** (multi-agent systems).

---

## 🧪 Guided lab (offer this)

When the learner is ready, walk them through building a tiny terminal chatbot **from a blank file**, one step at a time. Don't paste the whole thing — make them type each piece and run it:

1. **Step 1 — one call.** Have them write just the single-call example and run it. Confirm they see text + a token count.
2. **Step 2 — make it a loop.** Wrap it in `while True:` with `input("You: ")`, and a `quit` exit. At this point it answers but has *no memory* — point that out.
3. **Step 3 — add memory.** Introduce the `messages` list, append the user turn before the call and the assistant turn after. Now ask it "what's my name?" two turns later to prove memory works.
4. **Step 4 — break it on purpose.** Tell them to comment out the line that appends the assistant reply. Run again, watch it forget. Restore it. *This* is the moment the concept clicks.
5. **Step 5 — stretch.** Switch `create()` to `stream()` so replies type out live.

Keep each step to a few lines, run after every step, and explain what changed. End by connecting it forward: "this `messages` loop is the skeleton of every agent — next we give it tools."
