import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import { LambdaLayerStack } from './lambda-layer-stack';
import { ServiceTierLambdaStack } from './service_tier_stack';

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION
}
const app = new cdk.App();

new ServiceTierLambdaStack(app, 'ServiceTierStack', {env})
