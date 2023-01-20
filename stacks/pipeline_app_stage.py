import aws_cdk as cdk
from constructs import Construct
from stacks.serverless import ApiGatewayLambda

class ApiGatewayLambdaStage(cdk.Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ApiGatewayLambda(self, "api-gateway-lambda-stack")