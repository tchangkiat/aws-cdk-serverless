#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.serverless import ApiGatewayLambda


app = cdk.App()
ApiGatewayLambda(app, "cdk-serverless-app",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()
