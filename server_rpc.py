# This file uses RPC method to implement the communcation
# between single client and single data server
import xmlrpclib, os, random
import re
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
import threading
import time
from threading import Thread, Lock, Condition

class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

# total number of server
serverNum = 9

# This dictionary is used for storing user information in data server
user_record = dict()
# This dictionary is used for access key for different users
key_table = dict()
# This path is only used for listing files and changing directories
global root_path
global user_information
# Firstly, get the home directory of the computer
home_dir = os.path.expanduser("~")
root_path = home_dir + "/" + "CloudBox"
user_information = root_path + "/" + "User_information.txt"

# This function is used for testify whether the user has the access to
# use some specific functions




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


class MultiServer(Thread):
    def __init__(self,id):
        Thread.__init__(self)
        self.id =id
        
    
    
    def security_check(self,user_name, key):
        foundmatch = False
        for key in key_table:
            if key_table[key] == user_name:
                return user_name
        if ~foundmatch:
            result = "denied access"
            return result
     

    # This function is used for server to build directories at the beginning
    def build_up(self,root_path):
        global lock
        lock.acquire_write()
    # tests whether this directory exists or not, if the directory doesn't exist,
    # create root directory for servers
        if not (os.path.exists(root_path)):
            os.mkdir(root_path)
        if not (os.path.exists(root_path+"/"+str(self.id))):
            os.mkdir(root_path+"/"+str(self.id))
    # Then, based on the user_record, tests whether each user has its own directory
    # or not, if not, building corresponding folders
        user_folder = root_path + "/default"
        """" the creation of user fold should not build in this function
        for user_name in user_record:
            user_folder = root_path + "/" +str(self.id) +"/" + user_name;
        """
        if not (os.path.exists(user_folder)):
            os.mkdir(user_folder)
        lock.release_write()

    # This function is used for getting user record from specific file at the beginning
    def build_user_record(self):
        global lock
        lock.acquire_write()
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
        #print user_record 
        lock.release_write()

    # This function is used for signing up into the data server
    def sign_up(self, user_name, password):
    # Firstly make sure that the user_name doesn't exist
        print "here"
        global lock
        lock.acquire_write()
        if user_name in user_record:
            respond = "Error: This username has been used."
        else:
            initial_password = str(password)
    # add the user_name and initial password into user_record
            user_record[user_name] = initial_password	
            respond = "Sign up successfully!"
            f = open(user_information, 'a')
            content = "Username: " + user_name + "    " + "Password: " + initial_password + '\n'
            f.write(content)
    # build new directory file for new users
            new_dir = root_path + "/" +str(self.id) +"/"+ user_name
            os.mkdir(new_dir)
        lock.release_write()
        return respond

    # This function is used for changing the password for clients
    # The client has to provide original password, and new password
    def change_password(self, user_name, original_password, new_password):
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
    def login_in(self,user_name, password):
        global current_user
        global lock
        lock.acquire_write()
    # Firstly, make sure that there is user_name in the record
        if user_name in user_record.keys():
    # Then check whether the password corresponds or not
            if password == user_record[user_name]:
                access_key = random.randint(0, 10000000)
                access_key = str(access_key)
                key_table[access_key] = user_name
                respond = "Login in successfully#" + access_key
                current_user = user_name
    	    #print key_table
            else:
                respond = "The password doesn't match with the given username"
        else:
            respond = "The username doesn't exist"
        lock.release_write()
        return respond

    # This function is used for listing files in the data servers

    def list_files(self,user_name,rel_path,key):
        global lock
        lock.acquire_write()
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
        else:
            current_user = self.security_check(user_name, key)
            work_path = root_path + "/" +str(self.id) +"/" + current_user + "/" + rel_path
            file_list = os.listdir(work_path)
            respond = file_list
        lock.release_write()
        print "listfile %d" % self.id
        return respond

    # This function is used for change directories in the data server
    def change_directory(self,user_name,rel_path,key):
        global lock
        lock.acquire_write()
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
        else:
            current_user = self.security_check(user_name, key)
    # get the work path from the information sent by client
            work_path = root_path + "/" + str(self.id) +"/" + current_user + rel_path
    # Firstly, check if that this path exist or not
        if os.path.exists(work_path):
    # Then make sure that is directory
            if os.path.isdir(work_path):
                respond = "cd successfully"	
            else:
                respond = "From Server: This is not a directory!"
        else:
            respond = "From Server: This directory doesn't exist!"
        lock.release_write()
        return respond

    # This function is used for search files in the file system
    # of data server, if there is required file, return True,
    # otherwise return false
    def search_files(self,user_name, file_name, key):
        global lock
        lock.acquire_write()
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
        else:
            current_user = self.security_check(user_name, key)
    # set the path of root directory, and found flag to be false
            work_path = root_path + "/" + str(self.id) +"/" + current_user
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
    # If flag is false, return false information
            else:
                respond = "Not found"
        
        lock.release_write()    
        return respond

    # This function is used for downloading files to client
    def download_files(self,user_name, file_name, key):
        global lock
        lock.acquire_write()
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
        else:
            current_user =  self.security_check(user_name, key)
    # set the path root directory, and found flag to be false
            work_path = root_path + "/" + str(self.id) +"/" + current_user
    # get the file location of give file
            file_location = self.search_files(user_name, file_name, key)
            print "From server - The download file locates at " + file_location
            with open(file_location, "rb") as handle:
                respond = xmlrpclib.Binary(handle.read())
        lock.release_write()
        return respond
            

    # This function is used for uploading files from client
    def upload_files(self,user_name,file_name, transmit_data, key):
        global lock
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
            return respond
        else:
            lock.acquire_write()
            current_user = self.security_check(user_name, key)
    # set the root directory to store upload files, and get
    # the file location
            work_path = root_path + "/" + str(self.id) +"/" +current_user;
            file_location = work_path + "/" + file_name
            with open(file_location, "wb") as handle:
                handle.write(transmit_data.data)
            lock.release_write()
            return True

    # This function is used for deleting files from server
    def delete_files(self,user_name, file_name, key):
        global lock
        if self.security_check(user_name, key) == "denied access":
            respond = "You have no right to use this function"
            return respond
        else:
            lock.acquire_write()
            current_user = self.security_check(user_name, key)
    # get the location of the file which will be deleted
            file_location = self.search_files(user_name, file_name, key)
            os.remove(file_location)
            lock.release_write()
            return True
    
    def run(self):
        global server
        server[self.id] = ThreadXMLRPCServer(("localhost", 8000+self.id), allow_none=True)
        print "port %d" %(self.id+8000) + " is established!"
        self.build_up(root_path)
        self.build_user_record()
        server[self.id].register_introspection_functions()
        server[self.id].register_function(self.sign_up, "sign_up")
        server[self.id].register_function(self.change_password, "change_password")
        server[self.id].register_function(self.login_in, "login_in")
        server[self.id].register_function(self.list_files, "list_files")
        server[self.id].register_function(self.change_directory, "change_directory")
        server[self.id].register_function(self.search_files, "search_files")
        server[self.id].register_function(self.download_files, "download_files")
        server[self.id].register_function(self.upload_files, "upload_files")
        server[self.id].register_function(self.delete_files, "delete_files")
        server[self.id].serve_forever()
        print "port %d" %(self.id+8000) + " is established!"

lock = ReadWriteLock()
#server_object = Server()

server = [1]*serverNum
# for k in range(1):
#     server[k] = ThreadXMLRPCServer(("localhost", 8000+k), allow_none=True)
#     print "port %d" %(k+8000) + " is established!"
#     build_up(root_path)
#     build_user_record()
#     server[k].register_introspection_functions()
#     server[k].register_function(sign_up, "sign_up")
#     server[k].register_function(change_password, "change_password")
#     server[k].register_function(login_in, "login_in")
#     server[k].register_function(list_files, "list_files")
#     server[k].register_function(change_directory, "change_directory")
#     server[k].register_function(search_files, "search_files")
#     server[k].register_function(download_files, "download_files")
#     server[k].register_function(upload_files, "upload_files")
#     server[k].register_function(delete_files, "delete_files")
#     server[k].serve_forever()

for i in range(serverNum):
    svr = MultiServer(i);
    svr.start()