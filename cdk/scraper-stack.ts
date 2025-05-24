import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { LogGroup } from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';
import { CoreStack } from "./core_stack";
import * as dotenv from 'dotenv';

dotenv.config();

interface ExtendedProps extends cdk.StackProps {
  readonly coreStack: CoreStack;
}

export class ScraperStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ExtendedProps) {
    super(scope, id, props);

    const logGroup = new LogGroup(this, "ScraperLogGroup", {
      logGroupName: "ScraperLogGroup"
    })

    const lambdaFunction = new lambda.DockerImageFunction(this, 'ScraperFunction', {
      code: lambda.DockerImageCode.fromImageAsset('src/scraper'),
      timeout: cdk.Duration.minutes(15),
      memorySize: 2*1024,
      environment: {
        ASTRA_BUCKET_NAME: props.coreStack.s3AstraBucket.bucketName,
      },
      role: props.coreStack.astraLambdaRole,
      logGroup: logGroup
    });
  }
}
