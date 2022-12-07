import boto3
import csv

def getSecurityGroup():
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups()

    return response

def createSecurityGroup(vpcid, groupname, description):
    ec2 = boto3.client('ec2')
    response = ec2.create_security_group(
        Description=description,
        GroupName=groupname,
        VpcId=vpcid
    )

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

        print(tmp[0])        
        # count=0
        # for i in tmp:
        #     if count>0:
        #         count+=1
        #         print(i)
        
    return getSecurityGroup()

    # return {
    #     'statusCode': 200,
    #     'body': event
    # }
