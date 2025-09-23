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

export class NlpStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ExtendedProps) {
    super(scope, id, props);

    const logGroup = new logs.LogGroup(this, "NlpLogGroup", {
      logGroupName: "NlpLogGroup",
      retention: cdk.aws_logs.RetentionDays.ONE_MONTH
    })

    const lambdaFunction = new lambda.DockerImageFunction(this, 'NlpFunction', {
      code: lambda.DockerImageCode.fromImageAsset('src/nlp-lambda', {
        platform: Platform.LINUX_AMD64,
      }),
      timeout: cdk.Duration.minutes(15),
      memorySize: 2048,
      environment: {
        BUCKET_NAME: props.coreStack.s3Bucket.bucketName,
        CLUSTERER_QUEUE_URL: props.coreStack.clustererSQSQueue.queueUrl,
        NLP_QUEUE_URL: props.coreStack.nlpSQSQueue.queueUrl,
        DB_ACCESS_URL: process.env.DB_ACCESS_URL!,
        GOOGLE_API_KEY: process.env.GOOGLE_API_KEY!,
      },
      role: props.coreStack.generalLambdaRole,
      logGroup: logGroup
    });

    const NlplambdaErrorMetric = lambdaFunction.metricErrors({
      period: cdk.Duration.hours(20),
      statistic: 'Sum',
    });

    // Alarm for Lambda function errors
    const NlpLambdaFailureAlarm = new cloudwatch.Alarm(this, 'NlpLambdaFailureAlarm', {
      metric: NlplambdaErrorMetric,
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      alarmDescription: 'Alarm when Lambda function fails',
    });

    const NlpLambdaFailureAlarmTopic = new sns.Topic(this, 'NlpLambdaFailureAlarmTopic');
    NlpLambdaFailureAlarmTopic.addSubscription(new subs.EmailSubscription('rahilv99@gmail.com'));
    NlpLambdaFailureAlarm.addAlarmAction(new cloudwatchActions.SnsAction(NlpLambdaFailureAlarmTopic))

    // Grant Lambda permissions to send messages to the queue
    props.coreStack.nlpSQSQueue.grantSendMessages(lambdaFunction);

    // Grant Lambda permissions to be triggered by the queue
    lambdaFunction.addEventSource(
      new lambdaEventSources.SqsEventSource(props.coreStack.nlpSQSQueue, {
        batchSize: 1, // Process one message at a time
      })
    );
  }
}
