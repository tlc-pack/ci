resource "aws_route53_zone" "primary" {
  name = "tvm.octoml.ai"
}

resource "aws_route53_record" "jenkins-head-node" {
  zone_id = aws_route53_zone.primary.zone_id
  name    = "jenkins.tvm.octoml.ai"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_elb.tvm-lb.dns_name]
}

module "cloudflare" {
  source = "../../../../modules/cloudflare-dns"

  recordset = [
    {
      name    = "tvm"
      type    = "NS"
      ttl     = 1
      records = aws_route53_zone.primary.name_servers
    }
  ]
}
