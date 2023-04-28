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

### convertArrDic
### convert list to dictionary
def convertArrToDic(head,body):
    try:
        data = {}    
        for x in range(len(head)):
            data[head[x]] = body[x]
        
        response = data
        return response        
    except Exception:
        return Exception    

### getSecurityGroup
### describe security group
def getSecurityGroup(groupid):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_security_groups(
            GroupIds=[groupid]
        )

        return response    
    except Exception:
        return Exception

### createSecurityGroup
### creating security group
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

### deleteSecurityGroup
### deleting security group
def deleteSecurityGroup(groupid):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.delete_security_group(
            GroupId=groupid
        )

        return response
    except Exception:
        return Exception

### revokeIngressRecords
### remove ingress records from security group
def revokeIngressRecords(data):
    ec2 = boto3.client('ec2')
    data = data['SecurityGroups'][0]
    try:
        GroupId = data["GroupId"]
        
        if data["IpPermissions"] != [] or "UserIdGroupPairs" in data:
            ec2.revoke_security_group_ingress(
                DryRun=False,
                GroupId=GroupId,            
                IpPermissions=data["IpPermissions"]
            )   

    except botocore.exceptions.ClientError as e:
        raise e

### revokeEgressRecords
### remove egress records from security group
def revokeEgressRecords(data):
    ec2 = boto3.client('ec2')
    data = data['SecurityGroups'][0]
    try:
        GroupId = data["GroupId"]

        if data["IpPermissionsEgress"] != [] :
            ec2.revoke_security_group_egress(
                DryRun=False,
                GroupId=GroupId,            
                IpPermissions=data["IpPermissionsEgress"]
            )

    except botocore.exceptions.ClientError as e:
        raise e

### validatePort
### figure out from and to port    
def validatePort(tmpdic):
    fromPort = -1
    if tmpdic["FromPort"] != "":
        FromPort = tmpdic["FromPort"]

    toPort = -1
    if tmpdic["ToPort"] != "":
        ToPort = tmpdic["ToPort"] 
    
    return fromPort, toPort

### authorizeSecurityGroupIngress
### input ingress record to security group
def authorizeSecurityGroupIngress(groupid,tmpdic):
    # try:
    ec2 = boto3.client('ec2')
    # fromPort, toPort = validatePort(tmpdic)
    # response = ec2.authorize_security_group_ingress(
    #     GroupId=groupid,
    #     IpPermissions=[{
    #         'FromPort': fromPort, 
    #         'IpProtocol': 'tcp', 
    #         'IpRanges': [
    #             {
    #                 'CidrIp': '10.91.148.0/23', 
    #                 'Description': 'Access Web from VPN'
    #             }
    #         ], 
    #         'ToPort': toPort
    #     }]
    # )    
    fromPort, toPort = validatePort(tmpdic)

    if tmpdic["IpRanges"] != '':
        print(tmpdic)
        print("--- inbound 1 -----")            
        response = ec2.authorize_security_group_ingress(
            GroupId=groupid,
            IpPermissions=[{
                # 'FromPort': int(fromPort),
                'IpProtocol': tmpdic["IpProtocol"],
                'IpRanges': [
                    {
                        'CidrIp': tmpdic["IpRanges"],
                        'Description': tmpdic["Description"],
                    },
                ],
                # 'ToPort': int(toPort),
            }]
        )
        print(response)
        print("--------")
    else:
        print("--- inbound 2 -----")
        response = ec2.authorize_security_group_ingress(
            GroupId=groupid,
            IpPermissions=[{
                'FromPort': int(tmpdic["FromPort"]),
                'IpProtocol': tmpdic["IpProtocol"],
                'UserIdGroupPairs': [
                    {
                        'GroupId': tmpdic["UserIdGroupPairs\r"].replace("\r",""),
                        'Description': tmpdic["Description"],
                    },
                ],
                'ToPort': int(tmpdic["ToPort"]),

            }]
        )
        print("--------")

    return response
    # except Exception:
    #     return Exception

def authorizeSecurityGroupEgress(groupid,tmpdic):
    try:
        ec2 = boto3.client('ec2')
        fromPort, toPort = validatePort(tmpdic)

        if tmpdic["IpRanges"] != '':
            response = ec2.authorize_security_group_egress(
                GroupId=groupid,
                IpPermissions=[{
                    'FromPort': int(fromPort),
                    'IpProtocol': tmpdic["IpProtocol"],
                    'IpRanges': [
                        {
                            'CidrIp': tmpdic["IpRanges"],
                            'Description': tmpdic["Description"],
                        },
                    ],
                    'ToPort': int(toPort),
                }]
            )            
        else:
            response = ec2.authorize_security_group_egress(
                GroupId=groupid,
                IpPermissions=[{
                    'FromPort': int(tmpdic["FromPort"]),
                    'IpProtocol': tmpdic["IpProtocol"],
                    'UserIdGroupPairs': [
                        {
                            'GroupId': tmpdic["UserIdGroupPairs\r"].replace("\r",""),
                            'Description': tmpdic["Description"],
                        },
                    ],
                    'ToPort': int(tmpdic["ToPort"]),
                }]
            )            

        return response
    except Exception:
        return Exception

### writeAttachment
def writeAttachment(filename,value, mode):
    file_name = "/tmp/"+filename 
    my_file = open(file_name,"w+")
    temp_my_file = csv.writer(my_file)

    if mode==1:
        dichead=None
        dicbody=None
        for x in range(len(value)-1):
            if x==0:
                y= bytes.decode(value[x])
                dichead=y.split(";")
                temp_my_file.writerow(dichead)
                            
            if x!=0:
                y= bytes.decode(value[x])
                dicbody=y.split(";")
                temp_my_file.writerow(dicbody)
        my_file.close()
    # elif mode==2:
    #     if value["IpPermissions"] != []:        
    #         for x in range(len(value["IpPermissions"])-1):
    #             # csvbody[x] <--- value csv yang bisa di store di list untuk dijadikan report waktu di email
    #             if x==0:
    #                 y= bytes.decode(csvbody[x])
    #                 dichead=y.split(";")
    #             if x!=0:
    #                 y= bytes.decode(csvbody[x])
    #                 dicbody=y.split(";")
    #                 tmpdic = convertArrToDic(dichead,dicbody)
    #                 if tmpdic["Type"].lower() == "inbound":
    #                     response=authorizeSecurityGroupIngress(sggroupid,tmpdic)
    #                 elif tmpdic["Type"].lower() == "outbound":
    #                     response=authorizeSecurityGroupEgress(sggroupid,tmpdic)

    #     if value["IpPermissions"] != []:
    #         for x in range(len(value["IpPermissions"])-1):
    #             print(value["IpPermissions"][x])
    #             y= bytes.decode(value["IpPermissions"][x])
    #             z=y.split(";")
    #             temp_my_file.writerow(z)

    #     if "UserIdGroupPairs" in value:
    #         for x in range(len(value["UserIdGroupPairs"])-1):
    #             y= bytes.decode(value["UserIdGroupPairs"][x])
    #             z=y.split(";")
    #             temp_my_file.writerow(z)                

    #     if value["IpPermissionsEgress"] != [] :
    #         for x in range(len(value["IpPermissionsEgress"])-1):
    #             y= bytes.decode(value["IpPermissionsEgress"][x])
    #             z=y.split(";")
    #             temp_my_file.writerow(z)

    #     my_file.close()        
    return file_name

def compileEmail(mode, sgid, attachmentmode, newvalue, oldvalue=None):
    wib = dateutil.tz.gettz('Asia/Jakarta')
    x = datetime.datetime.now(tz=wib)

    if attachmentmode and mode=="NEW_SG_":
        filename1="new"
        fileNewValue=writeAttachment(filename1,newvalue, 1)

    elif attachmentmode and mode=="UPDATE_SG_":
        filename1="new"
        fileNewValue=writeAttachment(filename1,1)

        filename2="old"
        fileOldValue=writeAttachment(filename2,2)

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

        ATTACHMENT = fileNewValue

        part4 = MIMEApplication(open(ATTACHMENT, 'rb').read())
        part4.add_header('Content-Disposition', 'attachment', filename=filename1+".csv")
        msg.attach(part4)

    if attachmentmode and mode=="UPDATE_SG_":
        ATTACHMENT = fileOldValue

        part5 = MIMEApplication(open(ATTACHMENT, 'rb').read())
        part5.add_header('Content-Disposition', 'attachment', filename=filename2+".csv")
        msg.attach(part5)
    
    text = msg.as_string()
    return text    

### sendEmail
### send email using simple email service
def sendEmail(mode, sgid, attachmentmode, newvalue, oldvalue=None):
    # try:

    ses = boto3.client('ses', use_ssl=True)    
    if oldvalue:
        text = compileEmail(mode, sgid, attachmentmode, newvalue, oldvalue) 
    else:
        text = compileEmail(mode, sgid, attachmentmode, newvalue)

    ses.send_raw_email(
        RawMessage= { 'Data': text }
    )
    # except Exception as e:
    #     raise e

# def rollBackNewSG():

### readCSV
### extract csv content
def readCSV(record, csvfilename):
    s3 = boto3.client('s3')
    s3BucketName = record['s3']['bucket']['name']

    # read csv
    csvfile = s3.get_object(Bucket=s3BucketName,Key=csvfilename)
    csvbody = csvfile["Body"].read().split(b'\n')
    return csvbody

### getSGName function
### get security group name from csv file name
### that will be used as securigy group identifier
def getSGName(csvfilename,lookup):
    tmp=csvfilename.replace(lookup,"").replace(".csv", "")
    tmp=tmp.split("_")
    return tmp[1], tmp[1], tmp[0] 

### removeDuplicateValue
### removing duplicate value from list
def removeDuplicateValue(csvbody):
    csvbody = list(dict.fromkeys(csvbody))
    return csvbody

### constructIPPermissionIngress
###
def constructIPPermissionIngress():
    return

### processNewEmptySG
### create security group without ingress or egress record
### send email notification
def processNewEmptySG(csvfilename,csvbody):
    sggroupname, sgdescription, sgvpcid = getSGName(csvfilename,"NEWEMP_SG_")
    
    sggroupid = createSecurityGroup(sgvpcid, sggroupname,sgdescription)
    sggroupid = sggroupid["GroupId"]

    sgValue = getSecurityGroup(sggroupid)
    revokeIngressRecords(sgValue)
    revokeEgressRecords(sgValue) 

    sendEmail("NEWEMP_SG_",sggroupid,False,csvbody,"")

### processNewSG
### create security group with ingress or egress record
### send email notification
def processNewSG(csvfilename,csvbody):
    sggroupname, sgdescription, sgvpcid = getSGName(csvfilename,"NEW_SG_")

    sggroupid = createSecurityGroup(sgvpcid, sggroupname,sgdescription)
    sggroupid = sggroupid["GroupId"]

    sgValue = getSecurityGroup(sggroupid)
    revokeIngressRecords(sgValue)
    revokeEgressRecords(sgValue)             

    dichead=None
    dicbody=None
    csvbody = removeDuplicateValue(csvbody)
    IpPermissionsIngress = []
    IpPermissionsEgress = []
    for x in range(len(csvbody)-1):
        if x==0:
            y= bytes.decode(csvbody[x])
            dichead=y.split(";")
        if x!=0:
            y= bytes.decode(csvbody[x])
            dicbody=y.split(";")
            tmpdic = convertArrToDic(dichead,dicbody)
            if tmpdic["Type"].lower() == "inbound":
                # if tmpdic["IpRanges"] != '':
                #     # print(tmpdic)
                #     fromPort, toPort = validatePort(tmpdic)
                #     IpPermissionsIngress.append({
                #         'FromPort': int(fromPort),
                #         'IpProtocol': tmpdic["IpProtocol"],
                #         'IpRanges': [
                #             {
                #                 'CidrIp': tmpdic["IpRanges"],
                #                 'Description': tmpdic["Description"],
                #             },
                #         ],
                #         'ToPort': int(toPort),
                #     })
                # else:
                #     IpPermissionsIngress.append({
                #         'FromPort': int(tmpdic["FromPort"]),
                #         'IpProtocol': tmpdic["IpProtocol"],
                #         'UserIdGroupPairs': [
                #             {
                #                 'GroupId': tmpdic["UserIdGroupPairs\r"].replace("\r",""),
                #                 'Description': tmpdic["Description"],
                #             },
                #         ],
                #         'ToPort': int(tmpdic["ToPort"]),

                #     })
                response=authorizeSecurityGroupIngress(sggroupid,tmpdic)
            elif tmpdic["Type"].lower() == "outbound":
                print(tmpdic)
                # print("--- outbound " + str(x) + " -----")
                # response=authorizeSecurityGroupEgress(sggroupid,tmpdic)
                # print("--------")
    # print(IpPermissionsIngress)
    # print(IpPermissionsEgress) 
    # authorizeSecurityGroupIngress(sggroupid,IpPermissionsIngress)  
    sendEmail("NEW_SG_",sggroupid,True,csvbody)

### processRecord function
### processing record from main function
def processRecord(record):
    csvfilename = record['s3']['object']['key']
    CSV = readCSV(record, csvfilename)

    sggroupname=None
    sgdescription=None
    sgvpcid=None
    sggroupid=None

    if csvfilename.__contains__("NEWEMP_SG_"):
        processNewEmptySG(csvfilename,CSV)
    elif csvfilename.__contains__("NEW_SG_"):
        processNewSG(csvfilename,CSV)
    elif csvfilename.__contains__("UPDATE_SG_"):
        sggroupid=csvfilename.replace("UPDATE_SG_","").replace(".csv", "")

        sgvalue=getSecurityGroup(sggroupid)
        # print(sgvalue['SecurityGroups'][0])
        revokeIngressRecords(sgvalue)
        revokeEgressRecords(sgvalue)

        dichead=None
        dicbody=None
        csvbody = list(dict.fromkeys(csvbody))
        for x in range(len(csvbody)-1):
            # csvbody[x] <--- value csv yang bisa di store di list untuk dijadikan report waktu di email                
            # print(csvbody)
            if x==0:
                y= bytes.decode(csvbody[x])
                dichead=y.split(";")
            if x!=0:
                y= bytes.decode(csvbody[x])
                dicbody=y.split(";")
                tmpdic = convertArrToDic(dichead,dicbody)
                if tmpdic["Type"].lower() == "inbound":
                    # print("authorizeSecurityGroupIngress " + str(x) + " - start")
                    # print(tmpdic)
                    # print("authorizeSecurityGroupIngress " + str(x) + "  - end")
                    response=authorizeSecurityGroupIngress(sggroupid,tmpdic)
                elif tmpdic["Type"].lower() == "outbound":
                    # print("authorizeSecurityGroupEgress " + str(x) + "  - start")
                    # print(tmpdic)
                    # print("authorizeSecurityGroupEgress " + str(x) + "  - end")
                    response=authorizeSecurityGroupEgress(sggroupid,tmpdic)

        # print("---1---") 
        # print(csvbody)
        # print("---2---")
        sendEmail("UPDATE_SG_",sggroupid,True,csvbody,sgvalue['SecurityGroups'][0])
        # print("---3---")

    elif csvfilename.__contains__("DELETE_SG_"):
        sggroupid=csvfilename.replace("DELETE_SG_","").replace(".csv", "")
        response = deleteSecurityGroup(sggroupid)  

### main function
### process event records triggered by s3 events
def main(event, context):
    # capture event invoke from s3
    for record in event["Records"]:       
       processRecord(record)

    # return {
    #     'statusCode': 200,
    #     'body': response
    # }