
















# Terraform Deployment Guide - Photos OpenHand

Complete guide for deploying the Photos OpenHand serverless application using Terraform.

## 🏗️ Architecture Overview

The Terraform deployment creates:

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │
│   Lambda        │    │    Lambda       │
│   (HTML/CSS/JS) │    │   (REST API)    │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌─────────────────┐
         │  Lambda Layer   │
         │ (Dependencies)  │
         └─────────────────┘
                     │
         ┌─────────────────┐
         │   S3 Bucket     │
         │  (Pictures +    │
         │  Iceberg Data)  │
         └─────────────────┘
```

## 📋 Prerequisites

### 1. Install Required Tools

```bash
# Install Terraform
# macOS
brew install terraform

# Ubuntu/Debian
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Install AWS CLI
pip install awscli
```

### 2. Configure AWS Credentials

```bash
aws configure
```

Provide:
- AWS Access Key ID
- AWS Secret Access Key  
- Default region (e.g., `us-east-1`)
- Default output format (`json`)

### 3. Verify Prerequisites

```bash
# Check Terraform
terraform version

# Check AWS CLI
aws --version

# Check AWS credentials
aws sts get-caller-identity
```

## 🚀 Quick Deployment

### Option 1: Automated Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/ksadeghi/photos_openhand.git
cd photos_openhand

# Run automated deployment
./deploy-terraform.sh dev us-east-1
```

### Option 2: Manual Deployment

```bash
# 1. Build Lambda layer
./build-lambda-layer.sh

# 2. Navigate to terraform directory
cd terraform

# 3. Create configuration
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars as needed

# 4. Initialize Terraform
terraform init

# 5. Plan deployment
terraform plan

# 6. Deploy
terraform apply
```

## ⚙️ Configuration Options

### Environment Variables

Edit `terraform/terraform.tfvars`:

```hcl
# Basic Configuration
aws_region = "us-east-1"
environment = "dev"

# S3 Configuration
pictures_bucket_name = "my-unique-photos-bucket-2024"  # Must be globally unique

# Lambda Configuration
lambda_timeout = 30
lambda_memory_size = 512

# Features
enable_cors = true
iceberg_warehouse_path = "warehouse"
```

### Multi-Environment Setup

Deploy to different environments:

```bash
# Development
./deploy-terraform.sh dev us-east-1

# Staging
./deploy-terraform.sh staging us-west-2

# Production
./deploy-terraform.sh prod eu-west-1
```

## 📁 File Structure

```
photos_openhand/
├── terraform/
│   ├── main.tf              # Main configuration
│   ├── variables.tf         # Input variables
│   ├── outputs.tf          # Output values
│   ├── s3.tf               # S3 bucket setup
│   ├── iam.tf              # IAM roles and policies
│   ├── lambda.tf           # Lambda functions and layer
│   ├── versions.tf         # Provider versions
│   ├── terraform.tfvars.example
│   └── README.md
├── frontend_lambda.py       # Frontend Lambda function
├── backend_lambda.py        # Backend Lambda function
├── lambda_requirements.txt  # Lambda dependencies
├── build-lambda-layer.sh    # Layer build script
└── deploy-terraform.sh      # Automated deployment
```

## 🔧 Advanced Configuration

### Custom Domain (Optional)

To use a custom domain, add to your `terraform.tfvars`:

```hcl
# Note: This requires additional Terraform configuration
custom_domain = "photos.yourdomain.com"
```

### Resource Tagging

All resources are automatically tagged with:
- `Project`: photos-openhand
- `Environment`: dev/staging/prod
- `ManagedBy`: terraform

### Security Settings

The deployment includes:
- **S3 Bucket**: Private with encryption
- **IAM Roles**: Least-privilege access
- **CORS**: Configurable cross-origin access
- **Lambda URLs**: Public but can be restricted

## 📊 Monitoring & Debugging

### CloudWatch Logs

View Lambda logs:
```bash
# Backend logs
aws logs tail /aws/lambda/photos-openhand-backend-dev --follow

# Frontend logs  
aws logs tail /aws/lambda/photos-openhand-frontend-dev --follow
```

### AWS Console Links

After deployment, access:
- **Lambda Functions**: AWS Console → Lambda
- **S3 Bucket**: AWS Console → S3
- **CloudWatch Logs**: AWS Console → CloudWatch → Log groups
- **IAM Roles**: AWS Console → IAM → Roles

### Common Issues

1. **Bucket name conflicts**
   ```
   Error: BucketAlreadyExists
   Solution: Change pictures_bucket_name in terraform.tfvars
   ```

2. **Permission errors**
   ```
   Error: AccessDenied
   Solution: Check AWS credentials and IAM permissions
   ```

3. **Layer size limits**
   ```
   Error: Layer size exceeds limit
   Solution: Optimize lambda_requirements.txt
   ```

## 💰 Cost Estimation

### Monthly Costs (Light Usage)

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 1M requests, 512MB | ~$0.20 |
| S3 | 10GB storage, 1K requests | ~$0.50 |
| CloudWatch | Log storage | ~$0.10 |
| **Total** | | **~$0.80** |

### Cost Optimization

- Use smaller Lambda memory sizes for lower costs
- Enable S3 lifecycle policies for old data
- Set CloudWatch log retention periods

## 🔄 Updates & Maintenance

### Update Application Code

```bash
# After changing Lambda functions
terraform apply
```

### Update Dependencies

```bash
# Update lambda_requirements.txt
./build-lambda-layer.sh
terraform apply
```

### Backup & Recovery

S3 versioning is enabled by default. To restore:
```bash
aws s3api list-object-versions --bucket your-bucket-name
aws s3api restore-object --bucket your-bucket-name --key filename
```

## 🗑️ Cleanup

### Destroy Infrastructure

```bash
cd terraform
terraform destroy
```

**⚠️ Warning**: This will permanently delete:
- All uploaded pictures
- Lambda functions
- S3 bucket and data
- CloudWatch logs

### Selective Cleanup

Remove specific resources:
```bash
# Remove only Lambda functions
terraform destroy -target=aws_lambda_function.frontend -target=aws_lambda_function.backend
```

## 🆘 Troubleshooting

### Deployment Fails

1. **Check AWS credentials**:
   ```bash
   aws sts get-caller-identity
   ```

2. **Verify Terraform state**:
   ```bash
   terraform state list
   ```

3. **Check resource limits**:
   - Lambda concurrent executions
   - S3 bucket limits
   - IAM policy limits

### Application Issues

1. **Lambda function errors**:
   - Check CloudWatch logs
   - Verify environment variables
   - Test function locally

2. **S3 access issues**:
   - Check IAM permissions
   - Verify bucket policy
   - Test with AWS CLI

3. **CORS issues**:
   - Check Lambda function URL CORS settings
   - Verify frontend requests

## 📞 Support

For deployment issues:

1. **Check logs**: CloudWatch logs for detailed errors
2. **Verify configuration**: Review terraform.tfvars
3. **Test locally**: Use demo_server.py for local testing
4. **AWS documentation**: Reference AWS service documentation

## 🔗 Useful Commands

```bash
# Terraform
terraform init          # Initialize
terraform plan          # Plan changes
terraform apply         # Apply changes
terraform destroy       # Destroy infrastructure
terraform output        # Show outputs
terraform state list    # List resources

# AWS CLI
aws lambda list-functions
aws s3 ls
aws logs describe-log-groups
aws iam list-roles
```
















