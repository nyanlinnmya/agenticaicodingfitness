# 🏋️‍♂️ Agentic Coding Fitness @ Rust Tech Bar

Welcome to the repository for the **Agentic Coding Fitness** event series, hosted weekly at Rust Bar, Ban Tad Thong! 

This repository contains all the code, tools, and examples built during our hands-on "Vibe Coding" sessions. It serves as a living codebase demonstrating how to transition from basic AI API calls to building sophisticated, multi-agent systems and real-world IoT integrations.

**Event Details**: [Luma Event Page](https://lu.ma/jy6d10xq)
- **When**: Every Tuesday, 18:00 – 20:00
- **Where**: Rust Bar, Ban Tad Thong (Bangkok)

## 🤖 What is Agentic Coding Fitness?
Think of this as a "fitness center" for your coding brain—but instead of lifting weights, we are building AI muscle muscle memory. We focus on **Agentic AI**: moving beyond simple prompt-and-response mechanisms to build AI that can think, plan, decide, and collaborate using multi-agent systems.

We emphasize a **practice-first** approach (Vibe Coding). No long lectures, just shipping workable solutions that interact with the real world!

## 📚 Catching up? Install the Bootcamp Plugin

Missed a session or want to review at your own pace? We packaged the **entire course (weeks 2–18)** into a shareable **Claude Code plugin** — **20 bite-sized skills** (one per concept) that teach the idea, show runnable code (pointing at the real `weekN/` files here), and walk you through a hands-on **$0 lab** (a tiny `MockLLM`, or fully offline checkpoints, so you need no API key to start). Just ask Claude in plain English and the right skill loads automatically.

**Install** (run these in any Claude Code session):

```
/plugin marketplace add kwarodom/agenticaicodingfitness
/plugin install agentic-coding-fitness@agentic-coding-fitness
```

Then try: *"Recap the whole course and tell me which skill to start with."*

### 🔄 Already installed? Pull the latest version mid-session

We ship new skills as the course grows (we're on **v2.2.0 — 20 skills**). To grab the newest version **without restarting**, run these three in your current session:

```
/plugin marketplace update agentic-coding-fitness                 # 1. refresh the catalog from GitHub
/plugin install agentic-coding-fitness@agentic-coding-fitness     # 2. fetch the latest version
/reload-plugins                                                   # 3. activate the new skills now
```

> There's no separate `/plugin update` command — **reinstalling** pulls the latest version from the refreshed marketplace. Step 1's argument is the *marketplace name* (`agentic-coding-fitness`), not the GitHub repo.

**Prefer clicking?** Run `/plugin` for the interactive manager: **Marketplaces** tab → select *agentic-coding-fitness* → **Update**, then **Installed** tab → select the plugin → **Reinstall**, then `/reload-plugins`. (You can also toggle **Enable auto-update** on the marketplace so new versions are fetched at startup.)

Covers: LLM basics · tool use · agent loops (now incl. the Week 18 Claude Agent SDK production loop) · MCP & skills · RAG · multi-agent systems · production & observability · agent evaluation/CI · knowledge-graph memory · production GraphRAG · choosing models & patterns · the NVIDIA NeMo Agent Toolkit · long-running & distributed agents (Google ADK durable sessions, pause/resume, auth.md, A2A fleets) · self-evolving agents (tripartite memory + consolidation) · sovereign AI at the edge (local/$0 inference) · sovereign & self-evolving AI on an NVIDIA DGX (serve/fine-tune/observe/gateway) · vibe-coding & security · the A2A protocol · skill-authoring. See [`plugins/agentic-coding-fitness/`](plugins/agentic-coding-fitness/) for details.

## 📂 Repository Contents 

The project is structured week-by-week as our complexity scales up — from a single API call to long-running distributed fleets, self-evolving memory, and sovereign agents running entirely on hardware you own. Each week maps to a plugin skill (above) that recaps it with a $0 lab.

### Phase ① Foundation — talk → tools → agents

#### 🔹 Week 2: Claude API Foundations
Talking to modern LLMs programmatically. → skill `llm-fundamentals`
- `week2/claudeapicall.py`: basic single-turn API requests · `week2/claudestreamingapi.py`: streaming tokens · `week2/claudemulti_turn.py`: conversational state & history · `week2/lab/`: $0 practice drills.

#### 🔹 Week 3: Tool Use & Smart Assistants
Teaching agents to call external services (function calling). → skill `tool-use`
- `week3/toolsuse.py`: function calling (weather, calculator, web search) · `week3/buildsmartassistant3tools.py`: a full assistant · **Tapo Smart Plug Integration** (`check_tapo.py`, `scan.py`, `tapo_config.json`): a local HTTP wrapper so Claude controls TP-Link Tapo L530 lights.

#### 🔹 Week 4: Autonomous Pipelines & Hardware
Chaining actions and reaching into physical IoT. → skill `agent-loops`
- `week4/pipeline.py`: an autonomous research pipeline (web search → multi-agent synthesis → self-scoring → Markdown reports, with NotebookLM export) · `week4/dronecontrol.py`: flight patterns on a DJI Tello drone (`djitellopy`) · `week4/openrouterfreemodel.py`: a free-model gateway.

#### 🔹 Week 5: The Agent Loop
The reusable REASON → ACT → OBSERVE loop that turns a tool-user into an agent. → skill `agent-loops`
- `week5/autoagent.py`: the reusable bounded `Agent` class (ReAct + stop conditions).

### Phase ② Strength — single-agent mastery, reusable tools & knowledge

#### 🔹 Week 6: Full-Stack Agent App (deload / integration)
An agent put behind a real API. → skill `vibe-coding-and-security`
- `week6/src/` (Express/TypeScript/Postgres) · `week6/CLAUDE.md` + `AGENTS.md`: context engineering in practice.

#### 🔹 Week 7: MCP & Skills
Reusable tools (MCP) and reusable know-how (Skills). → skill `mcp-and-skills`
- `week7/mcpserver.py`, `week7/mcpfilesystem.py`: MCP servers · `week7/agent.py`, `week7/agenttooldt.py`: an MCP client agent · `week7/skill.md`: a worked Skill.

#### 🔹 Week 8: RAG — Knowledge Agents
Ground answers in your own documents (and prove it with RAGAS). → skill `rag-knowledge-agents`
- `week8/Week8_RAG_Knowledge_Agents_Lab.pdf`: the RAG lab.

### Phase ③ Endurance — systems that run reliably

#### 🔹 Week 9: Multi-Agent Systems
Sequential / router / parallel-swarm orchestration across frameworks. → skill `multi-agent-systems`
- `week9/ex1_crewai_sequential.py` (CrewAI) · `week9/ex2_LangGraphSupportGraph.py` (LangGraph router) · `week9/ex3_ParallelSwarm.py` (asyncio swarm) · plus AG2/Anthropic comparisons and 3 workshop PDFs.

#### 🔹 Week 10: Production & Observability
Make a prototype something you can *see, stop, and afford*. → skills `production-and-observability`, `agent-evaluation`
- `week10/notebooks/01_hello_graph.py` → `05_hybrid_sdk.py`: a support-routing system gaining a supervisor, `SqliteSaver` checkpointing + HITL `interrupt()`, LangSmith tracing, then a Claude Agent SDK hybrid · `week10/GUIDE.md`, `solutions/`.

#### 🔹 Week 11: Mastery — Models & Patterns
Pick the right model, framework, and pattern; the 12-pattern taxonomy. → skills `models-and-patterns`, `agent-drills`
- `week11/index.html`: model wizard + pattern playground + quiz · `week11/exercises/`: **14 graded MAS drills** (ex01–ex14, Beginner → Expert).

### Phase ④ Performance — memory, GraphRAG, production frameworks, fleets

#### 🔹 Week 14: Agent Memory with Knowledge Graphs
Durable memory agents remember across runs (Neo4j + GraphRAG). → skill `agent-memory-graphs`
- `week14/agent_memory.py`, `week14/hotel_kg_builder.py`, `week14/lab1_hotel_mas.py` · `week14/NEO4J_TUTORIAL.md` · `week14/pi-structured-extraction/`: a structured-extraction sub-project.

#### 🔹 Week 15: Production GraphRAG
Cypher + GDS, ingestion, GraphRAG across 7 frameworks, and **evaluating** it. → skills `knowledge-graph-mastery`, `agent-evaluation`
- `week15/kg_mastery/`: the 6-part code companion (fundamentals → building → GraphRAG → evaluation/RAGAS+CI → use cases → reference) · `week15/smart_hotel_mas/`: a 5-agent CrewAI system over a 4-layer memory stack.

#### 🔹 Week 16: Production Frameworks — NVIDIA NeMo Agent Toolkit
Config-driven multi-agent: register tools, compose YAML workflows, observe. → skill `nemo-agent-toolkit`
- `week16/adding_tools_to_agents.ipynb`: tool registration + LlamaIndex RAG tool · `week16/multi_agent_orchestration.ipynb`: supervisor → specialists with HITL.

#### 🔹 Week 17: Long-Running & Distributed Agents (Google ADK + A2A)
Agents that **pause for days and resume without losing context**, and delegate across services. → skills `long-running-and-distributed-agents`, `a2a-protocol`
- `week17/checkpoints/checkpoint1_state_machine.py` → `checkpoint6_fleet.py`: 6 offline steps (durable state → restart-survival → webhook resume → sub-agents → A2A cards → fleet capstone) · `week17/hr_onboarding/`: a live ADK onboarding agent · `week17/authmd_adk/`: **auth.md** × ADK — store the durable grant, re-mint a scoped token at every wake.

### Phase ⑤ Sovereignty & Self-Improvement — the stack you own, that gets better

#### 🔹 Week 18: Production Loops, Self-Evolving Memory & Sovereign Edge AI
Three interactive web apps + runnable demos that take the agent stack to production, make it *learn*, and take it *off the cloud*. → skills `agent-loops` (extended), `self-evolving-agents`, `sovereign-ai-edge`
- **`week18/agent_loop/`** — the loop as a *production* discipline via the **Claude Agent SDK**: built-in & custom tools, PreToolUse/PostToolUse safety hooks, resumable sessions, subagent orchestration, and `max_turns`/`max_budget_usd` caps. A clickable streaming web app (`tutorial_server.py`, port 8090) + 9 demos (`step01_hello_agent` → `step09_production`). Uses your `claude` CLI sign-in — **no API key**.
- **`week18/self_evolving_agent/`** — turn a *stateless* agent into one that **remembers, learns, and gets cheaper** via the **Tripartite Memory Model** (episodic `SessionDB` + semantic `MEMORY.md`/`USER.md` + procedural `SKILL.md` library) and a background **consolidation** loop → compound returns (~64% fewer turns / ~66% lower cost by run 5). Live visualizer (port 8088) + step-by-step guide (port 8090); 7 checkpoints (1–6 offline, $0).
- **`week18/sovereign_ai_edge/`** — run the **whole stack on hardware you own** with zero cloud dependency and **$0 per token**: local OpenAI-compatible inference (Ollama), RAM-based hardware sizing, quantization math, LoRA/NeMo fine-tuning, on-device tool-calling agents, a Smart-Hotel HVAC demo, and a live air-gap **sovereignty audit**. Web app on port 8091 + 9 demos.
- Comprehensive write-ups per folder (`README.md`/`TUTORIAL.md`) plus tutorial PDFs: `agent_loop_comprehensive_tutorial.pdf`, `self_evolving_agent_tutorial.pdf`, `sovereign_ai_edge_tutorial.pdf`.

#### 🔹 Week 19: Sovereign & Self-Evolving AI on a DGX
Five interactive web apps that take the whole stack onto an **NVIDIA DGX** — run/serve, fine-tune, observe, self-evolve, and gateway — grounded in NVIDIA's [`dgx-spark-playbooks`](https://github.com/NVIDIA/dgx-spark-playbooks). Every app runs **REAL** (a live Ollama/vLLM/DGX endpoint) or **SIM** (a faithful simulator — no GPU needed); cloud cost always **$0**.
- 👉 **Start here: the step-by-step walkthrough → [`week19/README.md`](week19/README.md)** — walks you through all five apps in order, chapter by chapter.
- **`week19/sovereign_dgx/`** (port 8092) — run + serve + manage models on a DGX: **Ollama, vLLM, llama.cpp**, TensorRT-LLM, NVFP4 quantization, multi-Spark scale-out, air-gap audit.
- **`week19/dgx_finetune/`** (port 8093) — adapt a model to **your domain**: LoRA/QLoRA with **NeMo AutoModel** + **Unsloth**, dataset prep, training loop, eval, GGUF/NVFP4 export.
- **`week19/dgx_observability/`** (port 8094) — **see, measure, judge** a sovereign agent: OpenTelemetry tracing → **Arize Phoenix**, metrics, LLM-as-judge evals, + a **NeMo Agent Toolkit** workflow.
- **`week19/self_evolving_agent_v2/`** (port 8095) — the Week 18 self-evolving agent, made sovereign: a **switchable brain** (DGX ↔ Claude) + tripartite **memory on the DGX** that learns over time.
- **`week19/dgx_litellm/`** (port 8096) — the **serving gateway**: one OpenAI URL over all backends with **LiteLLM** — routing, fallbacks, hot-swap, virtual keys/budgets, logging → Phoenix.

---

## 🛠️ Getting Started

### 1. Requirements
Ensure you have **Python 3.10+** installed on your machine.

Clone the repository and set up a virtual environment:
```bash
git clone https://github.com/your-username/AgenticCoding.git
cd AgenticCoding
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
To authenticate with the models, create a `.env` file in the root directory:
```ini
ANTHROPIC_API_KEY="sk-ant-api03-YourAnthropicKeyHere..."
```

### 4. Hardware Configuration (Optional)
- **Tapo Lights**: Edit `tapo_config.json` with your TP-Link account credentials and local IP address of your light bulb. 
- **Tello Drone**: Connect your computer directly to the Tello's Wi-Fi network before running `week4/dronecontrol.py`.

---

## 🎯 Who is this for?
- **Developers & Programmers** looking to elevate their workflow with AI.
- **Tech, Startup, and Product Innovators**.
- Anyone with basic coding knowledge ready to embrace the future of **AI-native, Agent-based development**.

## 🌟 Our Goal 
- Build **Real Stuff**
- Solve **Real Problems**
- Generate **Real Impact**

Come join us every Tuesday, stretch those brain muscles, and let's craft the future of Agentic AI together! 💪🤖
