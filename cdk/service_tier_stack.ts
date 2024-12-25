import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ecrAssets from 'aws-cdk-lib/aws-ecr-assets';
import { Construct } from 'constructs';

export class ServiceTierLambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new lambda.DockerImageFunction(this, 'ServiceTierFunction', {
      //code: lambda.DockerImageCode.fromImageAsset('.', {file:'./src/service_tier/Dockerfile'}),
      code: lambda.DockerImageCode.fromImageAsset('src/service_tier'),
      timeout: cdk.Duration.minutes(15),
      memorySize: 2*1024
    });
  }
}
