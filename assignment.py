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
