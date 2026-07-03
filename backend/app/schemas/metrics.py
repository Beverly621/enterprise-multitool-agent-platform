from pydantic import BaseModel


class ProviderMetricsSummary(BaseModel):
    total_calls: int
    success_calls: int
    failed_calls: int
    success_rate: float
    avg_latency_ms: int
    p95_latency_ms: int
    estimated_total_cost: float


class AgentRunMetricsSummary(BaseModel):
    total: int
    success: int
    failed: int
    cancelled: int
    success_rate: float
    avg_duration_ms: int
    p95_duration_ms: int
