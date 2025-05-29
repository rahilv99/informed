import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import { Construct } from 'constructs';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';

export class CoreStack extends cdk.Stack {
  public readonly s3AstraBucket: s3.Bucket;
  public readonly astraLambdaRole: iam.Role;
  public readonly s3ScraperBucket: s3.Bucket;
  public readonly ScraperLambdaRole: iam.Role;
  public readonly astraSQSQueue: sqs.Queue;
  public readonly scraperSQSQueue: sqs.Queue;
  public readonly puppetSqsQueue: sqs.Queue;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    //////// SERVICE TIER LAMBDA STACK ////////
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
    
    //////// SCRAPER LAMBDA STACK ////////
    // Create Lambda Role with S3 Permissions
    this.ScraperLambdaRole = new iam.Role(this, 'ScraperLambdaRole', {
        assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      });

    this.ScraperLambdaRole.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')
    );
      
    this.s3ScraperBucket = new s3.Bucket(this, 's3ScraperBucket', {
      bucketName: `${this.account}-scraper-bucket`,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      notificationsSkipDestinationValidation: true
    });

    this.s3ScraperBucket.grantReadWrite(this.ScraperLambdaRole);
    this.s3AstraBucket.grantReadWrite(this.ScraperLambdaRole);

    // Create SQS queue
    this.scraperSQSQueue = new sqs.Queue(this, 'ScraperSqsQueue', {
        visibilityTimeout: cdk.Duration.seconds(60*15),     // setting it to 15 minutes
        deadLetterQueue: {
            maxReceiveCount: 1, // Retry before moving to DLQ - TODO After testing change this to 3 or so
            queue: new sqs.Queue(this, 'scraper_DLQ', {
                queueName: 'ScraperSqsDLQ',
                retentionPeriod: cdk.Duration.days(14), // Retain messages in DLQ for 14 days
            })
        },
    });

    // Allow cloudwatch events to send messages to the SQS queue
    this.scraperSQSQueue.addToResourcePolicy(
      new cdk.aws_iam.PolicyStatement({
        effect: cdk.aws_iam.Effect.ALLOW,
        principals: [new cdk.aws_iam.ServicePrincipal('events.amazonaws.com')],
        actions: ['sqs:SendMessage'],
        resources: [this.scraperSQSQueue.queueArn],
      })
    );

    // Create a CloudWatch Event Rule for the scraper schedule
    const scraperRule = new events.Rule(this, 'ScraperRule', {
        schedule: events.Schedule.cron({
        minute: '0',
        hour: '10',
        day: '*',
        month: '*',
        year: '*',
        }),
    });

    const messagePayload = {
        "action": "e_dispatch"
    };

    scraperRule.addTarget(new targets.SqsQueue(this.scraperSQSQueue, {
      message: events.RuleTargetInput.fromObject(messagePayload)
    }));

    // Create a CloudWatch Event Rule for the scraper schedule
    const mergeRule = new events.Rule(this, 'mergeRule', {
        schedule: events.Schedule.cron({
        minute: '16',
        hour: '10',
        day: '*',
        month: '*',
        year: '*',
        }),
    });

    const messagePayload2 = {
        "action": "e_merge"
    };

    mergeRule.addTarget(new targets.SqsQueue(this.scraperSQSQueue, {
      message: events.RuleTargetInput.fromObject(messagePayload2)
    }));

    ////// PUPPETEER QUEUE ////////

    // Create SQS queue
    this.puppetSqsQueue = new sqs.Queue(this, 'puppetSqsQueue', {
        visibilityTimeout: cdk.Duration.seconds(60*15),     // setting it to 15 minutes
        deadLetterQueue: {
            maxReceiveCount: 1, // Retry before moving to DLQ - TODO After testing change this to 3 or so
            queue: new sqs.Queue(this, 'puppet_DLQ', {
                queueName: 'puppetSqsDLQ',
                retentionPeriod: cdk.Duration.days(14), // Retain messages in DLQ for 14 days
            })
        },
    });


    // Outputs
    new cdk.CfnOutput(this, 'BucketName', {
        value: this.s3AstraBucket.bucketName,
        description: 'Astra S3 Bucket to store data',
      });
    new cdk.CfnOutput(this, 'ScraperBucketName', {
        value: this.s3ScraperBucket.bucketName,
        description: 'Scraper bucket for news indexing',
      });
  }
}
