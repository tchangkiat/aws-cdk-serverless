#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_cdk_serverless.aws_cdk_serverless_stack import AwsCdkServerlessStack


app = cdk.App()
AwsCdkServerlessStack(app, "AwsCdkServerlessStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()
