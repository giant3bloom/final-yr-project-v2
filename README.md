# NexAI

NexAI is an AI-driven optimization loop that iteratively improves a maze navigation controller using Gemini, validates changes in an isolated sandbox, and benchmarks them in the demo engine.

## Project layout

```
.
├── config.py                 # Shared paths, ports, and environment settings
├── pyproject.toml            # Package metadata and `nexai` console script
├── demo_engine/              # Isolated sandbox + Arcade benchmark (child process)
│   ├── assets/               # Maze generation, controller, GUI, metrics
│   ├── io/                   # Result storage and graph export
│   ├── output/               # Generated results, graphs, and user runs
│   ├── sandbox.py            # Headless validation (subprocess target)
│   ├── main.py               # Automated benchmark loop
│   └── user_mode.py          # Manual play mode
├── NexAI/
│   ├── __main__.py           # python -m NexAI
│   ├── runtime/              # Bootstrap + child-process managers
│   ├── optimizer/            # Optimization orchestrator
│   ├── recreator/            # Gemini-based code rewriter
│   ├── v_sandbox/            # Standalone metrics (no demo_engine imports)
│   ├── dynamic/              # Status logging, SSM, live dashboard
│   └── hardware_profiler/    # System metrics
├── requirements.txt
└── .env.example
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # add GEMINI_API_KEY
```

Run all commands from the **project root** (`final-yr-pro-ject-main/`).

## Usage (modular `-m` entry points)

**Full NexAI loop** — starts SSM status shower + sandbox + demo_engine as child processes:

```bash
python -m NexAI
python -m NexAI.optimizer
python -m NexAI.optimizer.main
```

Equivalent console script (after `pip install -e .`):

```bash
nexai
```

**Isolated demo_engine sandbox** (headless controller validation):

```bash
python -m demo_engine.sandbox
```

**Arcade benchmark** (isolated child when launched by NexAI):

```bash
python -m demo_engine
```

**SSM status dashboard** (standalone):

```bash
python -m NexAI.dynamic.status_shower
```

**Manual maze play:**

```bash
python -m demo_engine.user_mode
```

Type `exit` in the optimizer terminal to stop. The status window is spawned and destroyed automatically.

## Process isolation

| Component       | Module                         | Runs as        |
|----------------|---------------------------------|----------------|
| Status shower  | `NexAI.dynamic.status_shower`   | Child process  |
| Sandbox        | `demo_engine.sandbox`           | Child process  |
| Demo benchmark | `demo_engine`                   | Child process  |
| NexAI optimizer| `NexAI.optimizer`               | Parent process |

NexAI never imports `demo_engine` code in-process. All controller validation and Arcade runs happen in isolated subprocesses. Optional separate venv: `demo_engine/venv`.

## Notes

- Generated artifacts: `demo_engine/output/`
- Status sockets: `127.0.0.1:5050` (override via `.env`)
- Sandbox errors and demo_engine tracebacks are fed back into the next LLM prompt; `code score` is `null` on failure
"# final-yr-project-v2" 
