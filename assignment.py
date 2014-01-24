from getFiles import getDocxsStr
from question_bank import Question_Bank

def getGradesStudentsLab(quesBank, studentDict):
    """A more robust system for grading labs
    grade could be either a 1 or 0
    can add a lot more to function but I just started it"""
    rE = .05 #rouding error
    for k in studentDict.keys():
        for key, value in studentDict[k].items():
            cleanQBV = quesBank[k]["answer"].replace(".","").replace("$","") #clean question bank value
            cleanedValue = value.replace(".","").replace("$","")
            if cleanQBV.isdigit() and cleanedValue.isdigit():
                # still correct up to x% rounding difference
                if (float(cleanQBV)*(1-rE)) < float(cleanedValue) < (float(cleanQBV)*(1+rE)):
                    grade = 1
                else:
                    grade = 0
            else: #its a word problem
                if cleanQBV in cleanedValue:
                    grade = 1
                else:
                    grade = 0

            studentDict[k]["grade"] = grade

    return studentDict

def getStudentAnswersFromLab(qDict, lab):
    # I changed this to using a new dictionary and only returning that dictionary
    # because I'd rather have that so we can keep the two different dictionaries
    # separate.  Otherwise there was a lot of overlap in the two qDict and studentDict.
    # fair point - Dan
    studentDict = {}
    for qNum in qDict.keys():
        # @TODO need some error handling on these indexes
        try:
            start = lab.index(qDict[qNum]["question"])
            start += len(qDict[qNum]["question"]) # to not include question
        except ValueError:
            print "Unable to find before text. Returning blank answers."
            start = -1

        try:
            if qDict[qNum]["aText"] == -1: # if its the last question it doesn't have aText
                end = -1
            else:
                end = lab.index(qDict[qNum]["aText"])
        except ValueError:
            print "Unable to find after text. Returning partial document string."
            end = -1

        #NOTE - I'm removing strange symbols here
        # might remove squared and stuff from answers
        answerUnicode = lab[start:end]
        answer = ""
        for char in answerUnicode:
            if 14 < ord(char) < 128:
                answer += char
        
        #Added some more automated grading here
        studentDict[qNum] = {"answer": answer.strip()}

    return studentDict


def getStudentInfo(lab, lWord):
    """Give the lab str and word you want
    (name|section)
    it will return the corresponding information"""
    info = ""
    for line in lab.split("\r"):
        if lWord in line.lower():
            info = line.split(":")[1].strip().replace("_","").lstrip("0")
    if info == "":
        info = "MissingInformation"
    return info


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
        self.studentQD = qD

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
        ex: self.studentQD[1][sAnswer]
        ex: self.studentQD[Question Number][Student Answer]"""
        return self.studentQD

    def getStudentFilepath(self):
        return self.filePath


def getAssignmentStack(subPath):
    """Returns a list assignments"""
    fileList,labs,miscObjects = getDocxsStr(subPath)

    qb = Question_Bank()
    assignmentStack = {}
    for i in range(len(labs)):
        #create the attributes for the new assignment object
        name = getStudentInfo(labs[i], "name")
        section = getStudentInfo(labs[i], "section")
        studentQD = getStudentAnswersFromLab(qb.getQuestionsDict(), labs[i])
        studentQD = getGradesStudentsLab(qb.getQuestionsDict(), studentQD)


        assignObj = assignment(labs[i])

        #assign the attributes
        assignObj.setName(name)
        assignObj.setSection(section)
        assignObj.setStudentDictionary(studentQD)
        assignObj.setStudentFilepath(fileList[i])
        assignObj.setMisc(miscObjects[i])

        assignmentStack[name] = assignObj

    return assignmentStack

if __name__ == "__main__":
    assignmentStack = getAssignmentStack("Examples\\test")
    print assignmentStack["Dan Rasmuson"].getStudentDictionary() #[0].getStudentDictionary()