from pydantic import BaseModel, Field


class CapacityPlanRequest(BaseModel):
    target_throughput_rps: float = Field(gt=0)
    capacity_per_replica_rps: float = Field(gt=0)
    headroom_pct: float = Field(default=20.0, ge=0, le=200)
    gpu_memory_gb_per_replica: float = Field(gt=0)
    gpu_memory_gb_per_node: float = Field(gt=0)
    max_replicas: int = Field(default=100, gt=0)


class CapacityPlanResponse(BaseModel):
    replicas_needed: int
    total_capacity_rps: float
    headroom_applied_pct: float
    gpu_memory_required_gb: float
    gpu_nodes_needed: int
    oom_risk: bool
    feasible: bool
    reason: str


class GpuSchedulingRequest(BaseModel):
    node_gpu_counts: list[int] = Field(min_length=1)
    gpu_requests: list[int] = Field(min_length=1)


class GpuSchedulingResponse(BaseModel):
    feasible: bool
    nodes_used: int
    fragmentation_pct: float
    reason: str


class AutoscaleEvaluateRequest(BaseModel):
    current_replicas: int = Field(ge=1)
    p95_latency_ms: float = Field(ge=0)
    queue_depth: int = Field(ge=0)
    error_rate: float = Field(ge=0, le=1)
    slo_p95_ms: float = Field(gt=0)
    error_budget: float = Field(ge=0, le=1)
    min_replicas: int = Field(default=1, ge=1)
    max_replicas: int = Field(default=20, gt=0)
    queue_per_replica_threshold: int = Field(default=100, gt=0)
    seconds_since_last_scale: int = Field(default=9999, ge=0)
    cooldown_seconds: int = Field(default=60, ge=0)


class AutoscaleDecisionResponse(BaseModel):
    action: str
    desired_replicas: int
    alert: bool
    reason: str


class RolloutEvaluateRequest(BaseModel):
    blue_p95_ms: float = Field(ge=0)
    green_p95_ms: float = Field(ge=0)
    blue_error_rate: float = Field(ge=0, le=1)
    green_error_rate: float = Field(ge=0, le=1)
    slo_p95_ms: float = Field(gt=0)
    error_budget: float = Field(ge=0, le=1)
    green_health_pass_rate: float = Field(ge=0, le=1)
    min_health_pass_rate: float = Field(default=0.99, ge=0, le=1)
    window_minutes: int = Field(default=10, gt=0)
    green_stable_minutes: int = Field(ge=0)
    canary_regression_pct: float = Field(default=20.0, ge=0)


class RolloutEvaluateResponse(BaseModel):
    cutover_allowed: bool
    decision: str
    slo_breach: bool
    reason: str


class SloCheckRequest(BaseModel):
    total_requests: int = Field(gt=0)
    error_count: int = Field(ge=0)
    slo_target: float = Field(default=0.99, gt=0, lt=1)
    burn_rate_threshold: float = Field(default=2.0, gt=0)
    p95_latency_ms: float = Field(default=0, ge=0)
    slo_p95_ms: float = Field(default=500, gt=0)


class SloCheckResponse(BaseModel):
    error_rate: float
    allowed_error_rate: float
    burn_rate: float
    slo_met: bool
    alert: bool
    reason: str
