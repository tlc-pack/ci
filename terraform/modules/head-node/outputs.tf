output "jenkins_head_ip" {
  value = aws_eip.static.public_ip
}
