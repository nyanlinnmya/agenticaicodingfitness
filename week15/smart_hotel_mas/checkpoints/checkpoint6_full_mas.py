#!/usr/bin/env python3
"""CHECKPOINT 6 — Full MAS + GraphRAG Demo.

Goal: tie all four layers together — Sensing, Energy (RL), Memory (the KG), and
Reporting — into one CrewAI multi-agent system whose shared long-term memory
*is* the Neo4j knowledge graph (L4). A GraphRAG tool lets agents query that
graph in natural language, so the report agent can reason over everything the
other agents just did.

  Part 1 — KG memory classes (L4). Importable WITHOUT crewai installed, so other
           modules can reuse HotelKGMemory on its own.
  Part 2 — the 5-agent CrewAI crew. crewai imports are kept lazy (inside the
           function) so importing Part 1 never requires crewai.

(smart_hotel_mas.pdf §CP6)

Run:  python week15/smart_hotel_mas/checkpoints/checkpoint6_full_mas.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # import config.py
from config import check_neo4j, get_driver, MODEL


# ════════════════════════════════════════════════════════════════════════════
# Part 1 — KG memory (L4).  Importable without crewai.
# ════════════════════════════════════════════════════════════════════════════
class AgentMemoryBase:
    """Thin Neo4j-backed memory base: store events, recall recent events."""

    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.driver = get_driver()

    def cypher(self, query, **params) -> list:
        with self.driver.session() as session:
            result = session.run(query, **params)
            return [dict(r) for r in result]

    def store_event(self, event_type, data: dict, entities: list = None):
        """Append an Event node tagged with this agent's id (entities reserved
        for richer linking by subclasses)."""
        self.cypher(
            """
            CREATE (e:Event {type: $etype, agent_id: $aid, data: $data, ts: datetime()})
            """,
            etype=event_type,
            aid=self.agent_id,
            data=json.dumps(data),
        )

    def recall_recent(self, hours=8, limit=20) -> list:
        return self.cypher(
            """
            MATCH (e:Event)
            WHERE e.agent_id = $aid AND e.ts > datetime() - duration({hours: $h})
            RETURN e.type AS type, e.data AS data, toString(e.ts) AS ts
            ORDER BY e.ts DESC
            LIMIT $limit
            """,
            aid=self.agent_id,
            h=hours,
            limit=limit,
        )

    def close(self):
        self.driver.close()


class HotelKGMemory(AgentMemoryBase):
    """Hotel-specific L4 memory: sensor batches, HVAC actions, alerts and the
    GraphRAG-style summary queries the agents call as tools."""

    def store_sensor_batch(self, room_id, reading, anomaly):
        self.store_event(
            "sensor_reading",
            {"room": room_id, "reading": reading, "anomaly": anomaly},
            entities=[("Room", room_id), ("Device", f"SENSOR_{room_id}")],
        )
        if anomaly:
            self.cypher(
                """
                MERGE (r:Room {id: $rid})
                CREATE (a:Alert {type: 'SENSOR_ANOMALY', severity: 'HIGH',
                                 ts: datetime(), data: $data})
                CREATE (r)<-[:AFFECTS]-(a)
                """,
                rid=room_id,
                data=json.dumps(reading),
            )

    def store_hvac_action(self, room_id, setpoint, energy_saved_kwh):
        self.store_event(
            "hvac_optimization",
            {"room": room_id, "setpoint": setpoint, "energy_saved_kwh": energy_saved_kwh},
            entities=[("Room", room_id), ("Device", f"HVAC_{room_id}")],
        )

    def query_floor_summary(self, floor) -> list:
        return self.cypher(
            """
            MATCH (r:Room)-[:HAS_DEVICE]->(d:Device {type: 'SENSOR'})
                  -[:RECORDED]->(sr:SensorReading)
            WHERE r.floor = $floor
              AND sr.ts > datetime() - duration({hours: 1})
            RETURN r.id AS room,
                   avg(sr.temp_c) AS avg_temp,
                   avg(sr.kwh)    AS avg_kwh,
                   count(sr)      AS readings
            ORDER BY avg_kwh DESC
            """,
            floor=floor,
        )

    def query_active_alerts(self) -> list:
        return self.cypher(
            """
            MATCH (a:Alert)-[:AFFECTS]->(r:Room)
            WHERE a.ts > datetime() - duration({hours: 4})
            RETURN r.id AS room,
                   a.type AS alert_type,
                   a.severity AS severity,
                   toString(a.ts) AS ts
            ORDER BY a.ts DESC
            LIMIT 10
            """
        )


# ════════════════════════════════════════════════════════════════════════════
# Part 2 — full 5-agent CrewAI crew.  crewai imports are LAZY (inside here).
# ════════════════════════════════════════════════════════════════════════════
def build_crew():
    """Build the 5-agent hotel crew. crewai imports happen here so Part 1 stays
    import-light."""
    try:
        from crewai import Agent, Crew, Process, Task
    except ImportError:
        print("Part 2 needs crewai. Install it with:")
        print("    pip install crewai")
        sys.exit(1)
    try:
        from crewai_tools import BaseTool
    except ImportError:
        print("Part 2 needs crewai-tools. Install it with:")
        print("    pip install crewai-tools")
        sys.exit(1)

    import random
    from random import gauss

    # Shared L4 memory: every tool writes to / reads from the same KG.
    kg_mem = HotelKGMemory("HotelMAS")

    class SensorReadTool(BaseTool):
        name: str = "read_sensors"
        description: str = "Read current sensor values for a comma-separated list of room ids."

        def _run(self, room_ids: str) -> str:
            rooms = [r.strip() for r in room_ids.split(",") if r.strip()]
            out = {}
            for rid in rooms:
                out[rid] = {
                    "temp_c": round(20 + gauss(4, 2), 1),
                    "humidity": round(50 + gauss(5, 3), 1),
                    "kwh": round(1.5 + random.random() * 2, 2),
                    "occupancy": random.random() > 0.4,
                }
            return json.dumps(out)

    class OptimizeTool(BaseTool):
        name: str = "optimize_hvac"
        description: str = "Compute optimized HVAC setpoints for a comma-separated list of room ids."

        def _run(self, room_ids: str) -> str:
            rooms = [r.strip() for r in room_ids.split(",") if r.strip()]
            out = {}
            for rid in rooms:
                setpoint = round(20 + random.random() * 6, 1)
                out[rid] = setpoint
                kg_mem.store_hvac_action(rid, setpoint, energy_saved_kwh=round(random.random(), 2))
            return json.dumps(out)

    class GraphRAGTool(BaseTool):
        name: str = "query_knowledge_graph"
        description: str = (
            "Query the hotel knowledge graph in natural language. Mention "
            "'alert', 'floor <n>', or anything else for recent activity."
        )

        def _run(self, query: str) -> str:
            q = query.lower()
            if "alert" in q:
                rows = kg_mem.query_active_alerts()
            elif "floor" in q:
                floor = 3
                for tok in q.replace("floor", " ").split():
                    if tok.isdigit():
                        floor = int(tok)
                        break
                rows = kg_mem.query_floor_summary(floor)
            else:
                rows = kg_mem.recall_recent(limit=10)
            return json.dumps(rows, default=str)[:500]

    sensor_tool = SensorReadTool()
    optimize_tool = OptimizeTool()
    graphrag_tool = GraphRAGTool()

    llm = f"anthropic/{MODEL}"

    sensor_agent = Agent(
        role="Hotel Sensor Monitor",
        goal="Read live sensor data for the requested rooms and surface anything unusual.",
        backstory="You watch every room's temperature, humidity, occupancy and energy draw.",
        tools=[sensor_tool],
        llm=llm,
        verbose=False,
    )
    energy_agent = Agent(
        role="Energy Optimization Engineer",
        goal="Set HVAC setpoints that keep guests comfortable while cutting energy use.",
        backstory="You trade comfort against kWh and apply the optimized setpoints.",
        tools=[optimize_tool],
        llm=llm,
        verbose=False,
    )
    memory_agent = Agent(
        role="Hotel Memory Manager",
        goal="Query the knowledge graph to recall what the hotel agents have done recently.",
        backstory="You are the institutional memory, answering questions from the graph.",
        tools=[graphrag_tool],
        llm=llm,
        verbose=False,
    )
    alert_agent = Agent(
        role="Hotel Alert Coordinator",
        goal="Surface and prioritise active alerts across the building.",
        backstory="You triage anomalies and make sure nothing urgent is missed.",
        tools=[graphrag_tool],
        llm=llm,
        verbose=False,
    )
    report_agent = Agent(
        role="Hotel Intelligence Reporter",
        goal="Write a concise operations report from the knowledge graph.",
        backstory="You turn raw graph data into a clear two-paragraph briefing for managers.",
        tools=[graphrag_tool],
        llm=llm,
        verbose=False,
    )

    t1 = Task(
        description="Read the current sensors for rooms R101, R102, R201, R202.",
        expected_output="A JSON map of each room's temp, humidity, occupancy and kWh.",
        agent=sensor_agent,
    )
    t2 = Task(
        description="Optimize HVAC setpoints for rooms R101, R102, R201, R202.",
        expected_output="A JSON map of each room's recommended setpoint in °C.",
        agent=energy_agent,
    )
    t3 = Task(
        description="Query the knowledge graph for active alerts and recent HVAC optimizations.",
        expected_output="A short summary of alerts and optimization events from the graph.",
        agent=memory_agent,
    )
    t4 = Task(
        description="Write a two-paragraph hotel operations report using the knowledge graph.",
        expected_output="A two-paragraph operations report covering sensors, energy and alerts.",
        agent=report_agent,
    )

    crew = Crew(
        agents=[sensor_agent, energy_agent, memory_agent, alert_agent, report_agent],
        tasks=[t1, t2, t3, t4],
        process=Process.sequential,
        verbose=False,
    )
    return crew, kg_mem


if __name__ == "__main__":
    import os

    if not check_neo4j():
        sys.exit(1)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY is not set. Export it and re-run:")
        print("    export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    print("── CHECKPOINT 6: Full MAS + GraphRAG ──")
    crew, kg_mem = build_crew()
    result = crew.kickoff()
    print("\n── Crew result ──")
    print(result)
    kg_mem.close()

    # ── Key Insight ─────────────────────────────────────────────────────────
    # With all four memory layers working together — L1 (in-process dict) for
    # the current task, L2 (SQLite) for the episodic event log, L3 (Chroma) for
    # semantic recall, and L4 (Neo4j) for the relationship graph the agents
    # query via GraphRAG — the crew has complete situational awareness: every
    # agent can see what every other agent just did, and reason over it.
