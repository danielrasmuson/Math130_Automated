import wx, os, time
from assignment import getAssignmentStack
from question_bank import *
from wx.lib.wordwrap import wordwrap

class Frame(wx.Frame):
    qb = Question_Bank()
    initialized = False
    def __init__(self):
        wx.Frame.__init__(self, None,title="Math 130 Automated Grading System", pos=(50,50), size=(800,600), style =wx.DEFAULT_FRAME_STYLE)
        self.SetMinSize((800,600))

        self.buildMenuNav()

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
        self.lab_tree_list.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelChanged, id=1)
        self.lab_tree_label = wx.StaticText(self.mainpanel, wx.ID_ANY, 'Student List')
        self.tree_list_sizer.Add(self.lab_tree_label,0,wx.ALIGN_CENTER)
        self.tree_list_sizer.Add(self.lab_tree_list, 1,wx.GROW)
        self.tree_root = self.lab_tree_list.AddRoot("Lab Sections")
        self.tree_rootDict = {}

        # This is the right frame containing the
        # student ID & the name etc.
        title = wx.StaticText(self.mainpanel, wx.ID_ANY, label="Math 130 Automated Grading System")
        titlefont = wx.Font(18,wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        title.SetFont(titlefont)
        self.right_sizer.Add(title, proportion=0, flag=wx.ALIGN_CENTER, border=0)
        
        si_sizer = wx.GridBagSizer(5, 5)
        si_sizer.Add(wx.StaticText(self.mainpanel, label="Student:"), pos=(0, 0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)
        si_sizer.Add(wx.StaticText(self.mainpanel, label="Section:"), pos=(1, 0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)
        si_sizer.Add(wx.StaticText(self.mainpanel, label="Questions Right:"), pos=(0, 3), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)
        si_sizer.Add(wx.StaticText(self.mainpanel, label="Questions Wrong:"), pos=(1, 3), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)
        
        self.si_name = wx.TextCtrl(self.mainpanel, value="")
        self.si_section = wx.TextCtrl(self.mainpanel, value="")
        self.si_right = wx.TextCtrl(self.mainpanel, value="")
        self.si_wrong = wx.TextCtrl(self.mainpanel, value="")
        
        si_sizer.Add(self.si_name, pos=(0, 1), flag=wx.ALL, border=0)
        si_sizer.Add(self.si_section, pos=(1, 1), flag=wx.ALL, border=0)
        si_sizer.Add(self.si_right, pos=(0, 4), flag=wx.ALL, border=0)
        si_sizer.Add(self.si_wrong, pos=(1, 4), flag=wx.ALL, border=0)
        
        si_sizer.AddGrowableCol(2)
        self.right_sizer.Add(si_sizer, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
        self.right_sizer.Add(wx.StaticLine(self.mainpanel, wx.ID_ANY), 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        
        # This last code just finally sets the main sizer
        # on the main box and calls the layout routine.
        self.buildBottomNav(self.mainpanel,self.bottom_button_sizer)
        
        self.mainpanel.SetSizer(self.main_sizer)
        self.mainpanel.Layout()
        
    def buildMenuNav(self):
        ''' Builds the menu bar, status bar, and the associated
        functions required for these things to work including loading
        questions and also selecting folders/directories.'''
        def onClose(event):
            dlg = wx.MessageDialog(self,
                "Do you really want to close this application?",
                "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                self.Destroy()
                
        def loadBank(event):
            dlg = wx.FileDialog(self, "Choose a lab file:",defaultFile="lab1.dat",defaultDir=os.getcwd(), style=wx.FD_OPEN)
            dlg.SetWildcard("Lab Dictionaries (*.dat)|*.dat")
            if dlg.ShowModal() == wx.ID_OK:
                self.qb.load(dlg.GetPath())
                try:
                    self.questions_area.Destroy()
                except:
                    pass
                self.initializeQuestionArea()
            dlg.Destroy()

        def onOpen(event):
            # I get the current working directory + the examples test stuff
            # so that while testing it'll default to our test directory.
            # Later we can navigate anywhere we want and cut that part.
            dlg = wx.DirDialog(self, "Choose a directory:",os.getcwd()+"\\Examples\\test")
            if dlg.ShowModal() == wx.ID_OK:
                self.assignmentStack = getAssignmentStack(dlg.GetPath())
                # Call our initial tree list build
                self.updateTreeList(self.lab_tree_list)
            dlg.Destroy()
            self.lab_tree_list.SelectItem(self.lab_tree_list.GetFirstVisibleItem())

        def onAbout(event):
            dlg = wx.MessageDialog(self, "Written by Daniel Rasmuson and Gregory Dosh", "About", wx.OK)
            result = dlg.ShowModal()
            dlg.Destroy()

        self.Bind(wx.EVT_CLOSE, onClose)
        # Utility stuff in order to get a menu
        # and a status bar in the bottom for the future.
        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        m_open = fileMenu.Append(wx.OPEN, "&Open Document Directory\tAlt-O", "Select the directory containing the student documents.")
        m_load = fileMenu.Append(wx.ID_ANY, "&Load Question Bank\tAlt-L", "Load's a new question bank for grading purposes.")
        m_exit = fileMenu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, onOpen, m_open)
        self.Bind(wx.EVT_MENU, loadBank, m_load)
        self.Bind(wx.EVT_MENU, onClose, m_exit)
        menuBar.Append(fileMenu, "&File")

        helpMenu = wx.Menu()
        m_about = helpMenu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, onAbout, m_about)
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)
        
        self.statusbar = self.CreateStatusBar()

    def buildBottomNav(self, panel, sizer):
        '''Builds a predefined set of buttons on a specific panel
         and utilizing the sizer provided'''
        def openDocument(event):
            current_item = self.lab_tree_list.GetItemText(self.lab_tree_list.GetSelection())
            if "Section" not in current_item:
                print "start \""+self.assignmentStack[current_item].getStudentFilepath()+"\""
                os.system("\""+self.assignmentStack[current_item].getStudentFilepath()+"\"")
        b_prev = wx.Button(panel, wx.ID_ANY, "Previous")
        b_prev.SetToolTipString("Selects the previous student of the current section.")
        b_prev.Bind(wx.EVT_BUTTON, self.previousButton)
        sizer.Add(b_prev, 0,wx.ALL,5)

        b_next = wx.Button(panel, wx.ID_ANY, "Next")
        b_next.SetToolTipString("Selects the next student of the current section")
        b_next.Bind(wx.EVT_BUTTON, self.nextButton)
        sizer.Add(b_next, 0,wx.ALL,5)

        sizer.Add(wx.BoxSizer(wx.HORIZONTAL), 1, wx.GROW, 0)

        # I was a little confused by open so I added Document
        b_open = wx.Button(panel, wx.ID_ANY, "Open Document") #works great
        b_open.SetToolTipString("Opens the Document Inspector (for now).")
        b_open.Bind(wx.EVT_BUTTON, openDocument)
        sizer.Add(b_open, 0,wx.ALL,5)
        
    def updateTreeList(self, tree):
        """Tree List on Left Side - Dynamic to Files"""
        for name in self.assignmentStack.keys():
            sec = self.assignmentStack[name].getSection()
            if sec == "MissingInformation":
                self.tree_rootDict[sec] = tree.AppendItem(self.tree_root, "Missing Lab Section")
                self.lab_tree_list.SetItemBackgroundColour(self.tree_rootDict[sec],"#FFAAAA")
            elif sec not in self.tree_rootDict.keys(): #creates root section if there isn't one
                self.tree_rootDict[sec] = tree.AppendItem(self.tree_root, "Section "+sec)
            tree.AppendItem(self.tree_rootDict[sec], name) #appends name onto section

    def onSelChanged(self, event):
        # Get our item that updated
        item = event.GetItem()
        if "Section" not in self.lab_tree_list.GetItemText(item):
            name = self.lab_tree_list.GetItemText(item)
            section = self.assignmentStack[name].getSection()
            # # @TODO get tech id
            self.updateStudentInformation(name, section, "Unknown")
            if self.initialized:
                self.updateQuestions(name)

    def updateStudentInformation(self, name, section, techid):
        self.si_name.SetValue(name)
        self.si_section.SetValue(section)
        self.si_right.SetValue("")
        self.si_wrong.SetValue("")

    def previousButton(self, event):
        current = self.lab_tree_list.GetSelection()
        prev = self.lab_tree_list.GetPrevSibling(current)
        if prev.IsOk() and not self.lab_tree_list.ItemHasChildren(prev):
            self.lab_tree_list.SelectItem(prev)
        elif prev.IsOk() and  self.lab_tree_list.ItemHasChildren(prev):
            self.lab_tree_list.SelectItem(self.lab_tree_list.GetLastChild(prev))
        else:
            parent = self.lab_tree_list.GetItemParent(self.lab_tree_list.GetSelection())
            if parent != self.lab_tree_list.GetRootItem():
                self.lab_tree_list.SelectItem(parent)

    def nextButton(self, event):
        current = self.lab_tree_list.GetSelection()
        if self.lab_tree_list.ItemHasChildren(current):
            next = self.lab_tree_list.GetFirstChild(current)[0]
        else:
            next = self.lab_tree_list.GetNextSibling(current)
        if next.IsOk():
            self.lab_tree_list.SelectItem(next)
        else:
            parent = self.lab_tree_list.GetItemParent(self.lab_tree_list.GetSelection())
            if self.lab_tree_list.GetNextSibling(parent).IsOk():
                self.lab_tree_list.SelectItem(self.lab_tree_list.GetNextSibling(parent))
                
    def initializeQuestionArea(self):
        self.questions_area = wx.ScrolledWindow(self.mainpanel)
        self.questions_area.SetScrollbars(1, 1, 650, 1000)
        self.questions_area.EnableScrolling(True,True)
        self.right_sizer.Add(self.questions_area, 1, wx.GROW)

        self.questions_area_sizer = wx.BoxSizer(wx.VERTICAL)
        self.questions_area.SetSizer(self.questions_area_sizer)

        self.student_answer_boxes = {}

        for qNum in self.qb.getQuestionsDict().keys():
            label = wx.StaticText(self.questions_area, wx.ID_ANY, "Question "+str(qNum) + ":\n"+ str(wordwrap(self.qb.getQuestionsDict()[qNum]["question"]+" "+str(self.qb.getQuestionsDict()[qNum]["answer"]), self.questions_area.GetVirtualSize()[0], wx.ClientDC(self.questions_area))) )
            self.questions_area_sizer.Add(label)

            q_sizer = wx.BoxSizer(wx.HORIZONTAL)

            student_answer = wx.TextCtrl(self.questions_area, wx.ID_ANY, style=wx.TE_READONLY, value="" )
            self.student_answer_boxes[qNum] = student_answer

            q_sizer.Add(student_answer, 1, wx.GROW|wx.TOP|wx.RIGHT, 5)
            self.questions_area_sizer.Add(q_sizer, 0, wx.GROW)
            if qNum != self.qb.getQuestionsDict().keys()[-1]:
                self.questions_area_sizer.Add(wx.StaticLine(self.questions_area, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)

        # I've got this initialized variable here to keep track
        # of whether we should warn about loading the question bank
        # when trying to select a student's responses.
        self.initialized = True
        self.mainpanel.Layout()

    def updateQuestions(self, name):
        # This gets our students answers and the dictionary we're comparing their answer to.
        # Yep I was going to tell you to pass in the name variable. That speeds things up
        studentQD = self.assignmentStack[name].getStudentDictionary()
        right = 0
        wrong = 0
        for qNum in studentQD.keys():
            self.student_answer_boxes[qNum].SetLabel(studentQD[qNum])

            #I changed this to not in because then it can verify more answers
            if str(self.qb.getQuestionsDict()[qNum]['answer']) not in str(studentQD[qNum]):
                self.student_answer_boxes[qNum].SetBackgroundColour("#FFAAAA")
                wrong += 1
            else:
                #Change 'NullColor' to Grey because I was getting errors
                self.student_answer_boxes[qNum].SetBackgroundColour("#FFFFFF")
                right += 1
        self.si_right.SetValue(str(right))
        self.si_wrong.SetValue(str(wrong))

if __name__ == "__main__":
    # Error messages go to pop-up window
    # because of the redirect=True.
    app = wx.App(redirect=False)
    top = Frame()
    top.Show()
    app.MainLoop()
