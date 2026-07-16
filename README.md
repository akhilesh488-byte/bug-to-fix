# bug-to-fix

An agentic AI workflow that debugs and fixes bugs in a target repo on its own, built to understand how a ReAct-based agent actually works end to end, not just to have a "bug fixing bot" that magically works.

## What it does

You give it a bug description, and it runs a loop where the LLM (Gemini 2.5 Flash via litellm) reasons about the problem, picks a tool, tests its fix in an isolated sandbox, and only then writes the fix back into the actual file.

## How the loop works

1. **Thought** — LLM reasons about what's going wrong and what to do next.
2. **Action** — picks a tool + input, outputs `PAUSE` and stops.
3. **Observation** — the tool (a python function) is executed, result is fed back to the LLM.
4. **Answer** — once the bug's fixed and verified, LLM gives a final summary: cause, fix, and why it works.

Steps 1-3 repeat until the LLM has enough to answer. The whole thing is wrapped in a `query()` loop so it runs on its own for up to `max_steps` iterations instead of manually stepping through it.

## Tools

**File system tools** (`tools/`)
- `scan_repo` — lists all files in `target_repo`
- `read_file` — reads a file's full content (works on `.py` and `.ipynb`)
- `write_file` — writes full content back into a file
- `execute_file` — runs a file and returns stdout (default 60s timeout, can override)

**Sandbox tools** — before touching the real file, the agent tests its fix in an isolated jupyter kernel (`notebook_sandbox.py`)
- `add_cell` — adds a code cell, returns its cell_id
- `execute_cell` — runs a cell by id, state persists across cells
- `edit_cell` — overwrites a cell's code if it errors out
- `get_sandbox_state` — dumps all cells, ids, and last outputs

**Tracking**
- `record_attempt` — logs hypothesis, what was changed, result, and why it failed (if it did), so the agent doesn't repeat a dead-end fix in the same run.

## Repo structure

```
bug-to-fix/
├── target_repo/                        # the buggy repo the agent operates on
├── tools/                               # all tool functions the agent can call
├── utils/                               # supporting utilities
├── manual_workflow_implementation.ipynb # step-by-step, no loop — for understanding each piece
├── workflow.ipynb                       # the automated version, wrapped in query()
└── requirements.txt
```

`manual_workflow_implementation.ipynb` exists separately from `workflow.ipynb` on purpose — it's the same loop done by hand, one cell at a time, before it got automated. Worth reading first if you want to see how the pieces connect.

## Setup

```bash
git clone https://github.com/akhilesh488-byte/bug-to-fix.git
cd bug-to-fix
python -m venv venv
source venv/bin/activate      # venv\Scripts\activate on windows
pip install -r requirements.txt
```

Add a `.env` file with your Gemini API key (litellm picks it up automatically):

```
GEMINI_API_KEY=your_key_here
```

Drop the buggy code into `target_repo/`, then run `workflow.ipynb` and call:

```python
query("describe the bug here")
```
