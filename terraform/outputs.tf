

# Backend API URL
output "backend_api_url" {
  description = "URL for the backend Lambda function API"
  value       = aws_lambda_function_url.backend.function_url
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

output "backend_lambda_name" {
  description = "Name of the backend Lambda function"
  value       = aws_lambda_function.backend.function_name
}

# Frontend deployment instructions
output "frontend_deployment_instructions" {
  description = "Instructions for deploying the frontend"
  value = <<-EOT
    
    FRONTEND DEPLOYMENT INSTRUCTIONS:
    
    1. Update script.js with the backend API URL:
       const API_BASE_URL = '${aws_lambda_function_url.backend.function_url}';
    
    2. Deploy to AWS Amplify:
       - Upload index.html, style.css, script.js, and amplify.yml
       - Or connect your Git repository to Amplify
    
    3. Your backend API is ready at:
       ${aws_lambda_function_url.backend.function_url}
    
  EOT
}

# Deployment information
output "deployment_info" {
  description = "Deployment information"
  value = {
    region      = data.aws_region.current.name
    account_id  = data.aws_caller_identity.current.account_id
    environment = local.environment
    project     = local.project_name
    backend_url = aws_lambda_function_url.backend.function_url
  }
}

