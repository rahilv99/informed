import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';
import { CoreStack } from "./core_stack";
import * as dotenv from 'dotenv';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subs from 'aws-cdk-lib/aws-sns-subscriptions';
import * as cloudwatchActions from 'aws-cdk-lib/aws-cloudwatch-actions';

dotenv.config();

interface ExtendedProps extends cdk.StackProps {
  readonly coreStack: CoreStack;
}

export class ScraperHelperStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ExtendedProps) {
    super(scope, id, props);

    const logGroup = new logs.LogGroup(this, "ScraperHelperLogGroup", {
      logGroupName: "ScraperHelperLogGroup"
    })

    new logs.MetricFilter(this, 'ErrorFilter', {
      logGroup,
      metricNamespace: 'ScraperHelper/Metrics',
      metricName: 'Error',
      filterPattern: logs.FilterPattern.literal('Error'),
      metricValue: '1',
    });

    const ErrorMetric = new cloudwatch.Metric({
      namespace: 'ScraperHelper/Metrics',
      metricName: 'Error',
      statistic: 'Sum',
      period: cdk.Duration.hours(20),
    });

    const ErrorAlarm = new cloudwatch.Alarm(this, 'ErrorAlarm', {
      metric: ErrorMetric,
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when scraper unexpected error occurs',
    });

    const ErrorAlarmTopic = new sns.Topic(this, 'ErrorAlarmTopic');
    ErrorAlarmTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));
    ErrorAlarm.addAlarmAction(new cloudwatchActions.SnsAction(ErrorAlarmTopic));
    
    new logs.MetricFilter(this, 'NoArticlesFilter', {
      logGroup,
      metricNamespace: 'ScraperHelper/Metrics',
      metricName: 'NoArticles',
      filterPattern: logs.FilterPattern.literal('No articles'),
      metricValue: '1',
    });

    const NoArticlesMetric = new cloudwatch.Metric({
      namespace: 'ScraperHelper/Metrics',
      metricName: 'NoArticles',
      statistic: 'Sum',
      period: cdk.Duration.hours(20),
    });

    const NoArticlesAlarm = new cloudwatch.Alarm(this, 'NoArticlesAlarm', {
      metric: NoArticlesMetric,
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when no articles are found from scraper',
    });

    const NoArticlesAlarmTopic = new sns.Topic(this, 'NoArticlesAlarmTopic');
    NoArticlesAlarmTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));
    NoArticlesAlarm.addAlarmAction(new cloudwatchActions.SnsAction(NoArticlesAlarmTopic));

    const lambdaFunction = new lambda.DockerImageFunction(this, 'ScraperHelperFunction', {
      code: lambda.DockerImageCode.fromImageAsset('src/scraper/collector'),
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      environment: {
        ASTRA_BUCKET_NAME: props.coreStack.s3AstraBucket.bucketName,
        BUCKET_NAME: props.coreStack.s3ScraperBucket.bucketName,
        SCRAPER_QUEUE_URL: props.coreStack.scraperSQSQueue.queueUrl,
        PUPPET_QUEUE_URL: props.coreStack.puppetSqsQueue.queueUrl,
        ASTRA_QUEUE_URL: props.coreStack.astraSQSQueue.queueUrl,
        GOVINFO_API_KEY: process.env.GOVINFO_API_KEY!,
      },
      role: props.coreStack.ScraperLambdaRole,
      logGroup: logGroup
    });

    const ScraperHelperlambdaErrorMetric = lambdaFunction.metricErrors({
      period: cdk.Duration.hours(20),
      statistic: 'Sum',
    });

    // Alarm for Lambda function errors
    const ScraperHelperLambdaFailureAlarm = new cloudwatch.Alarm(this, 'ScraperHelperLambdaFailureAlarm', {
      metric: ScraperHelperlambdaErrorMetric,
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when Lambda function fails',
    });

    const ScraperHelperLambdaFailureAlarmTopic = new sns.Topic(this, 'ScraperHelperLambdaFailureAlarmTopic');
    ScraperHelperLambdaFailureAlarmTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));
    ScraperHelperLambdaFailureAlarm.addAlarmAction(new cloudwatchActions.SnsAction(ScraperHelperLambdaFailureAlarmTopic));


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
