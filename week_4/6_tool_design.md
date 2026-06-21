# Lesson 6: Tool Design as a Craft (Closing Reading)

This lesson is reading, not a build step — by now you've already written `run_command`, `todo_write`, `edit_file`/`write_file`, and possibly `grep`. This is the lens to look back at them through, and to keep in mind for every tool you write for the rest of the course.

---

## Descriptions Are Prompts, Not Documentation

A model doesn't see your code. It sees a name, a description, and a parameter schema — that's the entire interface. If the description is vague, the model avoids the tool, calls it with wrong arguments, or guesses instead of looking something up. That's not a bug in your agent loop; it's a tool description that didn't do its job.

Compare two descriptions for `run_command`:

> "Runs a shell command and returns the output."

versus

> "Run a shell command in the workspace and return its output. Use this to search (grep/find), inspect history (git log/diff), run tests, or make a change. Read-only commands run immediately. Anything that writes, deletes, or installs will pause for human approval — expect that pause, it's not a failure."

The first is documentation. The second tells the model *when* to reach for it, *what's actually available* through it, and *the one mistake not to make* (treating an approval pause as an error and giving up instead of waiting for the result). Anthropic's own guidance in *["Claude Code: Best practices for agentic coding"](https://www.anthropic.com/engineering/claude-code-best-practices)* describes exactly this: tool descriptions in production agents read like onboarding notes for a capable but unfamiliar engineer, not API references — *when* to use this over that, and the specific mistake people make with it.

---

## What a Good Description Does

| Does | Doesn't |
|---|---|
| States *when* to use the tool relative to others ("use `run_command` for search and tests, `read_file` once you know the file") | Just states what the function technically does |
| Calls out the one mistake models actually make with this tool (treating truncated output as complete, ignoring `exit_code`, batching todo updates to the end) | Lists every parameter with no guidance on sequencing |
| Matches the schema's parameter descriptions to the tool description's vocabulary | Leaves parameter descriptions as an afterthought |
| Is short enough that a model attends to all of it | Reads like a man page |

The test: hand only the name + description + schema (no code) to an engineer who's never seen your project. Could they use it correctly on the first try, including knowing when *not* to use it? If not, the model can't either.

---

## Predictable Return Shapes

Every tool this week should follow Week 3's convention — `{"content": ...}` or `{"error": ...}`, never a raw traceback — held to a higher bar now that there are more tools and more chances for confusion:

- **Same shape across tools.** `run_command`, `read_file`, `edit_file`, and `todo_write` should all signal errors the same way.
- **Errors that suggest the next step.** `{"error": "blocked: user did not approve this command — try a narrower or read-only alternative, or explain why it's needed"}` is far more actionable than a bare exit trace.
- **Truncation is visible, never silent** — `"truncated": true` on a capped `stdout`, not a string that just stops mid-line with no signal.
- **An approval rejection isn't an error to recover from by retrying the same thing.** Distinguish "blocked: try something else" from "blocked: this exact action was declined" in the message itself, so the model doesn't just resubmit the identical command.

Anthropic's tool-use documentation makes the same point from the API side: a tool result the model can parse reliably matters as much as the tool actually working. See the *[tool use guide](https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview)* for the canonical treatment of description and schema quality.

---

## Schemas: Tight, Not Just Valid

1. **Enums over free text** wherever the value set is known — `todo_write`'s `status` field is `pending | in_progress | completed`, not a free-text string the model has to spell consistently.
2. **Required vs. optional should match what actually breaks the tool**, not just what's commonly provided. `run_command`'s `command` is required; `timeout` is optional with a stated default in the description.

---

## Things to Think About

- **Test descriptions like code.** Give the model a question that should trigger a specific tool and watch which one it picks. Wrong or skipped → fix the description before touching the model or the prompt.

- **Don't over-explain.** A description trying to cover every edge case becomes the man-page problem again. State the one or two things that actually change behavior; trust the schema and return shape for the rest.

- **Keep descriptions and `AGENTS.md` non-redundant.** Tool descriptions say *how to call this tool correctly*. `AGENTS.md` says *which tool to reach for given this kind of question*. Mixing the two makes both harder to maintain.

---

## Further Reading

- Anthropic, **"Claude Code: Best practices for agentic coding"** — <https://www.anthropic.com/engineering/claude-code-best-practices>
- Anthropic, **tool use guide** — <https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview>
- OpenAI function-calling guide — best practices on description writing

**Back to:** the [Code Scout project](../README.md#project-code-scout)
