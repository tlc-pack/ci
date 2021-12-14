locals {
  frontend_subnet_ids = [for name, subnet in local.network.public_subnet_ids :
    subnet if split("-", name)[0] == "frontend"
  ]
}

terraform {
  backend "gcs" {
    bucket = "octoml-terraform-state"
    prefix = "environments/aws/tvm-ci/agents"
  }
}

data "terraform_remote_state" "account" {
  backend   = "gcs"
  workspace = terraform.workspace

  config = {
    bucket = "octoml-terraform-state"
    prefix = "global/aws/accounts"
  }
}

provider "aws" {
  assume_role {
    role_arn = data.terraform_remote_state.account.outputs.role_arn
  }
  region = var.aws_default_region
}

data "terraform_remote_state" "network" {
  backend   = "gcs"
  workspace = terraform.workspace

  config = {
    bucket = "octoml-terraform-state"
    prefix = "environments/aws/tvm-ci/networking"
  }
}

resource "aws_key_pair" "tvm_ci_global_access_key" {
  key_name   = "tvm_ci_creds"
  public_key = var.global_access_pub_key
}

module "head_node" {
  source                    = "../../../../modules/aws/tvm-ci/head-node"
  count                     = var.provision_head_node ? 1 : 0
  environment               = var.environment
  instance_type             = var.head_node_instance_type
  ebs_vol_size              = var.ebs_vol_size
  vpc_id                    = local.network.vpc_id
  subnet_ids                = local.frontend_subnet_ids
  global_access_key_name    = aws_key_pair.tvm_ci_global_access_key.key_name
  subject_alternative_names = ["ci.staging.tlcpack.ai"]
}
