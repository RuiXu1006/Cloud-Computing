import xmlrpclib
import os
import sys
import errno
import thread
from threading import Thread, Lock, Condition
import random
import time

# Get the home directory
home_dir = os.path.expanduser("~")
# When setting up the client, build corresponding files
root_path = home_dir + "/" + "LocalBox"
if not (os.path.exists(root_path)):
    os.mkdir(root_path)

users = ["cai", "zc", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"]
passwords = ["533250", "682525", "001", "002", "003", "004", "005", "006", "007", "008"]
count = 0;

class ClientClass(Thread):
    def __init__(self,id):
        Thread.__init__(self)
        self.id =id
        self.user_name = ""
        self.work_path = ""
        self.rel_path = ""
        self.work_key = ""
        self.file_name = ""
        print "Current running client is # %d "  %self.id
        
    def run(self):
        self.doit(self.id, self.user_name, self.work_path, self.rel_path, self.work_key,self.file_name);
        
    def doit(self, id, user_name, work_path, rel_path, work_key, file_name):
        global users
        global passwords
        global root_path
        global count
        self.client = xmlrpclib.ServerProxy("http://localhost:8000/")
        #print "The following are available methods on data server"
        #print self.client.system.listMethods()

# check the sign_up method
        self.pwd = 0
        user_name = "cc"+str(self.id)
        self.pwd  = 10*100+self.id
        self.new_dir = ""
        self.initial_password = self.client.sign_up(user_name, self.pwd)
        
        if self.initial_password != "Error: This username has been used.":
            self.new_dir = root_path + "/" + user_name;
        else:
            print "From Server - Error: This username has been used"
        print "From Server: Your initial password is " + self.initial_password
        print "From Client - Sign up successfully"
        open(home_dir+"/CloudBox/"+user_name+"/b", 'a').close()
        open(home_dir+"/CloudBox/"+user_name+"/a", 'a').close()
        #print self.new_dir + "/" +"a"
        self.password = str(self.pwd)
        #print self.password

# check the login_in method
        #user_name = users[id]
        #password = passwords[id]
        respond = self.client.login_in(user_name, self.password)
        respond_buffer = respond.split('#')
        respond = respond_buffer[0]
        print "client#%d From client- " %self.id + respond
        if respond == "Login in successfully":
            rel_path = ""
            work_key = respond_buffer[1]
            print "From client - the key is " + work_key
            user_folder = root_path + "/" + user_name
            if not (os.path.exists(user_folder)):
                os.mkdir(user_folder)
            work_path = user_folder
        
        time.sleep(random.randint(1, 3))
# list files
        file_list = self.client.list_files(user_name,rel_path,work_key)
        for files in file_list:
            print files
            
            
        time.sleep(random.randint(1, 3))
# search files
        file_name = "a"
        respond = self.client.search_files(user_name,file_name,work_key)
        if respond == "Not found":
            print "client#%d Unable to find the corresponding file." %self.id
        else:
            print "client#%d The file is found, the location is " %self.id + respond
            
        
        time.sleep(random.randint(1, 3))
# download files
        file_name = "a"
        respond = self.client.search_files(user_name, file_name, work_key)
        if respond != "Not found":
            file_location = work_path + "/" + file_name
            print file_location +"\n"
            with open(file_location, "wb") as handle:
                handle.write(self.client.download_files(user_name,file_name,work_key).data)
            print "client#%d From client - Downloading file successfully" %self.id
        # If the file doesn't exist, show the failure of downloading
        else:
            print "client#%d From client - Downloading Failure: the required file doesn't exist in server" %self.id
            
            
        time.sleep(random.randint(1, 3))
# delete files  
        respond = self.client.search_files(user_name,file_name,work_key)
        # if the file exist, delete it
        if respond != "Not found":
            if self.client.delete_files(user_name,file_name,work_key):
                print "From client - Delete file successfully"
        # otherwise, print the error information
            else:
                print "From client - Delete file unsuccessfully, because the file doesn't exist."
                
        
        time.sleep(random.randint(1, 3))
# check if every thread runs to the end
        count += 1
        if (count >= 100):
            print "Cool! Everything works well!"

for i in range(50):
    c = ClientClass(i);
    c.start()