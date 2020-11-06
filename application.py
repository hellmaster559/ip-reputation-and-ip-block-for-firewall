from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from datetime import date
import time
import sqlite3
import random
import string
import requests
import json
import re
import paramiko
import cmd
import time
import sys


app = Flask(__name__)

con = sqlite3.connect('info.db')

@app.route('/',  methods=["GET", "POST"])
def ip():

    # Defining the api-endpoint
    url = 'https://api.abuseipdb.com/api/v2/check'

    fh = open(r"C:\Users\admin\Desktop\abusalpdw\a.txt", "r+")    #change the path
    fstring = fh.readlines()

    les1=[]
    for line in fstring:

        querystring = {
        'ipAddress': line.rstrip(),
        'maxAgeInDays': '90'
        }

        headers = {
        'Accept': 'application/json',
        'Key': 'API_KEY'  #enter your api key here
        }

        response = requests.request(method='GET', url=url, headers=headers, params=querystring)

        # Formatted output
        decodedResponse = json.loads(response.text)
        les1.append(decodedResponse)
    # TO GET CURRENT TIME AND DATE IN DATABASE
    current_date = date.today()

    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)

    datas=les1.copy()
    for data in datas:
        con = sqlite3.connect('info.db')

        cursorObj = con.cursor()

        infodb = (data['data']['ipAddress'], data['data']['countryCode'], data['data']['abuseConfidenceScore'], current_date, current_time)

        cursorObj.execute("INSERT INTO ip_info (ipAddress, countryCode, abuseConfidenceScore, date, time) VALUES(?, ?, ?, ?, ?)", infodb)

        con.commit()

        #print(data['data']['ipAddress'])

    #fh.truncate(0)
    fh.close()
    return render_template("main.html",datas=datas)


@app.route("/block", methods=['GET', 'POST'])
def block():

    if request.method == 'POST':
        blockip = request.form['ipblock']
        blockip_name = request.form['ipblock_name']
        buff = ''
        resp = ''

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('ip', username='username', password='password')         #enter the ip of firewall,Username and passowrd
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        chan = ssh.invoke_shell()

        # turn off paging
        chan.send('terminal length 0\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        # Display output of first command
        chan.send('config vdom')
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        # Display output of second command
        chan.send('edit *USER*')                                    #change the user 
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        chan.send('config firewall address')
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        chan.send(f'edit {blockip_name}')
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        chan.send('set type ipmask')
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        chan.send(f'set subnet {blockip}/32')
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        chan.send('set associated-interface *PORT_NUMBER*')                 #Enter the interface used in firewall
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        chan.send('end')
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        chan.send('config firewall addrgrp')
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        chan.send('edit "*Block_GROUP*"')               #enter the group name where blocked ip saved
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        chan.send(f'append member "{blockip_name}"')
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        chan.send('next')
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        chan.send('end')
        chan.send('\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        #print (''.join(output))

        ssh.close() 
        return render_template('ipb.html')
    else:
        return render_template('ipb.html')

#ip()