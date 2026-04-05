# Harness

Agentic AI chatbot framework using the OpenAI-compatible client library (currently targeting a local Ollama instance).

## Project Structure

- `main.py` — Entry point, REPL loop
- `agent.py` — Core agent loop (LLM calls, tool dispatch)
- `config.py` — Loads environment config from `.env`
- `memory/` — Conversation history management
- `prompts/` — Prompt templates (system prompt in `system.txt`)
- `tools/` — Extensible tool system (abstract base + implementations)
- `utils/` — Shared utilities (file loading, I/O formatting, enums)

## Running

```bash
python main.py
```

## Dependencies

Managed via `pyproject.toml`. Requires a `.env` file with `MODEL`, `BASE_URL`, and `API_KEY`.

```bash
pip install .            # runtime deps
pip install ".[dev]"     # + ruff
```

## Formatting

```bash
ruff format .    # format all files
ruff check .     # lint
ruff check . --fix  # lint + autofix
```
