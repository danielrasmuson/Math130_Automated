from getFiles import getDocxsFromFolder
import re, cPickle as pickle, xlrd, csv

class MasterDatabase():
    """ Holds all of our question information and student supplied information. """
    class Student():
        def __init__(self, parent, name, section, sAnswers, lastWordModified, lastExcelModified, wordFilePath, excelFilePath, documentStr):
            self.parent = parent
            self.name = name
            self.section = section
            self.sAnswers = sAnswers
            self.lastWordModified = lastWordModified
            self.lastExcelModified = lastExcelModified
            self.wordFilePath = wordFilePath
            self.excelFilePath = excelFilePath
            self.documentStr = documentStr

            self.gradeSubmitted = False
            self.tookAttendance = "Unknown"

            self.scoreDict = {}
            # Don't do this if we're loading data.
            if len(self.scoreDict) == 0:
                for qNum in self.parent.getQuestionKeys():
                    self.scoreDict[qNum] = {"weight":0,"points":self.parent.getQuestionPoints(qNum)}

        def _getName(self):
            return self.name

        def _getAttendance(self):
            return self.tookAttendance

        def _getLastWordModified(self):
            return self.lastWordModified

        def _getLastExcelModified(self):
            return self.lastExcelModified

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

        def _getStudentWordFilepath(self):
            return self.wordFilePath

        def _getStudentExcelFilepath(self):
            return self.excelFilePath

    def __init__(self, currentLab = "lab1"):
        """ Initializes our function and gets everything ready for us. """
        self.currentLab = currentLab
        self.gradeFile = ""
        self.labFolder = ""
        self.studentList = {}

        self.wordQB = {
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
        4:{"question":"What does the value of the slope in our linear model, 162.44, represent? (Yes, it represents rate of change, but be more descriptive; what quantity is changing, and how is it changing?)","answer":"Tuition","aText":"Based on the value of the R2, would this seem to be an accurate model or an inaccurate model for the data?","points":2},
        5:{"question":"Based on the value of the R2, would this seem to be an accurate model or an inaccurate model for the data?","answer":"Accurate","aText":"Do you think a linear model, in general, is a good model to use for tuition rates? Why or why not? (Be somewhat descriptive with your answer.)","points":2},
        6:{"question":"Do you think a linear model, in general, is a good model to use for tuition rates? Why or why not? (Be somewhat descriptive with your answer.)","answer":"Yes","aText":"You will now use the following data for remainder of this assignment.","points":2},
        7.0:{"question":"Write your equation and your R2 value here:","answer":["Y= 0.1009x + 0.4866","0.2053","0.4866","R^2=0.2053","R2=0.2053","R~ = 0.2053"],"aText":"(5 points)","points":0},
        7.1:{"question":"Print out a copy of your completed graph under the above guidelines and turn it in along with this assignment.","answer":"","aText":"In the equation given for your graph, what does the x represent? What does the y represent?","points":5},
        8:{"question":"In the equation given for your graph, what does the x represent? What does the y represent?","answer":["x=ACT","y=GPA","X Is ACT","Y is GPA"],"aText":"What is the slope of your line? What does it represent? (As in problem 4, be descriptive.)","points":2},
        9:{"question":"What is the slope of your line? What does it represent? (As in problem 4, be descriptive.)","answer":"0.1009","aText":"According to your model, if a mathematics or computer science major had mathematics ACT score of 22, what would be his or her predicted GPA?","points":2},
        10:{"question":"According to your model, if a mathematics or computer science major had mathematics ACT score of 22, what would be his or her predicted GPA?","answer":"2.7064","aText":"Is this likely to be an accurate model or an inaccurate model?","points":2},
        11:{"question":"Is this likely to be an accurate model or an inaccurate model? Why or why not?","answer":"Inaccurate","aText":-1,"points":2},
        },

        "lab3": {
        1.1:{"question":"After how many months of payments will the borrower be paying off more in principal per month than interest?","answer":"152","aText":"(2) What is the total","points":2},
        1.2:{"question":"What is the total amount of interest the borrower will pay over the life of this 30-year loan?","answer":"71,869.51","aText":"(2) What do you think","points":2},
        1.3:{"question":"What do you think about the answer to problem 2? How does this make you feel about the notion of, say, only paying minimum payments on a credit card balance?","answer":"","aText":"Problem #2 (11","points":2},
        2.1:{"question":"Print out this table and hand it in with your lab. (The file has been set up to print out as two pages.)","answer":"","aText":"","points":6,"excel":"2.1"},
        2.2:{"question":"After how many months of payments will Michael have paid off half of his principal? Circle this payment row on your printed table.","answer":"32","aText":"(3) Suppose that,","points":2},
        2.3:{"question":"At what month will Michael finish paying off the car, and what should be his final payment (it should be less than $425!)?","answer":"$75.27","aText":"Problem #3 (8","points":3},
        3.1:{"question":"Print out these tables and hand them in with your lab. (The sheet is set up to print out as four pages total.)","answer":"","aText":"","points":6,"excel":"3.1"},
        3.2:{"question":"How much total interest will Michael pay over 10 years if he only makes minimum payments?","answer":"$4,521.15","aText":-1,"points":2},
        }

        }

        self.excelQB = {
        "lab3":{
        2.1:{"sheet":"Car loan problem","cells":[["B5",17399.44],["B8",0.0039583],["B10",326.3597],["F3",19581.5],["F4",2182.1]]},
        3.1:{"sheet":"Student loans problem","cells":[["B4",13200],["B5",.026],["B6",12],["B7",0.00216666],["B8",120],["B9",125.0374252],["B132",124.767],["C132",.2703],["H4",7131],["H5",.068],["H6",12],["H7",0.0056666],["H8",120],["H9",82.06378],["H132",81.60],["I132",.46],["K3",24852.145],["K4",4521.145]]}
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
        self._autoGradeStudentsWord()
        self._autoGradeStudentsExcel()

    def isQuestionExcel(self, qNum):
        """ A way to check if a question requires excel checking or not. """
        if "excel" in self.wordQB[self.currentLab][qNum].keys():
            return True
        else:
            return False

    def getTotalQuestions(self):
        """ Returns the number of questions of the current lab. """
        return len(self.wordQB[self.currentLab])

    def getQuestion(self, qNum, niceFormat=False):
        """ Returns the questions of the current lab replacing new lines with a space. """
        if niceFormat:
            return self.wordQB[self.currentLab][qNum]["question"].replace("\n"," ")
        else:
            return self.wordQB[self.currentLab][qNum]["question"]

    def getAnswer(self, qNum):
        """ Returns the correct answer for the specified question. """
        return self.wordQB[self.currentLab][qNum]["answer"]

    def getAText(self, qNum):
        """ Returns the after text for the current question. """
        return self.wordQB[self.currentLab][qNum]["aText"]

    def getQuestionKeys(self):
        """ Returns the current lab's dictionary keys. """
        return self.wordQB[self.currentLab].keys()

    def getStudentKeys(self):
        """ Returns the student dictionary keys. """
        return self.studentList.keys()

    def getLastWordModified(self, student):
        """ Returns the last person to modify the word document. """
        return self.studentList[student]._getLastWordModified()

    def getLastExcelModified(self, student):
        """ Returns the last person to modify the excel document. """
        return self.studentList[student]._getLastExcelModified()

    def getStudentAnswer(self, student, qNum):
        """ Returns the supplied student's answer for the question number. """
        return self.studentList[student]._getAnswer(qNum)

    def getStudentLabString(self, student):
        return self.studentList[student]._getDocumentStr()

    def getStudentSubmittedGrade(self, student):
        """ Returns true if the students grade was submitted. """
        return self.studentList[student]._getGradeSubmitted()

    def setStudentSubmittedGrade(self, student, status):
        """ Returns true if the students grade was submitted. """
        self.studentList[student]._setGradeSubmitted(status)

    def getStudentSection(self, student):
        """ Returns the supplied student's section. """
        return self.studentList[student]._getSection()

    def getStudentAttendance(self, student):
        """ Returns the time if the student took the quiz.  Otherwise returns False. """
        return self.studentList[student]._getAttendance()

    def getStudentTotalWeight(self, student):
        """ Returns the total number of points the student has correct. """
        return self.studentList[student]._getTotalWeight()

    def getStudentTotalScore(self, student):
        """ Returns the total number of points the student has correct. """
        return self.studentList[student]._getTotalScore()

    def getStudentQuestionScore(self, student, qNum):
        """ Returns the student's score for a particular question. """
        return self.studentList[student]._getQuestionScore(qNum)

    def getStudentWordFilepath(self, student):
        """ Returns the student's word filepath. """
        return self.studentList[student]._getStudentWordFilepath()

    def getStudentExcelFilepath(self, student):
        """ Returns the student's excel filepath. """
        return self.studentList[student]._getStudentExcelFilepath()

    def getQuestionPoints(self, qNum):
        """ Returns how many points a specified question is worth. """
        return self.wordQB[self.currentLab][qNum]["points"]

    def getTotalPoints(self):
        """ Returns how many points the current lab is worth. """
        totalPoints = 0
        for qNum in self.getQuestionKeys():
            totalPoints += self.wordQB[self.currentLab][qNum]["points"]
        return totalPoints

    def getStudentQuestionWeight(self, student, qNum):
        """ Returns the student's question's specified weight. """
        return self.studentList[student]._getQuestionWeight(qNum)

    def setStudentQuestionWeight(self, student, qNum, weight):
        """ Sets the student's question's specified weight. """
        self.studentList[student]._setQuestionWeight(qNum, weight)

    def saveProgress(self, filename="lab.dat"):
        """ Function to allow us to save multiple things to one file that is specified while saving. """
        f = open(filename, "wb")
        pickle.dump(len(self.studentList), f , protocol=-1)
        pickle.dump(self.currentLab, f , protocol=-1)
        pickle.dump(self.gradeFile, f , protocol=-1)
        pickle.dump(self.labFolder, f , protocol=-1)
        for student in sorted(self.studentList.keys()):
            pickle.dump(self.studentList[student].name, f , protocol=-1)
            pickle.dump(self.studentList[student].section, f , protocol=-1)
            pickle.dump(self.studentList[student].sAnswers, f , protocol=-1)
            pickle.dump(self.studentList[student].lastWordModified, f , protocol=-1)
            pickle.dump(self.studentList[student].wordFilePath, f , protocol=-1)
            pickle.dump(self.studentList[student].excelFilePath, f , protocol=-1)
            pickle.dump(self.studentList[student].documentStr, f , protocol=-1)
            pickle.dump(self.studentList[student].scoreDict, f , protocol=-1)
            pickle.dump(self.studentList[student].tookAttendance, f , protocol=-1)
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
            lastWordModified = pickle.load(f)
            wordFilePath = pickle.load(f)
            excelFilePath = pickle.load(f)
            documentStr = pickle.load(f)
            scoreDict = pickle.load(f)
            tookAttendance = pickle.load(f)
            gradeSubmitted = pickle.load(f)

            newStudent = self.Student(self, name, section, sAnswers, lastWordModified, lastExcelModified="", wordFilePath=wordFilePath, excelFilePath=excelFilePath, documentStr=documentStr)
            newStudent.scoreDict = scoreDict
            newStudent.tookAttendance = tookAttendance
            newStudent._setGradeSubmitted(gradeSubmitted)
            self.studentList[name] = newStudent
            print "Processed "+name
        f.close()

    def checkAttendance(self, file):
        """Parses through the student list to see if a student took the attendance quiz or not."""
        quizNames = {}
        # First we get the names of everyone who took the quiz.
        with open(file, 'rb') as csvfile:
            linereader = csv.reader(csvfile, delimiter=',')
            next(linereader, None)
            for row in linereader:
                name = row[2] + " " + row[3]
                if name not in quizNames:
                    quizNames[name] = row[5]
        # Now we compare to students and get the time they took the quiz.
        for student in self.studentList:
            if student in quizNames:
                self.studentList[student].tookAttendance = quizNames[student]
                del quizNames[student]
            else:
                self.studentList[student].tookAttendance = False
        print str(len(quizNames)) + " Students took the quiz but couldn't be found in the lab list:"
        print ", ".join(sorted(quizNames.keys()))

    def _trunc(self, f, n):
        """ Truncates/pads a float f to n decimal places without rounding """
        slen = len('%.*f' % (n, f))
        return float(str(f)[:slen])

    def _getAssignments(self, subPath, importFilePath):
        """ Loads all of the assignments and gets the student information from them. """
        labs, fileNameList, wordFilePathList, lastWordModifiedAuthors, excelFiles = getDocxsFromFolder(subPath)

        #EX: Finite Math & Intro Calc 130 07_GradesExport_2014-01-25-16-06.csv
        section = importFilePath.split()[-1].split("_")[0] #this will give an error if the rename the file

        for i in range(len(labs)):
            name = fileNameList[i].split("-")[0]

            sAnswers = self._getStudentAnswersFromLab(labs[i])
            newStudent = self.Student(self, name, section, sAnswers, lastWordModified=lastWordModifiedAuthors[i], lastExcelModified="", wordFilePath=wordFilePathList[i], excelFilePath=excelFiles[name], documentStr=labs[i])
            self.studentList[name] = newStudent

    def _getStudentAnswersFromLab(self, lab):
        """ Extracts the students answers from the lab using the after text set previously. """
        lab = lab.replace("  10.","")
        lab = lab.replace("  11.","")
        lab = lab.replace("  12.","")
        lab = lab.replace("  13.","")
        lab = lab.replace("\n10.","")
        lab = lab.replace("\n11.","")
        lab = lab.replace("\n12.","")
        lab = lab.replace("\n13.","")
        lab = re.sub(r'\n +\d\. ',"", lab)
        lab = lab.replace("**","")

        studentAnswerDict = {}
        # Defines the keylist for use later if we need it.
        keyList = sorted(self.getQuestionKeys())
        for i, qNum in enumerate(keyList):
            try:
                start = lab.index(self.getQuestion(qNum))
                start += len(self.getQuestion(qNum)) # to not include question
            except ValueError:
                print "Unable to find before text for question #" + str(qNum) + ". Returning blank answers."
                start = -1

            try:
                if self.getAText(qNum) == -1: # if its the last question it doesn't have aText
                    end = -1
                # This is a way for us to just use the next question if there isn't aText.  So that way things are faster.
                elif self.getAText(qNum) == "":
                    end = lab.index(self.getQuestion(keyList[i+1]))
                else:
                    end = lab.index(self.getAText(qNum))
            except ValueError:
                print "Unable to find after text for question #" + str(qNum) + ". Returning partial document string."
                end = -1

            answer = lab[start:end]
            studentAnswerDict[qNum] = answer.strip()
        return studentAnswerDict

    def _autoGradeStudentsExcel(self):
        """ Will parse through all of the students and check if there
        is any grading of excel that needs to be done and if it can even open an excel file. 
        This gives fractional weights based on how many of the cells right they got. """
        def _round(value, step):
            return round(value/step)*step
        # Lot's of loops and fors, sorry about that.
        co_index = {"A":0,"B":1,"C":2,"D":3,"E":4,"F":5,"G":6,"H":7,"I":8,"J":9,"K":10,"L":11,"M":12}
        # Make sure we check each student.
        for student in self.getStudentKeys():
            filename = self.getStudentExcelFilepath(student)
            # If they have excel we proceed.
            if len(filename) > 0:
                workbook = xlrd.open_workbook(filename[0])
                self.studentList[student].lastExcelModified = workbook.user_name
                # Check each question.
                for qNum in self.getQuestionKeys():
                    currentPoints = 0
                    if self.isQuestionExcel(qNum):
                        # Clear the student answer box for excel grading report.
                        self.studentList[student].sAnswers[qNum] = ""
                        totalExcelPoints = len(self.excelQB[self.currentLab][qNum]["cells"])
                        worksheet = workbook.sheet_by_name(self.excelQB[self.currentLab][qNum]["sheet"])
                        for cell in self.excelQB[self.currentLab][qNum]["cells"]:
                            # Get's the location to trunacte the answers for checking precision.
                            if str(cell[1]).find(".")==-1:
                                trunc_loc = 0
                            else:
                                trunc_loc = len(str(cell[1]).split(".")[1])
                            # Try to find the value, if it's blank or not there we just move on.
                            try:
                                if self._trunc(worksheet.cell_value(int(cell[0][1:])-1,co_index[cell[0][0]]),trunc_loc) == cell[1]:
                                    currentPoints += 1.
                                else:
                                    self.studentList[student].sAnswers[qNum] += "Cell " + cell[0] +" wrong "+ str(worksheet.cell_value(int(cell[0][1:])-1,co_index[cell[0][0]])) + " != " + str(cell[1]) + "\n"
                            except:
                                self.studentList[student].sAnswers[qNum] += "Cell "+cell[0]+" missing in " +worksheet.name+ ".\n"
                        weight = _round( currentPoints/totalExcelPoints, 1./self.getQuestionPoints(qNum))
                        self.setStudentQuestionWeight(student,qNum,weight)
                        self.studentList[student].sAnswers[qNum] += "Finished autograding. Auto weight assigned: "+ str(weight)[0:5] + ". Points earned: " +str(self.getStudentQuestionScore(student,qNum))

    def _autoGradeStudentsWord(self):
        """A more robust system for grading labs
        grade could be either a 1 or 0
        can add a lot more to function but I just started it"""
        def roundingError(sAnswer, answer, rE):
            answerC = answer.replace("$","").replace(",","").strip().lower() #clean question bank value
            studentC = sAnswer.replace("$","").replace(",","").strip().lower()

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
                if not self.isQuestionExcel(qNum):
                    if self.getAnswer(qNum) == "":
                        grade = 0
                    elif type(self.getAnswer(qNum)) == list:
                        grade = gradeList(self.getStudentAnswer(student,qNum), [ s.lower() for s in self.getAnswer(qNum) ] )
                    else:
                        grade = roundingError(self.getStudentAnswer(student,qNum), self.getAnswer(qNum).lower(), .05)
                    self.setStudentQuestionWeight(student,qNum,grade)


if __name__ == '__main__':
    md = MasterDatabase("lab3")
    md._getAssignments("Examples\\test","07.csv")
    # md._autoGradeStudentsWord()
    md._autoGradeStudentsExcel()
    # for student in md.getStudentKeys():
    #     print md.getStudentAnswer(student,1)
    # md.saveProgress()
    # md.loadProgress()
    # for student in md.getStudentKeys():
    #     print md.getStudentQuestionWeight(student,1)