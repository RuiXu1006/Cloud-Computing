#!/usr/bin/python

import xmlrpclib
import os
import re

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
        self.sizer.Add(self.changePassPanel, 1, flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        
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
    
    def Log_inClick(self,event):
        # Login to the right server
        # Issue: what if user change computer to login?
        self.GetParent().username = self.text0.GetValue()
        f = open(user_information, 'r+')
        lines = f.readlines()
        # Flag to indicate whether the user record exists locally
        flag = 0
        for line in lines:
            con_buffer = re.split('\W+', line)
            if con_buffer[1] == self.GetParent().username:
                srvName = con_buffer[3]
                flag = 1
        
        if flag == 1:
            self.GetParent().client = xmlrpclib.ServerProxy("http://localhost:"+srvName+"/")
        else:
            self.GetParent().master = xmlrpclib.ServerProxy("http://localhost:8000/")
            respond, srvName = self.GetParent().master.query_server(self.GetParent().username)
            if respond == "Found":
                self.GetParent().client = xmlrpclib.ServerProxy("http://localhost:"+srvName+"/")
                flag = 1
            else:
                wx.MessageBox('Login failed!', 'Info', wx.OK | wx.ICON_INFORMATION)
                self.GetSizer().Layout()
                self.GetParent().Layout()
                self.GetParent().GetSizer().Layout()
        
        # Login to the corresponding server
        if flag == 1:    
            respond, srvName = self.GetParent().client.login_in(self.text0.GetValue(), self.text1.GetValue())
            respond_buffer = respond.split('#')
            if respond_buffer[0] == "Login in successfully":
                self.GetParent().key = respond_buffer[1]
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
        respond, srvName = self.GetParent().master.sign_up(username, self.text1.GetValue())
        if respond == "Sign up successfully!":
            self.Hide()  
            self.GetParent().initialPanel.Show()
            self.GetParent().GetSizer().Layout()
            # Add the user-server information
            f = open(user_information, 'a+')
            content = "Username: " + username + "    " + "ServerID: " + srvName + '\n'
            f.write(content)
            f.close()
            # Create new folder
            new_dir = root_path + "/" + username;
            if not (os.path.exists(new_dir)):
                os.mkdir(new_dir)           
        else:
            wx.MessageBox('Sign up failed!', 'Info', wx.OK | wx.ICON_INFORMATION)
            self.GetSizer().Layout()
            self.GetParent().Layout()
            self.GetParent().GetSizer().Layout()
        
# Panel for function toolbar
class functionMenuBar(wx.MenuBar):
    def __init__(self):
    	wx.MenuBar.__init__(self)
    	
        fileMenu = wx.Menu()
        
        upload = wx.MenuItem(fileMenu,wx.ID_ANY, 'Upload')
        fileMenu.AppendItem(upload)
        self.Bind(wx.EVT_MENU, self.UploadClick, upload)
        
        self.Append(fileMenu, 'File')
        
        userMenu = wx.Menu() 
        change_pass = wx.MenuItem(fileMenu,wx.ID_ANY, 'Change password')
        userMenu.AppendItem(change_pass)
        self.Bind(wx.EVT_MENU, self.Change_passClick, change_pass)
        
        self.Append(userMenu, 'User')
        
    # Individual panels for each function    
    def UploadClick(self,event):
        filePicker = wx.FileDialog(self, defaultDir=os.getcwd(), defaultFile="", style=wx.OPEN)
        filePicker.ShowModal()
        file_location = filePicker.GetPath()
        file_name = filePicker.GetFilename()
        with open(file_location, "rb") as handle:
            transmit_data = xmlrpclib.Binary(handle.read())
            respond = self.GetParent().client.upload_files(self.GetParent().username, file_name, transmit_data, self.GetParent().key)
        self.GetParent().listPanel.listbox.Append(file_name)
        self.GetParent().GetSizer().Layout()
    
    def Change_passClick(self,event):
        self.GetParent().HideAll()
        self.GetParent().changePassPanel.Show()
        self.GetParent().GetSizer().Layout()

# class WelcomePanel(wx.Panel):    
#     def __init__(self, parent):
#         wx.Panel.__init__(self, parent=parent, style=wx.ALIGN_CENTER)
#         sizer = wx.BoxSizer(wx.VERTICAL)
#         
#         # Initial message panel
#         font = wx.Font(36, wx.DEFAULT, wx.NORMAL, wx.BOLD)
#         label = wx.StaticText(self,-1,label=u'Welcome!', size=(300, 40), style=wx.ALIGN_CENTER)
#         label.SetForegroundColour(wx.RED)
#         label.SetFont(font)
#         sizer.Add(label, wx.ALIGN_CENTER )
#         
#         self.SetSizer(sizer)

class ListPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, style=wx.ALIGN_CENTER)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        filelist = self.GetParent().client.list_files(self.GetParent().username, "", self.GetParent().key)
        self.listbox = wx.ListBox(self, -1, choices=filelist)
        hbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 20)
        
        btnPanel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        download = wx.Button(btnPanel, -1, 'Download', size = (90, 30))
        delete = wx.Button(btnPanel, -1, 'Delete', size = (90, 30))
        
        self.Bind(wx.EVT_BUTTON, self.OnDownload, download)
        self.Bind(wx.EVT_BUTTON, self.OnDelete, delete)
        
        vbox.Add((-1, 20))
        vbox.Add(download)
        vbox.Add(delete, 0, wx.TOP, 5)
        
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

## TODO
# class SearchPanel(wx.Panel):
# class UploadPanel(wx.Panel):
# class DownloadPanel(wx.Panel):
# class DeletePanel(wx.Panel):

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
            self.GetSizer().Layout()
            self.GetParent().Layout()
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