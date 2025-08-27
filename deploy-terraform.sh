
#!/bin/bash

# Deploy Photos OpenHand using Terraform
# Usage: ./deploy-terraform.sh [environment] [region]

set -e

# Default values
ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}

echo "🚀 Deploying Photos OpenHand with Terraform"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform is not installed. Please install Terraform first."
    echo "   Visit: https://www.terraform.io/downloads.html"
    exit 1
fi

# Check if AWS CLI is installed and configured
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install AWS CLI first."
    echo "   Visit: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Navigate to terraform directory
cd terraform

# Create terraform.tfvars if it doesn't exist
if [ ! -f terraform.tfvars ]; then
    echo "📝 Creating terraform.tfvars from example..."
    cp terraform.tfvars.example terraform.tfvars
    
    # Update with provided values
    sed -i.bak "s/environment = \"dev\"/environment = \"$ENVIRONMENT\"/" terraform.tfvars
    sed -i.bak "s/aws_region = \"us-east-1\"/aws_region = \"$REGION\"/" terraform.tfvars
    rm terraform.tfvars.bak
    
    echo "✅ Created terraform.tfvars with environment=$ENVIRONMENT and region=$REGION"
    echo "   You can edit terraform.tfvars to customize other settings"
    echo ""
fi

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Validate configuration
echo "🔍 Validating Terraform configuration..."
terraform validate

# Plan deployment
echo "📋 Planning deployment..."
terraform plan -var="environment=$ENVIRONMENT" -var="aws_region=$REGION"

# Ask for confirmation
echo ""
read -p "🤔 Do you want to proceed with the deployment? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Deploying infrastructure..."
    terraform apply -var="environment=$ENVIRONMENT" -var="aws_region=$REGION" -auto-approve
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "📋 Deployment Summary:"
    echo "====================="
    terraform output
    
    echo ""
    echo "🌐 Your application is ready!"
    echo "Frontend URL: $(terraform output -raw frontend_url)"
    echo ""
    echo "💡 Next steps:"
    echo "1. Visit the frontend URL to access your picture gallery"
    echo "2. Upload some pictures to test the functionality"
    echo "3. Check CloudWatch logs if you encounter any issues"
    echo ""
    echo "📊 Monitor your application:"
    echo "- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#logsV2:log-groups"
    echo "- S3 Bucket: https://console.aws.amazon.com/s3/home?region=$REGION"
    echo "- Lambda Functions: https://console.aws.amazon.com/lambda/home?region=$REGION#/functions"
    
else
    echo "❌ Deployment cancelled"
    exit 1
fi

