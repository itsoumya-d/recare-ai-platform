from app.autoscale import evaluate_autoscale


def test_autoscale_hold_steady_state():
    r = evaluate_autoscale(5, p95_latency_ms=300, queue_depth=100, error_rate=0.001,
                           slo_p95_ms=500, error_budget=0.01)
    assert r["action"] == "hold"
    assert r["alert"] is False


def test_autoscale_queue_spike_scales_up():
    r = evaluate_autoscale(2, p95_latency_ms=200, queue_depth=1000, error_rate=0.001,
                           slo_p95_ms=500, error_budget=0.01)
    assert r["action"] == "scale_up"
    assert r["desired_replicas"] == 3


def test_autoscale_latency_pressure_scales_up():
    r = evaluate_autoscale(3, p95_latency_ms=450, queue_depth=10, error_rate=0.001,
                           slo_p95_ms=500, error_budget=0.01)
    assert r["action"] == "scale_up"


def test_autoscale_slo_guard_holds_scaledown():
    r = evaluate_autoscale(5, p95_latency_ms=900, queue_depth=0, error_rate=0.001,
                           slo_p95_ms=500, error_budget=0.01)
    assert r["action"] == "hold"
    assert r["alert"] is True


def test_autoscale_error_budget_guard():
    r = evaluate_autoscale(5, p95_latency_ms=100, queue_depth=0, error_rate=0.05,
                           slo_p95_ms=500, error_budget=0.01)
    assert r["action"] == "hold"
    assert r["alert"] is True


def test_autoscale_scale_down_allowed():
    r = evaluate_autoscale(5, p95_latency_ms=100, queue_depth=10, error_rate=0.001,
                           slo_p95_ms=500, error_budget=0.01,
                           seconds_since_last_scale=9999, cooldown_seconds=60)
    assert r["action"] == "scale_down"
    assert r["desired_replicas"] == 4


def test_autoscale_keda_cooldown_holds():
    r = evaluate_autoscale(5, p95_latency_ms=100, queue_depth=10, error_rate=0.001,
                           slo_p95_ms=500, error_budget=0.01,
                           seconds_since_last_scale=10, cooldown_seconds=60)
    assert r["action"] == "hold"
    assert "cooldown" in r["reason"].lower()


def test_autoscale_max_replicas_cap():
    r = evaluate_autoscale(20, p95_latency_ms=200, queue_depth=100000, error_rate=0.001,
                           slo_p95_ms=500, error_budget=0.01, max_replicas=20)
    assert r["desired_replicas"] <= 20
