# -*- coding: utf-8 -*-
import win32com.client as win32
import os,glob,win32clipboard
# os.system('cls' if os.name=='nt' else 'clear')

def getDocxsStr(subFolder):
    """Given a directory it will return a list of string
    elements for the docx in that given folder."""
    word = win32.gencache.EnsureDispatch('Word.Application')
    word.Visible = 0
    docxList = []
    fileList = []
    objectList = []
    for filePath in glob.glob(subFolder+"\*.docx"):
        misc_objects = []
        if filePath.find(":") == -1:
            filePath = os.getcwd()+'\\'+filePath
        doc = word.Documents.Open(filePath)
        string = doc.Content.Text.encode('utf8')

        # A way of dealing with equations, kind of.
        if doc.Content.OMaths.Count != 0:
            for i in range(1,doc.Content.OMaths.Count+1):
                try:
                    doc.Content.OMaths.Item(i).ConvertToMathText()
                    doc.Content.OMaths.Item(i).Range.Copy()
                    win32clipboard.OpenClipboard()
                    data = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                    misc_objects.append(data)
                except:
                    print "Error copying misc objects in file: ",filePath
                    # raise
        docxList.append(string)
        fileList.append(filePath)
        objectList.append(misc_objects)
    word.Application.Quit(-1)
    return fileList,docxList,objectList

if __name__ == "__main__":
    print getDocxsStr("Examples\\test")[0]