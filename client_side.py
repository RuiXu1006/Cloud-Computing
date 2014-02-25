# This file is used for the communication of clients with servers

import socket
import time
import os

# Define the class of user clients
class user_client:
# Initialize the parameters of user clients
    def __init__(self,socket):
        self.communication_counter = 0                                     # This parameter is used for recording times of communication with servers
        self.data_download = 0                                             # This parameter is used for data downloaded from servers ( in bytes )
	self.data_upload = 0                                               # This parameter is used for data uploaded to servers ( in bytes )                  
        self.socket = socket
	self.handle()

# This function is used for building the user directory, which
# is used for storing downloading files
def create_client_dir(path):
    dir_name = raw_input("Please enter the client directory file you want:")
    dir_name = path + dir_name
# tests whether this directory exists or not
    if not (os.path.exists(dir_name)):
        os.mkdir(dir_name)
        return dir_name	
    return dir_name

# This function is used for building connection with servers
def build_connection(socket):
# Firstly sending the request for connecting
    send_messages(socket, 1)
# If server feed back with ACK, reply with ACK. Otherwise, report error
    if socket.recv(1024) == "ACK of the request for building connection":
        socket.send("ACK of the reply from servers")
    else:
        print "From client - Error: Uable to get the reply of servers"
# If the connection build successfully, return true.
    if socket.recv(1024) == "Connection Built":
        return True
    else:
        return False

# This function is used for loginning into the data servers
def login_in(socket):
    send_messages(socket, 2)
# sending username and password
    if socket.recv(1024) == "Please enter your username":
        username = raw_input()
        socket.send(username)
    if socket.recv(1024) == "Please enter your password":
        password = raw_input()	
        socket.send(password)
# print the message from data server
    print "From server - " + socket.recv(1024)

# This function is used for searching files in the data server
# If there is one, the server will return the location
def search_files(socket):
    send_messages(socket, 3)
    if socket.recv(1024) == "What's file name you want":
	file_name = raw_input("Please enter the name of file you want:")
        socket.send(file_name)
# If the required file is found, return True. Otherwise, return False
	if socket.recv(1024) == "Found":
            return True
        else:
            return False	

# This function is used for downloading files from data servers
# Firstly, make sure the file exits, then downloading the file
def download_files(socket, working_directory):
    send_en = False
# Firstly, sending requests for downloading and notify servers  
    send_messages(socket, 4)
    if socket.recv(1024) == "What's file name you want":
        file_name = raw_input("Please enter the name of file you want:")
	socket.send(file_name)
# if the server that the requested files exist, get the location of file
	respond = socket.recv(1024)
	if respond == "The requested file exists":
	    location = socket.recv(1024)
	    print "The file is located at " + location
	    send_en = True
	elif respond != "The requested file exists":
	    print "From Server - Error:The requested file doesn't exist"
# If send_en flag is true, begin transmitting files
    if send_en:
        socket.send("Please send file")
	file_name = working_directory + "/" + file_name
	f = open(file_name, "wb")
	content = socket.recv(1024)
#	print content
	while (content):
	    f.write(content)
            content = socket.recv(1024)
            if content == "###":
                break;
#	    print content	

# This function is used for sending requests to servers, option
# represents different kinds of requests
def send_messages(socket, options):
# option 1 is used for establishing connection with server
    if ( options == 1 ):
        socket.send("Requests for building connection")
# option 2 is used for logining into the data servers
    elif ( options == 2 ):
	socket.send("Requests for permission of operation")
# option 2 is used for searching whether the required file in the server
    elif ( options == 3 ):
        socket.send("Requests for searching files")
# option 3 is used for asking for location of required file
    elif ( options == 4 ):
	socket.send("Requests for downloading files")

# Firstly, set up the working directory for clients
src_path = "/Users/kokkyounominamirui/Desktop"
working_dir = create_client_dir(src_path)
print working_dir
if working_dir != "":
    print "From client - Has built the working directory for the client"
else:
    print "From client - Error: Unable to build the working directory"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 12345

s.connect((host, port))
if build_connection(s):
    print "From client - The connection between client and data server has been built."
else:
    print "From client - Fatal: Unable to connect with data server"

#login_in(s)
#if search_files(s):
#    print "From client - The requested file exists in the data server, and data server has send the location"
#else:
#    print "From client - Fatal: Cannot find the requested file in the data server"

download_files(s, working_dir)
#s.close()
