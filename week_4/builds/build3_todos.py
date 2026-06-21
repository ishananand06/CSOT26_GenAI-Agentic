"""
Build 3: Todo Tools
======================
A todo list the model maintains itself — what it's planning to do, what
it's actually done, and how it'll know each item really worked.

This build is intentionally less prescriptive than Builds 1 and 2. You
decide the exact shape of a todo and how the list is stored — in memory,
in a dict, in a JSON file under .agent/, however you like. The one hard
requirement, from Lesson 2: every todo needs a short title, a
description, and a verification method — some concrete, checkable way
to know the item is actually done ("run pytest tests/test_auth.py and
confirm exit code 0"), not just a status flag the model sets on its own
say-so.

Tasks (design these yourself — the signatures below are a starting
point, not a contract you have to match):
  1. add_todos(...)  — add one or more todos to the list
  2. get_todos(...)  — return the current list, however you choose to
     filter or shape it
  3. mark_todo(...)  — update a todo's status
  4. Once you've settled on a shape, write the TOOLS schema yourself
     and wire it into the agent loop's stop condition (Lesson 2) — the
     loop shouldn't consider itself done while a todo is incomplete.

Questions to resolve before you write code — there's no single right
answer, but you should be able to defend whatever you pick:
  - What does "status" need to express? pending/in_progress/completed
    is Lesson 2's minimum — is that enough once verification enters
    the picture, or do you need something like "blocked" too?
  - Should mark_todo require evidence (e.g. a command's exit code)
    before it'll accept "completed," and refuse otherwise? Lesson 2's
    "Completed Should Mean Verified, Not Just Claimed" argues yes —
    decide how strict to make that in code.
  - Where does the list live, and what survives a resumed session
    (Week 3)? A module-level list won't survive a process restart;
    is that good enough for this build, or do you need it on disk?
  - Should add_todos take one todo or a whole plan at once? (Lesson 2's
    todo_write always sends the full current list back — you don't
    have to copy that design, but know why it might matter.)

Run directly once you've implemented something real: add a couple of
todos, mark one in_progress, try to mark it completed without evidence
and see whether your own rules let that happen, then get_todos() and
confirm the list reflects what you'd expect.
"""

# TODO: pick your own storage. A plain list/dict at module scope is fine
# to start; revisit once you decide whether todos need to survive a
# resumed session.

# implement the following: add_todos, get_todos, mark_todo


# TODO: once the functions above have a settled shape, write the TOOLS
# schema for add_todos / get_todos / mark_todo yourself. Lesson 6 has
# the guidance on what makes a tool description the model actually
# follows — apply it here instead of copying Lesson 2's example verbatim.
TOOLS = []


if __name__ == "__main__":
    # TODO: exercise add_todos / get_todos / mark_todo once they're real,
    # including the case where you try to mark something completed
    # without evidence — does your code stop you, or let it through?
    pass
