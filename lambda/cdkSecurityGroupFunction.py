import boto3
import csv

def getSecurityGroup():
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups()

    return response

def main(event, context):
    # capture event invoke from s3
    for record in event["Records"]:
        print(record['s3']['object'])
    return getSecurityGroup()

    # return {
    #     'statusCode': 200,
    #     'body': event
    # }
