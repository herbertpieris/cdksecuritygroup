import boto3
import csv

def convertArrToDic(head,body):
    data = {}    
    for x in range(len(head)):
        data[head[x]] = body[x]
    
    response = data
    return response


def getSecurityGroup():
    # try:
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups()

    return response    
    # except Exception:
    #     return Exception

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
    # try:
    ec2 = boto3.client('ec2')
    response = ec2.delete_security_group(
        GroupId=groupid
    )

    return response
    # except Exception:
    #     return Exception

def revokeIngress(sggroupid):
    ec2 = boto3.resource('ec2')
    security_group = ec2.SecurityGroup(sggroupid)

    response = security_group.revoke_ingress()

def authorizeSecurityGroupIngress(groupid,tmpdic):
    # try:
    ec2 = boto3.client('ec2')
    response = ec2.authorize_security_group_ingress(
        GroupId=groupid,
        IpPermissions=[
            {
                'FromPort': int(tmpdic["FromPort"]),
                'IpProtocol': tmpdic["IpProtocol"],
                'IpRanges': [
                    {
                        'CidrIp': tmpdic["IpRanges"],
                        'Description': tmpdic["Description"],
                    },
                ],
                'ToPort': int(tmpdic["ToPort"]),
            },
        ],
    )

    return response
    # except Exception:
    #     return Exception

def authorizeSecurityGroupEgress(groupid,tmpdic):
    # try:
    ec2 = boto3.client('ec2')
    response = ec2.authorize_security_group_egress(
        GroupId=groupid,
        IpPermissions=[
            {
                'FromPort': int(tmpdic["FromPort"]),
                'IpProtocol': tmpdic["IpProtocol"],
                'IpRanges': [
                    {
                        'CidrIp': tmpdic["IpRanges"],
                        'Description': tmpdic["Description"],
                    },
                ],
                'ToPort': int(tmpdic["ToPort"]),
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

            dichead=None
            dicbody=None
            for x in range(len(csvbody)-1):
                if x==0:
                    y= bytes.decode(csvbody[x])
                    dichead=y.split(";")
                if x!=0:
                    y= bytes.decode(csvbody[x])
                    dicbody=y.split(";")
                    tmpdic = convertArrToDic(dichead,dicbody)
                    if tmpdic["Type"].lower() == "inbound":
                        response=authorizeSecurityGroupIngress(sggroupid,tmpdic)
                    elif tmpdic["Type"].lower() == "outbound":
                        response=authorizeSecurityGroupEgress(sggroupid,tmpdic)
                    
                # response=None
                # try:                
                # response=authorizeSecurityGroupIngress(sggroupid)
                # except Exception:
                #     print(Exception)            
        elif csvfilename.__contains__("UPDATE_SG_"):
            sggroupid=csvfilename.replace("UPDATE_SG_","").replace(".csv", "")

            revokeIngress(sggroupid)

            dichead=None
            dicbody=None
            for x in range(len(csvbody)-1):
                if x==0:
                    y= bytes.decode(csvbody[x])
                    dichead=y.split(";")
                if x!=0:
                    y= bytes.decode(csvbody[x])
                    dicbody=y.split(";")
                    tmpdic = convertArrToDic(dichead,dicbody)
                    if tmpdic["Type"].lower() == "inbound":
                        response=authorizeSecurityGroupIngress(sggroupid,tmpdic)
                    elif tmpdic["Type"].lower() == "outbound":
                        response=authorizeSecurityGroupEgress(sggroupid,tmpdic)

        elif csvfilename.__contains__("DELETE_SG_"):
            sggroupid=csvfilename.replace("DELETE_SG_","").replace(".csv", "")
            response = deleteSecurityGroup(sggroupid)  

    # return {
    #     'statusCode': 200,
    #     'body': response
    # }              
    # except Exception:
    #     return Exception