from getFiles import getDocxsFromFolder
import re, cPickle as pickle

class MasterDatabase():
    """ Holds all of our question information and student supplied information. """
    class Student():
        def __init__(self, parent, name, section, sAnswers, lastModified, filePath, documentStr):
            self.parent = parent
            self.name = name
            self.section = section
            self.sAnswers = sAnswers
            self.lastModified = lastModified
            self.documentStr = documentStr
            self.filePath = filePath

            self.gradeSubmitted = False

            self.scoreDict = {}
            # Don't do this if we're loading data.
            if len(self.scoreDict) == 0:
                for qNum in self.parent.getQuestionKeys():
                    self.scoreDict[qNum] = {"weight":0,"points":self.parent.getQuestionPoints(qNum)}

        def _getName(self):
            return self.name

        def _getLastModified(self):
            return self.lastModified

        def _getGradeSubmitted(self):
            return self.gradeSubmitted

        def _setGradeSubmitted(self, status=False):
            self.gradeSubmitted = status

        def _getSection(self):
            return self.section

        def _getDocumentStr(self):
            return self.documentStr

        def _getAnswer(self, qNum):
            return self.sAnswers[qNum]

        def _getQuestionScore(self, qNum):
            return self.scoreDict[qNum]["weight"]*self.parent.getQuestionPoints(qNum)

        def _setQuestionWeight(self, qNum, weight):
            self.scoreDict[qNum]["weight"] = weight

        def _getQuestionWeight(self, qNum):
            return self.scoreDict[qNum]["weight"]

        def _getTotalScore(self):
            tempscore = 0
            for qNum in self.scoreDict:
                tempscore += self.scoreDict[qNum]["weight"]*self.scoreDict[qNum]["points"]
            return tempscore

        def _getTotalWeight(self):
            tempscore = 0
            for qNum in self.scoreDict:
                tempscore += self.scoreDict[qNum]["weight"]
            return tempscore

        def _getStudentFilepath(self):
            return self.filePath

    def __init__(self, currentLab = "lab1"):
        """ Initializes our function and gets everything ready for us. """
        self.currentLab = currentLab
        self.gradeFile = ""
        self.labFolder = ""
        self.studentList = {}

        self.qb = {

        "lab1": {
        1:{"question":"What is the 25th term of this sequence?","answer":"41.62","aText":"What is the 80th term of this sequence","points":2.5},
        2:{"question":"What is the 80th term of this sequence?","answer":"131.27", "aText":"What is the sum of the first through the 75th term of this sequence?","points":2.5},
        3:{"question":"What is the sum of the first through the 75th term of this sequence?","answer":"4710.75", "aText": "What is the sum of the 10th through the 90th term of this sequence?","points":2.5},
        4:{"question":"What is the sum of the 10th through the 90th term of this sequence?","aText":"Recall the explicit formulas for the nth term of an arithmetic sequence","answer":"6671.97","points":2.5},
        5:{"question":"Use these formulas to verify your answers for questions 1, 2, and 3. Show your\nwork.","aText":"Now, use your Excel workbook","answer":["2.5+1.63(25-1)","2.5+1.63(80-1)","75/2(2.5+123.12)"],"points":2.5},
        6:{"question":"What is the 15th term of this sequence?","answer":"5.43","aText":"What is the sum of the first 30 terms of this sequence?","points":2.5},
        7:{"question":"What is the sum of the first 30 terms of this sequence?","aText":"Recall the explicit formulas for the nth term of a geometric sequence","answer":"170.80","points":2.5},
        8:{"question":"Use these formulas to verify your answers for questions 6 and 7. Show your\nwork.","aText":"If this sequence represents inflation on the price of a box of cereal at the beginning of a year, where one box cost $3.59 in 2011, how much will a box of cereal cost in the year 2047?","answer":["3.59*1.03^(15-1)","3.59((1.03 ^30)-1)/(1.03-1)"],"points":2.5},
        9:{"question":"If this sequence represents inflation on the price of a box of cereal at the beginning of a year, where one box cost $3.59 in 2011, how much will a box of cereal cost in the year 2047?","aText":"An auditorium has","answer":"$10.40","points":2.5},
        10:{"question":"How many seats will there be in the 16th row?","answer":"40","aText":"How many total seats are there in the auditorium","points":2.5},
        11:{"question":"How many total seats are there in the auditorium?","answer":"580","aText":"In compound interest, time is divided into interest periods.","points":2.5},
        12:{"question":"Assuming that no payments are made during the time period, how much money would you owe back after 5 years if you borrowed $1000 at an interest rate of 2% per quarter?","answer":"$1,485.95","aText":-1,"points":2.5}
        },

        "lab2": {
        1:{"question":"According to our model, what is predicted to be the cost of a semester of tuition in 2015?","answer":"$3,860.30","aText":"How about the cost of tuition in 2020?","points":2},
        2:{"question":"How about the cost of tuition in 2020?","answer":"$4,672.50","aText":"Did you perform interpolation or extrapolation in questions 1 and 2?","points":2},
        3:{"question":"Did you perform interpolation or extrapolation in questions 1 and 2?","answer":"Extrapolation","aText":"What does the value of the slope in our linear model, 162.44, represent? (Yes, it represents rate of change, but be more descriptive; what quantity is changing, and how is it changing?)","points":2},
        4:{"question":"What does the value of the slope in our linear model, 162.44, represent?  (Yes, it represents rate of change, but be more descriptive; what quantity is changing, and how is it changing?)","answer":"Tuition change","aText":"Based on the value of the R^2, would this seem to be an accurate model or an inaccurate model for the data?","points":2},
        5:{"question":"Based on the value of the R^2, would this seem to be an accurate model or an inaccurate model for the data?","answer":"Accurate","aText":"Do you think a linear model, in general, is a good model to use for tuition rates?  Why or why not?  (Be somewhat descriptive with your answer.)","points":2},
        # 6:{"question":"","answer":"","aText":"","points":2},
        # 7:{"question":"","answer":"","aText":"","points":5},
        # 8:{"question":"","answer":"","aText":"","points":2},
        # 9:{"question":"","answer":"","aText":"","points":2},
        # 10:{"question":"","answer":"","aText":"","points":2},
        # 11:{"question":"","answer":"","aText":"","points":2},
        }

        }

    def getLab():
        """ Returns currently selected lab. """
        return self.currentLab

    def setLab(self, labNum):
        """ Sets the lab to a user specified lab. """
        self.currentLab = labNum

    def loadLabs(self, subPath, importFilePath):
        """ Imports the labs in the subPath directory and uses the importFilePath for validation """
        self._getAssignments(subPath, importFilePath)
        self._autoGradeStudentsLab()

    def getTotalQuestions(self):
        """ Returns the number of questions of the current lab. """
        return len(self.qb[self.currentLab])

    def getQuestion(self, qNum, niceFormat=False):
        """ Returns the questions of the current lab replacing new lines with a space. """
        if niceFormat:
            return self.qb[self.currentLab][qNum]["question"].replace("\n"," ")
        else:
            return self.qb[self.currentLab][qNum]["question"]

    def getAnswer(self, qNum):
        """ Returns the correct answer for the specified question. """
        return self.qb[self.currentLab][qNum]["answer"]

    def getAText(self, qNum):
        """ Returns the after text for the current question. """
        return self.qb[self.currentLab][qNum]["aText"]

    def getQuestionKeys(self):
        """ Returns the current lab's dictionary keys. """
        return self.qb[self.currentLab].keys()

    def getStudentKeys(self):
        """ Returns the student dictionary keys. """
        return self.studentList.keys()

    def getLastModified(self, student):
        """ Returns the last person to modify the word document. """
        return self.studentList[student]._getLastModified()

    def getStudentAnswer(self, student, qNum):
        """ Returns the supplied student's answer for the question number. """
        return self.studentList[student]._getAnswer(qNum)

    def getStudentSubmittedGrade(self, student):
        """ Returns true if the students grade was submitted. """
        return self.studentList[student]._getGradeSubmitted()

    def setStudentSubmittedGrade(self, student, status):
        """ Returns true if the students grade was submitted. """
        self.studentList[student]._setGradeSubmitted(status)

    def getStudentSection(self, student):
        """ Returns the supplied student's section. """
        return self.studentList[student]._getSection()

    def getStudentTotalWeight(self, student):
        """ Returns the total number of points the student has correct. """
        return self.studentList[student]._getTotalWeight()

    def getStudentTotalScore(self, student):
        """ Returns the total number of points the student has correct. """
        return self.studentList[student]._getTotalScore()

    def getStudentQuestionScore(self, student, qNum):
        """ Returns the student's score for a particular question. """
        return self.studentList[student]._getQuestionScore(qNum)

    def getStudentFilepath(self, student):
        """ Returns the student's word filepath. """
        return self.studentList[student]._getStudentFilepath()

    def getQuestionPoints(self, qNum):
        """ Returns how many points a specified question is worth. """
        return self.qb[self.currentLab][qNum]["points"]

    def getTotalPoints(self):
        """ Returns how many points the current lab is worth. """
        totalPoints = 0
        for qNum in self.getQuestionKeys():
            totalPoints += self.qb[self.currentLab][qNum]["points"]
        return totalPoints

    def getStudentQuestionWeight(self, student, qNum):
        """ Returns the student's question's specified weight. """
        return self.studentList[student]._getQuestionWeight(qNum)

    def setStudentQuestionWeight(self, student, qNum, weight):
        """ Sets the student's question's specified weight. """
        self.studentList[student]._setQuestionWeight(qNum, weight)

    def saveProgress(self, filename="lab1.dat"):
        """ Function to allow us to save multiple things to one file that is specified while saving. """
        f = open(filename, "wb")
        pickle.dump(len(self.studentList), f , protocol=-1)
        pickle.dump(self.currentLab, f , protocol=-1)
        pickle.dump(self.gradeFile, f , protocol=-1)
        pickle.dump(self.labFolder, f , protocol=-1)
        for student in self.studentList:
            pickle.dump(self.studentList[student].name, f , protocol=-1)
            pickle.dump(self.studentList[student].section, f , protocol=-1)
            pickle.dump(self.studentList[student].sAnswers, f , protocol=-1)
            pickle.dump(self.studentList[student].lastModified, f , protocol=-1)
            pickle.dump(self.studentList[student].filePath, f , protocol=-1)
            pickle.dump(self.studentList[student].documentStr, f , protocol=-1)
            pickle.dump(self.studentList[student].scoreDict, f , protocol=-1)
            pickle.dump(self.studentList[student]._getGradeSubmitted(), f , protocol=-1)
        f.close()

    def loadProgress(self, filename="lab1.dat"):
        """ Function to allow us to save multiple things to one file that is specified while saving. """
        f = open(filename, "rb")
        students = pickle.load(f)
        self.currentLab = pickle.load(f)
        self.gradeFile = pickle.load(f)
        self.labFolder = pickle.load(f)
        for i in range(1,students+1):
            name = pickle.load(f)
            section = pickle.load(f)
            sAnswers = pickle.load(f)
            lastModified = pickle.load(f)
            filePath = pickle.load(f)
            documentStr = pickle.load(f)
            scoreDict = pickle.load(f)
            gradeSubmitted = pickle.load(f)

            newStudent = self.Student(self, name, section, sAnswers, lastModified, filePath=filePath, documentStr=documentStr)
            newStudent.scoreDict = scoreDict
            newStudent._setGradeSubmitted(gradeSubmitted)
            self.studentList[name] = newStudent
            print "Processed "+name
        f.close()

    def _getAssignments(self, subPath, importFilePath):
        """ Loads all of the assignments and gets the student information from them. """
        labs, fileNameList, filePathList, lastModifiedAuthors = getDocxsFromFolder(subPath)

        #EX: Finite Math & Intro Calc 130 07_GradesExport_2014-01-25-16-06.csv
        section = importFilePath.split()[-1].split("_")[0] #this will give an error if the rename the file

        for i in range(len(labs)):
            name = fileNameList[i].split("-")[0]

            sAnswers = self._getStudentAnswersFromLab(labs[i])
            newStudent = self.Student(self, name, section, sAnswers, lastModified=lastModifiedAuthors[i], filePath=filePathList[i], documentStr=labs[i])
            self.studentList[name] = newStudent

    def _getStudentAnswersFromLab(self, lab):
        """ Extracts the students answers from the lab using the after text set previously. """
        lab = re.sub(r'\n +\d\. ',"", lab)
        lab = lab.replace("**","")

        studentAnswerDict = {}
        for qNum in self.getQuestionKeys():
            try:
                start = lab.index(self.getQuestion(qNum))
                start += len(self.getQuestion(qNum)) # to not include question
            except ValueError:
                print "Unable to find before text for question #" + str(qNum) + ". Returning blank answers."
                start = -1

            try:
                if self.getAText(qNum) == -1: # if its the last question it doesn't have aText
                    end = -1
                else:
                    end = lab.index(self.getAText(qNum))
            except ValueError:
                print "Unable to find after text for question #" + str(qNum) + ". Returning partial document string."
                end = -1

            answer = lab[start:end]
            studentAnswerDict[qNum] = answer.strip()
        return studentAnswerDict

    def _autoGradeStudentsLab(self):
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

        for student in self.getStudentKeys():
            for qNum in self.getQuestionKeys():
                # for key, value in studentAnswerDict[qNum].items():
                if type(self.getAnswer(qNum)) == list:
                    grade = gradeList(self.getStudentAnswer(student,qNum), self.getAnswer(qNum))
                else:
                    grade = roundingError(self.getStudentAnswer(student,qNum), self.getAnswer(qNum), .05)
                if qNum in [5,8]:
                    grade = 1
                self.setStudentQuestionWeight(student,qNum,grade) #studentAnswerDict[qNum]["grade"] = grade*self.getPoints(qNum)

if __name__ == '__main__':
    md = MasterDatabase()
    md._getAssignments("Examples\\test","07_GradesExport_2014-01-25-16-06.csv")
    # md._autoGradeStudentsLab
    # for student in md.getStudentKeys():
    #     print md.setStudentQuestionWeight(student,1,5)
    # md.saveProgress()
    md.loadProgress()
    for student in md.getStudentKeys():
        print md.getStudentQuestionWeight(student,1)