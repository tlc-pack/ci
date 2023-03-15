#!/bin/bash
# shellcheck disable=SC2129

echo "ENVIRONMENT=prod" >> "$GITHUB_ENV"
echo "STATE_PATH=tvm-ci-prod" >> "$GITHUB_ENV"
echo "OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID_PROD}" >> "$GITHUB_ENV"
echo "OAUTH_CLIENT_SECRET=${OAUTH_CLIENT_SECRET_PROD}" >> "$GITHUB_ENV"

echo 'JENKINS_PRIV_KEY<<EOF' >> "$GITHUB_ENV"
echo "$JENKINS_PRIV_KEY_PROD" >> "$GITHUB_ENV"
echo 'EOF' >> "$GITHUB_ENV"
export JENKINS_PRIV_KEY="$JENKINS_PRIV_KEY_PROD"

# shellcheck disable=SC2086
echo "JENKINS_PUB_KEY=$(ssh-keygen -yf /dev/stdin  <<<$JENKINS_PRIV_KEY)" >> "$GITHUB_ENV"
