# Lesson 4: Editing & Verifying

## The Agent Is Not Read-Only

Up to this point the agent can find things and run things. This lesson gives it the other half of being a real coding agent: it can change a file, and it can check whether that change actually worked.

Nothing about this needs a new safety model — Lesson 1 already built one. `run_command` already pauses for human approval on anything destructive or unclassified. Writing or editing a file is exactly that kind of action, so it goes through the same gate, not a separate one.

---

## Two Ways to Make a Change

### 1. Through `run_command` directly

The model can already write files with shell redirection (`echo "..." > file.py`), `sed -i` for in-place substitution, or a `python -c "..."` one-liner. This needs nothing new — it's the same tool from Lesson 1, and the same approval prompt fires because writes match the "destructive" bucket.

The downside: shell-based editing is fragile. Heredocs and `sed` expressions are easy for a model to get subtly wrong — wrong quoting, off-by-one on a line range, a regex that matches more than intended — and the failure often isn't visible until you read the file afterward.

### 2. Through dedicated `write_file` / `edit_file` tools

Port these straight from Week 3's `tools/files.py`, unchanged:

- `write_file(path, content)` — create or overwrite a file
- `edit_file(path, operation, start_line, end_line, content)` — line-based `replace` / `delete` / `append`, with a diff preview in the return value

These trade flexibility for reliability: the model can't make a quoting mistake in a schema-validated `start_line`/`end_line` pair the way it can in a raw shell string, and the diff-preview return value (from Week 3) gives the model — and the approval prompt — something concrete to show before anything is committed to disk.

**Use both.** Prefer `edit_file` for anything precise (you already know the lines); fall back to `run_command` for things `edit_file` doesn't cover (renaming a file, a multi-file find-and-replace via `sed`). Say this explicitly in `AGENTS.md` (Lesson 5) so the model doesn't have to guess.

---

## The Approval Gate, Applied to Edits

The same three-bucket logic from Lesson 1 governs edits:

```
function write_file(path, content):
    if not paths_within_sandbox([path], workspace_root):
        return {"error": "blocked: path escapes the workspace"}

    diff = compute_diff(read_existing(path), content)
    print("WARNING: the agent wants to write " + path + ":")
    print(diff)
    approved = input("Allow this write? [y/N]: ").strip().lower() == "y"

    if not approved:
        return {"error": "blocked: user did not approve this write"}

    perform_write(path, content)
    return {"content": "wrote " + path, "diff": diff}
```

A `diff` in the prompt, not just a path and a vague "this will write a file," is what makes the y/n meaningful — approving a one-line change and approving a file getting wiped and rewritten should not look the same to the human at the terminal. This is also this week's "colorized diff" bonus (see the README) if you want to go further than plain text.

---

## Verification Is Not Optional

A fix that compiles but doesn't actually fix anything is worse than no fix — it looks done. The discipline from [Lesson 2](2_todo_loop.md) applies directly here: don't let the model mark a code-change todo item `completed` on its own say-so. Require a verification command to actually pass first.

```
1. read the failing test / understand the bug
2. edit_file or run_command to make the change (behind the approval gate)
3. run_command("pytest path/to/test_file.py") to verify
4. only if exit_code == 0: todo_write to mark the item completed,
   citing the exit code as evidence
5. if exit_code != 0: keep iterating — don't claim done
```

This loop — change, run, check the result, repeat until the check actually passes — is the same shape SWE-agent and Claude Code use for real fixes, and it's the shape that turns "the model thinks it's right" into "a command confirms it's right." It's also a direct preview of what Week 5 goes deeper on (the polish: better diffs, richer test feedback, possibly multiple verification passes) — this week, get the loop itself working end to end at least once.

---

## Things to Think About

- **What if there's no test suite?** Not every repo or every task has an obvious verification command. `run_command("python -c 'import module; module.func()'")` as a smoke test, or simply re-running the command that originally failed, are reasonable fallbacks — say so in `AGENTS.md` rather than leaving the model to guess what counts as proof.

- **Diffs lie if you trust the wrong baseline.** `compute_diff` needs to read the file's *current* on-disk state right before computing the diff, not a stale copy from three tool calls ago, or the preview won't match what actually happens.

- **A failed verification isn't a dead end.** The loop should feed the failure (stderr, the failing assertion) back to the model as the next thing to act on — exactly the same "errors are context, not exceptions" principle from Week 2's tool dispatcher.

---

## Further Reading

- Week 3's `tools/files.py` — `read_file`, `write_file`, `edit_file`, `list_files` (port directly)
- Yang et al., **"SWE-agent"** (revisit from Lesson 1) — <https://arxiv.org/abs/2405.15793> — see how its edit-and-verify loop is structured

**Next:** [5_memory_and_subagents.md](5_memory_and_subagents.md)
