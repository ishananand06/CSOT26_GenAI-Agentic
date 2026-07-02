# Week 5: The Final Stretch — Make It Yours

## Objective

Five weeks ago you made a single API call. Last week you had an agent that could be handed a real bug in an unfamiliar codebase and left alone to fix it and prove the fix worked.

This is the capstone. There is barely any new theory this week and **no builds**. You take the Week 4 agent you already have and turn it from *a fixed set of capabilities someone (you) chose in advance* into *a platform that can be extended without editing its code*. Two mechanisms do this, and they're the two that every production agent has converged on:

1. **Skills** — teach the agent new *procedures* (a commit workflow, a review checklist, a deploy runbook) by dropping a markdown file in a folder. No code change.
2. **MCP servers** — give the agent new *tools* it never shipped with — GitHub, a database, a browser — by connecting to a server someone else wrote and maintains. Most real ones need an API key, so we cover authentication properly.

---

## What You'll Learn

1. **Skills: storage, loading, execution**
   - Where the idea came from and why bloated system prompts forced it into existence
   - **Progressive disclosure**: how real harnesses (Claude Code, the open Agent Skills standard) keep a hundred skills available for minimal context cost.
   - A simplified `skills/` directory + loader + `load_skill` tool you add to your Week 4 agent — no new execution engine needed, your existing `run_command` already runs any bundled script

2. **Connecting to MCP servers (with authentication)**
   - How MCP's transport evolved from stdio → HTTP+SSE → today's **Streamable HTTP**
   - Why almost every hosted server needs an **API key**, and exactly how that key travels (an HTTP header — usually `Authorization: Bearer …`)
   - A complete, working example connecting your agent to the **GitHub MCP server**

3. **Configuration as Code (your final reading )**
   - Why "just hardcode it" stops working the moment a tool is meant to be used by more than one person or in more than one situation
   - The Pragmatic Programmer's take, explained from scratch, plus free follow-up reading

---

There are **no `builds/` this week.** Every lesson is something you add directly into the agent you already built. Make sure to copy it into a `week_5` folder though.

## Lessons

| Lesson | Topic |
|---|---|
| [1_skills.md](1_skills.md) | Skills: storage, loading, and execution. A simple interpretation of the agentskills.io spec |
| [2_mcp.md](2_mcp.md) | Connecting to authenticated MCP servers, with a working GitHub example |
| [3_config_as_code.md](3_config_as_code.md) | Closing reading: configuration as code, and why it matters |

---

## Project: Your Agent

There is no "Perplexity clone" or "Code Scout" brief this week with a fixed spec. The brief is:

> Take your Week 4 agent and make it the most useful thing you can, and at the same time make it extendable with skills and MCP. This week is about creativity, so add in features you'd enjoy working with.

That's deliberately open. Some directions, none required, pick what's useful to *you*:

- A **commit** skill that runs your tests, stages, and writes a conventional commit message.
- A **review** skill that reads a diff against a checklist you actually care about.
- Wire in the **GitHub MCP server** so your agent can create repos, open issues, read PRs, or triage a repo without you leaving the terminal.

Build the one that would genuinely save *you* time. That's the whole assignment.

You are not limited to adding functionality via skills and MCP alone. Have ideas for an interesting tool? Add it!

When deciding whether some functionality would be useful or not, try doing the task it is supposed to help with, first without and with that functionality. Since no one really knows how LLMs perform better, experimentation is the only way to know if something is objectively 'better'.

### SUBMISSION.md: Don't take it lightly this week

This week, there is no fixed feature checklist to tick, so your writeup is how we understand what you built and why. Treat it as the primary artifact. It should cover:

- **What your agent does now** that the Week 4 version couldn't — concretely.
- **Every skill and feature you wrote**: what it does, why you chose it, and how the loader picks it up.
- **How you tested your agent**, since decisions on what to add should not be purely from speculation.

- **At least one cool thing your agent can do** — a task you can hand it in one sentence and walk away from, described end to end, *plus a precise recipe for how someone else could replicate it* (the skills/servers involved, the `.env` keys they'd need, the exact prompt you gave it, and what "done" looked like). This is the centerpiece 
- make it reproducible, not just impressive-sounding.
- Anything that surprised you, broke, or that you'd do differently.

A generic AI-generated summary scores poorly. Write it in your own voice, document like you're handing the project to a teammate.

---

## Some random ideas from the author

- **Per-session MCP toggles**: commands like `/mcp list`, `mcp enable/disable <server>` to toggle functionality per session.
- **A skill that writes skills** — a meta-skill that scaffolds a new `SKILL.md` from a short description.
- **Making your agent extendable**: The Pi agent provides the agent with instructions on how to edit the system prompt, add or modify its own tools. What if your agent could modify its capabilities based on what it needs?

---

## Resources

- Agent Skills — the open standard — <https://agentskills.io>
- MCP transports (Streamable HTTP) — <https://modelcontextprotocol.io/docs/concepts/transports>
- MCP authorization spec — <https://modelcontextprotocol.io/specification>
- GitHub MCP server — <https://github.com/github/github-mcp-server>
- Python MCP SDK — <https://github.com/modelcontextprotocol/python-sdk>
- The Pragmatic Programmer (Hunt & Thomas) — the "configuration" and "DRY" tips

---

## Submission Checklist

All project code stays in your Week 4 project directory (renamed to `week_5/project/` if you like, or wherever your agent lives).

**Packaging:**
- [ ] `requirements.txt` and `.env.example` exist; no real keys in source, config, or history
- [ ] Any MCP key is read from the environment, never committed

**Functionality:**
- [ ] The agent loads skills from a `skills/` directory and can execute at least one
- [ ] The agent can connect to any external MCP server and can call its tools. This server's detials may be defined in some config.json file.
- [ ] The user can easily add and see the status of added skills and MCPs
- [ ] Some extra creative features in your agent.

**Writeup (the main deliverable this week):**
- [ ] `SUBMISSION.md`, in your own words, documenting everything above
- [ ] It describes at least one cool feature and some autonomous task your agent can do, with a full replication recipe