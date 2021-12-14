locals {
  client_node_startup_script = templatefile("${path.module}/templates/client_node_startup_script.sh.tpl", {
    JENKINS_USER_ID          = var.jenkins_user
    JENKINS_TOKEN            = var.jenkins_token
    JENKINS_URL              = var.jenkins_url
    agent_attributes         = var.agent_attributes
    jenkins_pub_key          = var.jenkins_pub_key
    VM_GROUP_NAME            = var.vm_group_name
    executor_access_pub_keys = var.executor_access_pub_keys
  })
}

#The key pair data source is not implemented quite yet: see https://github.com/hashicorp/terraform-provider-aws/pull/15829
#data "aws_key_pair" "key" {
#  key_name   = "tvm_ci_creds"
#}

data "aws_ami" "agent-image" {
  most_recent = true
  #'octoml' aws account
  owners = ["436166962044"]

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

resource "aws_eip" "ips" {
  count    = var.replicas
  vpc      = true
  instance = aws_instance.instances[count.index].id
}

resource "aws_launch_template" "template" {
  name_prefix = var.vm_group_name
  image_id    = data.aws_ami.agent-image.id
  network_interfaces {
    associate_public_ip_address = true
    subnet_id                   = var.subnet_id
    security_groups             = var.security_groups
  }
  instance_type = var.agent_instance_type
  key_name      = "tvm_ci_creds"
}

resource "aws_instance" "instances" {
  count = var.replicas
  tags = {
    Name = "${var.vm_group_name}-${count.index}"
  }

  #We lock everything we can in a launch template and fix the version to reduce the blast radius
  launch_template {
    id      = aws_launch_template.template.id
    version = var.template_versions[count.index]
  }

  #Putting user_data in the launch template forces instance recreation on every terraform apply,
  #even if both the user data and launch template remain unaltered
  user_data = local.client_node_startup_script

  #When the iam_instance_profile is put into the launch templates, it does not work
  #whatsoever
  iam_instance_profile = var.jenkins_instance_profile

  #We lock the above attributes via a lifecycle policy, and this policy can be commented out when
  #an update needs to occur. I would make this possible to disable on a per-cluster basis, but Terraform
  #only supports literal values inside the lifecycle block for now, so this is impossible
  #   lifecycle {
  #     ignore_changes = [iam_instance_profile, user_data]
  #   }

  root_block_device {
    volume_size = var.volume_size
  }
}
