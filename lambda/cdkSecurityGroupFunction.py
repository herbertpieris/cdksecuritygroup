import boto3
import csv

def getSecurityGroup():
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups()

    return response

def main(event, context):
    print(event["Records"][0]])
    return getSecurityGroup()

    # return {
    #     'statusCode': 200,
    #     'body': event
    # }
