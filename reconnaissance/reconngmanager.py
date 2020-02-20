# !/usr/bin/env python
import sys
import os
import subprocess
from datetime import date
import sqlite3
import csv

from pathlib import Path

class ReconNgManager:

    def __init__(self):
        self.home = str(Path.home())

    def write_ressource_file(self, url, selected_modules):
        """
        Creates a ressource file to use with recon-ng
        """
        today = date.today()
        filename = url + "-" + str(today) + ".txt"

        with open(filename, 'w') as target:

            target.write("workspaces select "+ url + "-" + str(today) + '\n')

            #TODO: use other modules than just domains-hosts/...

            for m in selected_modules:
                target.write("use " + "recon/domains-hosts/" + m + '\n')
                target.write("set SOURCE "+ url + '\n')
                target.write("run " + '\n')

            #print("modules added to the file ")
            target.write("use recon/hosts-hosts/resolve" + '\n')
            target.write("set SOURCE default " + '\n')
            #Useless, written outside app - in ~/.recon-ng/./workspaces/wavestone.com-2019-05-10/results.csv
            target.write("use reporting/csv " + '\n')
            target.write("run " + '\n')
            target.write("exit() " + '\n')

        #print("file created")
        return filename

    def collecte_info_sqlite(self, url,selected_modules):
        today = date.today()
        print("Collecting data from: " + self.home + "/.recon-ng/workspaces/" + url + "-" + str(today) + "/data.db")
        database = self.home + "/.recon-ng/workspaces/" + url + "-" + str(today) + "/data.db"
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        modules_string = ""
        for m in selected_modules:
            modules_string = modules_string + "module = '" + m + "' OR "
        modules_string = modules_string[:-3]
        cursor.execute("""SELECT host,ip_address,module FROM hosts WHERE %s""" %modules_string)
        raws = cursor.fetchall()
        #print(type(raws))
        #for i in range(0,len(raws)):
            #print(raws[i])
        #print("all data collected")
        return raws

    def collecte_info_csv(self, url):
        today = date.today()
        fp = open(self.home + "/.recon-ng/workspaces/" + url + "-" + str(today) + "/results.csv")
        fcsv = csv.reader(fp)
        for ligne in fcsv:
            print(ligne[0] + ', ' + ligne[1] + ', ' + ligne[6])
        return fcsv

    def add_api_keys(self):

        pwd = os.getcwd()
        dir = os.path.join(pwd, '')

        filename = "recon-ng_api.keys" #don't put the keys in the code !

        while True:
            try:
                subprocess.call('recon-ng -r ' + filename)
                break
            except ValueError:
                print('Error adding api keys')

        print("API keys added")

    def globalProcess(self, url, selected_modules):

        pwd = os.getcwd()
        dir = os.path.join(pwd, '')

        filename = self.write_ressource_file(url, selected_modules)

        respath = os.path.join(pwd, str(filename))

        while True:
            try:
                subprocess.call('recon-ng -r ' + respath, shell=True)
                break
            except ValueError:
                print('Recon-ng is not working')

        raws = self.collecte_info_sqlite(url,selected_modules)

        fcsv = self.collecte_info_csv(url)

        print("Analysis complete !")
        return raws
