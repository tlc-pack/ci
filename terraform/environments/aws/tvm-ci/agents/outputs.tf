output "ansible_inventory" {
  value = var.provision_head_node ? templatefile("${path.module}/templates/ansible_inventory.txt.tpl", {
    head_node_ip = module.head_node[0].jenkins_head_ip
  }) : null
}

output "fleet_config" {
  value = templatefile("${path.module}/templates/fleet_config.yaml.tpl", {
    fleet_attributes = var.autoscaler_types
  })
}
