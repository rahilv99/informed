import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3Deployment from 'aws-cdk-lib/aws-s3-deployment';
import { Construct } from 'constructs';

export class LambdaLayerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // TODO - Lambda layer is currently built in build.sh - we can try to build asset using Code.fromDockerBuild
    
    // Create S3 Bucket
    // const bucket = new s3.Bucket(this, 'TestAS', {
    //   versioned: false,
    //   removalPolicy: cdk.RemovalPolicy.DESTROY,
    //   autoDeleteObjects: true,
    // });

    // // Copy Zipped layer to bucket
    // new s3Deployment.BucketDeployment(this, 'TestASDeployFile', {
    //   sources: [s3Deployment.Source.asset('./output')],
    //   destinationBucket: bucket,
    // });


    // Publish the built layer
    const layer = new lambda.LayerVersion(this, 'MyLayer', {
        // code: lambda.Code.fromAsset('./output'),
        code: lambda.Code.fromBucketV2(
          s3.Bucket.fromBucketName(this, 'ImportedBucket', 'foundry-misc') , 
          'layer.zip'),
        compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
    });
  }
}
