from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as _s3,
    aws_s3_notifications,
    aws_lambda as _lambda,
    aws_iam as _iam,
    aws_logs as _logs,
    RemovalPolicy as _removalpolicy
    # aws_sqs as sqs,
)
from constructs import Construct

class CdkSecurityGroupStack(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        
        #IAM
        managedPolicyStatement = _iam.PolicyStatement(
            actions=["logs:*"],
            resources=["*"]
        )
        managedPolicy = _iam.ManagedPolicy(
                self,
                "cdkSecurityGroupPolicy",
                description="iam policy for lambda",
                managed_policy_name="cdkSecurityGroupPolicy"
            )
        managedPolicy.add_statements(managedPolicyStatement)
        managedPolicy.apply_removal_policy(_removalpolicy.DESTROY)

        lambdaRole = _iam.Role(
                self,
                "cdkSecurityGroupRole",
                assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com"),
                description="iam role for lambda",
                role_name="cdkSecurityGroupRole"
            )
        lambdaRole.add_managed_policy(managedPolicy)
        lambdaRole.apply_removal_policy(_removalpolicy.DESTROY)

        # Cloudwatch Log
        log_group = _logs.LogGroup(
            self,
            "cdkSecurityGroupFunctionLogGroup",
            log_group_name="/aws/lambda/cdkSecurityGroupFunction"
        )
        log_group.apply_removal_policy(_removalpolicy.DESTROY)

        #LAMBDA
        lambdaFunction = _lambda.Function(
                self,
                "cdkSecurityGroupFunction",
                function_name="cdkSecurityGroupFunction",
                runtime=_lambda.Runtime.PYTHON_3_9,
                handler="lambda-handler.main",
                code=_lambda.Code.from_asset("./lambda"),
                role=lambdaRole
            )
        lambdaFunction.apply_removal_policy(_removalpolicy.DESTROY)

        #S3
        bucket = _s3.Bucket(
                self,
                "hapcdktestbucket",
                bucket_name="hapcdktestbucket"
            )
        bucket.apply_removal_policy(_removalpolicy.DESTROY)
        
        s3notification = aws_s3_notifications.lambdaDestination(lambdaFunction)
        _s3.add_event_notification(_s3.EventType.OBJECT_CREATED, s3notification)
