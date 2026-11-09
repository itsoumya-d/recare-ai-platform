import math


def plan_capacity(
    target_throughput_rps: float,
    capacity_per_replica_rps: float,
    headroom_pct: float = 20.0,
    gpu_memory_gb_per_replica: float = 16.0,
    gpu_memory_gb_per_node: float = 80.0,
    max_replicas: int = 100,
) -> dict:
    if target_throughput_rps <= 0 or capacity_per_replica_rps <= 0:
        raise ValueError("throughput must be positive")
    headroom_multiplier = 1 + headroom_pct / 100.0
    required_rps = target_throughput_rps * headroom_multiplier
    replicas_needed = math.ceil(required_rps / capacity_per_replica_rps)
    total_capacity = replicas_needed * capacity_per_replica_rps
    gpu_memory_required = replicas_needed * gpu_memory_gb_per_replica
    gpu_nodes_needed = math.ceil(gpu_memory_required / gpu_memory_gb_per_node)

    # GPU OOM: a single replica cannot fit on one node
    if gpu_memory_gb_per_replica > gpu_memory_gb_per_node:
        return {
            "replicas_needed": replicas_needed,
            "total_capacity_rps": total_capacity,
            "headroom_applied_pct": headroom_pct,
            "gpu_memory_required_gb": gpu_memory_required,
            "gpu_nodes_needed": gpu_nodes_needed,
            "oom_risk": True,
            "feasible": False,
            "reason": "GPU OOM: per-replica GPU memory exceeds per-node GPU memory",
        }

    if replicas_needed > max_replicas:
        return {
            "replicas_needed": replicas_needed,
            "total_capacity_rps": total_capacity,
            "headroom_applied_pct": headroom_pct,
            "gpu_memory_required_gb": gpu_memory_required,
            "gpu_nodes_needed": gpu_nodes_needed,
            "oom_risk": False,
            "feasible": False,
            "reason": f"replicas_needed {replicas_needed} exceeds max_replicas {max_replicas}",
        }

    return {
        "replicas_needed": replicas_needed,
        "total_capacity_rps": total_capacity,
        "headroom_applied_pct": headroom_pct,
        "gpu_memory_required_gb": gpu_memory_required,
        "gpu_nodes_needed": gpu_nodes_needed,
        "oom_risk": False,
        "feasible": True,
        "reason": "capacity plan feasible",
    }


def check_gpu_scheduling(node_gpu_counts: list[int], gpu_requests: list[int]) -> dict:
    if any(n < 0 for n in node_gpu_counts) or any(r < 0 for r in gpu_requests):
        raise ValueError("GPU counts must be non-negative")
    total_gpu = sum(node_gpu_counts)
    total_requested = sum(gpu_requests)
    if total_requested > total_gpu:
        return {
            "feasible": False,
            "nodes_used": len(node_gpu_counts),
            "fragmentation_pct": 0.0,
            "reason": f"insufficient GPU capacity: requested {total_requested} > available {total_gpu}",
        }
    # greedy bin-pack: count fragmented nodes
    remaining = sorted(node_gpu_counts, reverse=True)
    nodes_used = 0
    for req in sorted(gpu_requests, reverse=True):
        placed = False
        for i, cap in enumerate(remaining):
            if cap >= req:
                remaining[i] = cap - req
                nodes_used += 1
                placed = True
                break
        if not placed:
            return {
                "feasible": False,
                "nodes_used": nodes_used,
                "fragmentation_pct": 0.0,
                "reason": "GPU request cannot fit on any single node (fragmentation)",
            }
    leftover = sum(remaining)
    fragmentation = (leftover / total_gpu * 100.0) if total_gpu else 0.0
    return {
        "feasible": True,
        "nodes_used": nodes_used,
        "fragmentation_pct": fragmentation,
        "reason": "GPU scheduling feasible",
    }
