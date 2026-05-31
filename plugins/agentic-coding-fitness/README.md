# 🏋️ Agentic Coding Fitness — Bootcamp Plugin

A Claude Code plugin that turns **everything we built in class** — plus the strategy blueprint behind it — into skills you can *talk to*. For anyone who couldn't keep up on the day, wants to review at their own pace, or is ready to take an agent from "works on my machine" to **production**.

It's **16 bite-sized skills**, one per big idea. Each skill:
- **Teaches** the idea in plain language (no jargon walls),
- **Shows runnable example code** (with pointers to the real `weekN/` files in this repo),
- **Offers an interactive guided lab** — a *kata* with a warm-up, a runnable drill (using a tiny `MockLLM` so it costs **$0**), and an explicit pass threshold.

You don't read these like a book. You *talk to Claude* and the right skill loads automatically when your question matches.

> **Honesty note:** most skills are grounded in real `weekN/` code you can run. A few map ahead of the course — the **A2A protocol** is fully conceptual, and parts of **curriculum** and **vibe-coding** come from the blueprint rather than this repo (flagged ⚠️ in the tables below). A couple of otherwise-grounded skills (e.g. **production-and-observability**) also mark an individual *section* `⚠️ Conceptual` where it reaches past the repo (OpenTelemetry, OWASP-ASI). Every banner sits right next to the content it qualifies, so you always know what's runnable here vs. what's the map.

---

## 📦 Install (2 minutes)

In Claude Code:

```
/plugin marketplace add kwarodom/agenticaicodingfitness
/plugin install agentic-coding-fitness@agentic-coding-fitness
```

> Already have the repo cloned locally? You can instead point at the folder:
> `/plugin marketplace add /path/to/agenticaicodingfitness`

Then restart Claude Code (or run `/reload-plugins`). That's it.

To confirm it's loaded, run `/help` or just ask: *"I'm new to AI agents, where do I start?"*

---

## 🚀 How to use it

Just **ask Claude in plain language** — the matching skill activates on its own:

| You say… | Skill that wakes up |
|---|---|
| "How do I call Claude from Python?" | `llm-fundamentals` |
| "How does the AI call my code / APIs?" | `tool-use` |
| "What actually *is* an agent? Build me one." | `agent-loops` |
| "What's MCP? How do I build a server? Are skills safe?" | `mcp-and-skills` |
| "How do I make it answer from my PDFs — and know it's right?" | `rag-knowledge-agents` |
| "How do I make agents work together?" | `multi-agent-systems` |
| "How do agents remember across runs?" | `agent-memory-graphs` |
| "GDS / PageRank / Text2Cypher / how do I *evaluate* GraphRAG?" | `knowledge-graph-mastery` |
| "Which model/pattern should I use? What are the 12 patterns?" | `models-and-patterns` |
| "How do I take this prototype to production safely?" | `production-and-observability` |
| "How do I *score* and CI-gate an agent's quality?" | `agent-evaluation` |
| "Give me an exercise to practice X." | `agent-drills` |
| "What order should I learn this in?" | `curriculum-and-periodization` |
| "How do I work *with* the agent without shipping bugs?" | `vibe-coding-and-security` |
| "How do agents on different teams/frameworks talk?" | `a2a-protocol` ⚠️ |
| "How do I write my *own* skill?" | `skill-authoring` |

Or ask for a lab directly: *"Give me the guided lab for tool use."*

**Don't know where to start?** Ask: *"What order should I learn this in?"* → `curriculum-and-periodization` places you on the map, or `models-and-patterns` has the one-page recap of the whole course.

---

## 🗺️ The 16 skills

### Foundations — the core course (talk → tools → agents → data → teams → memory)

| # | Skill | Concept | Class weeks | Grounded |
|---|---|---|---|---|
| 1 | **llm-fundamentals** | Talking to an LLM: messages, streaming, memory, tokens, caching | W2 | ✅ |
| 2 | **tool-use** | Function calling — giving the model hands (+ the Tool-Definition-Mastery drill) | W3 | ✅ |
| 3 | **agent-loops** | REASON→ACT→OBSERVE; ReAct + bounded execution; token-budget guardrails | W4–W5 | ✅ |
| 4 | **mcp-and-skills** | MCP (use *and build* servers) + skills, security, CLAUDE.md context engineering | W7 | ✅ |
| 5 | **rag-knowledge-agents** | RAG: ground answers in your docs — and *evaluate* it with RAGAS | W8 | ✅ |
| 6 | **multi-agent-systems** | 6 orchestration patterns, topologies/state, supervisor + checkpointing | W9–W10 | ✅ |
| 7 | **agent-memory-graphs** | Durable memory with Neo4j; GraphRAG; event sourcing | W14 | ✅ |
| 8 | **knowledge-graph-mastery** | Production GraphRAG: Cypher+GDS, ingestion, 7 frameworks, RAGAS | W15 | ✅ |
| 9 | **models-and-patterns** | The 12-pattern taxonomy, framework matrix, cost economics, HITL/guardrails | W11 | ✅ |

### Production & practice — ship it, score it, rep it

| # | Skill | Concept | Class weeks | Grounded |
|---|---|---|---|---|
| 10 | **production-and-observability** | See it (LangSmith/OTel), stop it (HITL + checkpointing), afford it (cost) | W10 | ✅ |
| 11 | **agent-evaluation** | Golden datasets, eval frameworks, LLM-as-judge, the 5-gate CI/CD pipeline | W10 & W15 | ✅ |
| 12 | **agent-drills** | The practice menu — a catalog of katas grounded in the 14 `week11/exercises` | cross-cutting | ✅ |

### Platform & meta — the map, the discipline, the frontier, the craft

| # | Skill | Concept | Class weeks | Grounded |
|---|---|---|---|---|
| 13 | **curriculum-and-periodization** | The syllabus: 4 phases, progressive overload, the 16-week → real weeks-2–15 map | the whole program | ⚠️ partial |
| 14 | **vibe-coding-and-security** | Context engineering, TDD vibe coding, the ~45% vuln reality, hand-off vs control | W6 / cross-cutting | ⚠️ partial |
| 15 | **a2a-protocol** | Agent-to-Agent: agent cards, task lifecycle, A2A vs MCP — the map for going cross-service | cross-cutting | ⚠️ conceptual |
| 16 | **skill-authoring** | Write your *own* skills: the two types, anatomy, the creation pipeline, evaluation | W7+ | ✅ |

> The examples reference the real code in this repo's `week2/ … week15/` folders (Week 15's deep dive lives in `week15/kg_mastery/`). Clone the repo alongside installing the plugin to run them directly.

---

## 🎯 Suggested learning paths

- **Total beginner:** 1 → 2 → 3 → then pick what interests you.
- **"I can call the API, what's next?":** 2 → 3 → 4.
- **"I want agents that collaborate":** 3 → 6 → 7.
- **"I want it to use my data":** 5 → 7 → 8.
- **"I want production GraphRAG I can trust":** 7 → 8 → 11 (build, query with algorithms, then *evaluate* + gate).
- **"I'm taking a prototype to production":** 9 → 10 → 11 (judgment → see/stop/afford → score & gate).
- **"I want to work *with* the agent well":** 14 → 4 → 16 (vibe-coding → context/CLAUDE.md → author your own skills).
- **"Just tell me what order":** 13 (the curriculum map) or 9 (the one-page recap).
- **"Give me reps":** 12 (the drill library) — pick a kata by skill, time, and level.

---

## 🛠️ Requirements for the labs

- **Python 3.10+** and an `ANTHROPIC_API_KEY` in a `.env` file (see the main repo README).
- Every guided lab includes a **`MockLLM` warm-up that runs at $0** — no key needed to get started.
- Per-skill extras get installed as you go (e.g. `crewai`, `langgraph`, `neo4j`, `ragas`, `langsmith`, `claude-agent-sdk`, `mcp`). Each skill tells you what it needs.

---

## 💪 About

Built for **Agentic Coding Fitness @ Rust Tech Bar** (Bangkok) — every Tuesday, 18:00–20:00. Practice-first, ship-real-things. Share this with anyone catching up.

See [CHANGELOG.md](./CHANGELOG.md) for what's new in **v2.0.0** (9 → 16 skills).

MIT licensed. PRs welcome — add a skill for a week you loved.
