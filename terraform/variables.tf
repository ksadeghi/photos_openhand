

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "pictures_bucket_name" {
  description = "Name for the S3 bucket to store pictures (must be globally unique)"
  type        = string
  default     = ""
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
}

variable "enable_cors" {
  description = "Enable CORS for Lambda function URLs"
  type        = bool
  default     = true
}

variable "iceberg_warehouse_path" {
  description = "S3 path for Iceberg warehouse"
  type        = string
  default     = "warehouse"
}


