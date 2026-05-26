---
name: models-and-patterns
description: "Help choose the right LLM and the right agent design pattern for a task, and recap the canonical patterns (ReAct, Reflection, Plan-and-Execute, Router, Swarm, RAG, HITL, Guardrails). Covers how to pick a model by capability/cost/latency/context, how to pick a framework, and a map of all the course concepts. Use when someone asks 'which model/framework should I use?', wants a pattern catalog, or is reviewing Week 11 / wants a whole-course recap."
when_to_use: "Learner is deciding which model or framework to use, wants the catalog of agent patterns, or wants a big-picture recap of the whole course (Week 11 mastery lab)."
---

# Choosing Models & Patterns — The Decision Layer (Week 11)

> **The one idea:** Building agents well is mostly *judgment*: which model, which framework, which pattern for *this* problem. This skill is the decision toolkit and the map that ties all 14 weeks together.

---

## Part A — Picking a model

There's no "best model," only the best fit on four axes:

| Axis | Question | When it dominates |
|---|---|---|
| **Capability** | Can it actually do the task (reasoning, code, vision)? | Hard reasoning, complex code, agentic loops |
| **Cost** | $ per million tokens? | High volume, many agents, tight budget |
| **Latency** | How fast does it respond? | Real-time chat, user-facing, big swarms |
| **Context** | How much can it read at once? | Long docs, large codebases, big histories |

**Rules of thumb taught in class:**
- **Frontier model (e.g. Opus/Sonnet tier)** for the hard thinking — planning, tricky code, the "brain" of an agent.
- **Small/fast model (e.g. Haiku tier)** for high-volume, simple, or parallel work — classifiers, routers, swarm members. The Week 9 swarm and Week 14 hotel agents use Haiku *on purpose* for cost.
- **Mix models in one system:** a frontier model plans, cheap models execute. This is a standard cost-control move.
- **Open/alternative providers** (OpenRouter, z.ai/GLM, Qwen) appear across the course — the message: your code shouldn't be married to one vendor.

> 📁 Class repo: `week11/README.md` — an interactive **LLM Model Atlas**, a **Pick-the-Right-Model wizard**, and a **capability radar** comparing models. `week4/openrouterfreemodel.py` shows routing to alternative providers.

---

## Part B — Picking a framework

| Use… | When… |
|---|---|
| **Raw Anthropic SDK** | You want full control / are learning the fundamentals / custom orchestration (the swarm). |
| **Claude Agent SDK** | You want the agent loop + MCP handled for you. |
| **CrewAI** | Role-based teams, sequential/parallel crews, fast to stand up. |
| **LangGraph** | Stateful graphs, routing, cycles, fine-grained control flow. |
| **AutoGen / AG2** | Agents that converse with each other. |
| **MCP** | You need standardized, reusable tools across apps. |

Start with the **simplest thing that works**. Reach for a framework when hand-rolling the orchestration becomes the bottleneck — not before.

---

## Part C — The pattern catalog

The reusable shapes that show up everywhere. Knowing the name helps you reach for the right one.

| Pattern | What it does | Course link |
|---|---|---|
| **ReAct** | Reason → Act → Observe → repeat. The base agent loop. | `agent-loops` (W5) |
| **Tool Use** | Model calls functions/APIs to act. | `tool-use` (W3) |
| **Reflection** | Agent critiques and revises its own output. | code-review agent (W5) |
| **Plan-and-Execute** | Make a plan, then carry out the steps. | pipeline (W4) |
| **Router / Dispatcher** | Classify input → send to the right specialist. | LangGraph (W9) |
| **Sequential pipeline** | Assembly line of agents. | CrewAI (W9) |
| **Parallel swarm** | Fan out concurrently, then aggregate. | asyncio swarm (W9) |
| **Hierarchical** | Manager delegates to workers. | MAS theory (W9) |
| **RAG** | Retrieve relevant docs, then answer. | `rag-knowledge-agents` (W8) |
| **GraphRAG** | Retrieve over a knowledge graph. | `agent-memory-graphs` (W14) |
| **Event sourcing / memory** | Append facts; recall later. | `agent-memory-graphs` (W14) |
| **Human-in-the-loop (HITL)** | Pause for human approval on risky actions. | production practice |
| **Guardrails** | Validate/constrain inputs & outputs for safety. | production practice |

> 📁 Class repo: `week11/README.md` includes a **Pattern Library**, a topology **Playground** (sequential/parallel/router/swarm/reflection), and a 25-question **mastery quiz**.

---

## The whole course on one page

```
W2  LLM basics        → text in / text out, messages, streaming, memory   [llm-fundamentals]
W3  Tool use          → model calls your functions                        [tool-use]
W4  Pipelines + IoT   → chained steps; drones & smart lights              [agent-loops]
W5  Agent loop        → REASON→ACT→OBSERVE, the reusable Agent class       [agent-loops]
W6  Full-stack app    → put an agent behind a real API (Express/TS/PG)
W7  MCP & Skills      → reusable tools (MCP) + reusable know-how (skills)  [mcp-and-skills]
W8  RAG               → ground answers in your documents                   [rag-knowledge-agents]
W9  Multi-agent       → CrewAI / LangGraph / AutoGen / swarms              [multi-agent-systems]
W10 Production        → eval, monitoring, cost, HITL, guardrails
W11 Mastery           → pick models/frameworks/patterns                    [models-and-patterns]
W14 Graph memory      → Neo4j, GraphRAG, durable multi-agent memory        [agent-memory-graphs]
```

Each `[skill]` above is a skill in this plugin. Start at your gap and walk forward.

---

## Decision flow for a new project

1. **Is one model call enough?** → just call the API (`llm-fundamentals`). Don't build an agent.
2. **Does it need to *act* (APIs, files, math)?** → add tools (`tool-use`).
3. **Multi-step toward a goal?** → agent loop (`agent-loops`).
4. **Answers must come from your docs?** → RAG (`rag-knowledge-agents`).
5. **Genuinely distinct sub-tasks / parallelism?** → multi-agent (`multi-agent-systems`). Otherwise stay single-agent.
6. **Must remember across runs / coordinate a team?** → graph memory (`agent-memory-graphs`).
7. **Picking the model/framework?** → this skill, Parts A & B.

Bias toward the *simplest* rung that solves the problem.

---

## 🧪 Guided lab (offer this)

Practice judgment, not syntax:

1. **Bring a real goal** the learner cares about (e.g. "summarize my unread emails", "answer questions about our product docs", "monitor a server and alert me").
2. **Walk the decision flow** above together, out loud, ruling rungs in/out. Land on the *simplest* architecture that works.
3. **Choose a model** on the four axes — and decide if a single model or a frontier+cheap mix fits.
4. **Choose a framework** (or none). Justify it in one sentence.
5. **Name the patterns** their design uses (e.g. "router + RAG + HITL"). Sketch the topology.
6. **Sanity check:** did they over-engineer? Could a rung-1 or rung-2 solution do it? Simplify.
7. **Stretch:** open `week11/README.md` in a browser and run the model wizard, the pattern playground, and the 25-question quiz to pressure-test their mental model.

End with the meta-lesson: "frameworks and models change every few months; the *patterns* and the *judgment* are what you keep."
