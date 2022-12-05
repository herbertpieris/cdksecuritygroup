import boto3
import csv

def getSecurityGroup():
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups()

    return response

def main(event, context):
    for record in event:
        print(record)
#        print(event["Records"][0]["object"])
    return getSecurityGroup()

    # return {
    #     'statusCode': 200,
    #     'body': event
    # }
