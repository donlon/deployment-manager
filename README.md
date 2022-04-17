# Deployment Manager

A Django server for integrating continuous deployment (CD) functionalities.

## Docker Compose Example Configuration

``` YAML
version: "3"
services:
    deployment-manager:
        restart: always
        image: ghcr.io/donlon/deployment-manager/deployment-manager:latest
        container_name: deployment-manager
        volumes:
            - ./data:/data
        environment:
            - APP_STATIC_FILE_PATH={{GENERATED_STATIC_FILE_PATH}}
            - APP_PRODUCTION=True
            - APP_ALLOWED_HOSTS=*
            - APP_BEHIND_PROXY=True
            - APP_ROOT_URL=deployment/
            - APP_DEPLOY_ROOT={{DEPLOY_ROOT}}
            - APP_CSRF_TRUSTED_ORIGINS={{YOUR_SERVER_ORIGIN}}
            - APP_GITHUB_TOKEN={{YOUR_GITHUB_TOKEN}}
```
