# Archive backend Lambda code
data "archive_file" "backend_lambda" {
  type        = "zip"
  source_file = "${path.module}/../backend_lambda.py"
  output_path = "${path.module}/backend_lambda.zip"
}

# Backend Lambda function (API only)
resource "aws_lambda_function" "backend" {
  filename         = data.archive_file.backend_lambda.output_path
  function_name    = "${local.project_name}-backend-${local.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "backend_lambda.lambda_handler"
  source_code_hash = data.archive_file.backend_lambda.output_base64sha256
  runtime         = "python3.12"
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size

  environment {
    variables = {
      ENVIRONMENT           = local.environment
      PICTURES_BUCKET      = aws_s3_bucket.pictures.bucket
      ICEBERG_WAREHOUSE_PATH = var.iceberg_warehouse_path
    }
  }

  tags = merge(local.common_tags, {
    Name = "Backend Lambda API"
  })
}

# Lambda function URL for backend function
resource "aws_lambda_function_url" "backend" {
  function_name      = aws_lambda_function.backend.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = false
    allow_origins     = ["*"]
    allow_methods     = ["*"]
    allow_headers     = ["*"]
    max_age          = 86400
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "backend_logs" {
  name              = "/aws/lambda/${aws_lambda_function.backend.function_name}"
  retention_in_days = 14
  tags              = local.common_tags
}

