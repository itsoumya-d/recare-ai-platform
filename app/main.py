from fastapi import FastAPI

from app import autoscale, capacity, observability, rollout
from app.models import (
    AutoscaleDecisionResponse,
    AutoscaleEvaluateRequest,
    CapacityPlanRequest,
    CapacityPlanResponse,
    GpuSchedulingRequest,
    GpuSchedulingResponse,
    RolloutEvaluateRequest,
    RolloutEvaluateResponse,
    SloCheckRequest,
    SloCheckResponse,
)

app = FastAPI(title="Recare AI Platform Control Plane (Reference)", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "recare-ai-platform"}


@app.post("/capacity/plan", response_model=CapacityPlanResponse)
def plan(req: CapacityPlanRequest):
    return capacity.plan_capacity(
        target_throughput_rps=req.target_throughput_rps,
        capacity_per_replica_rps=req.capacity_per_replica_rps,
        headroom_pct=req.headroom_pct,
        gpu_memory_gb_per_replica=req.gpu_memory_gb_per_replica,
        gpu_memory_gb_per_node=req.gpu_memory_gb_per_node,
        max_replicas=req.max_replicas,
    )


@app.post("/capacity/gpu-schedule", response_model=GpuSchedulingResponse)
def gpu_schedule(req: GpuSchedulingRequest):
    return capacity.check_gpu_scheduling(req.node_gpu_counts, req.gpu_requests)


@app.post("/autoscale/evaluate", response_model=AutoscaleDecisionResponse)
def evaluate(req: AutoscaleEvaluateRequest):
    return autoscale.evaluate_autoscale(
        current_replicas=req.current_replicas,
        p95_latency_ms=req.p95_latency_ms,
        queue_depth=req.queue_depth,
        error_rate=req.error_rate,
        slo_p95_ms=req.slo_p95_ms,
        error_budget=req.error_budget,
        min_replicas=req.min_replicas,
        max_replicas=req.max_replicas,
        queue_per_replica_threshold=req.queue_per_replica_threshold,
        seconds_since_last_scale=req.seconds_since_last_scale,
        cooldown_seconds=req.cooldown_seconds,
    )


@app.post("/rollout/evaluate", response_model=RolloutEvaluateResponse)
def rollout_evaluate(req: RolloutEvaluateRequest):
    return rollout.evaluate_rollout(
        blue_p95_ms=req.blue_p95_ms,
        green_p95_ms=req.green_p95_ms,
        blue_error_rate=req.blue_error_rate,
        green_error_rate=req.green_error_rate,
        slo_p95_ms=req.slo_p95_ms,
        error_budget=req.error_budget,
        green_health_pass_rate=req.green_health_pass_rate,
        min_health_pass_rate=req.min_health_pass_rate,
        window_minutes=req.window_minutes,
        green_stable_minutes=req.green_stable_minutes,
        canary_regression_pct=req.canary_regression_pct,
    )


@app.post("/observability/slo", response_model=SloCheckResponse)
def slo(req: SloCheckRequest):
    return observability.check_slo(
        total_requests=req.total_requests,
        error_count=req.error_count,
        slo_target=req.slo_target,
        burn_rate_threshold=req.burn_rate_threshold,
        p95_latency_ms=req.p95_latency_ms,
        slo_p95_ms=req.slo_p95_ms,
    )
