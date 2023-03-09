from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as _s3,
    aws_s3_notifications as s3n,
    aws_lambda as _lambda,
    aws_lambda_event_sources as eventsources,
    aws_iam as _iam,
    aws_logs as _logs,
    aws_dynamodb as _dynamodb,
    RemovalPolicy as _removalpolicy,
    Duration as _duration
    # aws_sqs as sqs,
)
from constructs import Construct

class CdkSecurityGroupStack(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        
        #IAM
        # createemptysecuritygroup
        createEmptySecurityGroupPolicyStatement = _iam.PolicyStatement(
            actions=[
                "logs:*",
                "ec2:Describe*",
                "ec2:List*",
                "ec2:Get*",
                "ec2:CreateSecurityGroup",
                "s3:Describe*",
                "s3:List*",
                "s3:Get*"                
            ],
            resources=["*"]
        )
        createEmptySecurityGroupmanagedPolicy = _iam.ManagedPolicy(
                self,
                "createEmptySecurityGroupPolicy",
                description="iam policy for lambda create empty security group",
                managed_policy_name="createEmptySecurityGroupPolicy"
            )
        createEmptySecurityGroupmanagedPolicy.add_statements(createEmptySecurityGroupPolicyStatement)
        createEmptySecurityGroupmanagedPolicy.apply_removal_policy(_removalpolicy.DESTROY)

        createemptysecuritygroupLambdaRole = _iam.Role(
                self,
                "createemptysecuritygroupRole",
                assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com"),
                description="iam role for lambda create empty security group",
                role_name="createemptysecuritygroupRole"
            )
        createemptysecuritygroupLambdaRole.add_managed_policy(createEmptySecurityGroupmanagedPolicy)
        createemptysecuritygroupLambdaRole.apply_removal_policy(_removalpolicy.DESTROY)     

        # createsecuritygroup
        createSecurityGroupPolicyStatement = _iam.PolicyStatement(
            actions=[
                "logs:*",
                "ec2:Describe*",
                "ec2:List*",
                "ec2:Get*",
                "ec2:CreateSecurityGroup",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:AuthorizeSecurityGroupEgress",
                "ec2:RevokeSecurityGroupIngress",
                "ec2:RevokeSecurityGroupEgress",
                "s3:Describe*",
                "s3:List*",
                "s3:Get*"
            ],
            resources=["*"]
        )
        createSecurityGroupmanagedPolicy = _iam.ManagedPolicy(
                self,
                "createSecurityGroupPolicy",
                description="iam policy for lambda create security group",
                managed_policy_name="createSecurityGroupPolicy"
            )
        createSecurityGroupmanagedPolicy.add_statements(createSecurityGroupPolicyStatement)
        createSecurityGroupmanagedPolicy.apply_removal_policy(_removalpolicy.DESTROY)

        createsecuritygroupLambdaRole = _iam.Role(
                self,
                "createsecuritygroupRole",
                assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com"),
                description="iam role for lambda create security group",
                role_name="createsecuritygroupRole"
            )
        createsecuritygroupLambdaRole.add_managed_policy(createSecurityGroupmanagedPolicy)
        createsecuritygroupLambdaRole.apply_removal_policy(_removalpolicy.DESTROY)

        # deletesecuritygroup
        deleteSecurityGroupPolicyStatement = _iam.PolicyStatement(
            actions=[
                "logs:*",
                "ec2:Describe*",
                "ec2:List*",
                "ec2:Get*",
                "ec2:DeleteSecurityGroup",
                "s3:Describe*",
                "s3:List*",
                "s3:Get*"
            ],
            resources=["*"]
        )
        deleteSecurityGroupmanagedPolicy = _iam.ManagedPolicy(
                self,
                "deleteSecurityGroupPolicy",
                description="iam policy for lambda delete security group",
                managed_policy_name="deleteSecurityGroupPolicy"
            )
        deleteSecurityGroupmanagedPolicy.add_statements(deleteSecurityGroupPolicyStatement)
        deleteSecurityGroupmanagedPolicy.apply_removal_policy(_removalpolicy.DESTROY)

        deletesecuritygroupLambdaRole = _iam.Role(
                self,
                "deletesecuritygroupRole",
                assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com"),
                description="iam role for lambda delete security group",
                role_name="deletesecuritygroupRole"
            )
        deletesecuritygroupLambdaRole.add_managed_policy(deleteSecurityGroupmanagedPolicy)
        deletesecuritygroupLambdaRole.apply_removal_policy(_removalpolicy.DESTROY)        

        # modifysecuritygroup
        modifySecurityGroupPolicyStatement = _iam.PolicyStatement(
            actions=[
                "logs:*",
                "ec2:Describe*",
                "ec2:List*",
                "ec2:Get*",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:AuthorizeSecurityGroupEgress",
                "ec2:RevokeSecurityGroupIngress",
                "ec2:RevokeSecurityGroupEgress",
                "s3:Describe*",
                "s3:List*",
                "s3:Get*"
            ],
            resources=["*"]
        )
        modifySecurityGroupmanagedPolicy = _iam.ManagedPolicy(
                self,
                "modifySecurityGroupPolicy",
                description="iam policy for lambda modify security group",
                managed_policy_name="modifySecurityGroupPolicy"
            )
        modifySecurityGroupmanagedPolicy.add_statements(modifySecurityGroupPolicyStatement)
        modifySecurityGroupmanagedPolicy.apply_removal_policy(_removalpolicy.DESTROY)

        modifysecuritygroupLambdaRole = _iam.Role(
                self,
                "modifysecuritygroupRole",
                assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com"),
                description="iam role for lambda modify security group",
                role_name="modifysecuritygroupRole"
            )
        modifysecuritygroupLambdaRole.add_managed_policy(modifySecurityGroupmanagedPolicy)
        modifysecuritygroupLambdaRole.apply_removal_policy(_removalpolicy.DESTROY)

        #S3
        bucket = _s3.Bucket(
                self,
                "cdksecuritygroupbucket",
                bucket_name="cdksecuritygroupbucket"
            )
        bucket.apply_removal_policy(_removalpolicy.DESTROY)

        # Cloudwatch Log
        createEmptySecurityGroupLogGroup = _logs.LogGroup(
            self,
            "createemptysecuritygroupLogGroup",
            log_group_name="/aws/lambda/createEmptySecurityGroup"
        )
        createEmptySecurityGroupLogGroup.apply_removal_policy(_removalpolicy.DESTROY)

        createSecurityGroupLogGroup = _logs.LogGroup(
            self,
            "createsecuritygroupLogGroup",
            log_group_name="/aws/lambda/createSecurityGroup"
        )
        createSecurityGroupLogGroup.apply_removal_policy(_removalpolicy.DESTROY)

        deleteSecurityGroupLogGroup = _logs.LogGroup(
            self,
            "deletesecuritygroupLogGroup",
            log_group_name="/aws/lambda/deleteSecurityGroup"
        )
        deleteSecurityGroupLogGroup.apply_removal_policy(_removalpolicy.DESTROY)
        
        modifySecurityGroupLogGroup = _logs.LogGroup(
            self,
            "modifysecuritygroupLogGroup",
            log_group_name="/aws/lambda/modifySecurityGroup"
        )
        modifySecurityGroupLogGroup.apply_removal_policy(_removalpolicy.DESTROY)                        

        #LAMBDA
        # createEmptySecurityGroupFunction = _lambda.Function(
        #         self,
        #         "createEmptySecurityGroupFunction",
        #         function_name="createEmptySecurityGroupFunction",
        #         runtime=_lambda.Runtime.PYTHON_3_9,
        #         handler="createEmptySecurityGroupFunction.main",
        #         code=_lambda.Code.from_asset("./lambdas/createemptysecuritygroup"),
        #         role=createemptysecuritygroupLambdaRole,
        #         timeout=_duration.seconds(300)
        #     )
        # createEmptySecurityGroupFunction.add_event_source(
        #     eventsources.S3EventSource(
        #         bucket,
        #         events=[
        #             _s3.EventType.OBJECT_CREATED
        #         ]
        #     )
        # )
        # createEmptySecurityGroupFunction.apply_removal_policy(_removalpolicy.DESTROY)        

        # s3notification = aws_s3_notifications.lambdaDestination(lambdaFunction)
        # _s3.Bucket.add_event_notification(_s3.EventType.OBJECT_CREATED, s3n.LambdaDestination(lambdaFunction))