#!/usr/bin/python

import xmlrpclib
import os

try:
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"

class simpleapp_wx(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,id,title)
        self.parent = parent
        self.username = "null"
        self.client = xmlrpclib.ServerProxy("http://localhost:8000/")
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
        self.welcomePanel.Hide()
        self.changePassPanel.Hide()

# Panel for sign up or login
class InitialPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent=parent, size=(500,300), style=wx.ALIGN_CENTER)
    	sizer = wx.BoxSizer(wx.VERTICAL)
    	
    	# Sign up
    	sign_up = wx.Button(self,-1,label="Sign up", size=(150,20))
        sizer.Add(sign_up, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.TOP, border=25)
        self.Bind(wx.EVT_BUTTON, self.Sign_upClick, sign_up)
        
    	# Log in
    	log_in = wx.Button(self,-1,label="Log in", size=(150,20))
        sizer.Add(log_in, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.TOP, border=25)
        self.Bind(wx.EVT_BUTTON, self.Log_inClick, log_in)
        
        self.SetSizer(sizer)

    def Sign_upClick(self,event):
        self.Hide()
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
        self.GetParent().username = self.text0.GetValue()
        respond = self.GetParent().client.login_in(self.text0.GetValue(), self.text1.GetValue())
        if respond == "Login in successfully":
            self.Hide()
            self.menubar = functionMenuBar()
            self.GetParent().SetMenuBar(self.menubar)
            self.GetParent().Layout()
            self.GetParent().listPanel = ListPanel(self.GetParent())
            self.GetParent().GetSizer().Add(self.GetParent().listPanel, 1, flag= wx.ALIGN_TOP|wx.ALL, border=10)   
            self.GetParent().listPanel.Show()
            self.GetParent().GetSizer().Layout()
        else:
            self.label2 = wx.StaticText(self,-1,label='Login failed!', style=wx.ALIGN_CENTER)
            self.GetSizer().Add(self.label2, 1, flag=wx.ALIGN_CENTER)
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
        
        text0 = wx.TextCtrl(self, -1)
        sizer.Add(text0, (0,1), (1,1), wx.EXPAND)
        
        label1 = wx.StaticText(self,-1,label=u'Password', style=wx.ALIGN_CENTER)
        sizer.Add(label1, (1,0), (1,1))
        
        text1 = wx.TextCtrl(self, -1)
        sizer.Add(text1, (1,1), (1,1), wx.EXPAND)
        
        button = wx.Button(self,-1,label="Sign up")
        sizer.Add(button, (2,0), (1,2), wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.Sign_upClick, button)
        
        sizer.AddGrowableCol(1)
        
        hbox.Add(sizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

        self.SetSizer(hbox)
    
    # TODO: Need to define the right sign up interface
    def Sign_upClick(self, event):
        button = wx.Button(self,-1,label="Sign up")
        
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
            respond = self.GetParent().client.upload_files(self.GetParent().username, file_name, transmit_data)
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
        
        filelist = self.GetParent().client.list_files(self.GetParent().username)
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
            handle.write(self.GetParent().client.download_files(username, file_name).data)
    
    def OnDelete(self, event):
        username = self.GetParent().username
        sel = self.listbox.GetSelection()
        file_name = self.listbox.GetString(sel)
        
        self.GetParent().client.delete_files(username, file_name)
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
            self.label2 = wx.StaticText(self,-1,label='Change password successfully', style=wx.ALIGN_CENTER)
            self.GetSizer().Add(self.label2, 1, flag=wx.ALIGN_CENTER)
            self.GetSizer().Layout()
            self.GetParent().Layout()
            self.GetParent().GetSizer().Layout()
        else:
            self.label3 = wx.StaticText(self,-1,label='Failed!', style=wx.ALIGN_CENTER)
            self.GetSizer().Add(self.label3, 1, flag=wx.ALIGN_CENTER)
            self.GetSizer().Layout()
            self.GetParent().Layout()
            self.GetParent().GetSizer().Layout()
    
if __name__ == "__main__":
    app = wx.App()
    frame = simpleapp_wx(None,-1,'Cloud Storage System')
    app.MainLoop()