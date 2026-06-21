# Lesson 1: Command Execution — The Tool That Changes Everything

## The Problem

Every tool you've built since Week 2 — `web_fetch`, `read_file`, `list_files`, the arXiv tools — has the same shape: one narrow capability, one schema, one Python function you wrote by hand. That's been fine because each one solved a specific, anticipated need.

A shell already solves almost every need you haven't anticipated. `grep`, `find`, `ls`, `cat`, `git log`, `git diff`, a test runner, a linter, `python -c "..."` for a quick sanity check — all of it already exists, already works, and you didn't have to write a wrapper for any of it. The single highest-leverage tool you can give a coding agent isn't a clever bespoke one. It's a well-scoped way to run a command and read back what happened.

This is not a niche opinion. It's the tool that every serious coding agent — Claude Code, Aider, SWE-agent, Devin — is built around, and several of the most-cited posts on building agents reduce the entire problem to it.

---

## "It's Just a Bash Tool"

Anthropic's own engineering post, *["Claude Code: Best practices for agentic coding"](https://www.anthropic.com/engineering/claude-code-best-practices)*, describes Claude Code leaning on `bash` heavily for exactly this reason — exploring a codebase with `grep`/`find` rather than custom search tools, running the test suite directly, checking `git log` and `git blame` for history a file-read tool could never give you.

[Terminus](https://www.tbench.ai/news/terminus), an agent with just a tool to run commands over a tmux session ranks higher than Claude Code on the [Terminal bench](https://www.tbench.ai/leaderboard/terminal-bench/2.0?models=GPT-5.3-Codex,Claude+Opus+4.6)

Here's an interesting talk: https://www.youtube.com/watch?v=RjfbvDXpFls

---

## Designing `run_command` for This Week

The tool's contract is simple: take a shell command, run it, return what happened — structured, not as a raw terminal dump.

```
run_command:
  description: "Run a shell command in the workspace and return its output. Use this to search (grep/find), inspect history (git log/diff), run tests, or run linters. Read-only commands run immediately. Commands that write, delete, or install will pause and ask the human operator for approval before running — expect that pause, don't treat it as a failure."
  parameters:
    command  (string, required)  — the shell command to run
    timeout  (integer, optional) — seconds before the command is killed, default: 10
```

Returns:

```
{
  "stdout": "...",       (truncated if long, with "truncated": true)
  "stderr": "...",
  "exit_code": 0,
  "truncated": false
}
```

The `exit_code` field matters as much as the text — it's how the model knows a command *succeeded* without having to parse output for evidence. A test runner that prints nothing on success but exits `0` is unreadable without it.

https://www.redhat.com/en/blog/exit-codes-demystified

### Checking the Path

Before anything else, `run_command` needs the same sandbox discipline as every Week 3 file tool: a command shouldn't be able to reach outside the target repo just because it's phrased as a shell string instead of a file-tool argument.

```
function paths_within_sandbox(command, workspace_root):
    for token in shlex.split(command):
        if looks_like_a_path(token):
            if resolve_path(token, workspace_root) is None:   # Week 3's resolve_path
                return False
    return True
```

Treat this as a heuristic, not a guarantee — pipes, command substitution (`$(...)`), and environment variables can all smuggle a path past a token-level check. It's a meaningful first line of defense, not the whole defense.

### Allow by Default, Ask Before Anything Destructive

This week's agent stops treating "safety" as a blanket block on everything risky-looking, and instead splits commands into three buckets:

1. **Known read-only** — `grep`, `find`, `ls`, `cat`, `head`, `tail`, `git log`/`diff`/`status`/`blame`/`show`, test runners, linters. These run immediately once the path check passes — no friction for the thing the agent will do most.
2. **Known destructive** — `rm`, `mv`, `>`/`>>` redirection, `git commit`/`push`, `pip install`/`npm install`, `curl | sh`, `sudo`, `chmod`. These no longer get silently blocked — they get surfaced to you, the human at the terminal, with a clear warning, before anything runs.
3. **Anything unclassified** — treated like bucket 2. The safer default when a command doesn't match a known-safe pattern is to ask, not to assume it's fine.

```
function run_command(command, cwd, timeout=10):
    if not paths_within_sandbox(command, cwd):
        return {"error": "blocked: command references a path outside the workspace"}

    if matches_any(command, READ_ONLY_ALLOWLIST):
        return execute_and_format(command, cwd, timeout)

    print("WARNING: the agent wants to run a command that may write, delete, or install:")
    print("    " + command)
    approved = input("Allow this command? [y/N]: ").strip().lower() == "y"

    if not approved:
        return {"error": "blocked: user did not approve this command"}

    return execute_and_format(command, cwd, timeout)


function execute_and_format(command, cwd, timeout):
    result = execute(command, cwd=cwd, timeout=timeout, capture_output=True)
    return {
        "stdout": truncate(result.stdout),
        "stderr": truncate(result.stderr),
        "exit_code": result.exit_code,
        "truncated": was_truncated(result.stdout),
    }
```

Notice what changed from a pure deny-list: the agent is never silently stopped — it's stopped *in front of you*, with the exact command and a warning, and a human makes the call. That's a meaningfully more honest safety story than "the code quietly decided this was too dangerous to even mention."

A timeout still applies regardless of bucket — a hung process blocks the whole loop, approved or not, so kill it after `timeout` seconds either way.

Note that "destructive" here includes commands that edit or write files, not just ones that delete them — this agent is not read-only. The gate is what makes that safe enough to teach: the model can propose a real change, but a human approves the specific action before it happens. A colorized diff instead of a bare command string, and a "remember this for the session" option so you're not re-approving the same safe-ish command repeatedly, are both fair game as bonus polish (see the README) — get the bare y/n right first.

---

## Why Every Command Starts Fresh

Each call to `run_command` is its own subprocess — there's no shell sitting around between calls remembering what happened last time. A few consequences fall directly out of that:

- **`cd` doesn't persist.** If one command runs `cd src && ls`, the *next* `run_command` call starts back at `cwd`, not in `src`. Chain anything that depends on a working directory inside one command (`cd src && pytest`), or pass the directory explicitly each time.
- **Environment variables don't persist** between calls either, unless your wrapper explicitly carries them forward into the next one.
- **Background processes don't persist** — anything started with `&` is orphaned the moment the subprocess that launched it exits.

This is a deliberate simplicity trade-off, not an oversight — and it's worth knowing the alternative exists. [Terminus](https://www.tbench.ai/news/terminus), mentioned above, runs commands inside a single persistent `tmux` session instead of one-off subprocesses, so `cd`, environment state, and long-running processes *do* carry across calls — a meaningfully more powerful (and more complex) design than this week's stateless `run_command`. Stateless-per-call is the right scope for this week; a persistent session is a natural extension if you want to chase that design further.

To actually build `run_command`, you'll be reaching for Python's `subprocess` module — read up on `subprocess.run`, `capture_output`, and `timeout` before you start, and `shlex` for safely tokenizing a command string for the path check above.

---

## What `run_command` Replaces

You could still build bespoke `grep`/`list_files` tools (Lesson 3 covers when that's worth it) — but notice that once `run_command` exists, the model can already do most of that itself: `grep -rn pattern .`, `find . -name "*.py"`, `git log --oneline -- path/to/file`. The bespoke tools trade flexibility for structure (predictable JSON instead of raw stdout the model has to parse) — a real trade-off, not a strictly better option, and one worth discussing explicitly with students rather than assuming the answer.

---

## Things to Think About

- **Structured vs. raw.** `run_command("grep -n pattern .")` returns raw stdout the model has to parse itself. A bespoke `grep` tool (Lesson 3) returns `{"file", "line", "text"}` per match. Which is more reliable in practice? Try both and watch where the model gets confused.

- **Truncation and exit codes together.** A truncated `stdout` with `exit_code: 1` is ambiguous — did the command fail, or did it just get cut off before printing the error? Consider keeping `stderr` untruncated even when `stdout` is capped.

- **The classification will be incomplete.** Pattern-matching a command string into "read-only" vs. "ask" is a teaching-grade safety net, not a production one — a determined adversarial prompt can phrase a destructive command in a way your patterns don't catch, or hide it inside a pipeline. The path check has the same limits. None of this replaces a human actually reading the command before approving it.

- **Asking too often defeats the point.** If even harmless-but-unclassified commands constantly trigger a y/n prompt, you'll train yourself to reflexively hit "y" without reading — which defeats the entire safety mechanism. A tight, well-maintained read-only allowlist matters as much as the ask-prompt itself.

---

## Further Reading

- Thorsten Ball, **"How to Build an Agent"** — <https://ampcode.com/how-to-build-an-agent>
- Anthropic, **"Claude Code: Best practices for agentic coding"** — <https://www.anthropic.com/engineering/claude-code-best-practices>
- Yang et al., **"SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering"** — <https://arxiv.org/abs/2405.15793>
- Python docs, **`subprocess`** — <https://docs.python.org/3/library/subprocess.html> — `run`, `capture_output`, `timeout`, and why `shell=True` is usually the wrong default
- Real Python, **"The subprocess Module: Wrapping Programs With Python"** — <https://realpython.com/python-subprocess/>
- Python docs, **`shlex`** — <https://docs.python.org/3/library/shlex.html> — safely tokenizing a command string instead of splitting on spaces
- tmux wiki — <https://github.com/tmux/tmux/wiki> — the persistent-session model behind Terminus, for when stateless-per-call stops being enough

**Next:** [2_todo_loop.md](2_todo_loop.md)
