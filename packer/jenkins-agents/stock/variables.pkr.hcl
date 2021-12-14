variable "aws_access_key" {  
  type = string
}

variable "aws_secret_key" {
  type = string
}

variable "image_prefix" {
}

variable "source_image_family" {
}

variable "target_accounts" {
  type = list(string)
}
