import pytest

from app.observability import aggregate_metrics, check_slo


def test_slo_met_low_errors():
    r = check_slo(10000, 10, slo_target=0.99)
    assert r["slo_met"] is True
    assert r["alert"] is False


def test_slo_burn_alert():
    # 5% errors vs 1% allowed -> burn 5x
    r = check_slo(1000, 50, slo_target=0.99, burn_rate_threshold=2.0)
    assert r["alert"] is True
    assert r["slo_met"] is False
    assert r["burn_rate"] > 2.0


def test_slo_latency_breach_alert():
    r = check_slo(1000, 1, p95_latency_ms=900, slo_p95_ms=500)
    assert r["alert"] is True
    assert r["slo_met"] is False


def test_slo_invalid_inputs():
    with pytest.raises(ValueError):
        check_slo(0, 0)
    with pytest.raises(ValueError):
        check_slo(100, 200)


def test_aggregate_metrics_empty():
    r = aggregate_metrics([])
    assert r["count"] == 0


def test_aggregate_metrics_p95():
    spans = [{"latency_ms": i * 10, "error": i == 0} for i in range(1, 101)]
    r = aggregate_metrics(spans)
    assert r["count"] == 100
    assert r["p95_ms"] == 960
