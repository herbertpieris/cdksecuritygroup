import boto3;

def getSecurityGroup():
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups()

    return response

def main(event, context):
    getSecurityGroup()

    return {
        'statusCode': 200,
        'body': event
    }
