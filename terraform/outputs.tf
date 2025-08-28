

# Application URL
output "application_url" {
  description = "URL for the unified Lambda function (frontend + backend)"
  value       = aws_lambda_function_url.unified.function_url
}

# S3 bucket outputs
output "pictures_bucket_name" {
  description = "Name of the S3 bucket for pictures"
  value       = aws_s3_bucket.pictures.bucket
}

output "pictures_bucket_arn" {
  description = "ARN of the S3 bucket for pictures"
  value       = aws_s3_bucket.pictures.arn
}

# Lambda outputs
output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
}

output "unified_lambda_name" {
  description = "Name of the unified Lambda function"
  value       = aws_lambda_function.unified.function_name
}

# Deployment information
output "deployment_info" {
  description = "Deployment information"
  value = {
    region      = data.aws_region.current.name
    account_id  = data.aws_caller_identity.current.account_id
    environment = local.environment
    project     = local.project_name
  }
}

