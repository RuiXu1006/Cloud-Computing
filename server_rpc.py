# This file uses RPC method to implement the communcation
# between single client and single data server
import xmlrpclib, os
from SimpleXMLRPCServer import SimpleXMLRPCServer

# This function is used for logining into the date server
def login_in(user_name, password):
    user_record = dict([('rx37','xurui1006'),('zc','1234567')])
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
server.register_function(login_in, "login_in")
server.register_function(search_files, "search_files")
server.register_function(download_files, "download_files")
server.register_function(upload_files, "upload_files")
server.register_function(delete_files, "delete_files")
server.serve_forever()
