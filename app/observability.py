def aggregate_metrics(spans: list[dict]) -> dict:
    """OTel-style aggregation of span dicts with keys: latency_ms, error(bool)."""
    if not spans:
        return {"count": 0, "error_rate": 0.0, "p95_ms": 0.0, "p50_ms": 0.0}
    latencies = sorted(s.get("latency_ms", 0) for s in spans)
    errors = sum(1 for s in spans if s.get("error"))
    n = len(latencies)
    p95 = latencies[min(n - 1, int(0.95 * n))]
    p50 = latencies[min(n - 1, int(0.50 * n))]
    return {
        "count": n,
        "error_rate": errors / n,
        "p95_ms": float(p95),
        "p50_ms": float(p50),
    }


def check_slo(
    total_requests: int,
    error_count: int,
    slo_target: float = 0.99,
    burn_rate_threshold: float = 2.0,
    p95_latency_ms: float = 0,
    slo_p95_ms: float = 500,
) -> dict:
    if total_requests <= 0:
        raise ValueError("total_requests must be positive")
    if error_count < 0 or error_count > total_requests:
        raise ValueError("error_count must be between 0 and total_requests")
    if not 0 < slo_target < 1:
        raise ValueError("slo_target must be in (0,1)")
    error_rate = error_count / total_requests
    allowed_error_rate = 1 - slo_target
    burn_rate = error_rate / allowed_error_rate if allowed_error_rate > 0 else 0.0
    latency_breach = p95_latency_ms > slo_p95_ms
    slo_met = error_rate <= allowed_error_rate and not latency_breach
    alert = burn_rate > burn_rate_threshold or latency_breach
    if alert and burn_rate > burn_rate_threshold:
        reason = f"SLO burn rate {burn_rate:.2f}x exceeds threshold {burn_rate_threshold}x"
    elif latency_breach:
        reason = f"p95 latency {p95_latency_ms}ms exceeds SLO {slo_p95_ms}ms"
    elif slo_met:
        reason = "SLO met"
    else:
        reason = f"error rate {error_rate:.4f} exceeds allowed {allowed_error_rate:.4f}"
    return {
        "error_rate": error_rate,
        "allowed_error_rate": allowed_error_rate,
        "burn_rate": burn_rate,
        "slo_met": slo_met,
        "alert": alert,
        "reason": reason,
    }
