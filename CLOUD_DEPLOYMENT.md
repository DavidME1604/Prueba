# CELEC Flow Prediction - Cloud Deployment Guide

This project is fully containerized and deployable to AWS using Infrastructure as Code (IaC) with Terraform.

## 🏗️ Infrastructure Overview

### Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Internet      │    │  Application     │    │   Database      │
│   Gateway       │────│  Load Balancer   │────│   (RDS)         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ECS Fargate                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   MLflow UI     │  │   Data Pipeline │  │   Jupyter       │ │
│  │   Container     │  │   Container     │  │   Container     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        S3 Storage                               │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │   Raw Data      │  │   Model         │                      │
│  │   Bucket        │  │   Artifacts     │                      │
│  └─────────────────┘  └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### Components
- **VPC**: Isolated network with public/private subnets
- **ALB**: Application Load Balancer for traffic distribution
- **ECS Fargate**: Serverless container orchestration
- **RDS PostgreSQL**: Managed database for MLflow backend
- **S3**: Object storage for data and model artifacts
- **ECR**: Container registry for Docker images
- **CloudWatch**: Monitoring and logging

## 🚀 Quick Start

### Prerequisites
```bash
# Install required tools
# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip && sudo mv terraform /usr/local/bin/

# Docker
sudo apt-get update && sudo apt-get install docker.io
sudo usermod -aG docker $USER
```

### Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Key, and preferred region
```

### Deploy to Cloud
```bash
# 1. Clone and setup
git clone https://github.com/carol230/CELEC_forecast.git
cd CELEC_forecast

# 2. Set required environment variables
export TF_VAR_db_password="your-secure-password-here"

# 3. Deploy to staging
./scripts/deployment/deploy.sh -e staging

# 4. Deploy to production
./scripts/deployment/deploy.sh -e prod
```

## 🐳 Docker Deployment

### Local Development
```bash
# Start all services locally
docker-compose up -d

# Access services
# MLflow UI: http://localhost:5000
# Jupyter: http://localhost:8888 (token: celec-flow-2025)

# Development mode with Jupyter
docker-compose --profile development up -d

# Production mode with scheduler
docker-compose --profile production up -d
```

### Build and Test
```bash
# Build production image
docker build -t celec-flow-prediction:latest .

# Test the image
docker run --rm celec-flow-prediction:latest python test_environment.py

# Run model training
docker run --rm -v $(pwd)/data:/app/data -v $(pwd)/models:/app/models \
    celec-flow-prediction:latest python src/models/data_analysis.py
```

## ☁️ AWS Deployment

### Infrastructure as Code (Terraform)

#### 1. Backend Setup (One-time)
```bash
# Create S3 bucket for Terraform state
aws s3 mb s3://celec-terraform-state --region us-east-1

# Create DynamoDB table for state locking
aws dynamodb create-table \
    --table-name terraform-state-lock \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-1
```

#### 2. Environment Configuration
```bash
# Copy example variables
cp infrastructure/terraform/terraform.tfvars.example infrastructure/terraform/terraform.tfvars

# Edit variables for your deployment
nano infrastructure/terraform/terraform.tfvars
```

#### 3. Deploy Infrastructure
```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply (with confirmation)
terraform apply

# Save outputs
terraform output -json > ../../terraform-outputs.json
```

#### 4. Deploy Application
```bash
# Get ECR repository URL from Terraform outputs
ECR_REPO=$(terraform output -raw ecr_repository_url)

# Build and push Docker image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO
docker build -t $ECR_REPO:latest .
docker push $ECR_REPO:latest

# Update ECS service
aws ecs update-service \
    --cluster celec-flow-prediction-cluster \
    --service celec-flow-prediction-mlflow-service \
    --force-new-deployment
```

## 📊 Monitoring and Operations

### Access Services
```bash
# Get service endpoints from Terraform outputs
terraform output connection_info

# Example outputs:
# MLflow UI: http://alb-dns-name.us-east-1.elb.amazonaws.com
# S3 Data Bucket: celec-flow-prediction-data-12345678
# S3 Models Bucket: celec-flow-prediction-models-12345678
```

### Monitoring
```bash
# View ECS service status
aws ecs describe-services \
    --cluster celec-flow-prediction-cluster \
    --services celec-flow-prediction-mlflow-service

# View logs
aws logs tail /ecs/celec-flow-prediction --follow

# Check application health
curl -f http://your-alb-dns/health
```

### Scaling
```bash
# Scale ECS service
aws ecs update-service \
    --cluster celec-flow-prediction-cluster \
    --service celec-flow-prediction-mlflow-service \
    --desired-count 3

# Enable auto-scaling (already configured in Terraform)
# Based on CPU utilization: scale up at 70%, scale down at 30%
```

## 🔐 Security

### Network Security
- VPC with public/private subnets
- Security groups with least privilege access
- ALB with SSL termination (configurable)
- Database in private subnets only

### Data Security
- S3 buckets with versioning and encryption
- RDS with encryption at rest
- Secure container images with vulnerability scanning
- IAM roles with minimal required permissions

### Access Control
```bash
# Create read-only user for data scientists
aws iam create-user --user-name celec-data-scientist

# Attach policy for S3 read access
aws iam attach-user-policy \
    --user-name celec-data-scientist \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

## 💰 Cost Optimization

### Estimated Monthly Costs
- **ALB**: ~$16/month
- **ECS Fargate**: ~$15-30/month (based on usage)
- **RDS t3.micro**: ~$13/month
- **S3 Storage**: ~$5-20/month (based on data size)
- **CloudWatch**: ~$2/month
- **Data Transfer**: ~$5-15/month
- **Total**: ~$56-96/month

### Cost Optimization Tips
```bash
# Use Spot instances for development
# Schedule ECS tasks to scale down during off-hours
# Configure S3 lifecycle policies
# Use CloudWatch to monitor and optimize resource usage

# Example: Schedule scale-down at night
aws events put-rule \
    --name scale-down-night \
    --schedule-expression "cron(0 22 * * ? *)"
```

## 🚨 Troubleshooting

### Common Issues

#### ECS Service Won't Start
```bash
# Check service events
aws ecs describe-services \
    --cluster celec-flow-prediction-cluster \
    --services celec-flow-prediction-mlflow-service \
    --query 'services[0].events'

# Check task definition
aws ecs describe-task-definition \
    --task-definition celec-flow-prediction-mlflow
```

#### Database Connection Issues
```bash
# Test database connectivity
aws rds describe-db-instances \
    --db-instance-identifier celec-flow-prediction-mlflow-db

# Check security groups
aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=celec-flow-prediction-db-sg"
```

#### MLflow UI Not Accessible
```bash
# Check ALB target health
aws elbv2 describe-target-health \
    --target-group-arn $(aws elbv2 describe-target-groups \
        --names celec-flow-prediction-mlflow-tg \
        --query 'TargetGroups[0].TargetGroupArn' --output text)
```

## 🔄 CI/CD Pipeline

### GitHub Actions
The project includes a complete CI/CD pipeline:

1. **Code Quality**: Linting, formatting, security checks
2. **Testing**: Unit tests, integration tests
3. **Infrastructure**: Terraform validation and planning
4. **Security**: Docker image vulnerability scanning
5. **Deployment**: Automated deployment to staging/production
6. **Monitoring**: Post-deployment health checks

### Required Secrets
Set these in your GitHub repository settings:
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
DB_PASSWORD
```

## 🧹 Cleanup

### Destroy Infrastructure
```bash
# Using deployment script
./scripts/deployment/deploy.sh -d -e staging
./scripts/deployment/deploy.sh -d -e prod

# Or manually with Terraform
cd infrastructure/terraform
terraform destroy -auto-approve
```

### Remove Docker Resources
```bash
# Stop all containers
docker-compose down

# Remove images
docker rmi celec-flow-prediction:latest

# Clean up Docker system
docker system prune -a
```

## 📞 Support

For deployment issues or questions:
1. Check the troubleshooting section above
2. Review CloudWatch logs
3. Verify AWS permissions and quotas
4. Open an issue in the GitHub repository

## 🔗 Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [MLflow Deployment Guide](https://mlflow.org/docs/latest/deployment.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)