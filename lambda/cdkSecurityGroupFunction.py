import boto3
import botocore
import json
import datetime
import dateutil.tz
from datetime import date
import csv

from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

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

def sendEmail(mode,sgid,csvbody,attachmentmode):
    try:
        wib = dateutil.tz.gettz('Asia/Jakarta')
        x = datetime.datetime.now(tz=wib)

        if attachmentmode:
            file_name = "/tmp/1" 
            my_file = open(file_name,"w+")
            temp_my_file = csv.writer(my_file)

            dichead=None
            dicbody=None
            for x in range(len(csvbody)-1):
                if x==0:
                    y= bytes.decode(csvbody[x])
                    dichead=y.split(";")
                    temp_my_file.writerow(dichead)
                                
                if x!=0:
                    y= bytes.decode(csvbody[x])
                    dicbody=y.split(";")
                    temp_my_file.writerow(dicbody)
            my_file.close()
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = mode + " - " + "SG" + " Notification"
        msg['From'] = "herbertpieris@gmail.com"
        msg['To'] = "herbertpieris@gmail.com" #event["email"]
        if mode=="NEWEMP_SG_":
            mail_body = sgid + " created"
        elif mode=="NEW_SG_":
            mail_body = sgid + " created"
        elif mode=="UPDATE_SG_":
            mail_body = sgid + " updated"            


        # Create the body of the message (a plain-text and an HTML version).
        html = """\
        <html>
            <head></head>
            <body>
            <p style="margin-top: 0.0px;margin-bottom: 0.0px;font-size: 11.0pt;font-family: Calibri , sans-serif;color: rgb(33,33,33);">Dear Technician<br><br> """ + mail_body + """
            </p>
            <p>&nbsp;</p>
            <p style="margin-top: 0.0px;margin-bottom: 0.0px;font-size: 11.0pt;font-family: Calibri , sans-serif;color: rgb(33,33,33);"> <b><span lang="IN" style="font-size: 8.0pt;font-family: Arial , sans-serif;color: silver;">Note</span></b><span lang="IN" style="font-size: 8.0pt;font-family: Arial , sans-serif;color: silver;">:&nbsp;</span><span style="font-size: 8.0pt;font-family: Arial , sans-serif;color: silver;">This  email and its attachments are intended for the sole receipt of its stated addressees. Their contents are private and confidential. If you have received this email or its attachments in error, please immediately notify the sender and destroy the same without  reading, using, copying, storing and/or disseminating the same.</span><span lang="IN" style="font-size: 8.0pt;font-family: Arial , sans-serif;color: rgb(96,96,96);">&nbsp;&nbsp;</span><span style="font-size: 8.0pt;font-family: Arial , sans-serif;color: silver;">As  email communications are not secure, neither the sender nor any of the Japfa companies or their affiliates accepts any responsibility for any errors or changes resulting from interference or tampering.</span>
            </p>
            </body>
        </html>
        """      

        ses = boto3.client('ses', use_ssl=True)

        # Record the MIME types of both parts - text/plain and text/html.
        # part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        # msg.attach(part1)
        msg.attach(part2)
            
        if attachmentmode and (mode=="NEW_SG_" or mode=="UPDATE_SG_"):    
            # ATTACHMENT = tmp_summary_file_name

            # part3 = MIMEApplication(open(ATTACHMENT, 'rb').read())
            # part3.add_header('Content-Disposition', 'attachment', filename=summary_file_name)
            # msg.attach(part3)   

            ATTACHMENT = file_name

            part4 = MIMEApplication(open(ATTACHMENT, 'rb').read())
            part4.add_header('Content-Disposition', 'attachment', filename=file_name+".csv")
            msg.attach(part4)

        if attachmentmode and mode=="UPDATE_SG_":
            ATTACHMENT = file_name

            part5 = MIMEApplication(open(ATTACHMENT, 'rb').read())
            part5.add_header('Content-Disposition', 'attachment', filename=file_name+".csv")
            msg.attach(part5)                 
        
        text = msg.as_string()

        ses.send_raw_email(
            RawMessage= { 'Data': text }
        )
    except Exception as e:
        raise e

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
        if csvfilename.__contains__("NEWEMP_SG_"):
            tmp=csvfilename.replace("NEWEMP_SG_","").replace(".csv", "")
            tmp=tmp.split("_")
            sggroupname=tmp[1]
            sgdescription=tmp[1]
            sgvpcid=tmp[0]

            sggroupid = createSecurityGroup(sgvpcid, sggroupname,sgdescription)
            print(sggroupid)
            sggroupid = sggroupid["GroupId"]
            print(sggroupid)

            revokeIngress(getSecurityGroup(sggroupid))
            revokeEgress(getSecurityGroup(sggroupid)) 

            print("---1---") 
            print(csvbody)
            print("---2---")
            sendEmail("NEWEMP_SG_",sggroupid,csvbody,False)
            print("---3---")                       
        elif csvfilename.__contains__("NEW_SG_"):
            tmp=csvfilename.replace("NEW_SG_","").replace(".csv", "")
            tmp=tmp.split("_")
            sggroupname=tmp[1]
            sgdescription=tmp[1]
            sgvpcid=tmp[0]

            sggroupid = createSecurityGroup(sgvpcid, sggroupname,sgdescription)
            print(sggroupid)
            sggroupid = sggroupid["GroupId"]
            print(sggroupid)

            revokeIngress(getSecurityGroup(sggroupid))
            revokeEgress(getSecurityGroup(sggroupid))            

            dichead=None
            dicbody=None
            for x in range(len(csvbody)-1):
                # csvbody[x] <--- value csv yang bisa di store di list untuk dijadikan report waktu di email
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
            print("---1---") 
            print(csvbody)
            print("---2---")
            sendEmail("NEW_SG_",sggroupid,csvbody,True)
            print("---3---")
        elif csvfilename.__contains__("UPDATE_SG_"):
            sggroupid=csvfilename.replace("UPDATE_SG_","").replace(".csv", "")

            revokeIngress(getSecurityGroup(sggroupid))
            revokeEgress(getSecurityGroup(sggroupid))

            dichead=None
            dicbody=None
            for x in range(len(csvbody)-1):
                # csvbody[x] <--- value csv yang bisa di store di list untuk dijadikan report waktu di email                
                print(csvbody)
                # if x==0:
                #     y= bytes.decode(csvbody[x])
                #     dichead=y.split(";")
                # if x!=0:
                #     y= bytes.decode(csvbody[x])
                #     dicbody=y.split(";")
                #     tmpdic = convertArrToDic(dichead,dicbody)
                #     if tmpdic["Type"].lower() == "inbound":
                #         print("authorizeSecurityGroupIngress " + str(x) + " - start")
                #         print(tmpdic)
                #         print("authorizeSecurityGroupIngress " + str(x) + "  - end")
                #         response=authorizeSecurityGroupIngress(sggroupid,tmpdic)
                #     elif tmpdic["Type"].lower() == "outbound":
                #         print("authorizeSecurityGroupEgress " + str(x) + "  - start")
                #         print(tmpdic)
                #         print("authorizeSecurityGroupEgress " + str(x) + "  - end")
                #         response=authorizeSecurityGroupEgress(sggroupid,tmpdic)

        elif csvfilename.__contains__("DELETE_SG_"):
            sggroupid=csvfilename.replace("DELETE_SG_","").replace(".csv", "")
            response = deleteSecurityGroup(sggroupid)  

    # return {
    #     'statusCode': 200,
    #     'body': response
    # }              
    # except Exception:
    #     return Exception