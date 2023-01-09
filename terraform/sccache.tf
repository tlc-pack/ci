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
}
