# This part will enable Isis2 Library in the code
from System import Action
import sys
import clr
clr.AddReference('IsisLib')
import Isis 
from Isis import * 

# This file uses RPC method to implement the communcation
# between single client and single data server
import xmlrpclib, os, random
import re,datetime
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
import threading
import time
import shutil
from threading import Thread, Lock, Condition
import random
from os.path import join, getsize
from System import Action

class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


IPAddr = "localhost"

# total number of server
serverNum = 9

# this dictionary is used for serverID for each user
server_record = dict()
# This path is only used for listing files and changing directories
global root_path
# Firstly, get the home directory of the computer
home_dir = os.path.expanduser("~")
root_path = home_dir + "\\" + "CloudBox"
server_information = root_path + "\\" + "Master-Server\Server_information.txt"

IsisSystem.Start()
# This Lock class will used for the synchronization in data servers
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

class MultiServer(Thread):
    def __init__(self, id, recover):
        Thread.__init__(self)
        self.id =id
        self.groupID = (self.id+1)/2
        self.key = "ds400" + str(self.id)
        self.svr_name = "data_server#" + str(self.id)
        self.IPAddr = IPAddr
        self.svrName = "http://"+self.IPAddr+":"+ str(8000+self.id)+"/"
        self.user_information = root_path + "\\" + str(self.id) + "\\" + "User_information.txt"
        self.running_log = root_path + "\\" + str(self.id) + "\\" + "Running_Log.txt"
        # This dictionary is used for storing user information in data server
        self.user_record = dict()
        # This dictionary is used for access key for different users
        self.key_table = dict()
        # two servers will be assigned into one group
        self.group = Group("group"+str((id+1)/2))
        self.group_num = (id+1)/2
        self.recover = recover
        # Register Handlers in the group
        self.group.RegisterHandler(0, Action[str, str, str, str](self.upload_files))
        self.group.RegisterHandler(1, Action[str, str](self.update_keytable))
        self.group.RegisterHandler(2, Action[str, str, str](self.delete_files))
        self.group.RegisterHandler(3, Action[str, str, str](self.change_password))
        self.group.RegisterHandler(4, Action[str, str](self.update_user_record))
        self.group.RegisterHandler(5, Action[str, str, str, str](self.modifyUserTable))
        self.group.RegisterHandler(6, Action[str, str](self.log_out))
        self.group.RegisterHandler(7, Action[str, str, str, str](self.make_directory))
        self.group.RegisterHandler(8, Action[str, str, str, str](self.delete_directory))
        self.group.Join()
    # Security check function will check whether key matches with given user_name
    def security_check(self,user_name, key):
        foundmatch = False
        # for sharing file test
        if key == 8888:
            return user_name
        for key in self.key_table:
            if self.key_table[key] == user_name:
                return user_name
        if ~foundmatch:
            result = "denied access"
            return result

    # Security check function will check whether key matches with given data serve name
    def security_svr_check(self, svr_name, svr_key):
        foundmatch = False
        svr_name_buffer = svr_name.split("#")
        svr_type = svr_name_buffer[0]
        svr_id   = svr_name_buffer[1]
        if svr_type == "master_server":
            if svr_key == "ms" + "900" + svr_id:
                foundmatch = True
        elif svr_type == "data_server":
            if svr_key == "ds" + "400" + svr_id:
                foundmatch = True
        if foundmatch:
            result = "Authorized access"
            return result
        else:
            result = "Denied access"
            return result

     
    # This function is used for server to build directories at the beginning
    def build_up(self,root_path):
        global lock
        lock.acquire_write()
    # tests whether this directory exists or not, if the directory doesn't exist,
    # create root directory for servers
        if not (os.path.exists(root_path)):
            os.mkdir(root_path)
        if not (os.path.exists(root_path+"\\"+str(self.id))):
            os.mkdir(root_path+"\\"+str(self.id))
    # Then, based on the user_record, tests whether each user has its own directory
    # or not, if not, building corresponding folders
        user_folder = root_path + "\default"
        """" the creation of user fold should not build in this function
        for user_name in user_record:
            user_folder = root_path + "\\" +str(self.id) +"\\" + user_name;
        """
        if not (os.path.exists(user_folder)):
            os.mkdir(user_folder)
        
    # Build log file which documents the running information of data server
        if (os.path.exists(self.running_log)):
            f = open(self.running_log, 'r')
        else:
            f = open(self.running_log, 'w+')
        f.close()
        lock.release_write()
        tmpclient = xmlrpclib.ServerProxy("http://localhost:8000/")
        ip_address = "http://" + IPAddr + ":800" + str(self.id) + "/"
        respond = tmpclient.register_dsvr(ip_address, str(self.id), self.svr_name, self.key)
    
    # send command to all members in the group to prepare for updating their own user_record
    def update_user_record_cmd(self, user_name, password):
        self.group.OrderedSend(4, user_name, password)

    # actual operations to updata user_record
    def update_user_record(self, user_name, password):
        self.user_record[user_name] = password

    # This function is used for getting user record from specific file at the beginning
    def build_user_record(self):
        global lock
        lock.acquire_write()
    # firstly check that whether this user information file exist or not
        if os.path.exists(self.user_information):
            f = open(self.user_information, 'r')
        else:
            f = open(self.user_information, 'w+')
        f.close()
        f = open(self.user_information, 'r')
    # Each line in the file store the information of a user, therefore we read a line
    # each time
        content = f.readline()
        while (content):
            content_buffer = re.split('\W+', content)
            for index in range(0, len(content_buffer)):
                if ( index > 0 ) and ( content_buffer[index-1] == "Username"):
                    user_name = content_buffer[index]
                if ( index > 0 ) and ( content_buffer[index-1] == "Password"):
                    password = content_buffer[index]
                    self.update_user_record(user_name, password)
                #if ( index > 0 ) and ( content_buffer[index-1] == "ServerID"):
                #    server_record[user_name] = content_buffer[index]
            content = f.readline()
        lock.release_write()

    # Because each data server will store the user_information of other members in the same group
    # Therefore, when clients change their passowrd, data servers should also notify other servers
    # in the same group, to update the user information too.
    def change_password_cmd(self, user_name, original_password, newpassword):
        respond = True
        res = []
        nr = self.group.OrderedQuery(Group.ALL, 3, user_name, original_password, newpassword, EOLMarker(), res);
        for reply in res:
            if (reply == -1):
                respond = "Change password unsuccessfully!"
                break
        if (respond == True):
            respond = "Change password successfully"
        return respond

        
    # This function is used for changing the password for clients
    # The client has to provide original password, and new password
    def change_password(self, user_name, original_password, new_password):
    # Firstly, make sure that the user_name in the record:
        if user_name in self.user_record:
    # If original password matches, change the password
            if original_password == self.user_record[user_name]:
                self.user_record[user_name] = new_password
                respond = "Change password successfully"
    # update the change of password in user information file
                f = open(self.user_information, 'r')
                lines = f.readlines()
                f.close()
                f = open(self.user_information, 'w')
                for line in lines:
                    con_buffer = re.split('\W+', line)
                    if con_buffer[1] != user_name:
                        f.write(line)
                    else:
                        new_line = "Username: " + user_name + "    " + "Password: " + new_password + '\n'
                        f.write(new_line)
                self.group.Reply(1)
                return
            else:
                respond = "The original password is wrong"
                self.group.Reply(-1)
                return
        else:
            respond = "The username doesn't exist"
            self.group.Reply(-1)
            return

    # This function is used for logining into the date server
    def login_in(self,user_name, password):
        global current_user
        global lock
        lock.acquire_write()
        #print "haha"
    # Firstly, make sure that there is user_name in the record
        respond = "The username doesn't exist"
        svrName = 0
        if user_name in self.user_record.keys():
    # Then check whether the password corresponds or not
            if password == self.user_record[user_name]:
                access_key = random.randint(0, 10000000)
                access_key = str(access_key)
                self.update_keytable_cmd(user_name, access_key)
                respond = "Login in successfully#" + access_key
                current_user = user_name
                #svrName = "800" + str(self.id)
            else:
                respond = "The password doesn't match with the given username"
                svrName = 0
        # if not found in the memory, ask the user information in the disk
        else:
            # refresh user_record
            self.user_record = dict()
            self.build_user_record()
            # if the user stores in the 
            if user_name in self.user_record.keys():
            # Then check whether the password corresponds or not
                if password == self.user_record[user_name]:
                    access_key = random.randint(0, 10000000)
                    access_key = str(access_key)
                    self.update_keytable_cmd(user_name, access_key)
                    respond = "Login in successfully#" + access_key
                    current_user = user_name
                    #svrName = "800" + str(self.id)
                else:
                    respond = "The password doesn't match with the given username"
                    svrName = 0
            else:
                print "user name error"
                respond = "The username doesn't exist"
                svrName = 0
        lock.release_write()
        self.writeLog("haha")
        return respond, self.svrName

    # This function is used for listing files in the data servers

    def list_files(self,user_name,rel_path,key):
        global lock
        lock.acquire_write()
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
        else:
            current_user = self.security_check(user_name, key)
            work_path = root_path + "\\" +str(self.id) +"\\" + current_user + "\\" + rel_path
            file_list = os.listdir(work_path)
            respond = file_list
        lock.release_write()
        f = open(self.running_log, 'a')
        f.write("listfile " + str(self.id) + '\n')
        f.close()
        #print "listfile %d" % self.id
        return respond

    # This function is used for change directories in the data server
    def change_directory(self,user_name,rel_path,key):
        global lock
        lock.acquire_write()
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
        else:
            current_user = self.security_check(user_name, key)
            # get the work path from the information sent by client
            work_path = root_path + "\\" + str(self.id) +"\\" + current_user + rel_path
            #self.writeLog(str(work_path) + "\n")
    # Firstly, check if that this path exist or not
        if os.path.exists(work_path):
    # Then make sure that is directory
            if os.path.isdir(work_path):
                respond = "cd successfully"	
            else:
                respond = "From Server: This is not a directory!"
        else:
            respond = "From Server: This directory doesn't exist!"
        lock.release_write()
        return respond

    # This function is used for search files in the file system
    # of data server, if there is required file, return True,
    # otherwise return false
    def search_files(self,user_name, file_name, key):
        global lock
        lock.acquire_write()
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
        else:
            current_user = self.security_check(user_name, key)
    # set the path of root directory, and found flag to be false
            work_path = root_path + "\\" + str(self.id) +"\\" + current_user
            foundmatch = False
    # With the use of os.walk, go through all files in file system
            for root, dirs, files in os.walk(work_path):
    # If file found, set found flag, and get the location of file
                if file_name in files:
                    file_location = os.path.join(root, file_name)
                    foundmatch = True
                    break
    # If flag is true, found file and return the location
            if foundmatch:
                respond = file_location
    # If flag is false, return false information
            else:
                respond = "Not found"
        
        lock.release_write()    
        return respond

    # This function is used for search directory in the file system
    # of data server, if there is required file, return True,
    # otherwise return false
    def search_dirs(self,user_name, dir_name, key):
        global lock
        lock.acquire_write()
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
        else:
            current_user = self.security_check(user_name, key)
    # set the path of root directory, and found flag to be false
            work_path = root_path + "\\" + str(self.id) +"\\" + current_user
            foundmatch = False
    # With the use of os.walk, go through all files in file system
            for root, dirs, files in os.walk(work_path):
    # If file found, set found flag, and get the location of file
                if dir_name in dirs:
                    dir_location = os.path.join(root, dir_name)
                    foundmatch = True
                    break
    # If flag is true, found file and return the location
            if foundmatch:
                respond = dir_location
    # If flag is false, return false information
            else:
                respond = "Not found"
        
        lock.release_write()    
        return respond

    # This function is used for downloading files to client
    def download_files(self,user_name, file_name, key):
        global lock
        lock.acquire_write()
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
        else:
            current_user =  self.security_check(user_name, key)
    # set the path root directory, and found flag to be false
            work_path = root_path + "\\" + str(self.id) +"\\" + current_user
    # get the file location of give file
            file_location = self.search_files(user_name, file_name, key)
            self.writeLog("From server - The download file locates at " + file_location)
            with open(file_location, "rb") as handle:
                respond = xmlrpclib.Binary(handle.read())
        lock.release_write()
        return respond
    
    # This function will use call isis to update the key table of all memebers in the group
    def update_keytable_cmd(self, user_name, key):
        self.group.OrderedSend(1, user_name, key)
               
    def update_keytable(self, user_name, key):
        self.key_table[key] = user_name

    # In order to keep consistency of the whole system, when uploading a file to a server, 
    # it is also necessary to upload files to other servers in the same group
    def upload_files_cmd(self, user_name, file_name, transmit_data, key):
        #print "Enter upload files cmd"
        respond = True
        res = []
        nr = self.group.OrderedQuery(Group.ALL, 0, user_name, file_name, transmit_data.data, key, EOLMarker(), res)
        # if there are some fails in some servers, return False 
        for reply in res:
            if (reply == -1):
                respond = False
                break
        return respond

    # This function is used for uploading files from client
    def upload_files(self,user_name,file_name, transmit_data, key):
        global lock
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
            self.group.Reply(-1)
            return
        else:
            lock.acquire_write()
            current_user = self.security_check(user_name, key)
    # set the root directory to store upload files, and get
    # the file location
            work_path = root_path + "\\" + str(self.id) +"\\" +current_user;
            file_location = work_path + "\\" + file_name
            file_dir = '\\'.join(file_location.split('\\')[:-1])
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            with open(file_location, "wb") as handle:
                handle.write(transmit_data)
            lock.release_write()
            self.group.Reply(1)
            return

    # The situation is same as uploading files
    def delete_files_cmd(self, user_name, file_name, key):
        #print "Enter upload files cmd"
        respond = True
        res = []
        nr = self.group.OrderedQuery(Group.ALL, 2, user_name, file_name, key, EOLMarker(), res)
        # if there are some fails in some servers, return False 
        for reply in res:
            if (reply == -1):
                respond = False
                break
        return respond

    # This function is used for deleting files from server
    def delete_files(self,user_name, file_name, key):
        global lock
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
            self.group.Reply(-1)
            return
        else:
            lock.acquire_write()
            current_user = self.security_check(user_name, key)
    # get the location of the file which will be deleted
            file_location = self.search_files(user_name, file_name, key)
            os.remove(file_location)
            lock.release_write()
            self.group.Reply(1)
            return

    def delete_files_cmd(self, user_name, file_name, key):
        #print "Enter upload files cmd"
        respond = True
        res = []
        nr = self.group.OrderedQuery(Group.ALL, 2, user_name, file_name, key, EOLMarker(), res)
        # if there are some fails in some servers, return False 
        for reply in res:
            if (reply == -1):
                respond = False
                break
        return respond
    
    # This function is used for making directory in the data server
    def make_directory(self, rel_path, dir_name, user_name, key):
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
            self.group.Reply(-1)
            return
        else:
            current_user = self.security_check(user_name, key)
            # firstly check whether this directory exists
            if (os.path.exists(root_path + "\\" + str(self.id) + "\\" + current_user + rel_path + "\\" + dir_name)):
                respond = "This directory has existed!"
                self.group.Reply(0)
                return
            else:
                os.mkdir(root_path + "\\" + str(self.id) + "\\" + current_user + rel_path + "\\" + dir_name)
                respond = "Making directory successfully!"
                self.group.Reply(1)
                return

    def make_directory_cmd(self, rel_path, dir_name, user_name, key):
        reply = 1
        res = []
        nr = self.group.OrderedQuery(Group.ALL, 7, rel_path, dir_name, user_name, key, EOLMarker(), res)
        for res_g in res:
            if ( res_g == -1 ):
                reply = -1
                break
            elif ( res_g == 0 ):
                reply = 0
                break
        if reply == 1:
            respond = "Make directory successfully!"
        elif reply == -1:
            respond = "You have no right to use this function"
        else:
            respond = "This directory has existed!"
        return respond

    # This function is used for deleting directory
    def delete_directory(self, rel_path, dir_name, user_name, key):
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
            self.group.Reply(-1)
            return
        else:
            current_user = self.security_check(user_name, key)
            # firstly check whether this directory exists
            if not (os.path.exists(root_path + "\\" + str(self.id) + "\\" + current_user + rel_path + "\\" + dir_name)):
                respond = "This directory doesn't exist"
                self.group.Reply(0)
                return
            elif not (os.path.isdir(root_path + "\\" + str(self.id) + "\\" + current_user + rel_path + "\\" + dir_name)):
                respond = "This is not a directory"
                self.group.Reply(2)
                return
            else:
                shutil.rmtree(root_path + "\\" + str(self.id) + "\\" + current_user + rel_path + "\\" + dir_name)
                respond = "Deleting directory successfully!"
                self.group.Reply(1)
                return

    def delete_directory_cmd(self, rel_path, dir_name, user_name, key):
        reply = 1
        res = []
        nr = self.group.OrderedQuery(Group.ALL, 8, rel_path, dir_name, user_name, key, EOLMarker(), res)
        for res_g in res:
            if ( res_g == -1 ):
                reply = -1
                break
            elif ( res_g == 0 ):
                reply = 0
                break
            elif ( res_g == 2 ):
                reply = 2
                break
        if reply == 1:
            respond = "Deleting directory successfully!"
        elif reply == -1:
            respond = "You have no right to use this function"
        elif reply == 2:
            respond = "This is not a directory"
        else:
            respond = "This directory doesn't exist!"
        return respond

    # This function is used for users' logging out
    def log_out_cmd(self, user_name, key):
        reply = True
        res = []
        nr = self.group.OrderedQuery(Group.ALL, 6, user_name, key, EOLMarker(), res)
        for res_g in res:
            if ( res_g == -1 ):
                reply = False
                break
        if reply:
            respond = "Log out successfully!"
        else:
            respond = "Log out unsuccessfully!"
        return respond 

    def log_out(self, user_name, key):
        if self.security_check(user_name, key) == "denied access":
            self.group.Reply(-1)
            return
        else:
            if user_name in self.user_record:
                del self.user_record[user_name]
                del self.key_table[key]
                self.group.Reply(1)
                return
            else:
                self.group.Reply(-1)
                return
## file_sharing function
    def share_File(self, fromWho, filename, toWho):
        #send to master sever
        self.writeLog("enter in share_file")
        master = xmlrpclib.ServerProxy("http://localhost:8000/")
        master.updateSharedFile(filename, fromWho, toWho, self.groupID)
        return

## file_sharing function
    def list_SharedFiles(self, user_name):
        #retrieve info from master server
        self.writeLog("enter in list_share")
        master = xmlrpclib.ServerProxy("http://localhost:8000/")
        files = master.getSharingFiles(user_name)
        return files

## file_sharing function
    def download_SharedFiles(self,filename,user_name):
        # call the specific dataServer
        self.writeLog("enter download sharedFiles")
        master = xmlrpclib.ServerProxy("http://localhost:8000/")
        respond = master.downloadFiles(filename,user_name)
        self.writeLog("finish fetching file")
        return respond

    def modifyUserTable_cmd(self,user_name, initial_password, svr_name, svr_key):
        respond = True
        res = []
        nr = self.group.OrderedQuery(Group.ALL, 5, user_name,initial_password, svr_name, svr_key, EOLMarker(), res)
        for reply in res:
            if (reply == -1):
                respond = False
                break
        return respond

    def modifyUserTable(self, user_name, initial_password, svr_name, svr_key):
        if self.security_svr_check(svr_name, svr_key) == "Authorized access":
            self.writeLog("modifying User Table")
            svr.user_record[user_name] = initial_password
            self.writeLog(str(self.id) + " "+ str(user_name) + " " + str(initial_password)+"\n")
            f = open(root_path + "\\" + str(self.id) + "\\" + "User_information.txt", 'a')
            content = "Username: " + user_name + "    " + "Password: " + initial_password+"\n"
            f.write(content)
            f.close()
            self.writeLog("finish write to file on server"+ "800"+ str(self.id))
            # build file folder for new users
            new_dir = root_path + "\\" + str(self.id) + "\\" + user_name
            os.mkdir(new_dir)
            self.group.Reply(1)
            return
        else:
            self.group.Reply(-1)
            return

    # This function is used for proving that the data server currently works
    def query_work(self, str, svr_name, svr_key):
        if self.security_svr_check(svr_name, svr_key) == "Authorized access":
            return True
        else:
            return False

    def writeLog(self, log):
        f = open(root_path + "\\" + "Running_Log.txt", 'a')
        f.write(str(datetime.datetime.now()) + "\n")
        f.write(log)
        f.close()

    def getFilelist(self, svr_name, svr_key):
        if self.security_svr_check(svr_name, svr_key) == "Authorized access":
            file_list = []
            sourcePath = root_path + "\\" + str(self.id) + "\\"
            for root, dirs, files in os.walk(sourcePath):
                for f in files:
                    file_abspath = os.path.join(root, f)
                    file_relpath = os.path.relpath(file_abspath, root_path + "\\" + str(self.id) + "\\")
                    file_list.append(file_relpath)

        return file_list

    def getfilelist_client(self, user_name, key, dir_location):
        if self.security_check(user_name, key) == "denied access":
            file_list = ["none"]
        else:
            file_list = []
            for root, dirs, files in os.walk(dir_location):
                for f in files:
                    file_abspath = os.path.join(root, f)
                    file_relpath = os.path.relpath(file_abspath, dir_location)
                    file_list.append(file_relpath)
        return file_list

    def copyFile(self, fileLoc, svr_name, svr_key):
        if self.security_svr_check(svr_name, svr_key) == "Authorized access":
            sourcePath = root_path + "\\" + str(self.id) + "\\"
            with open(sourcePath + fileLoc, "rb") as handle:
                self.writeLog("Copying file" + sourcePath+fileLoc+'\n')
                filedata = xmlrpclib.Binary(handle.read())

        return filedata


    def run(self):
        global server
        server[self.id] = ThreadXMLRPCServer((IPAddr, 8000+self.id), allow_none=True)
        
        self.writeLog("port " + str(self.id + 8000) + " is established!\n")
        self.build_up(root_path)
        self.build_user_record()
        server[self.id].register_introspection_functions()
        server[self.id].register_function(self.writeLog, "writeLog")
        server[self.id].register_function(self.modifyUserTable_cmd, "modifyUserTable")
        server[self.id].register_function(self.change_password_cmd, "change_password")
        server[self.id].register_function(self.login_in, "login_in")
        server[self.id].register_function(self.list_files, "list_files")
        server[self.id].register_function(self.change_directory, "change_directory")
        server[self.id].register_function(self.search_files, "search_files")
        server[self.id].register_function(self.search_dirs,  "search_dirs")
        server[self.id].register_function(self.download_files, "download_files")
        server[self.id].register_function(self.upload_files_cmd, "upload_files")
        server[self.id].register_function(self.delete_files_cmd, "delete_files")
        server[self.id].register_function(self.make_directory_cmd, "make_directory")
        server[self.id].register_function(self.delete_directory_cmd, "delete_directory")
        server[self.id].register_function(self.log_out_cmd, "log_out")
        server[self.id].register_function(self.query_work,"query_work")
        server[self.id].register_function(self.getFilelist,"getFilelist")
        server[self.id].register_function(self.getfilelist_client,"getfilelist_client")
        server[self.id].register_function(self.copyFile,"copyFile")

        #### sharing file
        server[self.id].register_function(self.share_File, "share_File")
        server[self.id].register_function(self.list_SharedFiles, "list_SharedFiles")
        server[self.id].register_function(self.download_SharedFiles, "download_SharedFiles")


        #connect to master server to obtain server in the same group
        if self.recover:
            master_server = xmlrpclib.ServerProxy("http://" + IPAddr + ":8000/")
            peer_addr = master_server.getPeer(self.group_num, self.svr_name, self.id)
            peer_server = xmlrpclib.ServerProxy(peer_addr)
            file_list = peer_server.getFilelist(self.svr_name, self.key)
            for f in file_list:
                fileLoc = root_path + "\\" + str(self.id) + "\\" + f
                fileDir = '\\'.join(fileLoc.split('\\')[:-1])
                self.writeLog("The file directory is " + fileDir + "\n")
                if not os.path.exists(fileDir):
                    os.makedirs(fileDir)
                fileData = peer_server.copyFile(f, self.svr_name, self.key)
                with open(fileLoc, "wb+") as handle:
                    handle.write(fileData.data)


        server[self.id].serve_forever()

lock = ReadWriteLock()

server = [1]*serverNum

id = int(sys.argv[1])
recover = bool(int(sys.argv[2]))
svr = MultiServer(id, recover);
svr.start()

IsisSystem.WaitForever()





