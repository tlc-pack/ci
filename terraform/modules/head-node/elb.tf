resource "aws_lb" "tvm-lb" {
  name            = "tvm-lb"
  internal        = var.internal_load_balancer
  idle_timeout    = 600
  subnets         = var.subnet_ids
  security_groups = [aws_security_group.alb_group.id]
}

resource "aws_lb_listener" "tvm-lb" {
  load_balancer_arn = aws_lb.tvm-lb.arn
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = aws_acm_certificate.jenkins_cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.head_node.arn
  }
}

resource "aws_lb_listener" "redirect" {
  load_balancer_arn = aws_lb.tvm-lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_target_group" "head_node" {
  name     = "jenkins-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = var.vpc_id
}

resource "aws_lb_target_group_attachment" "head_node" {
  target_group_arn = aws_lb_target_group.head_node.arn
  target_id        = aws_instance.jenkins_head_node.id
}

resource "aws_acm_certificate" "jenkins_cert" {
  domain_name               = var.domain_name
  subject_alternative_names = var.subject_alternative_names
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}
