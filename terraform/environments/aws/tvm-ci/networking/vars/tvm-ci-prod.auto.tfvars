network = {
  name                  = "tvm-ci-staging"
  base_cidr_block       = "10.100.0.0/16"
  enable_single_gateway = true

  public_subnets = [
    {
      name                    = "frontend"
      az                      = "us-west-2a"
      cidr_block              = "10.100.192.0/24"
      map_public_ip_on_launch = true
    },
    {
      name                    = "frontend"
      az                      = "us-west-2b"
      cidr_block              = "10.100.193.0/24"
      map_public_ip_on_launch = true
    },
    {
      name                    = "frontend"
      az                      = "us-west-2c"
      cidr_block              = "10.100.194.0/24"
      map_public_ip_on_launch = true
    }
  ]

  private_subnets = [
    {
      name       = "agents"
      az         = "us-west-2a"
      cidr_block = "10.100.0.0/23"
    },
    {
      name       = "agents"
      az         = "us-west-2b"
      cidr_block = "10.100.2.0/23"
    },
    {
      name       = "agents"
      az         = "us-west-2c"
      cidr_block = "10.100.4.0/23"
    },
  ]

  customer_gateways = {}
}
