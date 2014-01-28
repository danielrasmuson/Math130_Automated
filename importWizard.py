import embeddedImages
import wx, os
import wx.wizard as wiz
import wx.lib.filebrowsebutton as filebrowse

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
        page1 = self.TitledPage(wizard, "Introduction")
        page2 = self.TitledPage(wizard, "Select Grading Sheet")
        page3 = self.TitledPage(wizard, "Select Grading DIrectory")
        page4 = self.TitledPage(wizard, "Select Lab")

        wizard.FitToPage(page2)
        currentDirectory = os.getcwd()
        # TODO: Insert better description of what we need and what is happening.
        page1.sizer.Add(wx.StaticText(page1, -1, "This automated wizard will help you set up the\nneeded materials in order to grade your student assignments."))
        page2.sizer.Add(wx.StaticText(page2, -1, "Please select the grading file you would like to use for your section.\nThis can be found on d2l under the section > grades > export > select the lab you are grading (do not select multiple labs)\nOnce grading is finished you will be able to upload this file to d2l."))
        self.gradingSheet = filebrowse.FileBrowseButton(page2, -1, size=(450, -1), labelText="Grading Sheet (.csv)", fileMask="*.csv", startDirectory=currentDirectory)
        page2.sizer.Add(self.gradingSheet)

        page3.sizer.Add(wx.StaticText(page3, -1, "Please select the directory for grading.\nThis can be found under the lab section > dropbox > select the dropbox for the lab > files > select all > download > unzip"))
        self.gradingDirectory = filebrowse.DirBrowseButton(page3, -1, size=(450, -1), labelText="Lab Directory", startDirectory=currentDirectory)
        page3.sizer.Add(self.gradingDirectory)

        page4.sizer.Add(wx.StaticText(page4, -1, "Lab Selection will be done here eventually and also show final results."))
        self.labDictionaryFile = filebrowse.FileBrowseButton(page4, -1, size=(450, -1), labelText="Lab Dict (.dat)", fileMask="*.dat", startDirectory=currentDirectory)
        page4.sizer.Add(self.labDictionaryFile)
        
        # Set the initial order of the pages
        page1.SetNext(page2)
        page2.SetPrev(page1)
        page2.SetNext(page3)
        page3.SetPrev(page2)
        page3.SetNext(page4)
        page4.SetPrev(page3)

        wizard.GetPageAreaSizer().Add(page1)
        wizard.RunWizard(page1)
        wizard.Destroy()

if __name__ == "__main__":
    app = wx.App(False)
    w = ImportWizard()
    print w.gradingSheet.GetValue()
    app.MainLoop()