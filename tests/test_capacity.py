import pytest

from app.capacity import check_gpu_scheduling, plan_capacity


def test_capacity_happy_path():
    r = plan_capacity(100, 50, headroom_pct=20)
    # 100*1.2/50 = 2.4 -> 3 replicas
    assert r["replicas_needed"] == 3
    assert r["feasible"] is True
    assert r["oom_risk"] is False


def test_capacity_headroom_scales_replicas():
    r = plan_capacity(100, 50, headroom_pct=0)
    assert r["replicas_needed"] == 2


def test_capacity_gpu_oom():
    r = plan_capacity(10, 10, gpu_memory_gb_per_replica=90, gpu_memory_gb_per_node=80)
    assert r["oom_risk"] is True
    assert r["feasible"] is False


def test_capacity_exceeds_max_replicas():
    r = plan_capacity(10000, 10, max_replicas=5)
    assert r["feasible"] is False


def test_capacity_gpu_nodes_computed():
    r = plan_capacity(100, 50, gpu_memory_gb_per_replica=16, gpu_memory_gb_per_node=80)
    # 3 replicas * 16 = 48GB -> 1 node
    assert r["gpu_nodes_needed"] == 1


def test_capacity_invalid_throughput():
    with pytest.raises(ValueError):
        plan_capacity(0, 50)


def test_gpu_scheduling_feasible():
    r = check_gpu_scheduling([4, 4], [2, 2])
    assert r["feasible"] is True


def test_gpu_scheduling_insufficient():
    r = check_gpu_scheduling([2], [4])
    assert r["feasible"] is False


def test_gpu_scheduling_fragmentation():
    # request of 4 cannot fit on nodes of 2+2 despite total capacity
    r = check_gpu_scheduling([2, 2], [4])
    assert r["feasible"] is False
