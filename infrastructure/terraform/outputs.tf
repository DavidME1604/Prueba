# Terraform Outputs for CELEC Flow Prediction Infrastructure

# Network Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

# Load Balancer Outputs
output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "mlflow_url" {
  description = "URL to access MLflow UI"
  value       = "http://${aws_lb.main.dns_name}"
}

# Database Outputs
output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.mlflow.endpoint
  sensitive   = true
}

output "database_port" {
  description = "RDS instance port"
  value       = aws_db_instance.mlflow.port
}

# Storage Outputs
output "data_bucket_name" {
  description = "Name of the S3 data bucket"
  value       = aws_s3_bucket.data.bucket
}

output "data_bucket_arn" {
  description = "ARN of the S3 data bucket"
  value       = aws_s3_bucket.data.arn
}

output "models_bucket_name" {
  description = "Name of the S3 models bucket"
  value       = aws_s3_bucket.models.bucket
}

output "models_bucket_arn" {
  description = "ARN of the S3 models bucket"
  value       = aws_s3_bucket.models.arn
}

# Container Outputs
output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.main.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.mlflow.name
}

# Security Outputs
output "web_security_group_id" {
  description = "ID of the web security group"
  value       = aws_security_group.web.id
}

output "database_security_group_id" {
  description = "ID of the database security group"
  value       = aws_security_group.database.id
}

# IAM Outputs
output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task_role.arn
}

output "ecs_execution_role_arn" {
  description = "ARN of the ECS execution role"
  value       = aws_iam_role.ecs_execution_role.arn
}

# Monitoring Outputs
output "cloudwatch_log_group" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.main.name
}

# Connection Information
output "connection_info" {
  description = "Connection information for the deployed infrastructure"
  value = {
    mlflow_ui           = "http://${aws_lb.main.dns_name}"
    jupyter_notebook    = "http://${aws_lb.main.dns_name}:8888"
    aws_region         = var.aws_region
    environment        = var.environment
    data_bucket        = aws_s3_bucket.data.bucket
    models_bucket      = aws_s3_bucket.models.bucket
    ecr_repository     = aws_ecr_repository.main.repository_url
  }
}

# Environment Configuration
output "environment_variables" {
  description = "Environment variables for application configuration"
  value = {
    AWS_REGION                  = var.aws_region
    AWS_DEFAULT_REGION         = var.aws_region
    MLFLOW_BACKEND_STORE_URI   = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.mlflow.endpoint}:5432/mlflow"
    MLFLOW_DEFAULT_ARTIFACT_ROOT = "s3://${aws_s3_bucket.models.bucket}/mlruns"
    S3_DATA_BUCKET             = aws_s3_bucket.data.bucket
    S3_MODELS_BUCKET           = aws_s3_bucket.models.bucket
    ECR_REPOSITORY_URI         = aws_ecr_repository.main.repository_url
    ECS_CLUSTER_NAME           = aws_ecs_cluster.main.name
  }
  sensitive = true
}

# Resource Costs Estimation (informational)
output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown (USD)"
  value = {
    "ALB"                = "~$16"
    "ECS_Fargate"        = "~$15-30 (based on usage)"
    "RDS_t3_micro"       = "~$13"
    "S3_storage"         = "~$5-20 (based on data size)"
    "CloudWatch_logs"    = "~$2"
    "Data_transfer"      = "~$5-15 (based on usage)"
    "Total_estimated"    = "~$56-96/month"
    "Note"              = "Actual costs depend on usage patterns and data volume"
  }
}

# Deployment Commands
output "deployment_commands" {
  description = "Commands to deploy the application"
  value = {
    "1_docker_build"    = "docker build -t ${aws_ecr_repository.main.repository_url}:latest ."
    "2_docker_login"    = "aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.main.repository_url}"
    "3_docker_push"     = "docker push ${aws_ecr_repository.main.repository_url}:latest"
    "4_update_service"  = "aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.mlflow.name} --force-new-deployment"
  }
}