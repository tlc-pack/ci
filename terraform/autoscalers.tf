locals {
  agent_subnet_ids = [for name, subnet in var.private_subnet_ids :
    subnet if split("-", name)[0] == "agents"
  ]
}

resource "aws_iam_role" "autoscalers" {
  name = "autoscalers_role"

  # Terraform's "jsonencode" function converts a
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
               "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF
}

resource "aws_iam_role_policy" "autoscalers" {
  name = "describeTags"
  role = aws_iam_role.autoscalers.id


  policy = <<-EOF
 {
   "Version": "2012-10-17",
   "Statement": [
      {
        "Sid": "SccacheAccess",
        "Effect": "Allow",
        "Action": [
         "s3:DeleteObject",
         "s3:GetObject",
         "s3:ListBucket",
         "s3:PutObject"
        ],
        "Resource": "arn:aws:s3:::tvm-sccache-${var.environment}/*"
      },
      {
        "Sid": "ArtifactsAccess",
        "Effect": "Allow",
        "Action": [
         "s3:DeleteObject",
         "s3:GetObject",
         "s3:ListBucket",
         "s3:PutObject"
        ],
        "Resource": "arn:aws:s3:::jenkins-artifacts-${var.environment}/*"
      },
      {
          "Sid": "ECRAccess1",
          "Effect": "Allow",
          "Action": [
              "ecr:BatchCheckLayerAvailability",
              "ecr:BatchGetImage",
              "ecr:CompleteLayerUpload",
              "ecr:DescribeImages",
              "ecr:DescribeRepositories",
              "ecr:GetDownloadUrlForLayer",
              "ecr:InitiateLayerUpload",
              "ecr:ListImages",
              "ecr:PutImage",
              "ecr:TagResource",
              "ecr:UploadLayerPart"
          ],
          "Resource": "arn:aws:ecr:us-west-2:*"
      },
      {
          "Sid": "ECRAccess2",
          "Effect": "Allow",
          "Action": [
              "ecr:DescribeRegistry",
              "ecr:GetAuthorizationToken"
          ],
          "Resource": "*"
      }
   ]
 }
EOF
}

resource "aws_iam_instance_profile" "autoscalers" {
  name = "autoscalers_instance_profile"
  role = aws_iam_role.autoscalers.name
}

module "Jenkins-Autoscalers" {
  for_each                                 = var.autoscaler_types
  source                                   = "./modules/autoscaler"
  autoscaler_name                          = each.key
  subnet_ids                               = var.is_private ? local.agent_subnet_ids : local.frontend_subnet_ids
  security_groups                          = [aws_security_group.ssh_inbound.id, aws_security_group.egress.id]
  image_family                             = each.value.image_family
  agent_instance_type                      = each.value.agent_instance_type
  jenkins_pub_key                          = var.jenkins_pub_key
  jenkins_instance_profile                 = aws_iam_instance_profile.autoscalers.name
  executor_access_pub_keys                 = var.executor_access_pub_keys
  min_size                                 = each.value.min_size
  max_size                                 = each.value.max_size
  on_demand_base_capacity                  = each.value.on_demand_base_capacity
  on_demand_percentage_above_base_capacity = each.value.on_demand_percentage_above_base_capacity
}
