# Lesson 1: Skills — Storage, Loading, and Execution

## Where This Came From

Think back to what you've done to change your agent's behavior so far. In Week 1 you wrote a system prompt. In Week 3 you added `AGENTS.md` and loaded it into the system prompt on startup. In Week 4 you added rules for your new tools — also in `AGENTS.md`, also loaded on startup.

Notice the pattern, and the problem it's heading toward: **every instruction you want the agent to have, you pay for on every single turn.** The system prompt and `AGENTS.md` are sent with every request, whether the current task needs them or not. That's fine for a handful of rules. It falls apart the moment you want the agent to know *procedures* — a full commit workflow, a database migration runbook, the exact 12 steps to cut a release. Ten detailed procedures in your system prompt is a system prompt that's mostly irrelevant on any given turn, costing tokens and diluting the model's attention on everything it *is* doing.

People hit this wall in practice. The instinct was to keep stuffing more into `AGENTS.md` until it became a sprawling document that was simultaneously too long to keep in context cheaply and too shallow to actually capture a real procedure. The fix, which Anthropic shipped in 2025 as **Agent Skills** and then published as an [open standard](https://agentskills.io) that several tools now share, is almost obvious once you see it:

> Don't load a procedure until the moment you need it. Keep a one-line *description* of each procedure always available, and load the full thing only when that description matches what the user is asking for.

That single move — splitting "what's available" from "the details of how" — is the whole idea. It's called **progressive disclosure**, and it's what this lesson is about.

---

## What a Skill Actually Is

A skill is not a function. It's a **directory** with one required file, `SKILL.md`:

```
skills/
  commit/
    SKILL.md            # required — the entry point
  release/
    SKILL.md
    scripts/
      bump_version.py   # optional — a script the skill tells the agent to run
    reference.md        # optional — detail loaded only if the skill points to it
```

`SKILL.md` has two parts: **YAML frontmatter** and a **markdown body**.

(YAML being Yet Another Markup Language)

```markdown
---
name: commit
description: >
  Stage changes and write a clean conventional-commit message. Use when the
  user asks to commit, save work, or "wrap this up" — not for pushing or PRs.
---

# Commit workflow

1. Run the test suite with `run_command`. If it fails, stop and report — do not commit broken code.
2. Run `git status` and `git diff --staged` to see what's actually changing.
3. Stage the relevant files (ask before `git add -A`).
4. Write a conventional-commit message: `type(scope): summary`, imperative mood, under 72 chars.
5. Show me the message and the file list, then commit once I approve.
```

- The **`description`** is the most important line in the file. It's the *only* part the model sees until the skill is invoked, so it has to answer "when should I reach for this?" — exactly the tool-description discipline from Week 4 Lesson 6. A skill nobody triggers is dead weight.
- The **body** is plain instructions. It can reference bundled files ("run `scripts/bump_version.py`", "see `reference.md` for the full changelog format"), which the agent loads or executes *only when it gets there*.

That's the storage format.

---

## The Three Tiers of Progressive Disclosure

This is the mental model to hold onto. A skill's information lives at three levels, each loaded at a different time:

| Tier | What | When it enters context | Cost |
|---|---|---|---|
| 1. Metadata | `name` + `description` | Always (injected at startup) | Tiny — one line per skill |
| 2. Body | The `SKILL.md` instructions | Only when the skill is invoked | Moderate — one skill's worth |
| 3. Resources | Bundled scripts, `reference.md`, templates | Only when the body points to them | Paid only if actually needed |

A hundred skills cost you a hundred one-line descriptions in the system prompt — cheap. The full body of any one of them is a cost you pay *only* on the tasks that use it. Bundled scripts are never loaded into context at all; they're **executed** (Tier 3 is the reason a skill can generate a chart or run a migration without dumping the script's source into the conversation).

Compare this to `AGENTS.md`, which is entirely Tier 1 behavior — always on. Skills are what you reach for when a procedure is too big or too situational to justify always-on cost. Keep the two non-redundant: `AGENTS.md` holds always-relevant *facts and preferences*; skills hold occasional *procedures*.

---

## Building the Simplified Version (into your Week 4 agent)

You already have every hard part. Your Week 4 agent has a tool loop, `read_file`, and `run_command`. Skills need three small additions, one per verb.

### Storage

A `skills/` directory in your project (from where you invoke the agent), or in your home directory. Each subdirectory is a skill with a `SKILL.md` file.

### Loading

On startup, scan `skills/`, parse the frontmatter of each `SKILL.md`, and inject **only** the name + description into the system prompt. Do **not** load the bodies.

### Execution

Add one tool — `load_skill(name)` — that reads the full `SKILL.md` body and returns it (plus a list of any bundled files, so the model knows what's there). That returned body enters the conversation, and from that point the model simply **follows the instructions using the tools it already has**. If the body says "run `scripts/bump_version.py`", the model calls your existing `run_command`. If it says "read `reference.md`", it calls `read_file`.

**There is no new execution engine.** That's the elegant part and the thing to notice: "executing a skill" is just the model reading a file and calling `run_command` / `read_file` — tools you added a week ago. The skill system is almost entirely a *loading* discipline.

Keep your return shape consistent with everything else — `{"content": ...}` / `{"error": ...}`, as per Week 4 Lesson 6.

## How the Real Harnesses Go Further (and why you don't need to)

So you know what you're simplifying away, here's what Claude Code layers on top of the same core — none of it required this week (but no one said you can't try :P):

- **Invocation control**: `disable-model-invocation` (only *you* can trigger it, e.g. `/deploy` — you don't want the model deciding to deploy) vs. `user-invocable: false` (only the model, for background knowledge).
- **Arguments**: `/fix-issue 123` substitutes `123` into the body via a `$ARGUMENTS` placeholder.
- **Dynamic context**: a `` !`git diff HEAD` `` line in the body runs *before* the model sees it, so the skill arrives with live data already inlined.
- **`allowed-tools`**: pre-approving specific tools while a skill is active, so it doesn't re-prompt.
- **Running in a subagent** (`context: fork`): the skill body becomes a fresh subagent's whole task — the exact Explore-subagent pattern from Week 4 Lesson 5.


## Things to Think About

- **Your description is the entire trigger.** The body can be perfect and the skill still never fires if the description doesn't match how you actually phrase requests. Test it like Week 4 Lesson 6 says: give the agent a prompt that *should* trigger the skill and watch whether it calls `load_skill`. If not, fix the description before anything else.

- **A skill once loaded stays in context.** In the real harnesses the body sits in the conversation for the rest of the session — so write it as *standing instructions*, not a one-time script. Keep it short for the same reason every token is a recurring cost.

- **When is a skill the wrong tool?** If the instruction is always relevant (citation style, tone), it belongs in `AGENTS.md`, not a skill — you'd just be paying an extra tool call to load something you always want. Skills earn their keep on procedures that are *occasionally* needed and *too big* to keep always-on.

---

## Further Reading

- Agent Skills — the open standard — <https://agentskills.io>
- Claude Code skills documentation — <https://code.claude.com/docs/en/skills>
- Anthropic, "Equipping agents for the real world with Agent Skills" — <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
- Revisit: Week 4 Lesson 6 (tool descriptions are prompts) and Week 3 (`AGENTS.md` loading)

**Next:** [2_mcp.md](2_mcp.md) — giving your agent tools it never shipped with.
