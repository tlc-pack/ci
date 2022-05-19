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
}
