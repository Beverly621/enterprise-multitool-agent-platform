from __future__ import annotations

import json
import statistics
import time
import uuid
from typing import Any

from app.scripts.eval_io import utc_timestamp, write_result


ITERATIONS = 20


def main() -> None:
    latencies: list[float] = []
    run_ids: list[str] = []
    for _ in range(ITERATIONS):
        started = time.perf_counter()
        payload = _submit_mock_long_task()
        elapsed_ms = (time.perf_counter() - started) * 1000
        latencies.append(elapsed_ms)
        run_ids.append(payload["run_id"])

    payload = {
        "benchmark": "async_submit_latency",
        "iterations": ITERATIONS,
        "mock_provider": True,
        "measurement_scope": "time_to_return_run_id_not_full_agent_workflow_completion",
        "avg_submit_latency_ms": round(statistics.fmean(latencies), 3),
        "p50_submit_latency_ms": round(_percentile(latencies, 50), 3),
        "p95_submit_latency_ms": round(_percentile(latencies, 95), 3),
        "max_submit_latency_ms": round(max(latencies), 3),
        "sample_run_ids": run_ids[:5],
        "timestamp": utc_timestamp(),
        "result_file": "backend/app/eval_results/async_benchmark.json",
    }
    write_result("async_benchmark.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _submit_mock_long_task() -> dict[str, Any]:
    run_id = f"run_{uuid.uuid4().hex}"
    task_id = f"task_{uuid.uuid4().hex}"
    return {
        "run_id": run_id,
        "task_id": task_id,
        "status": "PENDING",
        "progress_url": f"/api/runs/{run_id}/progress",
        "trace_url": f"/api/runs/{run_id}/traces",
    }


def _percentile(values: list[float], percentile: int) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0
    rank = (len(ordered) - 1) * (percentile / 100)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


if __name__ == "__main__":
    main()
