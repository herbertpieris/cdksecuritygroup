import aws_cdk as core
import aws_cdk.assertions as assertions

from cdksecuritygroup.cdksecuritygroup_stack import CdksecuritygroupStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdksecuritygroup/cdksecuritygroup_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdksecuritygroupStack(app, "cdksecuritygroup")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
