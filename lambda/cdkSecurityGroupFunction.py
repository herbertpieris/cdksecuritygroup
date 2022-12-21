import boto3
import csv

def getSecurityGroup():
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_security_groups()

        return response    
    except Exception:
        return Exception

def createSecurityGroup(vpcid, groupname, description):
    # try:
    ec2 = boto3.client('ec2')
    response = ec2.create_security_group(
        Description=description,
        GroupName=groupname,
        VpcId=vpcid
    )

    return response
    # except Exception:
    #     return Exception

def deleteSecurityGroup(groupid):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.delete_security_group(
            GroupId=groupid
        )

        return response
    except Exception:
        return Exception

def authorizeSecurityGroupIngress(groupid,port,protocol,ip,desc):
    # try:
    ec2 = boto3.client('ec2')
    response = ec2.authorize_security_group_ingress(
        GroupId=groupid,
        IpPermissions=[
            {
                'FromPort': port,
                'IpProtocol': protocol,
                'IpRanges': [
                    {
                        'CidrIp': ip,
                        'Description': desc,
                    },
                ],
                'ToPort': port,
            },
        ],
    )

    return response
    # except Exception:
    #     return Exception

def main(event, context):
    # try:
    s3 = boto3.client('s3')

    # capture event invoke from s3
    for record in event["Records"]:
        s3BucketName = record['s3']['bucket']['name']
        csvfilename = record['s3']['object']['key']

        # read csv
        csvfile = s3.get_object(Bucket=s3BucketName,Key=csvfilename)
        csvbody = csvfile["Body"].read().split(b'\n')

        sggroupname=None
        sgdescription=None
        sgvpcid=None
        sggroupid=None
        if csvfilename.__contains__("NEW_SG_"):
            tmp=csvfilename.replace("NEW_SG_","").replace(".csv", "")
            tmp=tmp.split("_")
            sggroupname=tmp[1]
            sgdescription=tmp[1]
            sgvpcid=tmp[0]

            sggroupid = createSecurityGroup(sgvpcid, sggroupname,sgdescription)
            sggroupid = sggroupid["GroupId"]

            print(csvbody)

            for x in range(len(csvbody)-1):
                if x==0:
                    print(csvbody[x])
                    y=csvbody[x].split(",")
                    print(y)
                response=None
                # try:                
                # response=authorizeSecurityGroupIngress(sggroupid)
                # except Exception:
                #     print(Exception)

        elif csvfilename.__contains__("DELETE_SG_"):
            sggroupid=csvfilename.replace("DELETE_SG_","").replace(".csv", "")
            response = deleteSecurityGroup(sggroupid)  

    return {
        'statusCode': 200,
        'body': response
    }              
    # except Exception:
    #     return Exception