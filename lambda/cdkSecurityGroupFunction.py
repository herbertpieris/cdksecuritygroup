import boto3
import botocore
import csv

def convertArrToDic(head,body):
    data = {}    
    for x in range(len(head)):
        data[head[x]] = body[x]
    
    response = data
    return response


def getSecurityGroup(groupid):
    # try:
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups(
        GroupIds=[groupid]
    )

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

def revokeIngress(data):
    ec2 = boto3.client('ec2')
    data = data['SecurityGroups'][0]
    # try:
    GroupId = data["GroupId"]
    
    FromPort = None
    ToPort = None
    IpProtocol = None
    IpRanges = None

    print(data)
    print(data["IpPermissions"])
    if data["IpPermissions"] != []:
        if "FromPort" in data["IpPermissions"][0]:
            FromPort = data["IpPermissions"][0]["FromPort"]
        else:
            FromPort = -1
        if "ToPort" in data["IpPermissions"][0]:
            ToPort = data["IpPermissions"][0]["ToPort"]
        else:
            ToPort = -1
        
        IpProtocol = data["IpPermissions"][0]['IpProtocol']

        if data["IpPermissions"][0]['IpRanges'] != [] :
            IpRanges = data["IpPermissions"][0]['IpRanges'] 

            for ip in IpRanges:
                print("revokeingress 1 - start")
                print(ip)
                print("revokeingress 1 - end")
                ec2.revoke_security_group_ingress(
                    DryRun=False,
                    GroupId=GroupId,            
                    IpPermissions=[
                        {
                            'FromPort': FromPort,
                            'IpProtocol': IpProtocol,                    
                            'IpRanges': [
                                {
                                    'CidrIp': ip["CidrIp"]
                                },
                            ],
                            'Ipv6Ranges': [],
                            'PrefixListIds': [],
                            'ToPort': ToPort,
                            'UserIdGroupPairs': []                        
                        }
                    ]
                )

    if "UserIdGroupPairs" in data:
        if "FromPort" in data["IpPermissions"][0]:
            FromPort = data["IpPermissions"][0]["FromPort"]
        else:
            FromPort = -1
        if "ToPort" in data["IpPermissions"][0]:
            ToPort = data["IpPermissions"][0]["ToPort"]
        else:
            ToPort = -1

        if len(data["IpPermissions"][0]['UserIdGroupPairs']) >= 0:
            print("revokeingress 2")
            SourceGroupIds = data["IpPermissions"][0]['UserIdGroupPairs']

            for SourceGroupId in SourceGroupIds:
                print("revokeingress 2 - start")
                print(SourceGroupId)
                print("revokeingress 2 - end")

                ec2.revoke_security_group_ingress(
                    DryRun=False,
                    GroupId=GroupId,            
                    IpPermissions=[
                        {
                            'FromPort': FromPort,
                            'IpProtocol': IpProtocol,                    
                            'IpRanges': [],
                            'Ipv6Ranges': [],
                            'PrefixListIds': [],
                            'ToPort': ToPort,
                            'UserIdGroupPairs': [
                                {
                                    'GroupId': SourceGroupId["GroupId"],
                                },
                            ],
                        }
                    ]
                )            
    # except botocore.exceptions.ClientError as e:
    #     raise e

def revokeEgress(data):
    ec2 = boto3.client('ec2')
    data = data['SecurityGroups'][0]
    # try:
    GroupId = data["GroupId"]
    
    FromPort = None
    ToPort = None
    IpProtocol = None
    IpRanges = None

    for x in range(len(data["IpPermissionsEgress"])):
        if "FromPort" in data["IpPermissionsEgress"][x]:
            FromPort = data["IpPermissionsEgress"][x]["FromPort"]
        else:
            FromPort = -1
        if "ToPort" in data["IpPermissionsEgress"][x]:
            ToPort = data["IpPermissionsEgress"][x]["ToPort"]
        else:
            ToPort = -1
        IpProtocol = data["IpPermissionsEgress"][x]['IpProtocol']

        # print(data)
        if data["IpPermissionsEgress"][x]['IpRanges'] != [] :
            IpRanges = data["IpPermissionsEgress"][x]['IpRanges'] 

            for ip in IpRanges:
                print("revoke egress 1 - start")
                print(ip)
                print("revoke egress 1 - end")
                ec2.revoke_security_group_egress(
                    DryRun=False,
                    GroupId=GroupId,            
                    IpPermissions=[
                        {
                            'FromPort': FromPort,
                            'IpProtocol': IpProtocol,                    
                            'IpRanges': [
                                {
                                    'CidrIp': ip["CidrIp"]
                                },
                            ],
                            'Ipv6Ranges': [],
                            'PrefixListIds': [],
                            'ToPort': ToPort,
                            'UserIdGroupPairs': []                        
                        }
                    ]
                )            
        else:
            # print(data)
            SourceGroupIds = data["IpPermissionsEgress"][x]['UserIdGroupPairs']

            for SourceGroupId in SourceGroupIds:
                print("revoke egress 2 - start")
                print(SourceGroupId)
                print("revoke egress 2 - end")                
                ec2.revoke_security_group_egress(
                    DryRun=False,
                    GroupId=GroupId,            
                    IpPermissions=[
                        {
                            'FromPort': FromPort,
                            'IpProtocol': IpProtocol,                    
                            'IpRanges': [],
                            'Ipv6Ranges': [],
                            'PrefixListIds': [],
                            'ToPort': ToPort,
                            'UserIdGroupPairs': [
                                {
                                    'GroupId': SourceGroupId["GroupId"],
                                },
                            ],                      
                        }
                    ]
                )

    # except botocore.exceptions.ClientError as e:
    #     raise e

def authorizeSecurityGroupIngress(groupid,tmpdic):
    # try:
    ec2 = boto3.client('ec2')

    if tmpdic["FromPort"] != "":
        FromPort = tmpdic["FromPort"]
    else:
        FromPort = -1
    if tmpdic["ToPort"] != "":
        ToPort = tmpdic["ToPort"]
    else:
        ToPort = -1

    if tmpdic["IpRanges"] != '':
        response = ec2.authorize_security_group_ingress(
            GroupId=groupid,
            IpPermissions=[
                {
                    'FromPort': int(FromPort),
                    'IpProtocol': tmpdic["IpProtocol"],
                    'IpRanges': [
                        {
                            'CidrIp': tmpdic["IpRanges"],
                            'Description': tmpdic["Description"],
                        },
                    ],
                    'ToPort': int(ToPort),
                },
            ]            
        )
    else:
        response = ec2.authorize_security_group_ingress(
            GroupId=groupid,
            IpPermissions=[
                {
                    'FromPort': int(tmpdic["FromPort"]),
                    'IpProtocol': tmpdic["IpProtocol"],
                    'UserIdGroupPairs': [
                        {
                            'GroupId': tmpdic["UserIdGroupPairs\r"].replace("\r",""),
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
    print(tmpdic)

    if tmpdic["FromPort"] != "":
        FromPort = tmpdic["FromPort"]
    else:
        FromPort = -1
    if tmpdic["ToPort"] != "":
        ToPort = tmpdic["ToPort"]
    else:
        ToPort = -1

    if tmpdic["IpRanges"] != '':
        response = ec2.authorize_security_group_egress(
            GroupId=groupid,
            IpPermissions=[
                {
                    'FromPort': int(FromPort),
                    'IpProtocol': tmpdic["IpProtocol"],
                    'IpRanges': [
                        {
                            'CidrIp': tmpdic["IpRanges"],
                            'Description': tmpdic["Description"],
                        },
                    ],
                    'ToPort': int(ToPort),
                },
            ],
        )
    else:
        response = ec2.authorize_security_group_egress(
            GroupId=groupid,
            IpPermissions=[
                {
                    'FromPort': int(tmpdic["FromPort"]),
                    'IpProtocol': tmpdic["IpProtocol"],
                    'UserIdGroupPairs': [
                        {
                            'GroupId': tmpdic["UserIdGroupPairs\r"].replace("\r",""),
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

            revokeIngress(getSecurityGroup(sggroupid))
            revokeEgress(getSecurityGroup(sggroupid))

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
                        print("authorizeSecurityGroupIngress " + str(x) + " - start")
                        print(tmpdic)
                        print("authorizeSecurityGroupIngress " + str(x) + "  - end")
                        response=authorizeSecurityGroupIngress(sggroupid,tmpdic)
                    elif tmpdic["Type"].lower() == "outbound":
                        print("authorizeSecurityGroupEgress " + str(x) + "  - start")
                        print(tmpdic)
                        print("authorizeSecurityGroupEgress " + str(x) + "  - end")
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