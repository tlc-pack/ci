variable "environment" {
}

variable "aws_default_region" {
  default = "us-west-2"
}

variable "public_subnet_ids" {
  type = map(string)
}

variable "private_subnet_ids" {
  type = map(string)
}

variable "vpc_id" {
  type = string
}

variable "account_role_arn" {
  type        = string
  description = "The role ARN which terraform will assume to deploy resources"
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
  default = "c4.4xlarge"
}

variable "ebs_vol_size" {
  default = "500"
}

variable "ebs_jobs_vol_size" {
  default = "1000"
}

variable "autoscaler_types" {
  type = map(object({
    image_family                             = string
    agent_instance_type                      = string
    labels                                   = string
    min_size                                 = number
    max_size                                 = number
    on_demand_percentage_above_base_capacity = number
    on_demand_base_capacity                  = number
  }))
  default = {}
}

variable "domain_name" {
  type = string
}

variable "subject_alternative_names" {
  type    = list(string)
  default = []
}

variable "ecr_repositories" {
  type    = list(string)
  default = []
}

variable "is_private" {
  type    = bool
  default = false
}

variable "additional_agents" {
  type = map(object({
    labels        = string
    host          = string
    num_executors = number
    remote_fs     = string
  }))
  default = {}
}

variable "tvm_bot_webhook_secret" {
  description = "The GitHub webhook secret for the tvm_bot webhook"
  type        = string
  sensitive   = true
}

variable "tvm_bot_github_token" {
  description = "The GitHub personal access token for tvm-bot"
  type        = string
  sensitive   = true
}

variable "tvm_bot_repo" {
  description = "The GitHub repository name to comment on"
  type        = string
  default     = "tvm"
}

variable "tvm_bot_user" {
  description = "The GitHub username for tvm_bot_repo"
  default     = "apache"
  type        = string
}
