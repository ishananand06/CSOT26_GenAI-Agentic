# Lesson 2: Connecting to MCP Servers — With Authentication

## Where This Came From

You met MCP in Week 2: the "USB for AI tools" standard that decouples a tool from the agent using it. Back then you connected to AlphaXiv.

The moment a tool touches something valuable — your GitHub repos, a production database, a paid API — the server can't just let anyone in. It needs to know *who's calling* and whether they're allowed. That's authentication, and it's the piece Week 2 skipped. This lesson fills it in, because in the real world almost every MCP server worth connecting to is behind a key.

First, a bit of how the protocol got here, because it explains the code you're about to write.

### The transport, briefly

MCP messages are just JSON-RPC. What changed over time is *how* those messages travel — the **transport**:

- **stdio** — the client launches the server as a subprocess and talks over stdin/stdout. Great for local tools (the server runs on your machine). No network, so authentication is mostly moot — if you can launch the process, you're trusted.
- **HTTP+SSE** (what Week 2's `sse_client` used) — the server is a remote process you connect to over HTTP, using Server-Sent Events to stream messages back. This is where "remote" — and therefore "who are you?" — enters the picture.
- **Streamable HTTP** (the current transport, 2025) — **replaced** HTTP+SSE. A single HTTP endpoint (e.g. `https://api.example.com/mcp`) that handles both POST and GET, optionally streaming with SSE when needed. Simpler to host, and the one new servers use.

You'll still see `sse_client` in older tutorials and older servers; it works, it's just deprecated. New code should reach for the **Streamable HTTP** client. The good news: from your agent's side, the connection code is nearly identical to Week 2 — same "connect, list tools, convert schemas, run the loop, forward tool calls" shape. The only genuinely new thing is **how the key gets attached.**

---

## How Authentication Actually Works

An MCP server over HTTP is just a web server. Web servers authenticate requests the way they always have: with an **HTTP header**. When you connect, you attach a header carrying your credential, and every request in that session carries it along. The two forms you'll see:

```
Authorization: Bearer <your-token>      # by far the most common
X-API-Key: <your-token>                 # some servers use a custom header instead
```

The key does not go in the URL, in a tool argument, or in the message body — it rides in the header, set once when you open the connection. The Python MCP SDK's clients take a `headers` dict for exactly this:

```python
headers = {"Authorization": f"Bearer {os.environ['GITHUB_PAT']}"}
```

The MCP spec also defines a complete **OAuth 2.1** flow for servers that want browser-based login and scoped, expiring tokens. That's what powers "click to connect your Google account" in polished products. It's heavier than we need. For now, we'll just use the **API-key-in-a-header** path. If you go on to build something public-facing, OAuth is the next step; the header is still where the resulting token ends up.

And because it's a secret sitting in a header, everything from **Week 1** applies unchanged: the key lives in `.env`, appears in `.env.example` only as a placeholder, and never touches source code or a committed config file.

## The Goal: A Config-Driven Loader

It's tempting to write a `connect_to_github()` function with the URL and the header baked in. It'll work — and then the next server means a second near-identical function, and a third, and your agent's source now knows the name of every service it talks to. That's exactly the hardcoding trap Lesson 3 is about.

So we won't do that. Your agent will read a **`config.json`** listing the servers it should connect to, and connect to *whatever is in that file* — GitHub, a database, a filesystem server, one you wrote yourself — without a single line of server-specific code. Adding a server becomes editing a data file, not editing Python. GitHub below is just the first entry in that file.

This is the real format, too: `config.json` mirrors the `mcpServers` block that Claude Desktop, Cursor, and other clients already use, so anything you learn here transfers.

### The config file

```json
{
  "mcpServers": {
    "github": {
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": { "Authorization": "Bearer ${GITHUB_PAT}" }
    },
    "some-other-server": {
      "url": "https://example.com/mcp",
      "headers": { "X-API-Key": "${SOME_API_KEY}" }
    }
  }
}
```

Two things to notice:

- Each server is **just data**: a name, a `url`, and whatever `headers` it needs. Different servers use different header names (`Authorization` vs. `X-API-Key`) — the config captures that difference so your code doesn't have to.
- The keys are **not in the file.** `${GITHUB_PAT}` is a placeholder your loader substitutes from the environment at load time. So `config.json` is safe to commit; the secret still lives only in `.env`.

### One example entry: getting a GitHub token

To make the `github` entry above actually connect, you need a token — this is the "authenticated server" part made concrete. GitHub publishes an official [remote MCP server](https://github.com/github/github-mcp-server) at `https://api.githubcopilot.com/mcp/`, exposing tools for issues, PRs, and repo contents, authenticated with a **fine-grained Personal Access Token** as a Bearer token:

1. GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token.
2. Give it access to a repo or two, read scopes to start. Least privilege — don't hand it your whole account for a demo.
3. Put the token in `.env` (and a placeholder in `.env.example`):

That's the *only* GitHub-specific thing you do — set an env var. Everything from here is generic.

### A quick note on `async`/`await`

The code below has `async`, `await`, and `AsyncExitStack` in it, which may be new. It centers around one idea: **network calls involve waiting, and Python's MCP SDK is written to wait efficiently.**

- A function defined with `async def` is a **coroutine** — calling it doesn't run it, it hands you something you must `await`.
- `await something()` means "start this, and pause here until it finishes." Talking to an MCP server is a network round-trip, so `initialize()`, `list_tools()`, and `call_tool()` are all `await`ed.
- `asyncio.run(main())` is the single entry point that actually kicks the whole thing off. You call it *once*, at the top.
- `async with` is just `with` for a resource whose setup/teardown needs to wait (like opening and closing a network connection).

That's the whole vocabulary you need. Why can't we just write plain synchronous code? Because **the MCP SDK only ships an async client** — there is no sync version to call. The good news: this agent does one thing at a time, so there's no real concurrency to reason about. It's ordinary top-to-bottom code with `await` marking the handful of spots that talk to the network. If you've seen JavaScript's `async`/`await`, it's the same model.

> If you'd rather keep your Week 4 agent loop fully synchronous, you *can* hide the async in a background thread and expose plain `mcp.call_tool(...)` methods — but that adds a thread and cross-thread plumbing to remove a few keywords. For a single-user CLI agent it's not worth it; embracing the `await`s is simpler than working around them.

### The loader

Read the config, substitute env vars, connect to every server, and merge their tools. Because you may hold several sessions open at once, use an `AsyncExitStack` to manage their lifetimes cleanly — it's a single object you register each connection with, and one `aclose()` call tears them all down in reverse order (the runtime-flexible version of nesting many `async with` blocks when you don't know how many servers the config has).

```python
import asyncio
import json
import os
import re
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from openai import OpenAI

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

load_dotenv()

openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)


def load_mcp_config(path="config.json"):
    """Read config.json and substitute ${ENV_VAR} references from the environment."""
    raw = open(path).read()

    def substitute(match):
        var = match.group(1)
        value = os.environ.get(var)
        if value is None:
            raise RuntimeError(f"config.json references ${{{var}}}, but it isn't set in your .env")
        return value

    resolved = re.sub(r"\$\{([A-Z0-9_]+)\}", substitute, raw)
    return json.loads(resolved)["mcpServers"]


class MCPManager:
    """Connects to every server in the config and exposes their tools as one flat list."""

    def __init__(self):
        self.stack = AsyncExitStack()
        self.openai_tools = []          # merged tool schemas, for the model
        self.tool_to_session = {}       # tool name -> the session that owns it

    async def connect_all(self, servers: dict):
        for name, cfg in servers.items():
            # streamablehttp_client yields THREE values (the third is a session-id callback).
            read, write, _ = await self.stack.enter_async_context(
                streamablehttp_client(cfg["url"], headers=cfg.get("headers"))
            )
            session = await self.stack.enter_async_context(ClientSession(read, write))
            await session.initialize()

            tools = await session.list_tools()
            for tool in tools.tools:
                self.tool_to_session[tool.name] = session
                self.openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                })
            print(f"connected '{name}': {len(tools.tools)} tools")

    async def call_tool(self, name: str, args: dict) -> str:
        result = await self.tool_to_session[name].call_tool(name, args)
        return result.content[0].text if result.content else ""

    async def aclose(self):
        await self.stack.aclose()
```

Notice there is **no mention of GitHub anywhere in this code.** It connects to whatever `config.json` lists.

### The agent loop

Merge the MCP tools with your Week 4 local tools into one list, and route each tool call to the right place — a remote server if the name came from MCP, otherwise your local Python function.

That `tool_to_session` dict is the whole trick for keeping local and remote tools in one loop: it's how the dispatcher knows a tool call named `create_issue` goes to GitHub while `run_command` stays home.

Note that multiple MCPs might have tools with the same name, how will you deal with that? (Hint: `github.create_pr`, not `create_pr`)

---

## Two Things Worth Pausing On

- **Trust boundary.** Every argument your agent sends to a remote MCP server, that server sees. A GitHub server seeing repo names is fine; a server seeing the contents of a private file you fetched is a decision, not a default. Connecting a third-party MCP server is granting it a seat at the table — know what crosses that line.
- **Tool-list bloat.** The GitHub server alone exposes dozens of tools. Connect three servers and you've dumped a hundred tool schemas into every request — token cost and a harder decision for the model. Real clients filter or paginate; at minimum, only connect the servers a given session actually needs. But how do you decide that?

---

## Bonus: Per-Session MCP Toggles

The loader above connects to *every* server in `config.json` at startup. Better: treat `config.json` as the list of servers your agent *knows about*, and let the user choose which are actually *connected* in the current session. This solves the tool-list-bloat problem interactively — connect the database server only for the session where you need it.

Add REPL commands (parsed before you hand input to the model, the same way you handled `/reset` or `/sessions` in earlier weeks):

```
/mcp list                 → show every server in config.json and whether it's connected
/mcp enable github        → connect that server now, merge its tools into the loop
/mcp disable github       → close its session, drop its tools from the list
```

You already have every piece — you're just calling `MCPManager`'s parts on demand instead of all at once:

- `/mcp list` reads `load_mcp_config()` and prints each name, marking which are currently in `tool_to_session`.
- `/mcp enable <name>` runs the same connect logic as `connect_all`, but for one server, and adds its tools to the live `all_tools` list.
- `/mcp disable <name>` closes that one server's session and removes its tools from both `all_tools` and `tool_to_session`.

The set of active servers becomes runtime state driven by the config file — the exact "configuration as code" idea the next lesson names.

---

## Further Reading

- MCP transports (Streamable HTTP) — <https://modelcontextprotocol.io/docs/concepts/transports>
- MCP authorization spec (the full OAuth story) — <https://modelcontextprotocol.io/specification>
- GitHub MCP server — <https://github.com/github/github-mcp-server>
- MCP server registry (find more to connect) — <https://github.com/modelcontextprotocol/servers>
- Python MCP SDK — <https://github.com/modelcontextprotocol/python-sdk>
- Revisit: Week 2 Lesson 3 (MCP basics) and Week 1 (key hygiene)

**Next:** [3_config_as_code.md](3_config_as_code.md) — the idea underneath both skills and MCP.
