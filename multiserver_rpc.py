# This file uses RPC method to implement the communcation
# between single client and single data server
import xmlrpclib, os, random
import re,sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
import threading
import time

# This class change simplexmlrpcserver from single thread to
# multi-thread 
class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class MultiServerThread(threading.Thread):
# Initiate the server with the given port number
    def __init__(self, port):
        threading.Thread.__init__(self)
	self.multiServer = ThreadXMLRPCServer(("localhost", port), allow_none = True)	
# This dictionary is used for storing user information in data server
        self.user_record = dict()
# This dictionary is used for access key for different users
        self.key_table = dict()
# This path is only used for listing files and changing directories
        self.root_path = ""
        self.user_information = ""
# Firstly, get the home directory of the computer
        self.home_dir = os.path.expanduser("~")
        self.root_path = self.home_dir + "/" + "CloudBox"
        self.user_information = self.root_path + "/" + "User_information.txt"
# intiate related folder and user information
        self.build_up(self.root_path)
	self.build_user_record()
        self.multiServer.register_introspection_functions()
        self.multiServer.register_function(self.sign_up, "sign_up")
        self.multiServer.register_function(self.change_password, "change_password")
        self.multiServer.register_function(self.login_in, "login_in")
        self.multiServer.register_function(self.list_files, "list_files")
        self.multiServer.register_function(self.change_directory, "change_directory")
        self.multiServer.register_function(self.search_files, "search_files")
        self.multiServer.register_function(self.download_files, "download_files")
        self.multiServer.register_function(self.upload_files, "upload_files")
        self.multiServer.register_function(self.delete_files, "delete_files")
#	self.multiServer.register_function(self.exit, "exit")
# run the server
    def run(self):
        self.multiServer.serve_forever()

# This function is used for testify whether the user has the access to
# use some specific functions
    def security_check(self, user_name, key):
        self.foundmatch = False
        for key in self.key_table:
            if self.key_table[key] == user_name:
	        return user_name
        if self.foundmatch:
            self.result = "denied access"
            return self.result
     

# This function is used for server to build directories at the beginning
    def build_up(self, root_path):
# tests whether this directory exists or not, if the directory doesn't exist,
# create root directory for servers
        if not (os.path.exists(root_path)):
            os.mkdir(root_path)
# Then, based on the user_record, tests whether each user has its own directory
# or not, if not, building corresponding folders
        for self.user_name in self.user_record:
            self.user_folder = self.root_path + "/" + self.user_name;
	    if not (os.path.exists(self.user_folder)):
	        os.mkdir(self.user_folder)

# This function is used for getting user record from specific file at the beginning
    def build_user_record(self):
# firstly check that whether this user information file exist or not
        if os.path.exists(self.user_information):
            self.f = open(self.user_information, 'r')
        else:
	    self.f = open(self.user_information, 'w+')
	    self.f.close()
	    self.f = open(self.user_information, 'r')
# Each line in the file store the information of a user, therefore we read a line
# each time
        self.content = self.f.readline()
        while (self.content):
            self.content_buffer = re.split('\W+', self.content)
	    for self.index in range(0, len(self.content_buffer)-1):
	        if ( self.index > 0 ) and ( self.content_buffer[self.index-1] == "Username"):
	            self.user_name = self.content_buffer[self.index]
	        if ( self.index > 0 ) and ( self.content_buffer[self.index-1] == "Password"):
	            self.password = self.content_buffer[self.index]
	            self.user_record[self.user_name] = self.password
	    self.content = self.f.readline()
	self.f.close()  
    #print user_record 

# This function is used for signing up into the data server
    def sign_up(self, user_name, password):
# Firstly make sure that the user_name doesn't exist
        if user_name in self.user_record:
            self.respond = "Error: This username has been used."
	    return self.respond
        else:
            self.initial_password = str(password)
# add the user_name and initial password into user_record
            self.user_record[user_name] = self.initial_password	
	    self.respond = "Sign up successfully!"
            self.f = open(self.user_information, 'a')
	    self.content = "Username: " + user_name + "    " + "Password: " + self.initial_password + '\n'
	    self.f.write(self.content)
	    self.f.close()
# build new directory file for new users
	    self.new_dir = self.root_path + "/" + user_name
	    os.mkdir(self.new_dir)
	    return self.respond

# This function is used for changing the password for clients
# The client has to provide original password, and new password
    def change_password(self, user_name, original_password, new_password):
# Firstly, make sure that the user_name in the record:
        if user_name in self.user_record:
# If original password matches, change the password
            if original_password == self.user_record[user_name]:
	        self.user_record[user_name] = new_password
	        self.respond = "Change password successfully"
# update the change of password in user information file
	        self.f = open(self.user_information, 'r')
	        self.lines = self.f.readlines()
	        self.f.close()
	        self.f = open(self.user_information, 'w')
	        for self.line in self.lines:
	            self.con_buffer = re.split('\W+', self.line)
		    if self.con_buffer[1] != user_name:
		        self.f.write(self.line)
	            else:
		        self.new_line = "Username: " + user_name + "    " + "Password: " + new_password + '\n'
		        self.f.write(self.new_line)
	        self.f.close()
	        return self.respond
	    else:
	        self.respond = "The original password is wrong"
	        return self.respond
        else:
            self.respond = "The username doesn't exist"
	    return self.respond

# This function is used for logining into the date server
    def login_in(self, user_name, password):
# Firstly, make sure that there is user_name in the record
        if user_name in self.user_record.keys():
# Then check whether the password corresponds or not
            if password == self.user_record[user_name]:
	        self.access_key = random.randint(0, 10000000)
	        self.access_key = str(self.access_key)
	        self.key_table[self.access_key] = user_name
	        self.respond = "Login in successfully#" + self.access_key
	        self.current_user = user_name
	    #print key_table
	        return self.respond
	    else:
                self.respond = "The password doesn't match with the given username"
                return self.respond
        else:
            self.respond = "The username doesn't exist"
            return self.respond	

# This function is used for listing files in the data servers

    def list_files(self, user_name, rel_path, key):
        if self.security_check(user_name, key) == "denied access":
	    self.respond = "You have no right to use this function"
	    return self.respond
        else:
	    self.current_user = self.security_check(user_name, key)
        self.work_path = self.root_path + "/" + self.current_user + "/" + rel_path
        self.file_list = os.listdir(self.work_path)
        return self.file_list

# This function is used for change directories in the data server
    def change_directory(self, user_name, rel_path, key):
        if self.security_check(user_name, key) == "denied access":
	    self.respond = "You have no right to use this function"
	    return self.respond
        else:
	    self.current_user = self.security_check(user_name, key)
# get the work path from the information sent by client
        self.work_path = self.root_path + "/" + self.current_user + rel_path
# Firstly, check if that this path exist or not
        if os.path.exists(self.work_path):
# Then make sure that is directory
            if os.path.isdir(self.work_path):
                self.respond = "cd successfully"
	        return self.respond	
            else:
	        self.respond = "From Server: This is not a directory!"		
	        return self.respond
        else:
	    self.respond = "From Server: This directory doesn't exist!"
            return self.respond

# This function is used for search files in the file system
# of data server, if there is required file, return True,
# otherwise return false
    def search_files(self, user_name, file_name, key):
        if self.security_check(user_name, key) == "denied access":
	    self.respond = "You have no right to use this function"
	    return self.respond
        else:
	    self.current_user = self.security_check(user_name, key)
# set the path of root directory, and found flag to be false
            self.work_path = self.root_path + "/" + self.current_user
            self.foundmatch = False
# With the use of os.walk, go through all files in file system
            for self.root, self.dirs, self.files in os.walk(self.work_path):
# If file found, set found flag, and get the location of file
                if file_name in self.files:
	            self.file_location = os.path.join(self.root, file_name)
	            self.foundmatch = True
	            break
# If flag is true, found file and return the location
            if self.foundmatch:
                self.respond = self.file_location
	        return self.respond
# If flag is false, return false information
            else:
                self.respond = "Not found"
	        return self.respond

# This function is used for downloading files to client
    def download_files(self, user_name, file_name, key):
        if self.security_check(user_name, key) == "denied access":
	    self.respond = "You have no right to use this function"
	    return self.respond
        else:
	    self.current_user =  self.security_check(user_name, key)
# set the path root directory, and found flag to be false
            self.work_path = self.root_path + "/" + self.current_user
# get the file location of give file
            self.file_location = self.search_files(user_name, file_name, key)
            print "From server - The download file locates at " + self.file_location
            with open(self.file_location, "rb") as handle:
                return xmlrpclib.Binary(handle.read())

# This function is used for uploading files from client
    def upload_files(self, user_name,file_name, transmit_data, key):
        if self.security_check(user_name, key) == "denied access":
	    self.respond = "You have no right to use this function"
	    return self.respond
        else:
	    self.current_user = self.security_check(user_name, key)
# set the root directory to store upload files, and get
# the file location
            self.work_path = self.root_path + "/" + self.current_user;
            self.file_location = self.work_path + "/" + file_name
            with open(self.file_location, "wb") as handle:
                handle.write(transmit_data.data)
            return True

# This function is used for deleting files from server
    def delete_files(self, user_name, file_name, key):
        if self.security_check(user_name, key) == "denied access":
	    self.respond = "You have no right to use this function"
	    return self.respond
        else:
	    self.current_user = self.security_check(user_name, key)
# get the location of the file which will be deleted
            self.file_location = self.search_files(user_name, file_name, key)
            os.remove(self.file_location)
            return True	

#    def exit(self):
#        sys.exit(0)


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

lock = ReadWriteLock()
#server_object = Server()
#server = ThreadXMLRPCServer(("localhost", 8000), allow_none=True)
#build_up(root_path)
#build_user_record()
server = MultiServerThread(8000)
server.start()
