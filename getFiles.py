# -*- coding: utf-8 -*-
import win32com.client as win32
import os,glob
# os.system('cls' if os.name=='nt' else 'clear')

def getDocxsStr(subFolder):
    """Given a directory it will return a list of string 
    elements for the docx in that given folder."""
    word = win32.gencache.EnsureDispatch('Word.Application')
    word.Visible = 0
    docxList = []
    for filePath in glob.glob(subFolder+"\*.docx"):
        if filePath.find(":") == -1:
            filePath = os.getcwd()+'\\'+filePath
        doc = word.Documents.Open(filePath)
        string = doc.Content.Text.encode('utf8')
        docxList.append(string)
    word.Application.Quit(-1)
    return docxList

if __name__ == "__main__":
    print getDocxsStr("Examples\\test")[0]