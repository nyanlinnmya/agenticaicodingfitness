---
name: tool-use
description: "Teach how an LLM uses tools (function calling) to act on the world — define a tool schema, detect when the model wants to call it, run the function, feed the result back. Use when someone asks 'how does the AI call my code / APIs?', wants to give Claude abilities (weather, calculator, web search, smart-home), is confused about tool_use / tool_result blocks, or is reviewing Week 3."
when_to_use: "Learner wants the model to DO things (call APIs, run code, control devices), asks about function calling / tool_use blocks, or is catching up on Week 3."
---

# Tool Use — Giving the Model Hands (Week 3)

> **The one idea:** The model can't run code or hit an API itself. Instead it *asks you* to, by emitting a `tool_use` block. You run the function and hand back a `tool_result`. The model decides **what** to call; **your code** does the calling.

This is the single most important leap from "chatbot" to "agent."

---

## The tool-use loop (memorize this shape)

```
1. You send: messages + a list of tool definitions
2. Model replies with a `tool_use` block:  "call get_weather(city='Bangkok')"
3. YOUR code runs the real function → gets "32°C"
4. You send the answer back as a `tool_result` block
5. Model reads it and writes the final human answer
   (repeat 2–4 if it wants more tools)
```

---

## 1. Define a tool (it's just JSON describing a function)

A tool definition is a name + description + a JSON Schema of its inputs. The **description is the prompt** — the model decides whether to call the tool based on it, so write it well.

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. 'Bangkok'"}
            },
            "required": ["city"],
        },
    },
    {
        "name": "calculate",
        "description": "Evaluate a mathematical expression. Use for any math.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "e.g. '500000 * 0.2'"}
            },
            "required": ["expression"],
        },
    },
]
```

## 2. Implement what each tool actually does

The model never runs this — you do. It's plain Python.

```python
import requests

def execute_tool(name, inputs):
    if name == "calculate":
        # ⚠️ eval() is for the demo only. Use simpleeval / ast in real code.
        return str(eval(inputs["expression"]))
    if name == "get_weather":
        city = inputs["city"]
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        ).json()["results"][0]
        w = requests.get(
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={geo['latitude']}&longitude={geo['longitude']}&current=temperature_2m"
        ).json()["current"]
        return f"Weather in {city}: {w['temperature_2m']}°C"
    return f"Unknown tool: {name}"
```

## 3. The loop that ties it together

```python
import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()

def ask(question):
    messages = [{"role": "user", "content": question}]
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )
        # Did the model ask for any tools?
        tool_calls = [b for b in response.content if b.type == "tool_use"]
        if not tool_calls:
            return response.content[0].text       # no tools → final answer

        # Record the model's turn (including its tool request)
        messages.append({"role": "assistant", "content": response.content})

        # Run each requested tool and send results back
        for call in tool_calls:
            print(f"  🔧 {call.name}({call.input})")
            result = execute_tool(call.name, call.input)
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": call.id,   # MUST match the call's id
                    "content": result,
                }],
            })

print(ask("What's 18% of 4,500, and what's the weather in Bangkok?"))
```

**The three things people get wrong:**
1. **Forgetting to append the assistant turn** (`response.content`) before the tool_result — the IDs won't line up.
2. **Mismatched `tool_use_id`** — each `tool_result` must carry the exact `id` of the `tool_use` it answers.
3. **Looping forever / not looping** — you `while True` because the model may want several rounds of tools before it's done.

> 📁 Class repo: `week3/toolsuse.py` (calculator + weather + **Tapo smart-light control**), `week3/buildsmartassistant3tools.py` (adds web search + file reading).

---

## Why this matters

With tools, the model stops being a text box and becomes something that can **check the weather, do exact math, search the web, read files, or switch on a real light bulb.** In Week 3 the class wired this to TP-Link Tapo bulbs — Claude literally turned the lights on/off in the room.

The agent loop (next skill) is *this exact loop* plus a system prompt, a goal, and an iteration cap.

---

## 🧪 Guided lab (offer this)

Walk the learner through adding **one tool at a time** to a working script:

1. **Start with `calculate` only.** Get the full loop running with a single tool. Ask "what's 17 * 23?" and watch the `🔧` print fire.
2. **Add `get_weather`.** Now ask a question that needs *both* ("weather in Bangkok, and 18% of 4500?") — show how the model can call multiple tools in sequence and the loop handles it.
3. **Write their own 3rd tool.** Pick something fun and simple: `roll_dice(sides)`, `get_time()`, or `read_file(path)`. They define the schema, write the function, register it. (Class homework files `week3/hwadd4thtool.py` / `hwadd5thtool.py` are exactly this exercise.)
4. **Break the `tool_use_id`** on purpose to see the error, then fix it — so they remember why it matters.
5. **Stretch:** point them at the real Tapo example in `week3/toolsuse.py` and discuss how `control_lights` is just another tool whose "function" happens to be an HTTP call to a smart bulb.

Emphasize the rhythm: *schema → implementation → register → run → observe the 🔧 calls.*
