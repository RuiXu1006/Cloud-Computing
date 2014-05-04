#!/usr/bin/python

import xmlrpclib
import os
import re
import random

try:
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"

global user_information

home_dir = os.path.expanduser("~")
root_path = home_dir + "/" + "LocalBox"
user_information = root_path + "/" + "User_information.txt"

class simpleapp_wx(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,id,title)
        self.parent = parent
        self.username = "null"
        self.key = "null"
        if not os.path.exists(root_path):
            os.mkdir(root_path)
        self.initialize()

    def initialize(self):
        self.sizer = wx.BoxSizer()
        
        # Sign up or login process
        self.initialPanel = InitialPanel(self)
        self.loginPanel = LoginPanel(self)
        self.loginPanel.Hide()
        self.signupPanel = SignupPanel(self)
        self.signupPanel.Hide() 
        #self.welcomePanel = WelcomePanel(self)
        #self.welcomePanel.Hide()
        self.changePassPanel = ChangePassPanel(self)
        self.changePassPanel.Hide()
        
        self.sizer.Add(self.initialPanel, 1, wx.EXPAND)
        self.sizer.Add(self.loginPanel, 1, wx.EXPAND)
        self.sizer.Add(self.signupPanel, 1, wx.EXPAND)
        #self.sizer.Add(self.welcomePanel, 1, flag= wx.ALIGN_CENTER|wx.ALL, border=10)        
        self.sizer.Add(self.changePassPanel, 1, wx.EXPAND)
        
        self.SetSizerAndFit(self.sizer)
        self.Show()
    
    def HideAll(self):
        self.listPanel.Hide()
        self.changePassPanel.Hide()

# Panel for sign up or login
class InitialPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent=parent, size=(400,350), style=wx.ALIGN_CENTER)
    	sizer = wx.BoxSizer(wx.VERTICAL)
    	
        #l Logo
        self.logo = wx.Image('logo.png', wx.BITMAP_TYPE_ANY)
        #self.logo = self.logo.Scale(300, 187)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(self.logo))
        sizer.Add(self.imageCtrl, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        # Sign up
    	sign_up = wx.Button(self,-1,label="Sign up", size=(150,20))
        sizer.Add(sign_up, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.TOP, border=15)
        self.Bind(wx.EVT_BUTTON, self.Sign_upClick, sign_up)
        
    	# Log in
    	log_in = wx.Button(self,-1,label="Log in", size=(150,20))
        sizer.Add(log_in, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.TOP, border=15)
        self.Bind(wx.EVT_BUTTON, self.Log_inClick, log_in)
        
        self.SetSizer(sizer)

    def Sign_upClick(self,event):
        self.Hide()
        # Talk to the master server when signup
        self.GetParent().master = xmlrpclib.ServerProxy("http://localhost:8000/")
        self.GetParent().signupPanel.Show()
        self.GetParent().GetSizer().Layout()
        
    def Log_inClick(self,event):        
        self.Hide()
        self.GetParent().loginPanel.Show()
        self.GetParent().GetSizer().Layout()
        
class LoginPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent=parent, style=wx.ALIGN_CENTER)
        hbox = wx.BoxSizer(wx.VERTICAL)
        
        sizer = wx.GridBagSizer(25,10)
        
        label0 = wx.StaticText(self,-1,label=u'Username', style=wx.ALIGN_CENTER)
        sizer.Add(label0, (0,0), (1,1))
        
        self.text0 = wx.TextCtrl(self, -1)
        sizer.Add(self.text0, (0,1), (1,1), wx.EXPAND)
        
        label1 = wx.StaticText(self,-1,label=u'Password', style=wx.ALIGN_CENTER)
        sizer.Add(label1, (1,0), (1,1))
        
        self.text1 = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD)
        sizer.Add(self.text1, (1,1), (1,1), wx.EXPAND)
        
        button = wx.Button(self,-1,label="Log in")
        sizer.Add(button, (2,0), (1,2), wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.Log_inClick, button)
        
        sizer.AddGrowableCol(1)
        
        hbox.Add(sizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

        self.SetSizer(hbox)
    
    # This function is used for selecting data server from clients side
    def select_dserver(self, username):
        svr_list = []
        if (os.path.exists(root_path + "/" +username + "/svrName.txt")):
            f = open(root_path + "/" + username + "/svrName.txt", 'r')
            # Store all valid data server names in the list
            svrName = f.readline()
            while (svrName):
                svrName = svrName.rstrip('\n')
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
            return svrName
        else:
            return 0;

    def Log_inClick(self,event):
        # Login to the right server
        # Issue: what if user change computer to login?
        self.GetParent().username = self.text0.GetValue()
        user_name = self.text0.GetValue()
        svrName = self.select_dserver(user_name)
        # if not found effective server port in local file, ask for master server
        if svrName == 0:
            self.GetParent().master = xmlrpclib.ServerProxy("http://localhost:8000/")
            respond, svr_list = self.GetParent().master.query_server(user_name)
            if respond == "Found":
                f = open(root_path+"/"+user_name+"/svrName.txt", 'w+')
                for index in range(0, len(svr_list)):
                    content = str(svr_list[index])
                    f.write(content + "\n")
                f.close()
            svrName = self.select_dserver(user_name)

            # If unable to connect with data server, the client will ask the master server
            # to update avaible data server list, and re-login again
        try:
            if svrName != 0:
                self.GetParent().client = xmlrpclib.ServerProxy(str(svrName))
                #print user_name + " || "+ password
                respond, svrName = self.GetParent().client.login_in(user_name, self.text1.GetValue())
                respond_buffer = respond.split('#')
                respond = respond_buffer[0]
                if respond == "Login in successfully":
                    self.GetParent().key = respond_buffer[1]
                    user_folder = root_path + "/" + user_name
                    if not (os.path.exists(user_folder)):
                        os.mkdir(user_folder)
                    self.Hide()
                    self.menubar = functionMenuBar()
                    self.GetParent().SetMenuBar(self.menubar)
                    self.GetParent().Layout()
                    self.GetParent().listPanel = ListPanel(self.GetParent())
                    self.GetParent().GetSizer().Add(self.GetParent().listPanel, 1, flag= wx.ALIGN_TOP|wx.ALL)   
                    self.GetParent().listPanel.Show()
                    self.GetParent().GetSizer().Layout()
                else:
                    wx.MessageBox('Login failed!', 'Info', wx.OK | wx.ICON_INFORMATION)
                    self.GetSizer().Layout()
                    self.GetParent().Layout()
                    self.GetParent().GetSizer().Layout()
            else:
                wx.MessageBox('Login failed!', 'Info', wx.OK | wx.ICON_INFORMATION)
                self.GetSizer().Layout()
                self.GetParent().Layout()
                self.GetParent().GetSizer().Layout()
        except:
            # Then client asks master servers to update current available data server list
            self.GetParent().master = xmlrpclib.ServerProxy("http://localhost:8000/")
            respond, svr_list = self.GetParent().master.update_dsvr(user_name)
            # Then update local available data server list
            if not os.path.exists(root_path+"/"+user_name):
                os.mkdir(root_path+"/"+user_name)
            f = open(root_path+"/"+user_name+"/svrName.txt", 'w+')
            for index in range(0, len(svr_list)):
                content = svr_list[index]
                f.write(str(content) + "\n")
            f.close()
            # Then login in again
            svrName = self.select_dserver(user_name)
            self.GetParent().client = xmlrpclib.ServerProxy(str(svrName))
            respond, svrName = self.GetParent().client.login_in(user_name, self.text1.GetValue())
            respond_buffer = respond.split('#')
            respond = respond_buffer[0]
            if respond == "Login in successfully":
                self.GetParent().key = respond_buffer[1]
                user_folder = root_path + "/" + user_name
                if not (os.path.exists(user_folder)):
                    os.mkdir(user_folder)
                self.Hide()
                self.menubar = functionMenuBar()
                self.GetParent().SetMenuBar(self.menubar)
                self.GetParent().Layout()
                self.GetParent().listPanel = ListPanel(self.GetParent())
                self.GetParent().GetSizer().Add(self.GetParent().listPanel, 1, flag= wx.ALIGN_TOP|wx.ALL, border=10)   
                self.GetParent().listPanel.Show()
                self.GetParent().GetSizer().Layout()
            else:
                wx.MessageBox('Login failed!', 'Info', wx.OK | wx.ICON_INFORMATION)
                self.GetSizer().Layout()
                self.GetParent().Layout()
                self.GetParent().GetSizer().Layout()

class SignupPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent=parent, style=wx.ALIGN_CENTER)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer = wx.GridBagSizer(25,10)
        
        label0 = wx.StaticText(self,-1,label=u'Username', style=wx.ALIGN_CENTER)
        sizer.Add(label0, (0,0), (1,1))
        
        self.text0 = wx.TextCtrl(self, -1)
        sizer.Add(self.text0, (0,1), (1,1), wx.EXPAND)
        
        label1 = wx.StaticText(self,-1,label=u'Password', style=wx.ALIGN_CENTER)
        sizer.Add(label1, (1,0), (1,1))
        
        self.text1 = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD)
        sizer.Add(self.text1, (1,1), (1,1), wx.EXPAND)
        
        button = wx.Button(self,-1,label="Sign up")
        sizer.Add(button, (2,0), (1,2), wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.Sign_upClick, button)
        
        sizer.AddGrowableCol(1)
        
        hbox.Add(sizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

        self.SetSizer(hbox)
    
    def Sign_upClick(self, event):
        username = self.text0.GetValue()
        respond, svr_list = self.GetParent().master.sign_up(username, self.text1.GetValue())
        if respond == "Sign up successfully!":
            self.Hide()  
            self.GetParent().initialPanel.Show()
            self.GetParent().GetSizer().Layout()
            # Add the user-server information
            new_dir = root_path + "/" + username;
            if not os.path.exists(new_dir):
                os.mkdir(new_dir)
            f = open(root_path+"/"+username+"/svrName.txt", 'w+')
            for index in range(0, len(svr_list)):
                content = str(svr_list[index])
                f.write(content + "\n")
            f.close()           
        else:
            wx.MessageBox('Sign up failed!', 'Info', wx.OK | wx.ICON_INFORMATION)
            self.GetSizer().Layout()
            self.GetParent().Layout()
            self.GetParent().GetSizer().Layout()
        
# Panel for function toolbar
class functionMenuBar(wx.MenuBar):
    def __init__(self):
    	wx.MenuBar.__init__(self)
        
        userMenu = wx.Menu() 

        shared_files = wx.MenuItem(userMenu,wx.ID_ANY, 'Shared files')
        userMenu.AppendItem(shared_files)
        self.Bind(wx.EVT_MENU, self.Shared_filesClick, shared_files)

        change_pass = wx.MenuItem(userMenu,wx.ID_ANY, 'Change password')
        userMenu.AppendItem(change_pass)
        self.Bind(wx.EVT_MENU, self.Change_passClick, change_pass)
        
        logout = wx.MenuItem(userMenu,wx.ID_ANY, 'Log out')
        userMenu.AppendItem(logout)
        self.Bind(wx.EVT_MENU, self.Log_outClick, logout)
        
        self.Append(userMenu, 'User')       
    
    def Shared_filesClick(self,event):
        self.GetParent().HideAll()
        self.GetParent().sharePanel = SharePanel(self.GetParent())
        self.GetParent().sizer.Add(self.GetParent().sharePanel, 1, wx.EXPAND)
        self.GetParent().sharePanel.Show()
        self.GetParent().GetSizer().Layout()

    def Change_passClick(self,event):
        self.GetParent().HideAll()
        self.GetParent().changePassPanel.Show()
        self.GetParent().GetSizer().Layout()
    
    def Log_outClick(self,event):
        try:
            respond = self.GetParent().client.log_out(self.GetParent().username, self.GetParent().key)
            self.GetParent().HideAll()
            self.GetParent().initialPanel.Show()
            self.GetParent().GetSizer().Layout()
        except:
            print "There are some errors when logging out"

class ListPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, size=(400,350),style=wx.ALIGN_CENTER)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        filelist = self.GetParent().client.list_files(self.GetParent().username, "", self.GetParent().key)
        self.listbox = wx.ListBox(self, -1, choices=filelist)
        hbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 20)
        
        btnPanel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        upload = wx.Button(btnPanel, -1, 'Upload', size = (90,30))
        download = wx.Button(btnPanel, -1, 'Download', size = (90, 30))
        delete = wx.Button(btnPanel, -1, 'Delete', size = (90, 30))
        share = wx.Button(btnPanel, -1, 'Share', size = (90, 30))
        
        self.Bind(wx.EVT_BUTTON, self.OnUpload, upload)
        self.Bind(wx.EVT_BUTTON, self.OnDownload, download)
        self.Bind(wx.EVT_BUTTON, self.OnDelete, delete)
        self.Bind(wx.EVT_BUTTON, self.OnShare, share)
        
        vbox.Add((-1, 20))
        vbox.Add(upload)
        vbox.Add(download, 0, wx.TOP, 5)
        vbox.Add(delete, 0, wx.TOP, 5)
        vbox.Add(share, 0, wx.TOP, 5)
        
        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND|wx.RIGHT, 20)
        
        self.SetSizer(hbox)
    
    def OnUpload(self, event):
        filePicker = wx.FileDialog(self, defaultDir=os.getcwd(), defaultFile="", style=wx.OPEN)
        filePicker.ShowModal()
        file_location = filePicker.GetPath()
        file_name = filePicker.GetFilename()
        with open(file_location, "rb") as handle:
            transmit_data = xmlrpclib.Binary(handle.read())
            respond = self.GetParent().client.upload_files(self.GetParent().username, file_name, transmit_data, self.GetParent().key)
        self.GetParent().listPanel.listbox.Append(file_name)
        self.GetParent().GetSizer().Layout()
        
    def OnDownload(self, event):
        username = self.GetParent().username
        home_dir = os.path.expanduser("~")
        root_path = home_dir + "/" + "LocalBox"
        user_folder = root_path + "/" + username
        sel = self.listbox.GetSelection()
        file_name = self.listbox.GetString(sel)
        
        if not (os.path.exists(user_folder)):
            os.mkdir(user_folder)
        file_location = user_folder + "/" + file_name
        with open(file_location, "wb") as handle:
            handle.write(self.GetParent().client.download_files(username, file_name, self.GetParent().key).data)
    
    def OnDelete(self, event):
        username = self.GetParent().username
        sel = self.listbox.GetSelection()
        file_name = self.listbox.GetString(sel)
        
        self.GetParent().client.delete_files(username, file_name, self.GetParent().key)
        self.listbox.Delete(sel)
        self.GetParent().GetSizer().Layout()

    def OnShare(self, event):
        username = self.GetParent().username
        sel = self.listbox.GetSelection()
        file_name = self.listbox.GetString(sel)
        
        shareDia = ShareDialog(file_name)
        shareDia.ShowModal()

class ShareDialog(wx.Dialog):
    def __init__(self, filename):
        wx.Dialog.__init__(self, None)
        self.filename = filename
        self.SetSize((200, 150))
        self.SetTitle("Share file")

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        label = wx.StaticText(self,-1,label='Share this file to whom', style=wx.ALIGN_CENTER)
        sizer.Add(label, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        self.text = wx.TextCtrl(self,-1)
        sizer.Add(self.text, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, border=15)

        button = wx.Button(self,-1,label="Submit")
        sizer.Add(button, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.TOP, border=15)

        self.Bind(wx.EVT_BUTTON, self.SubmitClick, button)

        self.SetSizer(sizer)

    def SubmitClick(self, event):
        #respond = self.GetParent.client.share_file(self.text.GetValue(), self.filename)
        respond = 'Share successfully'
        if respond == 'Share successfully':
            wx.MessageBox('Share file successfully!', 'Info', wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox('Share file failed!', 'Info', wx.OK | wx.ICON_INFORMATION)
        self.Destroy()

class SharePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, size=(400,350),style=wx.ALIGN_CENTER)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # TODO: filelist of files that are shared to this user
        filelist = self.GetParent().client.list_files(self.GetParent().username, "", self.GetParent().key)
        self.listbox = wx.ListBox(self, -1, choices=filelist)
        hbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 20)
        
        btnPanel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        download = wx.Button(btnPanel, -1, 'Download', size = (90, 30))
        returnb = wx.Button(btnPanel, -1, 'Return', size = (90, 30))
        
        self.Bind(wx.EVT_BUTTON, self.OnDownload, download)
        self.Bind(wx.EVT_BUTTON, self.OnReturn, returnb)
        
        vbox.Add((-1, 20))
        vbox.Add(download)
        vbox.Add(returnb, 0, wx.TOP, 5)
        
        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND|wx.RIGHT, 20)
        
        self.SetSizer(hbox)

    def OnDownload(self, event):
        username = self.GetParent().username
        home_dir = os.path.expanduser("~")
        root_path = home_dir + "/" + "LocalBox"
        user_folder = root_path + "/" + username
        sel = self.listbox.GetSelection()
        file_name = self.listbox.GetString(sel)
        
        # TODO: need to call server rpc to get data from another server
        if not (os.path.exists(user_folder)):
            os.mkdir(user_folder)
        file_location = user_folder + "/" + file_name
        with open(file_location, "wb") as handle:
            handle.write(self.GetParent().client.download_files(username, file_name, self.GetParent().key).data)

    def OnReturn(self, event):
        self.Hide()
        self.GetParent().listPanel.Show()
        self.GetParent().GetSizer().Layout()

class ChangePassPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, style=wx.ALIGN_CENTER)
        hbox = wx.BoxSizer(wx.VERTICAL)
        
        sizer = wx.GridBagSizer(25,10)
        
        label0 = wx.StaticText(self,-1,label=u'Old Password', style=wx.ALIGN_CENTER)
        sizer.Add(label0, (0,0), (1,1))
        
        self.text0 = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD)
        sizer.Add(self.text0, (0,1), (1,1), wx.EXPAND)
        
        label1 = wx.StaticText(self,-1,label=u'New Password', style=wx.ALIGN_CENTER)
        sizer.Add(label1, (1,0), (1,1))
        
        self.text1 = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD)
        sizer.Add(self.text1, (1,1), (1,1), wx.EXPAND)
        
        button = wx.Button(self,-1,label="Submit")
        sizer.Add(button, (2,0), (1,2), wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.SubmitClick, button)
        
        sizer.AddGrowableCol(1)
        
        hbox.Add(sizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

        self.SetSizer(hbox)
    
    def SubmitClick(self,event):
        respond = self.GetParent().client.change_password(self.GetParent().username, self.text0.GetValue(), self.text1.GetValue())
        if respond == "Change password successfully":
            wx.MessageBox('Change password successfully!', 'Info', wx.OK | wx.ICON_INFORMATION)
            self.Hide()
            self.GetParent().listPanel.Show()
            self.GetParent().GetSizer().Layout()
        else:
            wx.MessageBox('Change password failed!', 'Info', wx.OK | wx.ICON_INFORMATION)
            self.GetSizer().Layout()
            self.GetParent().Layout()
            self.GetParent().GetSizer().Layout()
    
if __name__ == "__main__":
    app = wx.App()
    frame = simpleapp_wx(None,-1,'Cloud Storage System')
    app.MainLoop()