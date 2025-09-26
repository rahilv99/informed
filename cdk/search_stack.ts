import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as dotenv from 'dotenv';

dotenv.config();

export class SearchStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Lambda from Docker image
    const searchLambda = new lambda.DockerImageFunction(this, "SearchLambda", {
      code: lambda.DockerImageCode.fromImageAsset('src/search-lambda'),
      memorySize: 1024,
      timeout: cdk.Duration.seconds(60),
      environment: {
        DB_URI: process.env.DB_URI!,
      },
    });

    // API Gateway
    const api = new apigateway.RestApi(this, "SearchApi", {
      restApiName: "Tags Search Service",
      description: "Clusters search results for specified tags.",
    });

    const searchIntegration = new apigateway.LambdaIntegration(searchLambda);
    const searchResource = api.root.addResource("search");
    searchResource.addMethod("GET", searchIntegration);
  }
}
