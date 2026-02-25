resource "aws_s3_bucket" "bucket" {
  bucket = "tvm-sccache-${var.environment}"
  acl    = "private"

  tags = {
    Name = "tvm-sccache-${var.environment}"
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
