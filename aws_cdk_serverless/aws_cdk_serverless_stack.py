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

        # Handles '/'
        fn_hello = _lambda.Function(self, "function_hello",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda_functions'),
            handler='hello.handler',
            function_name=app_name+'-hello',
        )

        # Handles '/products/v1'
        fn_products_v1 = _lambda.Function(self, "function_products_v1",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda_functions'),
            handler='products.v1',
            function_name=app_name+'-products-v1',
        )

        # Handles '/products/v2'
        fn_products_v2 = _lambda.Function(self, "function_products_v2",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda_functions'),
            handler='products.v2',
            function_name=app_name+'-products-v2',
        )

        # ------------------------------------
        # API Gateway
        # ------------------------------------

        # Creates a REST API in API Gateway
        api = apigw.RestApi(
            self, 'api',
            rest_api_name=app_name,
        )

        # Lambda Integration for root
        integration_hello = apigw.LambdaIntegration(fn_hello)
        api.root.add_method("GET", integration_hello)

        # Add resource for '/products'
        products = api.root.add_resource("products")

        # Lambda Integration for '/products/v1'
        integration_products_v1 = apigw.LambdaIntegration(fn_products_v1)
        products_v1 = products.add_resource("v1")
        products_v1.add_method("GET", integration_products_v1)

        # Lambda Integration for '/products/v2'
        integration_products_v2 = apigw.LambdaIntegration(fn_products_v2)
        products_v2 = products.add_resource("v2")
        products_v2.add_method("GET", integration_products_v2)
