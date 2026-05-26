---
name: multi-agent-systems
description: "Teach multi-agent systems (MAS) — coordinating several specialized agents instead of one do-everything agent. Covers the core coordination patterns (sequential pipeline, parallel swarm, router/dispatcher, hierarchical), the major frameworks (CrewAI, LangGraph, AutoGen, Anthropic SDK), and when MAS beats a single agent. Use when someone asks 'how do I make agents work together?', mentions CrewAI/LangGraph/AutoGen/swarms, or is reviewing Week 9."
when_to_use: "Learner wants multiple agents collaborating, asks about CrewAI / LangGraph / AutoGen / swarms / orchestration patterns, or is catching up on Week 9."
---

# Multi-Agent Systems — Many Specialists, One Goal (Week 9)

> **The one idea:** Instead of one agent juggling everything, use a *team* of focused agents — each with a narrow role — and a coordination pattern that decides who does what, when. A researcher + writer + editor beats one agent told to "research, write, and edit."

**Why bother?** Specialization (sharper prompts per role), parallelism (speed), modularity (swap one agent without breaking others), and separation of concerns.

---

## The four coordination patterns (this is the real lesson)

### 1. Sequential pipeline — assembly line
Agent A's output feeds Agent B feeds Agent C. Order is fixed.
**Use for:** workflows with clear stages (research → write → edit).

### 2. Parallel swarm — fan-out, then aggregate
Many agents work *at the same time* on independent sub-tasks; an aggregator merges results.
**Use for:** independent analyses (audit a building from 5 angles at once). ~3–5× faster than sequential.

### 3. Router / dispatcher — triage desk
One classifier agent inspects the input and routes it to the right specialist.
**Use for:** mixed inputs (support tickets → billing vs. technical vs. general).

### 4. Hierarchical — manager + workers
A manager agent plans and delegates sub-tasks to workers, then assembles their results.
**Use for:** complex goals that need decomposition.

```
Sequential:  A → B → C
Parallel:    A ┐
             B ┼→ aggregate
             C ┘
Router:      classify → (billing | technical | general)
Hierarchical: manager → [worker, worker, worker] → manager
```

---

## Pattern 1 in CrewAI — sequential crew

CrewAI models a team as **Agents** (role + goal + backstory) and **Tasks**, run by a **Crew** with a process.

```python
from crewai import Agent, Task, Crew, Process, LLM

llm = LLM(model="openai/glm-5", base_url="https://api.z.ai/api/paas/v4/", api_key=...)

researcher = Agent(role="Senior Research Analyst",
                   goal="Find the latest trends in building energy optimization",
                   backstory="Expert energy analyst tracking IoT + AI HVAC.",
                   llm=llm, tools=[search_tool], allow_delegation=False)
writer = Agent(role="Technical Content Writer",
               goal="Write an engaging blog post from the research",
               backstory="Writes for the engineering blog.", llm=llm)
editor = Agent(role="Chief Editor",
               goal="Polish for clarity, accuracy, brand voice",
               backstory="Senior editor.", llm=llm)

research_task = Task(description="Research AI-driven building energy trends...",
                     expected_output="5 findings with sources", agent=researcher)
writing_task  = Task(description="Write a 600-word post from the brief...",
                     expected_output="A 600-word markdown post", agent=writer)
editing_task  = Task(description="Review and polish...",
                     expected_output="Publication-ready post", agent=editor,
                     output_file="post.md")

crew = Crew(agents=[researcher, writer, editor],
            tasks=[research_task, writing_task, editing_task],
            process=Process.sequential, verbose=True)
print(crew.kickoff())
```

The **role + goal + backstory** is just a well-structured system prompt per agent. Output of each task flows into the next.

> 📁 Class repo: `week9/ex1_crewai_sequential.py`

---

## Pattern 3 in LangGraph — router as a state machine

LangGraph models the system as a **graph**: nodes are steps, a shared **state** flows through, and **conditional edges** pick the path.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class TicketState(TypedDict):
    ticket_text: str
    category: str
    response: str

def classify(state):          # router node → sets state["category"]
    ...  # ask the LLM: billing / technical / general
    return {"category": category}

def billing_agent(state):   ...   # specialist nodes
def technical_agent(state): ...
def general_agent(state):   ...

g = StateGraph(TicketState)
g.add_node("classify", classify)
g.add_node("billing", billing_agent)
g.add_node("technical", technical_agent)
g.add_node("general", general_agent)
g.set_entry_point("classify")
g.add_conditional_edges("classify", lambda s: s["category"],
    {"billing": "billing", "technical": "technical", "general": "general"})
for n in ["billing", "technical", "general"]:
    g.add_edge(n, END)
app = g.compile()

app.invoke({"ticket_text": "I don't recognize a charge on my invoice."})
```

This is centralized planning / BDI-style deliberation: decide **what** (classify) then **how** (route to specialist).

> 📁 Class repo: `week9/ex2_LangGraphSupportGraph.py`

---

## Pattern 2 — parallel swarm with asyncio

No framework needed — just `asyncio.gather` to fan out and aggregate. Five specialists audit a building concurrently:

```python
import asyncio, anthropic
client = anthropic.AsyncAnthropic()
MODEL = "claude-haiku-4-5-20251001"

SPECIALISTS = {
    "energy":      "Energy Efficiency Auditor",
    "comfort":     "Occupant Comfort Analyst",
    "maintenance": "Predictive Maintenance Engineer",
    "safety":      "Safety Compliance Officer",
    "cost":        "Cost Optimization Analyst",
}

async def run_specialist(name, role):
    resp = await client.messages.create(
        model=MODEL, max_tokens=300,
        system=f"You are a {role}. Give a concise 3-bullet audit finding.",
        messages=[{"role": "user", "content": "Audit a 50-floor Bangkok office tower."}])
    return name, resp.content[0].text

async def run_audit():
    results = await asyncio.gather(*(run_specialist(n, r) for n, r in SPECIALISTS.items()))
    for name, finding in results:
        print(f"--- {name} ---\n{finding}\n")

asyncio.run(run_audit())   # all 5 finish in ~the time of the slowest, not the sum
```

This is **distributed sensing + stigmergy**: agents work independently and write to shared results; an aggregator synthesizes.

> 📁 Class repo: `week9/ex3_ParallelSwarm.py`

---

## Framework cheat-sheet

| Framework | Best at | Mental model |
|---|---|---|
| **CrewAI** | Role-based teams, sequential/parallel crews | Agents + Tasks + Crew |
| **LangGraph** | Stateful graphs, routing, cycles, control flow | Nodes + shared state + edges |
| **AutoGen / AG2** | Conversational agents talking to each other | Chat between agents |
| **Anthropic SDK + asyncio** | Full control, custom orchestration, swarms | You write the loop |

There's no "best" — pick by the shape of your problem. Stuck choosing? See the `models-and-patterns` skill.

> 📁 Class workshop PDFs: `week9/week9_2_multi_agent_theory_workshop.pdf` (BDI, FIPA, coordination theory), `week9/week9_3_mas_coding_exercises.pdf`.

---

## Single agent vs. multi-agent — don't over-build
✅ **Go MAS** when sub-tasks are genuinely distinct, parallelizable, or need different expertise.
❌ **Stay single-agent** when one focused agent with a few tools already does the job — MAS adds latency, cost, and coordination bugs. Most problems don't need a swarm.

---

## 🧪 Guided lab (offer this)

Build the *same* small problem three ways so the patterns become muscle memory:

1. **Pick a task** with natural stages, e.g. "turn a topic into a polished tweet" (research → draft → punch-up).
2. **Sequential (CrewAI):** build the 3-agent crew. Watch each agent's output feed the next.
3. **Parallel (asyncio):** have 3 agents draft 3 *different* tweet styles at once with `asyncio.gather`, then a 4th picks the best. Time it vs. sequential — show the speedup.
4. **Router (LangGraph):** add a classifier that reads an incoming request and routes "make a tweet" vs. "make a blog" vs. "make a reply" to the right specialist.
5. **Reflect:** for *their* real project, which pattern fits? Could a single agent have done it? (Resist over-engineering.)
6. **Stretch:** give the swarm shared memory so agents see each other's output — natural bridge to the `agent-memory-graphs` skill.

End on the judgment call: "the pattern is the design decision — frameworks are just how you spell it."
