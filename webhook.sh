#!/bin/bash
docker push $DOCKER_USERNAME/my-test-image:latest
terraform output -raw cd_webhook