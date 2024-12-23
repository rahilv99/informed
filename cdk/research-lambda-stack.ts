import * as cdk from 'aws-cdk-lib';
import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { PythonFunction, PythonFunctionProps } from '@aws-cdk/aws-lambda-python-alpha';

export class PythonLambdaStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // Define the Python Lambda function
    const pythonLambda = new PythonFunction(this, 'MyPythonLambda', {
      entry: './lambda', // Path to the folder containing lambda_handler.py and requirements.txt
      runtime: lambda.Runtime.PYTHON_3_12, // Python runtime
      handler: 'handler', // The name of the function in lambda_handler.py
      index: 'lambda_handler.py', // The main file of the Lambda function
    });

    // Optionally, add environment variables or permissions
    pythonLambda.addEnvironment('ENV_VAR_EXAMPLE', 'value');
  }
}



import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export class LambdaLayerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define the Lambda Layer
    const sharedLayer = new lambda.LayerVersion(this, 'SharedLayer', {
      code: lambda.Code.fromAsset('layer'), // Path to your layer directory
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_9], // Specify the runtime
      description: 'A shared layer containing utility functions',
    });

    // Define a Lambda Function that uses the Layer
    const myFunction = new lambda.Function(this, 'MyFunction', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'app.handler',
      code: lambda.Code.fromAsset('src'), // Path to your Lambda source code
      layers: [sharedLayer], // Attach the layer
    });

    // Add permissions or other configurations as needed
  }
}
