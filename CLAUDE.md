# Harness

Agentic AI chatbot framework using the OpenAI-compatible client library (currently targeting a local Ollama instance).

## Project Structure

- `main.py` — Entry point, REPL loop, config/conversation init
- `agent.py` — Core agent loop with streaming, tool dispatch via `create_agent` factory
- `config.py` — `load_config()` loads and validates env vars from `.env`
- `memory/` — `Conversation` class with persistence (`history.json`)
- `prompts/` — Prompt templates loaded via `importlib.resources`
- `tools/` — Auto-discovered tool system (drop a `Tool` subclass in, it registers)
- `utils/` — Enums (`Role`), I/O formatting (`role_prefix`, `error_msg`), file loading
- `tests/` — pytest suite for tools and config

## Running

```bash
python main.py
```

## Dependencies

Managed via `pyproject.toml`. Requires a `.env` file with `MODEL`, `BASE_URL`, and `API_KEY`.

```bash
pip install .            # runtime deps
pip install ".[dev]"     # + ruff, pytest
```

## Formatting & Testing

```bash
ruff format .           # format
ruff check .            # lint
ruff check . --fix      # lint + autofix
pytest tests/ -v        # run tests
```
