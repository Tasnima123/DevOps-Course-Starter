#!/usr/bin/env bash
- docker push $DOCKER_USERNAME/my-test-image:latest
- docker login --username=$HEROKU_LOGIN --password=$HEROKU_API_KEY registry.heroku.com
- docker tag $DOCKER_USERNAME/my-test-image registry.heroku.com/devops-project-app/web
- docker push registry.heroku.com/devops-project-app/web
- heroku container:release web -a devops-project-app