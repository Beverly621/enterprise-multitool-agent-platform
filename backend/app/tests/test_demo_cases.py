from pathlib import Path


def _repo_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "data").exists() and (candidate / "docs").exists():
            return candidate
    workspace = Path("/workspace")
    if (workspace / "data").exists() and (workspace / "docs").exists():
        return workspace
    return Path(__file__).resolve().parents[3]


REPO_ROOT = _repo_root()


def test_demo_cases_cover_second_milestone_flows() -> None:
    content = (REPO_ROOT / "docs" / "DEMO_CASES.md").read_text(encoding="utf-8")

    required_markers = [
        "GENERAL_CHAT",
        "RAG_QA",
        "SQL_QUERY",
        "TOOL_CALL",
        "MULTI_STEP_REPORT",
        "Async Report",
        "SQL Guardrails",
    ]
    for marker in required_markers:
        assert marker in content

    assert "NEED_APPROVAL" in content or (
        "Human Approval" in content and "WAITING_APPROVAL" in content
    )


def test_demo_guide_references_real_demo_entrypoints() -> None:
    content = (REPO_ROOT / "docs" / "DEMO_GUIDE.md").read_text(encoding="utf-8")

    required_markers = [
        "docker compose up -d --build",
        "bash scripts/seed_demo_data.sh",
        "admin@example.com",
        "data/demo_docs/sample_company_policy.md",
        "结合最近 30 天订单异常数据和售后知识库生成一份分析报告",
        "scripts/check_public_safety.sh",
    ]
    for marker in required_markers:
        assert marker in content
