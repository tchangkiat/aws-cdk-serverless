from aws_cdk import (
    Stack,
    Environment,
    RemovalPolicy,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_logs as logs,
)
from constructs import Construct

class ApiGatewayLambda(Stack):

    def __init__(self, scope: Construct, construct_id: str, env: Environment, **kwargs) -> None:
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
            log_retention=logs.RetentionDays.ONE_DAY,
            runtime=_lambda.Runtime.PYTHON_3_9,
        )
        fn_hello.grant_invoke(iam.ServicePrincipal("apigateway.amazonaws.com"))

        fn_hello_v2 = _lambda.Function(self, "function_hello_v2",
            code=_lambda.Code.from_asset('lambda_functions'),
            function_name=app_name+'-hello-v2',
            handler='hello_v2.handler',
            log_retention=logs.RetentionDays.ONE_DAY,
            runtime=_lambda.Runtime.PYTHON_3_9,
        )
        fn_hello_v2.grant_invoke(iam.ServicePrincipal("apigateway.amazonaws.com"))

        # Handles '/products'
        fn_products = _lambda.Function(self, "function_products",
            code=_lambda.Code.from_asset('lambda_functions'),
            function_name=app_name+'-products',
            handler='products.handler',
            log_retention=logs.RetentionDays.ONE_DAY,
            runtime=_lambda.Runtime.PYTHON_3_9,
        )

        # ------------------------------------
        # API Gateway
        # ------------------------------------

        # Creates a REST API in API Gateway
        api = apigw.RestApi(
            self, 'api',
            # cloud_watch_role=True,
            deploy=False,
            rest_api_name=app_name,
        )

        deployment_v1 = apigw.Deployment(self, "deployment_v1", api=api)
        deployment_v2 = apigw.Deployment(self, "deployment_v2", api=api)

        # logs_v1 = logs.LogGroup(self, "logs_v1", log_group_name=app_name+"-v1-api-gateway-logs", retention=logs.RetentionDays.ONE_DAY, removal_policy=RemovalPolicy.DESTROY)
        # logs_v2 = logs.LogGroup(self, "logs_v2", log_group_name=app_name+"-v2-api-gateway-logs", retention=logs.RetentionDays.ONE_DAY, removal_policy=RemovalPolicy.DESTROY)

        # log_format = apigw.AccessLogFormat.json_with_standard_fields(
        #     caller=False,
        #     http_method=True,
        #     ip=True,
        #     protocol=True,
        #     request_time=True,
        #     resource_path=True,
        #     response_length=True,
        #     status=True,
        #     user=True
        # )

        apigw.Stage(self, "stage_v1",
            deployment=deployment_v1,
            # access_log_destination=apigw.LogGroupLogDestination(logs_v1),
            # access_log_format=log_format,
            # logging_level=apigw.MethodLoggingLevel.INFO,
            stage_name='v1',
            variables=dict([("lambda", fn_hello.function_name)])
        )

        apigw.Stage(self, "stage_v2",
            deployment=deployment_v2,
            # access_log_destination=apigw.LogGroupLogDestination(logs_v2),
            # access_log_format=log_format,
            # logging_level=apigw.MethodLoggingLevel.INFO,
            stage_name='v2',
            variables=dict([("lambda", fn_hello_v2.function_name)])
        )

        # Integration for '/'
        # The following solution is a workaround to leverage API Gateway Stages for versioning as CDK does not support the use of Stage Variables natively (https://github.com/aws/aws-cdk/issues/6143).
        # Lambda Integration is not used because CDK will try to add an IAM permission to the ARN automatically, and the permission will not be valid. Hence, a role is created with the permission to invoke Lambda functions for the API Gateway.
        fn_hello_placeholder = _lambda.Function.from_function_arn(self, fn_hello.function_name + "-dynamic", "arn:aws:lambda:" + env.region + ":" + env.account + ":function:${stageVariables.lambda}")
        credentials_role = iam.Role(self, "api-gateway-api-role", assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"))
        credentials_role.add_to_policy(iam.PolicyStatement(actions=["lambda:InvokeFunction"], resources=[fn_hello.function_arn, fn_hello_v2.function_arn], effect=iam.Effect.ALLOW))
        integration_hello = apigw.AwsIntegration(proxy=True, service="lambda", path="2015-03-31/functions/" + fn_hello_placeholder.function_arn + "/invocations", options=apigw.IntegrationOptions(credentials_role=credentials_role))
        api.root.add_method("GET", integration_hello)

        # Lambda Integration for '/products'
        integration_products = apigw.LambdaIntegration(fn_products)
        products = api.root.add_resource("products")
        products.add_method("GET", integration_products)