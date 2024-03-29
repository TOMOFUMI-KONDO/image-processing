data "aws_route53_zone" "main" {
  name         = var.domain.apex
  private_zone = false
}

resource "aws_route53_record" "apex" {
  name    = var.domain.apex
  type    = "A"
  zone_id = data.aws_route53_zone.main.id
  records = [var.vercel_record.a]
  ttl     = 300
}

resource "aws_route53_record" "www" {
  name    = var.domain.front
  type    = "CNAME"
  zone_id = data.aws_route53_zone.main.id
  records = [var.vercel_record.cname]
  ttl     = 300
}

resource "aws_route53_record" "api" {
  name    = var.domain.api
  type    = "A"
  zone_id = data.aws_route53_zone.main.id


  alias {
    evaluate_target_health = false
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
  }
}

resource "aws_acm_certificate" "main" {
  domain_name       = "*.${var.domain.apex}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "validation" {
  zone_id    = data.aws_route53_zone.main.zone_id
  ttl        = 60
  depends_on = [aws_acm_certificate.main]

  for_each = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }

  allow_overwrite = true
  name            = each.value.name
  type            = each.value.type
  records         = [each.value.record]
}

resource "aws_acm_certificate_validation" "main" {
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for record in aws_route53_record.validation : record.fqdn]
}
