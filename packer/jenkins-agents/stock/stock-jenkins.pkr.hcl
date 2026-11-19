packer {
  required_plugins {
    amazon = {
      version = ">= 1.2.0"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

variable "buildtime" {
    default = "{{isotime \"200601021504\"}}"
}

source "amazon-ebs" "jenkins_stock_image" {
  access_key = var.aws_access_key  
  secret_key =  var.aws_secret_key
  communicator        = "ssh"
  ami_name          = "${var.image_prefix}-x64-v${var.buildtime}"
  tags = {
    image_family = "${var.image_prefix}-x64"
  }
  # Allow room for CUDA image extraction.
  instance_type        = "t3.large"
  launch_block_device_mappings {
    device_name           = "/dev/sda1"
    volume_size           = 100
    volume_type           = "gp3"
    delete_on_termination = true
  }
  source_ami_filter {
    filters = {
    virtualization-type = "hvm"
    "tag:image_family" = "${var.source_image_family}-x64"
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
  tags = {
    image_family = "${var.image_prefix}-arm"
  }
  instance_type        = "m6g.medium"
  launch_block_device_mappings {
    device_name           = "/dev/sda1"
    volume_size           = 100
    volume_type           = "gp3"
    delete_on_termination = true
  }
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

  provisioner "file" {
    source      = "${path.root}/../../scripts/jenkins-docker-cleanup.sh"
    destination = "/tmp/jenkins-docker-cleanup.sh"
  }

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

  provisioner "shell" {
    execute_command = "echo 'ubuntu' | {{.Vars}} sudo -S -E bash '{{.Path}}'"
    environment_vars = [
      "DOCKER_CACHE_IMAGES=${join(" ", var.docker_cache_images)}"
    ]
    scripts = ["${path.root}/../../scripts/preload-docker-images.sh"]
  }
}
