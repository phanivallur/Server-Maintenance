#!/usr/local/bin/python2.7

import base64
import json
import requests
import os
import re
import shutil
import MySQLdb
import getpass

username="phani.valluri@accelerite.com"
password="phani@123"

nonClosedCases=[]
rootFolder="/case_data"
num_pattern=r"^\d{5,}$"
db=MySQLdb.connect(host="localhost",user="root",passwd="password")

def clearDatabases(currentCase):
    caseDBList=[]
    cur=db.cursor()
    casenum=os.path.basename(currentCase)
    cur.execute("show databases like '%"+casenum+"%';")
    for row in cur.fetchall():
        caseDBList.append(row[0])
    
    for caseDB in caseDBList:
        print("Removing database "+caseDB)
        cur.execute("drop database "+caseDB)


def clearCases(cwd):
        print("Current Working Directory: "+str(cwd))
        caseDirs=[folder for folder in os.listdir(cwd) if os.path.isdir(os.path.join(cwd,folder))]
        print(caseDirs)
        for case in caseDirs:
            if re.search(num_pattern, case):
               url="https://accelerite.zendesk.com/api/v2/tickets/"+str(case)+".json"
               print(url)
               response=requests.get(url, auth=(username, password))
               if response.status_code!=200:
                  print('Status:', response.status_code, 'Problem with the request. Exiting.')
                  exit()
               data=response.json()
               #print(json.dumps(data,indent=4,sort_keys=True))        
               if data["ticket"]["status"] != "solved" and data["ticket"]["status"] != "closed":
                  nonClosedCases.append(case)
            else:
               print(str(case)+" is not a valid case directory") 
        
        for folder in os.listdir(cwd):
            if re.search(num_pattern,folder) and folder not in nonClosedCases:
               clearDatabases(os.path.join(cwd,folder))
               shutil.rmtree(os.path.join(cwd,folder)) 

         
#for eng in engineers:
currentFolder=os.path.join(rootFolder)
clearCases(currentFolder)
