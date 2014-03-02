import xmlrpclib

# connect to the remote server of RPC
client = xmlrpclib.ServerProxy("http://localhost:8000/")
print "The following are available methods on data server"
print client.system.listMethods()

while True:
        # Ask clients to select which function will be used
    function = raw_input("Please enter the function name you want:")
    # Based on the input function, set state parameter to corresponding value
    if function == "login_in":
        state = 0
    elif function == "search_files":
        state = 1
    elif function == "download_files":
        state = 2
    elif function == "upload_files":
        state = 3
    elif function == "delete_files":
        state = 4
    elif function == "sign_up":
        state = 5
    elif function == "change_password":
        state = 6
    elif function == "list_files":
        state = 7
    elif function == "change_directory":
        state = 8
    else:
        state = 9

# call login_in function to login into the remote server
    if state == 0:
        user_name = raw_input("Please enter your username:")
        password = raw_input("Please enter your password:")
        respond = client.login_in(user_name, password)
        print "From client - " + respond

# call search_files function in the remote server
    elif state == 1:
        file_name = raw_input("Please enter the file name you want to find:")
        respond = client.search_files(file_name)
# if respond is not found, print corresponding result
        if respond == "Not found":
            print "Unable to find the corresponding file."
        else:
            print "The file is found, the location is " + respond

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
# otherwise, print the error information
        else:
            print "From client - Delete file unsuccessfully, because the file doesn't exist."

# call sign_up function to sign up in the data server
    elif state == 5:
        while True:
            user_name = raw_input("Please enter the username you want:")
	    initial_password = client.sign_up(user_name)
	    if initial_password != "Error: This username has been used.":
	        break
	    else:
	        print "From Server - Error: This username has been used"
	print "From Server: Your initial password is " + initial_password
	print "From Client - Sign up successfully"

# call change_password function to change password
    elif state == 6:
        while True:
	    user_name = raw_input("Please enter your username:")
	    original_password = raw_input("Please enter your original password:")
	    new_password = raw_input("Please enter your new password:")
	    respond = client.change_password(user_name, original_password, new_password)
	    if respond == "Change password successfully":
	        print "From Server - " + respond
		break
	    elif respond == "The original password is wrong":
	        print "From Server - Error: " + respond
	    else:
	        print "From Server - Error: " + respond

# call list_files function to get the list of files under current directory
    elif state == 7:
        file_list = client.list_files()
	for files in file_list:
	    print files

# call change_directory function
    elif state == 8:
        dir_name = raw_input("Change directory to: ")
	respond = client.change_directory(dir_name)
	print respond

# if the function is unrecognized, print Error information
    else:
        print "From client - Unrecognized function, please enter again!"

