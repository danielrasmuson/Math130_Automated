import embeddedImages
import wx, os
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
            sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 5)

    def __init__(self):
        wizard = wiz.Wizard(None, -1, "Lab Grading Wizard", embeddedImages.SideImage.GetBitmap())
        currentDirectory = os.getcwd()

        #page 1 - Intro
        page1 = self.TitledPage(wizard, "Introduction")
        page1text = "This automated wizard will help you set up the needed materials in order to grade your student assignments."
        page1.sizer.Add(wx.StaticText(page1, -1, str(wordwrap(page1text, 500, wx.ClientDC(page1))) ))

        #page 2 - Import File
        page2 = self.TitledPage(wizard, "Select Grading Sheet")
        page2text = "Please select the grading file you would like to use for your section.\nThis can be found on d2l under the section > grades > export > select the lab you are grading (do not select multiple labs)\nOnce grading is finished you will be able to upload this file to d2l."
        page2.sizer.Add(wx.StaticText(page2, -1, str(wordwrap(page2text, 500, wx.ClientDC(page2))) ))
        self.gradingSheet = filebrowse.FileBrowseButton(page2, -1, size=(450, -1), labelText="Grading Sheet (.csv)", fileMask="*.csv", startDirectory=currentDirectory)
        page2.sizer.Add(self.gradingSheet, 1, flag=wx.ALIGN_CENTER)

        #page 3 - Lab Directory
        page3 = self.TitledPage(wizard, "Select Grading DIrectory")
        page3text = "Please select the directory for grading.\nThis can be found under the lab section > dropbox > select the dropbox for the lab > files > select all > download > unzip"
        page3.sizer.Add(wx.StaticText(page3, -1, str(wordwrap(page3text, 500, wx.ClientDC(page3))) ))
        self.gradingDirectory = filebrowse.DirBrowseButton(page3, -1, size=(450, -1), labelText="Lab Directory", startDirectory=currentDirectory)
        page3.sizer.Add(self.gradingDirectory, 1, flag=wx.ALIGN_CENTER)

        wizard.FitToPage(page1)
        # @TODO : add email setup in wizard

        # Set the initial order of the pages
        page1.SetNext(page2)
        page2.SetPrev(page1)
        page2.SetNext(page3)
        page3.SetPrev(page2)

        wizard.GetPageAreaSizer().Add(page1)
        wizard.RunWizard(page1)

        #page 4 - Lab Number
        labName = self.getLabName(self.gradingSheet.GetValue())
        self.labDictionaryFile = "Labs\\"+ labName + ".dat"

        #end
        wizard.Destroy()

    def getLabName(self, filePath):
        """gets lab number from import file"""
        textFile = open(filePath,"r")
        fullText = textFile.read()
        textFile.close()

        labNameList = fullText.split(",")[3].split()[:2]
        return "".join(labNameList).lower()


if __name__ == "__main__":
    app = wx.App(False)
    w = ImportWizard()
    print w.gradingSheet.GetValue()
    app.MainLoop()