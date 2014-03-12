# This file uses RPC method to implement the communcation
# between single client and single data server
import xmlrpclib, os, random
import re
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
import threading
import time


class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

# This dictionary is used for storing user information in data server
user_record = dict()
# This path is only used for listing files and changing directories
global root_path
global user_information
global current_user
# Firstly, get the home directory of the computer
home_dir = os.path.expanduser("~")
root_path = home_dir + "/" + "CloudBox"
user_information = root_path + "/" + "User_information.txt"

# This function is used for server to build directories at the beginning
def build_up(root_path):
# tests whether this directory exists or not, if the directory doesn't exist,
# create root directory for servers
    if not (os.path.exists(root_path)):
        os.mkdir(root_path)
# Then, based on the user_record, tests whether each user has its own directory
# or not, if not, building corresponding folders
    for user_name in user_record:
        user_folder = root_path + "/" + user_name;
	if not (os.path.exists(user_folder)):
	    os.mkdir(user_folder)

# This function is used for getting user record from specific file at the beginning
def build_user_record():
# firstly check that whether this user information file exist or not
    if os.path.exists(user_information):
        f = open(user_information, 'r')
    else:
	f = open(user_information, 'w+')
	f.close()
	f = open(user_information, 'r')
# Each line in the file store the information of a user, therefore we read a line
# each time
    content = f.readline()
    while (content):
        content_buffer = re.split('\W+', content)
	for index in range(0, len(content_buffer)-1):
	    if ( index > 0 ) and ( content_buffer[index-1] == "Username"):
	        user_name = content_buffer[index]
	    if ( index > 0 ) and ( content_buffer[index-1] == "Password"):
	        password = content_buffer[index]
	        user_record[user_name] = password
	content = f.readline()
    print user_record 

# This function is used for signing up into the data server
def sign_up(user_name, password):
# Firstly make sure that the user_name doesn't exist
    if user_name in user_record:
        respond = "Error: This username has been used."
	return respond
    else:
        initial_password = str(password)
# add the user_name and initial password into user_record
        user_record[user_name] = initial_password	
	respond = "Sign up successfully!"
	f = open(user_information, 'a')
	content = "Username: " + user_name + "    " + "Password: " + initial_password + '\n'
	f.write(content)
# build new directory file for new users
	new_dir = root_path + "/" + user_name
	os.mkdir(new_dir)
	return respond

# This function is used for changing the password for clients
# The client has to provide original password, and new password
def change_password(user_name, original_password, new_password):
# Firstly, make sure that the user_name in the record:
    if user_name in user_record:
# If original password matches, change the password
        if original_password == user_record[user_name]:
	    user_record[user_name] = new_password
	    respond = "Change password successfully"
# update the change of password in user information file
	    f = open(user_information, 'r')
	    lines = f.readlines()
	    f.close()
	    f = open(user_information, 'w')
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
def login_in(user_name, password):
    global current_user 
# Firstly, make sure that there is user_name in the record
    if user_name in user_record.keys():
# Then check whether the password corresponds or not
        if password == user_record[user_name]:
	    respond = "Login in successfully"
	    current_user = user_name
	    return respond
	else:
            respond = "The password doesn't match with the given username"
            return respond
    else:
        respond = "The username doesn't exist"
        return respond	

# This function is used for listing files in the data servers

def list_files(rel_path):
    work_path = root_path + "/" + current_user + "/" + rel_path
    file_list = os.listdir(work_path)
    return file_list

# This function is used for change directories in the data server
def change_directory(rel_path):
# get the work path from the information sent by client
    work_path = root_path + "/" + current_user + rel_path
# Firstly, check if that this path exist or not
    if os.path.exists(work_path):
# Then make sure that is directory
        if os.path.isdir(work_path):
            respond = "cd successfully"
	    return respond	
        else:
	    respond = "From Server: This is not a directory!"		
	    return respond
    else:
	 respond = "From Server: This directory doesn't exist!"
         return respond

# This function is used for search files in the file system
# of data server, if there is required file, return True,
# otherwise return false
def search_files(file_name):
# set the path of root directory, and found flag to be false
    work_path = root_path + "/" + current_user
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
	return respond
# If flag is false, return false information
    else:
        respond = "Not found"
	return respond

# This function is used for downloading files to client
def download_files(file_name):
# set the path root directory, and found flag to be false
    work_path = root_path + "/" + current_user
# get the file location of give file
    file_location = search_files(file_name)
    print "From server - The download file locates at " + file_location
    with open(file_location, "rb") as handle:
        return xmlrpclib.Binary(handle.read())

# This function is used for uploading files from client
def upload_files(file_name, transmit_data):
# set the root directory to store upload files, and get
# the file location
    work_path = root_path + "/" + current_user;
    file_location = work_path + "/" + file_name
    with open(file_location, "wb") as handle:
        handle.write(transmit_data.data)
    return True

# This function is used for deleting files from server
def delete_files(file_name):
# get the location of the file which will be deleted
    file_location = search_files(file_name)
    os.remove(file_location)
    return True	



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
server = ThreadXMLRPCServer(("localhost", 8000), allow_none=True)
build_up(root_path)
build_user_record()
server.register_introspection_functions()
server.register_function(sign_up, "sign_up")
server.register_function(change_password, "change_password")
server.register_function(login_in, "login_in")
server.register_function(list_files, "list_files")
server.register_function(change_directory, "change_directory")
server.register_function(search_files, "search_files")
server.register_function(download_files, "download_files")
server.register_function(upload_files, "upload_files")
server.register_function(delete_files, "delete_files")
server.serve_forever()
