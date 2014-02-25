# This file is act as simulating servers to test the functionality of client program

import socket
import os

#This function is used for searching files in the file system
def search_files(file_name, path):
    tar_Files = os.listdir(path)
    Found = False
    for file in tar_Files:
        if file == file_name:
	   Found = True
	   break
    if Found == True:
        return True
    else:
        return False

# This function will return the path of required file
def locate_files(file_name, path):
    if search_files(file_name, path):
        location = path + "/" + file_name
	return location
    else:
	print "From Server - Error: The requested file doesn't exist"

# This function will send requested files to clients, then
# open the file, read the content and send to the clients
def sendfiles(socket, location):
    send_file = open(location, 'rb')
    content = send_file.read()
    socket.sendall(data)

# This directory is used for storing username and password
user_record = dict([('rx','xurui1006'),('zc','1234567')])

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = socket.gethostname()
port = 12345
serversocket.bind((host, port))

serversocket.listen(5)
print 'Setting up the server'
while True:
    conn, addr = serversocket.accept()
    print "Welcome to data server"
    data = conn.recv(1024)
    i = 0
    while (len(data)>0):
	processing_block = False
        print "From server  # %d " % (i) + data
# If the data shows that the new connection has been built, reply to clients
	if data == "Requests for building connection":
	    processing_block = True
	    conn.send("ACK of the request for building connection")
            if conn.recv(1024) == "ACK of the reply from servers":
	        conn.send("Connection Built")
	    processing_block = False
		
# If the request is for logining in, ask for username and password
	elif data == "Requests for permission of operation":
	    processing_block = True
	    print "From server - Please enter your username"
	    conn.send("Please enter your username")
	    username = conn.recv(1024)
	    print "From server - Please enter your password"
	    conn.send("Please enter your password")
	    password = conn.recv(1024)
# If the username exists, and match with password login in successfully
            if username in user_record.keys():
	        if password == user_record[username]:
		    conn.send("Login in successfully")
		else:
		    conn.send("Password doesn't match with username")
	    else:
		conn.send("The username doesn't exist")
	    processing_block = False

# If the request is for searching files, asking for file name
	elif data == "Requests for searching files":
	    processing_block = True
	    conn.send("What's file name you want")
	    file_name = conn.recv(1024)
	    path = "/Users/kokkyounominamirui/Desktop"
	    print "From server - The required file is " + file_name
	    if search_files(file_name, path):
	        print "From server - The required file exists in the file system"
		conn.send("Found")
	    else:
		print "From server - Error: The required file doesn't exist"
		conn.send("Not Found")
	    processing_block = False

# If the request is for downloading files
	elif data == "Requests for downloading files":
	    processing_block = True
	    conn.send("What's file name you want")
	    file_name = conn.recv(1024)
	    path = "/Users/kokkyounominamirui/Desktop"
# After receiving the file name, then make sure the file does exist, and return location 
# Then transmitt the file to clients
	    if search_files(file_name, path):
		print "From Server - Found the file"
	        conn.send("The requested file exists")
		location = locate_files(file_name, path)
		conn.send(location)
# After getting the request for transmitting files, begin transmitting
		respond = conn.recv(1024)
		if respond == "Please send file":
		    f = open(location, "rb")
		    content = f.read(1024)
	            conn.send(content)
	            while (content):
			content = f.readline()
			conn.send(content)
		    conn.send("###")
	    else:
                conn.send("The requested file doens't exist")
            processing_block = False

	if processing_block == False:	
	    data = conn.recv(1024)
	i = i + 1
conn.close() 
