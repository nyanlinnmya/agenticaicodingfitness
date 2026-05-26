---
name: agent-memory-graphs
description: "Teach durable agent memory using a Neo4j knowledge graph — how agents store decisions/observations as connected facts, recall them later, and answer natural-language questions via GraphRAG (NL → Cypher → answer). Covers event sourcing, the AgentMemory pattern, basic Cypher, and how shared graph memory coordinates a multi-agent system. Use when someone asks 'how do agents remember across runs?', mentions Neo4j/Cypher/knowledge graphs/GraphRAG, or is reviewing Week 14."
when_to_use: "Learner wants agents to remember across sessions, asks about Neo4j / Cypher / knowledge graphs / GraphRAG / event sourcing, or is catching up on Week 14."
---

# Agent Memory & Knowledge Graphs — Memory That Lasts (Week 14)

> **The one idea:** The `messages` list (Week 2) is *short-term* memory — it vanishes when the program ends. For agents that learn over days and coordinate with each other, you need **durable, structured memory**: a knowledge graph where every decision and observation is a connected, queryable fact.

```
Short-term (Week 2):  messages list   → gone when the script exits
Document memory (W8): vector store    → retrieve relevant TEXT
Graph memory (W14):   Neo4j graph     → store/recall structured FACTS + relationships
```

---

## Why a graph?

Agent knowledge is naturally *connected*: this **agent** PERFORMED this **event**, which INVOLVES this **room**, which HAS this **sensor**. A graph stores those relationships directly, so you can ask things a flat log can't easily answer:

- "Which rooms had more than 3 temperature overrides this month?" (predictive maintenance)
- "What did the HVAC agent decide about Room 301, and why?"
- "Which equipment shows up across the most fault events?"

Nodes = things (Agent, Event, Room, Equipment). Relationships = verbs (PERFORMED, INVOLVES). Both can carry properties.

---

## Event sourcing — every action becomes a fact

The core pattern: **don't overwrite state — append events.** Each decision/observation is a timestamped `Event` node linked to the agent and the things it touched. The full history is the memory.

```
(Agent {id})-[:PERFORMED]->(Event {type, data, ts})-[:INVOLVES]->(Room {name})
```

---

## The reusable `AgentMemory` class

A drop-in memory layer any agent can use — store, recall, and query:

```python
import json
from datetime import datetime
from neo4j import GraphDatabase
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain

class AgentMemory:
    def __init__(self, agent_id, uri="bolt://localhost:7687", auth=("neo4j", "password")):
        self.agent_id = agent_id
        self.uri, self.auth = uri, auth
        self.driver = GraphDatabase.driver(uri, auth=auth)
        with self.driver.session() as s:               # ensure this agent exists
            s.run("MERGE (a:Agent {id:$id}) ON CREATE SET a.created=datetime()", id=agent_id)

    def store_event(self, event_type, data, entities=None):
        """Append an event linked to this agent and any domain entities."""
        eid = f"{self.agent_id}:{datetime.now().isoformat()}"
        with self.driver.session() as s:
            s.run("MATCH (a:Agent {id:$aid}) "
                  "CREATE (e:Event {id:$eid, type:$t, data:$d, ts:datetime()}) "
                  "CREATE (a)-[:PERFORMED]->(e)",
                  aid=self.agent_id, eid=eid, t=event_type, d=json.dumps(data))
            for label, name in (entities or []):        # e.g. ("Room","301")
                s.run(f"MERGE (n:{label} {{name:$name}}) "
                      f"WITH n MATCH (e:Event {{id:$eid}}) MERGE (e)-[:INVOLVES]->(n)",
                      name=name, eid=eid)
        return eid

    def recall_recent(self, event_type=None, limit=5):
        """Most recent events for this agent, newest first."""
        q = ("MATCH (a:Agent {id:$aid})-[:PERFORMED]->(e:Event) "
             + ("WHERE e.type=$t " if event_type else "")
             + "RETURN e ORDER BY e.ts DESC LIMIT $lim")
        with self.driver.session() as s:
            return [dict(r["e"]) for r in s.run(q, aid=self.agent_id, t=event_type, lim=limit)]

    def close(self):
        self.driver.close()
```

Using it:

```python
mem = AgentMemory("hvac-monitor-01")
mem.store_event("FAULT_DETECTED",
                {"room": "301", "unit": "AHU-3", "severity": "high"},
                entities=[("Room", "Room 301"), ("Equipment", "AHU-3")])
mem.store_event("FAULT_RESOLVED",
                {"room": "301", "resolution": "capacitor replaced"},
                entities=[("Room", "Room 301"), ("Equipment", "AHU-3")])

for e in mem.recall_recent():
    print(e["type"], e["data"])
```

Run it tomorrow, next week — the facts are still there. That's durable memory.

> 📁 Class repo: `week14/agent_memory.py` (the full class), `week14/lab1_hotel_mas.py` (a 2-agent hotel crew that reads/writes this memory), `week14/lab1_hotel_memory.py`.

---

## A little Cypher (the graph query language)

Cypher is "SQL for graphs" — you draw the pattern you want with ASCII arrows.

```cypher
// Find all events involving Room 301
MATCH (e:Event)-[:INVOLVES]->(r:Room {name: "Room 301"})
RETURN e.type, e.data, e.ts
ORDER BY e.ts DESC

// Rooms with more than 3 HVAC override events (predictive maintenance signal)
MATCH (e:Event {type: "HVAC_OVERRIDE"})-[:INVOLVES]->(r:Room)
WITH r, count(e) AS overrides
WHERE overrides > 3
RETURN r.name, overrides ORDER BY overrides DESC
```

- `MATCH` = the pattern to find · `WHERE` = filter · `RETURN` = what to output · `MERGE` = create-if-absent (idempotent).

> 📁 Class repo: `week14/NEO4J_TUTORIAL.md` — full Cypher walkthrough with hotel scenarios.

---

## GraphRAG — ask the graph in plain English

You don't have to write Cypher by hand. **GraphRAG** lets an LLM translate a natural-language question into Cypher, run it, and phrase the answer:

```python
from langchain_anthropic import ChatAnthropic

def build_graphrag_chain(mem, llm):
    graph = Neo4jGraph(url=mem.uri, username=mem.auth[0], password=mem.auth[1])
    graph.refresh_schema()                       # show the LLM what's in the graph
    return GraphCypherQAChain.from_llm(llm, graph=graph, allow_dangerous_requests=True)

llm = ChatAnthropic(model="claude-haiku-4-5-20251001", max_tokens=512)
chain = build_graphrag_chain(mem, llm)
print(chain.invoke({"query": "What faults were detected in Room 301?"})["result"])
```

Under the hood: NL question → LLM writes Cypher → Neo4j runs it → LLM turns rows into a sentence. This is RAG (Week 8) but retrieving over a **graph** instead of a pile of text.

---

## Shared graph = multi-agent coordination
When several agents read and write the *same* graph, it becomes their shared world model. A sensor agent writes `TEMPERATURE_ALERT`; an optimizer agent reads it, decides, and writes `HVAC_SETPOINT_CHANGED`. No direct messaging needed — the graph is the blackboard. (This is the Week 14 hotel energy-optimization lab: 300 rooms, multiple agents, one graph.)

> 📁 Class repo: `week14/6.hotel_kg_builder.py` (builds the hotel graph), `week14/NEO4J_WEBAPP_INTEGRATION.md` (wiring a graph into a real backend).

---

## Quick start (run Neo4j locally)

```bash
docker run -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password neo4j:latest
pip install neo4j langchain-neo4j langchain-anthropic
# Browser UI at http://localhost:7474  ·  Bolt driver at bolt://localhost:7687
```

> 📁 Class repo: `week14/1.docker-compose.yml`, `week14/2.neo4j_connect.py`.

---

## 🧪 Guided lab (offer this)

Give an agent a memory it keeps:

1. **Start Neo4j** with the Docker command above; open the browser UI so they can *see* nodes appear.
2. **Store events.** Use `AgentMemory` to record 3–4 events (a fault, a work order, a resolution) with linked entities. Refresh the Neo4j browser and watch the graph grow visually — this is the moment it clicks.
3. **Recall.** Call `recall_recent()` and a "recall everything involving Room 301" query. Confirm the facts persisted.
4. **Restart the script.** Run a *fresh* process and recall again — the memory survived. Contrast with the Week-2 `messages` list that would have been empty.
5. **GraphRAG.** Wire up `build_graphrag_chain` and ask "what happened in Room 301?" in plain English. Have them peek at the Cypher it generated.
6. **Two agents, one graph.** Spin up a second `AgentMemory("sensor-01")` writing alerts; show the first agent can query events the second one wrote. That's coordination via shared memory.
7. **Stretch:** point them at `week14/lab1_hotel_mas.py` and the `multi-agent-systems` skill — combine a swarm with graph memory.

End by tying the whole course together: "Week 2 gave the model a sentence of memory; Week 14 gives a team of agents a memory that outlives them."
