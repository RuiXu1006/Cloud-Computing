# This file uses RPC method to implement the communcation
# between single client and single data server
import xmlrpclib, os, random
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
import threading
import time

id = 1;
class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass
    self.id = id;
    id++;

# This dictionary is used for storing user information in data server
user_record = dict([('rx37','xurui1006'),('zc','1234567')])
# This path is only used for listing files and changing directories
global current_path
global parent_path
current_path  = "/Users/Zachary/Desktop/unixtest"
parent_path  = "/Users/Zachary/Desktop"
global lock

# This function is used for signing up into the data server
def sign_up(user_name):
# Firstly make sure that the user_name doesn't exist
    if user_name in user_record:
        respond = "Error: This username has been used."
	return respond
    else:
        initial_password = random.randint(1, 1000000)
        initial_password = str(initial_password)
# add the user_name and initial password into user_record
        user_record[user_name] = initial_password
	respond = initial_password
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
	    return respond
	else:
	    respond = "The original password is wrong"
	    return respond
    else:
        respond = "The username doesn't exist"
	return respond

# This function is used for logining into the date server
def login_in(user_name, password):
# Firstly, make sure that there is user_name in the record
    if user_name in user_record.keys():
# Then check whether the password corresponds or not
        if password == user_record[user_name]:
	    respond = "Login in successfully"
	    return respond
	else:
            respond = "The password doesn't match with the given username"
            return respond
    else:
        respond = "The username doesn't exist"
        return respond	

# This function is used for listing files in the data servers
def list_files():
    global lock
    lock.acquire_read()
    time.sleep(5)
    file_list = os.listdir(current_path)
    lock.release_read()
    return file_list

# This function is used for change directories in the data server
def change_directory(dir_name):
    global lock
    global current_path
    global parent_path
    lock.acquire_read()
# If the dir_name is .., it means that it will return to the parent directory
    if dir_name == "..":
        current_path = parent_path
	parent_path = os.path.abspath(os.path.join(current_path, os.path.pardir))
	respond = "cd successfully"
# otherwise change to other directories
    else:
# make sure that is under the current directory
        if dir_name in os.listdir(current_path):        #! if is not in use
# Then make sure that is directory
	    current_path = current_path + "/" + dir_name    #! indentation problem
	    if os.path.isdir(current_path):
	        parent_path = os.path.abspath(os.path.join(current_path, os.path.pardir))
	        respond = "cd successfully"
	    else:
		current_path = parent_path              #! indetation
	        parent_path = os.path.abspath(os.path.join(current_path, os.path.pardir))
	        respond = "From Server: This is not a directory!"		
	else:
	    respond = "From Server - Error: The directory doesn't exist."
    lock.release_read()
    return respond

# This function is used for search files in the file system
# of data server, if there is required file, return True,
# otherwise return false
def search_files(file_name):
    global lock
    lock.acquire_read()
# set the path of root directory, and found flag to be false
    path = "/Users/Zachary/Desktop/unixtest"
    foundmatch = False
# With the use of os.walk, go through all files in file system
    for root, dirs, files in os.walk(path):
# If file found, set found flag, and get the location of file
        if file_name in files:
	    file_location = os.path.join(root, file_name)
	    foundmatch = True
	    break
    
    respond = "Not found"
# If flag is true, found file and return the location
    if foundmatch:
        respond = file_location
	lock.release_read()
    return respond

# This function is used for downloading files to client
def download_files(file_name):
    global lock
    lock.acquire_read()
# set the path root directory, and found flag to be false
    path = "/Users/Zachary/Desktop/unixtest"
# get the file location of give file
    file_location = search_files(file_name)
    print "From server - The download file locates at " + file_location + "haha"
    time.sleep(5)
    with open(file_location, "rb") as handle:
        res = xmlrpclib.Binary(handle.read())
        lock.release_read()
        return res

# This function is used for uploading files from client
def upload_files(file_name, transmit_data):
# set the root directory to store upload files, and get
# the file location
    lock.acquire_write()
    path = "/Users/Zachary/Desktop/server"
    file_location = path + "/" + file_name
    with open(file_location, "wb") as handle:
        handle.write(transmit_data.data)
    lock.release_write()
    return True

# This function is used for deleting files from server
def delete_files(file_name):
# get the location of the file which will be deleted
    lock.acquire_write()
    file_location = search_files(file_name)
    os.remove(file_location)
    lock.release_write()
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
#server.register_instance(server_object)
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
#server.register_multicall_functions()
server.serve_forever()
