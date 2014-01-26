import cPickle as pickle

def getCurrentLab():
    return "lab1" #@TODO: this is where we will adjust the wizard


class Question_Bank():
    """
    Create a class called Question_Bank
    that we can use to hold all of our questions
    and information for faster saving and loading
    manipulating etc of our questions.
    """

    def __init__(self):
        self.setLab(getCurrentLab()) 

        self.qb = {"lab1": {
        1:{"question":"What is the 25th term of this sequence?","answer":"41.62","aText":"What is the 80th term of this sequence"},
        2:{"question":"What is the 80th term of this sequence?","answer":"131.27", "aText":"What is the sum of the first through the 75th term of this sequence?"},
        3:{"question":"What is the sum of the first through the 75th term of this sequence?","answer":"4710.75", "aText": "What is the sum of the 10th through the 90th term of this sequence?"},
        4:{"question":"What is the sum of the 10th through the 90th term of this sequence?","aText":"Recall the explicit formulas for the nth term of an arithmetic sequence","answer":"6671.97"},
        5:{"question":"Use these formulas to verify your answers for questions 1, 2, and 3.  Show your work.","aText":"Now, use your Excel workbook to set up a geometric progression with a first term of 3.59 and a common multiplier of 1.03.  Answer the following problems","answer":["2.5+1.63(25-1)","2.5+1.63(80-1)","75/2(2.5+123.12)"]},
        6:{"question":"What is the 15th term of this sequence?","answer":"5.43","aText":"What is the sum of the first 30 terms of this sequence?"},
        7:{"question":"What is the sum of the first 30 terms of this sequence?","aText":"Recall the explicit formulas for the nth term of a geometric sequence","answer":"170.80"},
        8:{"question":"Use these formulas to verify your answers for questions 6 and 7.  Show your work.","aText":"If this sequence represents inflation on the price of a box of cereal at the beginning of a year, where one box cost $3.59 in 2011, how much will a box of cereal cost in the year 2047?","answer":["3.59*1.03^(15-1)","3.59((1.03 ^30)-1)/(1.03-1)"]},
        9:{"question":"If this sequence represents inflation on the price of a box of cereal at the beginning of a year, where one box cost $3.59 in 2011, how much will a box of cereal cost in the year 2047?","aText":"An auditorium has","answer":"$10.40"},
        10:{"question":"How many seats will there be in the 16th row?","answer":"40","aText":"How many total seats are there in the auditorium"},
        11:{"question":"How many total seats are there in the auditorium?","answer":"580","aText":"In compound interest, time is divided into interest periods."},
        12:{"question":"Assuming that no payments are made during the time period, how much money would you owe back after 5 years if you borrowed $1000 at an interest rate of 2% per quarter?","answer":"$1,485.95","aText":-1}
        }}

    def getQuestionsDict(self):
        return self.qb
        
    def setLab(self, labNum):
        self.lab = labNum

    def getTotalQuestions(self):
        return len(self.qb[self.lab])

    def getQuestion(self, qNum):
        return self.qb[self.lab][qNum]["question"]
        
    def getAnswer(self, qNum):
        return self.qb[self.lab][qNum]["answer"]

    def getAText(self, qNum):
        return self.qb[self.lab][qNum]["aText"]

    def getKeys(self):
        return self.qb[self.lab].keys()

    def save(self,filename="lab1.dat"):
        """ Function to allow us to save multiple things to one file that is specified while saving. """
        f = open(filename, "wb")
        # pickle.dump(self.lab, f , protocol=-1)
        pickle.dump(self.questionsDict, f , protocol=-1)
        f.close()

    def load(self,filename="lab1.dat"):
        """ Load our data back from a file we've already created. """
        f = open(filename, "rb")
        # self.lab = pickle.load(f)
        self.questionsDict = pickle.load(f)
        f.close()

    def add_question(self,question_number, question, answer, substring1="", substring2=""):
        """ A simple way to add questions to the dictionary. """
        #Note this is assuming lab 1
        self.questionsDict[question_number] = {"question":question,"answer":answer}

    def print_questions_to_console(self):
        """ Just a quick test function to print all the data to the console """
        #Note this is assuming lab 1
        # Wont work right now because of lists
        for qNum in self.getKeys():
            if type(self.getAnswer(qNum)) == list:
                print "Question " + str(qNum) + ": " + " ".join(self.getAnswer(qNum)) + " " + self.getQuestion(qNum)
            else:
                print "Question " + str(qNum) + ": " + self.getAnswer(qNum) + " " + self.getQuestion(qNum)


if __name__ == "__main__":
    qb = Question_Bank()
    # print qb.getKeys()
    qb.print_questions_to_console()
    # qb.save()
    # qb.add_question(15,"asdf","lkasdj")
    # qb.print_questions_to_console()