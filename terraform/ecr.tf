resource "aws_ecr_repository" "ci_ecr" {
  for_each             = toset(var.ecr_repositories)
  name                 = each.value
  image_tag_mutability = "IMMUTABLE"
}

resource "aws_ecr_lifecycle_policy" "untagged_removal_policy" {
  for_each   = toset(var.ecr_repositories)
  repository = aws_ecr_repository.ci_ecr[each.value].name

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
