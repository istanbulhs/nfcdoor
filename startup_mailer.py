#!/usr/bin/python
import commands
import ParsePy
import serial
import ftplib
import os
import sys
import traceback
import subprocess
import smtplib
import socket
from email.mime.text import MIMEText
import datetime
import time
from threading import Thread
import httplib, urllib
from constants import strings


def OpenDoor():
	subprocess.call(['./servo.py'])

def uploadPhotoTaken():
	ftp = ftplib.FTP()
	ftp.connect(strings.FTP_URL)
	ftp.login(strings.FTP_LOGIN, strings.FTP_PASS)  
	fullname = './webcam.png'
	name = os.path.split(fullname)[1]
	f = open(fullname, "rb")
	name = os.path.split(fullname)[1]
	f = open(fullname, "rb")
	ftp.storbinary('STOR ' + name, f)
	f.close()


def WrongId():
	
	nfc= ParsePy.ParseObject("NFC")
	nfc.TagId = id
	nfc.HasAccess=False
	nfc.save()
	subprocess.call(['./camera.sh'])
	uploadPhotoTaken();
	#ser.write('d');
	
def ExistingWrongId():
	subprocess.call(['./camera.sh'])
	uploadPhotoTaken();
	#ser.write('d');
	
def AdminCheck(i):
	while(1):
		AdminOrder = ParsePy.ParseQuery("KapiAc")
		AdminOrder = AdminOrder.eq("KapiAc", True)
		fetchit=AdminOrder.fetch()
		if (len(fetchit)>0):
			if(fetchit[0].KapiAc):
				fetchit[0].KapiAc=False;
				fetchit[0].save()
				OpenDoor();
				print "Kapi Aciliyor.."
		time.sleep(5)
		
def sendIPWithEmail():
	# Change to your own account information
	to = strings.EMAIL_TO
	gmail_user = strings.EMAIL_FROM
	gmail_password = strings.EMAIL_PASS
	smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
	smtpserver.ehlo()
	smtpserver.starttls()
	smtpserver.ehlo()
	smtpserver.login(gmail_user, gmail_password)
	today = datetime.date.today()
	# Very Linux Specific
	arg='ip route list'
	p=subprocess.Popen(arg,shell=True,stdout=subprocess.PIPE)
	data = p.communicate()
	split_data = data[0].split()
	ipaddr = split_data[split_data.index('src')+1]
	my_ip = 'Your ip is %s' %  ipaddr
	msg = MIMEText(my_ip)
	msg['Subject'] = 'IP For RaspberryPi on %s' % today.strftime('%b %d %Y')
	msg['From'] = gmail_user
	msg['To'] = to
	smtpserver.sendmail(gmail_user, [to], msg.as_string())
	smtpserver.quit()

ParsePy.APPLICATION_ID = strings.PARSE_APP_ID
ParsePy.MASTER_KEY = strings.PARSE_MASTER_KEY


while (1):
	( stat, id ) = commands.getstatusoutput( "sudo ./nfc-poll")

	query = ParsePy.ParseQuery("NFC")
	query = query.eq("TagId", id)
	fetched=query.fetch()
	print fetched
	
	if (len(fetched)>0):
		if(fetched[0].HasAccess):
			print "Kapi Aciliyor.."
			OpenDoor();
		else:
			ExistingWrongId();
			print "Intruder Alert.."
	else:
		WrongId();
		print "Intruder Alert.."
	
t = Thread(target=AdminCheck, args=(0,))
t.start()
