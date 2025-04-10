import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { LogGroup } from 'aws-cdk-lib/aws-logs';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import { Construct } from 'constructs';
import { CoreStack } from "./core_stack";
import * as ecr from 'aws-cdk-lib/aws-ecr';

interface ExtendedProps extends cdk.StackProps {
  readonly coreStack: CoreStack;
}

export class CronStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ExtendedProps) {
    super(scope, id, props);

    const logGroup = new LogGroup(this, "CronLogGroup", {
      logGroupName: "CronLogGroup"
    })

    // Update if changing requirements.txt
    const imageTag = '67158f1876b4364f92707ad9108a7db00f77092778c04901eb27793c16b4d296'
    const repo_name = 'cdk-hnb659fds-container-assets-905418457861-us-east-1'

    const ecrRepo = ecr.Repository.fromRepositoryName(this, 'FunctionEcrRepo', repo_name);

    const lambdaFunction = new lambda.DockerImageFunction(this, 'CronFunction', {
      code: lambda.DockerImageCode.fromImageAsset('src/cron'),
      //code: lambda.DockerImageCode.fromEcr(ecrRepo, {
      //  tagOrDigest: imageTag,
      //}),
      timeout: cdk.Duration.minutes(15),
      memorySize: 1*1024,
      environment: {
        ASTRA_QUEUE_URL: props.coreStack.astraSQSQueue.queueUrl,
        DB_ACCESS_URL: process.env.DB_ACCESS_URL!
      },
      role: props.coreStack.astraLambdaRole,
      logGroup: logGroup
    });

    // Grant Lambda permissions to send messages to the queue
    props.coreStack.astraSQSQueue.grantSendMessages(lambdaFunction);

    // Create a CloudWatch Event Rule for the cron schedule
    const scheduleRule = new events.Rule(this, 'ScheduleRule', {
      schedule: events.Schedule.cron({
        minute: '0', // Run every hour at the top of the hour
        hour: '*',
        day: '*',
        month: '*',
        year: '*',
      }),
    });
    // Add the Lambda function as the target of the Event Rule
    scheduleRule.addTarget(new targets.LambdaFunction(lambdaFunction));
  }
}
