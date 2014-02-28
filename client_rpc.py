import xmlrpclib

# connect to the remote server of RPC
client = xmlrpclib.ServerProxy("http://localhost:8000/")
# this state will determine which state, 0 is initial state
state = 2;

while ( state != 5):
# call login_in function to login into the remote server
    if state == 0:
        user_name = raw_input("Please enter your username:")
        password = raw_input("Please enter your password:")
        respond = client.login_in(user_name, password)
        print "From client - " + respond
        if respond == "Login in successfully":
            state += 1

# call search_files function in the remote server
    elif state == 1:
        file_name = raw_input("Please enter the file name you want to find:")
        respond = client.search_files(file_name)
# if respond is not found, print corresponding result
        if respond == "Not found":
            print "Unable to find the corresponding file."
        else:
            print "The file is found, the location is " + respond
	    state += 1

# call download_files function in the remote server
    elif state == 2:
        path = "/Users/kokkyounominamirui/Documents/client"
        file_name = raw_input("Please enter the file name you want to download:")
# before downloading, make sure that the file exists
        respond = client.search_files(file_name)
# If the file exists, begin downloading
        if respond != "Not found":
            file_location = path + "/" + file_name
            with open(file_location, "wb") as handle:
                handle.write(client.download_files(file_name).data)
	    print "From client - Downloading file successfully"
#	    state += 1
# If the file doesn't exist, show the failure of downloading
        else:
            print "From client - Downloading Failure: the required file doesn't exist in server" 

# call upload_file function to upload files to server
    elif state == 3:
        path = "/Users/kokkyounominamirui/Desktop"
# input the file name which will be uploaded
        file_name = raw_input("Please enter the file name you want to upload:")
        file_location = path + "/" + file_name
# open the file, reand the content and send these content
        with open(file_location, "rb") as handle:
            transmit_data = xmlrpclib.Binary(handle.read())
            respond = client.upload_files(file_name, transmit_data)
# Based on the respond to output corresponding information
        if respond:
            print "From client - Uploading file successfully"
	    state += 1
        else:
            print "From client - Uploading file unsuccessfully"

# call delete_file function to delete files in the data server
    elif state == 4:
# enter the file name which will be deleted
        file_name = raw_input("Please enter the file name you want to delete:")
# make sure that the file does exist
        respond = client.search_files(file_name)
# if the file exist, delete it
        if respond != "Not found":
            if client.delete_files(file_name):
	        print "From client - Delete file successfully"
	        state += 1
# otherwise, print the error information
        else:
            print "From client - Delete file unsuccessfully, because the file doesn't exist."

