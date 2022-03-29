variable "buildtime" {
    default = "{{isotime \"200601021504\"}}"
}

source "amazon-ebs" "aws_base_image" {
  access_key = var.aws_access_key  
  secret_key =  var.aws_secret_key
  communicator        = "ssh"
  ami_name          = "${var.image_prefix}-v${var.buildtime}"
  ami_groups = ["all"]
  tags = {
    image_family = "${var.image_prefix}"
  }
  instance_type        = "t2.micro"
  source_ami_filter {
    filters = {
    virtualization-type = "hvm"
    name = "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"
    root-device-type = "ebs"
    }
    owners = ["099720109477"]
    most_recent = true
  }
  ssh_username = "ubuntu"
  region = "us-west-2"
}

source "amazon-ebs" "aws_base_image_arm" {
  access_key = var.aws_access_key  
  secret_key =  var.aws_secret_key
  communicator        = "ssh"
  ami_name          = "${var.image_prefix}-arm-v${var.buildtime}"
  ami_groups = ["all"]
  tags = {
    image_family = "${var.image_prefix}-arm"
  }
  instance_type        = "m6g.medium"
  source_ami_filter {
    filters = {
    virtualization-type = "hvm"
    name = "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-arm64-server-*"
    root-device-type = "ebs"
    }
    owners = ["099720109477"]
    most_recent = true
  }
  ssh_username = "ubuntu"
  region = "us-west-2"
}

build {
  sources = ["source.amazon-ebs.aws_base_image", "source.amazon-ebs.aws_base_image_arm"]

  provisioner "shell" {
    execute_command = "echo 'ubuntu' | {{.Vars}} sudo -S -E bash '{{.Path}}'"
    inline = [
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done"
    ]
  }

  provisioner "shell" {
    execute_command = "echo 'ubuntu' | {{.Vars}} sudo -S -E bash '{{.Path}}'"

    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive"
    ]

    scripts = [
      "${path.root}/../scripts/update.sh",
      "${path.root}/../scripts/tools.sh",
      "${path.root}/../scripts/datadog.sh",
      "${path.root}/../scripts/coredumps.sh",
      "${path.root}/../scripts/fail2ban.sh",
      "${path.root}/../scripts/aws-extras.sh"
    ]
  }
}
