import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { LogGroup } from 'aws-cdk-lib/aws-logs';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import { Construct } from 'constructs';
import { CoreStack } from "./core_stack";
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subs from 'aws-cdk-lib/aws-sns-subscriptions';
import * as cloudwatchActions from 'aws-cdk-lib/aws-cloudwatch-actions';


interface ExtendedProps extends cdk.StackProps {
  readonly coreStack: CoreStack;
}

export class CronStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ExtendedProps) {
    super(scope, id, props);

    const logGroup = new LogGroup(this, "CronLogGroup", {
      logGroupName: "CronLogGroup"
    })


    const lambdaFunction = new lambda.DockerImageFunction(this, 'CronFunction', {
      code: lambda.DockerImageCode.fromImageAsset('src/cron'),
      timeout: cdk.Duration.minutes(15),
      memorySize: 1*1024,
      environment: {
        ASTRA_QUEUE_URL: props.coreStack.astraSQSQueue.queueUrl,
        DB_ACCESS_URL: process.env.DB_ACCESS_URL!
      },
      role: props.coreStack.astraLambdaRole,
      logGroup: logGroup
    });

    const CronlambdaErrorMetric = lambdaFunction.metricErrors({
      period: cdk.Duration.hours(20),
      statistic: 'Sum',
    });

    // Alarm for Lambda function errors
    const CronLambdaFailureAlarm  = new cloudwatch.Alarm(this, 'CronLambdaFailureAlarm', {
      metric: CronlambdaErrorMetric,
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when Lambda function fails',
    });

    const CronLambdaFailureAlarmTopic = new sns.Topic(this, 'CronLambdaFailureAlarmTopic');
    CronLambdaFailureAlarmTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));
    CronLambdaFailureAlarm.addAlarmAction(new cloudwatchActions.SnsAction(CronLambdaFailureAlarmTopic));

    // Grant Lambda permissions to send messages to the queue
    props.coreStack.astraSQSQueue.grantSendMessages(lambdaFunction);

    // Create a CloudWatch Event Rule for the cron schedule
    const scheduleRule = new events.Rule(this, 'ScheduleRule', {
      schedule: events.Schedule.cron({
        minute: '0',
        hour: '11',
        day: '*',
        month: '*',
        year: '*',
      }),
    });
    // Add the Lambda function as the target of the Event Rule
    scheduleRule.addTarget(new targets.LambdaFunction(lambdaFunction));
  }
}
