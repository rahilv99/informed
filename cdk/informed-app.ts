import * as cdk from 'aws-cdk-lib';
import { CoreStack } from './core_stack';
import { ClustererStack } from './clusterer_stack';
import { CronStack } from './cron_stack';
import { ScraperStack } from './scraper_stack';
import { NlpStack } from './nlp_stack';

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION
}
console.log(`CDK Working with Account ${process.env.CDK_DEFAULT_ACCOUNT} Region ${process.env.CDK_DEFAULT_REGION}`);
const app = new cdk.App();

const coreStack = new CoreStack(app, "CoreStack", {env});
//new ClustererStack(app, 'ClustererStack', {env, coreStack});
//new CronStack(app, 'CronStack', {env, coreStack});
new ScraperStack(app, 'ScraperStack', {env, coreStack});
new NlpStack(app, 'NlpStack', {env, coreStack});