resource "aws_ecr_repository" "ci_ecr" {
  count                = "${length(var.ecr_repositories)}"
  name                 = "${var.ecr_repositories[count.index]}"
  image_tag_mutability = "IMMUTABLE"
}

resource "aws_ecr_lifecycle_policy" "untagged_removal_policy" {
  count      = "${length(var.ecr_repositories)}"
  depends_on = [ "aws_ecr_repository.ci_ecr" ]
  repository = "${aws_ecr_repository.ci_ecr[count.index].name}"

  policy = <<EOF
{
    "rules": [
        {
        "action": {
            "type": "expire"
        },
        "selection": {
            "countType": "sinceImagePushed",
            "countUnit": "days",
            "countNumber": 1,
            "tagStatus": "tagged",
            "tagPrefixList": [
            "PR-"
            ]
        },
        "description": "Remove PR images",
        "rulePriority": 1
        }
    ]
}
EOF
}