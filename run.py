from docx import opendocx, getdocumenttext
from Tkinter import *
from docx import opendocx, getdocumenttext
import os


def assignmentObjects(folderName):
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


class AssignmentGrading(Frame):
    def __init__(self,assignmentStack):
        Frame.__init__(self)
        self.canvas = Canvas(self) # , width=400, height=300
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas_id = self.canvas.create_text(10, 10, anchor="nw", justify="left")

        self.assignmentStack = assignmentStack

        self.canvas.itemconfig(self.canvas_id, text="This is the starting screen\n\nClick Next to see the first student\nI will write some more instrucations")

        self.previousAssignment = Button(self, text="Previous", command=self.previousAssignment)
        self.previousAssignment.pack(side="left")

        self.nextButton = Button(self, text="Next", command=self.nextAssignment)
        self.nextButton.pack(side="left")

        self.next = 0

    def nextAssignment(self):
        if self.next != (len(assignmentStack)-1):
            self.next += 1
        self.canvas.itemconfig(self.canvas_id, text=self.assignmentStack[self.next].answerStr)

    def previousAssignment(self):
        if self.next != 0:
            self.next -= 1
        self.canvas.itemconfig(self.canvas_id, text=self.assignmentStack[self.next].answerStr)

# @todo make this part of the gui
folderName = "lab2_section12"
assignmentStack = assignmentObjects(folderName)

frame = Tk()
gradingObject = AssignmentGrading(assignmentStack)
gradingObject.pack(side="top", fill="both", expand=True)

# gradingObject.next()

frame.mainloop()
