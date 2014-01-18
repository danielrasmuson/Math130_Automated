#TODO
#see the name an stuff above the assignment
    #names and info
    #seperator
    #what I currently see
#grades assignments
    #takes a list of correct answers
    #checks question to see if it contains anything
    #scores box on the side and colors the box
    #if I click inside the box its then scored
#I can adjust grades
    #I can adjust the score inside the box
#finally exports grades
    #after each grade there is a confirm button I click it then writes the file

from docx import opendocx, getdocumenttext
import wx
import os


def getAssignmentStack(folderName):
    fileNameList = os.listdir(folderName)
    assignments = [] #  a list of instance variables of assignment
    for fileName in fileNameList:
        assignments.append(assignment(folderName+"\\"+fileName))
    return assignments


class assignment():
    def __init__(self, filePath):
        self.filePath = filePath
        self.document = self.setDocumentStr()

        studentInfo, answersList = self.setAandInfo()
        self.name = studentInfo[0]
        self.techid = studentInfo[1]
        self.section = studentInfo[2]
        self.nameStr = "\n".join(studentInfo[:3])
        self.answerList = answersList
        self.answerStr = "\n\n".join(answersList)

    def setDocumentStr(self):
        docxDocument = opendocx(self.filePath)
        paratextlist = getdocumenttext(docxDocument)
        documentList = []
        for paratext in paratextlist:
            documentList.append(paratext.encode("utf-8"))

        return "".join(documentList)

    def setAandInfo(self):
        documentList = self.document.split("<!")
        answerList = []
        for answer in documentList:
            if "!>" in answer:
                answerList.append(answer[:answer.index("!>")])

        answers = []
        for i in range(3,len(answerList)):
            answers.append(str(i-2)+". "+answerList[i])

        studentInfo = answerList[:3]
        return [studentInfo, answers]


class Example(wx.Frame):
  
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title, 
            size=(700, 700))
            
        self.InitUI()
        self.Centre()
        self.Show()     
        
    def InitUI(self):

        self.panel = wx.Panel(self)
        self.assignmentStack = assignmentStack
        self.next = 0  # controls position of stack

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.name = wx.StaticText(self.panel, label="Daniel") #----- REPLACE HERE ----
        hbox1.Add(self.name, flag=wx.RIGHT, border=8)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1, 10))

        #should make each question an element
            #then I can add buttons on top of those elements
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.updateAssignment()
        # self.assignment = wx.StaticText(self.panel, label="Answer1\nAnswer2\nAnswer3") #----- REPLACE HERE ----
        hbox2.Add(self.assignment, flag=wx.RIGHT, border=8)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1, 10))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.pButton =wx.Button(self.panel, label="Previous", pos=(0, 405), size=(70, 30))
        self.nButton =wx.Button(self.panel, label="Next", pos=(70, 405), size=(70, 30))
        self.Bind(wx.EVT_BUTTON, self.previousAssignment, self.pButton)
        self.Bind(wx.EVT_BUTTON, self.nextAssignment, self.nButton)
        hbox3.Add(self.pButton, flag=wx.RIGHT, border=8)
        hbox3.Add(self.nButton, flag=wx.RIGHT, border=8)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1, 10))

        self.panel.SetSizer(vbox) #sizes the vbox

        # self.ln = wx.StaticLine(self.panel, -1, style=wx.LI_VERTICAL)

    def nextAssignment(self, e):
        if self.next != (len(self.assignmentStack)-1):
            self.next += 1
        self.updateAssignment()

    def previousAssignment(self, e):
        if self.next != 0:
            self.next -= 1
        self.updateAssignment()

    def updateAssignment(self):
        # self.assignment = wx.StaticText(self.panel, label="Daniel")
        self.assignment = wx.StaticText(self.panel, label=self.assignmentStack[self.next].answerStr, pos=(5, 5), size=(400, 400))



# @todo make this part of the gui
folderName = "lab2_section12"
assignmentStack = getAssignmentStack(folderName)

# app = wx.App(False)
# frame = wx.Frame(None) #, size=(700,700)
# panel = ExamplePanel(frame, assignmentStack)
# frame.Show()
# app.MainLoop()

app = wx.App()
Example(None, title='Go To Class')
app.MainLoop()