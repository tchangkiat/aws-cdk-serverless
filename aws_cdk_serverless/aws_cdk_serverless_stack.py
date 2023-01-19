from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)
from constructs import Construct

class AwsCdkServerlessStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_name='app'

        # ------------------------------------
        # Lambda Functions
        # ------------------------------------

        fn_hello = _lambda.Function(self, "function_hello",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda_functions'),
            handler='hello.handler',
            function_name=app_name+'-hello',
        )
        fn_products = _lambda.Function(self, "function_products",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda_functions'),
            handler='products.handler',
            function_name=app_name+'-products',
        )

        # ------------------------------------
        # API Gateway
        # ------------------------------------

        api = apigw.RestApi(
            self, 'api',
            rest_api_name=app_name,
        )

        # Lambda Integration with 'Hello' function
        integration_hello = apigw.LambdaIntegration(fn_hello)
        api.root.add_method("GET", integration_hello)

        # Lambda Integration with 'Products' function
        integration_products = apigw.LambdaIntegration(fn_products)
        products = api.root.add_resource("products")
        products.add_method("GET", integration_products)
