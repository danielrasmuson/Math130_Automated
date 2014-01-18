import wx, wx.html
import sys
import wx.lib.inspection

# This was taken from somewhere, I can't recall where though.
class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600,400)):
        wx.html.HtmlWindow.__init__(self,parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())
# This was taken from somewhere, I can't recall where though.
class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "About <<project>>",
            style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|
                wx.TAB_TRAVERSAL)
        aboutText = """<p>Sorry, there is no information about this program. It is
        running on version %(wxpy)s of <b>wxPython</b> and %(python)s of <b>Python</b>.
        See <a href="http://wiki.wxpython.org">wxPython Wiki</a></p>"""
        hwin = HtmlWindow(self, -1, size=(400,500))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        hwin.SetPage(aboutText % vers)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+25))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()

class Frame(wx.Frame):
    def __init__(self):
        # The ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX makes it so
        # the window isn't resizeable so we dont' see horrible things
        # happen to the stuff in the frames.
        wx.Frame.__init__(self, None,title="Math 130 Automated Grading System", pos=(50,50), size=(800,600))#, style =wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Utility stuff in order to get a menu
        # and a status bar in the bottom for the future.
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")
        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)

        # Style=0 makes it so no resize handle shows up
        # in the status bar
        self.statusbar = self.CreateStatusBar(style=0)

        
        
        # We need a panel in order to put stuff on
        # and then we are adding the things we want to see on this panel.
        # I made this red at first so that I can see exactly where things
        # are positioned and if they're even being rendered since they ususally
        # just blend in.
        self.mainpanel = wx.Panel(self, wx.ID_ANY)
        self.mainpanel.SetBackgroundColour("red")
        
        # Set all of our sizers here
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bottom_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tree_list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        
        # This is our outer most sizer and its components.
        self.main_sizer.Add(self.top_sizer, 1, wx.GROW)
        self.main_sizer.Add(wx.StaticLine(self.mainpanel), 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        self.main_sizer.Add(self.bottom_button_sizer, 0)
        
        
        # Our top sizer contains the left hand tree list and
        # the right hand side list for the student information
        # and the questions eventually.
        self.top_sizer.Add(self.tree_list_sizer,0,wx.ALL|wx.GROW,5)
        self.top_sizer.Add(self.right_sizer,1,wx.TOP|wx.BOTTOM|wx.RIGHT|wx.GROW,5)
        
        # This is our lab tree list and also the label above it.
        self.lab_tree_list = wx.TreeCtrl(self.mainpanel, -1, size=wx.Size(200,-1),style=wx.TR_HAS_BUTTONS)
        self.lab_tree_label = wx.StaticText(self.mainpanel, wx.ID_ANY, 'Lab Sections and Students')
        self.tree_list_sizer.Add(self.lab_tree_label,0,wx.ALIGN_CENTER)
        self.tree_list_sizer.Add(self.lab_tree_list, 1,wx.GROW)
        
        
        
        
        # This is the right frame containing the 
        # student ID & the name etc.
        self.student_info_container = wx.StaticBox(self.mainpanel, label='Current Student Information')
        self.student_info_container_sizer = wx.StaticBoxSizer(self.student_info_container, wx.VERTICAL)
        self.student_info_label = wx.StaticText(self.mainpanel, wx.ID_ANY, 'Username: Anthony Anderson\nSection: 5\nTech ID: 123456789')
        self.student_info_container_sizer.Add(self.student_info_label)
        self.right_sizer.Add(self.student_info_container_sizer, 0 , wx.BOTTOM|wx.GROW,5)
        

        # This is the hardest part.  This is where the
        # questions and the scrollable area is going to be.
        self.questions_area = wx.ScrolledWindow(self.mainpanel)
        self.questions_area.SetScrollbars(1, 1, 1000, 1000)
        self.questions_area.EnableScrolling(True,True)
        self.right_sizer.Add(self.questions_area, 1, wx.GROW)
                
        self.tbutton = wx.Button(self.questions_area, -1, "Scroll Bottom", pos=(0, 0))
        self.tbutton.Bind(wx.EVT_BUTTON, self.ScrollBottom)
        self.bbutton = wx.Button(self.questions_area, -1, "Scroll Top", pos=(900, 900))
        self.bbutton.Bind(wx.EVT_BUTTON, self.ScrollTop)
        
        
        
        
        
        # These contain all of our buttons along the bottom of the app.
        self.b_open = wx.Button(self.mainpanel, wx.ID_ANY, "Open")
        self.b_open.Bind(wx.EVT_BUTTON, self.ShowInspector)
        self.bottom_button_sizer.Add(self.b_open, 1,wx.ALL,5)
        
        self.b_close = wx.Button(self.mainpanel, wx.ID_CLOSE, "Quit")
        self.b_close.Bind(wx.EVT_BUTTON, self.OnClose)
        self.bottom_button_sizer.Add(self.b_close, 1, wx.ALL, 5)
        
        self.b_prev = wx.Button(self.mainpanel, wx.ID_ANY, "Previous")
        self.bottom_button_sizer.Add(self.b_prev, 1,wx.ALL,5)

        self.b_next = wx.Button(self.mainpanel, wx.ID_ANY, "Next")
        self.bottom_button_sizer.Add(self.b_next, 1,wx.ALL,5)

        
        # This last code just finally sets the main sizer
        # on the main box and calls the layout routine.
        self.mainpanel.SetSizer(self.main_sizer)
        self.mainpanel.Layout()
        
    def ShowInspector(self, event):
        wx.lib.inspection.InspectionTool().Show()
        
    def ScrollTop(self,event):
        self.questions_area.Scroll(1,1)
        
    def ScrollBottom(self,event):
        self.questions_area.Scroll(1000,1000)
        
    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()
        
if __name__ == "__main__":
    # Error messages go to popup window
    # because of the redirect.
    app = wx.App(redirect=True)
    top = Frame()
    top.Show()
    app.MainLoop()