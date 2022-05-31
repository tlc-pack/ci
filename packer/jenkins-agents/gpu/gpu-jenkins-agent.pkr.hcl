variable "buildtime" {
    default = "{{isotime \"200601021504\"}}"
}

source "amazon-ebs" "jenkins_gpu_image" {
  instance_type        = "g4dn.xlarge"
  access_key = var.aws_access_key  
  secret_key =  var.aws_secret_key
  communicator        = "ssh"
  ami_groups = ["all"]
  ami_name          = "${var.image_prefix}-v${var.buildtime}"
  tags = {
    image_family = "${var.image_prefix}"
  }
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
      "NVIDIA_DRIVER_VERSION=${var.nvidia_driver_version}",
      "BASE_URL=${var.nvidia_driver_base_url}"
    ]
    execute_command = "echo 'ubuntu' | {{.Vars}} sudo -S -E bash '{{.Path}}'"
    scripts = ["${path.root}/../../scripts/nvidia-drivers.sh", "${path.root}/vulkan-setup.sh"]
  }
}
