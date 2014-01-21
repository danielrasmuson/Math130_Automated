from getFiles import getDocxsStr
from question_bank import Question_Bank
import re

def getStudentAnswersFromLab(qDict, lab):
    answersList = []
    for k in qDict.keys():
        # @TODO need some error handling on these indexs
        start = lab.index(qDict[k]["question"])
        start += len(qDict[k]["question"]) # to not include question 

        if qDict[k]["aText"] == -1: # if its the last questoin it doesnt have aText
            end = -1
        else:
            end = lab.index(qDict[k]["aText"])

        answerUnicode = lab[start:end]
        answer = ""
        for char in answerUnicode:
            if 14 < ord(char) < 128:
                answer += char
        answersList.append(answer)
        qDict[k]["sAnswer"] = answer
    return qDict


def getStudentInfo(lab, lWord):
    """Give the lab str and word you want 
    (name|section) 
    it will return the corresponding information"""
    info = ""
    for line in lab.split("\r"):
        if lWord in line.lower():
            info = line.split(":")[1].strip()
    return info


class assignment():
    def __init__(self, documentStr):
        self.documentStr = documentStr
        # self.filePath = filePath
        # self.document = self.setDocumentStr()

        # studentInfo, answersList = self.setAandInfo()
    def setName(self, name):
        self.name = name

    def setSection(self, section):
        self.section = section

    def setStudentAnswers(self, sAnswers):
        self.sAnswers = sAnswers

    def setStudentDictionary(self, qD):
        self.studentQD = qD

    def getName(self):
        return self.name

    def getSection(self):
        return self.section

    def getDocumentStr(self):
        return self.documentStr

    def getStudentDictionary(self):
        """A dictionary containing the question bank
        along with the students answer
        ex: self.studentQD[1][sAnswer]
        ex: self.studentQD[Question Number][Student Answer]"""
        return self.studentQD


def getAssignmentStack(subPath):
    """Returns a list assignments"""
    labN = 1
    
    qb = Question_Bank()
    labs = getDocxsStr(subPath)
    assignmentStack = []
    for lab in labs:
        name = getStudentInfo(lab, "name")
        section = getStudentInfo(lab, "section")
        studentQD = getStudentAnswersFromLab(qb.questionsDict[labN], lab)

        studentAssign = assignment(lab)
        studentAssign.setName(name)
        studentAssign.setSection(section)
        studentAssign.setStudentDictionary(studentQD)



        assignmentStack.append(studentAssign)

    return assignmentStack

if __name__ == "__main__":
    assignmentStack = getAssignmentStack("Examples\\test")