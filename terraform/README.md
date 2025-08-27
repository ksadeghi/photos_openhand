













# Terraform Infrastructure for Photos OpenHand

This directory contains Terraform configuration files to deploy the Photos OpenHand serverless application to AWS.

## Architecture

The infrastructure includes:
- **AWS Lambda Functions**: Frontend and Backend with Function URLs
- **S3 Bucket**: For storing pictures with encryption and versioning
- **IAM Roles**: Least-privilege access for Lambda functions
- **CloudWatch Logs**: For monitoring and debugging

## Prerequisites

1. **AWS CLI configured** with appropriate credentials
2. **Terraform installed** (>= 1.0)
3. **AWS Account** with permissions to create:
   - Lambda functions
   - S3 buckets
   - IAM roles and policies
   - CloudWatch log groups

## Quick Start

### 1. Configure Variables

Copy the example variables file:
```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your desired configuration:
```hcl
aws_region = "us-east-1"
environment = "dev"
pictures_bucket_name = "my-unique-bucket-name"  # Optional
lambda_timeout = 30
lambda_memory_size = 512
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Plan Deployment

```bash
terraform plan
```

### 4. Deploy Infrastructure

```bash
terraform apply
```

### 5. Access Your Application

After deployment, Terraform will output the URLs:
```
frontend_url = "https://abc123.lambda-url.us-east-1.on.aws/"
backend_url = "https://def456.lambda-url.us-east-1.on.aws/"
```

Visit the `frontend_url` to access your picture gallery!

## Configuration Options

### Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `aws_region` | AWS region for deployment | `us-east-1` | No |
| `environment` | Environment name (dev/staging/prod) | `dev` | No |
| `pictures_bucket_name` | S3 bucket name (globally unique) | Auto-generated | No |
| `lambda_timeout` | Lambda timeout in seconds | `30` | No |
| `lambda_memory_size` | Lambda memory in MB | `512` | No |
| `enable_cors` | Enable CORS for Lambda URLs | `true` | No |
| `iceberg_warehouse_path` | S3 path for Iceberg data | `warehouse` | No |

### Environments

Deploy to different environments by changing the `environment` variable:

```bash
# Development
terraform apply -var="environment=dev"

# Staging  
terraform apply -var="environment=staging"

# Production
terraform apply -var="environment=prod"
```

## File Structure

```
terraform/
├── main.tf              # Main configuration and providers
├── variables.tf         # Input variables
├── outputs.tf          # Output values
├── versions.tf         # Provider version constraints
├── s3.tf              # S3 bucket configuration
├── iam.tf             # IAM roles and policies
├── lambda.tf          # Lambda functions and URLs
├── terraform.tfvars.example  # Example variables
└── README.md          # This file
```

## Security Features

- **S3 Bucket**: Private with encryption enabled
- **IAM Roles**: Least-privilege access
- **CORS**: Configurable cross-origin access
- **Versioning**: S3 object versioning enabled
- **Lifecycle**: Automatic cleanup of old Iceberg data

## Monitoring

CloudWatch Log Groups are created for both Lambda functions:
- `/aws/lambda/photos-openhand-frontend-{env}`
- `/aws/lambda/photos-openhand-backend-{env}`

## Cleanup

To destroy all resources:
```bash
terraform destroy
```

**Warning**: This will delete all pictures and data!

## Troubleshooting

### Common Issues

1. **Bucket name conflicts**: S3 bucket names must be globally unique
   - Solution: Specify a unique `pictures_bucket_name` or leave empty for auto-generation

2. **Permission errors**: Ensure AWS credentials have sufficient permissions
   - Required: Lambda, S3, IAM, CloudWatch permissions

3. **Region issues**: Some regions may not support Lambda Function URLs
   - Solution: Use supported regions like `us-east-1`, `us-west-2`, `eu-west-1`

### Debugging

Check Lambda logs in CloudWatch:
```bash
aws logs tail /aws/lambda/photos-openhand-backend-dev --follow
```

## Cost Estimation

Estimated monthly costs for light usage:
- **Lambda**: ~$0.20 (1M requests)
- **S3**: ~$0.50 (10GB storage)
- **CloudWatch**: ~$0.10 (logs)
- **Total**: ~$0.80/month

## Support

For issues with the Terraform configuration, check:
1. AWS credentials and permissions
2. Terraform version compatibility
3. Variable configuration
4. CloudWatch logs for runtime errors













