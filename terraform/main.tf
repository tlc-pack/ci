locals {
  frontend_subnet_ids = [for name, subnet in var.public_subnet_ids :
    subnet if split("-", name)[0] == "frontend"
  ]
}

terraform {
  required_version = ">= 1.1.9, < 2.0.0"
  required_providers {
    aws = "~> 3.73.0"
    archive = {
      source = "hashicorp/archive"
      version = "2.3.0"
    }
  }

  backend "s3" {
    bucket = "tvm-ci-terraform-state-new"
    key    = "tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  assume_role {
    role_arn = var.account_role_arn
  }
  region = var.aws_default_region
}

resource "aws_key_pair" "tvm_ci_global_access_key" {
  key_name   = "tvm_ci_creds"
  public_key = var.global_access_pub_key
}

module "head_node" {
  source                    = "./modules/head-node"
  environment               = var.environment
  instance_type             = var.head_node_instance_type
  ebs_vol_size              = var.ebs_vol_size
  ebs_jobs_vol_size         = var.ebs_jobs_vol_size
  vpc_id                    = var.vpc_id
  subnet_ids                = local.frontend_subnet_ids
  global_access_key_name    = aws_key_pair.tvm_ci_global_access_key.key_name
  domain_name               = var.domain_name
  subject_alternative_names = var.subject_alternative_names
  internal_load_balancer    = var.is_private
}
