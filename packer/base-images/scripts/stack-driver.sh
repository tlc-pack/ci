#! /usr/bin/env bash
set -xe
set -o pipefail

# Install stackdriver for logging and metrics
curl -sSfL https://dl.google.com/cloudagents/install-logging-agent.sh | bash
curl -sSfL https://dl.google.com/cloudagents/install-monitoring-agent.sh | bash
