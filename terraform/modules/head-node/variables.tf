variable "environment" {
}

variable "instance_type" {
}

variable "ebs_vol_size" {
  description = "The size of the persistent volume which stores job histories"
}

variable "vpc_id" {
}

variable "subnet_ids" {
  type = list(string)
}

variable "global_access_key_name" {
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

variable "disk_size" {
  type    = number
  default = 100
}

variable "internal_load_balancer" {
  type    = bool
  default = false
}
