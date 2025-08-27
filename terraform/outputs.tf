






output "frontend_url" {
  description = "URL for the frontend Lambda function"
  value       = aws_lambda_function_url.frontend.function_url
}

output "backend_url" {
  description = "URL for the backend Lambda function"
  value       = aws_lambda_function_url.backend.function_url
}

output "pictures_bucket_name" {
  description = "Name of the S3 bucket for pictures"
  value       = aws_s3_bucket.pictures.bucket
}

output "pictures_bucket_arn" {
  description = "ARN of the S3 bucket for pictures"
  value       = aws_s3_bucket.pictures.arn
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
}

output "frontend_lambda_name" {
  description = "Name of the frontend Lambda function"
  value       = aws_lambda_function.frontend.function_name
}

output "backend_lambda_name" {
  description = "Name of the backend Lambda function"
  value       = aws_lambda_function.backend.function_name
}

output "deployment_info" {
  description = "Deployment information"
  value = {
    region      = data.aws_region.current.name
    account_id  = data.aws_caller_identity.current.account_id
    environment = local.environment
    project     = local.project_name
  }
}






