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
        self.mainpanel = wx.Panel(self, wx.ID_ANY)
        self.mainpanel.SetBackgroundColour("red")
        
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bottom_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        tree_list_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(tree_list_sizer,0,wx.ALL|wx.GROW,5)
        top_sizer.Add(right_sizer,0,wx.TOP|wx.BOTTOM|wx.GROW,5)
        
        
        # This is our lab tree list and also the label above it.
        lab_tree_list = wx.TreeCtrl(self.mainpanel, -1, size=wx.Size(200,-1),style=wx.TR_HAS_BUTTONS)
        lab_tree_label = wx.StaticText(self.mainpanel, wx.ID_ANY, 'Lab Sections and Students')
        tree_list_sizer.Add(lab_tree_label,0,wx.ALIGN_CENTER)
        tree_list_sizer.Add(lab_tree_list, 1,wx.GROW)
        
        
        
        # This is the top right of our frame containing the 
        # student ID & the name etc.
        b_open2 = wx.Button(self.mainpanel, wx.ID_ANY, "Open")
        right_sizer.Add(b_open2, 1 ,wx.GROW)
        # top_sizer.Add(right_sizer,1,wx.ALL|wx.GROW, 0)
        # right_sizer.Add(wx.StaticLine(self.mainpanel), 5, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        b_open3 = wx.Button(self.mainpanel, wx.ID_ANY, "Ope66446436346234623462346234623462352352352351452346n")
        right_sizer.Add(b_open3, 5,wx.GROW)
        
        # These contain all of our buttons along the bottom of the app.
        b_open = wx.Button(self.mainpanel, wx.ID_ANY, "Open")
        b_open.Bind(wx.EVT_BUTTON, self.ShowInspector)
        bottom_button_sizer.Add(b_open, 1,wx.ALL,5)
        
        b_close = wx.Button(self.mainpanel, wx.ID_CLOSE, "Quit")
        b_close.Bind(wx.EVT_BUTTON, self.OnClose)
        bottom_button_sizer.Add(b_close, 1, wx.ALL, 5)
        
        b_prev = wx.Button(self.mainpanel, wx.ID_ANY, "Previous")
        bottom_button_sizer.Add(b_prev, 1,wx.ALL,5)

        b_next = wx.Button(self.mainpanel, wx.ID_ANY, "Next")
        bottom_button_sizer.Add(b_next, 1,wx.ALL,5)
        
        
        # This last code just puts our top and bottom sub boxes
        # on the main box so they're aligned correctly.
        main_sizer.Add(top_sizer, wx.GROW)
        main_sizer.Add(wx.StaticLine(self.mainpanel), 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        main_sizer.Add(bottom_button_sizer)
        self.mainpanel.SetSizer(main_sizer)
        self.mainpanel.Layout()
        
    def ShowInspector(self, event):
        wx.lib.inspection.InspectionTool().Show()

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