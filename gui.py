from __future__ import division
import wx, os, subprocess, difflib, glob
from wx.lib.wordwrap import wordwrap
from toImportDocument import sendToImport
from commentBrowser import CommentBrowser # split this to a new file because this one is so big
from importWizard import *
from MasterDatabase import *

class MainApp(wx.Frame):
    class MenuNav:
        """ Create our menu bar with all the appropriate buttons and methods. """
        def __init__(self, parent):
            self.parent = parent
            self.parent.Bind(wx.EVT_CLOSE, self.onClose)

            menuBar = wx.MenuBar()

            fileMenu = wx.Menu()
            m_new = fileMenu.Append(wx.ID_NEW, "&New Grading Session\tCtrl-N", "Removes all of the students and the currently loaded dictionary.")
            m_save = fileMenu.Append(wx.ID_SAVE, "&Save Grading Session\tCtrl-S", "Saves the current grading progress to disk.")
            m_open = fileMenu.Append(wx.ID_OPEN, "&Open Grading Session\tCtrl-O", "Opens a previous grading session from disk.")
            m_wizard = fileMenu.Append(wx.ID_ANY, "Import &Wizard\tCtrl-W", "Opens the guided wizard for the setup process.")
            fileMenu.AppendSeparator()
            m_default = fileMenu.Append(wx.ID_ANY, "&Default Load Stuffs (Delete Me Later)\tCtrl-D", "Loads all of the above stuff in one click.  Will get deleted later.")
            fileMenu.AppendSeparator()
            m_exit = fileMenu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
            self.parent.Bind(wx.EVT_MENU, self.onNew, m_new)
            self.parent.Bind(wx.EVT_MENU, self.onSave, m_save)
            self.parent.Bind(wx.EVT_MENU, self.onOpen, m_open)
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
            tempwiz = ImportWizard(self.parent)

        def onSave(self, event):
            dlg = wx.FileDialog(self.parent, "Choose a lab file:",defaultFile=str(self.parent.masterDatabase.currentLab)+"-"+str(self.parent.tree_rootDict.keys()[0]).lstrip("0"),defaultDir=os.getcwd(), style=wx.FD_SAVE|wx.OVERWRITE_PROMPT)
            dlg.SetWildcard("Lab Dictionaries (*.dat)|*.dat")
            if dlg.ShowModal() == wx.ID_OK:
                self.parent.masterDatabase.saveProgress(dlg.GetPath())
            dlg.Destroy()

        def onOpen(self, event):
            dlg = wx.FileDialog(self.parent, "Choose a lab file:",defaultFile="",defaultDir=os.getcwd(), style=wx.FD_OPEN)
            dlg.SetWildcard("Lab Dictionaries (*.dat)|*.dat")
            if dlg.ShowModal() == wx.ID_OK:
                self.parent.masterDatabase.loadProgress(dlg.GetPath())
                self.parent.studentTree.updateTreeList()
                self.parent.questionsArea.drawQuestions()
                self.parent.lab_tree_list.SelectItem(self.parent.lab_tree_list.GetFirstVisibleItem())
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

    class BottomNav:
        """ Builds a predefined set of buttons on a specific panel and utilizing the sizer provided """
        def __init__(self, parent, panel, sizer):
            self.parent = parent
            self.panel = panel
            self.sizer = sizer

            sizer.AddSpacer(8)

            b_prev = wx.Button(panel, wx.ID_ANY, "Previous")
            b_prev.SetToolTipString("Selects the previous student of the current section.")
            b_prev.Bind(wx.EVT_BUTTON, self.previousButton)
            sizer.Add(b_prev, 0,wx.ALL,5)

            b_next = wx.Button(panel, wx.ID_ANY, "Next")
            b_next.SetToolTipString("Selects the next student of the current section")
            b_next.Bind(wx.EVT_BUTTON, self.nextButton)
            sizer.Add(b_next, 0,wx.ALL,5)

            sizer.AddStretchSpacer(1)

            self.b_cheat = wx.Button(panel, wx.ID_ANY, "Cheat Check")
            self.b_cheat.SetToolTipString("Runs some basic cheat detection on the currently loaded students.")
            self.b_cheat.Bind(wx.EVT_BUTTON, self.ratioCheck)
            self.b_cheat.Bind(wx.EVT_BUTTON, self.cheatCheck)
            sizer.Add(self.b_cheat, 0,wx.ALL,5)

            sizer.AddStretchSpacer(1)

            self.b_comments = wx.Button(panel, wx.ID_ANY, "Comments")
            self.b_comments.SetToolTipString("Opens a new dialog box with extra comments (if available) for the current student.")
            self.b_comments.Bind(wx.EVT_BUTTON, self.parent.commentWindow.display)
            sizer.Add(self.b_comments, 0,wx.ALL,5)

            b_open = wx.Button(panel, wx.ID_ANY, "Open Document")
            b_open.SetToolTipString("Opens the document in word.")
            b_open.Bind(wx.EVT_BUTTON, self.openDocument)
            sizer.Add(b_open, 0,wx.ALL,5)

            self.b_open_excel = wx.Button(panel, wx.ID_ANY, "Excel Document")
            self.b_open_excel.SetToolTipString("Opens the excel document if available.")
            self.b_open_excel.Disable()
            self.b_open_excel.Bind(wx.EVT_BUTTON, self.openExcel)
            sizer.Add(self.b_open_excel, 0,wx.ALL,5)

            # A button for sending the grade to the excel file
            b_grade = wx.Button(panel, wx.ID_ANY, "Submit Grade")
            b_grade.SetToolTipString("Sends the grade to excel file")
            b_grade.Bind(wx.EVT_BUTTON, self.submitGrade)
            sizer.Add(b_grade, 0,wx.ALL,5)

        def openDocument(self, event):
            current_item = self.parent.studentTree.getSelected()
            if "Section" not in current_item:
                subprocess.Popen(["explorer",self.parent.masterDatabase.getStudentWordFilepath(current_item)], shell=False)

        def openExcel(self, event):
            subprocess.Popen(["explorer",self.parent.xlsx_path], shell=False)

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

        def submitGrade(self, event):
            # @TODO: right answers should be divided by the total score (30 points)
            name = self.parent.questionsArea.si_name.GetValue()
            name = name.split()
            score = self.parent.questionsArea.si_score.GetValue()
            if self.parent.questionsArea.si_attendance.GetValue() == "No Quiz":
                dlg = wx.MessageDialog(self.parent,name[0] + "did not take the attendance quiz. Submit 0 instead of "+str(score)+"?","Confirmation", wx.YES_NO | wx.ICON_QUESTION)
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == wx.ID_YES:
                    score = "0"
            result = sendToImport(self.parent.masterDatabase.gradeFile, name[0], " ".join(name[1:]), score)
            if result:
                self.parent.masterDatabase.setStudentSubmittedGrade(str(self.parent.questionsArea.si_name.GetValue()),True)
                self.parent.lab_tree_list.SetItemText(self.parent.lab_tree_list.GetSelection(), u"\u2714"+self.parent.questionsArea.si_name.GetValue())
                self.parent.lab_tree_list.SetItemTextColour(self.parent.lab_tree_list.GetSelection(), (0,150,0))
            else:
                wx.MessageBox("Unable to find "+name[0]+" in the file "+self.parent.masterDatabase.gradeFile,"Grade Not Submitted!", wx.OK | wx.ICON_ERROR)

        def ratioCheck(self, event):
            """ Checks for the ratio of similarity between all of the labs, but it slower than other method. """
            names = sorted(self.parent.masterDatabase.getStudentKeys())
            ratioList = []
            for i,name1 in enumerate(names):
                for j,name2 in enumerate(names):
                    if i < j:
                        labcheck1 = u"".join(self.parent.masterDatabase.getStudentLabString(name1).split("\n")[4:])
                        labcheck1 = labcheck1.replace("\n","")
                        labcheck1 = labcheck1.replace("\r","")
                        labcheck2 = u"".join(self.parent.masterDatabase.getStudentLabString(name2).split("\n")[4:])
                        labcheck2 = labcheck2.replace("\n","")
                        labcheck2 = labcheck2.replace("\r","")
                        ratio = difflib.SequenceMatcher(None,labcheck1,labcheck2).ratio()
                        ratioList.append([name1,name2,ratio])
                        if ratio > .96:
                            wx.MessageBox(name1 + " and " + name2 + " have a ratio of "+str(ratio), 'High Text Similarity!', wx.OK | wx.ICON_INFORMATION)
            ratioList = sorted(ratioList,key=lambda x:x[2], reverse=True)
            ratioInfo = [ x[0] + " & " + x[1] + ": " + str(x[2])[0:6] for x in ratioList[0:5]]
            wx.MessageBox("\n".join(ratioInfo),"Top 5 Ratios", wx.OK | wx.ICON_INFORMATION)
            event.Skip() #Let's us have the button do two things at once.

        def cheatCheck(self, event):
            """Checks for identical labs past the grade, takes likes .001 of a second to run so cant hurt"""
            names = self.parent.masterDatabase.getStudentKeys()
            labs = {}
            for name in names:
                labString = self.parent.masterDatabase.getStudentLabString(name)
                labNoName = u"".join(labString.split("\n")[4:])
                if labNoName in labs.values():
                    for name2, labString2 in labs.items():
                        if labString2 == labNoName:
                            wx.MessageBox("Cheated " + name + " and " + name2 + " identical lab", 'Cheating Detected!', wx.OK | wx.ICON_INFORMATION)
                else:
                    labs[name] = labNoName
            wx.MessageBox("Finished with the Cheat Checking.","Done", wx.OK | wx.ICON_INFORMATION)
            event.Skip() #Let's us have the button do two things at once.

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
                self.parent.questionsArea.updateStudentInformation(currentSelection, self.parent.masterDatabase.getLastWordModified(currentSelection), self.parent.masterDatabase.getLastExcelModified(currentSelection))
                self.parent.commentWindow.setStudent(currentSelection)
                self.parent.questionsArea.updateStudentAnswers(currentSelection)

                # Turns on or off our excel button.
                files = self.parent.masterDatabase.getStudentExcelFilepath(currentSelection)
                if len(files) > 0:
                    self.parent.xlsx_path = files[0]
                    self.parent.buttonArea.b_open_excel.Enable()
                else:
                    self.parent.buttonArea.b_open_excel.Disable()
                self.parent.questionsArea.scrollTop()

        def updateTreeList(self):
            """Tree List on Left Side - Dynamic to Files"""
            for name in sorted(self.parent.masterDatabase.getStudentKeys()):
                sec = self.parent.masterDatabase.getStudentSection(name)
                if sec == "MissingInformation":
                    self.parent.tree_rootDict[sec] = self.parent.lab_tree_list.AppendItem(self.parent.tree_root, "Missing Lab Section")
                    self.parent.lab_tree_list.SetItemBackgroundColour(self.parent.tree_rootDict[sec],"#FFAAAA")
                elif sec not in self.parent.tree_rootDict.keys(): #creates root section if there isn't one
                    self.parent.tree_rootDict[sec] = self.parent.lab_tree_list.AppendItem(self.parent.tree_root, "Section "+sec)
                # During update check if submitted or not and then append on to tree.
                if self.parent.masterDatabase.getStudentSubmittedGrade(name):
                    temp = self.parent.lab_tree_list.AppendItem(self.parent.tree_rootDict[sec], u"\u2714" + name)
                    self.parent.lab_tree_list.SetItemTextColour(temp, (0,150,0))
                else:
                    self.parent.lab_tree_list.AppendItem(self.parent.tree_rootDict[sec], name)

    class QuestionsArea:
        def __init__(self, parent, panel, sizer):
            self.parent = parent
            self.panel = panel
            self.sizer = sizer

            si_sizer = wx.GridBagSizer(5, 5)
            si_sizer.Add(wx.StaticText(panel, label="Student:"), pos=(0, 0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)
            si_sizer.Add(wx.StaticText(panel, label="Attendance:"), pos=(1, 0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)
            si_sizer.Add(wx.StaticText(panel, label="Word Author:"), pos=(0, 2), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)
            si_sizer.Add(wx.StaticText(panel, label="Excel Author:"), pos=(1, 2), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)
            si_sizer.Add(wx.StaticText(panel, label="Questions Right:"), pos=(0, 4), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)
            si_sizer.Add(wx.StaticText(panel, label="Score:"), pos=(1, 4), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=0)

            self.si_name = wx.TextCtrl(panel, value="")
            self.si_attendance = wx.TextCtrl(panel, value="")
            self.si_wordauthor = wx.TextCtrl(panel, value="")
            self.si_excelauthor = wx.TextCtrl(panel, value="")
            self.si_right = wx.TextCtrl(panel, value="", size=(65,-1))
            self.si_score = wx.TextCtrl(panel, value="", size=(65,-1))

            self.si_right.Bind(wx.EVT_TEXT, self.setScore)

            si_sizer.Add(self.si_name, pos=(0, 1), flag=wx.ALL, border=0)
            si_sizer.Add(self.si_attendance, pos=(1, 1), flag=wx.ALL, border=0)
            si_sizer.Add(self.si_wordauthor, pos=(0, 3), flag=wx.ALL, border=0)
            si_sizer.Add(self.si_excelauthor, pos=(1, 3), flag=wx.ALL, border=0)
            si_sizer.Add(self.si_right, pos=(0, 6), flag=wx.ALL, border=0)
            si_sizer.Add(self.si_score, pos=(1, 6), flag=wx.ALL, border=0)

            sizer.Add(si_sizer, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)
            sizer.Add(wx.StaticLine(panel, wx.ID_ANY), 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)

        def scrollTop(self):
            self.questions_area.Scroll((0,0))

        def drawQuestions(self):
            def otherWeightDialog(qNum):
                name = self.si_name.GetValue()
                dlg = wx.TextEntryDialog(self.parent, "Enter new weight for question #"+str(qNum), "Question #"+str(qNum), str(self.parent.masterDatabase.getStudentQuestionWeight(name, qNum)))
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == wx.ID_OK:
                    newWeight = dlg.GetValue()
                    try:
                        if "/" in newWeight:
                            newWeight = newWeight.split("/")
                            newWeight = float(newWeight[0])/float(newWeight[1])
                        else:
                            newWeight = float(newWeight)
                        if 0 <= newWeight <= 1:
                            setCorrect(qNum,newWeight)
                        else:
                            raise
                    except:
                        wx.MessageBox("Weight must be between 0 and 1 and be only a number.\nText entered: "+str(dlg.GetValue()), "Invalid Weight!", wx.OK | wx.ICON_INFORMATION)
            def setCorrect(qNum, weight):
                name = self.si_name.GetValue()
                if weight == 1:
                    color = "#FFFFFF"
                else:
                    if weight == 0:
                        color = "#FFAAAA"
                    else:
                        color = "#FFAA00"
                self.student_answer_boxes[qNum].SetBackgroundColour(color)
                self.student_answer_boxes[qNum].Refresh() #fix for delay

                self.parent.masterDatabase.setStudentQuestionWeight(name, qNum, weight)
                self.parent.commentWindow.defaultCommentButton("")
                self.si_right.SetValue(str(self.parent.masterDatabase.getStudentTotalWeight(name))[0:5] + " / " + str(int(self.parent.masterDatabase.getTotalQuestions())))

            self.questions_area = wx.ScrolledWindow(self.panel)
            self.questions_area.SetScrollbars(1, 5, 500, 1000)
            self.questions_area.EnableScrolling(True,True)
            self.sizer.Add(self.questions_area, 1, wx.EXPAND)

            self.questions_area_sizer = wx.BoxSizer(wx.VERTICAL)
            self.questions_area.SetSizer(self.questions_area_sizer)

            self.student_answer_boxes = {}
            for qNum in sorted(self.parent.masterDatabase.getQuestionKeys()):


                # Question Num
                # Question 1
                qNum_sizer = wx.BoxSizer(wx.HORIZONTAL)
                qNumText = wx.StaticText(self.questions_area, wx.ID_ANY, "Question "+str(qNum)+" (" + str(self.parent.masterDatabase.getQuestionPoints(qNum)) + (" Points):" if self.parent.masterDatabase.getQuestionPoints(qNum) > 1 else " Point):"))
                boldFont = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
                qNumText.SetFont(boldFont) # applies bold font
                qNum_sizer.Add(qNumText)

                # Answer
                # 3.34
                answer = unicode(self.parent.masterDatabase.getAnswer(qNum,pretty=True))
                answerTextBox = wx.StaticText(self.questions_area, wx.ID_ANY, answer, style=wx.ALIGN_RIGHT)
                qNum_sizer.AddStretchSpacer(1) #to push button to end
                qNum_sizer.Add(answerTextBox, flag=wx.ALIGN_RIGHT|wx.ALIGN_TOP, border=0)

                #adds qNum_sizer to the panel
                self.questions_area_sizer.Add(qNum_sizer, 0, wx.EXPAND)

                # Question and Answer
                # What is the 3rd term of the sequence? 
                c_sizer = wx.BoxSizer(wx.HORIZONTAL)
                question = self.parent.masterDatabase.getQuestion(qNum, niceFormat=True)
                sizeQArea = self.questions_area.GetVirtualSize()[0]-20
                textInQandA = unicode(wordwrap(question, sizeQArea, wx.ClientDC(self.questions_area)))
                textInQandA = wx.StaticText(self.questions_area, wx.ID_ANY, textInQandA)
                c_sizer.Add(textInQandA)

                # Correct Buttons \u2714
                c_sizer.AddStretchSpacer(1) #to push buttons to end
                fullCorrect = wx.Button(self.questions_area, size=(20,20), id=wx.ID_ANY, label=u"\u2714")
                fullCorrect.SetForegroundColour((0,150,0))
                fullCorrect.SetToolTipString("Sets the question as correct")
                fullCorrect.Bind(wx.EVT_BUTTON,  lambda evt , qNum=qNum: setCorrect(qNum,1))
                c_sizer.Add(fullCorrect, 0, flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=0)

                # Half Correct Buttons \u00BD
                halfCorrect = wx.Button(self.questions_area, size=(20,20), id=wx.ID_ANY, label=u"\u00BD")
                halfCorrect.SetForegroundColour("#FFAA00")
                halfCorrect.SetToolTipString("Sets the question as half correct")
                halfCorrect.Bind(wx.EVT_BUTTON,  lambda evt , qNum=qNum: setCorrect(qNum,1.0/2))
                c_sizer.Add(halfCorrect, 0, flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=0)

                # Wrong Buttons \u2717
                markWrong = wx.Button(self.questions_area, size=(20,20), id=wx.ID_ANY, label=u"\u2717")
                markWrong.SetForegroundColour("#FF0000")
                markWrong.SetToolTipString("Sets the question as wrong")
                markWrong.Bind(wx.EVT_BUTTON, lambda evt , qNum=qNum: setCorrect(qNum,0))
                c_sizer.Add(markWrong, 0, flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=0)

                # Other Button
                otherWeight = wx.Button(self.questions_area, size=(20,20), id=wx.ID_ANY, label="?")
                otherWeight.SetToolTipString("Sets a different weight for the question.")
                otherWeight.Bind(wx.EVT_BUTTON, lambda evt , qNum=qNum: otherWeightDialog(qNum))
                c_sizer.Add(otherWeight, 0, flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=0)

                self.questions_area_sizer.Add(c_sizer, 0, wx.EXPAND)

                # Student Answer Section
                q_sizer = wx.BoxSizer(wx.HORIZONTAL)
                student_answer = wx.TextCtrl(self.questions_area, wx.ID_ANY, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH, value="")
                self.student_answer_boxes[qNum] = student_answer
                q_sizer.Add(student_answer, 1) #1, wx.EXPAND|wx.TOP|wx.RIGHT, 5
                self.questions_area_sizer.Add(q_sizer, 0, wx.EXPAND)

                # The Last Question Cleanup
                if qNum != sorted(self.parent.masterDatabase.getQuestionKeys())[-1]:
                    self.questions_area_sizer.Add(wx.StaticLine(self.questions_area, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)

            self.parent.mainpanel.Layout()

        def updateStudentAnswers(self, name):
            for qNum in self.parent.masterDatabase.getQuestionKeys():
                self.student_answer_boxes[qNum].SetLabel(unicode(self.parent.masterDatabase.getStudentAnswer(name, qNum)))
                if self.parent.masterDatabase.getStudentQuestionWeight(name, qNum) == 1:
                    self.student_answer_boxes[qNum].SetBackgroundColour("#FFFFFF")
                else:
                    if self.parent.masterDatabase.getStudentQuestionWeight(name, qNum) > 0:
                        self.student_answer_boxes[qNum].SetBackgroundColour("#FFAA00")
                    else:
                        self.student_answer_boxes[qNum].SetBackgroundColour("#FFAAAA")
            self.panel.Layout()
            self.si_right.SetValue(str(self.parent.masterDatabase.getStudentTotalWeight(name))[0:5] + " / " + str(int(self.parent.masterDatabase.getTotalQuestions())))

        def updateStudentInformation(self, name, wordauthor, excelauthor):
            self.si_name.ChangeValue(name)
            self.si_wordauthor.ChangeValue(wordauthor)
            self.si_excelauthor.ChangeValue(excelauthor)
            self.si_right.ChangeValue("")
            self.si_score.ChangeValue("")
            if self.parent.masterDatabase.getStudentAttendance(name) != False:
                self.si_attendance.ChangeValue(self.parent.masterDatabase.getStudentAttendance(name))
                self.si_attendance.SetBackgroundColour(wx.NullColour)
            else:
                self.si_attendance.SetBackgroundColour("#FFAAAA")
                self.si_attendance.ChangeValue("No Quiz")

        def setScore(self, event):
            name = self.si_name.GetValue()
            try:
                self.si_score.ChangeValue( str(self.parent.masterDatabase.getStudentTotalScore(name)) + " / " + str(self.parent.masterDatabase.getTotalPoints()) )
            except:
                pass

    def __init__(self):
        self.masterDatabase = MasterDatabase()
        wx.Frame.__init__(self, None,title="Math 130 Automated Grading System", pos=(50,50), size=(800,600), style =wx.DEFAULT_FRAME_STYLE)
        self.SetMinSize((800,600))

        # We need a panel in order to put stuff on
        # and then we are adding the things we want to see on this panel.
        self.mainpanel = wx.Panel(self, wx.ID_ANY)

        # Define most of our main sizers here
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer_a = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer_b = wx.BoxSizer(wx.HORIZONTAL)
        tree_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Set up the first layer of sizers for the top and
        # bottom panels separated by a line.
        main_sizer.Add(main_sizer_a, 1, wx.EXPAND)
        main_sizer.Add(wx.StaticLine(self.mainpanel), 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        main_sizer.Add(main_sizer_b, 0, wx.EXPAND)

        # Our top sizer contains the left hand tree list and
        # the right hand side list for the student information
        main_sizer_a.Add(tree_sizer,0,wx.ALL|wx.EXPAND,5)
        main_sizer_a.Add(right_sizer,1,wx.TOP|wx.BOTTOM|wx.RIGHT|wx.EXPAND,5)
        self.mainpanel.SetSizer(main_sizer)

        # Create our Comment Browser so that we can use it later,
        # it's hidden by default.
        self.commentWindow = CommentBrowser(self, initialSize=(500,500),initialPosition=(0,0), database=self.masterDatabase)

        # We create the MenuNav class here and pass in the self
        # argument so that we can catch it and set it as the parent
        # for the MenuClass to use as it's parent.
        self.menuNavigation = self.MenuNav(self)

        # Now we call the routines to build the main content
        self.studentTree = self.TreeNav(self, self.mainpanel, tree_sizer)
        self.questionsArea = self.QuestionsArea(self, self.mainpanel, right_sizer)
        self.buttonArea = self.BottomNav(self, self.mainpanel, main_sizer_b)

        self.mainpanel.Layout()

        self.Show()

    def deleteMeLater(self, event):
        self.masterDatabase.labFolder = os.getcwd()+"\\Examples\\Test6"
        self.masterDatabase.gradeFile = os.getcwd()+"\\Examples\\Lab 6.csv"
        self.masterDatabase.setLab("lab6")
        self.masterDatabase.loadLabs(self.masterDatabase.labFolder, self.masterDatabase.gradeFile)
        self.studentTree.updateTreeList()
        self.questionsArea.drawQuestions()
        self.lab_tree_list.SelectItem(self.lab_tree_list.GetFirstVisibleItem())
        print "Done With Sample Load"

def newSession():
    main = MainApp()

if __name__ == "__main__":
    # Error messages go to pop-up window
    # because of the redirect=True.
    app = wx.App(redirect=False)
    newSession()
    app.MainLoop()