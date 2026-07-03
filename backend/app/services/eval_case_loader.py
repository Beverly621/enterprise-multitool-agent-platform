from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EVAL_DIR = Path(__file__).resolve().parents[1] / "evals"

CASE_FILES = {
    "rag": "rag_eval_cases.jsonl",
    "sql-guardrails": "sql_guardrails_eval_cases.jsonl",
    "tool": "tool_eval_cases.jsonl",
    "agent": "agent_eval_cases.jsonl",
    "regression": "regression_cases.jsonl",
}


def load_eval_cases(eval_type: str) -> list[dict[str, Any]]:
    filename = CASE_FILES[eval_type]
    path = EVAL_DIR / filename
    cases: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                cases.append(json.loads(stripped))
    return cases
