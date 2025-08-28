

# Lambda Layer for dependencies
resource "aws_lambda_layer_version" "dependencies" {
  filename   = "${path.module}/../lambda-layer.zip"
  layer_name = "${local.project_name}-dependencies-${local.environment}"

  compatible_runtimes = ["python3.12"]
  
  source_code_hash = filebase64sha256("${path.module}/../lambda-layer.zip")

  description = "Python dependencies for Photos OpenHand application"
}

# Archive unified Lambda code
data "archive_file" "unified_lambda" {
  type        = "zip"
  source_file = "${path.module}/../unified_lambda.py"
  output_path = "${path.module}/unified_lambda.zip"
}

# Unified Lambda function (frontend + backend)
resource "aws_lambda_function" "unified" {
  filename         = data.archive_file.unified_lambda.output_path
  function_name    = "${local.project_name}-unified-${local.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "unified_lambda.lambda_handler"
  source_code_hash = data.archive_file.unified_lambda.output_base64sha256
  runtime         = "python3.12"
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size

  layers = [aws_lambda_layer_version.dependencies.arn]

  environment {
    variables = {
      ENVIRONMENT           = local.environment
      PICTURES_BUCKET      = aws_s3_bucket.pictures.bucket
      ICEBERG_WAREHOUSE_PATH = var.iceberg_warehouse_path
    }
  }

  tags = merge(local.common_tags, {
    Name = "Unified Lambda (Frontend + Backend)"
  })

  depends_on = [aws_lambda_layer_version.dependencies]
}

# Lambda function URL for unified function
resource "aws_lambda_function_url" "unified" {
  function_name      = aws_lambda_function.unified.function_name
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
resource "aws_cloudwatch_log_group" "unified_logs" {
  name              = "/aws/lambda/${aws_lambda_function.unified.function_name}"
  retention_in_days = 14
  tags              = local.common_tags
}

