terraform {
  backend "gcs" {
    bucket = "octoml-terraform-state"
    prefix = "environments/aws/tvm-ci/networking"
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
