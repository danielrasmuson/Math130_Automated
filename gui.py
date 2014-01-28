from __future__ import division
import wx, os, time
from assignment import getAssignmentStack
from question_bank import *
from wx.lib.wordwrap import wordwrap
from toImportDocument import sendToImport
from commentBrowser import CommentBrowser # split this to a new file because this one is so big
from importWizard import *

class MainApp(wx.Frame):
    initialized = False
    class MenuNav:
        """ Create our menu bar with all the appropriate buttons and methods. """
        def __init__(self, parent):
            self.parent = parent
            self.parent.Bind(wx.EVT_CLOSE, self.onClose)

            menuBar = wx.MenuBar()

            fileMenu = wx.Menu()
            m_new = fileMenu.Append(wx.ID_NEW, "&New Grading Session\tAlt-N", "Removes all of the students and the currently loaded dictionary.")
            m_open = fileMenu.Append(wx.ID_OPEN, "&Open Document Directory\tAlt-O", "Select the directory containing the student documents.")
            m_load = fileMenu.Append(wx.ID_ANY, "&Load Question Bank\tAlt-L", "Load's a new question bank for grading purposes.")
            m_import = fileMenu.Append(wx.ID_ANY, "&Load Import Template\tAlt-I", "Will write grades to this document for later import.")
            m_wizard = fileMenu.Append(wx.ID_ANY, "Guided &Wizard\tAlt-W", "Opens the guided wizard for the setup process.")
            fileMenu.AppendSeparator()
            m_default = fileMenu.Append(wx.ID_ANY, "&Default Load Stuffs (Delete Me Later)\tAlt-D", "Loads all of the above stuff in one click.  Will get deleted later.")
            fileMenu.AppendSeparator()
            m_exit = fileMenu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
            self.parent.Bind(wx.EVT_MENU, self.onNew, m_new)
            self.parent.Bind(wx.EVT_MENU, self.onOpen, m_open)
            self.parent.Bind(wx.EVT_MENU, self.loadBank, m_load)
            self.parent.Bind(wx.EVT_MENU, self.loadImportFile, m_import)
            self.parent.Bind(wx.EVT_MENU, self.wizardEvent, m_wizard)
            self.parent.Bind(wx.EVT_MENU, self.parent.deleteMeLater, m_default)
            self.parent.Bind(wx.EVT_MENU, self.onClose, m_exit)
            menuBar.Append(fileMenu, "&File")

            helpMenu = wx.Menu()
            m_about = helpMenu.Append(wx.ID_ABOUT, "&About", "Information about this program")
            self.parent.Bind(wx.EVT_MENU, self.onAbout, m_about)
            menuBar.Append(helpMenu, "&Help")

            self.parent.SetMenuBar(menuBar)

            self.parent.statusbar = self.parent.CreateStatusBar()

        def wizardEvent(self, event):
            tempwiz = ImportWizard()
            start = time.clock()
            self.parent.importFilePath = tempwiz.gradingSheet.GetValue()
            self.parent.assignmentStack = getAssignmentStack(tempwiz.gradingDirectory.GetValue(),self.parent.importFilePath)
            end = time.clock()
            print "Time taken to load files:",end-start
            self.parent.studentTree.updateTreeList()
            self.parent.qb.load(tempwiz.labDictionaryFile.GetValue())
            self.parent.questionsArea.drawQuestions()
            self.parent.lab_tree_list.SelectItem(self.parent.lab_tree_list.GetFirstVisibleItem())
            print "Done With Wizard Load"

        def loadBank(self, event):
            dlg = wx.FileDialog(self.parent, "Choose a lab file:",defaultFile="lab1.dat",defaultDir=os.getcwd(), style=wx.FD_OPEN)
            dlg.SetWildcard("Lab Dictionaries (*.dat)|*.dat")
            if dlg.ShowModal() == wx.ID_OK:
                self.parent.qb.load(dlg.GetPath())
                try:
                    self.parent.questions_area.Destroy()
                except:
                    pass
                self.parent.questionsArea.drawQuestions()
            dlg.Destroy()

        def loadImportFile(self, event):
            """The user finds the template import file
            downloaded from d2l and then the program will
            fill in the values."""
            dlg = wx.FileDialog(self.parent, "Choose an import file:",defaultDir=os.getcwd(), style=wx.FD_OPEN)
            dlg.SetWildcard("Lab Import File (*.csv)|*.csv")
            if dlg.ShowModal() == wx.ID_OK:
                self.parent.importFilePath = dlg.GetPath()
            dlg.Destroy()

        def onAbout(self, event):
            dlg = wx.MessageDialog(self.parent, "Written by Daniel Rasmuson and Gregory Dosh", "About", wx.OK)
            result = dlg.ShowModal()
            dlg.Destroy()

        def onClose(self, event):
            dlg = wx.MessageDialog(self.parent,
                "Do you really want to close this application?",
                "Confirm Exit", wx.YES_NO|wx.ICON_EXCLAMATION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
                self.parent.Destroy()

        def onNew(self, event):
            dlg = wx.MessageDialog(self.parent,
                "Do you want to clear everything and start a new session?",
                "Confirm New", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_OK:
                self.parent.Show(False)
                newSession()
                self.parent.Destroy()

        def onOpen(self, event):
            # I get the current working directory + the examples test stuff
            # so that while testing it'll default to our test directory.
            # Later we can navigate anywhere we want and cut that part.
            dlg = wx.DirDialog(self.parent, "Choose a directory:",os.getcwd()+"\\Examples\\test")
            if dlg.ShowModal() == wx.ID_OK:
                self.parent.assignmentStack = getAssignmentStack(dlg.GetPath(), self.parent.getImportFilePath())
                # Call our initial tree list build
                self.parent.studentTree.updateTreeList()
            dlg.Destroy()
            self.parent.lab_tree_list.SelectItem(self.parent.lab_tree_list.GetFirstVisibleItem())

    class BottomNav:
        """ Builds a predefined set of buttons on a specific panel and utilizing the sizer provided """
        def __init__(self, parent, panel, sizer):
            self.parent = parent
            self.panel = panel
            self.sizer = sizer

            b_prev = wx.Button(panel, wx.ID_ANY, "Previous")
            b_prev.SetToolTipString("Selects the previous student of the current section.")
            b_prev.Bind(wx.EVT_BUTTON, self.previousButton)
            sizer.Add(b_prev, 0,wx.ALL,5)

            b_next = wx.Button(panel, wx.ID_ANY, "Next")
            b_next.SetToolTipString("Selects the next student of the current section")
            b_next.Bind(wx.EVT_BUTTON, self.nextButton)
            sizer.Add(b_next, 0,wx.ALL,5)

            sizer.AddStretchSpacer(1)

            self.b_comments = wx.Button(panel, wx.ID_ANY, "Comments")
            self.b_comments.SetToolTipString("Opens a new dialog box with extra comments (if available) for the current student.")
            self.b_comments.Bind(wx.EVT_BUTTON, self.parent.commentWindow.display)
            sizer.Add(self.b_comments, 0,wx.ALL,5)

            b_open = wx.Button(panel, wx.ID_ANY, "Open Document")
            b_open.SetToolTipString("Opens the document in word.")
            b_open.Bind(wx.EVT_BUTTON, self.openDocument)
            sizer.Add(b_open, 0,wx.ALL,5)

            # A button for sending the grade to the excel file
            b_grade = wx.Button(panel, wx.ID_ANY, "Submit Grade")
            b_grade.SetToolTipString("Sends the grade to excel file")
            b_grade.Bind(wx.EVT_BUTTON, self.sendGrade)
            sizer.Add(b_grade, 0,wx.ALL,5)

        def openDocument(self, event):
            current_item = self.parent.studentTree.getSelected()
            if "Section" not in current_item:
                os.system("\""+self.parent.assignmentStack[current_item].getStudentFilepath()+"\"")

        def previousButton(self, event):
            current = self.parent.lab_tree_list.GetSelection()
            prev = self.parent.lab_tree_list.GetPrevSibling(current)
            if prev.IsOk() and not self.parent.lab_tree_list.ItemHasChildren(prev):
                self.parent.lab_tree_list.SelectItem(prev)
                self.parent.questionsArea.scrollTop()
            elif prev.IsOk() and  self.parent.lab_tree_list.ItemHasChildren(prev):
                self.parent.lab_tree_list.SelectItem(self.parent.lab_tree_list.GetLastChild(prev))
            else:
                parent = self.parent.lab_tree_list.GetItemParent(self.parent.lab_tree_list.GetSelection())
                if parent != self.parent.lab_tree_list.GetRootItem():
                    self.parent.lab_tree_list.SelectItem(parent)

        def nextButton(self, event):
            current = self.parent.lab_tree_list.GetSelection()
            if self.parent.lab_tree_list.ItemHasChildren(current):
                next = self.parent.lab_tree_list.GetFirstChild(current)[0]
            else:
                next = self.parent.lab_tree_list.GetNextSibling(current)
            if next.IsOk():
                self.parent.lab_tree_list.SelectItem(next)
                self.parent.questionsArea.scrollTop()
            else:
                parent = self.parent.lab_tree_list.GetItemParent(self.parent.lab_tree_list.GetSelection())
                if self.parent.lab_tree_list.GetNextSibling(parent).IsOk():
                    self.parent.lab_tree_list.SelectItem(self.parent.lab_tree_list.GetNextSibling(parent))

        def sendGrade(self, event):
            # @TODO: right answers should be divided by the total score (30 points)
            name = self.parent.questionsArea.si_name.GetValue().split()
            score = self.parent.questionsArea.si_score.GetValue()
            sendToImport(self.parent.importFilePath, name[0], " ".join(name[1:]), score)
            self.parent.lab_tree_list.SetItemText(self.parent.lab_tree_list.GetSelection(), u"\u2714"+self.parent.questionsArea.si_name.GetValue())
            self.parent.lab_tree_list.SetItemTextColour(self.parent.lab_tree_list.GetSelection(), (0,150,0))

    class TreeNav:
        """ Builds our tree list of students """
        def __init__(self, parent, panel, sizer):
            self.parent = parent
            self.panel = panel
            self.sizer = sizer

            self.parent.lab_tree_list = wx.TreeCtrl(panel, 1, size=wx.Size(200,-1),style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT)
            self.parent.lab_tree_list.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelChanged, id=1)
            lab_tree_label = wx.StaticText(panel, wx.ID_ANY, 'Student List')
            sizer.Add(lab_tree_label,0,wx.ALIGN_CENTER)
            sizer.Add(self.parent.lab_tree_list, 1,wx.EXPAND)
            self.parent.tree_root = self.parent.lab_tree_list.AddRoot("Lab Sections")
            self.parent.tree_rootDict = {}

        def getSelected(self):
            return str(self.parent.lab_tree_list.GetItemText(self.parent.lab_tree_list.GetSelection()).strip(u"\u2714"))

        def onSelChanged(self, event):
            # Get our item that updated
            item = event.GetItem()
            currentSelection = self.getSelected()
            if "Section" not in currentSelection:
                section = self.parent.assignmentStack[currentSelection].getSection()
                self.parent.questionsArea.updateStudentInformation(currentSelection, section)
                self.parent.commentWindow.setStudent(currentSelection)
                if self.parent.initialized:
                    self.parent.questionsArea.updateStudentAnswers(currentSelection)

        def updateTreeList(self):
            """Tree List on Left Side - Dynamic to Files"""
            for name in sorted(self.parent.assignmentStack.keys()):
                sec = self.parent.assignmentStack[name].getSection()
                if sec == "MissingInformation":
                    self.parent.tree_rootDict[sec] = self.parent.lab_tree_list.AppendItem(self.parent.tree_root, "Missing Lab Section")
                    self.parent.lab_tree_list.SetItemBackgroundColour(self.parent.tree_rootDict[sec],"#FFAAAA")
                elif sec not in self.parent.tree_rootDict.keys(): #creates root section if there isn't one
                    self.parent.tree_rootDict[sec] = self.parent.lab_tree_list.AppendItem(self.parent.tree_root, "Section "+sec)
                self.parent.lab_tree_list.AppendItem(self.parent.tree_rootDict[sec], name) #appends name onto section

    class QuestionsArea:
        def __init__(self, parent, panel, sizer):
            self.parent = parent
            self.panel = panel
            self.sizer = sizer

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

        def scrollTop(self):
            self.questions_area.Scroll((0,0))

        def drawQuestions(self):
            def setFullCorrect(event):
                qNum = event.GetId()
                self.parent.commentWindow.removeWrong(qNum)
                #changes the background color
                self.student_answer_boxes[qNum].SetBackgroundColour("#FFFFFF")
                self.qs.setGrade(qNum, 1) # keeps after switching pages
                self.student_answer_boxes[qNum].Refresh() #fix for delay

                #hides button to prevent reclick
                self.fullCorrectButtons[qNum].Hide()
                self.halfCorrectButtons[qNum].Hide()
                self.markWrongButtons[qNum].Hide()

                # increases score by one
                right = float(self.si_right.GetValue().split()[0]) + 1
                self.si_right.SetValue(str(right) + " / " + str(int(self.parent.qb.getTotalQuestions())))

            def setHalfCorrect(event):
                qNum = event.GetId()-100
                self.parent.commentWindow.removeWrong(qNum)
                #changes the background color
                self.student_answer_boxes[qNum].SetBackgroundColour("#FFAA00")
                self.qs.setGrade(qNum, .5) # keeps after switching pages
                self.student_answer_boxes[qNum].Refresh() #fix for delay

                #hides button to prevent reclick
                self.fullCorrectButtons[qNum].Hide()
                self.halfCorrectButtons[qNum].Hide()
                self.markWrongButtons[qNum].Hide()

                # increases score by one
                right = float(self.si_right.GetValue().split()[0]) + 0.5
                self.si_right.SetValue(str(right) + " / " + str(int(self.parent.qb.getTotalQuestions())))

            def setWrong(event):
                qNum = event.GetId()-1000
                # self.parent.commentWindow.removeWrong(qNum)
                #changes the background color
                self.student_answer_boxes[qNum].SetBackgroundColour("#FFAAAA")
                self.qs.setGrade(qNum, 0) # keeps after switching pages
                self.student_answer_boxes[qNum].Refresh() #fix for delay

                #hides button to prevent reclick
                self.fullCorrectButtons[qNum].Hide()
                self.halfCorrectButtons[qNum].Hide()
                self.markWrongButtons[qNum].Hide()

                # increases score by one
                right = float(self.si_right.GetValue().split()[0]) - 1
                self.si_right.SetValue(str(right) + " / " + str(int(self.parent.qb.getTotalQuestions())))

            self.questions_area = wx.ScrolledWindow(self.panel)
            self.questions_area.SetScrollbars(1, 5, 500, 1000)
            self.questions_area.EnableScrolling(True,True)
            self.sizer.Add(self.questions_area, 1, wx.EXPAND)

            self.questions_area_sizer = wx.BoxSizer(wx.VERTICAL)
            self.questions_area.SetSizer(self.questions_area_sizer)

            self.student_answer_boxes = {}
            self.fullCorrectButtons = {}
            self.halfCorrectButtons = {}
            self.markWrongButtons = {}
            for qNum in self.parent.qb.getKeys():


                # Question Num
                # Question 1:
                qNum_sizer = wx.BoxSizer(wx.HORIZONTAL)
                qNumText = wx.StaticText(self.questions_area, wx.ID_ANY, "Question "+str(qNum) + ":") #,pos=(-1,-1),size=(100,-1)
                boldFont = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
                qNumText.SetFont(boldFont) # applies bold font
                qNum_sizer.Add(qNumText)

                # Answer
                # 3.34
                answer = str(self.parent.qb.getAnswer(qNum))
                answerTextBox = wx.StaticText(self.questions_area, wx.ID_ANY, answer)
                qNum_sizer.AddStretchSpacer(1) #to push button to end
                qNum_sizer.Add(answerTextBox, flag=wx.ALIGN_RIGHT|wx.ALIGN_TOP, border=20) # TODO: this boarder is not working

                #adds qNum_sizer to the panel
                self.questions_area_sizer.Add(qNum_sizer, 0, wx.EXPAND)

                # Question and Answer
                # What is the 3rd term of the sequence? 
                c_sizer = wx.BoxSizer(wx.HORIZONTAL)
                question = self.parent.qb.getQuestion(qNum)
                sizeQArea = self.questions_area.GetVirtualSize()[0]
                textInQandA = str(wordwrap(question, sizeQArea, wx.ClientDC(self.questions_area)))
                textInQandA = wx.StaticText(self.questions_area, wx.ID_ANY, textInQandA)
                c_sizer.Add(textInQandA)

                # Correct Buttons \u2714
                c_sizer.AddStretchSpacer(1) #to push buttons to end
                fullCorrect = wx.Button(self.questions_area, size=(20,20), id=qNum, label=u"\u2714")
                fullCorrect.SetForegroundColour((0,150,0))
                fullCorrect.SetToolTipString("Sets the question as correct")
                fullCorrect.Bind(wx.EVT_BUTTON, setFullCorrect)
                fullCorrect.Hide()
                self.fullCorrectButtons[qNum] = fullCorrect #add it to the dictionary
                c_sizer.Add(fullCorrect, 0, flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=0)

                # Half Correct Buttons \u00BD
                halfCorrect = wx.Button(self.questions_area, size=(20,20), id=qNum+100, label=u"\u00BD")
                halfCorrect.SetForegroundColour("#FFAA00")
                halfCorrect.SetToolTipString("Sets the question as half correct")
                halfCorrect.Bind(wx.EVT_BUTTON, setHalfCorrect)
                halfCorrect.Hide()
                self.halfCorrectButtons[qNum] = halfCorrect #add it to the dictionary
                c_sizer.Add(halfCorrect, 0, flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=0)

                # Wrong Buttons \u2717
                markWrong = wx.Button(self.questions_area, size=(20,20), id=qNum+1000, label=u"\u2717")
                markWrong.SetForegroundColour("#FF0000")
                markWrong.SetToolTipString("Sets the question as wrong")
                markWrong.Bind(wx.EVT_BUTTON, setWrong)
                markWrong.Hide()
                self.markWrongButtons[qNum] = markWrong #add it to the dictionary
                c_sizer.Add(markWrong, 0, flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=0)

                self.questions_area_sizer.Add(c_sizer, 0, wx.EXPAND)

                # Student Answer Section
                q_sizer = wx.BoxSizer(wx.HORIZONTAL)
                student_answer = wx.TextCtrl(self.questions_area, wx.ID_ANY, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH, value="")
                self.student_answer_boxes[qNum] = student_answer
                q_sizer.Add(student_answer, 1) #1, wx.EXPAND|wx.TOP|wx.RIGHT, 5
                self.questions_area_sizer.Add(q_sizer, 0, wx.EXPAND)

                # The Last Question Cleanup
                if qNum != self.parent.qb.getKeys()[-1]:
                    self.questions_area_sizer.Add(wx.StaticLine(self.questions_area, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)

            # I've got this initialized variable here to keep track
            # of whether we should warn about loading the question bank
            # when trying to select a student's responses.
            self.parent.initialized = True

        def updateStudentAnswers(self, name):
            # This gets our students answers and the dictionary we're comparing their answer to.
            self.qs = self.parent.assignmentStack[name] # current student sheet
            right = 0

            for qNum in self.qs.getKeys():
                self.student_answer_boxes[qNum].SetLabel(str(self.qs.getAnswer(qNum)))
                if self.qs.getGrade(qNum):
                    self.student_answer_boxes[qNum].SetBackgroundColour("#FFFFFF")
                    self.fullCorrectButtons[qNum].Hide()
                    self.halfCorrectButtons[qNum].Hide()
                    self.markWrongButtons[qNum].Show()
                    right += 1
                else:
                    self.student_answer_boxes[qNum].SetBackgroundColour("#FFAAAA")
                    self.fullCorrectButtons[qNum].Show()
                    self.halfCorrectButtons[qNum].Show()
                    self.markWrongButtons[qNum].Hide()
                    self.panel.Layout()
                    self.parent.commentWindow.addWrong(qNum, self.parent.qb.getQuestion(qNum), self.parent.qb.getAnswer(qNum), self.qs.getAnswer(qNum))
            self.si_right.SetValue(str(right) + " / " + str(int(self.parent.qb.getTotalQuestions())))

        def updateStudentInformation(self, name, section):
            self.si_name.ChangeValue(name)
            self.si_section.ChangeValue(section)
            self.si_right.ChangeValue("")
            self.si_score.ChangeValue("")

        def setScore(self, event):
            # try:
            self.si_score.ChangeValue(str(self.qs.getTotalScore()) + " / " + str(self.parent.qb.getTotalPoints()))
            # except:
            #     pass

    def __init__(self):
        self.qb = Question_Bank()
        wx.Frame.__init__(self, None,title="Math 130 Automated Grading System", pos=(50,50), size=(800,600), style =wx.DEFAULT_FRAME_STYLE)
        self.SetMinSize((800,600))

        # We need a panel in order to put stuff on
        # and then we are adding the things we want to see on this panel.
        mainpanel = wx.Panel(self, wx.ID_ANY)

        # Define most of our main sizers here
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer_a = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer_b = wx.BoxSizer(wx.HORIZONTAL)
        tree_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Set up the first layer of sizers for the top and
        # bottom panels separated by a line.
        main_sizer.Add(main_sizer_a, 1, wx.EXPAND)
        main_sizer.Add(wx.StaticLine(mainpanel), 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        main_sizer.Add(main_sizer_b, 0, wx.EXPAND)

        # Our top sizer contains the left hand tree list and
        # the right hand side list for the student information
        main_sizer_a.Add(tree_sizer,0,wx.ALL|wx.EXPAND,5)
        main_sizer_a.Add(right_sizer,1,wx.TOP|wx.BOTTOM|wx.RIGHT|wx.EXPAND,5)
        mainpanel.SetSizer(main_sizer)

        # Creat our Comment Browswer so that we can use it later,
        # it's hidden by default.
        self.commentWindow = CommentBrowser(self, initialSize=(500,500),initialPosition=(0,0))

        # We create the MenuNav class here and pass in the self
        # arguement so that we can catch it and set it as the parent
        # for the MenuClass to use as it's parent.
        self.menuNavigation = self.MenuNav(self)

        # Now we call the routines to build the main content
        self.studentTree = self.TreeNav(self, mainpanel, tree_sizer)
        self.questionsArea = self.QuestionsArea(self, mainpanel, right_sizer)
        self.buttonArea = self.BottomNav(self, mainpanel, main_sizer_b)

        mainpanel.Layout()

        self.Show()

    def deleteMeLater(self, event):
        start = time.clock()
        self.importFilePath = os.getcwd()+"\\Examples\\Finite Math & Intro Calc 130 07_GradesExport_2014-01-25-16-06.csv"
        self.assignmentStack = getAssignmentStack(os.getcwd()+"\\Examples\\Test", self.getImportFilePath())
        end = time.clock()
        print "Time taken to load files:",end-start
        self.studentTree.updateTreeList()
        self.qb.load(os.getcwd()+"\\lab1.dat")
        self.questionsArea.drawQuestions()
        print "Done With Sample Load"

    def getImportFilePath(self):
        #TODO: if we make sub classes we can embed this into buildMenuNav
        return self.importFilePath

def newSession():
    main = MainApp()

if __name__ == "__main__":
    # Error messages go to pop-up window
    # because of the redirect=True.
    app = wx.App(redirect=False)
    newSession()
    app.MainLoop()