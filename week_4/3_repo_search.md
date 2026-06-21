# Lesson 3: Finding Code in a Large Repo

## grep: Command or Bespoke Tool?

Lesson 1 gave the agent `run_command`, which means it can already search a repo: `grep -rn pattern .`, `find . -name "*.py"`. For a lot of questions, that's enough, and it's one less tool to build.

A custom `grep` tool still earns its place when you want **structure** the model can act on directly — `{"file": ..., "line": ..., "text": ...}` per match, ready to feed straight into `read_file`'s `start_line` — instead of raw stdout the model has to parse itself. The trade-off is real, not a strict win either way:

| | `run_command("grep ...")` | custom `grep` tool |
|---|---|---|
| Setup | none — already exists | a function + schema to write |
| Output | raw stdout, model parses it | structured, ready to use |
| Flexibility | full grep/ripgrep flag surface | only what you implemented |
| Safety | needs the deny-list/sandbox from Lesson 1 | sandboxed and capped at the tool level |

Build whichever fits how far you've gotten — or both, and let `AGENTS.md` (Lesson 4) tell the model which to prefer for which kind of question.

---

## How Real Agents Actually Find Code

Regardless of which tool issues the search, the underlying strategy question is the same, and real products answer it differently:

### 1. grep-first

Search the raw text, every time, no precomputed index. Claude Code and Amp's primary strategy.

- **Pros:** zero setup, always current, exact and predictable
- **Cons:** blind to renames and synonyms — searching "auth" won't find `verify_credentials`

### 2. Embeddings / RAG

Chunk the repo, embed each chunk, retrieve by vector similarity at query time. Cursor's older codebase indexer, Copilot Workspace.

- **Pros:** finds semantically related code without exact keyword overlap
- **Cons:** needs an index kept in sync — a stale index returns confidently wrong results

### 3. Repo maps (structural)

Parse the repo into symbols and a call/import graph; rank files by graph centrality. Aider's repo map ranks files PageRank-style and hands the model a compact, budget-capped summary of structurally important files — even ones it never searched for directly.

- **Pros:** structural context neither plain search nor embeddings give you on their own
- **Cons:** needs a parser and a build step; doesn't help find a specific string, only what matters

### A Single-File Stepping Stone: `list_definitions`

A full repo map is this week's bonus track, but the building block underneath it is small enough to build now: given one file, list every function and class it declares — with line numbers — using Python's stdlib `ast` module. No parser to install, no index to keep fresh. `build2_explore.py` (this week's second build) implements this as `list_definitions`.

This answers a specific gap `grep` leaves open: `grep "def "` finds *every* function definition line, but doesn't tell the model which ones are worth reading first, or that a 2,000-line file has exactly 6 top-level functions and the one it wants is the third. `list_definitions` gives the model that shape in one call, cheaper than reading the file:

```
grep("connection")                  → 1 match, in db/pool.py, line 412
list_definitions("db/pool.py")      → [{"kind": "class", "name": "ConnectionPool", "line": 380, "end_line": 460},
                                        {"kind": "method", "name": "acquire", "line": 401, "end_line": 420},
                                        {"kind": "method", "name": "release", "line": 422, "end_line": 430}, ...]
                                     → now the model knows line 412 is inside ConnectionPool.acquire
                                       without reading the other 80 lines of the class
```

Run the same idea across every file in a repo, weight each definition by how often it's referenced elsewhere, and you've rebuilt the core of Aider's repo map — that's exactly the bonus challenge.

| Question shape | Best fit |
|---|---|
| "Where is the string `DATABASE_URL` used?" | grep-first |
| "Where is something like authentication handled?" (no exact term known) | embeddings, or grep several likely synonyms |
| "What are the most important files to understand first?" | repo map |

**grep-first (via `run_command` or a bespoke tool) is the required baseline this week.** Repo maps are this week's bonus track (see the README) if you want to go further.

---

## The Search-Then-Read(-Then-Fix) Workflow

```
1. run_command("git log --oneline -5")        → orient: what's this repo, recent activity
2. run_command("grep -rn resolve_path .")     → find candidate files + line numbers
3. read_file(file, start_line=line-10,        → read the match in context,
             read_lines=30)                      not the whole file
4. (repeat as needed; check off a todo item per finding)
5. if the task calls for a fix: edit_file or run_command to make the change,
   then run_command to re-run tests and verify it (Lesson 4)
6. answer, citing file:line — and the verification command's exit code if you fixed something
```

The failure mode to design against: the agent defaulting to reading files top to bottom because that's the tool it's most comfortable with from Week 3. This is a tool-description problem from the original Week 4 plan — `grep`/`run_command`'s description should say *use this before read_file when you don't already know which file you need*.

---

## Things to Think About

- **grep is precise but dumb.** Zero results often means "wrong keyword," not "doesn't exist." Should the tool description nudge the model to try a broader or alternate term before reporting absence?

- **Line numbers are the glue.** Search output and `read_file`'s `start_line` need to share a coordinate system (1-indexed lines), or the agent constantly reads the wrong window.

- **Don't let a cap hide the truth.** If results are truncated at 50 of 4,000 matches, say so — otherwise the model will confidently report "there are 50 usages."

- **What if you don't know what you're looking for?**: Maybe feeding just the classes, functions and constants declared in each file can be useful. Check out the first and second link below. You'll be building your own ast tool in build 2.

---

## Further Reading

- Aider's repo map — <https://aider.chat/docs/repomap.html>, and the deeper build writeup at <https://aider.chat/2023/10/22/repomap.html> (tree-sitter tags + PageRank, the multi-language version of `list_definitions`)
- Python's ast module: <https://medium.com/@wshanshan/intro-to-python-ast-module-bbd22cd505f7>
- Aider's `repomap.py` source — <https://github.com/Aider-AI/aider/blob/main/aider/repomap.py> — what the real implementation looks like once you go past one file
- ripgrep — <https://github.com/BurntSushi/ripgrep> — what most production agents shell out to
- Python `ast` module — <https://docs.python.org/3/library/ast.html> — `FunctionDef`/`ClassDef`/`lineno`/`end_lineno`, everything `list_definitions` needs

**Next:** [4_editing_and_verification.md](4_editing_and_verification.md)
