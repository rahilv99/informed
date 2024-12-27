import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { Construct } from 'constructs';

export class CoreStack extends cdk.Stack {
  public readonly s3AstraBucket: s3.Bucket;
  public readonly astraLambdaRole: iam.Role;
  public readonly astraSQSQueue: sqs.Queue;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.s3AstraBucket = new s3.Bucket(this, 's3AstraBucket', {
      bucketName: `${this.account}-astra-bucket`,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      notificationsSkipDestinationValidation: true
    });

    // Create Lambda Role with S3 Permissions
    this.astraLambdaRole = new iam.Role(this, 'AstraLambdaRole', {
        assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      });
    this.astraLambdaRole.addManagedPolicy(
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')
      );
    this.s3AstraBucket.grantReadWrite(this.astraLambdaRole);

    // Create SQS queue
    this.astraSQSQueue = new sqs.Queue(this, 'AstraSqsQueue', {
        visibilityTimeout: cdk.Duration.seconds(60*15),     // setting it to 15 minutes
        deadLetterQueue: {
            maxReceiveCount: 1, // Retry before moving to DLQ - TODO After testing change this to 3 or so
            queue: new sqs.Queue(this, 'DLQ', {
                queueName: 'AstraSqsDLQ',
                retentionPeriod: cdk.Duration.days(14), // Retain messages in DLQ for 14 days
            })
        },
    });

    // Outputs
    new cdk.CfnOutput(this, 'BucketName', {
        value: this.s3AstraBucket.bucketName,
        description: 'Astra S3 Bucket to store data',
      });
  }
}
