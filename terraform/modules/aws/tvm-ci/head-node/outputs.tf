output "jenkins_head_ip" {
  value = aws_eip.jenkins_head_node.public_ip
}
