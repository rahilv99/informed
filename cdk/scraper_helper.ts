import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import { LogGroup } from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';
import { CoreStack } from "./core_stack";
import * as dotenv from 'dotenv';

dotenv.config();

interface ExtendedProps extends cdk.StackProps {
  readonly coreStack: CoreStack;
}

export class ScraperHelperStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ExtendedProps) {
    super(scope, id, props);

    const logGroup = new LogGroup(this, "ScraperHelperLogGroup", {
      logGroupName: "ScraperHelperLogGroup"
    })

    const lambdaFunction = new lambda.DockerImageFunction(this, 'ScraperHelperFunction', {
      code: lambda.DockerImageCode.fromImageAsset('src/scraper/collector'),
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      environment: {
        ASTRA_BUCKET_NAME: props.coreStack.s3AstraBucket.bucketName,
        BUCKET_NAME: props.coreStack.s3ScraperBucket.bucketName,
        SCRAPER_QUEUE_URL: props.coreStack.scraperSQSQueue.queueUrl,
        PUPPET_QUEUE_URL: props.coreStack.puppetSqsQueue.queueUrl,
        GOVINFO_API_KEY: process.env.GOVINFO_API_KEY!,
      },
      role: props.coreStack.ScraperLambdaRole,
      logGroup: logGroup
    });

    // Grant Lambda permissions to send messages to the queue
    props.coreStack.scraperSQSQueue.grantSendMessages(lambdaFunction);
    props.coreStack.puppetSqsQueue.grantSendMessages(lambdaFunction);
    props.coreStack.astraSQSQueue.grantSendMessages(lambdaFunction);
    
    // Grant Lambda permissions to be triggered by the queue
    lambdaFunction.addEventSource(
        new lambdaEventSources.SqsEventSource(props.coreStack.scraperSQSQueue, {
        batchSize: 1, // Process one message at a time
        })
    );

  }
}
