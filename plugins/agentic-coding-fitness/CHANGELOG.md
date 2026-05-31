# Changelog

All notable changes to the **Agentic Coding Fitness** plugin.
This project adheres to [Semantic Versioning](https://semver.org/).

## [2.0.0] — 2026-05-31

A major expansion driven by the *Agentic AI Fitness Class: Claude Code Plugin & Skill Strategy* blueprint. The plugin grows from a 9-skill course recap into a **16-skill curriculum-and-practice platform**, and every existing skill gains production-grade depth.

### Added — 7 new skills
- **production-and-observability** (W10) — take a prototype to production: *see it* (LangSmith tracing, OpenTelemetry `gen_ai.*` conventions), *stop it* (HITL `interrupt()` + durable `SqliteSaver` checkpointing, progressive autonomy, the OWASP-ASI 4-layer guardrail stack), *afford it* (budgets, cost-per-successful-task, CI cost-regression gate). Grounded in `week10/`.
- **agent-evaluation** (W10 & W15) — measure and **gate** agent quality: golden datasets, the eval-framework landscape (RAGAS/DeepEval/Braintrust/Inspect AI), LLM-as-judge with bias mitigation, and the 5-gate CI/CD pipeline (lint → eval → cost → canary → shadow). Grounded in `week15/kg_mastery/part4_evaluation/`.
- **agent-drills** — the practice menu: warm-up/skill/endurance/sparring/capstone katas, grounded in the 14 real `week11/exercises` (ex01–ex14) plus the flagship drills authored into the other skills.
- **curriculum-and-periodization** ⚠️ — the syllabus: four phases (Foundation → Strength → Endurance → Performance), progressive overload, deload weeks, and a map bridging the blueprint's idealized 16 weeks to this repo's real weeks 2–15.
- **vibe-coding-and-security** ⚠️ — working *with* a coding agent: context engineering (CLAUDE.md, six-layer framework, Preferred/Avoid pairs), test-driven vibe coding, the ~45% AI-code vulnerability reality + a self-review security loop, and a hand-off-vs-take-control decision tree.
- **a2a-protocol** ⚠️ — the Agent-to-Agent protocol (cross-framework counterpart to MCP): Agent Cards at `/.well-known/agent.json`, the six-state task lifecycle, polling/SSE/webhooks, and A2A vs MCP. Conceptual/stretch — not yet implemented in this repo.
- **skill-authoring** (W7+) — the meta-skill: the two skill types (Capability Uplift vs Encoded Preference), full frontmatter + progressive disclosure, the 7-step creation pipeline, and how to evaluate/maintain a skill. This plugin is the worked example.

### Changed — all 9 existing skills enriched
- **models-and-patterns** — reconciled the loose catalog into the canonical **12-pattern, 3-tier taxonomy** (Core/Workflow/Advanced), added a 12×4 framework-support matrix, a 5-question pattern-selection decision tree (with the compounding-error rationale), concrete **cost economics** (3-tier cascade, savings levers, break-even, cost-per-successful-task), and real **HITL + guardrails** coverage (progressive autonomy, OWASP-ASI stack, hand-off tree).
- **mcp-and-skills** — added *Capability Uplift vs Encoded Preference*, fuller SKILL.md anatomy + progressive disclosure, **building an MCP server** with FastMCP (grounded in `week15/.../05_fastmcp_server.py`), a one-screen **MCP security** awareness section, and **CLAUDE.md context engineering**.
- **multi-agent-systems** — expanded to a 6-pattern orchestration framework with a "which pattern?" decision table, **communication topologies + state management** (chain/star/mesh; shared/message-passing/event-driven/blackboard), and real `week10` supervisor/checkpointer/HITL code + Claude Agent SDK primitives.
- **agent-loops** — labelled the loop as **ReAct / Bounded Execution**, added Karpathy's 4 LLM failure modes for the reflection loop, and 5 deterministic token-budget guardrails ("denial of wallet" prevention).
- **rag-knowledge-agents** — its first runnable grounding: a **"how do I know my RAG is good?"** section built on `week15/kg_mastery/part4_evaluation/` (RAGAS metrics, golden testset, CI threshold gate).
- **llm-fundamentals, tool-use, agent-memory-graphs, knowledge-graph-mastery** — standardized guided labs into the **kata template** ($0 `MockLLM` warm-up + skill drill + weighted rubric + pass threshold), added cross-links to the new skills, the **Tool-Definition-Mastery** flagship drill (`tool-use`), a security caveat for model-written Cypher (`agent-memory-graphs`), and a prompt-caching cost note (`llm-fundamentals`).

### Versioning
- Bumped `plugin.json` and `.claude-plugin/marketplace.json` (top-level + nested) to **2.0.0**; refreshed descriptions (9 → 16 skills) and keywords. Skills are auto-discovered from `skills/*/SKILL.md`, so no skill list is hardcoded in the manifest.

## [1.1.0]
- 9 concept skills recapping the course: llm-fundamentals, tool-use, agent-loops, mcp-and-skills, rag-knowledge-agents, multi-agent-systems, agent-memory-graphs, knowledge-graph-mastery, models-and-patterns.
