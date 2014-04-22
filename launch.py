# Need to set this file as the startup file in this project
from System.Diagnostics import Process
from System import Action
import sys
import clr
clr.AddReference('IsisLib')
import Isis 
from Isis import * 
import os
home_dir = os.path.expanduser("~")
root_path = home_dir + "/" + "CloudBox"
f = open(root_path + "/" + "Running_Log.txt", 'w')
f.close()

p = Process()
masterNum = 2
for i in range(0, masterNum+1):
    p.StartInfo.UseShellExecute = False
    p.StartInfo.RedirectStandardOutput = True
    p.StartInfo.FileName = 'C:\Program Files (x86)\IronPython 2.7\ipy'
    p.StartInfo.Arguments = 'master_server.py ' + str(i)
    p.Start()

svrNum  = 8
for i in range(1, svrNum+1):
    p = Process()
    p.StartInfo.UseShellExecute = False
    p.StartInfo.RedirectStandardOutput = True
    # put ironpython binary path here
    p.StartInfo.FileName = 'C:\Program Files (x86)\IronPython 2.7\ipy'
    p.StartInfo.Arguments = 'data_server_replica.py '+ str(i)
    p.Start()

