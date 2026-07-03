import importlib.util
from pathlib import Path


def _load_check_env():
    path = Path(__file__).resolve().parents[2] / "scripts" / "check_env.py"
    spec = importlib.util.spec_from_file_location("check_env", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


check_env = _load_check_env()


def _set_required(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://agent:agent@postgres:5432/db")
    monkeypatch.setenv("REDIS_URL", "redis://redis:6379/0")
    monkeypatch.setenv("JWT_SECRET_KEY", "change-me-to-a-long-random-secret")
    monkeypatch.setenv("DEFAULT_LLM_PROVIDER", "mock")
    monkeypatch.setenv("DEFAULT_EMBEDDING_PROVIDER", "mock")


def test_mock_provider_mode_allows_missing_real_api_keys(monkeypatch) -> None:
    _set_required(monkeypatch)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert check_env.main() == 0


def test_real_provider_mode_requires_matching_key(monkeypatch) -> None:
    _set_required(monkeypatch)
    monkeypatch.setenv("DEFAULT_LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert check_env.main() == 1
