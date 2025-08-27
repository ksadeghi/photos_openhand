




# Lambda Layer for dependencies
resource "aws_lambda_layer_version" "dependencies" {
  filename   = "${path.module}/../lambda-layer.zip"
  layer_name = "${local.project_name}-dependencies-${local.environment}"

  compatible_runtimes = ["python3.12"]
  
  source_code_hash = filebase64sha256("${path.module}/../lambda-layer.zip")

  description = "Python dependencies for Photos OpenHand application"
}

# Archive frontend Lambda code
data "archive_file" "frontend_lambda" {
  type        = "zip"
  source_file = "${path.module}/../frontend_lambda.py"
  output_path = "${path.module}/frontend_lambda.zip"
}

# Archive backend Lambda code
data "archive_file" "backend_lambda" {
  type        = "zip"
  source_file = "${path.module}/../backend_lambda.py"
  output_path = "${path.module}/backend_lambda.zip"
}

# Frontend Lambda function
resource "aws_lambda_function" "frontend" {
  filename         = data.archive_file.frontend_lambda.output_path
  function_name    = "${local.project_name}-frontend-${local.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "frontend_lambda.lambda_handler"
  source_code_hash = data.archive_file.frontend_lambda.output_base64sha256
  runtime         = "python3.12"
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size

  layers = [aws_lambda_layer_version.dependencies.arn]

  environment {
    variables = {
      ENVIRONMENT = local.environment
      BACKEND_URL = aws_lambda_function_url.backend.function_url
    }
  }

  tags = merge(local.common_tags, {
    Name = "Frontend Lambda"
  })

  depends_on = [aws_lambda_layer_version.dependencies]
}

# Backend Lambda function
resource "aws_lambda_function" "backend" {
  filename         = data.archive_file.backend_lambda.output_path
  function_name    = "${local.project_name}-backend-${local.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "backend_lambda.lambda_handler"
  source_code_hash = data.archive_file.backend_lambda.output_base64sha256
  runtime         = "python3.12"
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size

  layers = [aws_lambda_layer_version.dependencies.arn]

  environment {
    variables = {
      ENVIRONMENT           = local.environment
      PICTURES_BUCKET      = aws_s3_bucket.pictures.bucket
      ICEBERG_WAREHOUSE_PATH = var.iceberg_warehouse_path
      AWS_REGION           = data.aws_region.current.name
    }
  }

  tags = merge(local.common_tags, {
    Name = "Backend Lambda"
  })

  depends_on = [aws_lambda_layer_version.dependencies]
}

# Lambda function URL for frontend
resource "aws_lambda_function_url" "frontend" {
  function_name      = aws_lambda_function.frontend.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = false
    allow_origins     = ["*"]
    allow_methods     = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
    allow_headers     = ["date", "keep-alive", "content-type", "content-length", "authorization"]
    expose_headers    = ["date", "keep-alive"]
    max_age          = 86400
  }
}

# Lambda function URL for backend
resource "aws_lambda_function_url" "backend" {
  function_name      = aws_lambda_function.backend.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = false
    allow_origins     = ["*"]
    allow_methods     = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
    allow_headers     = ["date", "keep-alive", "content-type", "content-length", "authorization"]
    expose_headers    = ["date", "keep-alive"]
    max_age          = 86400
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "frontend_logs" {
  name              = "/aws/lambda/${aws_lambda_function.frontend.function_name}"
  retention_in_days = 14
  tags              = local.common_tags
}

resource "aws_cloudwatch_log_group" "backend_logs" {
  name              = "/aws/lambda/${aws_lambda_function.backend.function_name}"
  retention_in_days = 14
  tags              = local.common_tags
}




