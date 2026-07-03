from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


REQUIRED_DOCS = [
    "README.md",
    "docs/RESUME_DESCRIPTION.md",
    "docs/INTERVIEW_QA.md",
    "docs/ARCHITECTURE_EXPLAIN.md",
    "docs/DEMO_SCRIPT.md",
    "docs/PROJECT_REVIEW.md",
    "docs/TECHNICAL_HIGHLIGHTS.md",
    "docs/CHALLENGES_AND_SOLUTIONS.md",
    "docs/STAR_PROJECT_STORY.md",
    "docs/SCREENSHOTS.md",
    "docs/PROJECT_FILE_MAP.md",
    "docs/ROADMAP.md",
    "docs/FINAL_PRESENTATION_GUIDE.md",
]


def test_stage11_required_docs_exist() -> None:
    missing = [path for path in REQUIRED_DOCS if not (ROOT / path).is_file()]
    assert missing == []


def test_interview_qa_has_at_least_40_questions() -> None:
    content = (ROOT / "docs/INTERVIEW_QA.md").read_text(encoding="utf-8")
    question_count = sum(1 for line in content.splitlines() if re.match(r"^\d+\. \*\*", line))
    assert question_count >= 40


def test_public_docs_do_not_include_local_absolute_paths() -> None:
    docs = [ROOT / path for path in REQUIRED_DOCS]
    forbidden = [
        "/Users/beverlykim",
        "/private/tmp/enterprise-multitool-agent-platform-stage8",
    ]
    offenders: list[str] = []
    for path in docs:
        content = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in content:
                offenders.append(f"{path.relative_to(ROOT)} contains {marker}")
    assert offenders == []
