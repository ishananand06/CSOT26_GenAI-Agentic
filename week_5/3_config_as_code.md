# Lesson 3: Configuration as Code

## Closing Reading — the idea underneath the whole week

Look back at what you just did. In Lesson 1, skills lived in a **directory** the agent scanned at startup — not a list hardcoded in `agent.py`. In Lesson 2, the MCP servers your agent connects to lived in a **`config.json`** it read at load time — deliberately *not* a `connect_to_github()` function with the URL baked in. In both cases, the *thing that varies* got pulled out of the code and into data.

That move has a name, and it's one of the oldest good habits in software.

### The problem it solves

Ask why you hardcode anything. You do it because it's the fastest way to get one specific case working. `model = "deepseek/deepseek-v4-flash:free"`. `skills = [commit_skill, review_skill]`. `if user == "me"`. It works, right up until one of these is true:

- Someone else wants to use your tool with *their* choices.
- *You* want a different choice tomorrow without editing and re-testing code.
- The choice depends on the environment — dev vs. prod, free model vs. paid, this repo vs. that one.

The instant a value needs to differ across people, time, or environment, hardcoding it stops being fast and starts being a tax you pay on every change. The fix is to treat **the things that change as data the program reads**, not as code the program *is*. Your `.env` from Week 1 was already this — you didn't hardcode your API key, you read it from the environment, precisely because it differs per person and must never be baked into source. **Configuration as code** is that same instinct, generalized to *every* choice that might reasonably vary: models, skill directories, which MCP servers exist, approval policies, timeouts.

The Pragmatic Programmer states it as a tip: **"put abstractions in code, details in metadata."** Code expresses *how* your agent works — the loop, the dispatch, the parsing. Metadata (config files, env vars, a `skills/` folder) expresses *what* this particular instance should do. Keep them apart and you can change the *what* without touching or re-testing the *how*.

### Why it matters *here*, specifically

An agent is the extreme case of software-that-must-vary. Its entire value proposition this week was *extensibility* — new procedures without code changes, new tools without code changes. Skills and MCP are configuration-as-code applied to *capabilities*:

| Hardcoded | Configuration as code |
|---|---|
| Procedures written into the system prompt | Skills discovered from a `skills/` directory |
| Tools compiled into the agent | MCP servers listed in config, connected on demand |
| API key as a string literal | Key read from `.env` |
| One user's preferences in `if` branches | An `AGENTS.md` / config file per project |

Every row is the same move: the varying part lives *outside* the logic, so the logic never has to change to accommodate a new case. That's why a mature agent can gain a capability by dropping in a file instead of shipping a new release — and it's why yours can too, now.

### The good version has guardrails

"Put it in config" isn't a license to make everything configurable — that's its own kind of mess (a program with 200 knobs nobody understands). The judgment call is the same as DRY: pull out what *genuinely varies or is genuinely secret*. And config that loads external behavior needs the same care as code, because it *is* behavior:

- **Validate on load.** A malformed `SKILL.md` or a bad server URL should fail loudly at startup with a clear message, not mysteriously mid-task.
- **Secrets stay in the environment.** Config files get committed; `.env` does not. A config file references `${GITHUB_PAT}`; it never contains the token. (Week 1, one more time.)
- **Sensible defaults.** Missing config should degrade gracefully — no `skills/` directory means zero skills, not a crash.

### You've already started — now finish the thought

Lesson 2's `config.json` was your first real config file: adding an MCP server is already editing data, not writing code. The natural extension is to notice what *else* in your agent is a hardcoded value that wants to live there too. Think about it.

---

## Things to Think About

- Where in your Week 4 agent is a value hardcoded that *should* be config? Would moving it actually help, or just add a knob? Both answers are legitimate — the skill is telling them apart.
- Config that loads and runs external things (skills, servers) is an attack surface. If your agent read a `skills/` directory from a repo it just cloned, would you trust every `SKILL.md` in it? Where's the line between convenient and dangerous?

## Further Reading

- Twelve-Factor App, Factor III: Config — <https://12factor.net/config> (the canonical "config in the environment" argument)
- Hunt & Thomas, *The Pragmatic Programmer* — the "Metadata-Driven" / configuration tips and DRY

---

That's Week 5, and the track. You started with one API call. You now have an agent that reasons in a loop, remembers, edits and verifies code, learns new procedures from files, and reaches out to tools across the internet; and you understand every layer because you built each one by hand. Go make it genuinely yours, and write the `SUBMISSION.md` that proves it.