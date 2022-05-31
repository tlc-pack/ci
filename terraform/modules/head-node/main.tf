locals {
  head_node_startup_script = templatefile("${path.module}/templates/head_node_startup_script.sh.tpl", {
  })
}

resource "aws_iam_role" "jenkins_fleet" {
  name = "jenkins_fleet_role"

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
resource "aws_iam_role_policy" "jenkins_fleet" {
  name = "jenkins_fleet"
  role = aws_iam_role.jenkins_fleet.id


  policy = <<-EOF
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Effect":"Allow",
         "Action":[
            "ec2:DescribeSpotFleetInstances",
            "ec2:ModifySpotFleetRequest",
            "ec2:CreateTags",
            "ec2:DescribeRegions",
            "ec2:DescribeInstances",
            "ec2:TerminateInstances",
            "ec2:DescribeInstanceStatus",
            "ec2:DescribeSpotFleetRequests"
         ],
         "Resource":"*"
      },
      {
         "Effect":"Allow",
         "Action":[
            "autoscaling:DescribeAutoScalingGroups",
            "autoscaling:UpdateAutoScalingGroup"
         ],
         "Resource":"*"
      },
      {
         "Effect":"Allow",
         "Action":[
            "iam:ListInstanceProfiles",
            "iam:ListRoles",
            "iam:PassRole"
         ],
         "Resource":"*"
      }
   ]
}
EOF
}

data "aws_subnet" "head_node" {
  id = var.subnet_ids[0]
}

resource "aws_ebs_volume" "jobs_storage" {
  availability_zone = data.aws_subnet.head_node.availability_zone
  size              = var.ebs_vol_size

  tags = {
    Name = "${title(var.environment)}-Jenkins-Persistent-Storage"
  }
}

resource "aws_volume_attachment" "jobs_storage" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.jobs_storage.id
  instance_id = aws_instance.jenkins_head_node.id
}


resource "aws_iam_instance_profile" "jenkins_fleet" {
  name = "jenkins-fleet-profile"
  role = aws_iam_role.jenkins_fleet.name
}

resource "aws_eip" "static" {
  vpc      = true
  instance = aws_instance.jenkins_head_node.id
  tags = {
    Name = "eip-jenkins-server-${var.environment}"
  }
}

resource "aws_instance" "jenkins_head_node" {
  #Older jenkins-stock-agent AMI
  ami           = "ami-056c71c88d13476dd"
  instance_type = var.instance_type
  subnet_id     = data.aws_subnet.head_node.id
  vpc_security_group_ids = [aws_security_group.egress.id,
    aws_security_group.head_node.id,
    aws_security_group.ssh_inbound.id
  ]
  key_name = var.global_access_key_name
  root_block_device {
    volume_size = var.ebs_vol_size
  }
  timeouts {
    create = "60m"
    update = "60m"
  }

  tags = {
    Name        = "${title(var.environment)}-Jenkins-Head-Node"
    Environment = "title(var.environment)"
  }
  user_data            = local.head_node_startup_script
  iam_instance_profile = aws_iam_instance_profile.jenkins_fleet.name
}
