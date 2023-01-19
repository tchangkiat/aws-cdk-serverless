from aws_cdk import (
    # Duration,
    Stack,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_logs as logs,
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
        fn_hello.grant_invoke(iam.ServicePrincipal('apigateway.amazonaws.com'))

        # Handles '/products'
        fn_products = _lambda.Function(self, "function_products",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda_functions'),
            handler='products.handler',
            function_name=app_name+'-products',
        )
        fn_products.grant_invoke(iam.ServicePrincipal('apigateway.amazonaws.com'))

        # ------------------------------------
        # API Gateway
        # ------------------------------------

        # Creates a REST API in API Gateway
        apigw_logs_v1 = logs.LogGroup(self, "api_gateway_logs_v1", log_group_name=app_name+"-v1-api-gateway-logs", retention=logs.RetentionDays.THREE_DAYS)
        api = apigw.RestApi(
            self, 'api',
            deploy_options=apigw.StageOptions(
                access_log_destination=apigw.LogGroupLogDestination(apigw_logs_v1),
                access_log_format=apigw.AccessLogFormat.json_with_standard_fields(
                    caller=False,
                    http_method=True,
                    ip=True,
                    protocol=True,
                    request_time=True,
                    resource_path=True,
                    response_length=True,
                    status=True,
                    user=True
                ),
                logging_level=apigw.MethodLoggingLevel.INFO,
                stage_name='v1'
            ),
            rest_api_name=app_name,
        )
        deployment = apigw.Deployment(self, "Deployment", api=api)

        # Lambda Integration for '/'
        integration_hello = apigw.LambdaIntegration(fn_hello)
        api.root.add_method("GET", integration_hello)

        # Lambda Integration for '/products'
        integration_products = apigw.LambdaIntegration(fn_products)
        products = api.root.add_resource("products")
        products.add_method("GET", integration_products)

        apigw_logs_v2 = logs.LogGroup(self, "api_gateway_logs_v2", log_group_name=app_name+"-v2-api-gateway-logs", retention=logs.RetentionDays.THREE_DAYS)
        stage_v2 = apigw.Stage(self, "stage-v2",
            deployment=deployment,
            access_log_destination=apigw.LogGroupLogDestination(apigw_logs_v2),
            access_log_format=apigw.AccessLogFormat.json_with_standard_fields(
                caller=False,
                http_method=True,
                ip=True,
                protocol=True,
                request_time=True,
                resource_path=True,
                response_length=True,
                status=True,
                user=True
            ),
            logging_level=apigw.MethodLoggingLevel.INFO,
            stage_name='v2'
        )