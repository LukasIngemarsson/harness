# Harness

Agentic AI framework using the OpenAI-compatible client library (currently targeting a local Ollama instance). Two interfaces: terminal REPL and web UI.

## Project Structure

- `main.py` — Terminal REPL entry point
- `server.py` — FastAPI + WebSocket entry point for web UI
- `agent.py` — Core agent loop, yields events via generator pattern
- `config.py` — `load_config()` validates and loads env vars from `.env`
- `memory/` — `Conversation` class with JSON persistence
- `prompts/` — System prompt templating (`build_system_prompt`, `load_prompt`)
- `tools/` — Auto-discovered tools sandboxed to `.workspace/`
- `utils/` — Enums (`Role`), I/O formatting, logging setup
- `tests/` — pytest suite for tools and config
- `frontend/` — Vite + React + TypeScript + Tailwind web UI

## Running

### Terminal REPL
```bash
python main.py
```

### Web UI (development)
```bash
uvicorn server:app --reload                  # backend (port 8000)
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
