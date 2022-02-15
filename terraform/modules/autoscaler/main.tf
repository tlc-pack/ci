locals {
  autoscaler_startup_script = templatefile("${path.module}/templates/autoscaler_startup_script.sh.tpl", {
    jenkins_pub_key          = var.jenkins_pub_key
    executor_access_pub_keys = var.executor_access_pub_keys
  })
}
data "aws_ami" "agent-image" {
  most_recent = true
  #'terraform-tvm' aws account
  owners = ["649843420731"]

  filter {
    name   = "name"
    values = ["${var.image_family}*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

resource "aws_launch_template" "autoscaler" {
  image_id    = data.aws_ami.agent-image.id
  name_prefix = var.autoscaler_name
  key_name    = var.global_access_key_name
  user_data   = base64encode(local.autoscaler_startup_script)
  block_device_mappings {
    device_name = "/dev/sda1"
    ebs {
      volume_size = 250
    }
  }
  iam_instance_profile {
    name = var.jenkins_instance_profile
  }
  vpc_security_group_ids = var.security_groups
  instance_type          = var.agent_instance_type
}

resource "aws_autoscaling_group" "agents" {
  name                  = var.autoscaler_name
  min_size              = var.min_size
  max_size              = var.max_size
  vpc_zone_identifier   = var.subnet_ids
  protect_from_scale_in = false

  launch_template {
    id      = aws_launch_template.autoscaler.id
    version = aws_launch_template.autoscaler.latest_version
  }
  lifecycle {
    ignore_changes = [
      # Jenkins managing scaling protection, so we ignore those changes
      protect_from_scale_in,
    ]
  }
}
