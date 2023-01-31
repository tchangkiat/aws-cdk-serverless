from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    aws_apigateway as apigw,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
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
            handler='hello.v1',
            log_retention=logs.RetentionDays.ONE_DAY,
            runtime=_lambda.Runtime.PYTHON_3_9,
        )
        # grant_invoke is required for API Gateway to invoke Lambda functions when using Stage Variables
        fn_hello.grant_invoke(iam.ServicePrincipal("apigateway.amazonaws.com"))

        fn_hello_v2 = _lambda.Function(self, "function_hello_v2",
            code=_lambda.Code.from_asset('lambda_functions'),
            function_name=app_name+'-hello-v2',
            handler='hello.v2',
            log_retention=logs.RetentionDays.ONE_DAY,
            runtime=_lambda.Runtime.PYTHON_3_9,
        )
        # grant_invoke is required for API Gateway to invoke Lambda functions when using Stage Variables
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

        # Creates a deployment in API Gateway
        deployment = apigw.Deployment(self, "deployment", api=api)

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

        # Creates a Stage for v1
        # logs_v1 = logs.LogGroup(self, "logs_v1", log_group_name=app_name+"-v1-api-gateway-logs", retention=logs.RetentionDays.ONE_DAY, removal_policy=RemovalPolicy.DESTROY)
        stage_v1 = apigw.Stage(self, "stage_v1",
            deployment=deployment,
            # access_log_destination=apigw.LogGroupLogDestination(logs_v1),
            # access_log_format=log_format,
            # logging_level=apigw.MethodLoggingLevel.INFO,
            stage_name='v1',
            variables=dict([("lambda", fn_hello.function_name)])
        )

        # Creates a Stage for v2
        # logs_v2 = logs.LogGroup(self, "logs_v2", log_group_name=app_name+"-v2-api-gateway-logs", retention=logs.RetentionDays.ONE_DAY, removal_policy=RemovalPolicy.DESTROY)
        stage_v2 = apigw.Stage(self, "stage_v2",
            deployment=deployment,
            # access_log_destination=apigw.LogGroupLogDestination(logs_v2),
            # access_log_format=log_format,
            # logging_level=apigw.MethodLoggingLevel.INFO,
            stage_name='v2',
            variables=dict([("lambda", fn_hello_v2.function_name)])
        )

        env = kwargs.get("env")

        # Integration for '/'
        # The following solution is a workaround to leverage API Gateway Stages for versioning as CDK does not support the use of Stage Variables natively (https://github.com/aws/aws-cdk/issues/6143).
        # Lambda Integration is not used because CDK will try to add an IAM permission to the ARN automatically, and the permission will not be valid. Hence, a role is created with the permission to invoke Lambda functions for the API Gateway.
        fn_hello_placeholder = _lambda.Function.from_function_arn(self, fn_hello.function_name + "-dynamic", "arn:aws:lambda:" + env.region + ":" + env.account + ":function:${stageVariables.lambda}")
        credentials_role = iam.Role(self, "hello-api-role", assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"))
        credentials_role.add_to_policy(iam.PolicyStatement(actions=["lambda:InvokeFunction"], resources=[fn_hello.function_arn, fn_hello_v2.function_arn], effect=iam.Effect.ALLOW))
        integration_hello = apigw.AwsIntegration(proxy=True, service="lambda", path="2015-03-31/functions/" + fn_hello_placeholder.function_arn + "/invocations", options=apigw.IntegrationOptions(credentials_role=credentials_role))
        api.root.add_method("GET", integration_hello)

        # Lambda Integration for '/products'
        integration_products = apigw.LambdaIntegration(fn_products)
        products = api.root.add_resource("products")
        products.add_method("GET", integration_products)

        # ------------------------------------
        # CloudWatch Dashboard
        # ------------------------------------

        cw_dashboard = cloudwatch.Dashboard(self, "cw-dashboard",
            dashboard_name=app_name,
            start="-PT3H"
        )

        apigw_metric_requests = api.metric_count(period=Duration.minutes(1), label="Requests")
        apigw_metric_latency = api.metric_latency(period=Duration.minutes(1), label="Latency")
        apigw_metric_4xx_errors = api.metric_client_error(period=Duration.minutes(1), label="Client (4xx) Errors")
        apigw_metric_5xx_errors = api.metric_client_error(period=Duration.minutes(1), label="Server (5xx) Errors")

        stage_v1_metric_requests = stage_v1.metric_count(period=Duration.minutes(1), label="v1 - Requests")
        stage_v1_metric_latency = stage_v1.metric_latency(period=Duration.minutes(1), label="v1 - Latency")
        stage_v1_metric_4xx_errors = stage_v1.metric_client_error(period=Duration.minutes(1), label="v1 - Client (4xx) Errors")
        stage_v1_metric_5xx_errors = stage_v1.metric_client_error(period=Duration.minutes(1), label="v1 - Server (5xx) Errors")

        stage_v2_metric_requests = stage_v2.metric_count(period=Duration.minutes(1), label="v2 - Requests")
        stage_v2_metric_latency = stage_v2.metric_latency(period=Duration.minutes(1), label="v2 - Latency")
        stage_v2_metric_4xx_errors = stage_v2.metric_client_error(period=Duration.minutes(1), label="v2 - Client (4xx) Errors")
        stage_v2_metric_5xx_errors = stage_v2.metric_client_error(period=Duration.minutes(1), label="v2 - Server (5xx) Errors")

        cw_dashboard.add_widgets(
            cloudwatch.GraphWidget(left=[apigw_metric_requests], title="Requests"),
            cloudwatch.GraphWidget(left=[apigw_metric_latency], title="Latency"),
            cloudwatch.GraphWidget(left=[apigw_metric_4xx_errors], title="Client (4xx) Errors"),
            cloudwatch.GraphWidget(left=[apigw_metric_5xx_errors], title="Server (5xx) Errors"),

            cloudwatch.GraphWidget(left=[stage_v1_metric_requests], title="v1 - Requests"),
            cloudwatch.GraphWidget(left=[stage_v1_metric_latency], title="v1 - Latency"),
            cloudwatch.GraphWidget(left=[stage_v1_metric_4xx_errors], title="v1 - Client (4xx) Errors"),
            cloudwatch.GraphWidget(left=[stage_v1_metric_5xx_errors], title="v1 - Server (5xx) Errors"),

            cloudwatch.GraphWidget(left=[stage_v2_metric_requests], title="v2 - Requests"),
            cloudwatch.GraphWidget(left=[stage_v2_metric_latency], title="v2 - Latency"),
            cloudwatch.GraphWidget(left=[stage_v2_metric_4xx_errors], title="v2 - Client (4xx) Errors"),
            cloudwatch.GraphWidget(left=[stage_v2_metric_5xx_errors], title="v2 - Server (5xx) Errors"),
        )