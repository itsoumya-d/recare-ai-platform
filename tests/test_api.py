from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_capacity_endpoint():
    r = client.post("/capacity/plan", json={
        "target_throughput_rps": 100,
        "capacity_per_replica_rps": 50,
        "gpu_memory_gb_per_replica": 16,
        "gpu_memory_gb_per_node": 80,
    })
    assert r.status_code == 200


def test_autoscale_endpoint():
    r = client.post("/autoscale/evaluate", json={
        "current_replicas": 2,
        "p95_latency_ms": 200,
        "queue_depth": 1000,
        "error_rate": 0.001,
        "slo_p95_ms": 500,
        "error_budget": 0.01,
    })
    assert r.status_code == 200
    assert r.json()["action"] == "scale_up"


def test_rollout_endpoint():
    r = client.post("/rollout/evaluate", json={
        "blue_p95_ms": 200,
        "green_p95_ms": 210,
        "blue_error_rate": 0.001,
        "green_error_rate": 0.001,
        "slo_p95_ms": 500,
        "error_budget": 0.01,
        "green_health_pass_rate": 1.0,
        "green_stable_minutes": 15,
    })
    assert r.status_code == 200
    assert r.json()["cutover_allowed"] is True


def test_slo_endpoint():
    r = client.post("/observability/slo", json={
        "total_requests": 10000,
        "error_count": 10,
    })
    assert r.status_code == 200
