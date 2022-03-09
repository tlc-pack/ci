#!/bin/bash
JENKINS_TOKEN=$1
CRUMB=$(curl -u "tvm-bot:${JENKINS_TOKEN}" -X GET http://localhost:8080/crumbIssuer/api/json | jq --raw-output .crumb)
curl -u "tvm-bot:${JENKINS_TOKEN}" -X POST http://localhost:8080/configuration-as-code/reload -H "Jenkins-Crumb: ${CRUMB}"
