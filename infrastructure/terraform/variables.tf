# Terraform Variables for CELEC Flow Prediction Infrastructure

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "celec-flow-prediction"
}

# Networking Variables
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_count" {
  description = "Number of public subnets"
  type        = number
  default     = 2
  
  validation {
    condition     = var.public_subnet_count >= 2 && var.public_subnet_count <= 6
    error_message = "Public subnet count must be between 2 and 6."
  }
}

variable "private_subnet_count" {
  description = "Number of private subnets"
  type        = number
  default     = 2
  
  validation {
    condition     = var.private_subnet_count >= 2 && var.private_subnet_count <= 6
    error_message = "Private subnet count must be between 2 and 6."
  }
}

# Database Variables
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "mlflow"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
  default     = "mlflow-password-2025"
  
  validation {
    condition     = length(var.db_password) >= 8
    error_message = "Database password must be at least 8 characters long."
  }
}

# Application Variables
variable "app_port" {
  description = "Port for application"
  type        = number
  default     = 5000
}

variable "jupyter_port" {
  description = "Port for Jupyter notebook"
  type        = number
  default     = 8888
}

# Compute Variables
variable "ecs_cpu" {
  description = "CPU units for ECS tasks (256, 512, 1024, etc.)"
  type        = number
  default     = 512
  
  validation {
    condition = contains([
      256, 512, 1024, 2048, 4096
    ], var.ecs_cpu)
    error_message = "ECS CPU must be a valid Fargate CPU value."
  }
}

variable "ecs_memory" {
  description = "Memory for ECS tasks in MB"
  type        = number
  default     = 1024
  
  validation {
    condition = var.ecs_memory >= 512 && var.ecs_memory <= 30720
    error_message = "ECS memory must be between 512 and 30720 MB."
  }
}

variable "desired_count" {
  description = "Desired number of ECS service instances"
  type        = number
  default     = 1
}

# Monitoring Variables
variable "log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 7
  
  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.log_retention_days)
    error_message = "Log retention days must be a valid CloudWatch retention period."
  }
}

# Backup Variables
variable "backup_retention_period" {
  description = "RDS backup retention period in days"
  type        = number
  default     = 7
  
  validation {
    condition     = var.backup_retention_period >= 0 && var.backup_retention_period <= 35
    error_message = "Backup retention period must be between 0 and 35 days."
  }
}

# Auto Scaling Variables
variable "min_capacity" {
  description = "Minimum number of ECS service instances"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of ECS service instances"
  type        = number
  default     = 5
}

variable "scale_up_threshold" {
  description = "CPU utilization threshold for scaling up"
  type        = number
  default     = 70
}

variable "scale_down_threshold" {
  description = "CPU utilization threshold for scaling down"
  type        = number
  default     = 30
}

# Data Variables
variable "enable_data_pipeline" {
  description = "Enable automated data pipeline"
  type        = bool
  default     = true
}

variable "data_pipeline_schedule" {
  description = "Cron expression for data pipeline schedule"
  type        = string
  default     = "0 2 * * ? *"  # Daily at 2 AM
}

# Security Variables
variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Restrict this in production
}

variable "enable_ssl" {
  description = "Enable SSL/TLS termination at load balancer"
  type        = bool
  default     = false
}

variable "ssl_certificate_arn" {
  description = "ARN of SSL certificate for HTTPS"
  type        = string
  default     = ""
}

# Feature Flags
variable "enable_monitoring" {
  description = "Enable detailed monitoring and alerting"
  type        = bool
  default     = true
}

variable "enable_auto_scaling" {
  description = "Enable auto scaling for ECS service"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default = {
    DataClassification = "Internal"
    Compliance         = "Required"
    BackupRequired     = "Yes"
  }
}