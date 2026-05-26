---
name: agent-loops
description: "Teach the core agent loop (REASON → ACT → OBSERVE → repeat) — the thing that turns a tool-using model into an autonomous agent that pursues a goal across many steps. Covers the reusable Agent class, stop conditions, iteration limits, and autonomous multi-step pipelines. Use when someone asks 'what actually IS an agent?', wants to build an agent that works toward a goal on its own, or is reviewing Weeks 4–5."
when_to_use: "Learner wants to build an autonomous agent that loops toward a goal, asks what distinguishes an agent from a chatbot, wants a reusable Agent framework, or is catching up on Weeks 4–5."
---

# Agent Loops — From Tool Caller to Autonomous Agent (Weeks 4–5)

> **The one idea:** An *agent* is a loop. Give it a goal and tools, then let it repeatedly **REASON** (decide next step) → **ACT** (call a tool) → **OBSERVE** (read the result) → repeat, until it declares itself done. A chatbot answers once; an agent keeps going until the job is finished.

This is the ReAct pattern (Reason + Act). Everything in Weeks 6–14 sits on top of it.

---

## Chatbot vs. Agent

| Chatbot (Week 2) | Agent (Week 5) |
|---|---|
| One question → one answer | One **goal** → many steps |
| You drive every turn | It drives itself in a loop |
| No tools, or you call them manually | It decides which tools to call and when |
| Stops after replying | Stops when the goal is met (or hits a limit) |

---

## The reusable Agent class

This is the heart of the course — a ~40-line class that runs the loop for *any* goal and *any* set of tools:

```python
import anthropic, json
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()

class Agent:
    def __init__(self, system_prompt, tools, tool_executor, max_iterations=10):
        self.system_prompt = system_prompt
        self.tools = tools
        self.tool_executor = tool_executor      # your execute_tool(name, inputs)
        self.max_iterations = max_iterations

    def run(self, goal):
        messages = [{"role": "user", "content": goal}]

        for i in range(self.max_iterations):
            print(f"--- Iteration {i+1} ---")

            # REASON + ACT: ask the model what to do next
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=self.system_prompt,
                tools=self.tools,
                messages=messages,
            )

            has_tool_use = any(b.type == "tool_use" for b in response.content)
            text = [b.text for b in response.content if b.type == "text"]
            for t in text:
                print(f"  💭 {t[:200]}")          # the agent thinking out loud

            # DONE? finished its turn with no tool calls = goal complete
            if response.stop_reason == "end_turn" and not has_tool_use:
                print(f"✅ Done in {i+1} iterations")
                return text[-1] if text else "Done"

            # OBSERVE: run each tool, feed results back, loop again
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  🔧 {block.name}({json.dumps(block.input)[:100]})")
                    out = self.tool_executor(block.name, block.input)
                    print(f"  📋 {str(out)[:150]}")
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(out),
                    })
            messages.append({"role": "user", "content": results})

        return "⚠️ Max iterations reached"
```

**The two things that make it an *agent* and not a chatbot:**
1. **The loop with a stop condition** — `stop_reason == "end_turn" and not has_tool_use` means "the model is satisfied, nothing left to do."
2. **`max_iterations`** — the seatbelt. Without it, a confused agent can loop (and bill) forever. Always cap it.

> 📁 Class repo: `week5/autoagent.py` — the full class plus a **Code Review Agent** that reads a file, lints it, fixes bugs, rewrites it, and runs it to verify.

---

## Example: the Code Review Agent

Same `Agent` class, given file-system tools and a process to follow in its system prompt:

```python
agent = Agent(
    system_prompt="""You are a code review agent. Your process:
1. Read the target file
2. Run the linter to find issues
3. Fix bugs and style issues
4. Write the fixed version
5. Run it to verify it works; if it errors, fix and retry.
When clean and working, explain what you fixed.""",
    tools=code_review_tools,          # read_file, write_file, run_python, run_lint
    tool_executor=execute_code_tool,
    max_iterations=10,
)
agent.run("Review and fix 'sample.py'. Fix all bugs and style issues.")
```

The system prompt is the agent's **playbook**. The loop just keeps asking "what's next?" until the playbook is satisfied.

---

## Autonomous pipelines (Week 4)

Before the generic loop, Week 4 built a fixed-sequence **research pipeline** — a hand-wired chain of LLM steps:

```
generate search queries → web search → summarize sources
   → synthesize → self-score the quality → write a Markdown report
```

The difference is **who decides the order**:
- **Pipeline (Week 4):** *you* hard-code the steps. Predictable, easy to debug. Good when the workflow is known.
- **Agent loop (Week 5):** *the model* decides the steps via tool calls. Flexible, handles surprises. Good when the path isn't known upfront.

Real systems mix both. (Week 4 also drove a **DJI Tello drone** — the same "decide → act → observe" idea, but the "act" was a physical flight command.)

> 📁 Class repo: `week4/pipeline.py` (autonomous research pipeline), `week4/dronecontrol.py` (physical actions).

---

## 🧪 Guided lab (offer this)

Build an agent from the `Agent` class and watch it loop:

1. **Reuse the class.** Have them paste the `Agent` class and the `execute_tool` from the `tool-use` skill (calculator + weather).
2. **Give it a multi-step goal:** *"Find the temperature in Bangkok and Tokyo, then tell me which is hotter and by how many degrees."* This forces ≥2 tool calls + reasoning. Watch the `💭`/`🔧`/`📋` trace across iterations.
3. **Read the trace together.** Point out each REASON→ACT→OBSERVE cycle in the printout. This is where "what is an agent" finally clicks.
4. **Lower `max_iterations` to 1.** Run again — it can't finish. Show how the cap is a safety limit, then restore it.
5. **Build a mini code agent.** Give it `read_file` + `write_file` tools and ask it to "add docstrings to every function in `foo.py`." Let it read, edit, and confirm.
6. **Stretch:** discuss when to choose a fixed *pipeline* vs. a free-running *agent* (predictability vs. flexibility), pointing at `week4/pipeline.py`.

End by framing the next step: "one agent is powerful; in Week 9 we run *several* agents together — that's multi-agent systems."
