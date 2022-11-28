from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as _s3,
    aws_s3_notifications,
    aws_lambda as _lambda,
    aws_iam as _iam,
    RemovalPolicy as _removalpolicy
    # aws_sqs as sqs,
)
from constructs import Construct

class CdkSecurityGroupStack(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        
        #IAM
        lambdaRole = _iam.Role(self,
                               "Role",
                               assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com"),
                               description="iam role for lambda"
                            )

        lambdaRole.apply_removal_policy(_removalpolicy.DESTROY)

        #LAMBDA
        function = _lambda.Function(self,
                                    "lambda_function",
                                    function_name="lambda_function",
                                    runtime=_lambda.Runtime.PYTHON_3_9,
                                    handler="lambda-handler.main",
                                    code=_lambda.Code.from_asset("./lambda"),
                                    role=lambdaRole
                                    )

        function.apply_removal_policy(_removalpolicy.DESTROY)

        #S3
        bucket = _s3.Bucket(self, 
                            "hapcdktestbucket",
                            bucket_name="hapcdktestbucket"
                            )
        bucket.apply_removal_policy(_removalpolicy.DESTROY)
        
        #notification = aws_s3_notifications.lambdaDestination(function)
        #_s3.add_event_notification(_s3.EventType.OBJECT_CREATED, notification)

        # example resource
        # queue = sqs.Queue(
        #     self, "CdkSecurityGroupQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
