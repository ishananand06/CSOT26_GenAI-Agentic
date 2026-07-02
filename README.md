# CSOT GenAI/Agentic Track 2026

## Introduction

Welcome to the **GenAI/Agentic** track of CAIC Summer of Technology 2026.

Five weeks. One project, built entirely from scratch.

This track takes you from your first LLM API call to shipping a real, working AI agent — the kind that doesn't just generate text, but *takes action*. You'll implement every layer by hand: tool dispatchers, agent loops, memory systems, execution environments. No frameworks doing the heavy lifting (Langchain is overrated anyway). Just you and the primitives.

---

## Why the Agents Track?

AI powered engineering is moving fast — from prompt design to orchestration to smarter checks to make it harder for developers to shoot themselves in the foot. Here's what this track gives you:

* **Manual Orchestration Mastery**: Understand the exact mechanics of tool calling, function schemas, and multi-turn loops by coding them yourself — without high-level abstractions hiding the details.

* **State Management Architecture**: Move beyond stateless APIs by designing context buffers, working memory, and evolving long-term memory stores that persist across sessions.

* **Real-World Execution Capabilities**: Bridge the gap between text generation and environment interaction — your agent won't just *describe* what to do, it'll *do it*.

* **Leaderboard-Driven Validation**: Each week ships to an auto-graded eval set. You know exactly where you stand.

---

## What Are We Building?

![](https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzR2YjB2emk1Mm8zYTJ1dTBqM3RtZjkycHo2dXY3NGlta3dmb2pvaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/g0JP0HG6zF0o8/giphy.gif)

The project reveals itself as the weeks progress. Each week you add a new capability layer, and by Week 5 those layers compose into an agent you could actually hand to someone.

---

## Weekly Roadmap

### Week 1: LLM APIs, API-Key Safety & Conversation State

Foundation week — get the fundamentals right so everything built on top of them is solid.

Focus on:

* Understanding LLM API mechanics: requests, responses, tokens, and how to read a response object properly.
* Understanding chat templates: How the conversation is represented as system, assistant and user dialogues.
* Strict API-key hygiene using `.env` files, `python-dotenv`, and `.gitignore` — keys that leak cost you more than just money.
* Managing the stateless nature of LLM APIs by building manual, role-assigned conversation history from scratch.

✅ *Deliverable*: A terminal chatbot that holds a coherent multi-turn conversation, with the API key loaded from the environment and never touching the source code.

---

### Week 2: Tools, Agents, and TUIs

The heart of the course. A tool is a contract between your code and the model. An agent is a loop around tool calls. Once you see it, you can't unsee it.

Focus on:

* Implementing tool calling from scratch using a custom text format — so the SDK abstraction is never magic.
* Using the OpenAI SDK's native function calling: tool schemas, the `tool_calls` response field, and the full round-trip.
* Building web tools: fetching and cleaning pages with `requests`, searching the web with Serper, and understanding `llms.txt`.
* Connecting an online MCP server (AlphaXiv) to an OpenAI SDK agent loop, so the agent can search and read academic papers.
* Wrapping everything in a full-screen terminal UI with Textual.

✅ *Deliverable*: **Build your own Perplexity** — a TUI research agent that chains web search, page fetching, and academic paper search (via AlphaXiv MCP) to answer research questions it couldn't answer alone.

---

### Week 3: Memory, Sessions & the Filesystem

An agent that forgets everything the moment you close it isn't much of an agent. This week it gains persistence and hands.

Focus on:

* Building persistent, resumable sessions that survive restarts by saving conversation state to disk.
* Loading an `AGENTS.md` file into the system prompt so the agent carries standing instructions and preferences across every run.
* Adding academic-paper tools backed by the Hugging Face Papers API.
* Implementing a proper file toolset — `read_file` (with line numbers and paging), `edit_file`, `write_file`, `list_files` — modeled on how real coding agents read and modify code.
* Refactoring into a clean `Agent` class hierarchy so the REPL and TUI share one brain.

✅ *Deliverable*: An agent that remembers past sessions, follows project-level instructions from `AGENTS.md`, and can read and edit files on disk.

---

### Week 4: Code Scout — A Real Coding Agent

The capstone build-up. This week the agent stops describing changes and starts making them — running commands, editing code, and proving its own work.

Focus on:

* Command execution with a safety gate: a sandboxed, timed-out `run_command` that runs read-only commands immediately but pauses destructive ones for your approval.
* A todo loop that keeps the agent working toward a goal until the change is actually verified, not just attempted.
* Repository search — grep and definition-listing tools — so the agent can find its way around an unfamiliar codebase.
* An edit-and-verify cycle: make a change, run the tests, read the failure, iterate.
* Memory and subagents: an `AGENTS.md` standard plus a read-only "Explore" subagent that gathers context without crowding the main loop.
* Tool design as a discipline — descriptions are prompts, not documentation.

✅ *Deliverable*: **Code Scout** — a coding agent you can hand a real bug in an unfamiliar repo and leave alone to fix it and prove the fix works.

---

### Week 5: The Final Stretch — Make It Yours

No new agent this week. You take Code Scout and turn it from a fixed toolset into a platform anyone can extend without touching its code.

Focus on:

* **Skills**: storage, loading, and execution — teach the agent new *procedures* by dropping a `SKILL.md` in a folder, using the progressive-disclosure pattern the real harnesses (Claude Code, the open Agent Skills standard) converged on.
* **MCP with authentication**: connect to *any* external MCP server declared in a `config.json`, handling API-key auth via HTTP headers, with a working GitHub example.
* **Configuration as code**: the principle underneath both — declare your agent's capabilities as data, keep secrets in the environment.

✅ *Deliverable*: **Your agent.** The Code Scout brain plus whatever skills and external tools make it genuinely useful to *you* — documented in a `SUBMISSION.md` well enough that someone else could recreate it.