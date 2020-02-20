import sys
import os, errno
import subprocess
import ipaddress
from datetime import date
import sqlite3
import csv
import base64
from .models import Nmap
from .resources import NmapResource
from celery import shared_task
import json
from jsonmerge import merge
from jsonmerge import Merger

class NmapManager:

    #NMAP PROCESS FOLDER
    nmap_process_folder = "./scans/results/"
    nmap_process_folder_reports = "./scans/reports/"

    def handle_uploaded_file(file,filename):
        with open(filename, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    #Create folder /data/ + /data/<title>-date
    def create_folder(title):
        if not os.path.exists(NmapManager.nmap_process_folder):
            while True:
                try:
                    os.makedirs(NmapManager.nmap_process_folder)
                    break
                except ValueError:
                    print('Impossible to create the folder %sl') % nmap_process_folder

        full_path_clean = os.path.join(NmapManager.nmap_process_folder, title).replace(" ", "\ ") + "-" + str(date.today())
        full_path = os.path.join(NmapManager.nmap_process_folder, title) + "-" + str(date.today())
        if os.path.exists(full_path):
            i=0
            while os.path.exists(full_path+str(i)):
                i=i+1
            full_path=full_path+str(i)
        
        while True:
            try:
                os.makedirs(full_path)
                break
            except ValueError:
                print('Impossible to create the folder %sl') % full_path

        return full_path_clean

    #Create folder /reports/ + /reports/reports.csv, json, yaml
    def create_folder_reports():
        if not os.path.exists(NmapManager.nmap_process_folder_reports):
            while True:
                try:
                    os.makedirs(NmapManager.nmap_process_folder_reports)
                    break
                except ValueError:
                    print('Impossible to create the folder %sl') % nmap_process_folder_reports

    def nessusProcess(title, targets, file):
        #TODO
        return None

    #Launch a subprocess
    """def launchSubprocess(command):
        while True:
            try:
                subprocess.call(command, shell=True)
                break
            except ValueError:
                print(command + ' is not working !')

    #Launch a subprocess csv
    def launchSubprocess_csv(command, output_csv):
        while True:
            try:
                subprocess(command, shell=True)
                NmapManager.importToPostgreSQL(output_csv)
                break
            except ValueError:
                print(command + ' is not working !')
    """

    @shared_task
    def nmapProcess(title, targets, file, nmapOptions):
        #Creation of the folder to store nmap data
        folder_path = NmapManager.create_folder(title)

        #Targets treatment : write .input file
        input_filename = "%(1)s/%(2)s-%(3)s.input" % {"1" : folder_path, "2" : title, "3" : date.today()}
        if file:
            NmapManager.handle_uploaded_file(file, input_filename)
        else:
            input_file = open(input_filename,"w")
            for element in targets.split(";"):
                input_file.write(element+"\n")
            input_file.close()

        #For each IP or domain, make a nmap in a subprocess
        with open(input_filename) as f:
            for IP in f:
                IP = IP.rstrip()
                print(IP)
                if IP.find('/')!=-1:
                #if '/' in IP:
                    IP = list(ipaddress.ip_network(IP, False).hosts())
                    for IPs in IP:
                        print(IPs)
                        IPs = str(IPs)
                        print(IPs)
                        #Commands preparation for nmap and nmaptocsv execution
                        #output_xml = "%(1)s/%(2)s-%(3)s.xml" % {"1" : folder_path, "2" : IPs, "3" : date.today()}
                        output_xml = "%(1)s/%(2)s.xml" % {"1" : folder_path, "2" : IPs}
                        command_nmap = "nmap %(1)s -oX %(2)s %(3)s" % {"1" : IPs, "2" : output_xml, "3" : nmapOptions}
                        #output_csv = "%(1)s/%(2)s-%(3)s.csv" % {"1" : folder_path, "2" : IPs, "3" : date.today()}
                        output_csv = "%(1)s/%(2)s.csv" % {"1" : folder_path, "2" : IPs}
                        command_csv = "nmaptocsv -s -x %(1)s -o %(2)s" % {"1" : output_xml, "2" : output_csv}
                    
                        #Execution of nmap and nmaptocsv
                        #NmapManager.launchSubprocess.call(command_nmap)
                        #NmapManager.launchSubprocess_csv.call(command_csv, output_csv)
                        #Launch a subprocess
                        while True:
                            try:
                                subprocess.call(command_nmap, shell=True)
                                break
                            except ValueError:
                                print(command + ' is not working !')

                    #Launch a subprocess csv
                        while True:
                            try:
                                subprocess.call(command_csv, shell=True)
                                NmapManager.importToPostgreSQL(output_csv)
                                break
                            except ValueError:
                                print(command + ' is not working !')
                             
                        """#NmapManager.importToPostgreSQL(output_csv)"""

                else:

                    #Commands preparation for nmap and nmaptocsv execution
                    #output_xml = "%(1)s/%(2)s-%(3)s.xml" % {"1" : folder_path, "2" : IP, "3" : date.today()}
                    output_xml = "%(1)s/%(2)s.xml" % {"1" : folder_path, "2" : IP}
                    command_nmap = "nmap %(1)s -oX %(2)s %(3)s" % {"1" : IP, "2" : output_xml, "3" : nmapOptions}
                    #output_csv = "%(1)s/%(2)s-%(3)s.csv" % {"1" : folder_path, "2" : IP, "3" : date.today()}
                    output_csv = "%(1)s/%(2)s.csv" % {"1" : folder_path, "2" : IP}
                    command_csv = "nmaptocsv -s -x %(1)s -o %(2)s" % {"1" : output_xml, "2" : output_csv}
                    
                    #Execution of nmap and nmaptocsv
                    #NmapManager.launchSubprocess(command_nmap)
                    #NmapManager.launchSubprocess_csv(command_csv)

                    #Launch a subprocessl
                    while True:
                        try:
                            subprocess.call(command_nmap, shell=True)
                            break
                        except ValueError:
                            print('Something goes wrong with nmap !')

                    #Launch a subprocess csv
                    while True:
                        try:
                            subprocess.call(command_csv, shell=True)
                            NmapManager.importToPostgreSQL(output_csv)
                            break
                        except ValueError:
                            print('Something goes wrong with nmaptocsv !')
                         
                    """#NmapManager.importToPostgreSQL(output_csv)"""

        return True

    #Add the CSV content to the database
    def importToPostgreSQL(csvfilename):
        with open(csvfilename, 'r') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=';')
            iterrow = iter(readCSV)
            #next(iterrow)
            for row in iterrow:
                if row != []:
                    modelpsql = Nmap(IP=row[0], FQDN=row[1], PORT=row[2], PROTOCOL=row[3], SERVICE=row[4], VERSION=row[5])
                    try:
                        modelpsql.save()
                    except:
                        print("Something goes wrong with psql.")

    #Return the database content into a CSV file
    def DBtoCSV():
        nmap_resource = NmapResource()
        dataset = nmap_resource.export()
        return dataset.csv

    #Return the database content into a JSON file
    def DBtoJSON():
        nmap_resource = NmapResource()
        dataset = nmap_resource.export()
        return dataset.json

    #Return the database content into a YAML file
    def DBtoYAML():
        nmap_resource = NmapResource()
        dataset = nmap_resource.export()
        return dataset.yaml

    #Create a JSON to display graphs
    def JSONforGraph():
        schema = {
            "net": "string",
            "mask": "number",
            "children":
            {
                "net": "string",
                "mask": "number",
                "children":
                {
                    "net": "string",
                    "mask": "number",
                    "children":
                    {
                        "IP": "string",
                        "FQDN": "string",
                        "children":
                        {
                            "Protocol": "string",
                            "Port": "number",
                            "Service": "string",
                            #"Version": "string",
                            "mergeStrategy": "arrayMergeById",
                            "mergeOptions": {"idRef": "/Port"}
                        },
                    },
                    "mergeStrategy": "arrayMergeById",
                    "mergeOptions": {"idRef": "/net"}
                    #"mergeStrategy": "append"
              
                },
            "mergeStrategy": "arrayMergeById",
            "mergeOptions": {"idRef": "/net"}
            #"mergeStrategy": "append"
            },
           }
        merger = Merger(schema)
        try:
            jsonInput = json.loads(NmapManager.DBtoJSON())
        except ValueError:
            print ("error loading JSON")
        
        IP_v1 = jsonInput[0]['IP']
        FQDN_v1 = jsonInput[0]['FQDN']
        PORT_v1 = jsonInput[0]['PORT']
        PROTOCOL_v1 = jsonInput[0]['PROTOCOL']
        SERVICE_v1 = jsonInput[0]['SERVICE']
        VERSION_v1 = jsonInput[0]['VERSION']
        W_v1,X_v1,Y_v1,Z_v1 = IP_v1.split('.')

        subnetService = {
            "Protocol": PROTOCOL_v1,
            "Port": PORT_v1,
            "Service": SERVICE_v1,
            "Version": VERSION_v1
        }

        subnetIP = {
            "IP": IP_v1,
            "FQDN": FQDN_v1,
            "children": subnetService
        }

        subnet24 = {
                "net": W_v1+'.'+X_v1+'.'+Y_v1+'.0',
                "mask": "24",
                "children": subnetIP
        }

        subnet16 = {
            "net": W_v1+'.'+X_v1+'0.0',
            "mask": "16",
            "children": subnet24
        }

        subnet8 = {
            "net": W_v1+'.0.0.0',
            "mask": "8",
            "children": subnet16
        }


        v1 ={}
        v1['net'] = '0.0.0.0'
        v1['mask'] = '0'
        v1['children'] = subnet8

        base = None
        #base = merger.merge(base,v1,meta={"version": 1})
        base = merger.merge(base,v1)
        k=2

        for i in jsonInput:
         
            IP = i['IP']
            FQDN = i['FQDN']
            PORT = i['PORT']
            PROTOCOL = i['PROTOCOL']
            SERVICE = i['SERVICE']
            VERSION = i['VERSION']
            W,X,Y,Z = IP.split('.')

            subnetService = {
            "Protocol": PROTOCOL,
            "Port": PORT,
            "Service": SERVICE,
            "Version": VERSION
            }

            subnetIP = {
                "IP": IP,
                "FQDN": FQDN,
                "children": subnetService
            }

            subnet24 = {
                "net": W+'.'+X+'.'+Y+'.0',
                "mask": "24",
                "children": subnetIP
            }

            subnet16 = {
                "net": W+'.'+X+'0.0',
                "mask": "16",
                "children": subnet24
            }

            subnet8 = {
                "net": W+'.0.0.0',
                "mask": "8",
                "children": subnet16
            }

            v2 ={}
            v2['net'] = '0.0.0.0'
            v2['mask'] = '0'
            v2['children'] = subnet8

            #base = merger.merge(base,v2,meta={"version": k})
            base = merger.merge(base,v2)
            k=k+1
                     
        json_data = json.dumps(base)
        print(json_data)
        return json_data

    """#Merge 2 JSON
    def JSONmerge(json1, json2):
        try:
            jsonInput1 = json.loads(json1)
        except ValueError:
            print ("error loading JSON")
        try:
            jsonInput2 = json.loads(json2)
        except ValueError:
            print ("error loading JSON")

        if jsonInput1['net'] == jsonInput2['net']:
        elif jsonInput1['net'][] == jsonInput2['net']:"""