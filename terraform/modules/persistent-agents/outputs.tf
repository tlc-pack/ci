output "executor_ips" {
  value = [for eip in aws_eip.ips : eip.public_ip]
}
