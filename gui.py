import wx, wx.html
import sys


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
        wx.Frame.__init__(self, None,title="Math 130 Automated Grading System", style =wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX, pos=(50,50), size=(800,600))
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
        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        # m_text = wx.StaticText(panel, -1, "Hello World!")
        # m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        # m_text.SetSize(m_text.GetBestSize())
        # box.Add(m_text, 0, wx.ALL, 10)

        # m_close = wx.Button(panel, wx.ID_CLOSE, "Close")
        # m_close.Bind(wx.EVT_BUTTON, self.OnClose)
        # box.Add(m_close, 1, wx.ALL, 10)

        panel.SetSizer(box)
        panel.Layout()

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