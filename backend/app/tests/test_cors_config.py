from app.main import _cors_origins
from app.core.config import settings


def test_cors_includes_frontend_origin(monkeypatch) -> None:
    monkeypatch.setattr(settings, "frontend_origin", "https://frontend.example.com")
    monkeypatch.setattr(settings, "environment", "staging")

    assert "https://frontend.example.com" in _cors_origins()


def test_prod_cors_removes_unsafe_wildcard(monkeypatch) -> None:
    monkeypatch.setattr(settings, "frontend_origin", "https://frontend.example.com")
    monkeypatch.setattr(settings, "cors_origins", ["*"])
    monkeypatch.setattr(settings, "environment", "prod")

    assert "*" not in _cors_origins()
