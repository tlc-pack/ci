resource "aws_security_group" "ssh_inbound" {
  vpc_id = local.network.vpc_id
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "ssh_inbound"
  }
}

resource "aws_security_group" "egress" {
  vpc_id = local.network.vpc_id
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "egress"
  }
}
