#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_cdk_serverless.serverless_stack import ServerlessStack


app = cdk.App()
ServerlessStack(app, "cdk-serverless-app",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()
