def evaluate_autoscale(
    current_replicas: int,
    p95_latency_ms: float,
    queue_depth: int,
    error_rate: float,
    slo_p95_ms: float,
    error_budget: float,
    min_replicas: int = 1,
    max_replicas: int = 20,
    queue_per_replica_threshold: int = 100,
    seconds_since_last_scale: int = 9999,
    cooldown_seconds: int = 60,
) -> dict:
    # SLO guard has priority: hold scale-down
    if p95_latency_ms > slo_p95_ms or error_rate > error_budget:
        breach = []
        if p95_latency_ms > slo_p95_ms:
            breach.append("p95 latency exceeds SLO")
        if error_rate > error_budget:
            breach.append("error rate exceeds error budget")
        return {
            "action": "hold",
            "desired_replicas": current_replicas,
            "alert": True,
            "reason": "SLO guard: " + "; ".join(breach) + "; scale-down held",
        }

    # Queue spike -> scale up (even inside cooldown for scale-up safety)
    queue_threshold = current_replicas * queue_per_replica_threshold
    if queue_depth > queue_threshold:
        desired = min(current_replicas + 1, max_replicas)
        if desired == current_replicas:
            return {
                "action": "hold",
                "desired_replicas": current_replicas,
                "alert": True,
                "reason": "queue spike but already at max_replicas",
            }
        return {
            "action": "scale_up",
            "desired_replicas": desired,
            "alert": False,
            "reason": f"queue_depth {queue_depth} exceeds threshold {queue_threshold}",
        }

    # Latency pressure -> scale up
    if p95_latency_ms > 0.8 * slo_p95_ms:
        desired = min(current_replicas + 1, max_replicas)
        if desired == current_replicas:
            return {
                "action": "hold",
                "desired_replicas": current_replicas,
                "alert": False,
                "reason": "latency pressure but already at max_replicas",
            }
        return {
            "action": "scale_up",
            "desired_replicas": desired,
            "alert": False,
            "reason": f"p95 {p95_latency_ms}ms above 80% of SLO {slo_p95_ms}ms",
        }

    # Scale-down candidate: low latency + shallow queue
    if p95_latency_ms < 0.5 * slo_p95_ms and queue_depth < 0.5 * queue_threshold:
        if seconds_since_last_scale < cooldown_seconds:
            return {
                "action": "hold",
                "desired_replicas": current_replicas,
                "alert": False,
                "reason": f"KEDA/HPA cooldown active: {seconds_since_last_scale}s < {cooldown_seconds}s",
            }
        desired = max(current_replicas - 1, min_replicas)
        if desired == current_replicas:
            return {
                "action": "hold",
                "desired_replicas": current_replicas,
                "alert": False,
                "reason": "already at min_replicas",
            }
        return {
            "action": "scale_down",
            "desired_replicas": desired,
            "alert": False,
            "reason": "low latency and shallow queue; scale-down allowed",
        }

    return {
        "action": "hold",
        "desired_replicas": current_replicas,
        "alert": False,
        "reason": "within steady-state bounds; hold",
    }
