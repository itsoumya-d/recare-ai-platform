# Recare AI Platform (Reference)

[![CI](https://github.com/itsoumya-d/recare-ai-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/itsoumya-d/recare-ai-platform/actions/workflows/ci.yml)

Simulation/reference implementation of an AWS/EKS AI platform control plane for
**Recare Deutschland GmbH** — Senior Forward Deployed Platform Engineer role-fit.

## Role fit

- **Recare AI platform:** capacity planning for GPU inference fleets.
- **AWS / EKS / SageMaker:** EKS HPA + KEDA ScaledObject manifests, SageMaker
  blue/green endpoint config generation (text templates only).
- **Capacity & autoscaling:** `replicas = ceil(target_throughput / capacity_per_replica)`
  with headroom %, GPU memory constraints, GPU scheduling + fragmentation checks.
- **Blue/green rollout:** canary evaluation (blue vs green p95/error, health pass
  rate, SLO window) gating cutover.
- **Observability SLO guard:** OTel-style span aggregation, Datadog-style burn-rate
  alerting.

## Architecture

```
app/
  main.py          FastAPI endpoints (/health, /capacity/plan, /autoscale/evaluate,
                   /rollout/evaluate, /observability/slo)
  models.py        pydantic request/response schemas
  capacity.py      capacity planning + GPU scheduling on EKS nodes
  autoscale.py     HPA/KEDA scale decision with SLO guard + cooldown
  rollout.py       SageMaker blue/green canary evaluation
  observability.py OTel span aggregation + SLO burn-rate check
  k8s.py           HPA / KEDA ScaledObject / SageMaker + Terraform text templates
tests/             pytest suite (happy path + GPU OOM, queue spike, canary breach,
                   KEDA cooldown, SLO burn, fragmentation)
```

## Quickstart

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest -q
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## API examples

```bash
curl -s localhost:8000/health

curl -s -X POST localhost:8000/capacity/plan -H 'content-type: application/json' -d '{
  "target_throughput_rps": 100, "capacity_per_replica_rps": 50,
  "headroom_pct": 20, "gpu_memory_gb_per_replica": 16,
  "gpu_memory_gb_per_node": 80
}'

curl -s -X POST localhost:8000/autoscale/evaluate -H 'content-type: application/json' -d '{
  "current_replicas": 2, "p95_latency_ms": 200, "queue_depth": 1000,
  "error_rate": 0.001, "slo_p95_ms": 500, "error_budget": 0.01
}'

curl -s -X POST localhost:8000/rollout/evaluate -H 'content-type: application/json' -d '{
  "blue_p95_ms": 200, "green_p95_ms": 210, "blue_error_rate": 0.001,
  "green_error_rate": 0.001, "slo_p95_ms": 500, "error_budget": 0.01,
  "green_health_pass_rate": 1.0, "green_stable_minutes": 15
}'

curl -s -X POST localhost:8000/observability/slo -H 'content-type: application/json' -d '{
  "total_requests": 10000, "error_count": 50, "slo_target": 0.99
}'
```

## Boundaries

Reference implementation only. **No live AWS/EKS calls, no real credentials,
synthetic metrics, no production traffic.** Manifests are generated as text
templates for review. Not affiliated with Recare Deutschland GmbH.

## License

MIT
