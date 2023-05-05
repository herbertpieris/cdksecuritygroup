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
    # try:
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups(
        GroupIds=[groupid]
    )

    return response    
    # except Exception:
    #     return Exception

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
    # try:
    GroupId = data["GroupId"]
    
    if data["IpPermissions"] != [] or "UserIdGroupPairs" in data:
        ec2.revoke_security_group_ingress(
            DryRun=False,
            GroupId=GroupId,            
            IpPermissions=data["IpPermissions"]
        )   

    # except botocore.exceptions.ClientError as e:
    #     raise e

### revokeEgressRecords
### remove egress records from security group
def revokeEgressRecords(data):
    ec2 = boto3.client('ec2')
    data = data['SecurityGroups'][0]
    # try:
    GroupId = data["GroupId"]

    if data["IpPermissionsEgress"] != [] :
        ec2.revoke_security_group_egress(
            DryRun=False,
            GroupId=GroupId,            
            IpPermissions=data["IpPermissionsEgress"]
        )

    # except botocore.exceptions.ClientError as e:
    #     raise e

### validatePortocol    
def validatePortocol(tmpdic):
    ipProtocol = -1
    if tmpdic["FromPort"] != "" and tmpdic["ToPort"] != "":
        ipProtocol = tmpdic["IpProtocol"]
    
    return str(ipProtocol)

### validatePort
### figure out from and to port    
def validatePort(tmpdic):
    fromPort = -1
    if tmpdic["FromPort"] != "":
        fromPort = tmpdic["FromPort"]

    toPort = -1
    if tmpdic["ToPort"] != "":
        toPort = tmpdic["ToPort"]
    
    return int(fromPort), int(toPort)

### authorizeSecurityGroupIngress
### input ingress record to security group
def authorizeSecurityGroupIngress(groupid,ipPermission):
    # try:
    ec2 = boto3.client('ec2')

    response = ec2.authorize_security_group_ingress(
        GroupId=groupid,
        IpPermissions=ipPermission
    )  
  
    return response
    # except Exception:
    #     return Exception

def authorizeSecurityGroupEgress(groupid,ipPermission):
    # try:
    ec2 = boto3.client('ec2')

    response = ec2.authorize_security_group_egress(
        GroupId=groupid,
        IpPermissions=ipPermission
    )
              
    return response
    # except Exception:
    #     return Exception

### writeAttachment
### 
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
    elif mode==2:
        IpPermissionIngress=[]
        if value["IpPermissions"] != []:            
            for x in range(len(value["IpPermissions"])):
                compileIPPermissionIngress(value["IpPermissions"][x], IpPermissionIngress, 2)
            
        print("-----")
        print(IpPermissionIngress)
        print("-----")
                # if x==0:
                #     y= bytes.decode(csvbody[x])
                #     dichead=y.split(";")
                # if x!=0:
                #     y= bytes.decode(csvbody[x])
                #     dicbody=y.split(";")
                #     tmpdic = convertArrToDic(dichead,dicbody)
                #     if tmpdic["Type"].lower() == "inbound":
                #         response=authorizeSecurityGroupIngress(sggroupid,tmpdic)
                #     elif tmpdic["Type"].lower() == "outbound":
                #         response=authorizeSecurityGroupEgress(sggroupid,tmpdic)

                # if value["IpPermissions"] != []:
                #     for x in range(len(value["IpPermissions"])-1):
                #         print(value["IpPermissions"][x])
                #         y= bytes.decode(value["IpPermissions"][x])
                #         z=y.split(";")
                #         temp_my_file.writerow(z)

                # if "UserIdGroupPairs" in value:
                #     for x in range(len(value["UserIdGroupPairs"])-1):
                #         y= bytes.decode(value["UserIdGroupPairs"][x])
                #         z=y.split(";")
                #         temp_my_file.writerow(z)                

        if value["IpPermissionsEgress"] != [] :
            print(value["IpPermissionsEgress"])
            # for x in range(len(value["IpPermissionsEgress"])-1):
            #     y= bytes.decode(value["IpPermissionsEgress"][x])
            #     z=y.split(";")
            #     temp_my_file.writerow(z)

        my_file.close()        
    return file_name

def compileEmail(mode, sgid, attachmentmode, newvalue, oldvalue=None):
    wib = dateutil.tz.gettz('Asia/Jakarta')
    x = datetime.datetime.now(tz=wib)

    if attachmentmode and mode=="NEW_SG_":
        filename1="new-sg-"+sgid+"-records"
        fileNewValue=writeAttachment(filename1,newvalue, 1)

    elif attachmentmode and mode=="UPDATE_SG_":
        filename1="new-sg-"+sgid+"-records"
        fileNewValue=writeAttachment(filename1,newvalue,1)

        filename2="old-"+sgid+"-records"
        fileOldValue=writeAttachment(filename2,oldvalue,2)

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

### compileIPPermissionIngress
### create list of ip permission for ingress record
def compileIPPermissionIngress(tmpdic, IpPermissionIngress, mode):
    fromPort, toPort = validatePort(tmpdic)

    if mode == 1:
        if tmpdic["IpRanges"] != '':
            IpPermissionIngress.append({
                'FromPort': fromPort,
                'IpProtocol': validatePortocol(tmpdic),
                'IpRanges': [
                    {
                        'CidrIp': tmpdic["IpRanges"],
                        'Description': tmpdic["Description"],
                    },
                ],
                'ToPort': toPort,
            })
        else:
            IpPermissionIngress.append({
                'FromPort': fromPort,
                'IpProtocol': validatePortocol(tmpdic),
                'UserIdGroupPairs': [
                    {
                        'GroupId': tmpdic["UserIdGroupPairs\r"].replace("\r",""),
                        'Description': tmpdic["Description"],
                    },
                ],
                'ToPort': toPort,

            })
    elif mode == 2:
        if tmpdic["IpRanges"] != '':
            for x in range(len(tmpdic["IpRanges"])):
                IpPermissionIngress.append({
                    'FromPort': fromPort,
                    'IpProtocol': validatePortocol(tmpdic),
                    'IpRanges': [
                        {
                            'CidrIp': tmpdic["IpRanges"][x]["CidrIp"],
                            'Description': tmpdic["IpRanges"][x]["Description"],
                        },
                    ],
                    'ToPort': toPort,
                })
            print(tmpdic)
            if "UserIdGroupPairs" in tmpdic:
                for x in range(len(tmpdic["UserIdGroupPairs"])):
                    IpPermissionIngress.append({
                        'FromPort': fromPort,
                        'IpProtocol': validatePortocol(tmpdic),
                        'UserIdGroupPairs': [
                            {
                                'GroupId': tmpdic["UserIdGroupPairs"][x]["GroupId"],
                                'Description': tmpdic["UserIdGroupPairs"][x]["Description"],
                            },
                        ],
                        'ToPort': toPort,
                    })                
        else:
            IpPermissionIngress.append({
                'FromPort': fromPort,
                'IpProtocol': validatePortocol(tmpdic),
                'UserIdGroupPairs': [
                    {
                        'GroupId': tmpdic["UserIdGroupPairs"]["GroupId"],
                        'Description': tmpdic["UserIdGroupPairs"]["Description"],
                    },
                ],
                'ToPort': toPort,
            })            
    return IpPermissionIngress

### compileIPPermissionEgress
### create list of ip permission for egress record
def compileIPPermissionEgress(tmpdic, IpPermissionEgress, mode):
    fromPort, toPort = validatePort(tmpdic)

    if mode == 1:
        if tmpdic["IpRanges"] != '':
            IpPermissionEgress.append({
                'FromPort': fromPort,
                'IpProtocol': validatePortocol(tmpdic),
                'IpRanges': [
                    {
                        'CidrIp': tmpdic["IpRanges"],
                        'Description': tmpdic["Description"],
                    },
                ],
                'ToPort': toPort,
            })
        else:
            IpPermissionEgress.append({
                    'FromPort': fromPort,
                    'IpProtocol': validatePortocol(tmpdic),
                    'UserIdGroupPairs': [
                        {
                            'GroupId': tmpdic["UserIdGroupPairs\r"].replace("\r",""),
                            'Description': tmpdic["Description"],
                        },
                    ],
                    'ToPort': toPort,
                })
    elif mode ==2:
        print("")
    return IpPermissionEgress

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
    IpPermissionIngress = []
    IpPermissionEgress = []
    for x in range(len(csvbody)-1):
        if x==0:
            y= bytes.decode(csvbody[x])
            dichead=y.split(";")
        if x!=0:
            y= bytes.decode(csvbody[x])
            dicbody=y.split(";")

            tmpdic = convertArrToDic(dichead,dicbody)
            if tmpdic["Type"].lower().__contains__("inbound"):
                IpPermissionIngress = compileIPPermissionIngress(tmpdic, IpPermissionIngress, 1)
            elif tmpdic["Type"].lower().__contains__("outbound"):
                IpPermissionEgress = compileIPPermissionEgress(tmpdic, IpPermissionEgress, 1)

    authorizeSecurityGroupIngress(sggroupid,IpPermissionIngress)
    authorizeSecurityGroupEgress(sggroupid,IpPermissionEgress)
    sendEmail("NEW_SG_",sggroupid,True,csvbody)

### processUpdateSG
### modify ( add or remove ) ingress or egress record 
### send email notification
def processUpdateSG(csvfilename,csvbody):
    sggroupid=csvfilename.replace("UPDATE_SG_","").replace(".csv", "")

    sgvalue=getSecurityGroup(sggroupid)
    revokeIngressRecords(sgvalue)
    revokeEgressRecords(sgvalue)

    dichead=None
    dicbody=None
    csvbody = removeDuplicateValue(csvbody)
    IpPermissionIngress = []
    IpPermissionEgress = []    
    for x in range(len(csvbody)-1):
        if x==0:
            y= bytes.decode(csvbody[x])
            dichead=y.split(";")
        if x!=0:
            y= bytes.decode(csvbody[x])
            dicbody=y.split(";")

            tmpdic = convertArrToDic(dichead,dicbody)
            if tmpdic["Type"].lower().__contains__("inbound"):
                IpPermissionIngress = compileIPPermissionIngress(tmpdic, IpPermissionIngress, 1)
            elif tmpdic["Type"].lower().__contains__("outbound"):
                IpPermissionEgress = compileIPPermissionEgress(tmpdic, IpPermissionEgress, 1)

    authorizeSecurityGroupIngress(sggroupid,IpPermissionIngress)
    authorizeSecurityGroupEgress(sggroupid,IpPermissionEgress)
    sendEmail("UPDATE_SG_",sggroupid,True,csvbody,sgvalue['SecurityGroups'][0])

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
        processUpdateSG(csvfilename,CSV)
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