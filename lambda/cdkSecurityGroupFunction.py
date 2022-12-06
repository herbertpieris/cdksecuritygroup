import boto3
import csv

def getSecurityGroup():
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups()

    return response

def main(event, context):
    s3 = boto3.client('s3')

    # capture event invoke from s3
    for record in event["Records"]:
        s3BucketName = record['s3']['bucket']['name']
        csvfilename = record['s3']['object']['key']

        # read csv
        csvfile = s3.get_object(Bucket=s3BucketName,Key=csvfilename)
        tmp = csvfile["Body"].read().split(b'\n')
        for i in tmp:
            print(i)
        
    return getSecurityGroup()

    # return {
    #     'statusCode': 200,
    #     'body': event
    # }
