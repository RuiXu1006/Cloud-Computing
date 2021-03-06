from System import Action
import sys
import clr
clr.AddReference('IsisLib')
import Isis 
from Isis import *

import urllib2
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


MasterIPAddr = "10.33.128.79"
DataIPAddr = "10.32.38.93"

# total number of server
serverNum = 8
# the data servers in a group
Num_mem = 2
# the list to store the address of each server
groups = []
for i in range(0, serverNum/Num_mem + 1):
    groups.append([])

# this dictionary is used for serverID for each user
group_record = dict()
# this dict is used for file sharing info
shared_record = dict()
# This path is only used for listing files and changing directories
global root_path
# Firstly, get the home directory of the computer
home_dir = os.path.expanduser("~")
root_path = home_dir + "\\" + "CloudBox"
#if not os.path.exists(root_path):
#    os.mkdir(root_path)
server_information = root_path + "\\" + "Master-Server\Server_information.txt"

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
        self.svr_name = "master_server#" + str(self.id)
        self.key = "ms900" + str(self.id) 
        server_information = root_path + "\\" + "Master-Server" + str(self.id) + "\Server_information.txt"
        # two servers will be assigned into one group
        self.group = Group("group"+"_master")
        # Register Handlers in the group
        self.group.RegisterHandler(0, Action[str, str](self.writeServerInfo))
        self.group.RegisterHandler(1, Action[str, str, str, str](self.register_dsvr))
        self.group.RegisterHandler(2, Action[str](self.update_dsvrinfo))
        self.group.RegisterHandler(3, Action[str, str, str, str](self.updateSharedFile))
        self.group.Join()

    # Security check function will check whether key matches with given data serve name
    def security_svr_check(self, svr_name, svr_key):
        foundmatch = 0
        svr_name_buffer = svr_name.split("#")
        svr_type = svr_name_buffer[0]
        svr_id   = svr_name_buffer[1]
        if svr_type == "master_server":
            if svr_key == "ms" + "900" + svr_id:
                foundmatch = 1
        elif svr_type == "data_server":
            if svr_key == "ds" + "400" + svr_id:
                foundmatch = 1
        else:
            foundmatch = 0
        if foundmatch:
            result = "Authorized access"
            return result
        else:
            result = "Denied access"
            return result

    # Build directory for master-server at the beginning
    def build_up(self, root_path):
        global lock
        lock.acquire_write()
    # test whether this directory exists or not, if the directory doesn't exits,
    # create root directory for master server
        if not (os.path.exists(root_path)):
            os.mkdir(root_path)
        if not (os.path.exists(root_path + "\\" + "Master-Server" +str(self.id))):
            os.mkdir(root_path + "\\" + "Master-Server" + str(self.id))

        # Building running log file
        if not (os.path.exists(root_path + "\\" + "Running_Log.txt")):
            f = open(root_path + "\\" + "Running_Log.txt", 'w+')
            f.close()
        else:
            f = open(root_path + "\\" + "Running_Log.txt", 'r')
            f.close()

        # Building data server information file, if exists, flush all content
        if not (os.path.exists(root_path + "\\" + "Master-Server" +str(self.id) + "\\" + "Data_server_information.txt")):
            f = open(root_path + "\\" + "Master-Server" +str(self.id) + "\\" +"Data_server_information.txt", 'w+')
            f.close()
        else:
            f = open(root_path + "\\" + "Master-Server" +str(self.id) + "\\" + "Data_server_information.txt", 'w')
            f.flush()
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
    def getdirsize(self, id):
        try:
            data_server = xmlrpclib.ServerProxy("http://" + DataIPAddr + ":800" + str(id) +"/")
            self.writeLog("RPC connected! here")
            size = data_server.getdirsize()
            return size
        except:
            return 1000000000L

# Selecting server based on the size of each server, and select the one which has the
# least size
    def select_group(self):
        minNum = 100000000000L
        grpName = 1
        for item in range(1, serverNum, Num_mem):
            temp = 0
            for member in range (0, Num_mem):
                temp = temp + self.getdirsize(item + member)
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
        self.writeLog("MasterServer" + str(self.id)+" is handling sign_up")
        global lock, serverNum, svr
        lock.acquire_write()
        user_name_used = False
        # Firstly make sure that this username doesn't exist
        if user_name in group_record:
            respond = "Error: This username has been used."
            user_name_used = True
        # add the user_name and initial password into corresponding user_record of each server
        else:
            initial_password = str(password)
            respond = "Sign up successfully!"
            sel_group = self.select_group()
            # record server information into global server information file
            self.writeServerInfo_cmd(user_name, str(sel_group))
            
            
            # choose one of the data server
            for svrN in range(0, len(groups[sel_group])):
                # Only the first member in the group needs to broadcast all members in the group
                if svrN == 0:
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
                    tempClient.modifyUserTable(user_name, initial_password, self.svr_name, self.key)
                    tempClient = None
                    self.writeLog("start write user_info!\n")

            lock.release_write()
        # return the list of available data server to the clients
        dsvr_list = []
        if not user_name_used:
            for mem in range(0, len(groups[sel_group])):
                dsvr = groups[sel_group][mem]
                dsvr_list.append(dsvr)
        else:
            dsvr_list = ['none']
        return respond, dsvr_list
        
        
# Client will connect master-server to get the corresponding port
    def query_group(self, user_name):
        dsvr_list = []
    # First make sure that the user_name exists
        if user_name in group_record:
            groupName = group_record[user_name]
            respond = "Found"
            for mem in range(0, len(groups[int(groupName)])):
                dsvr = groups[int(groupName)][mem]
                dsvr_list.append(dsvr)
            return respond, dsvr_list
        else:
            respond = "Not found"
            return respond, dsvr_list

    # When clients fails to connect with data servers, it will request the 
    # master server to update current available data servers based on the 
    # user-name
    def update_dsvr(self, user_name):
        self.writeLog("Enter the phase of update_dsvr\n")
        dsvr_list = []
        # firstly, the user_name need to exist in the current record
        if user_name in group_record:
            groupName = group_record[user_name]
        # Then query the data servers in the same group in one by one, if
        # there is no reply, mark this data server is unavailable
            for mem in range(0, Num_mem):
                dsvr = "http://" + DataIPAddr + ":800" + str(2*int(groupName) - 1 + mem) + "/"
                self.writeLog(dsvr)
                tempClient = xmlrpclib.ServerProxy(dsvr)
                try:
                    respond = tempClient.query_work("Y/N", self.svr_name, self.key)
                    if respond == True:
                        dsvr_list.append(dsvr)
                except:
                    self.writeLog("Data server " + str(dsvr) + "failed")
                    self.update_dsvrinfo_cmd(dsvr)
            return respond, dsvr_list
        else:
           respond = "The user_name doesn't exist, you need to sign up firstly"
           dsvr_list = []
           return respond, dsvr_list
    # This function is used for updating data information in the master server
    def update_dsvrinfo_cmd(self, dsvr):
        self.group.OrderedSend(2, dsvr)

    def update_dsvrinfo(self, dsvr):
        f= open(root_path + "\\" + "Master-Server" +str(self.id) + "\\" +"Data_server_information.txt", 'r')
        lines = f.readlines()
        f.close()
        self.writeLog("Begin modifying in ms" + str(self.id) + "\n")
        f= open(root_path + "\\" + "Master-Server" +str(self.id) + "\\" +"Data_server_information.txt", 'w')
        for line in lines:
            con_buffer = re.split(' ', line)
            self.writeLog("Debug1 "+con_buffer[0])
            self.writeLog("Debug2 "+dsvr)
            if (con_buffer[0]) != "IP_Address:" + dsvr:
                f.write(line)
            else:
                f.write("")
        f.close()


## file_sharing function
## simply consider that the file in the root directory of each dataServer
    def updateSharedFile(self, filename, fromWho, toWho, groupID):
        self.writeLog("enter in updateSharedFile")
        if (shared_record.has_key(toWho) != True):
            shared_record[toWho] = dict();
        shared_record[toWho][filename] = [fromWho, groupID]        
        return

    def updateSharedFile_cmd(self, filename, fromWho, toWho, groupID):
        self.writeLog("enter in ISIS updateSharedFile")
        nr = self.group.OrderedSend(3, filename, fromWho, toWho, groupID)
        return
    
    def getSharingFiles(self, username):
        self.writeLog("enter in getSharingFiles")
        files = []
        if (shared_record.has_key(username) == True):
            files = shared_record[username].keys()
        return files
        
    def downloadFiles(self, filename, username):
        self.writeLog("enter master's download shared")
        groupInfo = int(shared_record[username][filename][1])
        dServer = xmlrpclib.ServerProxy(groups[groupInfo][0])
        dUser = shared_record[username][filename][0]
        respond = dServer.download_files(dUser, filename, 8888)
        return respond

    def writeLog(self, log):
        f = open(root_path + "\\" + "Running_Log.txt", 'a')
        f.write(str(datetime.datetime.now()) + "\n")
        f.write(log)
        f.close()

    # This function is used for registering the data-server information in master server
    def register_dsvr(self, ip_address, id, svr_name, svr_key):
        global lock
        respond = self.security_svr_check(svr_name, svr_key)
        if self.security_svr_check(svr_name, svr_key) == "Authorized access":
            lock.acquire_write()
            f = open(root_path + "\\" + "Master-Server" +str(self.id) + "\\" +"Data_server_information.txt", 'a')
            f.write("IP_Address:" + str(ip_address) + "          ")
            group_id = (int(id)+1)/2
            self.writeLog("register dsvr: groupi"+str(group_id))
            groups[group_id].append(str(ip_address))
            f.write("Group_ID:" + str(group_id) + "\n")
            f.close()
            lock.release_write()
        else:
            self.writeLog("Denied access to master server\n")

    def register_dsvr_cmd(self, ip_address, id, svr_name, svr_key):
        respond = "Register successfully"
        nr = self.group.OrderedSend(1, ip_address, id, svr_name, svr_key)
        return respond

    def getPeer(self, group_num, svr_name, svr_key):
        #return address of node in the same group
        if self.security_svr_check(svr_name, svr_key) == "Authorized access":
            IP_Address = groups[int(group_num)][0]
            return IP_Address

    def run(self):
        self.masterserver = ThreadXMLRPCServer((MasterIPAddr, 8000+self.id*100), allow_none=True)
        
        self.build_up(root_path)
        self.build_group_record()
        self.masterserver.register_introspection_functions()
        self.masterserver.register_function(self.sign_up, "sign_up")
        self.masterserver.register_function(self.query_group, "query_server")
        self.masterserver.register_function(self.update_dsvr, "update_dsvr")
        self.masterserver.register_function(self.register_dsvr_cmd, "register_dsvr")
        self.masterserver.register_function(self.getPeer, "getPeer")

##sharing files functions
        self.masterserver.register_function(self.updateSharedFile_cmd, "updateSharedFile")
        self.masterserver.register_function(self.getSharingFiles, "getSharingFiles")
        self.masterserver.register_function(self.downloadFiles, "downloadFiles")

        self.writeLog("Master-Server has been established!")
        self.masterserver.serve_forever()


lock = ReadWriteLock()

masterSVR = [1] * serverNum
server = [1]*serverNum
svr = [1]*(serverNum)

id = int(sys.argv[1])
master_svr = MasterServer(id);
master_svr.start()

IsisSystem.WaitForever()



