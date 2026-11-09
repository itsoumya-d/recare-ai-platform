from app.rollout import evaluate_rollout


def _base(**kw):
    d = dict(blue_p95_ms=200, green_p95_ms=210, blue_error_rate=0.001,
             green_error_rate=0.001, slo_p95_ms=500, error_budget=0.01,
             green_health_pass_rate=1.0, min_health_pass_rate=0.99,
             window_minutes=10, green_stable_minutes=15)
    d.update(kw)
    return d


def test_rollout_promote_when_green_healthy():
    r = evaluate_rollout(**_base())
    assert r["cutover_allowed"] is True
    assert r["decision"] == "promote"


def test_rollout_canary_breach_p95():
    r = evaluate_rollout(**_base(green_p95_ms=600))
    assert r["cutover_allowed"] is False
    assert r["slo_breach"] is True


def test_rollout_canary_breach_error():
    r = evaluate_rollout(**_base(green_error_rate=0.05))
    assert r["cutover_allowed"] is False
    assert r["slo_breach"] is True


def test_rollout_health_gate_rollback():
    r = evaluate_rollout(**_base(green_health_pass_rate=0.5))
    assert r["decision"] == "rollback"
    assert r["cutover_allowed"] is False


def test_rollout_window_not_met():
    r = evaluate_rollout(**_base(green_stable_minutes=3))
    assert r["cutover_allowed"] is False
    assert r["decision"] == "hold"


def test_rollout_canary_regression_vs_blue():
    r = evaluate_rollout(**_base(blue_p95_ms=100, green_p95_ms=200))
    assert r["cutover_allowed"] is False
