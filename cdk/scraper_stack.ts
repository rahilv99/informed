import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import { CoreStack } from "./core_stack";
import * as dotenv from 'dotenv';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subs from 'aws-cdk-lib/aws-sns-subscriptions';

dotenv.config();

interface ExtendedProps extends cdk.StackProps {
  readonly coreStack: CoreStack;
}

export class ScraperStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ExtendedProps) {
    super(scope, id, props);

    const logGroup = new logs.LogGroup(this, "ScraperLogGroup", {
      logGroupName: "ScraperLogGroup"
    });

    new logs.MetricFilter(this, 'RestartBrowserFilter', {
      logGroup,
      metricNamespace: 'Scraper/Metrics',
      metricName: 'RestartBrowser',
      filterPattern: logs.FilterPattern.literal('Restarting browser'),
      metricValue: '1',
    });

    const RestartBrowserMetric = new cloudwatch.Metric({
      namespace: 'Scraper/Metrics',
      metricName: 'RestartBrowser',
      statistic: 'Sum',
      period: cdk.Duration.hours(20),
    });

    new cloudwatch.Alarm(this, 'RestartBrowserAlarm', {
      metric: RestartBrowserMetric,
      threshold: 3,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when there the browser is restarted multiple times',
    });

    const RestartBrowserAlarmTopic = new sns.Topic(this, 'RestartBrowserAlarmTopic');
    RestartBrowserAlarmTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));

    new logs.MetricFilter(this, 'TimeoutFilter', {
      logGroup,
      metricNamespace: 'Scraper/Metrics',
      metricName: 'Timeout',
      filterPattern: logs.FilterPattern.literal('timeout'),
      metricValue: '1', // Value to emit when the pattern matches
    });

    const TimeoutMetric = new cloudwatch.Metric({
      namespace: 'Scraper/Metrics',
      metricName: 'Timeout',
      statistic: 'Sum',
      period: cdk.Duration.hours(20),
    });

    new cloudwatch.Alarm(this, 'TimeoutAlarm', {
      metric: TimeoutMetric,
      threshold: 10,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when there are many timeout events',
    });

    const TimeoutAlarmTopic = new sns.Topic(this, 'TimeoutAlarmTopic');
    TimeoutAlarmTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));

    new logs.MetricFilter(this, 'FailureFilter', {
      logGroup,
      metricNamespace: 'Scraper/Metrics',
      metricName: 'Failure',
      filterPattern: logs.FilterPattern.literal('Task timed out'),
      metricValue: '1', // Value to emit when the pattern matches
    });

    const FailureMetric = new cloudwatch.Metric({
      namespace: 'Scraper/Metrics',
      metricName: 'Failure',
      statistic: 'Sum',
      period: cdk.Duration.hours(20),
    });

    new cloudwatch.Alarm(this, 'FailureAlarm', {
      metric: FailureMetric,
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when scraper fails (exits early)',
    });

    const FailureAlarmTopic = new sns.Topic(this, 'FailureAlarmTopic');
    FailureAlarmTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));

    const lambdaFunction = new lambda.DockerImageFunction(this, 'ScraperFunction', {
      code: lambda.DockerImageCode.fromImageAsset('src/scraper/puppet'),
      timeout: cdk.Duration.minutes(15),
      memorySize: 3008,
      environment: {
       BUCKET_NAME: props.coreStack.s3ScraperBucket.bucketName
      },
      role: props.coreStack.ScraperLambdaRole,
      logGroup: logGroup
    });

    // Grant Lambda permissions to be triggered by the queue
    lambdaFunction.addEventSource(
        new lambdaEventSources.SqsEventSource(props.coreStack.puppetSqsQueue, {
        batchSize: 1, // Process one message at a time
        })
    );
  }
}
