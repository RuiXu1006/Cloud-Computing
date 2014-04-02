# This file uses RPC method to implement the communcation
# between single client and single data server
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


# This server is used for distributed servers to clients based on
# load balancing
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
	#print svrName
	return svrName

# Sign up new user
    def sign_up(self, user_name, password):
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
	    MultiServer(1)
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
	    return svrName
        else:
	    svrName = "8000"
	    return svrName
        
    def run(self):
        self.masterserver = ThreadXMLRPCServer(("localhost", 8000), allow_none=True)
	print "Master-Server has been established!"
	self.build_up(root_path)
	self.build_server_record()
        self.masterserver.register_introspection_functions()
	self.masterserver.register_function(self.sign_up, "sign_up")
	self.masterserver.register_function(self.query_server, "query_server")
	self.masterserver.serve_forever()

class MultiServer(Thread):
    def __init__(self,id):
        Thread.__init__(self)
        self.id =id
        self.user_information = root_path + "/" + str(self.id) + "/" + "User_information.txt"
        # This dictionary is used for storing user information in data server
	self.user_record = dict()
        # This dictionary is used for access key for different users
	self.key_table = dict()
    
    def security_check(self,user_name, key):
        foundmatch = False
        for key in self.key_table:
            if self.key_table[key] == user_name:
                return user_name
        if ~foundmatch:
            result = "denied access"
            return result
     

    # This function is used for server to build directories at the beginning
    def build_up(self,root_path):
        global lock
        lock.acquire_write()
    # tests whether this directory exists or not, if the directory doesn't exist,
    # create root directory for servers
        if not (os.path.exists(root_path)):
            os.mkdir(root_path)
        if not (os.path.exists(root_path+"/"+str(self.id))):
            os.mkdir(root_path+"/"+str(self.id))
    # Then, based on the user_record, tests whether each user has its own directory
    # or not, if not, building corresponding folders
        user_folder = root_path + "/default"
        """" the creation of user fold should not build in this function
        for user_name in user_record:
            user_folder = root_path + "/" +str(self.id) +"/" + user_name;
        """
        if not (os.path.exists(user_folder)):
            os.mkdir(user_folder)
        lock.release_write()

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
                    self.user_record[user_name] = password
                #if ( index > 0 ) and ( content_buffer[index-1] == "ServerID"):
                #    server_record[user_name] = content_buffer[index]
            content = f.readline()
        lock.release_write()

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
                return respond
            else:
                respond = "The original password is wrong"
                return respond
        else:
            respond = "The username doesn't exist"
            return respond

    # This function is used for logining into the date server
    def login_in(self,user_name, password):
        global current_user
        global lock
        lock.acquire_write()
    # Firstly, make sure that there is user_name in the record
        if user_name in self.user_record.keys():
    # Then check whether the password corresponds or not
            if password == self.user_record[user_name]:
                access_key = random.randint(0, 10000000)
                access_key = str(access_key)
                self.key_table[access_key] = user_name
                respond = "Login in successfully#" + access_key
                current_user = user_name
		svrName = "800" + str(self.id)
            else:
                respond = "The password doesn't match with the given username"
		svrName = 0
        else:
            respond = "The username doesn't exist"
	    svrName = 0
        lock.release_write()
        return respond, svrName

    # This function is used for listing files in the data servers

    def list_files(self,user_name,rel_path,key):
        global lock
        lock.acquire_write()
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
        else:
            current_user = self.security_check(user_name, key)
            work_path = root_path + "/" +str(self.id) +"/" + current_user + "/" + rel_path
            file_list = os.listdir(work_path)
            respond = file_list
        lock.release_write()
        print "listfile %d" % self.id
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
            work_path = root_path + "/" + str(self.id) +"/" + current_user + rel_path
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
            work_path = root_path + "/" + str(self.id) +"/" + current_user
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

    # This function is used for downloading files to client
    def download_files(self,user_name, file_name, key):
        global lock
        lock.acquire_write()
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
        else:
            current_user =  self.security_check(user_name, key)
    # set the path root directory, and found flag to be false
            work_path = root_path + "/" + str(self.id) +"/" + current_user
    # get the file location of give file
            file_location = self.search_files(user_name, file_name, key)
            print "From server - The download file locates at " + file_location
            with open(file_location, "rb") as handle:
                respond = xmlrpclib.Binary(handle.read())
        lock.release_write()
        return respond
            

    # This function is used for uploading files from client
    def upload_files(self,user_name,file_name, transmit_data, key):
        global lock
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
            return respond
        else:
            lock.acquire_write()
            current_user = self.security_check(user_name, key)
    # set the root directory to store upload files, and get
    # the file location
            work_path = root_path + "/" + str(self.id) +"/" +current_user;
            file_location = work_path + "/" + file_name
            with open(file_location, "wb") as handle:
                handle.write(transmit_data.data)
            lock.release_write()
            return True

    # This function is used for deleting files from server
    def delete_files(self,user_name, file_name, key):
        global lock
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
            return respond
        else:
            lock.acquire_write()
            current_user = self.security_check(user_name, key)
    # get the location of the file which will be deleted
            file_location = self.search_files(user_name, file_name, key)
            os.remove(file_location)
            lock.release_write()
            return True
    
    def run(self):
        global server
        server[self.id] = ThreadXMLRPCServer(("localhost", 8000+self.id), allow_none=True)
        print "port %d" %(self.id+8000) + " is established!"
        self.build_up(root_path)
        self.build_user_record()
        server[self.id].register_introspection_functions()
        server[self.id].register_function(self.change_password, "change_password")
        server[self.id].register_function(self.login_in, "login_in")
        server[self.id].register_function(self.list_files, "list_files")
        server[self.id].register_function(self.change_directory, "change_directory")
        server[self.id].register_function(self.search_files, "search_files")
        server[self.id].register_function(self.download_files, "download_files")
        server[self.id].register_function(self.upload_files, "upload_files")
        server[self.id].register_function(self.delete_files, "delete_files")
        server[self.id].serve_forever()
        print "port %d" %(self.id+8000) + " is established!"

lock = ReadWriteLock()

server = [1]*serverNum

masterserver = MasterServer()
masterserver.start()
svr = [1]*(serverNum)
for i in range(1, serverNum):
    svr[i] = MultiServer(i);
    svr[i].start()
