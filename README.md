# Deployment Manager

A lightweight Django server for integrating continuous deployment (CD) functionalities.

This application accepts webhook requests from continuous integration (CI) services likes GitHub Actions and automatically pulls generated files to your server.

## Getting Started

### Deploying the application with Docker

Create the Docker Compose configuration file and start the container with `docker-compose up` command.

``` YAML
# docker-compose.yml
version: "3"
services:
    deployment-manager:
        restart: always
        image: ghcr.io/donlon/deployment-manager/deployment-manager:latest
        container_name: deployment-manager
        volumes:
            - ./data:/data
        environment:
            - APP_STATIC_FILE_PATH=<path-to-generated-static-file>
            - APP_PRODUCTION=True
            - APP_ALLOWED_HOSTS=*
            - APP_BEHIND_PROXY=True
            - APP_ROOT_URL=deployment/
            - APP_DEPLOY_ROOT=<deploy-root>
            - APP_CSRF_TRUSTED_ORIGINS=<your-server-origin>
            - APP_GITHUB_TOKEN=<your-github-token>
```

### Configuring your server

Open Django admin page at `https://<hostname-of-your-server>/admin`, create `Identity` and `Target` objects, and fill out the fields in the database editor.

### Integrating with GitHub Actions

Example of [GitHub Actions workflow](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions) configuration file:

``` YAML
name: Deploy Build Outputs to Server

on:
  push:

jobs:
  build:
    runs-on: ubuntu-20.04
    steps:
      -
        name: Checkout the code
        uses: actions/checkout@v2
      -
        name: Do whatever you want to generate outputs
        run: <dO-WHaTeVeR-YOu-wANt-To-gEnErAtE-oUTpUts>
      -
        name: Publish output files
        uses: actions/upload-artifact@v3
        with:
          name: <your-awesome-artifact-name>
          path: <path-to-output-files>
      -
        name: Invoke deployment hook
        run: >
          curl -fsSL
          -X POST
          "https://<hostname-of-your-server>/webhook"
          -d "token=<webhook-token>"
          -d "repo=${{ github.repository }}"
          -d "run_id=${{ github.run_id }}"
          -d "artifact_name=<your-awesome-artifact-name>"
          -d "target=<target-name>"
```

## License

See [LICENSE](LICENSE).