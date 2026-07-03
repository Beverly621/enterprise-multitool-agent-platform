from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


REQUIRED_FINAL_ASSETS = [
    "RELEASE_NOTES.md",
    "docs/FINAL_CHECKLIST.md",
    "docs/PROJECT_FINAL_REVIEW.md",
    "docs/FINAL_ROADMAP.md",
    "docs/FINAL_RELEASE_GUIDE.md",
    "docs/THIRD_VALIDATION_PREP.md",
    "scripts/final_public_safety_check.sh",
    "scripts/final_repo_check.sh",
    "scripts/final_smoke_test.sh",
    "readme/12-README.md",
    "test/12-test-result.md",
]


def test_stage12_final_assets_exist() -> None:
    missing = [path for path in REQUIRED_FINAL_ASSETS if not (ROOT / path).is_file()]
    assert missing == []


def test_release_notes_do_not_claim_production_deployment() -> None:
    content = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8").lower()
    forbidden_claims = [
        "real customer",
        "production users",
        "large-scale production",
        "真实客户",
        "真实用户",
        "大规模上线",
    ]
    offenders = [claim for claim in forbidden_claims if claim in content]
    assert offenders == []


def test_final_docs_reference_third_validation() -> None:
    checklist = (ROOT / "docs/FINAL_CHECKLIST.md").read_text(encoding="utf-8")
    prep = (ROOT / "docs/THIRD_VALIDATION_PREP.md").read_text(encoding="utf-8")
    assert "03-test.md" in checklist
    assert "03-test.md" in prep
