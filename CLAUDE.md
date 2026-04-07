# Harness

Agentic AI framework using the OpenAI-compatible client library. Works with local models (Ollama) and cloud APIs (OpenAI). Two interfaces: terminal REPL and web UI.

## Project Structure

- `main.py` — Terminal REPL entry point
- `server.py` — FastAPI + WebSocket entry point for web UI
- `agent.py` — Core agent loop, yields events via generator pattern
- `config.py` — `load_config()` for env vars, all path constants
- `memory/` — `Conversation` class with JSON persistence, `TaskStore` for task tracking
- `prompts/` — System prompt templating with memory injection
- `tools/` — Auto-discovered tools sandboxed to `.workspace/`
- `utils/` — Enums (`Role`, `Status`), I/O formatting, logging setup
- `tests/` — pytest suite for tools, config, and tasks
- `frontend/` — Vite + React + TypeScript + Tailwind web UI

## Tools

Auto-discovered from `tools/`. Drop a `Tool` subclass in and it registers.

- `calculate` — Basic arithmetic
- `read_file` / `write_file` — File ops in `.workspace/`
- `run_shell` — Allowlisted shell commands
- `python_eval` — Unrestricted Python execution (local use only)
- `web_search` — Google search via ddgs library
- `read_url` — Fetch and extract text from any URL
- `get_current_time` — Current date/time
- `plan_task` / `update_task` / `list_tasks` — Task planning and tracking
- `save_memory` / `read_memory` — Persistent agent memory

## Running

### Terminal REPL
```bash
python main.py
```

### Web UI (development)
```bash
python run_dev.py                            # backend (port 8000, auto-reload)
cd frontend && npm run dev                   # frontend (port 5173, proxies to 8000)
```

### Web UI (production)
```bash
cd frontend && npm run build                 # outputs to static/
uvicorn server:app                           # serves everything
```

## Dependencies

Managed via `pyproject.toml`. Requires a `.env` file with `MODEL`, `BASE_URL`, and `API_KEY`.

```bash
pip install .            # runtime deps (includes fastapi, uvicorn)
pip install ".[agent]"   # + pandas, numpy, matplotlib, requests, bs4
pip install ".[dev]"     # + ruff, pytest
cd frontend && npm install  # frontend deps
```

## Formatting & Testing

### Backend
```bash
ruff format .           # format
ruff check .            # lint
ruff check . --fix      # lint + autofix
pytest tests/ -v        # run tests
```

### Frontend
```bash
cd frontend
npx prettier --write "src/**/*.{ts,tsx,css}"  # format
```
