#!/bin/bash
set -eux

docker build . --tag vendor_ci:latest
source prod.env

docker run \
    --env AWS_ACCESS_KEY_ID \
    --env AWS_SECRET_ACCESS_KEY \
    --env GITHUB_TOKEN \
    --env GITHUB_REPO \
    --env GITHUB_OWNER \
    --env API_KEYS_JSON \
    --net=host \
    -it vendor_ci:latest