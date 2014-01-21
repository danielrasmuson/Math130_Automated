import wx, wx.lib.inspection
from assignment import getAssignmentStack

class Frame(wx.Frame):
    def __init__(self):
        self.assignmentStack = getAssignmentStack("Examples\\test")


        # The ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX makes it so
        # the window isn't resizeable so we dont' see horrible things
        # happen to the stuff in the frames.
        wx.Frame.__init__(self, None,title="Math 130 Automated Grading System", pos=(50,50), size=(800,600), style =wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Utility stuff in order to get a menu
        # and a status bar in the bottom for the future.
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit) #binds the event to the menu item
        menuBar.Append(menu, "&File") #add the menu to the menubar
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
        # just blend in. <-- good call
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
        self.lab_tree_list = wx.TreeCtrl(self.mainpanel, 1, size=wx.Size(200,-1),style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT)
        self.lab_tree_list.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)
        self.lab_tree_label = wx.StaticText(self.mainpanel, wx.ID_ANY, 'Student List')
        self.tree_list_sizer.Add(self.lab_tree_label,0,wx.ALIGN_CENTER)
        self.tree_list_sizer.Add(self.lab_tree_list, 1,wx.GROW)
        
        # Call our initial tree list build
        self.updateTreeList(self.lab_tree_list)
        
        
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
        self.questions_area.SetScrollbars(1, 1, 560, 1000)
        self.questions_area.EnableScrolling(True,True)
        self.right_sizer.Add(self.questions_area, 1, wx.GROW)
                
        self.tbutton = wx.Button(self.questions_area, -1, "Scroll Bottom", pos=(0, 0))
        self.tbutton.Bind(wx.EVT_BUTTON, self.ScrollBottom)
        self.bbutton = wx.Button(self.questions_area, -1, "Scroll Top", pos=(470, 900))
        self.bbutton.Bind(wx.EVT_BUTTON, self.ScrollTop)
        
        # These contain all of our buttons along the bottom of the app.
        self.b_open = wx.Button(self.mainpanel, wx.ID_ANY, "Open")
        self.b_open.Bind(wx.EVT_BUTTON, self.ShowInspector)
        self.bottom_button_sizer.Add(self.b_open, 1,wx.ALL,5)
        
        self.b_close = wx.Button(self.mainpanel, wx.ID_CLOSE, "Quit")
        self.b_close.Bind(wx.EVT_BUTTON, self.OnClose)
        self.bottom_button_sizer.Add(self.b_close, 1, wx.ALL, 5)
        
        self.b_prev = wx.Button(self.mainpanel, wx.ID_ANY, "Previous")
        self.b_prev.Bind(wx.EVT_BUTTON, self.PreviousButton)
        self.bottom_button_sizer.Add(self.b_prev, 1,wx.ALL,5)

        self.b_next = wx.Button(self.mainpanel, wx.ID_ANY, "Next")
        self.b_next.Bind(wx.EVT_BUTTON, self.NextButton)
        self.bottom_button_sizer.Add(self.b_next, 1,wx.ALL,5)
        

        
        # This last code just finally sets the main sizer
        # on the main box and calls the layout routine.
        self.mainpanel.SetSizer(self.main_sizer)
        self.mainpanel.Layout()
        
        # I was looking at an easy way to make buttons but it looks like it might be worse
        # than just doing the three lines of code above to get stuff done.
        # self.EasyButtonAdd("test","bottom_button_sizer","Test",border=5)
        # def EasyButtonAdd(self, buttonname, sizer, label, border=0, proportion=0, flags=wx.ALL, function=False):
        # exec("self."+str(buttonname)+" = wx.Button(self.mainpanel, wx.ID_ANY, \""+str(label)+"\")")
        # exec("self."+str(sizer) + ".Add(self."+str(buttonname) + ", "+str(proportion)+", " + str(flags)+","+str(border)+")" )
        # if 

      
    def updateTreeList(self, tree):
        """Tree List on Left Side - Dynamic to Files"""
        tree_root = tree.AddRoot("Lab Sections")
        rootDict = {}
        for assignment in self.assignmentStack:
            sec = assignment.getSection()
            if sec not in rootDict.keys(): #creats root section if there isnt one
                rootDict[sec] = tree.AppendItem(tree_root, "Section "+sec)
            tree.AppendItem(rootDict[sec], assignment.getName()) #appends name onto section

        
    def OnSelChanged(self, event):
        # Get our item that updated
        item = event.GetItem()
        if "Section" not in self.lab_tree_list.GetItemText(item):
            # Find the item text from the tree and update the student information
            self.UpdateStudentInformation(self.lab_tree_list.GetItemText(item), 1234, 8)
            # Eventually update student response questions here:
        
    def UpdateStudentInformation(self, user, techid, section):
        self.student_info_label.SetLabel("Username: " + str(user) + "\nSection: "+str(section) + "\nTech ID: " + str(techid))
        
    def ShowInspector(self, event):
        wx.lib.inspection.InspectionTool().Show()
        
    def PreviousButton(self, event):
        print self.lab_tree_list.GetSelection()

    def NextButton(self, event):
        pass
        
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
        dlg = wx.MessageDialog(self, "Written by Daniel Rasmuson and Gregory Dosh", "About", wx.OK)
        result = dlg.ShowModal()
        dlg.Destroy()
        
if __name__ == "__main__":
    # Error messages go to popup window
    # because of the redirect.
    app = wx.App(redirect=True)
    top = Frame()
    top.Show()
    app.MainLoop()