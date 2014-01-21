import wx, wx.lib.inspection
from assignment import getAssignmentStack
from question_bank import *

class Frame(wx.Frame):
    def __init__(self):
        # The ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX makes it so
        # the window isn't resizeable so we dont' see horrible things
        # happen to the stuff in the frames.
        wx.Frame.__init__(self, None,title="Math 130 Automated Grading System", pos=(50,50), size=(800,600), style =wx.DEFAULT_FRAME_STYLE)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.assignmentStack = getAssignmentStack("Examples\\test")

        # Utility stuff in order to get a menu
        # and a status bar in the bottom for the future.
        menuBar = wx.MenuBar()

        menu = wx.Menu()
        m_open = menu.Append(wx.ID_ANY, "&Load Question Bank\tAlt-L", "Load's a new question bank for grading purposes.")
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.LoadBank, m_open)
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

        # Set all of our sizers here
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bottom_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tree_list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)


        # This is our outer most sizer and its components.
        self.main_sizer.Add(self.top_sizer, 1, wx.GROW)
        self.main_sizer.Add(wx.StaticLine(self.mainpanel), 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        self.main_sizer.Add(self.bottom_button_sizer, 0, wx.GROW)


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
        self.student_info_label = wx.StaticText(self.mainpanel, wx.ID_ANY) #'Username: Anthony Anderson\nSection: 5\nTech ID: 123456789'
        self.student_info_container_sizer.Add(self.student_info_label)
        self.right_sizer.Add(self.student_info_container_sizer, 0 , wx.BOTTOM|wx.GROW,5)



        # self.tbutton = wx.Button(self.questions_area, -1, "Scroll Bottom", pos=(0, 0))
        # self.tbutton.Bind(wx.EVT_BUTTON, self.ScrollBottom)
        # self.bbutton = wx.Button(self.questions_area, -1, "Scroll Top", pos=(470, 900))
        # self.bbutton.Bind(wx.EVT_BUTTON, self.ScrollTop)

        # These contain all of our buttons along the bottom of the app.
        self.b_prev = wx.Button(self.mainpanel, wx.ID_ANY, "Previous")
        self.b_prev.SetToolTipString("Selects the previous student of the current section.")
        self.b_prev.Bind(wx.EVT_BUTTON, self.PreviousButton)
        self.bottom_button_sizer.Add(self.b_prev, 0,wx.ALL,5)

        self.b_next = wx.Button(self.mainpanel, wx.ID_ANY, "Next")
        self.b_next.SetToolTipString("Selects the next student of the current section")
        self.b_next.Bind(wx.EVT_BUTTON, self.NextButton)
        self.bottom_button_sizer.Add(self.b_next, 0,wx.ALL,5)

        self.bottom_button_sizer.Add(wx.BoxSizer(wx.HORIZONTAL), 1, wx.GROW, 0)

        self.b_open = wx.Button(self.mainpanel, wx.ID_ANY, "Open")
        self.b_open.SetToolTipString("Opens the Document Inspector (for now).")
        self.b_open.Bind(wx.EVT_BUTTON, self.ShowInspector)
        self.bottom_button_sizer.Add(self.b_open, 0,wx.ALL,5)

        self.b_close = wx.Button(self.mainpanel, wx.ID_CLOSE, "Quit")
        self.b_close.SetToolTipString("Quits the application.")
        self.b_close.Bind(wx.EVT_BUTTON, self.OnClose)
        self.bottom_button_sizer.Add(self.b_close, 0, wx.ALL, 5)

        # This is the hardest part.  This is where the
        # questions and the scrollable area is going to be.
        self.qb = Question_Bank()
        self.InitializeQuestionArea()

        # This last code just finally sets the main sizer
        # on the main box and calls the layout routine.
        self.mainpanel.SetSizer(self.main_sizer)
        self.mainpanel.Layout()

    def updateTreeList(self, tree):
        """Tree List on Left Side - Dynamic to Files"""
        tree_root = tree.AddRoot("Lab Sections")
        rootDict = {}
        for assignment in self.assignmentStack:
            sec = assignment.getSection()
            if sec not in rootDict.keys(): #creats root section if there isnt one
                rootDict[sec] = tree.AppendItem(tree_root, "Section "+sec)
            tree.AppendItem(rootDict[sec], assignment.getName()) #appends name onto section

        tree.ExpandAll()


    def OnSelChanged(self, event):
        # Get our item that updated
        item = event.GetItem()
        if "Section" not in self.lab_tree_list.GetItemText(item):
            # Find the item text from the tree and update the student information
            name = self.lab_tree_list.GetItemText(item)
            section = ""
            for assignment in self.assignmentStack:
                if assignment.getName() == name:
                    section = assignment.getSection()
            # # @TODO get tech id
            self.UpdateStudentInformation(name, section, 1234)
            self.UpdateQuestions(name)

    def UpdateStudentInformation(self, name, section, techid):
        self.student_info_label.SetLabel("Name: " + str(name) + "\nSection: "+str(section) + "\nTech ID: " + str(techid))

    def ShowInspector(self, event):
        wx.lib.inspection.InspectionTool().Show()

    def PreviousButton(self, event):
        current = self.lab_tree_list.GetSelection()
        prev = self.lab_tree_list.GetPrevSibling(current)
        if prev.IsOk():
            self.lab_tree_list.SelectItem(prev)

    def NextButton(self, event):
        current = self.lab_tree_list.GetSelection()
        next = self.lab_tree_list.GetNextSibling(current)
        if next.IsOk():
            self.lab_tree_list.SelectItem(next)

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

    def LoadBank(self, event):
        # The self.qb_load() here will allow
        # us to load the question bank before updating
        # the drawing area to include the information.
        # self.qb.load()
        if self.questions_area:
            self.questions_area.Destroy()

    def InitializeQuestionArea(self):
        self.questions_area = wx.ScrolledWindow(self.mainpanel)
        self.questions_area.SetScrollbars(1, 1, 560, 1000)
        self.questions_area.EnableScrolling(True,True)
        self.right_sizer.Add(self.questions_area, 1, wx.GROW)

        self.questions_area_sizer = wx.BoxSizer(wx.VERTICAL)
        self.questions_area.SetSizer(self.questions_area_sizer)

        # self.UpdateQuestions()
        self.mainpanel.Layout()

    def UpdateQuestions(self, name):
        # This is just a temporary test to see if I can dynamically add things
        # and it appears to work.  Next we need to actually get the student answers.

        # see what name the information box is currently displaying and shows that student
        # this requires that the infromation box be created prior to this
        for assignment in self.assignmentStack:
            print assignment.getStudentDictionary()
            if assignment.getName() == name:
                studentQD = assignment.getStudentDictionary()
                # print name
                # print studentQD

        # studentQD = self.assignmentStack[0].getStudentDictionary()
        for question in studentQD.keys():
            label = wx.StaticText(self.questions_area, wx.ID_ANY, "Question "+str(question) + ":\n"+ str(studentQD[question]['question']) )
            self.questions_area_sizer.Add(label)
            answerbox = wx.TextCtrl(self.questions_area, wx.ID_ANY, str(studentQD[question]['answer']) )
            self.questions_area_sizer.Add(answerbox)
            answerbox2 = wx.TextCtrl(self.questions_area, wx.ID_ANY, str(studentQD[question]['sAnswer']) )
            self.questions_area_sizer.Add(answerbox2)


    def OnAbout(self, event):
        dlg = wx.MessageDialog(self, "Written by Daniel Rasmuson and Gregory Dosh", "About", wx.OK)
        result = dlg.ShowModal()
        dlg.Destroy()

if __name__ == "__main__":
    # Error messages go to popup window
    # because of the redirect=True.
    app = wx.App(redirect=False)
    top = Frame()
    top.Show()
    app.MainLoop()