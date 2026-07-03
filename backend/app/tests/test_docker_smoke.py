from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_docker_smoke_script_documents_required_flow() -> None:
    script = ROOT / "scripts" / "docker_smoke_test.sh"
    content = script.read_text()

    assert "docker compose down -v" in content
    assert "docker compose up -d --build" in content
    assert "/health" in content
    assert "/api/agent/chat" in content
