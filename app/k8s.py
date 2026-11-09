"""Terraform / Kubernetes manifest generation (text templates, no live cloud calls)."""


def hpa_manifest(
    name: str = "recare-ai-hpa",
    deployment: str = "recare-ai-inference",
    min_replicas: int = 1,
    max_replicas: int = 20,
    target_cpu_pct: int = 70,
    target_memory_pct: int = 80,
) -> str:
    return f"""apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {name}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {deployment}
  minReplicas: {min_replicas}
  maxReplicas: {max_replicas}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {target_cpu_pct}
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: {target_memory_pct}
"""


def keda_scaledobject(
    name: str = "recare-ai-scaledobject",
    deployment: str = "recare-ai-inference",
    queue_name: str = "recare-inference-queue",
    max_replicas: int = 20,
    polling_interval: int = 15,
    cooldown_period: int = 60,
) -> str:
    return f"""apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: {name}
spec:
  scaleTargetRef:
    name: {deployment}
  pollingInterval: {polling_interval}
  cooldownPeriod: {cooldown_period}
  minReplicaCount: 1
  maxReplicaCount: {max_replicas}
  triggers:
  - type: aws-sqs-queue
    metadata:
      queueURL: https://sqs.eu-central-1.amazonaws.com/000000000000/{queue_name}
      queueLength: '100'
      awsRegion: eu-central-1
"""


def sagemaker_endpoint_config(
    name: str = "recare-ai-green",
    instance_type: str = "ml.g5.xlarge",
    instance_count: int = 2,
    image_uri: str = "000000000000.dkr.ecr.eu-central-1.amazonaws.com/recare-ai-inference:latest",
) -> str:
    return f"""resource "aws_sagemaker_endpoint_configuration" "{name}" {{
  name = "{name}-config"
  production_variants {{
    variant_name = "AllTraffic"
    model_name = aws_sagemaker_model.recare_ai.name
    initial_instance_count = {instance_count}
    instance_type = "{instance_type}"
    initial_variant_weight = 1
  }}
}}

# blue/green: green variant {name} on {instance_type} x{instance_count}
# image: {image_uri}
"""


def terraform_eks_hpa_fragment(cluster_name: str = "recare-ai-eks") -> str:
    return f"""# Terraform fragment (reference, no live apply)
resource "aws_eks_cluster" "recare_ai" {{
  name = "{cluster_name}"
  role_arn = aws_iam_role.eks_cluster.arn
  version = "1.29"
  vpc_config {{
    subnet_ids = var.subnet_ids
  }}
}}

resource "kubernetes_horizontal_pod_autoscaler_v2" "recare_ai" {{
  metadata {{
    name = "recare-ai-hpa"
  }}
  spec {{
    scale_target_ref {{
      api_version = "apps/v1"
      kind = "Deployment"
      name = "recare-ai-inference"
    }}
    min_replicas = 1
    max_replicas = 20
  }}
}}
"""
