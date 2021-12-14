locals {
  enable_vpn_gateway = length(keys(var.network.customer_gateways)) > 0
}

module "vpc" {
  source = "../../../../modules/aws/vpc"

  name       = var.network.name
  cidr_block = var.network.base_cidr_block

  public_subnets        = var.network.public_subnets
  private_subnets       = var.network.private_subnets
  customer_gateways     = var.network.customer_gateways
  enable_single_gateway = var.network.enable_single_gateway
}
