output "ansible_inventory" {
  value = templatefile("${path.module}/templates/ansible_inventory.txt.tpl", {
    head_node_ip = module.head_node.jenkins_head_ip
  })
}

output "fleet_config" {
  value = templatefile("${path.module}/templates/fleet_config.yaml.tpl", {
    fleet_attributes = var.autoscaler_types
    is_private       = var.is_private
  })
}

output "persistent_agent_config" {
  value = templatefile("${path.module}/templates/persistent_agent_config.yaml.tpl", {
    additional_agents = var.additional_agents
  })
}
