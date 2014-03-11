import embeddedImages
import wx
import os
import wx.wizard as wiz
import wx.lib.filebrowsebutton as filebrowse
from wx.lib.wordwrap import wordwrap


class ImportWizard:

    class TitledPage(wiz.WizardPageSimple):

        def __init__(self, parent, title):
            """Constructor"""
            wiz.WizardPageSimple.__init__(self, parent)

            sizer = wx.BoxSizer(wx.VERTICAL)
            self.sizer = sizer
            self.SetSizer(sizer)

            title = wx.StaticText(self, -1, title)
            title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
            sizer.Add(title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)

    def __init__(self, parent):
        wizard = wiz.Wizard(
            None, -1, "Lab Grading Wizard", embeddedImages.SideImage.GetBitmap())
        self.parent = parent
        currentDirectory = os.path.expanduser('~') + "/Desktop/"
        wizard.Bind(wiz.EVT_WIZARD_FINISHED, self.onFinished)

        # page 1 - Intro
        page1 = self.TitledPage(wizard, "Introduction")
        page1text = "This automated wizard will help you set up the needed materials in order to grade your student assignments."
        page1.sizer.Add(
            wx.StaticText(page1, -1, str(wordwrap(page1text, 500, wx.ClientDC(page1)))))

        # page 2 - Import File
        page2 = self.TitledPage(wizard, "Select Grading Sheet")
        page2text = "Please select the grading file you would like to use for your section.\nThis can be found on d2l under the section > grades > export > select the lab you are grading (do not select multiple labs)\nOnce grading is finished you will be able to upload this file to d2l."
        page2.sizer.Add(
            wx.StaticText(page2, -1, str(wordwrap(page2text, 500, wx.ClientDC(page2)))))
        self.gradingSheet = filebrowse.FileBrowseButton(
            page2, -1, size=(450, -1), labelText="Grading Sheet:", fileMask="Grading Sheet|Finite*.csv|All CSV (*.csv)|*.csv|All Files (*.*)|*.*", startDirectory=currentDirectory)
        page2.sizer.Add(self.gradingSheet, 1, flag=wx.ALIGN_CENTER)

        # page 3 - Optional Attendance
        page3 = self.TitledPage(wizard, "Select (Optional) Attendance Sheet")
        page3text = "This is an optional thing you can select if you'd like to automatically check if the student took the attendance quiz or not."
        page3.sizer.Add(
            wx.StaticText(page3, -1, str(wordwrap(page3text, 500, wx.ClientDC(page3)))))
        self.attendanceSheet = filebrowse.FileBrowseButton(
            page3, -1, size=(450, -1), labelText="Attendance File:", fileMask="Attendance File|Att*.csv|All CSV (*.csv)|*.csv|All Files (*.*)|*.*", startDirectory=self.gradingSheet.GetValue())
        page3.sizer.Add(self.attendanceSheet, 1, flag=wx.ALIGN_CENTER)

        # page 4 - Optional Email
        # @TODO - chang ethe foamatting of this page to look better
        page4 = self.TitledPage(wizard, "Input (Optional) Email Sheet")
        page4text = "This is an optional setting to email your results to the students. You need to navigate to d2l and click classlist then select all students and click email. Copy the bcc field and paste it below along with your credentials to your mnsu email."
        page4.sizer.Add(
            wx.StaticText(page4, 1, str(wordwrap(page4text, 500, wx.ClientDC(page4)))))

        # MNSU Email Address - MNSU Star ID:' - 'Email password:' - classList
        # string
        self.emailAddress = wx.TextCtrl(page4, value="") 
        self.emailStarID = wx.TextCtrl(page4, value="") 
        self.emailPassword = wx.TextCtrl(page4, value="", style=wx.TE_PASSWORD) 
        self.emailStudents = wx.TextCtrl(page4, style=wx.TE_MULTILINE, value="") # TODO - make this strech across horizontal too 

        page4.sizer.Add(wx.StaticText(page4, label="MNSU Email:"))
        page4.sizer.Add(self.emailAddress)
        page4.sizer.Add(wx.StaticText(page4, label="Star ID:"))
        page4.sizer.Add(self.emailStarID)
        page4.sizer.Add(wx.StaticText(page4, label="Email Password:"))
        page4.sizer.Add(self.emailPassword)
        page4.sizer.Add(wx.StaticText(page4, label="Enter D2L Email String:"))
        page4.sizer.Add(self.emailStudents, 1)

        # page 5 - Lab Directory
        page5 = self.TitledPage(wizard, "Select Grading Directory")
        page5text = "Please select the directory for grading.\nThis can be found under the lab section > dropbox > select the dropbox for the lab > files > select all > download > unzip"
        page5.sizer.Add(
            wx.StaticText(page5, -1, str(wordwrap(page5text, 500, wx.ClientDC(page5)))))
        self.gradingDirectory = filebrowse.DirBrowseButton(
            page5, -1, size=(450, -1), labelText="Lab Directory", startDirectory=self.gradingSheet.GetValue())
        page5.sizer.Add(self.gradingDirectory, 1, flag=wx.ALIGN_CENTER)

        wizard.FitToPage(page1)

        # Set the initial order of the pages
        page1.SetNext(page2)
        page2.SetPrev(page1)
        page2.SetNext(page3)
        page3.SetPrev(page2)
        page3.SetNext(page4)
        page4.SetPrev(page3)
        page4.SetNext(page5)
        page5.SetPrev(page4)

        wizard.GetPageAreaSizer().Add(page1)
        wizard.RunWizard(page1)

        # end
        wizard.Destroy()

    def getLabName(self, filePath):
        """gets lab number from import file"""
        textFile = open(filePath, "r")
        fullText = textFile.read()
        textFile.close()

        labNameList = fullText.split(",")[3].split()[:2]
        return "".join(labNameList).lower()

    def onFinished(self, event):
        self.parent.masterDatabase.gradeFile = self.gradingSheet.GetValue()
        self.parent.masterDatabase.labFolder = self.gradingDirectory.GetValue()
        if len(self.parent.masterDatabase.gradeFile) and len(self.parent.masterDatabase.labFolder):
            self.labName = self.getLabName(self.gradingSheet.GetValue())
            self.parent.masterDatabase.setLab(self.labName)
            self.parent.masterDatabase.loadLabs(
                self.parent.masterDatabase.labFolder, self.parent.masterDatabase.gradeFile)
            self.parent.treeArea.updateTreeList()
            self.parent.questionsArea.drawQuestions()
            self.parent.labTree.SelectItem(
                self.parent.labTree.GetFirstVisibleItem())

        if len(self.attendanceSheet.GetValue()):
            self.parent.masterDatabase.checkAttendance(
                self.attendanceSheet.GetValue())

        if len(self.emailAddress.GetValue()) and len(self.emailStarID.GetValue()) and len(self.emailPassword.GetValue()) and len(self.emailStudents.GetValue()):
            self.parent.commentWindow.username = self.emailAddress.GetValue()
            self.parent.commentWindow.starid = self.emailStarID.GetValue()
            self.parent.commentWindow.password = self.emailPassword.GetValue()
            self.parent.commentWindow.userEmailString = self.emailStudents.GetValue()
            self.parent.commentWindow.loadEmailList()
            print "email done"

        print "Done With Wizard Load"


if __name__ == "__main__":
    app = wx.App(False)
    w = ImportWizard("")
    print w.gradingSheet.GetValue()
    app.MainLoop()
