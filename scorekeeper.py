from __future__ import division

class ScoreKeeper:
    def __init__(self, questionBankKeys, totalPoints, numberQuestions):
        self.scoreDict = {}
        self.totalPoints = totalPoints
        self.numberQuestions = numberQuestions
        for qNum in questionBankKeys:
            self.scoreDict[qNum] = {"weight":0,"points":1.0/numberQuestions*totalPoints}

    def getTotalScore(self):
        tempscore = 0
        for qNum in self.scoreDict:
            tempscore += self.scoreDict[qNum]["weight"]*self.scoreDict[qNum]["points"]
        return tempscore

    def getRawRight(self):
        tempscore = 0
        for qNum in self.scoreDict:
            tempscore += self.scoreDict[qNum]["weight"]
        return tempscore

    def setQuestionWeight(self, question, weight):
        self.scoreDict[question]["weight"] = weight

    def getQuestionWeight(self, question):
        return self.scoreDict[question]["weight"]

    def setQuestionPointsWorth(self, question, points):
        self.scoreDict[question]["points"] = points

    def getQuestionPointsWorth(self, question):
        return self.scoreDict[question]["points"]

if __name__ == "__main__":
    dictionary = {1:"",2:"",3:""}
    SK = ScoreKeeper(dictionary.keys(),totalPoints=30,numberQuestions=12)
    SK.setQuestionWeight(1,1)
    print SK.getTotalScore()