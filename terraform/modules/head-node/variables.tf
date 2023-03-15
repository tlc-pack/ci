variable "environment" {
  type = string
}

variable "instance_type" {
  type = string
}

variable "ebs_vol_size" {
  description = "The size of the persistent volume which stores runtime data"
  type = number
}

variable "ebs_jobs_vol_size" {
  description = "The size of the persistent volume which stores job histories"
  type = number
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "global_access_key_name" {
  type = string
  description = "The name of the key used to access all executors for SSH authentication"
}

variable "domain_name" {
  type = string
}

variable "subject_alternative_names" {
  type        = list(string)
  description = "extra alt names to add to ssl cert for ELB"
  default     = []
}

# variable "disk_size" {
#   type    = number
#   default = 100
# }

variable "internal_load_balancer" {
  type    = bool
  default = false
}
