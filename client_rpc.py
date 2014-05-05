import xmlrpclib
import os
import random

# Get the home directory
home_dir = os.path.expanduser("~")
# When setting up the client, build corresponding files
root_path = home_dir + "/" + "LocalBox" 
if not (os.path.exists(root_path)):
    os.mkdir(root_path)

# find which server to put data


# the IPAddress of MasterServers
IPAddr = "localhost"

# the total number of server
svrNum = 9

# connect to the remote server of RPC
# this is connect to the master server to determine which server to serve
"""
client = xmlrpclib.ServerProxy("http://localhost:8000/")
print "The following are available methods on data server"
print client.system.listMethods()
"""
global client
#global user_name
global work_path
global rel_path
global work_key
user_name = ""
svr_list = []
print "Note: At the beginning, you should login in firstly!"


# this function is used for random select from master server
def select_master():
    ret = "http://" + IPAddr+ ":" + str(8000+random.randint(0,1)*100) +"/"
    return ret

# This function is used for selecting data server from clients side
def select_dserver():
    svr_list = []
    if (os.path.exists(root_path + "/" +user_name + "/svrName.txt")):
        print "From client - Local record exists"
        f = open(root_path + "/" + user_name + "/svrName.txt", 'r')
        # Store all valid data server names in the list
        svrName = f.readline()
        while (svrName):
            svrName = svrName.rstrip('\n')
            print svrName
            # check whether the server port is correct or not
            # if (int(svrName) <= 8000) or (int(svrName) > (8000 + svrNum)):
#                 print "This server name is not valid"
#             else:
#                 svr_list.append(svrName)
            svr_list.append(svrName)
            svrName = f.readline()
        if len(svr_list) != 0:
            local_found = True
        else:
            return 0;
    else:
        local_found = False

    # if there are valid data server in the list, random selects among them
    if local_found:
        #print svr_list
        svr_index = random.randint(0, 100000000)
        svr_index = svr_index % len(svr_list)
        #print svr_index
        svrName = svr_list[svr_index]
        print "The selected data serve is " + str(svrName)
        return svrName
    else:
        return 0;
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
    elif function == "log_out":
        state = 9
    elif function == "share_file":
        state = 10
    elif function == "list_shared":
        state = 11
    elif function == "download_shared":
        state = 12
    elif function == "fork_shared":
        state = 13
    else:
        state = 14

# call login_in function to login into the remote server
    if state == 0:    
        user_name = raw_input("Please enter your username:")
        password = raw_input("Please enter your password:")
        svrName = 0
        local_found = False
        client = xmlrpclib.ServerProxy(select_master())
        svrName = select_dserver()
        # if not found effective server port in local file, ask for master server
        if svrName == 0:
            respond, svr_list = client.query_server(user_name)
            print respond
            print svr_list
            print "Get the list from master-server"
            if respond == "Found":
                f = open(root_path+"/"+user_name+"/svrName.txt", 'w+')
                for index in range(0, len(svr_list)):
                    content = str(svr_list[index])
                    f.write(content + "\n")
                f.close()
            svrName = select_dserver()

        # If unable to connect with data server, the client will ask the master server
        # to update avaible data server list, and re-login again
        try:
            #print "HHHHH" + str(svrName)
            client = xmlrpclib.ServerProxy(str(svrName))
            #print user_name + " || "+ password
            respond, svrName = client.login_in(user_name, password)
            #svrName = "http://" + IPAddr + ":" + str(svrName) + "/"
            #print respond, svrName
            respond_buffer = respond.split('#')
            respond = respond_buffer[0]
            print svrName
            print "From client - " + respond
            # if login in successfully, building sub-folders for this user in
            # the local folder
            if respond == "Login in successfully":
                rel_path = ""
                work_key = respond_buffer[1]
                print "From client - the key is " + work_key
                user_folder = root_path + "/" + user_name
                if not (os.path.exists(user_folder)):
                    os.mkdir(user_folder)
                #f = open(root_path+"/"+user_name+"/svrName.txt", 'w')
                #f.write(str(svrName))
                #f.close()
                work_path = user_folder
        except:
            print "Unable to connect with data server"
            # Then client asks master servers to update current available data server list
            client = xmlrpclib.ServerProxy(select_master())
            respond, svr_list = client.update_dsvr(user_name)
            print svr_list
            # Then update local available data server list
            f = open(root_path+"/"+user_name+"/svrName.txt", 'w')
            for index in range(0, len(svr_list)):
                content = svr_list[index]
                f.write(str(content) + "\n")
            f.close()
            # Then login in again
            svrName = select_dserver()
            client = xmlrpclib.ServerProxy(str(svrName))
            respond, svrName = client.login_in(user_name, password)
            #svrName = "http://" + IPAddr + ":" + str(svrName) + "/"
            print respond, svrName
            respond_buffer = respond.split('#')
            respond = respond_buffer[0]
            print svrName
            print "From client - " + respond
            # if login in successfully, building sub-folders for this user in
            # the local folder
            if respond == "Login in successfully":
                rel_path = ""
                work_key = respond_buffer[1]
                print "From client - the key is " + work_key
                user_folder = root_path + "/" + user_name
                if not (os.path.exists(user_folder)):
                    os.mkdir(user_folder)
                work_path = user_folder

# call search_files function in the remote server
    elif state == 1:
        try:
            file_name = raw_input("Please enter the file name you want to find:")
            respond = client.search_files(user_name,file_name,work_key)
            # if respond is not found, print corresponding result
            if respond == "Not found":
                print "Unable to find the corresponding file."
            else:
                print "The file is found, the location is " + respond
        except:
            print "There are some errors when searching files in the data server!"

# call download_files function in the remote server
    elif state == 2:
        try:
            file_name = raw_input("Please enter the file name you want to download:")
            # before downloading, make sure that the file exists
            respond = client.search_files(user_name, file_name, work_key)
            # If the file exists, begin downloading
            if respond != "Not found":
                file_location = work_path + "/" + file_name
                with open(file_location, "wb") as handle:
                    handle.write(client.download_files(user_name,file_name,work_key).data)
                    print "From client - Downloading file successfully"
            # If the file doesn't exist, show the failure of downloading
            else:
                print "From client - Downloading Failure: the required file doesn't exist in server" 
        except:
            print "There are some errors when downloading files from the data server!"

# call upload_file function to upload files to server
    elif state == 3:
        try:
            # input the file name which will be uploaded
            file_name = raw_input("Please enter the file name you want to upload:")
            file_location = work_path + "/" + file_name
            #firstly need to make sure that the file uploaded does exist
            if os.path.exists(file_location):
                # open the file, reand the content and send these content
                with open(file_location, "rb") as handle:
                    transmit_data = xmlrpclib.Binary(handle.read())
                    respond = client.upload_files(user_name,file_name,transmit_data,work_key)
                # Based on the respond to output corresponding information
                if respond:
                    print "From client - Uploading file successfully"
                else:
                    print "From client - Uploading file unsuccessfully"
            else:
                print "From client - Error: The uploaded file doesn't exist"
        except:
            print "There are some errors when uploading files to the data server"

# call delete_file function to delete files in the data server
    elif state == 4:
        try:
            # enter the file name which will be deleted
            file_name = raw_input("Please enter the file name you want to delete:")
            # make sure that the file does exist
            respond = client.search_files(user_name,file_name,work_key)
            # if the file exist, delete it
            if respond != "Not found":
                if client.delete_files(user_name,file_name,work_key):
                    print "From client - Delete file successfully"
            # otherwise, print the error information
            else:
                print "From client - Delete file unsuccessfully, because the file doesn't exist."
        except:
            print "There are some errors when deleting files in the data server"

# call sign_up function to sign up in the data server
    elif state == 5:
        try:
            client = xmlrpclib.ServerProxy(select_master())        
            randNum = random.randint(1,svrNum-1)
#         print "the randnum is" + str(randNum)
#         client = xmlrpclib.ServerProxy("http://localhost:800"+str(randNum)+"/")

            while True:
                user_name = raw_input("Please enter the username you want:")
                password  = raw_input("Please enter the password you want:")
                initial_password, svr_list = client.sign_up(user_name, password)
                print initial_password
                print svr_list
                if initial_password != "Error: This username has been used.":
                    # build local folder for new user
                    new_dir = root_path + "/" + user_name;
                    if not (os.path.exists(new_dir)):
                        os.mkdir(new_dir)
                    f = open(root_path+"/"+user_name+"/svrName.txt", 'w')
                    for index in range(0, len(svr_list)):
                        content = str(svr_list[index])
                        f.write(content + "\n")
                    f.close()
                    break
                else:
                    print "From Server - Error: This username has been used"
            print "From Server: Your initial password is " + initial_password
            print "From Client - Sign up successfully"
        except:
            print "There are some errors when signing up"

# call change_password function to change password
    elif state == 6:
        try:
            user_name = raw_input("Please enter your username:")
            original_password = raw_input("Please enter your original password:")
            new_password = raw_input("Please enter your new password:")
            respond = client.change_password(user_name, original_password, new_password)
            if respond == "Change password successfully":
                print "From Server - " + respond
            elif respond == "The original password is wrong":
                print "From Server - Error: " + respond
            else:
                print "From Server - Error: " + respond
        except:
            print "There are some errors when changing the user password"

# call list_files function to get the list of files under current directory
    elif state == 7:
        try:
            file_list = client.list_files(user_name,rel_path,work_key)
            for files in file_list:
                print files
        except:
            print "There are some errors when calling the ls function"

# call change_directory function
    elif state == 8:
        try:
        # get the directory name from the input of users
            dir_name = raw_input("Change directory to: ")
            rel_path_buffer = dir_name
            # If users need to go back to parent directory
            if dir_name == "..":
            # check whether it reaches the root of user directory or not
                if rel_path == "/":
                    dir_name = "/"
                else:
                    dir_name = rel_path
                    dir_name_buffer = dir_name.split('/')
                    if len(dir_name_buffer) == 2:
                        dir_name = "/"
                    elif len(dir_name_buffer) > 2:
                        for i in range(1, len(dir_name_buffer)-1):
                            dir_name = "/" + dir_name_buffer[i]
                #dir_name = os.path.relpath(os.path.join(dir_name, os.pardir))
            if dir_name == "/":
                rel_path_buffer = ""
            elif rel_path_buffer == "..":
                dir_name = dir_name
            else:
                dir_name = rel_path + "/" + dir_name
            respond = client.change_directory(user_name,dir_name,work_key)
            # if cd successfully, update rel_path parameter
            if respond == "cd successfully":
                rel_path = dir_name
            print respond	    
        except:
            print "There are some errors when changing the directory"

# call the log out function to delete related user information
    elif state == 9:
        try:
            respond = client.log_out(user_name, work_key)
            print respond
        except:
            print "There are some errors when logging out"

# share file
    elif state == 10:
        try:
            filename = raw_input("Please enter the filename:")
            toWho = raw_input("Please enter the user you want to share file with:")
            client.share_File(user_name, filename, toWho)
        except:
            print "There are some errors when sharing specific file"
# list shared files
    elif state == 11:
        try:
            file_list = client.list_SharedFiles(user_name)
            for files in file_list:
                print files
        except:
            print "There are some errors when listing shared files"
# download shared files  instruction "donwload_shared"
    elif state == 12:
        try:
            file_name = raw_input("Please enter the filename:")
            file_location = work_path + "/" + file_name
            with open(file_location, "wb") as handle:
                handle.write(client.download_SharedFiles(file_name,user_name).data)
            print "From client - Downloading shared file successfully"
        except:
            print "There are some errors when downloading shared files"
    elif state == 13:
        try:
            file_name = raw_input("Please enter the filename:")
            file_location = work_path + "/" + file_name
            with open(file_location, "wb") as handle:
                handle.write(client.download_SharedFiles(file_name,user_name).data)
            file_location = work_path + "/" + file_name
            #firstly need to make sure that the file uploaded does exist
            if os.path.exists(file_location):
                # open the file, reand the content and send these content
                with open(file_location, "rb") as handle:
                    transmit_data = xmlrpclib.Binary(handle.read())
                    respond = client.upload_files(user_name,file_name,transmit_data,work_key)
                # Based on the respond to output corresponding information
            print "From client - forking shared file to cloud successfully"
        except:
            print "There are some errors when forking shared files"
# if the function is unrecognized, print Error information
    else:
        print "From client - Unrecognized function, please enter again!"




