# -*- coding: utf-8 -*-

def find_between(string,question_bank,question=1):
    if question > len(question_bank):
        return ""
    try:
        if question < len(question_bank):
            if len(question_bank[question-1]) == 1:
                substring1 = question_bank[question-1][0]
                substring2 = question_bank[question][0]
            else:
                substring1 = question_bank[question-1][0]
                substring2 = question_bank[question-1][1] 
        else:
            substring1 = question_bank[question-1][0]
            return string[(string.index(substring1)+len(substring1)):-1].strip()
        return string[(string.index(substring1)+len(substring1)):string.index(substring2)].strip()
    except:
        return ""

question_bank=[
["What is the 25th term of this sequence?"],
["What is the 80th term of this sequence?"],
["What is the sum of the first through the 75th term of this sequence?"],
["What is the sum of the 10th through the 90th term of this sequence?","Recall"],
["What is the 15th term of this sequence?"],
["What is the sum of the first 30 terms of this sequence?","Recall the explicit formulas for the nth term of a geometric sequence"],
["how much will a box of cereal cost in the year 2047?","An auditorium"],
["How many seats will there be in the 16th row?"],
["How many total seats are there in the auditorium?","In compound"],
["at an interest rate of 2% per quarter?"],
["asdlfkjasdklfjasg"]
]
    


string = """
Math 130Lab #1 GÇô AssignmentUse your Excel workbook to set up an arithmetic progression with a first term of 2.5 and a common difference of 1.63.  Answer the following problems.What is the 25th term of this sequence?
41.62What is the 80th term of this sequence?
131.27What is the sum of the first through the 75th term of this sequence?
4710.75What is the sum of the 10th through the 90th term of this sequence?
6671.97Recall the explicit formulas for the nth term of an arithmetic sequence, =¥æÄ=¥æ¢, and the sum through the nth term, =¥æå=¥æ¢:
=¥æÄ=¥æ¢==¥æÄ1+=¥ææ=¥æ¢GêÆ1                  =¥æå=¥æ¢= =¥æ¢2(=¥æÄ1+=¥æÄ=¥æ¢)
Use these formulas to verify your answers for questions 1, 2, and 3.  Show your work.Now, use your Excel workbook to set up a geometric progression with a first term of 3.59 and a common multiplier of 1.03.  Answer the following problems.What is the 15th term of this sequence?
5.43What is the sum of the first 30 terms of this sequence?
170.80Recall the explicit formulas for the nth term of a geometric sequence, =¥æÄ=¥æ¢, and the sum through the nth term, =¥æå=¥æ¢:
=¥æÄ=¥æ¢==¥æÄ1Gêù=¥æƒ=¥æ¢GêÆ1                              =¥æå=¥æ¢= =¥æÄ1(=¥æƒ=¥æ¢GêÆ1)=¥æƒGêÆ1
Use these formulas to verify your answers for questions 6 and 7.  Show your work.If this sequence represents inflation on the price of a box of cereal at the beginning of a year, where one box cost $3.59 in 2011, how much will a box of cereal cost in the year 2047?$10.10 is 36th term, but corresponds with the year 2046 the cost in 2047 should be $10.40.An auditorium has ten seats in the first row.  Each succeeding row has two more seats in an ever widening pattern.  The auditorium has a total of 20 rows of seats.  Use your Excel workbook to set up and answer these questions.How many seats will there be in the 16th row?
40How many total seats are there in the auditorium?580In compound interest, time is divided into interest periods.  During each period, interest is earned at a certain rate per interest period.  For example, if you borrow $1000 and the interest rate is 1% per quarter, the interest accumulated after one quarter would be $1000(0.01) = $10, and the total amount of money you would owe back after one quarter would be found by $1000(1 + 0.01) = $1000(1.01) = $1010.  After two quarters, you would owe $1000(1.01)2; after three quarters, $1000(1.01)3; and in general, after n quarters, $1000(1.01)n.Use your Excel workbook to set up and answer the following question.Assuming that no payments are made during the time period, how much money would you owe back after 5 years if you borrowed $1000 at an interest rate of 2% per quarter?$1,485.95"""

print find_between(string,question_bank,1)
print find_between(string,question_bank,2)
print find_between(string,question_bank,3)
print find_between(string,question_bank,4)
print find_between(string,question_bank,5)
print find_between(string,question_bank,6)
print find_between(string,question_bank,7)
print find_between(string,question_bank,8)
print find_between(string,question_bank,9)
print find_between(string,question_bank,10)