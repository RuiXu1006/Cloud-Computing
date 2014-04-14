# Need to set this file as the startup file in this project
from System.Diagnostics import Process
from System import Action
import sys
import clr
clr.AddReference('IsisLib')
import Isis 
from Isis import * 

for i in range(1,3):
    p = Process()
    p.StartInfo.UseShellExecute = False
    p.StartInfo.RedirectStandardOutput = True
    # put ironpython binary path here
    p.StartInfo.FileName = 'C:\Program Files (x86)\IronPython 2.7\ipy'
    p.StartInfo.Arguments = 'data_server_replica.py '+ str(i)
    p.Start()

