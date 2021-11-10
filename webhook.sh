#!/bin/bash
terraform init
docker push $DOCKER_USERNAME/my-test-image:latest
curl -dH -X POST "$(terraform output -raw cd_webhook)" 