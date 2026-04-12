import pytest

from harness.config import load_config


def test_missing_env_vars_exits(monkeypatch):
    monkeypatch.setattr("harness.config.load_dotenv", lambda: None)
    monkeypatch.delenv("MODEL", raising=False)
    monkeypatch.delenv("BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    with pytest.raises(SystemExit):
        load_config()
