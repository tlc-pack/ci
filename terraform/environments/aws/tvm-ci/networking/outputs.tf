output "vpc_id" {
  value = module.vpc.id
}

output "cidr_block" {
  value = var.network.base_cidr_block
}

output "public_subnet_ids" {
  value = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  value = module.vpc.private_subnet_ids
}

output "public_routing_table_id" {
  value = module.vpc.public_routing_table_id
}

output "private_routing_table_id" {
  value = module.vpc.private_routing_table_id
}

output "nat_gateway_ids" {
  value = module.vpc.nat_gateway_ids
}
