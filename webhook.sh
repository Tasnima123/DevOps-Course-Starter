#!/bin/bash
terraform init
terraform apply -var="location=uksouth" -var="client_id=$client_id" -var="client_secret=$client_secret" -auto-approve
docker push $DOCKER_USERNAME/my-test-image:latest
curl -dH -X POST "$(terraform output -raw cd_webhook)" 