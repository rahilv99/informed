import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ecrAssets from 'aws-cdk-lib/aws-ecr-assets';
import { Construct } from 'constructs';

export class DiscoverContainerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // // Build the Docker image
    // const dockerImage = new ecrAssets.DockerImageAsset(this, 'DiscoverContainerImage', {
    //   directory: './src/service_tier/research/discover', // Directory containing the Dockerfile
    // });

    // // Define the Lambda function
    // new lambda.Function(this, 'DiscoverLambdaFunction', {
    //   code: lambda.Code.fromEcrImage(dockerImage.imageUri), // Use the built Docker image
    //   handler: lambda.Handler.FROM_IMAGE, // Specify that it's a container image
    //   runtime: lambda.Runtime.FROM_IMAGE, // Runtime is derived from the image
    //   timeout: cdk.Duration.seconds(30),
    //   memorySize: 1024,
    // });

    new lambda.DockerImageFunction(this, 'DiscoverFunction', {
      code: lambda.DockerImageCode.fromImageAsset('.', {file:'./src/service_tier/research/discover/Dockerfile'}),
      timeout: cdk.Duration.minutes(15),
      memorySize: 1024
    });
  }
}
