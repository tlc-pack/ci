# terraform

This folder handles the Terraform configuration for TVM Jenkins Infrastructure.

## Local Usage

```bash
# if anything is broken, remove all terraform local files
git clean -xfd .

# set credentials
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...

# get terraform state
terraform init

# the workspace must be selected or else 'plan' will not read the correct state
terraform workspace new tvm-ci-prod
terraform workspace select tvm-ci-prod

# run the actual plan against AWS
terraform plan -var-file=vars/tvm-ci-prod.auto.tfvars
```