#!/bin/bash

# Use this script to verify the Jenkins docker image build locally before
# deploying it. If successful, Jenkins should come up and be visitable at
# localhost:8081
docker build . --tag jenkins:local
docker run \
    --rm \
    --name localjenkins \
    --env-file /var/jenkins/.env \
    -p 8081:8080 -p 50001:50000 \
    --mount type=bind,source=/var/jenkins/casc,target=/var/jenkins_home/casc,readonly \
    -it jenkins:local
