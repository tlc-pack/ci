#!/usr/bin/env bash
set -euo pipefail

# Preserve containers that pin AMI-cached layers.
docker container prune --force --filter 'until=1h' --filter 'label!=ci.ami-cache=true'
docker image prune --all --force --filter 'until=1h'
docker network prune --force --filter 'until=1h'
docker builder prune --all --force --filter 'until=1h'
