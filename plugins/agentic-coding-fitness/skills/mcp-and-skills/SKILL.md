---
name: mcp-and-skills
description: "Teach the Model Context Protocol (MCP) and Claude Code Skills — the standard, reusable ways to give agents tools and know-how without re-coding them every time. Covers what MCP is, connecting MCP servers via the Claude Agent SDK, the filesystem server, and how a SKILL.md packages repeatable expertise. Use when someone asks 'what is MCP?', wants to connect external tools/servers, asks how skills/plugins work, or is reviewing Week 7."
when_to_use: "Learner asks about MCP, wants to connect an external tool server, asks how Claude Code skills/plugins work, or is catching up on Week 7."
---

# MCP & Skills — Reusable Tools and Know-How (Week 7)

> **The one idea:** Hand-coding tools for every project (Week 3) doesn't scale. **MCP** is a universal plug for *tools* — write a tool server once, any agent can use it. **Skills** are a universal plug for *know-how* — write a `SKILL.md` once, the model loads that expertise on demand. (The very plugin you're reading is built from skills.)

---

## Part A — MCP (Model Context Protocol)

### What it is
MCP is an open standard (think "USB-C for AI tools"). Instead of writing `get_weather`, `search_web`, `read_db` inside every app, you connect to an **MCP server** that already exposes those tools. The model can then call any tool the server offers — files, databases, Slack, GitHub, your company's API, etc.

```
Your agent ──MCP──▶ filesystem server   (read/write files)
            ──MCP──▶ docs server         (search documentation)
            ──MCP──▶ database server      (query rows)
```

One protocol, many servers, zero custom glue per tool.

### Connecting an MCP server with the Claude Agent SDK

```python
import asyncio
from dotenv import load_dotenv
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
load_dotenv()

async def main():
    options = ClaudeAgentOptions(
        mcp_servers={
            "claude-code-docs": {
                "type": "http",
                "url": "https://code.claude.com/docs/mcp",
            }
        },
        allowed_tools=["mcp__claude-code-docs__*"],   # whitelist this server's tools
    )

    async for message in query(
        prompt="Use the docs MCP server to explain what hooks are in Claude Code",
        options=options,
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)

asyncio.run(main())
```

**Notice:**
- `mcp_servers` registers a server by name; here it's a remote HTTP server.
- Tools from a server are namespaced `mcp__<server-name>__<tool>`. `allowed_tools` is your safety gate — the agent can only touch what you permit.
- The Agent SDK runs the *whole agent loop* for you (the loop you built by hand in the `agent-loops` skill) — you just supply the prompt and the servers.

> 📁 Class repo: `week7/mcpserver.py` (remote docs server), `week7/mcpfilesystem.py` (local filesystem server), `week7/agent.py` (plain chat loop for comparison).

### MCP vs. hand-written tools
| Hand-written tools (Week 3) | MCP servers (Week 7) |
|---|---|
| Defined inside your script | Reusable across any agent/app |
| You write schema + function | Server already exposes them |
| Great for one bespoke ability | Great for standard capabilities (files, DBs, SaaS) |

---

## Part B — Skills (and Plugins)

### What a Skill is
A **Skill** is a folder with a `SKILL.md` file: a description of *when* to use it plus instructions/know-how. When a task matches the description, Claude loads the skill's content into context — like giving the model a just-in-time playbook. (This file is a skill. So is `/graphify`.)

Minimal anatomy:

```
my-skill/
└── SKILL.md
```

```markdown
---
name: pr-description
description: "Write a clear pull-request description from the staged git diff. Use when the user asks for a PR description or summary of their changes."
---

# PR Description Writer

1. Run `git diff --staged` and `git log -5 --oneline` to see what changed.
2. Summarize the change: what & why, not line-by-line.
3. Output sections: Summary, Changes, Testing, Notes.
```

The **frontmatter `description` is the trigger** — write it as "what it does + when to use it," because that text is how the model decides to invoke the skill. The body is the expertise.

> 📁 Class repo: `week7/skill.md` — a PR-description skill built in class.

### Skills → Plugins → Marketplaces
- **Skill** = one folder with a `SKILL.md`.
- **Plugin** = a bundle of skills (+ optional commands, agents, MCP servers) with a `plugin.json`. *This bootcamp is one plugin with 8 skills.*
- **Marketplace** = a git repo listing plugins, so others can install them:

```
/plugin marketplace add <owner>/<repo>
/plugin install agentic-coding-fitness@agentic-coding-fitness
```

That's the whole distribution chain: write know-how once → package it → share it → teammates `/plugin install` and get it instantly.

---

## How MCP and Skills fit together
- **MCP** gives an agent new **tools** (things it can *do*).
- **Skills** give an agent new **know-how** (how to do something well, when to do it).
- A plugin can ship *both*: skills for expertise + MCP servers for capabilities.

---

## 🧪 Guided lab (offer this)

Two short builds — pick based on interest:

**Lab 1 — Use an MCP server (15 min)**
1. `pip install claude-agent-sdk` and run the docs-server example above. Confirm it answers from the live docs.
2. Swap in the **filesystem** MCP server and ask the agent to summarize a file in the repo. Discuss how `allowed_tools` limits what it can touch.
3. Reflect: which Week-3 tools could be replaced by an existing MCP server?

**Lab 2 — Write your own Skill (15 min)**
1. Make a folder `my-first-skill/` with a `SKILL.md`. Pick a repeatable task they actually do (e.g. "write a commit message from the diff", "explain a stack trace").
2. Focus on the `description` line — rewrite it twice until it clearly says *what + when*.
3. Drop the folder in `~/.claude/skills/`, restart, and trigger it by asking for that task.
4. **Stretch:** add it to a `plugins/<name>/skills/` folder with a `plugin.json` and a `marketplace.json`, then `/plugin marketplace add ./` locally — they've now built a shareable plugin, exactly like this bootcamp.

End by pointing out the meta-moment: "you just learned the format this whole course was packaged in."
