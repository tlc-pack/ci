variable "buildtime" {
    default = "{{isotime \"200601021504\"}}"
}

source "amazon-ebs" "jenkins_stock_image" {
  access_key = var.aws_access_key  
  secret_key =  var.aws_secret_key
  communicator        = "ssh"
  ami_name          = "${var.image_prefix}-v${var.buildtime}"
  ami_users = var.target_accounts
  tags = {
    image_family = "${var.image_prefix}"
  }
  instance_type        = "t2.micro"
  source_ami_filter {
    filters = {
    virtualization-type = "hvm"
    "tag:image_family" = "${var.source_image_family}"
    root-device-type = "ebs"
    }
    owners = ["self"]
    most_recent = true
  }
  ssh_username = "ubuntu"
  region = "us-west-2"
}

source "amazon-ebs" "jenkins_stock_image_arm" {
  access_key = var.aws_access_key  
  secret_key =  var.aws_secret_key
  communicator        = "ssh"
  ami_name          = "${var.image_prefix}-arm-v${var.buildtime}"
  ami_users = var.target_accounts
  tags = {
    image_family = "${var.image_prefix}-arm"
  }
  instance_type        = "m6g.medium"
  source_ami_filter {
    filters = {
    virtualization-type = "hvm"
    "tag:image_family" = "${var.source_image_family}-arm"
    root-device-type = "ebs"
    }
    owners = ["self"]
    most_recent = true
  }
  ssh_username = "ubuntu"
  region = "us-west-2"
}

build {
  sources = ["source.amazon-ebs.jenkins_stock_image", "source.amazon-ebs.jenkins_stock_image_arm"]

  provisioner "shell" {
    execute_command = "echo 'ubuntu' | {{.Vars}} sudo -S -E bash '{{.Path}}'"
    inline = [
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done"
    ]
  }

  provisioner "shell" {
    only = ["amazon-ebs.jenkins_stock_image"]
    execute_command = "echo 'ubuntu' | {{.Vars}} sudo -S -E bash '{{.Path}}'"

    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive"
    ]

    scripts = [
      "${path.root}/install-docker.sh",
    ]
  }

  provisioner "shell" {
    only = ["amazon-ebs.jenkins_stock_image_arm"]
    execute_command = "echo 'ubuntu' | {{.Vars}} sudo -S -E bash '{{.Path}}'"

    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive"
    ]

    scripts = [
      "${path.root}/install-docker-arm.sh",
    ]
  }

  provisioner "shell" {
    execute_command = "echo 'ubuntu' | {{.Vars}} sudo -S -E bash '{{.Path}}'"

    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive"
    ]

    scripts = [
      "${path.root}/configure-jenkins.sh",
    ]
  }
}
