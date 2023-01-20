import aws_cdk as cdk
import os
from constructs import Construct
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from stacks.pipeline_app_stage import ApiGatewayLambdaStage

class Pipeline(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        pipeline = CodePipeline(self, "pipeline", 
                        pipeline_name="aws-cdk-serverless-pipeline",
                        synth=ShellStep("synth", 
                            input=CodePipelineSource.git_hub("tchangkiat/aws-cdk-serverless", "main"),
                            commands=["npm install -g aws-cdk", 
                                "python -m pip install -r requirements.txt", 
                                "cdk synth"]
                        )
                    )

        pipeline.add_stage(ApiGatewayLambdaStage(self, "api-gateway-lambda-stage",
            env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))))