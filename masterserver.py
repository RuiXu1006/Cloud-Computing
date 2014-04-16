

import xmlrpclib, os, random
import re
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
import threading
import time
from threading import Thread, Lock, Condition
import random
from os.path import join, getsize


class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

# total number of server
serverNum = 9

# this dictionary is used for serverID for each user
server_record = dict()
# This path is only used for listing files and changing directories
global root_path
# Firstly, get the home directory of the computer
home_dir = os.path.expanduser("~")
root_path = home_dir + "/" + "CloudBox"
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
    def __init__(self):
        Thread.__init__(self)

    # Build directory for master-server at the beginning
    def build_up(self, root_path):
        global lock
        lock.acquire_write()
    # test whether this directory exists or not, if the directory doesn't exits,
    # create root directory for master server
        if not (os.path.exists(root_path)):
            os.mkdir(root_path)
        if not (os.path.exists(root_path + "/" + "Master-Server")):
            os.mkdir(root_path + "/" + "Master-Server")
        lock.release_write()

    # Build server record information when masterserver establishes
    def build_server_record(self):
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
                if ( index > 0 ) and ( content_buffer[index-1] == "ServerID"):
                    server_record[user_name] = content_buffer[index]
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
    def select_server(self):
        minNum = 100000000000L
        svrName = 1
        for item in range(1, serverNum):
            temp = self.getdirsize(root_path + "/" + str(item))
            print 'There are %.3f' % (temp), 'byte in the %d folder' % (item)
            # if current foler is the minimum one, record it
            if ( temp < minNum ):
                minNum = temp
                svrName = item
        print ("From server - " + str(svrName))
        return svrName


    def getRandom(self, sel_server):
        return random.randint((sel_server-1)/2*2+1, (sel_server-1)/2*2+2)

# Sign up new user
    def sign_up1(self, user_name, password):
    # Firstly, make sure that the user_name doesn't exist
        #print "here"
        global lock, serverNum, svr
        lock.acquire_write()
        if user_name in server_record:
            respond = "Error: This username has been used."
            svrName = 0
        # add the user_name and initial password into corresponding user_record of each server
        else:
            initial_password = str(password)
            respond = "Sign up successfully!"
            sel_server = self.select_server()
            for svrN in range((sel_server-1)/2*2+1, (sel_server-1)/2*2+3):
                svrName = "800" + str(svrN)
                server_record[user_name] = svrName
                # record server information into global server information file
                f = open(server_information, 'a')
                content = "Username: " + user_name + "    " + "ServerID: " + str(svrName)
                f.write(content)
                f.close()
                # record new user information into corresponding servers' user information
                """"
                svr[sel_server].user_record[user_name] = initial_password
                """
                dataServerName = "808" + str(svrN)
                tempClient = xmlrpclib.ServerProxy("http://localhost:"+str(dataServerName)+"/")
                print tempClient.system.listMethods()
                tempClient.modifyUserTable(user_name, initial_password)
                tempClient = None
                

                f = open(root_path + "/" + str(svrN) + "/" + "User_information.txt", 'a')
                content = "Username: " + user_name + "    " + "Password: " + initial_password+"\n"
                f.write(content)
                f.close()
                print "finish write to file on server"+ svrName
                # build file folder for new users
                new_dir = root_path + "/" + str(svrName)[len(svrName)-1] + "/" + user_name
                os.mkdir(new_dir)

            lock.release_write()
            svrname = self.getRandom(sel_server)
        return respond, svrName
        
        
# Sign up new user
    def sign_up(self, user_name, password):
    # Firstly, make sure that the user_name doesn't exist
        #print "here"
        global lock, serverNum, svr
        lock.acquire_write()
        print "here sign up"
        if user_name in server_record:
            respond = "Error: This username has been used."
            svrName = 0
        # add the user_name and initial password into corresponding user_record of each server
        else:
            initial_password = str(password)
            respond = "Sign up successfully!"
            sel_server = self.select_server()
            svrName = "800" + str(sel_server)
            server_record[user_name] = svrName
            # record server information into global server information file
            f = open(server_information, 'a')
            content = "Username: " + user_name + "    " + "ServerID: " + str(svrName)
            f.write(content)
            f.close()
            # record new user information into corresponding servers' user information
            svr[sel_server].user_record[user_name] = initial_password
            f = open(root_path + "/" + str(sel_server) + "/" + "User_information.txt", 'a')
            content = "Username: " + user_name + "    " + "Password: " + initial_password
            f.write(content)
            f.close()
            print "here 2"
            #MultiServer(1)
            # build file folder for new users
            new_dir = root_path + "/" + str(svrName)[len(svrName)-1] + "/" + user_name
            os.mkdir(new_dir)

            lock.release_write()
        return respond, svrName

# Client will connect master-server to get the corresponding port
    def query_server(self, user_name):
    # First make sure that the user_name exists
        if user_name in server_record:
            svrName = server_record[user_name]
            respond = "Found"
            return respond, svrName
        else:
            svrName = "8000"
            respond = "Not found"
            return respond, svrName
        
    def run(self):
        self.masterserver = ThreadXMLRPCServer(("localhost", 8000), allow_none=True)
        print "Master-Server has been established!"
        self.build_up(root_path)
        self.build_server_record()
        self.masterserver.register_introspection_functions()
        self.masterserver.register_function(self.sign_up1, "sign_up")
        self.masterserver.register_function(self.query_server, "query_server")
        self.masterserver.serve_forever()


lock = ReadWriteLock()

server = [1]*serverNum
svr = [1]*(serverNum)
masterserver = MasterServer()
masterserver.start()