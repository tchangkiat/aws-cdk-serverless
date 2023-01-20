#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.serverless import ApiGatewayLambda
from stacks.pipeline import Pipeline

app = cdk.App()

# Uncomment if using 'cdk deploy'
ApiGatewayLambda(app, "cdk-api-gateway-lambda", env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')))

# Uncomment if using a pipeline to deploy when a commit is made to the code repository
#Pipeline(app, "aws-cdk-serverless-pipeline", env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')))

app.synth()
