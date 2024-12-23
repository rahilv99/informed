import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export class LambdaLayerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // TODO - Lambda layer is currently built in build.sh - we can try to build asset using Code.fromDockerBuild
    
    // Publish the built layer
    const layer = new lambda.LayerVersion(this, 'MyLayer', {
        code: lambda.Code.fromAsset('./output'),
        compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
    });
  }
}
