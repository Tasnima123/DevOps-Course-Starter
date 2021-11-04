#!/bin/bash
docker push $DOCKER_USERNAME/my-test-image:latest
curl -dH -X POST "$WEBHOOK_URL"