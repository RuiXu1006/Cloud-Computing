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
        self.sizer = wx.GridBagSizer()
        # Top panel
        self.mainPanel = wx.Panel(self, -1)
        # Panel for function toolbar (left side)
        self.functionPanel = wx.Panel(self, -1)
        # Panel for each function (right side)
        self.displayPanel = wx.Panel(self, -1)
        
        # Sign up or login process
        self.LoginPanel()
        self.sizer.Add(self.mainPanel, (0,0), (1,1), wx.ALIGN_CENTER)
        
        self.SetSizerAndFit(self.sizer)
        self.Show(True)

	# Panel for sign up or login
    def LoginPanel(self):
    	panel = wx.Panel(self, -1, size=(200, 100), style=wx.ALIGN_CENTER)
    	sizer = wx.BoxSizer(wx.VERTICAL)
    	
    	# Sign up
    	sign_up = wx.Button(self,-1,label="Sign up", size=(150,20))
        sizer.Add(sign_up, 1, wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.Sign_upClick, sign_up)
        
    	# Log in
    	log_in = wx.Button(self,-1,label="Log in", size=(150,20))
        sizer.Add(log_in, 2, wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.Log_inClick, log_in)
        
        panel.SetSizer(sizer)
        panel.Layout()
        self.mainPanel = panel;
        
    # Panel for function toolbar
    def FunctionPanel(self):
    	panel = wx.Panel(self, -1, size=(400, 200))
    	sizer = wx.BoxSizer(wx.VERTICAL)
    	
        # Function buttons
        search = wx.Button(self,-1,label="Search", size=(150,20))
        sizer.Add(search, 0)
        self.Bind(wx.EVT_BUTTON, self.SearchClick, search)
        
        download = wx.Button(self,-1,label="Downlaod", size=(150,20))
        sizer.Add(download, 1)
        self.Bind(wx.EVT_BUTTON, self.DownloadClick, download)
        
        upload = wx.Button(self,-1,label="Upload", size=(150,20))
        sizer.Add(upload, 2)
        self.Bind(wx.EVT_BUTTON, self.UploadClick, upload)
        
        delete = wx.Button(self,-1,label="Delete", size=(150,20))
        sizer.Add(delete, 3)
        self.Bind(wx.EVT_BUTTON, self.DeleteClick, delete)
         
        change_pass = wx.Button(self,-1,label="Change password", size=(150,20))
        sizer.Add(change_pass, 4)
        self.Bind(wx.EVT_BUTTON, self.Change_passClick, change_pass)
        
        panel.SetSizer(sizer)
        panel.Layout()
        self.functionPanel = panel;
    
    def InitialPanel(self):
        panel = wx.Panel(self, -1, size=(250, 200))
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Initial message panel
        label = wx.StaticText(self,-1,label=u'Welcome!', size=(250, 200), style=wx.ALIGN_CENTER)
        label.SetForegroundColour(wx.RED)
        sizer.Add( self.label, wx.ALIGN_CENTER )
        
        panel.SetSizer(sizer)
        panel.Layout()
        self.displayPanel = panel;

    # Individual panels for each function
    def Log_inClick(self,event):
        self.Show(False)
        self.Show(True)
    
    def SearchClick(self,event):
        self.label.SetLabel( "Search process" )
    
    def DownloadClick(self,event):
        self.label.SetLabel( "Download process" )
    
    def UploadClick(self,event):
        self.label.SetLabel( "Upload process" )
    
    def DeleteClick(self,event):
        self.label.SetLabel( "Delete process" )
    
    def Sign_upClick(self,event):
        self.label.SetLabel( "Sign up process" )
    
    def Change_passClick(self,event):
        self.label.SetLabel( "Change password process" )
    
    

if __name__ == "__main__":
    app = wx.App()
    frame = simpleapp_wx(None,-1,'Cloud Storage')
    app.MainLoop()