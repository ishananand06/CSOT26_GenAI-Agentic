# Lesson 5: AGENTS.md as a Standard, and Delegating Search

## AGENTS.md Isn't Just Yours

Week 3 treated `AGENTS.md` as a convention you invented for your own research agent. It's bigger than that now: `AGENTS.md` is an actual open specification (see [agents.md](https://agents.md)) that multiple agent tools read directly — write one and, in principle, several different coding agents pick up the same project rules without tool-specific config for each. Cursor's `.cursor/rules`, Claude Code's `CLAUDE.md`, and Aider's conventions file are the same idea under different names; the industry is converging on `AGENTS.md` as the common one.

For Code Scout, carry over the Week 3 split — user-editable rules live in `AGENTS.md`, developer-owned rules (iteration caps, the tool list) stay in code — and write rules specific to *this* agent's new capabilities:

```markdown
# Code Scout Rules

## Tools
- Prefer run_command for git history, tests, and broad search (grep/find)
- Use read_file once you know the file and roughly which lines matter
- Prefer edit_file over run_command for precise, line-level changes;
  use run_command for anything edit_file doesn't cover
- Expect destructive or unclassified commands and any write/edit to pause
  for human approval — that's normal, not an error

## Planning
- For any task with more than one sub-question, call todo_write first with
  your full plan before doing anything else
- Update todo_write as items complete — don't batch updates to the end
- A todo item that changes code is not "completed" until the relevant
  verification command (usually the test suite) has actually exited 0 —
  cite the exit code as evidence

## Citations
- Always cite file:line for any claim about behavior
- If grep/run_command returns zero results, try a broader term before
  reporting that something doesn't exist
```

This is the same loading pattern as Week 3 — read the file, prepend it to the system prompt — applied to tools that didn't exist last week.

---

## When One Agent's Context Gets Too Crowded

A real investigation can take many command/search round trips before the agent has enough to answer. Every tool call and result stays in the conversation, growing what the model has to re-process every turn — even the dead ends.

One answer, used in production agents including the one driving this course: dispatch a **subagent** — a separate, bounded tool-call loop with a narrow toolset (`run_command`, `read_file`, restricted to read-only commands) and a turn cap — give it a sub-question, let it explore, and have it return a short digest. The main agent's context grows by one digest, not by every intermediate step.

```
Orchestrator (Agent, with todo list: "investigate test failures")
  todo item: "find out why test_auth.py is failing"
  dispatches → Explore subagent
                  tools: run_command (read-only), read_file
                  task: "find and explain why test_auth.py fails"
                  returns: short digest with file:line citations
  receives digest, marks todo item completed, moves to next item
```

In pseudocode, the dispatch is just another tool call from the orchestrator's point of view:

```
function explore(task, max_turns):
    sub_messages = [system: "You are a read-only investigation agent. Tools:
                              run_command (read-only commands only), read_file.
                              Return a concise digest with file:line citations."]
    sub_messages.append(user: task)

    for turn in range(max_turns):
        response = call_model(sub_messages, tools=[run_command, read_file])
        if response.has_tool_calls:
            run tool calls, append results to sub_messages
        else:
            return response.text     # the digest

    return "exploration incomplete after max_turns"
```

This is a bonus-tier build (see the README), not required for the core deliverable — but it's the direct answer to "what do you do when search starts eating your context window," a problem every coding agent in production has solved some version of.

---

## Why the Explore Subagent Stays Read-Only Even Though the Orchestrator Isn't

Notice the asymmetry above: Code Scout itself can write, edit, and run destructive commands (behind approval). The Explore *subagent* it dispatches cannot — its toolset is deliberately limited to `run_command` (read-only) and `read_file`. That's not a leftover constraint from an earlier draft of this week — it's a deliberate privilege-separation choice: delegate the part of the work that's safe to parallelize and doesn't need a human in the loop (looking around), and keep the part that changes the repo (editing, destructive commands) on the one agent whose actions you're actually watching and approving. A subagent you've spun off to "go find out why X is failing" should not be the one quietly running `git commit` while you're not looking at its transcript.

Week 5 goes further than this week's bare y/n — richer diffs, persistent approval memory across a session, and more deliberate multi-step refactors — but the core loop (search → act → verify, gated by human approval) is fully in place this week, not deferred.

---

## Things to Think About

- **AGENTS.md drift.** As Code Scout's behavior evolves, rules accumulate. Reread your own `AGENTS.md` periodically and check it still matches what the agent does — an instruction the agent silently ignores looks authoritative but isn't.

- **Subagent digests need the same structure discipline as every other tool.** A digest that's unstructured prose is harder for the orchestrator to act on than one with `file:line` citations baked in.

- **Delegation costs latency, not correctness.** A subagent call is a full extra loop of model calls before the orchestrator gets anything back. It saves context, not time.

---

## Further Reading

- agents.md — the open AGENTS.md spec — <https://agents.md>
- OpenCode's context file handling — <https://opencode-ai-opencode.mintlify.app/core-concepts/architecture>
- CoALA paper (revisit from Week 3) — <https://arxiv.org/abs/2309.02427>

**Next:** [6_tool_design.md](6_tool_design.md) (closing reading)
