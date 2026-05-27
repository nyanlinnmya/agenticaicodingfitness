# 🏋️ Agentic Coding Fitness — Bootcamp Plugin

A Claude Code plugin that recaps **everything we built in class** — for anyone who couldn't keep up on the day, or wants to review at their own pace.

It's 9 bite-sized **skills**, one per big concept. Each skill:
- **Teaches** the idea in plain language (no jargon walls),
- **Shows runnable example code** (with pointers to the real `weekN/` files in this repo),
- **Offers an interactive guided lab** — just ask, and Claude walks you through building it yourself, step by step.

You don't read these like a book. You *talk to Claude* and the right skill loads automatically when your question matches.

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
| "What's MCP? How do skills/plugins work?" | `mcp-and-skills` |
| "How do I make it answer from my PDFs?" | `rag-knowledge-agents` |
| "How do I make agents work together?" | `multi-agent-systems` |
| "How do agents remember across runs?" | `agent-memory-graphs` |
| "GDS / PageRank / Text2Cypher / how do I *evaluate* GraphRAG?" | `knowledge-graph-mastery` |
| "Which model/framework should I use?" | `models-and-patterns` |

Or ask for a lab directly: *"Give me the guided lab for tool use."*

**Don't know where to start?** Ask: *"Recap the whole course and tell me which skill to begin with."* → `models-and-patterns` has the one-page map of all 14 weeks.

---

## 🗺️ The 9 skills (by concept)

| # | Skill | Concept | Class weeks |
|---|---|---|---|
| 1 | **llm-fundamentals** | Talking to an LLM: messages, streaming, memory, tokens | W2 |
| 2 | **tool-use** | Function calling — giving the model hands | W3 |
| 3 | **agent-loops** | REASON→ACT→OBSERVE; the reusable Agent class; pipelines | W4–W5 |
| 4 | **mcp-and-skills** | MCP servers (reusable tools) + Skills (reusable know-how) | W7 |
| 5 | **rag-knowledge-agents** | RAG: ground answers in your own documents | W8 |
| 6 | **multi-agent-systems** | Sequential, parallel swarm, router; CrewAI/LangGraph/AutoGen | W9 |
| 7 | **agent-memory-graphs** | Durable memory with Neo4j; GraphRAG; event sourcing | W14 |
| 8 | **knowledge-graph-mastery** | Production GraphRAG: Cypher+GDS, ingestion, 7 frameworks, RAGAS evaluation | W15 |
| 9 | **models-and-patterns** | Choosing models/frameworks; pattern catalog; course map | W11 |

> The examples reference the real code in this repo's `week2/ … week15/` folders (Week 15's deep dive lives in `week15/kg_mastery/`). Clone the repo alongside installing the plugin to run them directly.

---

## 🎯 Suggested learning paths

- **Total beginner:** 1 → 2 → 3 → then pick what interests you.
- **"I can call the API, what's next?":** 2 → 3 → 4.
- **"I want agents that collaborate":** 3 → 6 → 7.
- **"I want it to use my data":** 5 → 7 → 8.
- **"I want production GraphRAG I can trust":** 7 → 8 (build, query with algorithms, then *evaluate* with RAGAS).
- **"Just give me the big picture":** 9 (start here, it maps everything).

---

## 🛠️ Requirements for the labs

- **Python 3.10+** and an `ANTHROPIC_API_KEY` in a `.env` file (see the main repo README).
- Per-skill extras get installed as you go (e.g. `crewai`, `langgraph`, `neo4j`, `claude-agent-sdk`). Each skill tells you what it needs.

---

## 💪 About

Built for **Agentic Coding Fitness @ Rust Tech Bar** (Bangkok) — every Tuesday, 18:00–20:00. Practice-first, ship-real-things. Share this with anyone catching up.

MIT licensed. PRs welcome — add a skill for a week you loved.
