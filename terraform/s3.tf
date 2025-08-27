


# S3 bucket for storing pictures
resource "aws_s3_bucket" "pictures" {
  bucket = var.pictures_bucket_name != "" ? var.pictures_bucket_name : "${local.project_name}-pictures-${random_id.bucket_suffix.hex}"

  tags = merge(local.common_tags, {
    Name = "Pictures Storage"
  })
}

# Random ID for bucket naming
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "pictures" {
  bucket = aws_s3_bucket.pictures.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "pictures" {
  bucket = aws_s3_bucket.pictures.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 bucket public access block
resource "aws_s3_bucket_public_access_block" "pictures" {
  bucket = aws_s3_bucket.pictures.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 bucket CORS configuration
resource "aws_s3_bucket_cors_configuration" "pictures" {
  bucket = aws_s3_bucket.pictures.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# S3 bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "pictures" {
  bucket = aws_s3_bucket.pictures.id

  rule {
    id     = "iceberg_cleanup"
    status = "Enabled"

    filter {
      prefix = "${var.iceberg_warehouse_path}/"
    }

    expiration {
      days = 365
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}


