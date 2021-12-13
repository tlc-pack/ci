#!/bin/bash

export AWS_DEFAULT_REGION=us-west-2
aws s3 cp s3://tvm-ci-terraform-state/env:/tvm-ci-prod/tfstate .

jq --raw-output .outputs.fleet_config.value > fleet_config.yaml \
  tfstate
jq --raw-output .outputs.ansible_inventory.value > ansible_inventory.txt \
  tfstate
jq --raw-output .outputs.persistent_agent_config.value > persistent_agent_config.yaml \
  tfstate
