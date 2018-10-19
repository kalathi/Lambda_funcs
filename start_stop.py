#!/usr/bin/python
########################################################################
# Description: Auto Start | Stop the AWS EC2 instances
# Created: Gulfa rani
# Modified: Amit Surana : Replaced IAM Keys with Roles, Script code adjusted to                                                                                         accomodate the feature
########################################################################
import boto.ec2
import sys
import os
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.MIMEText import MIMEText
from email.mime.image import MIMEImage
import smtplib

# specify AWS keys
def main():
    if len(sys.argv) < 2:
        print "Usage: python start_stop.py {start|stop vpc-id}\n"
        sys.exit(0)
    else:
        action = sys.argv[1]
    if action == "start":
        startInstance()
    elif action == "stop":
        stopInstance()
    elif action == "wtsstart":
        start_wts_instances()
    elif action == "wtsstop":
        stop_wts_instances()
    else:
        print "Usage: python start_stop.py {start|stop vpc-id}\n"

# fecth the VPC Details
def get_vpc_details():
    vpcid = sys.argv[2].upper()
    if vpcid == "DV":
        vpcid = 'vpc-72f02e17'
    elif  vpcid == "QA":
        vpcid = 'vpc-61f02e04'
    elif  vpcid == "PD":
        vpcid = 'vpc-88f32ded'
    else:
        print "Invalid VPC ID"
    return vpcid

# Get the Instances Details
def get_instance_id():
    try:
        conn = boto.ec2.connect_to_region("eu-west-1")
    except Exception, e1:
        error1 = "Error1: %s" % str(e1)
        print(error1)
        sys.exit(0)
    try:
        instances_id = []
        instances = []
        vpcid = get_vpc_details()
        reservations = conn.get_all_instances(filters={'vpc-id':vpcid})
        for r in reservations:
            for i in r.instances:
                instances.append(i)
        for instance in instances:
            instances_id.append(instance.id)
        return instances_id
    except Exception, e2:
        error2 = "Error2: %s" % str(e2)
        print(error2)
        sys.exit(0)

#Start The requested Environment based on given VPC-ID
def startInstance():
    #boto.set_stream_logger('boto')
    print "Starting the instance..."
    try:
        conn = boto.ec2.connect_to_region("eu-west-1")
    except Exception, e1:
        error1 = "Error1: %s" % str(e1)
        print(error1)
        sys.exit(0)
    try:
         instance_id = get_instance_id()
         for item in instance_id:
             conn.start_instances(instance_ids=item)
         send_mail()
    except Exception, e2:
        error2 = "Error2: %s" % str(e2)
        print(error2)
        sys.exit(0)

#Stop The requested Environment based on given VPC-ID
def stopInstance():
    print "Stopping the instance..."

    try:
        conn = boto.ec2.connect_to_region("eu-west-1")
    except Exception, e1:
        error1 = "Error1: %s" % str(e1)
        print(error1)
        sys.exit(0)
    try:
         instance_id = get_instance_id()
         for item in instance_id:
             conn.stop_instances(instance_ids=item)
         send_mail()
    except Exception, e2:
        error2 = "Error2: %s" % str(e2)
        print(error2)
        sys.exit(0)

#Start The WTS Instances
def start_wts_instances():
    instlist = []
    print "Starting WTS Instances....."
    try:
        conn = boto.ec2.connect_to_region("eu-west-1")
    except Exception, e1:
        error1 = "Error1: %s" % str(e1)
        print(error1)
        sys.exit(0)
    try:
        with open ('/scripts/WTS_ids') as wts_list:
            for item in wts_list:
                instlist.append(item.rstrip('\n'))
            for i in instlist:
                conn.start_instances(instance_ids=i)
    except Exception, e2:
        error2 = "Error2: %s" % str(e2)
        print(error2)
        sys.exit(0)
    send_mail()

#Stop The WTS Instances
def stop_wts_instances():
    instlist = []
    print "Stoping WTS Instances....."
    try:
        conn = boto.ec2.connect_to_region("eu-west-1")
    except Exception, e1:
        error1 = "Error1: %s" % str(e1)
        print(error1)
        sys.exit(0)
    try:
        with open ('/scripts/WTS_ids') as wts_list:
            for item in wts_list:
                instlist.append(item.rstrip('\n'))
            for i in instlist:
                conn.stop_instances(instance_ids=i)
    except Exception, e2:
        error2 = "Error2: %s" % str(e2)
        print(error2)
        sys.exit(0)
    send_mail()
#Send an Email To Astrus team reagring the Schedule
def send_mail():
    msg = MIMEMultipart()
    msg['Subject'] = 'Environment Scheduling'
    Fromaddr = u'Astrus@kpmg-astrus2.com'
    Toaddr  = ('amit.surana@cognizant.com',)
    cond1 = sys.argv[1]
    if cond1 == "start":
        cond1 = 'Started'
        Env = sys.argv[2]
        Body = "As per Environment scheduling the %s environment Instances has b                                                                                        een %s\n\nRegards,\nAstrus" %(Env,cond1)
    elif cond1 == "stop":
        cond1 = 'Stopped'
        Env = sys.argv[2]
        Body = "As per Environment scheduling the %s environment Instances has b                                                                                        een %s\n\nRegards,\nAstrus" %(Env,cond1)
    elif cond1 == "wtsstop":
        cond1 = 'Stopped'
        Body = "As per Environment scheduling the WTS Instances has been %s\n\nR                                                                                        egards,\nAstrus" %cond1
    elif cond1 == "wtsstart":
        cond1 = 'Started'
        Body = "As per Environment scheduling the WTS Instances has been %s\n\nR                                                                                        egards,\nAstrus" %cond1
    img_data = open("/scripts/TeamWork.jpg", 'rb').read()
    msg.attach(MIMEText(Body, 'plain'))
    image = MIMEImage(img_data, name=os.path.basename("/scripts/TeamWork.jpg"))
    msg.attach(image)
#SMTP Details
    smtp_server = 'email-smtp.eu-west-1.amazonaws.com'
    smtp_username = 'AKIAITZ2RQHEGW5ZOGBA'
    smtp_password = 'AhZdkCnsrQ3jhi3T+jqZWnWX/BhCiSLFWmSjc5jJYbzd'
    smtp_port = '587'
    smtp_do_tls = True
    server = smtplib.SMTP(
        host = smtp_server,
        port = smtp_port,
        timeout = 10
       )
    server.set_debuglevel(10)
    server.starttls()
    server.ehlo()
    server.login(smtp_username, smtp_password)
    server.sendmail(Fromaddr, Toaddr, msg.as_string())
if __name__ == '__main__':
    main()

