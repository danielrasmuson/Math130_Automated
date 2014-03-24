# -*- coding: utf8 -*-
from __future__ import division
import wx, os, subprocess, difflib, glob, embeddedImages, ConfigParser, codecs
from wx.lib.wordwrap import wordwrap
from exportGrade import exportGrade
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

            m_new = wx.MenuItem(fileMenu, wx.ID_NEW, "&New Grading Session\tCtrl-N", "Removes all of the students and the currently loaded dictionary.")
            m_new.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_MENU))
            fileMenu.AppendItem(m_new)

            m_save = wx.MenuItem(fileMenu, wx.ID_SAVE, "&Save Grading Session\tCtrl-S", "Saves the current grading progress to disk.")
            m_save.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_MENU))
            fileMenu.AppendItem(m_save)

            m_open = wx.MenuItem(fileMenu, wx.ID_OPEN, "&Open Grading Session\tCtrl-O", "Opens a previous grading session from disk.")
            m_open.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU))
            fileMenu.AppendItem(m_open)

            m_wizard = wx.MenuItem(fileMenu,wx.ID_ANY, "Import &Wizard\tCtrl-W", "Opens the guided wizard for the setup process.")
            m_wizard.SetBitmap(wx.BitmapFromImage(wx.ImageFromBitmap(embeddedImages.wizard.GetBitmap()).Scale(16,16, wx.IMAGE_QUALITY_HIGH)))
            fileMenu.AppendItem(m_wizard)
            fileMenu.AppendSeparator()


            m_default = fileMenu.Append(wx.ID_ANY, "&Default Load Stuffs (Delete Me Later)\tCtrl-D", "Loads all of the above stuff in one click.  Will get deleted later.")
            fileMenu.AppendSeparator()

            m_exit = wx.MenuItem(fileMenu, wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
            m_exit.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU))
            fileMenu.AppendItem(m_exit)

            self.parent.Bind(wx.EVT_MENU, self.onNew, m_new)
            self.parent.Bind(wx.EVT_MENU, self.onSave, m_save)
            self.parent.Bind(wx.EVT_MENU, self.onOpen, m_open)
            self.parent.Bind(wx.EVT_MENU, self.wizardEvent, m_wizard)
            self.parent.Bind(wx.EVT_MENU, self.parent.deleteMeLater, m_default)
            self.parent.Bind(wx.EVT_MENU, self.onClose, m_exit)
            menuBar.Append(fileMenu, "&File")

            helpMenu = wx.Menu()
            m_about = wx.MenuItem(helpMenu, wx.ID_ABOUT, "&About", "Information about this program")
            m_about.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_MENU))
            helpMenu.AppendItem(m_about)
            self.parent.Bind(wx.EVT_MENU, self.onAbout, m_about)
            menuBar.Append(helpMenu, "&Help")

            self.parent.SetMenuBar(menuBar)

            # self.parent.statusbar = self.parent.CreateStatusBar()

        def wizardEvent(self, event):
            tempwiz = ImportWizard(self.parent)

        def onSave(self, event):
            if len(self.parent.tree_rootDict.keys()) == 0:
                wx.MessageBox("Nothing to save.","Warning", wx.OK | wx.ICON_INFORMATION)
            else:
                dlg = wx.FileDialog(self.parent, "Choose a lab file:",defaultFile=str(self.parent.masterDatabase.currentLab)+"-"+str(self.parent.tree_rootDict.keys()[0]).lstrip("0"),defaultDir=self.parent.config.get("Main_Gui","save_dir"), style=wx.FD_SAVE|wx.OVERWRITE_PROMPT)
                dlg.SetWildcard("Lab Dictionaries (*.dat)|*.dat")
                if dlg.ShowModal() == wx.ID_OK:
                    self.parent.masterDatabase.saveProgress(dlg.GetPath())
                    self.parent.config.set("Main_Gui","save_dir",os.path.dirname(dlg.GetPath()))
                    self.parent.config.write(open("Math130.ini", "wb"))
                dlg.Destroy()

        def onOpen(self, event):
            dlg = wx.FileDialog(self.parent, "Choose a lab file:",defaultFile="",defaultDir=self.parent.config.get("Main_Gui","save_dir"), style=wx.FD_OPEN)
            dlg.SetWildcard("Lab Dictionaries (*.dat)|*.dat")
            if dlg.ShowModal() == wx.ID_OK:
                self.parent.masterDatabase.loadProgress(dlg.GetPath())
                self.parent.treeArea.updateTreeList()
                self.parent.questionsArea.drawQuestions()
                self.parent.labTree.SelectItem(self.parent.labTree.GetFirstVisibleItem())
                self.parent.config.set("Main_Gui","save_dir",os.path.dirname(dlg.GetPath()))
                self.parent.config.write(open("Math130.ini", "wb"))
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
                # Save our configuration stuff in case something borks later.
                self.parent.config.set("Main_Gui","size_x",str(self.parent.GetSize()[0]))
                self.parent.config.set("Main_Gui","size_y",str(self.parent.GetSize()[1]))
                self.parent.config.set("Main_Gui","pos_x",str(self.parent.GetScreenPosition()[0]))
                self.parent.config.set("Main_Gui","pos_y",str(self.parent.GetScreenPosition()[1]))
                self.parent.config.write(open("Math130.ini", "wb"))
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

            self.b_cheat = wx.Button(panel, wx.ID_ANY, "Cheat Check", style=wx.BU_EXACTFIT)
            self.b_cheat.SetToolTipString("Runs some basic cheat detection on the currently loaded students.")
            self.b_cheat.SetBitmap(wx.BitmapFromImage(wx.ImageFromBitmap(embeddedImages.cheat.GetBitmap()).Scale(20,20, wx.IMAGE_QUALITY_HIGH)))
            self.b_cheat.Bind(wx.EVT_BUTTON, self.ratioCheck)
            self.b_cheat.Bind(wx.EVT_BUTTON, self.cheatCheck)
            sizer.Add(self.b_cheat, 0,wx.ALL,4)

            sizer.AddStretchSpacer(1)

            def _combinedGrade(event):
                name = self.parent.questionsArea.si_name.GetValue()
                if name in self.parent.masterDatabase.studentList.keys():
                    self.parent.masterDatabase._gradeStudentExcel(name)
                    self.parent.masterDatabase._gradeStudentWord(name)
                    self.parent.questionsArea.updateStudentAnswers(name)

            self.b_regrade = wx.Button(panel, wx.ID_ANY, "Regrade", style=wx.BU_EXACTFIT)
            self.b_regrade.SetToolTipString("Regrades the current student.")
            self.b_regrade.SetBitmap(wx.BitmapFromImage(wx.ImageFromBitmap(embeddedImages.regrade.GetBitmap()).Scale(19,20, wx.IMAGE_QUALITY_HIGH)))
            self.b_regrade.Bind(wx.EVT_BUTTON, _combinedGrade)
            sizer.Add(self.b_regrade, 0,wx.ALL,4)

            self.b_comments = wx.Button(panel, wx.ID_ANY, "Comments", style=wx.BU_EXACTFIT)
            self.b_comments.SetToolTipString("Opens a new dialog box with extra comments (if available) for the current student.")
            self.b_comments.SetBitmap(wx.BitmapFromImage(wx.ImageFromBitmap(embeddedImages.comments.GetBitmap()).Scale(20,20, wx.IMAGE_QUALITY_HIGH)))
            self.b_comments.Bind(wx.EVT_BUTTON, self.parent.commentWindow.display)
            sizer.Add(self.b_comments, 0,wx.ALL,4)

            b_open = wx.Button(panel, wx.ID_ANY, "Word Doc", style=wx.BU_EXACTFIT)
            b_open.SetToolTipString("Opens the document in word.")
            b_open.SetBitmap(embeddedImages.word.GetBitmap())
            b_open.Bind(wx.EVT_BUTTON, self.openDocument)
            sizer.Add(b_open, 0,wx.ALL,4)

            self.b_open_excel = wx.Button(panel, wx.ID_ANY, "Excel Doc", style=wx.BU_EXACTFIT)
            self.b_open_excel.SetToolTipString("Opens the excel document if available.")
            self.b_open_excel.SetBitmap(embeddedImages.excel.GetBitmap())
            self.b_open_excel.Disable()
            self.b_open_excel.Bind(wx.EVT_BUTTON, self.openExcel)
            sizer.Add(self.b_open_excel, 0,wx.ALL,4)

            # A button for sending the grade to the excel file
            b_grade = wx.Button(panel, wx.ID_ANY, "Submit Grade", style=wx.BU_EXACTFIT)
            b_grade.SetToolTipString("Sends the grade to excel file")
            b_grade.SetBitmap(wx.BitmapFromImage(wx.ImageFromBitmap(embeddedImages.submit.GetBitmap()).Scale(20,20, wx.IMAGE_QUALITY_HIGH)))
            b_grade.Bind(wx.EVT_BUTTON, self.submitGrade)
            sizer.Add(b_grade, 0,wx.ALL,4)

        def openDocument(self, event):
            try:
                current_item = self.parent.treeArea.getSelected()
                if "Section" not in current_item:
                    subprocess.Popen(["explorer",self.parent.masterDatabase.getStudentWordFilepath(current_item)], shell=False)
            except:
                pass

        def openExcel(self, event):
            subprocess.Popen(["explorer",self.parent.xlsx_path], shell=False)

        def submitGrade(self, event):
            # @TODO: right answers should be divided by the total score (30 points)
            name = self.parent.questionsArea.si_name.GetValue()
            name = name.split()
            score = self.parent.questionsArea.si_score.GetValue()
            if len(name) > 0:
                if self.parent.questionsArea.si_attendance.GetValue() == "No Quiz":
                    dlg = wx.MessageDialog(self.parent,name[0] + "did not take the attendance quiz. Submit 0 instead of "+str(score)+"?","Confirmation", wx.YES_NO | wx.ICON_QUESTION)
                    result = dlg.ShowModal()
                    dlg.Destroy()
                    if result == wx.ID_YES:
                        score = "0"
                result = exportGrade(self.parent.masterDatabase.gradeFile, name[0], " ".join(name[1:]), score)
                if result:
                    self.parent.masterDatabase.setStudentSubmittedGrade(str(self.parent.questionsArea.si_name.GetValue()),True)
                    self.parent.labTree.SetItemText(self.parent.labTree.GetSelection(), u"\u2714"+self.parent.questionsArea.si_name.GetValue())
                    self.parent.labTree.SetItemTextColour(self.parent.labTree.GetSelection(), (0,150,0))
                else:
                    wx.MessageBox("Unable to find "+name[0]+" in the file "+self.parent.masterDatabase.gradeFile,"Grade Not Submitted!", wx.OK | wx.ICON_ERROR)
            self.parent.treeArea.nextButton("")

        def ratioCheck(self, event):
            """ Checks for the ratio of similarity between all of the labs, but it slower than other method. """
            names = sorted(self.parent.masterDatabase.getStudentKeys())
            if len(names) > 0:
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
            if len(names) > 0:
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

            self.parent.labTree = wx.TreeCtrl(panel, 1, size=wx.Size(200,-1),style=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT)
            self.parent.labTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelChanged, id=1)
            lab_tree_label = wx.StaticText(panel, wx.ID_ANY, 'Student List')
            self.parent.tree_root = self.parent.labTree.AddRoot("Lab Sections")
            self.parent.tree_rootDict = {}

            sizer.Add(lab_tree_label,0,wx.ALIGN_CENTER)
            sizer.Add(self.parent.labTree, 1,wx.EXPAND)

            sButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(sButtonSizer, 0, wx.ALIGN_CENTER)

            b_prev = wx.Button(panel, wx.ID_ANY, "Previous", size=wx.Size(80,20), style=wx.BU_EXACTFIT)
            b_prev.SetBitmap(embeddedImages.arrowLeft.GetBitmap())
            b_prev.SetToolTipString("Selects the previous student of the current section.")
            b_prev.Bind(wx.EVT_BUTTON, self.previousButton)
            sButtonSizer.Add(b_prev, 0,wx.ALIGN_CENTER|wx.ALL,5)

            b_next = wx.Button(panel, wx.ID_ANY, "Next", size=wx.Size(80,20), style=wx.BU_EXACTFIT)
            b_next.SetBitmap(embeddedImages.arrowRight.GetBitmap(), wx.RIGHT)
            b_next.SetToolTipString("Selects the next student of the current section")
            b_next.Bind(wx.EVT_BUTTON, self.nextButton)
            sButtonSizer.Add(b_next, 0,wx.ALIGN_CENTER|wx.ALL,5)

        def previousButton(self, event):
            try:
                current = self.parent.labTree.GetSelection()
                prev = self.parent.labTree.GetPrevSibling(current)
                if prev.IsOk() and not self.parent.labTree.ItemHasChildren(prev):
                    self.parent.labTree.SelectItem(prev)
                    self.parent.questionsArea.scrollTop()
                elif prev.IsOk() and  self.parent.labTree.ItemHasChildren(prev):
                    self.parent.labTree.SelectItem(self.parent.labTree.GetLastChild(prev))
                else:
                    parent = self.parent.labTree.GetItemParent(self.parent.labTree.GetSelection())
                    if parent != self.parent.labTree.GetRootItem():
                        self.parent.labTree.SelectItem(parent)
            except:
                pass

        def nextButton(self, event):
            try:
                current = self.parent.labTree.GetSelection()
                if self.parent.labTree.ItemHasChildren(current):
                    next = self.parent.labTree.GetFirstChild(current)[0]
                else:
                    next = self.parent.labTree.GetNextSibling(current)
                if next.IsOk():
                    self.parent.labTree.SelectItem(next)
                    self.parent.questionsArea.scrollTop()
                else:
                    parent = self.parent.labTree.GetItemParent(self.parent.labTree.GetSelection())
                    if self.parent.labTree.GetNextSibling(parent).IsOk():
                        self.parent.labTree.SelectItem(self.parent.labTree.GetNextSibling(parent))
            except:
                pass

        def getSelected(self):
            return str(self.parent.labTree.GetItemText(self.parent.labTree.GetSelection()).strip(u"\u2714"))

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

        def updateTreeList(self):
            """Tree List on Left Side - Dynamic to Files"""
            for name in sorted(self.parent.masterDatabase.getStudentKeys()):
                sec = self.parent.masterDatabase.getStudentSection(name)
                if sec == "MissingInformation":
                    self.parent.tree_rootDict[sec] = self.parent.labTree.AppendItem(self.parent.tree_root, "Missing Lab Section")
                    self.parent.labTree.SetItemBackgroundColour(self.parent.tree_rootDict[sec],"#FFAAAA")
                elif sec not in self.parent.tree_rootDict.keys(): #creates root section if there isn't one
                    self.parent.tree_rootDict[sec] = self.parent.labTree.AppendItem(self.parent.tree_root, "Section "+sec)
                # During update check if submitted or not and then append on to tree.
                if self.parent.masterDatabase.getStudentSubmittedGrade(name):
                    temp = self.parent.labTree.AppendItem(self.parent.tree_rootDict[sec], u"\u2714" + name)
                    self.parent.labTree.SetItemTextColour(temp, (0,150,0))
                else:
                    self.parent.labTree.AppendItem(self.parent.tree_rootDict[sec], name)

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

            self.questionTextCtrls = []
            self.panel.Bind(wx.EVT_SIZE, self.updateWordwrap)

        def getColor(self,weight):
            # Just an easy way to color specific weight ranges to be consistent.
            if weight == 1:
                return "#FFFFFF"
            elif weight == 0:
                return "#FF2200"
            elif weight == .5:
                return "#FFAA00"
            elif weight > .5:
                return "#FFD47F"
            elif weight < .5:
                return "#FF6600"

        def scrollTop(self):
            self.stagingArea.Scroll((0,0))

        def updateWordwrap(self,event):
            for textCtrl,text in self.questionTextCtrls:
                textCtrl.SetLabel(unicode(wordwrap(text.replace("\n",""), self.sizer.GetSizeTuple()[0]-90, wx.ClientDC(self.stagingArea))))
            self.parent.mainpanel.Layout()

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
                self.student_answer_boxes[qNum].SetBackgroundColour(self.getColor(weight))
                self.student_answer_boxes[qNum].Refresh() #fix for delay

                self.parent.masterDatabase.setStudentQuestionWeight(name, qNum, weight)
                self.parent.commentWindow.defaultCommentButton("")
                self.si_right.SetValue(str(self.parent.masterDatabase.getStudentTotalWeight(name))[0:5] + " / " + str(int(self.parent.masterDatabase.getTotalQuestions())))

            self.stagingArea = wx.ScrolledWindow(self.panel)
            self.stagingArea.SetScrollbars(1, 15, 200, 200)
            self.stagingArea.EnableScrolling(True,True)
            self.sizer.Add(self.stagingArea, 1, wx.EXPAND)

            self.stagingArea_sizer = wx.BoxSizer(wx.VERTICAL)
            self.stagingArea.SetSizer(self.stagingArea_sizer)

            self.student_answer_boxes = {}
            for qNum in sorted(self.parent.masterDatabase.getQuestionKeys()):


                # Question Num
                # Question 1
                qNum_sizer = wx.BoxSizer(wx.HORIZONTAL)
                qNumText = wx.StaticText(self.stagingArea, wx.ID_ANY, "Question "+str(qNum)+" (" + str(self.parent.masterDatabase.getQuestionPoints(qNum)) + (" Points):" if self.parent.masterDatabase.getQuestionPoints(qNum) > 1 else " Point):"))
                boldFont = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
                qNumText.SetFont(boldFont) # applies bold font
                qNum_sizer.Add(qNumText)

                # Answer
                # 3.34
                answer = unicode(self.parent.masterDatabase.getAnswer(qNum,pretty=True))
                answerTextBox = wx.StaticText(self.stagingArea, wx.ID_ANY, answer, style=wx.ALIGN_RIGHT)
                qNum_sizer.AddStretchSpacer(1) #to push button to end
                qNum_sizer.Add(answerTextBox, flag=wx.ALIGN_RIGHT|wx.ALIGN_TOP, border=0)

                #adds qNum_sizer to the panel
                self.stagingArea_sizer.Add(qNum_sizer, 0, wx.EXPAND)

                # Question and Answer
                # What is the 3rd term of the sequence? 
                c_sizer = wx.BoxSizer(wx.HORIZONTAL)
                question = self.parent.masterDatabase.getQuestion(qNum, niceFormat=True)
                sizeQArea = self.sizer.GetSize()[0]-90
                text = unicode(wordwrap(question, sizeQArea, wx.ClientDC(self.stagingArea)))
                textCtrl = wx.StaticText(self.stagingArea, wx.ID_ANY, text)
                c_sizer.Add(textCtrl)
                self.questionTextCtrls.append([textCtrl,text])

                # Correct Buttons \u2714
                c_sizer.AddStretchSpacer(1) #to push buttons to end
                fullCorrect = wx.Button(self.stagingArea, size=(20,20), id=wx.ID_ANY, label=u"\u2714")
                fullCorrect.SetForegroundColour((0,150,0))
                fullCorrect.SetToolTipString("Sets the question as correct")
                fullCorrect.Bind(wx.EVT_BUTTON,  lambda evt , qNum=qNum: setCorrect(qNum,1))
                c_sizer.Add(fullCorrect, 0, flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=0)

                # Half Correct Buttons \u00BD
                halfCorrect = wx.Button(self.stagingArea, size=(20,20), id=wx.ID_ANY, label=u"\u00BD")
                halfCorrect.SetForegroundColour("#FFAA00")
                halfCorrect.SetToolTipString("Sets the question as half correct")
                halfCorrect.Bind(wx.EVT_BUTTON,  lambda evt , qNum=qNum: setCorrect(qNum,1.0/2))
                c_sizer.Add(halfCorrect, 0, flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=0)

                # Wrong Buttons \u2717
                markWrong = wx.Button(self.stagingArea, size=(20,20), id=wx.ID_ANY, label=u"\u2717")
                markWrong.SetForegroundColour("#FF0000")
                markWrong.SetToolTipString("Sets the question as wrong")
                markWrong.Bind(wx.EVT_BUTTON, lambda evt , qNum=qNum: setCorrect(qNum,0))
                c_sizer.Add(markWrong, 0, flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=0)

                # Other Button
                otherWeight = wx.Button(self.stagingArea, size=(20,20), id=wx.ID_ANY, label="?")
                otherWeight.SetToolTipString("Sets a different weight for the question.")
                otherWeight.Bind(wx.EVT_BUTTON, lambda evt , qNum=qNum: otherWeightDialog(qNum))
                c_sizer.Add(otherWeight, 0, flag=wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=0)

                self.stagingArea_sizer.Add(c_sizer, 0, wx.EXPAND)

                # Student Answer Section
                q_sizer = wx.BoxSizer(wx.HORIZONTAL)
                student_answer = wx.TextCtrl(self.stagingArea, wx.ID_ANY, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH, value="")
                self.student_answer_boxes[qNum] = student_answer
                q_sizer.Add(student_answer, 1) #1, wx.EXPAND|wx.TOP|wx.RIGHT, 5
                self.stagingArea_sizer.Add(q_sizer, 0, wx.EXPAND)

                # The Last Question Cleanup
                if qNum != sorted(self.parent.masterDatabase.getQuestionKeys())[-1]:
                    self.stagingArea_sizer.Add(wx.StaticLine(self.stagingArea, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)

            self.parent.mainpanel.Layout()

        def updateStudentAnswers(self, name):
            for qNum in self.parent.masterDatabase.getQuestionKeys():
                self.student_answer_boxes[qNum].SetLabel(unicode(self.parent.masterDatabase.getStudentAnswer(name, qNum)))
                self.student_answer_boxes[qNum].SetBackgroundColour(self.parent.questionsArea.getColor(self.parent.masterDatabase.getStudentQuestionWeight(name, qNum)))
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
        # Trying to keep track of personal settings and locations of files
        # so we don't have to keep navigating to folders to find our labs.
        self.config = ConfigParser.SafeConfigParser()
        try:
            with codecs.open('Math130.ini', 'r', encoding='utf-8') as f:
                self.config.readfp(f)
        except:
            print "Creating default configuration file: " + str(os.getcwd()) + "\\Math130.ini"
            open(str(os.getcwd()) + "\\Math130.ini", 'a').close()
        if not self.config.has_section("Main_Gui"):
            self.config.add_section("Main_Gui")

        optionsList = ["pos_x","pos_y","size_x","size_y","save_dir"]
        defaultOptions = [50,50,800,600,""]
        for i, option in enumerate(optionsList):
            if option not in self.config.options("Main_Gui"):
                self.config.set("Main_Gui",option,str(defaultOptions[i]))

        pos_x = int(self.config.get("Main_Gui","pos_x"))
        pos_y = int(self.config.get("Main_Gui","pos_y"))
        size_x = int(self.config.get("Main_Gui","size_x"))
        size_y = int(self.config.get("Main_Gui","size_y"))

        wx.Frame.__init__(self, None,title="Math 130 Automated Grading System", pos=(pos_x,pos_y), size=(size_x,size_y), style =wx.DEFAULT_FRAME_STYLE)
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
        main_sizer_a.Add(tree_sizer,0,wx.TOP|wx.RIGHT|wx.LEFT|wx.EXPAND,5)
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
        self.treeArea = self.TreeNav(self, self.mainpanel, tree_sizer)
        self.questionsArea = self.QuestionsArea(self, self.mainpanel, right_sizer)
        self.buttonArea = self.BottomNav(self, self.mainpanel, main_sizer_b)

        self.mainpanel.Layout()

        self.Show()

    def deleteMeLater(self, event):
        self.masterDatabase.labFolder = os.getcwd()+"\\Examples\\Test8"
        self.masterDatabase.gradeFile = os.getcwd()+"\\Examples\\Lab 8.csv"
        self.masterDatabase.setLab("lab8")
        self.masterDatabase.loadLabs(self.masterDatabase.labFolder, self.masterDatabase.gradeFile)
        self.treeArea.updateTreeList()
        self.questionsArea.drawQuestions()
        self.labTree.SelectItem(self.labTree.GetFirstVisibleItem())
        print "Done With Sample Load"

def newSession():
    main = MainApp()

if __name__ == "__main__":
    # Error messages go to pop-up window
    # because of the redirect=True.
    app = wx.App(redirect=False)
    newSession()
    app.MainLoop()