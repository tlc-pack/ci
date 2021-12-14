resource "aws_elb" "tvm-lb" {
  name            = "tvm-lb"
  internal        = false
  idle_timeout    = 600
  subnets         = var.subnet_ids
  security_groups = [aws_security_group.alb_group.id]
  listener {
    instance_port      = 8080
    instance_protocol  = "http"
    lb_port            = 443
    lb_protocol        = "https"
    ssl_certificate_id = aws_acm_certificate.jenkins_cert.arn
  }
  listener {
    instance_port      = 8080
    instance_protocol  = "http"
    lb_port            = 80
    lb_protocol        = "https"
    ssl_certificate_id = aws_acm_certificate.jenkins_cert.arn
  }
  listener {
    instance_port     = 50000
    instance_protocol = "tcp"
    lb_port           = 50000
    lb_protocol       = "tcp"
  }
  instances = [aws_instance.jenkins_head_node.id]
  health_check {
    healthy_threshold   = 3
    unhealthy_threshold = 10
    target              = "TCP:50000"
    interval            = 60
    timeout             = 10
  }
}

resource "aws_acm_certificate" "jenkins_cert" {
  domain_name               = "jenkins.tvm.octoml.ai"
  subject_alternative_names = var.subject_alternative_names
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}
