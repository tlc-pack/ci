variable "aws_default_region" {
  default = "us-west-2"
}

variable "network" {
  type = object({
    name                  = string
    base_cidr_block       = string
    enable_single_gateway = bool

    public_subnets = list(object({
      name                    = string,
      cidr_block              = string,
      az                      = string,
      map_public_ip_on_launch = bool,
    }))

    private_subnets = list(object({
      name       = string,
      cidr_block = string,
      az         = string,
    }))

    customer_gateways = map(object({
      bgp_asn    = number
      ip_address = string
      routes     = list(string)
    }))
  })
}

variable "environment" {
  description = "Environment where resources are deployed"
}
