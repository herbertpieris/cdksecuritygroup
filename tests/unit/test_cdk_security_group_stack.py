import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_security_group.cdk_security_group_stack import CdkSecurityGroupStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_security_group/cdk_security_group_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkSecurityGroupStack(app, "cdk-security-group")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
