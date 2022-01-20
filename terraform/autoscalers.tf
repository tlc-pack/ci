locals {
  agent_subnet_ids = [for name, subnet in var.private_subnet_ids :
    subnet if split("-", name)[0] == "agents"
  ]
}

module "Jenkins-Autoscalers" {
  for_each                 = var.autoscaler_types
  source                   = "./modules/autoscaler"
  autoscaler_name          = each.key
  subnet_ids               = var.is_private ? local.agent_subnet_ids : local.frontend_subnet_ids
  security_groups          = [aws_security_group.ssh_inbound.id, aws_security_group.egress.id]
  image_family             = each.value.image_family
  agent_instance_type      = each.value.agent_instance_type
  jenkins_pub_key          = var.jenkins_pub_key
  executor_access_pub_keys = var.executor_access_pub_keys
  min_size                 = each.value.min_size
  max_size                 = each.value.max_size
}
