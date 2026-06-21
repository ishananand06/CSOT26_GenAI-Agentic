# Lesson 2: Todo Lists & the Loop-Until-Done Pattern

## The Problem

Your agent loop since Week 2 has had one termination condition: keep calling tools while the model keeps returning tool calls; stop when it stops. That's correct for a single question with a single answer. However, it becomes insufficienat for tasks with multiple sub-goals: "investigate why these 12 tests are failing".

The model can call a tool a few times, find *one* answer, and produce a final response that only addresses part of the task. The loop ends. Nothing told it to keep going.

The fix isn't a smarter model. It's giving the agent an explicit, visible plan, and changing what "done" means from *the model stopped talking* to *every item on its own plan is checked off*.

---

## The Pattern: An Explicit Todo List the Model Maintains

This is not a course invention — it's how Claude Code actually works. Its `TodoWrite` tool exists specifically so multi-step tasks don't get abandoned halfway, and so the operator watching the terminal can see the plan as it executes rather than getting a single opaque final answer. Anthropic's own description of this, in *["Claude Code: Best practices for agentic coding"](https://www.anthropic.com/engineering/claude-code-best-practices)*, frames task-list tracking as core to how Claude Code stays on multi-step work without losing the thread.

The tool is simple. The model writes and updates a checklist of its own subgoals:

```
todo_write:
  description: "Record or update your task list for this request. Call this
                before starting multi-step work to write your plan, and again
                whenever an item's status changes. Always include the full
                current list, not just the item that changed."
  parameters:
    items (array, required):
      - id      (string)
      - content (string)               — what this subtask is
      - status  (enum: pending | in_progress | completed)
```

Returns the full list back, so both the model and (if you're building a TUI) the user can see current state:

```
{"todos": [{"id": "1", "content": "find failing tests", "status": "completed"},
           {"id": "2", "content": "identify root cause for test_auth", "status": "in_progress"},
           {"id": "3", "content": "identify root cause for test_db",  "status": "pending"}]}
```

---

## Changing the Loop's Termination Condition

The agent loop itself changes shape. It no longer stops the moment the model produces text instead of a tool call — it checks whether the model's own todo list is actually finished first:

```
function run_loop(messages, max_iterations):
    for i in range(max_iterations):
        response = call_model(messages, tools=ALL_TOOLS)

        if response.has_tool_calls:
            dispatch tool calls (including todo_write), append results to messages
            continue

        if todo_list_exists() and not all_items_completed(current_todo_state):
            messages.append(user: "Your todo list still has pending or in_progress
                                    items. Continue working through it, or update
                                    the list if something is blocked.")
            continue

        return response.text   # genuinely done: no tool calls, list complete

    return "stopped after max_iterations without completing the todo list"
```

Two failure modes this guards against:

- **Premature stopping** — the model answers part of the task and calls it done. The loop pushes back instead of accepting the first plausible-looking stop.
- **Silent abandonment of subgoals** — without a visible list, "I looked into a few things" can hide that three sub-questions were never actually addressed. With the list, an unaddressed item is visible, not implicit.

This is the same iteration-cap discipline from Week 2's agent loop, now wrapping a longer-running process — `max_iterations` still has to exist and still has to be enforced, because a model that never marks anything `completed` would otherwise loop forever.

---

## "Completed" Should Mean Verified, Not Just Claimed

Once the agent can actually edit files and run commands (Lesson 1, Lesson 4), a new failure mode opens up that a pure research agent never had: the model can mark a todo item `completed` because it *wrote a plausible-looking fix*, without that fix actually working. "I edited the function" and "the bug is fixed" are different claims, and only one of them is checkable.

The fix is the same idea Week 2's tool loop was already built on — don't trust a claim you can verify, verify it:

```
function mark_completed(item, evidence):
    if item.requires_verification and evidence.command_exit_code != 0:
        return {"error": "cannot mark completed: verification command failed (exit " +
                          str(evidence.command_exit_code) + "). Fix and re-run first."}
    return update_status(item, "completed")
```

In practice this means your `AGENTS.md` (Lesson 4) should say something like: *"a todo item that changes code is not `completed` until you've re-run the relevant test/build command via `run_command` and it exited 0 — paste the exit code as evidence."* The model still writes the todo list and still decides when it's done; you're just making "done" mean something a command exit code agrees with, not something the model asserts on its own authority.

This is the same idea, scaled down, behind how coding-agent benchmarks like SWE-bench and Terminal-Bench score a submission: not "did the model say it solved it," but "does the test suite pass afterward." Bringing that discipline into your own agent's loop — instead of only seeing it in a benchmark — is the point of this section.

---

## Why This Is a Genuine Step Up, Not Just Bookkeeping

Anthropic's *["Building Effective Agents"](https://www.anthropic.com/research/building-effective-agents)* draws a line between fixed **workflows** (predetermined steps) and true **agents** (the model directs its own process, deciding what to do next based on what it's learned so far). A loop with no explicit task state is closer to the workflow end — it just keeps reacting one tool call at a time with no model of its own progress. A loop with an explicit, model-maintained todo list is closer to the agent end: the model is reasoning about its own plan, not just the next single action.

The academic framing for the underlying reason this works is the **ReAct** pattern — Yao et al., *["ReAct: Synergizing Reasoning and Acting in Language Models"](https://arxiv.org/abs/2210.03629)* — interleaving explicit reasoning traces with actions improves task completion over acting alone, because the model is forced to articulate what it's doing and why before doing it. A todo list is a structured, persistent version of that reasoning trace — one that survives across many tool calls instead of being re-derived (or forgotten) every turn.

---

## Things to Think About

- **What counts as "blocked"?** Should `status` include a fourth value beyond `pending`/`in_progress`/`completed` — e.g. `blocked`, with a reason — so the model can honestly report it's stuck rather than mislabeling something `completed`?

- **Sessions and todos.** Week 3 sessions persist `messages` to disk. Should the todo list be persisted as part of the session too, so resuming a session resumes the plan, not just the conversation?

- **The loop can still legitimately end early.** If the model updates the list to mark something `blocked` with a clear reason and nothing else is `pending`, that's a valid stop — don't force infinite looping on a list that's honestly stuck, only on one that's silently incomplete.

- **Iteration cap sizing.** A todo-driven loop runs longer than a single-question loop by design. `max_iterations` needs to be sized for "complete a multi-step plan," not "answer one question" — too low and you cut off legitimate work, too high and a misbehaving loop burns a lot of tokens before you notice.

---

## Further Reading

- Anthropic, **"Building Effective Agents"** — <https://www.anthropic.com/research/building-effective-agents>

**Next:** [3_repo_search.md](3_repo_search.md)
