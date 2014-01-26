#must run "pip install pydocx"
#must run "pip install html2text"

import os, glob
from html2text import *
from pydocx import *

def getDocxStr(docxFile):
    #remove unicode
    newText = ""
    for char in docx2html(docxFile): # .docx --> html
        if ord(char) < 128: #unicode problems
            newText += char
        else:
            newText += "~" 

    # get text from html file
    fileStr = html2text(newText)

    return fileStr

def getDocxsFromFolder(folderPath):
    fileList = []
    fileNameList = []
    for filePath in glob.glob(folderPath+"\*.docx"):
        fileNameList.append(filePath.split("\\")[-1])
        fileStr = getDocxStr(filePath)
        fileList.append(fileStr)
    return fileList, fileNameList


if __name__ == "__main__":
    docxStack, fileNameList = getDocxsFromFolder("C:\\Users\\Daniel\\Google Drive\\Classes\\Math 130 TA\\Lab1_TA130\\Lab1_Grading_Spring2014\\labs")
    print len(docxStack)
    print docxStack[2]