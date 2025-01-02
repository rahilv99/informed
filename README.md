# Welcome to your CDK TypeScript project

This is a blank project for CDK development with TypeScript.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `npx cdk deploy`  deploy this stack to your default AWS account/region
* `npx cdk diff`    compare deployed stack with current state
* `npx cdk synth`   emits the synthesized CloudFormation template


# Useful AWS Commands for logging in
export AWS_DEFAULT_PROFILE=atul-dev-profile
aws sso login --profile atul-dev-profile
## To export creds as env variables after SSO login
eval "$(aws configure export-credentials --profile atul-dev-profile --format env)"

# ECR Login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 905418457861.dkr.ecr.us-east-1.amazonaws.com
docker pull 905418457861.dkr.ecr.us-east-1.amazonaws.com/cdk-hnb659fds-container-assets-905418457861-us-east-1:2aa906cc65c8963f9bead1a3e5363cb5949442ff6b7b33423533b15df2

# Attach shell to lambda function locally
docker run -it --entrypoint /bin/bash -v $(pwd):/tmp service_tier-service_tier:latest
docker run -it --rm --entrypoint /bin/bash -v $(pwd):/tmp $(docker build -q .)


## Get account info
aws sts get-caller-identity