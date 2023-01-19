from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
)
from constructs import Construct

class AwsCdkServerlessStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        _lambda.Function(self, "function_hello",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda_functions'),
            handler='hello.handler',
            function_name='hello',
        )
