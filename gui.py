from __future__ import division
import wx, os, time
from assignment import getAssignmentStack
from question_bank import *
from wx.lib.wordwrap import wordwrap
from toImportDocument import sendToImport

class EquationsBrowser(wx.Frame):
    def __init__(self, parent, initialPosition, initialSize):
        wx.Frame.__init__(self, parent, title='Equation Browser', pos=initialPosition, size=initialSize)
        self.panel = wx.Panel(self)
        self.parent = parent

        def onClose(event):
            self.Hide()
        self.Bind(wx.EVT_CLOSE, onClose)

        self.createEquations()

    def createEquations(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self.panel, wx.ID_ANY, label="Equations Browser")
        titlefont = wx.Font(18,wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        title.SetFont(titlefont)
        sizer.Add(title, proportion=0, flag=wx.ALIGN_CENTER, border=0)

        self.parent.si_misc = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE, value="")
        sizer.Add(self.parent.si_misc, 1, flag=wx.ALL|wx.GROW, border=0)

        self.panel.SetSizer(sizer)
        self.Layout()


class MainApp(wx.Frame):
    qb = Question_Bank()
    initialized = False
    def __init__(self):
        wx.Frame.__init__(self, None,title="Math 130 Automated Grading System", pos=(50,50), size=(800,600), style =wx.DEFAULT_FRAME_STYLE)
        self.eq_frame = EquationsBrowser(self, initialSize=(500,500),initialPosition=(0,0))
        self.SetMinSize((800,600))

        self.buildMenuNav()
        # We need a panel in order to put stuff on
        # and then we are adding the things we want to see on this panel.
        self.mainpanel = wx.Panel(self, wx.ID_ANY)

        # Define most of our main sizers here
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer_a = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer_b = wx.BoxSizer(wx.HORIZONTAL)
        self.tree_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Set up the first layer of sizers for the top and
        # bottom panels separated by a line.
        self.main_sizer.Add(self.main_sizer_a, 1, wx.EXPAND)
        self.main_sizer.Add(wx.StaticLine(self.mainpanel), 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        self.main_sizer.Add(self.main_sizer_b, 0, wx.EXPAND)

        # Our top sizer contains the left hand tree list and
        # the right hand side list for the student information
        self.main_sizer_a.Add(self.tree_sizer,0,wx.ALL|wx.EXPAND,5)
        self.main_sizer_a.Add(self.right_sizer,1,wx.TOP|wx.BOTTOM|wx.RIGHT|wx.EXPAND,5)

        # Now we call the routines to build the main content
        self.buildTreeNav(self.mainpanel, self.tree_sizer)
        self.buildRightQuestionsArea(self.mainpanel, self.right_sizer)
        self.buildBottomNav(self.mainpanel,self.main_sizer_b)

        self.mainpanel.SetSizer(self.main_sizer)
        self.mainpanel.Layout()

    def buildMenuNav(self):
        """ Builds the menu bar, status bar, and the associated
        functions required for these things to work including loading
        questions and also selecting folders/directories."""
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

        def loadImportFile(event):
            """The user finds the template import file
            downloaded from d2l and then the program will
            fill in the values."""
            dlg = wx.FileDialog(self, "Choose an import file:",defaultDir=os.getcwd(), style=wx.FD_OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self.importFilePath = dlg.GetPath()
            dlg.Destroy()

        def onAbout(event):
            dlg = wx.MessageDialog(self, "Written by Daniel Rasmuson and Gregory Dosh", "About", wx.OK)
            result = dlg.ShowModal()
            dlg.Destroy()

        def onClose(event):
            dlg = wx.MessageDialog(self,
                "Do you really want to close this application?",
                "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                self.Destroy()

        def onNew(event):
            dlg = wx.MessageDialog(self,
                "Do you want to clear everything and start a new session?",
                "Confirm New", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                self.Show(False)
                newSession()
                self.Destroy()

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

        self.Bind(wx.EVT_CLOSE, onClose)

        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        m_new = fileMenu.Append(wx.ID_NEW, "&New Grading Session\tAlt-N", "Removes all of the students and the currently loaded dictionary.")
        m_open = fileMenu.Append(wx.ID_OPEN, "&Open Document Directory\tAlt-O", "Select the directory containing the student documents.")
        m_load = fileMenu.Append(wx.ID_ANY, "&Load Question Bank\tAlt-L", "Load's a new question bank for grading purposes.")
        m_import = fileMenu.Append(wx.ID_ANY, "&Load Import Template\tAlt-I", "will write grades to this document for later import.")
        fileMenu.AppendSeparator()
        m_exit = fileMenu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, onNew, m_new)
        self.Bind(wx.EVT_MENU, onOpen, m_open)
        self.Bind(wx.EVT_MENU, loadBank, m_load)
        self.Bind(wx.EVT_MENU, loadImportFile, m_import)
        self.Bind(wx.EVT_MENU, onClose, m_exit)
        menuBar.Append(fileMenu, "&File")

        helpMenu = wx.Menu()
        m_about = helpMenu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, onAbout, m_about)
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)

        self.statusbar = self.CreateStatusBar()

    def buildBottomNav(self, panel, sizer):
        """Builds a predefined set of buttons on a specific panel
         and utilizing the sizer provided"""
        def openDocument(event):
            current_item = self.lab_tree_list.GetItemText(self.lab_tree_list.GetSelection())
            if "Section" not in current_item:
                os.system("\""+self.assignmentStack[current_item].getStudentFilepath()+"\"")

        def previousButton(event):
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

        def nextButton(event):
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

        def sendGrade(event):
            # Do you know how to do complete this first check greg?
            # @TODO: when you change the value of the score box in the gui it needs change the value of the variable
            # @TODO: Hoping to add \xe2 to the start of tree names if sendGrade has been executed
            # @TODO: right answers should be divided by the total score (30 points)
            # @TODO: wont work if they have more then 2 word name
            name = self.si_name.GetValue().split()
            score = self.si_score.GetValue()
            sendToImport(self.importFilePath, name[0], name[1], score)


        b_prev = wx.Button(panel, wx.ID_ANY, "Previous")
        b_prev.SetToolTipString("Selects the previous student of the current section.")
        b_prev.Bind(wx.EVT_BUTTON, previousButton)
        sizer.Add(b_prev, 0,wx.ALL,5)

        b_next = wx.Button(panel, wx.ID_ANY, "Next")
        b_next.SetToolTipString("Selects the next student of the current section")
        b_next.Bind(wx.EVT_BUTTON, nextButton)
        sizer.Add(b_next, 0,wx.ALL,5)

        sizer.Add(wx.BoxSizer(wx.HORIZONTAL), 1, wx.EXPAND, 0)

        self.b_equations = wx.Button(panel, wx.ID_ANY, "Equations")
        self.b_equations.Disable()
        self.b_equations.SetToolTipString("Opens a new dialog box with extra equations (if available) for the current student.")
        self.b_equations.Bind(wx.EVT_BUTTON, self.equationsBrowser)
        sizer.Add(self.b_equations, 0,wx.ALL,5)

        b_open = wx.Button(panel, wx.ID_ANY, "Open Document")
        b_open.SetToolTipString("Opens the document in word.")
        b_open.Bind(wx.EVT_BUTTON, openDocument)
        sizer.Add(b_open, 0,wx.ALL,5)

        # A button for sending the grade to the excel file
        b_grade = wx.Button(panel, wx.ID_ANY, "Submit Grade")
        b_grade.SetToolTipString("Sends the grade to excel file")
        b_grade.Bind(wx.EVT_BUTTON, sendGrade)
        sizer.Add(b_grade, 0,wx.ALL,5)

    def equationsBrowser(self, event):
        w,h = self.GetSizeTuple()
        x,y = self.GetPositionTuple()
        self.eq_frame.SetPosition((w+x,y))
        self.eq_frame.Show()
        self.eq_frame.Raise()

    def buildTreeNav(self, panel, sizer):
        """ Builds our tree list of students """
        def onSelChanged(event):
            # Get our item that updated
            item = event.GetItem()
            if "Section" not in self.lab_tree_list.GetItemText(item):
                name = self.lab_tree_list.GetItemText(item)
                section = self.assignmentStack[name].getSection()
                self.updateStudentInformation(name, section)
                uni_str = u""
                for number, line in enumerate(self.assignmentStack[name].getMisc()):
                    uni_str += u"Equation #"+unicode(number)+u" "+line+u"\n"
                self.si_misc.ChangeValue(unicode(uni_str))
                if self.initialized:
                    self.updateQuestions(name)
        self.lab_tree_list = wx.TreeCtrl(panel, 1, size=wx.Size(200,-1),style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT)
        self.lab_tree_list.Bind(wx.EVT_TREE_SEL_CHANGED, onSelChanged, id=1)
        lab_tree_label = wx.StaticText(panel, wx.ID_ANY, 'Student List')
        sizer.Add(lab_tree_label,0,wx.ALIGN_CENTER)
        sizer.Add(self.lab_tree_list, 1,wx.EXPAND)
        self.tree_root = self.lab_tree_list.AddRoot("Lab Sections")
        self.tree_rootDict = {}

    def buildRightQuestionsArea(self, panel, sizer):
        si_sizer = wx.GridBagSizer(5, 5)
        si_sizer.Add(wx.StaticText(panel, label="Student:"), pos=(0, 0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)
        # @NOTE: we might not need the section in the student information, since its already denoted in the tree - just a thought not sure
        si_sizer.Add(wx.StaticText(panel, label="Section:"), pos=(1, 0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)
        si_sizer.Add(wx.StaticText(panel, label="Questions Right:"), pos=(0, 3), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)
        si_sizer.Add(wx.StaticText(panel, label="Score:"), pos=(1, 3), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)

        self.si_name = wx.TextCtrl(panel, value="")
        self.si_section = wx.TextCtrl(panel, value="")
        self.si_right = wx.TextCtrl(panel, value="")
        self.si_score = wx.TextCtrl(panel, value="")

        self.si_right.Bind(wx.EVT_TEXT, self.setScore)

        si_sizer.Add(self.si_name, pos=(0, 1), flag=wx.ALL, border=0)
        si_sizer.Add(self.si_section, pos=(1, 1), flag=wx.ALL, border=0)
        si_sizer.Add(self.si_right, pos=(0, 4), flag=wx.ALL, border=0)
        si_sizer.Add(self.si_score, pos=(1, 4), flag=wx.ALL, border=0)

        si_sizer.AddGrowableCol(2)

        sizer.Add(si_sizer, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
        sizer.Add(wx.StaticLine(panel, wx.ID_ANY), 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)

    def updateTreeList(self, tree):
        """Tree List on Left Side - Dynamic to Files"""
        for name in sorted(self.assignmentStack.keys()):
            sec = self.assignmentStack[name].getSection()
            if sec == "MissingInformation":
                self.tree_rootDict[sec] = tree.AppendItem(self.tree_root, "Missing Lab Section")
                self.lab_tree_list.SetItemBackgroundColour(self.tree_rootDict[sec],"#FFAAAA")
            elif sec not in self.tree_rootDict.keys(): #creates root section if there isn't one
                self.tree_rootDict[sec] = tree.AppendItem(self.tree_root, "Section "+sec)
            tree.AppendItem(self.tree_rootDict[sec], name) #appends name onto section

    def updateStudentInformation(self, name, section):
        self.si_name.ChangeValue(name)
        self.si_section.ChangeValue(section)
        self.si_right.ChangeValue("")
        self.si_score.ChangeValue("")

    def updateQuestions(self, name):
        # @TODO - it would be better if this variable could be set somewhere else
        self.totalPoints = 30 #if they are floats answer will be more accurate
        self.numberQuestions = 12

        # This gets our students answers and the dictionary we're comparing their answer to.
        studentQD = self.assignmentStack[name].getStudentDictionary()
        right = 0
        if self.assignmentStack[name].getMisc() != []:
            self.b_equations.Enable()
        else:
            self.b_equations.Disable()
        for qNum in studentQD.keys():
            self.student_answer_boxes[qNum].SetLabel(studentQD[qNum]["answer"])

            if studentQD[qNum]['grade']:
                self.student_answer_boxes[qNum].SetBackgroundColour(wx.NullColour)
                right += 1
            else:
                self.student_answer_boxes[qNum].SetBackgroundColour("#FFAAAA")
        self.si_right.SetValue(str(right) + " / " + str(int(self.numberQuestions)))
        
    def setScore(self, event):
        try:
            self.si_score.ChangeValue( str(float(self.si_right.GetValue().split(" ")[0])/self.numberQuestions*self.totalPoints) + " / " + str(self.totalPoints) )
        except:
            pass

    def initializeQuestionArea(self):
        self.questions_area = wx.ScrolledWindow(self.mainpanel)
        self.questions_area.SetScrollbars(1, 1, 650, 1000)
        self.questions_area.EnableScrolling(True,True)
        self.right_sizer.Add(self.questions_area, 1, wx.EXPAND)

        self.questions_area_sizer = wx.BoxSizer(wx.VERTICAL)
        self.questions_area.SetSizer(self.questions_area_sizer)

        self.student_answer_boxes = {}

        for qNum in self.qb.getQuestionsDict().keys():
            label = wx.StaticText(self.questions_area, wx.ID_ANY, "Question "+str(qNum) + ":\n"+ str(wordwrap(self.qb.getQuestionsDict()[qNum]["question"]+" "+str(self.qb.getQuestionsDict()[qNum]["answer"]), self.questions_area.GetVirtualSize()[0], wx.ClientDC(self.questions_area))) )
            self.questions_area_sizer.Add(label)

            q_sizer = wx.BoxSizer(wx.HORIZONTAL)

            student_answer = wx.TextCtrl(self.questions_area, wx.ID_ANY, style=wx.TE_READONLY, value="" )
            self.student_answer_boxes[qNum] = student_answer

            q_sizer.Add(student_answer, 1, wx.EXPAND|wx.TOP|wx.RIGHT, 5)
            self.questions_area_sizer.Add(q_sizer, 0, wx.EXPAND)
            if qNum != self.qb.getQuestionsDict().keys()[-1]:
                self.questions_area_sizer.Add(wx.StaticLine(self.questions_area, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)

        # I've got this initialized variable here to keep track
        # of whether we should warn about loading the question bank
        # when trying to select a student's responses.
        self.initialized = True
        self.mainpanel.Layout()

def newSession():
    main = MainApp()
    main.Show()

if __name__ == "__main__":
    # Error messages go to pop-up window
    # because of the redirect=True.
    app = wx.App(redirect=False)
    newSession()
    app.MainLoop()