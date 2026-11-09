from app.k8s import hpa_manifest, keda_scaledobject, sagemaker_endpoint_config


def test_hpa_manifest_contains_bounds():
    m = hpa_manifest(max_replicas=30)
    assert "HorizontalPodAutoscaler" in m
    assert "maxReplicas: 30" in m


def test_keda_scaledobject_queue():
    m = keda_scaledobject(queue_name="my-queue")
    assert "ScaledObject" in m
    assert "my-queue" in m
    assert "keda.sh/v1alpha1" in m


def test_sagemaker_endpoint_config():
    m = sagemaker_endpoint_config(instance_type="ml.g5.xlarge", instance_count=3)
    assert "aws_sagemaker_endpoint_configuration" in m
    assert "ml.g5.xlarge" in m
