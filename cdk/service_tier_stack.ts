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

dotenv.config();

interface ExtendedProps extends cdk.StackProps {
  readonly coreStack: CoreStack;
}

export class ServiceTierLambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ExtendedProps) {
    super(scope, id, props);

    const logGroup = new logs.LogGroup(this, "ServiceTierLogGroup", {
      logGroupName: "ServiceTierLogGroup"
    })

    new logs.MetricFilter(this, 'DBErrorFilter', {
      logGroup,
      metricNamespace: 'ServiceTier/Metrics',
      metricName: 'DBError',
      filterPattern: logs.FilterPattern.literal('Error inserting clusters'),
      metricValue: '1',
    });

    const DBErrorMetric = new cloudwatch.Metric({
      namespace: 'ServiceTier/Metrics',
      metricName: 'DBError',
      statistic: 'Sum',
      period: cdk.Duration.hours(20),
    });

    new cloudwatch.Alarm(this, 'DBErrorAlarm', {
      metric: DBErrorMetric,
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when there is a database error',
    });

    const dberrorTopic = new sns.Topic(this, 'DBErrorAlarmTopic');
    dberrorTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));

    new logs.MetricFilter(this, 'RecommendationSizeFilter', {
      logGroup,
      metricNamespace: 'ServiceTier/Metrics',
      metricName: 'RecommendationSize',
      filterPattern: logs.FilterPattern.literal('Warning: Low number of recommendations'),
      metricValue: '1',
    });

    const RecommendationSizeMetric = new cloudwatch.Metric({
      namespace: 'ServiceTier/Metrics',
      metricName: 'RecommendationSize',
      statistic: 'Sum',
      period: cdk.Duration.hours(20),
    });

    new cloudwatch.Alarm(this, 'RecommendationSizeAlarm', {
      metric: RecommendationSizeMetric,
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when there is a database error',
    });

    const RecommendationSizeAlarmTopic = new sns.Topic(this, 'RecommendationSizeAlarmTopic');
    RecommendationSizeAlarmTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));

    const lambdaFunction = new lambda.DockerImageFunction(this, 'ServiceTierFunction', {
      code: lambda.DockerImageCode.fromImageAsset('src/service_tier'),
      timeout: cdk.Duration.minutes(15),
      memorySize: 2*1024,
      environment: {
        ASTRA_BUCKET_NAME: props.coreStack.s3AstraBucket.bucketName,
        ASTRA_QUEUE_URL: props.coreStack.astraSQSQueue.queueUrl,
        OPENAI_API_KEY: process.env.OPENAI_API_KEY!,
        GOVINFO_API_KEY: process.env.GOVINFO_API_KEY!,
        DB_ACCESS_URL: process.env.DB_ACCESS_URL!,
        TAVILY_API_KEY: process.env.TAVILY_API_KEY!,
        GOOGLE_API_KEY: process.env.GOOGLE_API_KEY!,
        VOYAGE_API_KEY: process.env.VOYAGE_API_KEY!
      },
      role: props.coreStack.astraLambdaRole,
      logGroup: logGroup
    });

    // Grant Lambda permissions to send messages to the queue
    props.coreStack.astraSQSQueue.grantSendMessages(lambdaFunction);

    // Grant Lambda permissions to be triggered by the queue
    lambdaFunction.addEventSource(
      new lambdaEventSources.SqsEventSource(props.coreStack.astraSQSQueue, {
        batchSize: 1, // Process one message at a time
      })
    );
  }
}
