import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import { Construct } from 'constructs';
import { CoreStack } from "./core_stack";
import * as dotenv from 'dotenv';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subs from 'aws-cdk-lib/aws-sns-subscriptions';
import * as cloudwatchActions from 'aws-cdk-lib/aws-cloudwatch-actions';
import { Platform } from 'aws-cdk-lib/aws-ecr-assets';

dotenv.config();

interface ExtendedProps extends cdk.StackProps {
  readonly coreStack: CoreStack;
}

export class ClustererStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ExtendedProps) {
    super(scope, id, props);

    const logGroup = new logs.LogGroup(this, "ClustererLogGroup", {
      logGroupName: "ClustererLogGroup",
      retention: cdk.aws_logs.RetentionDays.ONE_MONTH
    })

    new logs.MetricFilter(this, 'DBErrorFilter', {
      logGroup,
      metricNamespace: 'Clusterer/Metrics',
      metricName: 'DBError',
      filterPattern: logs.FilterPattern.literal('Error inserting clusters'),
      metricValue: '1',
    });

    const DBErrorMetric = new cloudwatch.Metric({
      namespace: 'Clusterer/Metrics',
      metricName: 'DBError',
      statistic: 'Sum',
      period: cdk.Duration.hours(20),
    });

    const DBErrorAlarm = new cloudwatch.Alarm(this, 'DBErrorAlarm', {
      metric: DBErrorMetric,
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when there is a database error',
    });

    const dberrorTopic = new sns.Topic(this, 'DBErrorAlarmTopic');
    dberrorTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));
    DBErrorAlarm.addAlarmAction(new cloudwatchActions.SnsAction(dberrorTopic))

    new logs.MetricFilter(this, 'RecommendationSizeFilter', {
      logGroup,
      metricNamespace: 'Clusterer/Metrics',
      metricName: 'RecommendationSize',
      filterPattern: logs.FilterPattern.literal('Low number of recommendations'),
      metricValue: '1',
    });

    const RecommendationSizeMetric = new cloudwatch.Metric({
      namespace: 'Clusterer/Metrics',
      metricName: 'RecommendationSize',
      statistic: 'Sum',
      period: cdk.Duration.hours(20),
    });

    const RecommendationSizeAlarm = new cloudwatch.Alarm(this, 'RecommendationSizeAlarm', {
      metric: RecommendationSizeMetric,
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when there is a database error',
    });

    const RecommendationSizeAlarmTopic = new sns.Topic(this, 'RecommendationSizeAlarmTopic');
    RecommendationSizeAlarmTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));
    RecommendationSizeAlarm.addAlarmAction(new cloudwatchActions.SnsAction(RecommendationSizeAlarmTopic))

    const lambdaFunction = new lambda.DockerImageFunction(this, 'ClustererFunction', {
      code: lambda.DockerImageCode.fromImageAsset('src/clusterer-lambda', {
        platform: Platform.LINUX_AMD64,
      }),
      timeout: cdk.Duration.minutes(15),
      memorySize: 2048,
      environment: {
        BUCKET_NAME: props.coreStack.s3Bucket.bucketName,
        CLUSTERER_QUEUE_URL: props.coreStack.clustererSQSQueue.queueUrl,
        NLP_QUEUE_URL: props.coreStack.nlpSQSQueue.queueUrl,
        DB_ACCESS_URL: process.env.DB_ACCESS_URL!,
        GOOGLE_API_KEY: process.env.GOOGLE_API_KEY!
      },
      role: props.coreStack.generalLambdaRole,
      logGroup: logGroup
    });

    const ClustererlambdaErrorMetric = lambdaFunction.metricErrors({
      period: cdk.Duration.hours(20),
      statistic: 'Sum',
    });

    // Alarm for Lambda function errors
    const ClustererLambdaFailureAlarm = new cloudwatch.Alarm(this, 'ClustererLambdaFailureAlarm', {
      metric: ClustererlambdaErrorMetric,
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when Lambda function fails',
    });

    const ClustererLambdaFailureAlarmTopic = new sns.Topic(this, 'ClustererLambdaFailureAlarmTopic');
    ClustererLambdaFailureAlarmTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));
    ClustererLambdaFailureAlarm.addAlarmAction(new cloudwatchActions.SnsAction(ClustererLambdaFailureAlarmTopic))

    // Grant Lambda permissions to send messages to the queue
    props.coreStack.clustererSQSQueue.grantSendMessages(lambdaFunction);
    props.coreStack.nlpSQSQueue.grantSendMessages(lambdaFunction);

    // Grant Lambda permissions to be triggered by the queue
    lambdaFunction.addEventSource(
      new lambdaEventSources.SqsEventSource(props.coreStack.clustererSQSQueue, {
        batchSize: 1, // Process one message at a time
      })
    );
  }
}
