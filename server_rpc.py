# This file uses RPC method to implement the communcation
# between single client and single data server
import xmlrpclib, os, random
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

# This dictionary is used for storing user information in data server
user_record = dict([('rx37','xurui1006'),('zc','1234567')])
# This path is only used for listing files and changing directories
global current_path
global parent_path
current_path  = "/Users/kokkyounominamirui/Desktop"
parent_path  = "/Users/kokkyounominamirui"

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
    file_list = os.listdir(current_path)
    return file_list

# This function is used for change directories in the data server
def change_directory(dir_name):
    global current_path
    global parent_path
# If the dir_name is .., it means that it will return to the parent directory
    if dir_name == "..":
        current_path = parent_path
	parent_path = os.path.abspath(os.path.join(current_path, os.path.pardir))
	respond = "cd successfully"
	return respond 
# otherwise change to other directories
    else:
# make sure that is under the current directory
        if dir_name in os.listdir(current_path):
# Then make sure that is directory
	    current_path = current_path + "/" + dir_name
	    if os.path.isdir(current_path):
	        parent_path = os.path.abspath(os.path.join(current_path, os.path.pardir))
	        respond = "cd successfully"
	        return respond	
	    else:
		current_path = parent_path
	        parent_path = os.path.abspath(os.path.join(current_path, os.path.pardir))
	        respond = "From Server: This is not a directory!"		
		return respond
	else:
	    respond = "From Server - Error: The directory doesn't exist."
            return respond

# This function is used for search files in the file system
# of data server, if there is required file, return True,
# otherwise return false
def search_files(file_name):
# set the path of root directory, and found flag to be false
    path = "/Users/kokkyounominamirui/Desktop"
    foundmatch = False
# With the use of os.walk, go through all files in file system
    for root, dirs, files in os.walk(path):
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
    path = "/Users/kokkyounominamirui/Desktop"
# get the file location of give file
    file_location = search_files(file_name)
    print "From server - The download file locates at " + file_location
    with open(file_location, "rb") as handle:
        return xmlrpclib.Binary(handle.read())

# This function is used for uploading files from client
def upload_files(file_name, transmit_data):
# set the root directory to store upload files, and get
# the file location
    path = "/Users/kokkyounominamirui/Desktop/server"
    file_location = path + "/" + file_name
    with open(file_location, "wb") as handle:
        handle.write(transmit_data.data)
    return True

# This function is used for deleting files from server
def delete_files(file_name):
# get the location of the file which will be deleted
    file_location = search_files(file_name)
    os.remove(file_location)
    return True	

server = SimpleXMLRPCServer(("localhost", 8000))
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
