#!/bin/bash
# CELEC Flow Prediction - Deployment Script
# Automated deployment to AWS using Infrastructure as Code

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
TERRAFORM_DIR="$PROJECT_ROOT/infrastructure/terraform"

# Default values
ENVIRONMENT="staging"
AWS_REGION="us-east-1"
PROJECT_NAME="celec-flow-prediction"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
CELEC Flow Prediction - Deployment Script

Usage: $0 [OPTIONS]

OPTIONS:
    -e, --environment   Environment to deploy (staging|prod) [default: staging]
    -r, --region       AWS region [default: us-east-1]
    -p, --project      Project name [default: celec-flow-prediction]
    -d, --destroy      Destroy infrastructure instead of creating
    -h, --help         Show this help message

EXAMPLES:
    $0                                    # Deploy to staging
    $0 -e prod                           # Deploy to production
    $0 -e staging -r us-west-2          # Deploy to staging in us-west-2
    $0 -d -e staging                     # Destroy staging environment

PREREQUISITES:
    - AWS CLI configured with appropriate permissions
    - Terraform >= 1.0 installed
    - Docker installed and running
    - Required environment variables set:
      * TF_VAR_db_password
      * AWS_ACCESS_KEY_ID (or AWS profile configured)
      * AWS_SECRET_ACCESS_KEY (or AWS profile configured)

EOF
}

# Parse command line arguments
DESTROY=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -p|--project)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -d|--destroy)
            DESTROY=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "prod" ]]; then
    log_error "Environment must be 'staging' or 'prod'"
    exit 1
fi

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        exit 1
    fi
    
    # Check required environment variables
    if [[ -z "$TF_VAR_db_password" ]]; then
        log_warning "TF_VAR_db_password not set. Using default password."
        export TF_VAR_db_password="mlflow-password-2025"
    fi
    
    log_success "Prerequisites check passed"
}

# Initialize Terraform backend
init_terraform() {
    log_info "Initializing Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Create backend configuration if it doesn't exist
    if [[ ! -f "backend.conf" ]]; then
        cat > backend.conf << EOF
bucket         = "${PROJECT_NAME}-terraform-state"
key            = "${ENVIRONMENT}/terraform.tfstate"
region         = "${AWS_REGION}"
dynamodb_table = "terraform-state-lock"
encrypt        = true
EOF
    fi
    
    # Initialize Terraform
    terraform init -backend-config=backend.conf
    
    # Select or create workspace
    terraform workspace select "$ENVIRONMENT" || terraform workspace new "$ENVIRONMENT"
    
    log_success "Terraform initialized for environment: $ENVIRONMENT"
}

# Build and push Docker image
build_and_push_docker() {
    log_info "Building and pushing Docker image..."
    
    cd "$PROJECT_ROOT"
    
    # Get ECR login token
    ECR_REGISTRY=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION}.amazonaws.com
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REGISTRY"
    
    # Build Docker image
    docker build -t "${PROJECT_NAME}:latest" .
    docker build -t "${PROJECT_NAME}:${ENVIRONMENT}" .
    
    # Tag for ECR
    docker tag "${PROJECT_NAME}:latest" "${ECR_REGISTRY}/${PROJECT_NAME}:latest"
    docker tag "${PROJECT_NAME}:${ENVIRONMENT}" "${ECR_REGISTRY}/${PROJECT_NAME}:${ENVIRONMENT}"
    
    # Push to ECR
    docker push "${ECR_REGISTRY}/${PROJECT_NAME}:latest"
    docker push "${ECR_REGISTRY}/${PROJECT_NAME}:${ENVIRONMENT}"
    
    log_success "Docker image built and pushed"
}

# Deploy infrastructure
deploy_infrastructure() {
    log_info "Deploying infrastructure..."
    
    cd "$TERRAFORM_DIR"
    
    # Set environment-specific variables
    export TF_VAR_environment="$ENVIRONMENT"
    export TF_VAR_aws_region="$AWS_REGION"
    export TF_VAR_project_name="$PROJECT_NAME"
    
    # Plan deployment
    terraform plan -out=tfplan
    
    # Confirm deployment
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        read -p "Are you sure you want to deploy to PRODUCTION? (yes/no): " -r
        if [[ ! $REPLY =~ ^yes$ ]]; then
            log_info "Deployment cancelled"
            exit 0
        fi
    fi
    
    # Apply deployment
    terraform apply tfplan
    
    # Save outputs
    terraform output -json > "${PROJECT_ROOT}/terraform-outputs-${ENVIRONMENT}.json"
    
    log_success "Infrastructure deployed successfully"
}

# Destroy infrastructure
destroy_infrastructure() {
    log_warning "Destroying infrastructure for environment: $ENVIRONMENT"
    
    cd "$TERRAFORM_DIR"
    
    # Confirm destruction
    read -p "Are you sure you want to DESTROY the $ENVIRONMENT environment? This cannot be undone. (yes/no): " -r
    if [[ ! $REPLY =~ ^yes$ ]]; then
        log_info "Destruction cancelled"
        exit 0
    fi
    
    # Set environment variables
    export TF_VAR_environment="$ENVIRONMENT"
    export TF_VAR_aws_region="$AWS_REGION"
    export TF_VAR_project_name="$PROJECT_NAME"
    
    # Destroy infrastructure
    terraform destroy -auto-approve
    
    log_success "Infrastructure destroyed"
}

# Update application
update_application() {
    log_info "Updating application..."
    
    # Force new deployment of ECS service
    aws ecs update-service \
        --cluster "${PROJECT_NAME}-cluster" \
        --service "${PROJECT_NAME}-mlflow-service" \
        --force-new-deployment \
        --region "$AWS_REGION"
    
    # Wait for deployment to stabilize
    log_info "Waiting for deployment to complete..."
    aws ecs wait services-stable \
        --cluster "${PROJECT_NAME}-cluster" \
        --services "${PROJECT_NAME}-mlflow-service" \
        --region "$AWS_REGION"
    
    log_success "Application updated"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Get load balancer DNS
    LB_DNS=$(aws elbv2 describe-load-balancers \
        --names "${PROJECT_NAME}-alb" \
        --query 'LoadBalancers[0].DNSName' \
        --output text \
        --region "$AWS_REGION")
    
    if [[ "$LB_DNS" != "None" ]]; then
        ENDPOINT="http://$LB_DNS"
        
        log_info "Testing endpoint: $ENDPOINT"
        
        # Wait for service to be ready
        for i in {1..30}; do
            if curl -f "$ENDPOINT" &> /dev/null; then
                log_success "Health check passed - Service is running"
                log_info "MLflow UI: $ENDPOINT"
                return 0
            fi
            log_info "Waiting for service to be ready... ($i/30)"
            sleep 10
        done
        
        log_warning "Health check failed - Service may still be starting"
    else
        log_warning "Could not retrieve load balancer DNS"
    fi
}

# Main execution
main() {
    log_info "Starting CELEC Flow Prediction deployment"
    log_info "Environment: $ENVIRONMENT"
    log_info "Region: $AWS_REGION"
    log_info "Project: $PROJECT_NAME"
    echo
    
    check_prerequisites
    
    if [[ "$DESTROY" == "true" ]]; then
        init_terraform
        destroy_infrastructure
    else
        init_terraform
        build_and_push_docker
        deploy_infrastructure
        update_application
        health_check
        
        log_success "Deployment completed successfully!"
        echo
        log_info "Next steps:"
        log_info "1. Check the MLflow UI at the endpoint shown above"
        log_info "2. Review the infrastructure in the AWS console"
        log_info "3. Monitor logs in CloudWatch"
        echo
        log_info "To destroy this environment later, run:"
        log_info "$0 -d -e $ENVIRONMENT"
    fi
}

# Run main function
main "$@"