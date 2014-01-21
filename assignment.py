from getFiles import getDocxsStr
from question_bank import Question_Bank
import re

def getStudentAnswers(qb, lab):
    answers = []
    for k in qb.questions.keys():
        # @TODO need some error handling on these indexs
        start = lab.index(qb.questions[k]["question"])
        start += len(qb.questions[k]["question"]) # to not include question 

        if qb.questions[k]["aText"] == -1: # if its the last questoin it doesnt have aText
            end = -1
        else:
            end = lab.index(qb.questions[k]["aText"])

        answerUnicode = lab[start:end]
        answer = ""
        for char in answerUnicode:
            if 14 < ord(char) < 128:
                answer += char
        answers.append(answer)
    return answers


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
    def __init__(self):
        pass
        # self.filePath = filePath
        # self.document = self.setDocumentStr()

        # studentInfo, answersList = self.setAandInfo()
    def setName(self, name):
        self.name = name

    def setSection(self, section):
        self.section = section

    def setStudentAnswers(self, sAnswers):
        self.sAnswers = sAnswers

    def getName(self):
        return self.name

    def getSection(self):
        return self.section

    def getStudentAnswers(self):
        """Returns a list of the answers the student gave"""
        return self.sAnswers


def getAssignmentStack(subPath):
    """Returns a list assignments"""

    qb = Question_Bank()
    labs = getDocxsStr(subPath)
    assignmentStack = []
    for lab in labs:
        name = getStudentInfo(lab, "name")
        section = getStudentInfo(lab, "section")
        answerList = getStudentAnswers(qb, lab)

        studentAssign = assignment()
        studentAssign.setName(name)
        studentAssign.setSection(section)
        studentAssign.setStudentAnswers(answerList)

        assignmentStack.append(studentAssign)

    return assignmentStack

if __name__ == "__main__":
    assignmentStack = getAssignmentStack("Examples\\test")