# -*- coding: utf-8 -*-
import win32com.client as win32
import os,glob,win32clipboard,time
import ImageGrab

def getDocxsStr(subFolder):
    """Given a directory it will return a list of string
    elements for the docx in that given folder."""
    word = win32.gencache.EnsureDispatch('Word.Application')
    word.Visible = 0
    docxList = []
    fileList = []
    objectList = []
    fileNameList = []
    for filePath in glob.glob(subFolder+"\*.docx"):
        fileNameList.append(filePath.split("\\")[-1])
        start = time.clock()
        misc_objects = []
        if filePath.find(":") == -1:
            filePath = os.getcwd()+'\\'+filePath
        doc = word.Documents.Open(filePath)
        string = doc.Content.Text.encode('utf8')

        # A way of dealing with equations and pictures kind of. 
        # It's not fool proof and there isn't any realy way to
        # do this without utilizing the clipboard as far as I know.
        if doc.Content.OMaths.Count != 0:
            for i in range(1,doc.Content.OMaths.Count+1):
                try:
                    doc.OMaths.Item(i).ConvertToMathText()
                    doc.OMaths.Item(i).Range.Copy()
                    win32clipboard.OpenClipboard()
                    data = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                    misc_objects.append(data)
                except:
                    print "Error copying misc objects in file: ",filePath
        if (doc.InlineShapes.Count != 0) & False:
            for i in range(1,doc.InlineShapes.Count+1):
                try:
                    doc.InlineShapes(i).Select()
                    Selection = word.Selection
                    Selection.CopyAsPicture()
                    im = ImageGrab.grabclipboard()
                    im.save(filePath.split(".")[0]+"_"+str(i)+".png",'PNG')
                except:
                    print "Error saving images from file: ",filePath
        end = time.clock()
        print "Time Taken:",end-start
        doc.Close()
        docxList.append(string)
        fileList.append(filePath)
        objectList.append(misc_objects)
    word.Application.Quit(-1)
    return fileList, docxList, objectList, fileNameList

if __name__ == "__main__":
    print getDocxsStr("Examples\\test")[0]