#!/usr/bin/python

try:
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"

class simpleapp_wx(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,id,title)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.sizer = wx.BoxSizer()
        
        # Sign up or login process
        self.initialPanel = InitialPanel(self)
        #self.initialPanel.Hide()
        self.loginPanel = LoginPanel(self)
        self.loginPanel.Hide()
        self.signupPanel = SignupPanel(self)
        self.signupPanel.Hide()    
        self.welcomePanel = WelcomePanel(self)
        self.welcomePanel.Hide()
        self.changePassPanel = ChangePassPanel(self)
        self.changePassPanel.Hide()
        
        self.sizer.Add(self.initialPanel, 1, wx.EXPAND)
        self.sizer.Add(self.loginPanel, 1, wx.EXPAND)
        self.sizer.Add(self.signupPanel, 1, wx.EXPAND)
        self.sizer.Add(self.welcomePanel, 1, flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        self.sizer.Add(self.changePassPanel, 1, flag= wx.ALIGN_CENTER|wx.ALL, border=10)
        
        self.SetSizerAndFit(self.sizer)
        self.Show()
    
    def HideAll(self):
        self.welcomePanel.Hide()
        self.changePassPanel.Hide()

# Panel for sign up or login
class InitialPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent=parent, size=(300,200), style=wx.ALIGN_CENTER)
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
        
        button = wx.Button(self,-1,label="Log in")
        sizer.Add(button, (2,0), (1,2), wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.Log_inClick, button)
        
        sizer.AddGrowableCol(1)
        
        hbox.Add(sizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

        self.SetSizer(hbox)
    
    def Log_inClick(self,event):
        self.Hide()
        self.menubar = functionMenuBar()
        self.GetParent().SetMenuBar(self.menubar)
        self.GetParent().Layout()
        self.GetParent().welcomePanel.Show()
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
        
        sizer.AddGrowableCol(1)
        
        hbox.Add(sizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

        self.SetSizer(hbox)
        
# Panel for function toolbar
class functionMenuBar(wx.MenuBar):
    def __init__(self):
    	wx.MenuBar.__init__(self)
    	
        fileMenu = wx.Menu()
        search = wx.MenuItem(fileMenu,wx.ID_ANY, 'Search')
        fileMenu.AppendItem(search)
        self.Bind(wx.EVT_MENU, self.SearchClick, search)
        
        download = wx.MenuItem(fileMenu,wx.ID_ANY, 'Download')
        fileMenu.AppendItem(download)
        self.Bind(wx.EVT_MENU, self.DownloadClick, download)
        
        upload = wx.MenuItem(fileMenu,wx.ID_ANY, 'Upload')
        fileMenu.AppendItem(upload)
        self.Bind(wx.EVT_MENU, self.UploadClick, upload)
        
        delete = wx.MenuItem(fileMenu,wx.ID_ANY, 'Delete')
        fileMenu.AppendItem(delete)
        self.Bind(wx.EVT_MENU, self.DeleteClick, delete)
        
        self.Append(fileMenu, 'File')
        
        userMenu = wx.Menu() 
        change_pass = wx.MenuItem(fileMenu,wx.ID_ANY, 'Change password')
        userMenu.AppendItem(change_pass)
        self.Bind(wx.EVT_MENU, self.Change_passClick, change_pass)
        
        self.Append(userMenu, 'User')
        
    # Individual panels for each function    
    def SearchClick(self,event):
        self.SetSizer(sizer)
    
    def DownloadClick(self,event):
        self.SetSizer(sizer)
    
    def UploadClick(self,event):
        self.SetSizer(sizer)
    
    def DeleteClick(self,event):
        self.SetSizer(sizer)
    
    def Change_passClick(self,event):
        self.GetParent().HideAll()
        self.GetParent().changePassPanel.Show()
        self.GetParent().GetSizer().Layout()

class WelcomePanel(wx.Panel):    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, style=wx.ALIGN_CENTER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Initial message panel
        font = wx.Font(36, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        label = wx.StaticText(self,-1,label=u'Welcome!', size=(300, 40), style=wx.ALIGN_CENTER)
        label.SetForegroundColour(wx.RED)
        label.SetFont(font)
        sizer.Add(label, wx.ALIGN_CENTER )
        
        self.SetSizer(sizer)

## TODO
# class SearchPanel(wx.Panel):
# class UploadPanel(wx.Panel):
# class DownloadPanel(wx.Panel):
# class DeletePanel(wx.Panel):

class ChangePassPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, style=wx.ALIGN_CENTER)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer = wx.GridBagSizer(25,10)
        
        label0 = wx.StaticText(self,-1,label=u'Old Password', style=wx.ALIGN_CENTER)
        sizer.Add(label0, (0,0), (1,1))
        
        text0 = wx.TextCtrl(self, -1)
        sizer.Add(text0, (0,1), (1,1), wx.EXPAND)
        
        label1 = wx.StaticText(self,-1,label=u'New Password', style=wx.ALIGN_CENTER)
        sizer.Add(label1, (1,0), (1,1))
        
        text1 = wx.TextCtrl(self, -1)
        sizer.Add(text1, (1,1), (1,1), wx.EXPAND)
        
        button = wx.Button(self,-1,label="Submit")
        sizer.Add(button, (2,0), (1,2), wx.ALIGN_CENTER)
        #self.Bind(wx.EVT_BUTTON, self.SubmitClick, button)
        
        sizer.AddGrowableCol(1)
        
        hbox.Add(sizer, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)

        self.SetSizer(hbox)
        
    
if __name__ == "__main__":
    app = wx.App()
    frame = simpleapp_wx(None,-1,'Cloud Storage System')
    app.MainLoop()