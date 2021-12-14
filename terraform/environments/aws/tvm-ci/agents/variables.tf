variable "environment" {
}

variable "aws_default_region" {
  default = "us-west-2"
}

variable "global_access_pub_key" {
  description = "The public key used to access all Jenkins VM's by Ansible. Note that this key is intentionally different than the one used by Jenkins to authenticate to the executors"
}

variable "executor_access_pub_keys" {
  description = "The public key used to access all Jenkins agents by developers."
}

variable "jenkins_pub_key" {
  description = "The public key inserted on remoteFS' for the agents so that Jenkins can log in to them to execute jobs"
}

variable "head_node_instance_type" {
  default = "t3.xlarge"
}

variable "ebs_vol_size" {
  default = "500"
}

variable "jenkins_token" {
  sensitive = true
}

variable "persistent_agent_types" {
  type = map(object({
    image_family        = string
    agent_instance_type = string
    agent_attributes = list(object({
      labels    = string
      executors = string
      prefix    = string
    }))
    replicas          = number
    template_versions = list(string)
  }))
  default = {}
}

variable "autoscaler_types" {
  type = map(object({
    image_family        = string
    agent_instance_type = string
    labels              = string
    min_size            = number
    max_size            = number
  }))
  default = {}
}

variable "provision_head_node" {
  type    = bool
  default = true
}
