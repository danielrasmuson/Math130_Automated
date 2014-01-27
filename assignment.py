from getFiles import getDocxsFromFolder
from question_bank import *
import re

def getGradesStudentsLab(qb, studentDict):
    """A more robust system for grading labs
    grade could be either a 1 or 0
    can add a lot more to function but I just started it"""
    def roundingError(sAnswer, answer, rE):
        answerC = answer.replace("$","").replace(",","").strip() #clean question bank value
        studentC = sAnswer.replace("$","").replace(",","").strip()

        try: #isdigit() doesnt work on floats i guess
            if (float(answerC)*(1-rE)) < float(studentC) < (float(answerC)*(1+rE)):
                return 1
            else:
                return 0
        except ValueError:
            if answerC in studentC:
                return 1
            else:
                return 0

    def gradeList(sAnswer, answerList):
        """This will hopefully grade answers
        that are show your work involving mutliple steps
        and have answers such as 3.59*1.03^15-1"""
        for answer in answerList:
            answer = answer.replace(" ","")
            sAnswer = sAnswer.replace(" ","")
            if answer not in sAnswer:
                return 0
        return 1


    for qNum in studentDict.keys():
        for key, value in studentDict[qNum].items():
            if type(qb.getAnswer(qNum)) == list:
                grade = gradeList(value, qb.getAnswer(qNum))
            else:
                grade = roundingError(value, qb.getAnswer(qNum), .05)

            studentDict[qNum]["grade"] = grade

    return studentDict


def getStudentAnswersFromLab(qb, lab):
    #remove numbers for start of aText to work
    #ex. 1. What is the 45th term?
    lab = re.sub(r'\n +\d\. ',"", lab)
    lab = lab.replace("**","")

    studentDict = {}
    for qNum in qb.getKeys():
        try:
            start = lab.index(qb.getQuestion(qNum))
            start += len(qb.getQuestion(qNum)) # to not include question
        except ValueError:
            print "Unable to find before text for question #" + str(qNum) + ". Returning blank answers."
            start = -1

        try:
            if qb.getAText(qNum) == -1: # if its the last question it doesn't have aText
                end = -1
            else:
                end = lab.index(qb.getAText(qNum))
        except ValueError:
            print "Unable to find after text for question #" + str(qNum) + ". Returning partial document string."
            end = -1

        answer = lab[start:end]
        studentDict[qNum] = {"answer": answer.strip()}

    return studentDict


class assignment():
    def __init__(self, documentStr):
        self.documentStr = documentStr

    def setName(self, name):
        self.name = name

    def setSection(self, section):
        self.section = section

    def setStudentAnswers(self, sAnswers):
        self.sAnswers = sAnswers

    def setStudentDictionary(self, qD):
        self.qs = qD

    def setStudentFilepath(self, path):
        self.filePath = path

    def setMisc(self, misc):
        self.misc = misc

    def getMisc(self):
        return self.misc

    def getName(self):
        return self.name

    def getSection(self):
        return self.section

    def getDocumentStr(self):
        return self.documentStr

    def getStudentDictionary(self):
        """A dictionary containing the question bank
        along with the students answer
        ex: self.qs[1][sAnswer]
        ex: self.qs[Question Number][Student Answer]"""
        return self.qs

    def getQuestion(self, qNum):
        return self.qs[qNum]["question"]

    def getAnswer(self, qNum):
        return self.qs[qNum]["answer"]

    def getAText(self, qNum):
        return self.qs[qNum]["aText"]

    def getGrade(self, qNum):
        return self.qs[qNum]["grade"]

    def getKeys(self):
        return self.qs.keys()

    def getStudentFilepath(self):
        return self.filePath

def getAssignmentStack(subPath, importFilePath):
    """Returns a list assignments"""
    labs, fileNameList, filePathList = getDocxsFromFolder(subPath)

    qb = Question_Bank()
    assignmentStack = {}

    #EX: Finite Math & Intro Calc 130 07_GradesExport_2014-01-25-16-06.csv
    section = importFilePath.split()[-1].split("_")[0] #this will give an error if the rename the file

    for i in range(len(labs)):
        name = fileNameList[i].split("-")[0]

        qs = getStudentAnswersFromLab(qb, labs[i])
        qs = getGradesStudentsLab(qb, qs)

        assignObj = assignment(labs[i])

        #assign the attributes
        assignObj.setName(name)
        assignObj.setSection(section)
        assignObj.setStudentDictionary(qs)
        assignObj.setStudentFilepath(filePathList[i])

        assignmentStack[name] = assignObj

    return assignmentStack

if __name__ == "__main__":
    assignmentStack = getAssignmentStack("Examples\\test", "C:\\Users\\Daniel\\Documents\\GitHub\\Math130_Automated\\Examples\\Finite Math & Intro Calc 130 07_GradesExport_2014-01-25-16-06.csv")
    # for name, assignObj in assignmentStack.items():
    #     print assignObj.getStudentDictionary()