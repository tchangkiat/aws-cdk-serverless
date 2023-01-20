from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_logs as logs,
)
from constructs import Construct

class ApiGatewayLambda(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_name='cdk-api-gateway-lambda'

        # ------------------------------------
        # Lambda Functions
        # ------------------------------------

        # Handles '/'
        fn_hello = _lambda.Function(self, "function_hello",
            code=_lambda.Code.from_asset('lambda_functions'),
            function_name=app_name+'-hello',
            handler='hello.handler',
            log_retention=logs.RetentionDays.THREE_DAYS,
            runtime=_lambda.Runtime.PYTHON_3_9,
        )

        # Handles '/products'
        fn_products = _lambda.Function(self, "function_products",
            code=_lambda.Code.from_asset('lambda_functions'),
            function_name=app_name+'-products',
            handler='products.handler',
            log_retention=logs.RetentionDays.THREE_DAYS,
            runtime=_lambda.Runtime.PYTHON_3_9,
        )

        # ------------------------------------
        # API Gateway
        # ------------------------------------

        # Creates a REST API in API Gateway
        api = apigw.RestApi(
            self, 'api',
            deploy=False,
            rest_api_name=app_name,
        )

        deployment_v1 = apigw.Deployment(self, "deployment_v1", api=api)
        deployment_v2 = apigw.Deployment(self, "deployment_v2", api=api)

        logs_v1 = logs.LogGroup(self, "logs_v1", log_group_name=app_name+"-v1-api-gateway-logs", retention=logs.RetentionDays.THREE_DAYS)
        logs_v2 = logs.LogGroup(self, "logs_v2", log_group_name=app_name+"-v2-api-gateway-logs", retention=logs.RetentionDays.THREE_DAYS)

        log_format = apigw.AccessLogFormat.json_with_standard_fields(
            caller=False,
            http_method=True,
            ip=True,
            protocol=True,
            request_time=True,
            resource_path=True,
            response_length=True,
            status=True,
            user=True
        )

        apigw.Stage(self, "stage_v1",
            deployment=deployment_v1,
            access_log_destination=apigw.LogGroupLogDestination(logs_v1),
            access_log_format=log_format,
            logging_level=apigw.MethodLoggingLevel.INFO,
            stage_name='v1'
        )

        apigw.Stage(self, "stage_v2",
            deployment=deployment_v2,
            access_log_destination=apigw.LogGroupLogDestination(logs_v2),
            access_log_format=log_format,
            logging_level=apigw.MethodLoggingLevel.INFO,
            stage_name='v2'
        )

        # Lambda Integration for '/'
        integration_hello = apigw.LambdaIntegration(fn_hello)
        api.root.add_method("GET", integration_hello)

        # Lambda Integration for '/products'
        integration_products = apigw.LambdaIntegration(fn_products)
        products = api.root.add_resource("products")
        products.add_method("GET", integration_products)