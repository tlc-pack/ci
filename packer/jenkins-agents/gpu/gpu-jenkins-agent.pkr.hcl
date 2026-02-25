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

source "amazon-ebs" "jenkins_gpu_image" {
  instance_type        = "g4dn.xlarge"
  access_key = var.aws_access_key  
  secret_key =  var.aws_secret_key
  communicator        = "ssh"
  ami_name          = "${var.image_prefix}-x64-v${var.buildtime}"
  tags = {
    image_family = "${var.image_prefix}-x64"
  }
  launch_block_device_mappings {
    device_name = "/dev/sda1"
    volume_size = 40
    volume_type = "gp2"
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

build {
  sources = ["source.amazon-ebs.jenkins_gpu_image"]

  provisioner "shell" {
    execute_command = "echo 'ubuntu' | {{.Vars}} sudo -S -E bash '{{.Path}}'"
    inline = [
      "while [ ! -f /var/lib/cloud/instance/boot-finished ]; do echo 'Waiting for cloud-init...'; sleep 1; done"
    ]
  }

  provisioner "shell" {
    environment_vars = [
      "NVIDIA_DRIVER_VERSION=${var.nvidia_driver_version}"
    ]
    execute_command = "echo 'ubuntu' | {{.Vars}} sudo -S -E bash '{{.Path}}'"
    scripts = ["${path.root}/../../scripts/nvidia-drivers.sh", "${path.root}/vulkan-setup.sh"]
  }
}
