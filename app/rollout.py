def evaluate_rollout(
    blue_p95_ms: float,
    green_p95_ms: float,
    blue_error_rate: float,
    green_error_rate: float,
    slo_p95_ms: float,
    error_budget: float,
    green_health_pass_rate: float,
    min_health_pass_rate: float = 0.99,
    window_minutes: int = 10,
    green_stable_minutes: int = 0,
    canary_regression_pct: float = 20.0,
) -> dict:
    # Health check gate
    if green_health_pass_rate < min_health_pass_rate:
        return {
            "cutover_allowed": False,
            "decision": "rollback",
            "slo_breach": False,
            "reason": f"green health pass {green_health_pass_rate} below minimum {min_health_pass_rate}",
        }
    # SLO breach gate
    if green_p95_ms > slo_p95_ms or green_error_rate > error_budget:
        parts = []
        if green_p95_ms > slo_p95_ms:
            parts.append(f"green p95 {green_p95_ms}ms exceeds SLO {slo_p95_ms}ms")
        if green_error_rate > error_budget:
            parts.append(f"green error {green_error_rate} exceeds budget {error_budget}")
        return {
            "cutover_allowed": False,
            "decision": "hold",
            "slo_breach": True,
            "reason": "; ".join(parts),
        }
    # Canary regression vs blue
    if blue_p95_ms > 0 and green_p95_ms > blue_p95_ms * (1 + canary_regression_pct / 100.0):
        return {
            "cutover_allowed": False,
            "decision": "hold",
            "slo_breach": False,
            "reason": f"canary regression: green p95 {green_p95_ms}ms exceeds blue {blue_p95_ms}ms by >{canary_regression_pct}%",
        }
    if blue_error_rate >= 0 and green_error_rate > blue_error_rate + 0.01:
        return {
            "cutover_allowed": False,
            "decision": "hold",
            "slo_breach": False,
            "reason": f"canary error regression: green error {green_error_rate} vs blue {blue_error_rate}",
        }
    # Window gate
    if green_stable_minutes < window_minutes:
        return {
            "cutover_allowed": False,
            "decision": "hold",
            "slo_breach": False,
            "reason": f"green stable {green_stable_minutes}min < required window {window_minutes}min",
        }
    return {
        "cutover_allowed": True,
        "decision": "promote",
        "slo_breach": False,
        "reason": "green within SLO for full window; cutover allowed",
    }
