---
track: "genai"
week: 4
---

# Week 4: From General Agent to Specialist

## Objective

This is the week your agent stops being a demo and starts being autonomous.

Every week so far built one piece: tools, memory, a class hierarchy. This week those pieces click into an agent that can be handed a real problem in a codebase it has never seen — and left alone to find the bug, fix it, prove the fix works, and tell you it's done. No hand-holding, no pre-fetched context, no "here's the file, now what." It searches. It runs commands. It edits real files. It checks its own work against a real test suite before it dares say "done." That's not a metaphor for autonomy — by the end of this week, it's what's actually running on your machine.

This is the **seam week**, and it has exactly **two focus points**:

1. **Exploring codebases** — knowing where to look before you act, instead of reading a repo top to bottom
2. **Running commands** — turning what you found into something that actually changes (and verifies) the repo

This agent is not read-only. It searches, reads, edits, writes, and runs commands — including ones that modify the target repo — the same way a real coding agent does. The safety rail isn't "writes are banned," it's "anything destructive or unclassified pauses for your explicit y/n approval, with the exact command or diff shown to you first." That distinction — gate the action, don't ban the capability — is the whole design philosophy this week.

By the end you'll have **Code Scout**: a CLI agent that can investigate *and fix* issues in a real, unfamiliar codebase — searching, reading, editing, running tests, and working through an explicit todo list until the fix is actually verified, not just claimed.

---

## What You'll Learn and Build

1. **Command Execution — the prime tool**
   - A `run_command` tool: the single capability that subsumes search, history, verification, and — once approved — change
   - Why production coding agents (Claude Code, SWE-agent, Aider) are built around a well-scoped shell tool rather than many bespoke ones
   - Path-checking, a read-only allowlist that runs immediately, and a y/n approval prompt with a clear warning for anything destructive or unclassified — gating the action, not banning it

2. **Todo Lists & the Loop-Until-Done Pattern**
   - A `todo_write` tool the model uses to record and update its own plan
   - Changing the agent loop's stopping condition from "model stopped calling tools" to "the model's own plan is actually complete *and verified*"
   - Why this is what separates a reactive tool-caller from a genuine agent (and how Claude Code's own `TodoWrite` tool works)

3. **Finding Code in a Large Repo**
   - `grep`, via `run_command` or a bespoke tool — the trade-offs between the two
   - grep-first vs. embeddings/RAG vs. repo maps, and why different real products picked different answers

4. **Editing & Verifying**
   - Reusing Week 3's `write_file`/`edit_file` for structured, reliable changes, alongside `run_command` for anything a dedicated tool doesn't cover
   - Verifying a change by actually re-running the test suite, not by asking the model if it's confident

5. **Project Memory & Delegation**
   - `AGENTS.md` as a real, converging cross-tool standard, extended with rules for the new tools
   - The "Explore" subagent pattern: delegating bounded, read-only search to a sub-call that returns a digest instead of flooding the main context

6. **Tool Design as a Craft** (closing reading)
   - What separates a tool description the model follows from one it ignores or misuses, looked at through the tools you just built

---

## Setup

No new dependencies — Week 3's environment is enough:

```bash
uv add openai python-dotenv requests markdownify trafilatura textual
```

Your `.env` should still have `OPENROUTER_API_KEY`. `run_command` is built on the standard library `subprocess` module — no external API required.

---

## Lessons

Six lessons, three builds, one project.

| Lesson | Topic |
|---|---|
| [1_command_execution.md](1_command_execution.md) | `run_command` — the tool that changes everything |
| [2_todo_loop.md](2_todo_loop.md) | `todo_write` and looping until the plan is actually done — and verified |
| [3_repo_search.md](3_repo_search.md) | `grep`, and how real agents find code in large repos |
| [4_editing_and_verification.md](4_editing_and_verification.md) | `write_file`/`edit_file`, the approval gate applied to edits, and verifying a fix actually works |
| [5_memory_and_subagents.md](5_memory_and_subagents.md) | `AGENTS.md` as a standard, and delegating search to a subagent |
| [6_tool_design.md](6_tool_design.md) | Closing reading: tool descriptions that actually get used correctly |

**Builds:**

- [builds/build1_command_execution.py](builds/build1_command_execution.py) — `run_command`: path-checking, the read-only/ask classification, the approval prompt
- [builds/build2_explore.py](builds/build2_explore.py) — `grep` and `list_definitions` (AST-aware file outline): the tools for finding the right place before you read or change it
- [builds/build3_todos.py](builds/build3_todos.py) — `add_todos`/`get_todos`/`mark_todo`: deliberately open-ended — you design the shape of a todo and how state is stored, the only hard requirement is title + description + verification method

---

## Project: Code Scout

Your Week 3 `Agent` class, pointed at a codebase instead of the open web, with full read/write/execute capability and a real plan.

### What it does

A real coding agent that:

1. **Explores** a real, unfamiliar open-source repository — `list_files`, `read_file`, and `grep` (via `run_command` or a bespoke tool)
2. **Runs commands** via `run_command` — tests, linters, `git log`/`diff`/`status`, and anything else needed. Known read-only commands run immediately; destructive or unclassified ones pause for your y/n approval with a clear warning
3. **Edits and fixes** real files — via Week 3's `write_file`/`edit_file`, or via `run_command` itself — behind the same approval gate
4. **Verifies its own work** by re-running the test suite (or whatever command defines "correct") after a change, and only marks the relevant todo item complete when that command actually passes — not when the model says it's confident
5. **Plans and persists** — `todo_write` drives the loop until the plan is genuinely, verifiably complete; `AGENTS.md` and sessions carry over from Week 3 unchanged
6. **Runs the same two ways as Week 3**:
   - `python agent.py` — interactive REPL
   - `python agent.py "why is test_auth.py failing — fix it"` — single task, print result, exit

Point the agent at a real external repository you didn't write — cloned into your workspace — ideally one with a test suite you can break and fix on purpose. "Find out why these tests are failing and fix it" is the kind of multi-part, verifiable task this week's tools are built for; a single-file toy repo won't exercise any of it.

> **Grading note:** the graded evaluation for this project is **one single, complex, real-world task** on a large, well-known open-source codebase — not a basket of small self-chosen questions. Practice accordingly: pick a sizeable, well-tested library (something in the spirit of Django, Flask, scikit-learn, or PyTorch — large enough that reading the whole thing isn't an option) and try giving your agent a real bug to find and fix, end to end, before submission. The task you're graded on will be unseen, but the *shape* of it — one nontrivial issue, one real codebase, fix it and verify with tests — won't be a surprise if you've rehearsed it yourself.

### Suggested layout

```
week_4/project/
  agent.py        # Agent, REPLAgent — Week 3's hierarchy, unchanged
  tools/
    exec.py         # run_command (new)
    plan.py         # add_todos / get_todos / mark_todo (new — design is yours, see build3)
    files.py        # read_file, write_file, edit_file, list_files — ported from Week 3
    search.py       # optional bespoke grep
  .agent/sessions/
  AGENTS.md
  target_repo/    # the external codebase under investigation (gitignored or submoduled)
```

### SUBMISSION.md

What you built, which repo you pointed it at, and why — your own voice. Include one example where the agent actually fixed something and verified the fix by rerunning tests, and one example where the todo loop or approval prompt caught a mistake before it became one.

### Getting started

1. Pick an external open-source repo with a real test suite to investigate — something large enough to need real search, in the spirit of Django/Flask/scikit-learn/PyTorch
2. Implement `run_command` (start from [builds/build1_command_execution.py](builds/build1_command_execution.py), [Lesson 1](1_command_execution.md)) — sandboxed, timed out, path-checked, with a y/n approval prompt for anything destructive or unclassified
3. Port `write_file`/`edit_file` from Week 3 so the model has a reliable, structured way to make changes alongside raw `run_command`
4. Design and implement your own todo tools (start from [builds/build3_todos.py](builds/build3_todos.py), [Lesson 2](2_todo_loop.md)) and rewire the agent loop's stop condition to require verification, not just task completion
5. Decide bespoke `grep`/`list_files` vs. relying on `run_command` for search (start from [builds/build2_explore.py](builds/build2_explore.py), [Lesson 3](3_repo_search.md))
6. Write `AGENTS.md` for the project: tool preference order, planning expectations, when to verify, citation format
7. One-shot CLI: `python agent.py "why is test_auth.py failing — fix it"`
8. REPL: `python agent.py`

---

## Bonus Challenges

- **Repo map** — extend `list_definitions` (build 2) across every file in the repo, rank files by how often each declared name is referenced elsewhere (Aider does this with PageRank — see [aider.chat/2023/10/22/repomap.html](https://aider.chat/2023/10/22/repomap.html)), and inject a budget-capped map into context
- **Subagent dispatch** — a second, separately-prompted "explore" agent instance with only read-only `run_command`/`read_file`, capped turns, returning a digest per todo item rather than flooding the orchestrator's context
- **Colorized diff on approval** — when the agent proposes a destructive command or a file edit, show a colorized diff (or the exact command) in the terminal before asking for y/n, instead of a bare string
- **Prompt-injection red-team** — plant a hidden instruction in a target repo's README or a code comment and see whether your agent obeys it when it reads the file; write up a mitigation

---

## Resources

- Thorsten Ball, **"How to Build an Agent"** — <https://ampcode.com/how-to-build-an-agent>
- Anthropic, **"Claude Code: Best practices for agentic coding"** — <https://www.anthropic.com/engineering/claude-code-best-practices>
- Anthropic, **"Building Effective Agents"** — <https://www.anthropic.com/research/building-effective-agents>
- Yao et al., **"ReAct"** — <https://arxiv.org/abs/2210.03629>
- Yang et al., **"SWE-agent"** — <https://arxiv.org/abs/2405.15793>
- Aider's repo map — <https://aider.chat/docs/repomap.html>
- agents.md — the open AGENTS.md spec — <https://agents.md>

---

## Submission Checklist

All project code in `week_4/project/`.

**Packaging:**
- [ ] `requirements.txt` and `.env.example` exist; no real keys in source

**Functionality:**
- [ ] `run_command` is sandboxed to the target repo, timed out, and path-checks command arguments
- [ ] Known read-only commands run immediately; destructive or unclassified commands (including ones that write or edit) pause and ask the human operator for y/n approval with a clear warning, rather than running silently or being silently blocked
- [ ] `write_file`/`edit_file` (ported from Week 3) are available and actually used to fix something in the target repo, behind the same approval gate
- [ ] Todo tool(s) exist (your own design — see build3) and the agent loop's stop condition checks the todo list is actually complete
- [ ] A todo item involving a code change is only marked complete after a verification command (e.g. the test suite) actually passes
- [ ] Agent can search the target repo (via `run_command` and/or a bespoke `grep`) and read files
- [ ] `python agent.py "task"` runs one task against the target repo end-to-end, including any needed fix and verification
- [ ] `python agent.py` starts an interactive REPL
- [ ] Agent loads and follows `AGENTS.md` for the target-repo project
- [ ] Sessions persist and resume, unchanged from Week 3
- [ ] Agent demonstrably works a multi-step task to completion, with at least one approval prompt observed in a live run

**Writeup:**
- [ ] `SUBMISSION.md` in your own words, naming the repo used, with one fix-and-verify example and one approval-gate example

Submission instructions will be posted separately.

---

## Project Brief

Build a CLI program, `agent.py`, that takes a natural-language task about an unfamiliar codebase on disk, figures out on its own which files matter, makes a plan in the form of a todo list, makes whatever changes are needed, proves the change works by actually running a verification command, and reports back — with no human pre-fetching context for it and no human approving anything except the specific destructive actions the safety gate flags. Given a problem or feature, it works until the plan is finished.

### Inputs and outputs

| | Spec |
|---|---|
| **Input** | One task as a string — either a CLI argument or a line typed into the REPL — plus a repo already present on disk at some path under your project (`target_repo/` in the suggested layout) |
| **Output** | A final natural-language answer printed to stdout, citing `file:line` for any factual claim and a verification command's exit code for any fix claim. If the task required a change, that change is actually present on disk in `target_repo/` when the run ends |
| **Not an input** | You do not hand the agent a pre-identified file, line number, or diff. If you find yourself doing that to make a demo work, the exploration half of the project isn't done yet |

### Required capabilities

| Capability | Tool(s) | Name fixed? | Source |
|---|---|---|---|
| Run a shell command, gated by approval | `run_command` | Yes, this name | [build1](builds/build1_command_execution.py) |
| Track a multi-step plan | your own todo tool(s) | No — your design | [build3](builds/build3_todos.py) |
| Search file contents | `grep` (bespoke) or `run_command` | No, your choice | [build2](builds/build2_explore.py) / Lesson 1 |
| Outline a file's declarations | `list_definitions` | Yes, this name | [build2](builds/build2_explore.py) |
| Read a file in windows | `read_file` | Yes, this name | ported from Week 3 |
| Write / line-edit a file | `write_file`, `edit_file` | Yes, these names | ported from Week 3 |
| List a directory | `list_files` | Yes, this name | ported from Week 3 |

Every tool that can write, delete, install, or otherwise change the repo — including `write_file`/`edit_file` and any destructive `run_command` call — goes through the same y/n approval flow from Lesson 1. There is exactly one safety mechanism this week, applied everywhere it's needed, not one per tool.

### CLI contract

```
python agent.py                          # interactive REPL, reuses Week 3's session UX
python agent.py "<task>"                 # one-shot: run the task once, print the answer, exit
python agent.py --session <id> "<task>"  # resume a prior session, then run the task (Week 3 behavior, unchanged)
```

No flag changes this week's required behavior beyond what Week 3 already specified for the REPL/one-shot/session split.

### Worked example: what a real run should look like

Given a target repo with a genuinely failing test, running:

```
python agent.py "the test in tests/test_auth.py is failing, find out why and fix it"
```

should produce a tool-call sequence shaped like this — not these exact calls, but this *shape*:

```
1. run_command("python -m pytest tests/test_auth.py")       → confirm it actually fails, read the traceback
2. add_todos(...)                                            → write a short plan: locate cause, fix, verify
3. grep("def test_") or list_definitions("tests/test_auth.py") → find the failing test function
4. read_file(...)                                             → read the test and the code it exercises
5. edit_file(...) or run_command(...)                         → propose the fix — pauses for y/n approval
6. run_command("python -m pytest tests/test_auth.py")        → re-run; must see exit_code 0 this time
7. mark_todo(..., status="completed", evidence="exit 0")      → only now, with evidence in hand
8. final answer: what was wrong, what changed (file:line), and the verifying exit code
```

If your agent can produce this shape end to end on a repo it's never seen, the project works. If it "fixes" the test by skipping straight from step 1 to step 5 with no search, or marks step 7 complete without re-running anything, that's the gap to close.

### Definition of done

The project is complete when, on a fresh clone of an external repo your agent has never been pointed at before:

1. A single CLI invocation with a real feature or bug-fix task produces a verified fix or an honest, evidenced "I couldn't verify this" — never a confident claim with no exit code behind it
2. At least one destructive action during that run actually paused for your y/n approval, and the run continued correctly after you answered
3. The transcript shows search happening before broad reading — not the whole repo read top to bottom
4. The same agent object/class also runs as a REPL and resumes a saved session, unmodified from how Week 3 built that
5. Your agent handles todos gracefully, even on session restarts

Tip: While testing your agent, make Opencode or Claude Code do the same thing and notice the difference of approach. There is a lot you can learn from this exercise.