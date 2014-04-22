from System import Action
import sys
import clr
clr.AddReference('IsisLib')
import Isis 
from Isis import *

import xmlrpclib, os, random
import re,datetime
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
import threading
import time
from threading import Thread, Lock, Condition
import random
from os.path import join, getsize

IsisSystem.Start()

class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

# total number of server
serverNum = 9
# the data servers in a group
Num_mem = 2
# the list to store the address of each server
groups = []

# this dictionary is used for serverID for each user
group_record = dict()
# This path is only used for listing files and changing directories
global root_path
# Firstly, get the home directory of the computer
home_dir = os.path.expanduser("~")
root_path = home_dir + "/" + "CloudBox"
#if not os.path.exists(root_path):
#    os.mkdir(root_path)
server_information = root_path + "/" + "Master-Server/Server_information.txt"

# This function is used for testify whether the user has the access to
# use some specific functions


class ReadWriteLock:
    def __init__(self):
        self._read_ready = threading.Condition()
        self._readers = 0
        
    def acquire_read(self):
        self._read_ready.acquire()
        try:
            self._readers+=1
        finally:
            self._read_ready.release()
    
    def release_read(self):
        self._read_ready.acquire()
        try:
            self._readers-=1
            if not self._readers:
                self._read_ready.notifyAll()
        finally:
            self._read_ready.release()
            
    def acquire_write(self):
        self._read_ready.acquire()
        while self._readers:
            self._read_ready.wait()
    
    def release_write(self):
        self._read_ready.release()


class MasterServer(Thread):
    def __init__(self, id):
        global server_information
        Thread.__init__(self)
        self.id = id
        server_information = root_path + "/" + "Master-Server" + str(self.id) + "/Server_information.txt"
        # two servers will be assigned into one group
        self.group = Group("group"+"_master")
        # Register Handlers in the group
        self.group.RegisterHandler(0, Action[str, str](self.writeServerInfo))
        self.group.Join()

    # Build directory for master-server at the beginning
    def build_up(self, root_path):
        global lock
        lock.acquire_write()
    # test whether this directory exists or not, if the directory doesn't exits,
    # create root directory for master server
        if not (os.path.exists(root_path)):
            os.mkdir(root_path)
        if not (os.path.exists(root_path + "/" + "Master-Server" +str(self.id))):
            os.mkdir(root_path + "/" + "Master-Server" + str(self.id))
        if not (os.path.exists(root_path + "/" + "Running_Log.txt")):
            f = open(root_path + "/" + "Running_Log.txt", 'w+')
            f.close()
        else:
            f = open(root_path + "/" + "Running_Log.txt", 'r')
            f.close()
            
            
        # build the server Address for each dataServer
        f = open(root_path + "/" + "Master-Server" + str(self.id) + "/ServerAddress.txt", 'r')
        line = 1
        groups.append([])
        content = f.readline()
        while (content):
            content_buffer = re.split('\t', content)
            groups.append([])
            for i in range(0, len(content_buffer)):
                groups[line].append(re.split('\n', content_buffer[i])[0])
            line += 1
            content = f.readline()
        f.close()
        
        lock.release_write()

    # Build server record information when masterserver establishes
    def build_group_record(self):
    # Using lock to synchronize the operation about server record
        global lock
        lock.acquire_write()
    # firstly check that whether this user information file exist or not
        if os.path.exists(server_information):
            f = open(server_information, 'r')
        else:
            f = open(server_information, 'w+')
        f.close()
        f = open(server_information, 'r')
    # Each line in the file stores the information of a user, therefore we read a line
    # each time
        content = f.readline()
        while (content):
            content_buffer = re.split('\W+', content)
            for index in range(0, len(content_buffer)):
                if ( index > 0 ) and ( content_buffer[index-1] == "Username"):
                    user_name = content_buffer[index]
                if ( index > 0 ) and ( content_buffer[index-1] == "GroupID"):
                    group_record[user_name] = content_buffer[index]
            content = f.readline()
        lock.release_write()

# This will be used for get the size of given directory, and it will help balance the
# load when sign up
    def getdirsize(self, dir):
        size = 0L
        for root, dirs, files in os.walk(dir):
            size += sum([getsize(join(root, name)) for name in files])
        return size

# Selecting server based on the size of each server, and select the one which has the
# least size
    def select_group(self):
        minNum = 100000000000L
        grpName = 1
        for item in range(1, serverNum, Num_mem):
            temp = 0
            for member in range (0, Num_mem):
                temp = temp + self.getdirsize(root_path + "/" + str(item + member))
                #self.writeLog( "There are %.3f" % (temp)+ "byte in the %d folder" % (item)+"\n")
            self.writeLog( "There are %.3f" % (temp) + "byte in the %d group" % (item) + "\n")
            # if current foler is the minimum one, record it
            if ( temp < minNum ):
                minNum = temp
                grpName = int(item/Num_mem) + 1
        self.writeLog ("Selecting group " + str(grpName) + "\n")
        return grpName


    def getRandom(self, sel_server):
        return random.randint((sel_server-1)/2*2+1, (sel_server-1)/2*2+2)

    # write master-server-user-table separately
    def writeServerInfo(self, user_name, grpID):
        group_record[user_name] = grpID
        f = open(server_information, 'a')
        content = "Username: " + user_name + "    " + "GroupID: " + grpID + "\n"
        f.write(content)
        f.close()
        self.group.Reply(1)
        return

    def writeServerInfo_cmd(self, user_name, grpID):
        respond = True
        res = []
        nr = self.group.OrderedQuery(Group.ALL, 0, user_name, grpID, EOLMarker(), res)
        for reply in res:
            if (reply == -1):
                respond = False
                break
        return respond

# Sign up new user
    def sign_up(self, user_name, password):
    # Firstly, make sure that the user_name doesn't exist
        #print "here"
        global lock, serverNum, svr
        lock.acquire_write()
        if user_name in group_record:
            respond = "Error: This username has been used."
            svrName = 0
        # add the user_name and initial password into corresponding user_record of each server
        else:
            initial_password = str(password)
            respond = "Sign up successfully!"
            sel_group = self.select_group()
            # record server information into global server information file
            self.writeServerInfo_cmd(user_name, str(sel_group))
            
            
            # choose one of the data server
            for svrN in range(0, len(groups[sel_group])-1):
                svrName = groups[sel_group][svrN]
                self.writeLog("The current data server is " + str(svrName) + "\n")
                # record new user information into corresponding servers' user information
                """"
                svr[sel_server].user_record[user_name] = initial_password
                """
                dataServerName = svrName
                self.writeLog("from master write to "+dataServerName + "\n")
                tempClient = xmlrpclib.ServerProxy(dataServerName)
                tempClient.writeLog("here!!!")
                #writeLog(tempClient.system.listMethods())
                tempClient.modifyUserTable(user_name, initial_password)
                tempClient = None
                self.writeLog("start write user_info!\n")

            lock.release_write()
        # return the list of available data server to the clients
        dsvr_list = []
        for mem in range(0, len(groups[sel_group])):
            dsvr = groups[sel_group][mem]
            dsvr_list.append(dsvr)
        return respond, dsvr_list
        
        
# Client will connect master-server to get the corresponding port
    def query_group(self, user_name):
        dsvr_list = []
    # First make sure that the user_name exists
        if user_name in group_record:
            groupName = group_record[user_name]
            respond = "Found"
            for mem in range(0, len(groups[sel_group])):
                dsvr = groups[sel_group][mem]
                dsvr_list.append(dsvr)
            return respond, dsvr_list
        else:
            respond = "Not found"
            return respond, dsvr_list

    def writeLog(self, log):
        f = open(root_path + "/" + "Running_Log.txt", 'a')
        f.write(str(datetime.datetime.now()) + "\n")
        f.write(log)
        f.close()

    def run(self):
        self.masterserver = ThreadXMLRPCServer(("localhost", 8000+self.id*1000), allow_none=True)
        print "Master-Server has been established!"
        self.build_up(root_path)
        self.build_group_record()
        self.masterserver.register_introspection_functions()
        self.masterserver.register_function(self.sign_up, "sign_up")
        self.masterserver.register_function(self.query_group, "query_server")
        self.masterserver.serve_forever()


lock = ReadWriteLock()

masterSVR = [1] * serverNum
server = [1]*serverNum
svr = [1]*(serverNum)

id = int(sys.argv[1])
master_svr = MasterServer(id);
master_svr.start()

IsisSystem.WaitForever()

