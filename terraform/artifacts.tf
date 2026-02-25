resource "aws_s3_bucket" "artifacts-bucket" {
  bucket = "tvm-jenkins-artifacts-${var.environment}"
  acl    = "private"

  tags = {
    Name = "tvm-jenkins-artifacts-${var.environment}"
  }

  lifecycle_rule {
    id      = "weekly_retention"
    enabled = true

    expiration {
      days = 7
    }
  }
  logging {
    target_bucket = var.access_logs_target_bucket
    target_prefix = "log/"
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}
