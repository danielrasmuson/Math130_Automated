#must run "pip install pydocx"
#must run "pip install html2text"

import os, glob, zipfile, lxml.etree
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
    fullPath = []
    lastModifiedAuthors = []


    for filePath in glob.glob(folderPath+"\*.docx"):
        fileNameList.append(filePath.split("\\")[-1])
        fileStr = getDocxStr(filePath)
        fileList.append(fileStr)
        fullPath.append(filePath)

        zf = zipfile.ZipFile(filePath)
        doc = lxml.etree.fromstring(zf.read('docProps/core.xml'))
        ns = {"cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"}
        lastModifiedAuthors.append(doc.xpath("//cp:lastModifiedBy", namespaces=ns)[0].text)
    return fileList, fileNameList, fullPath, lastModifiedAuthors


if __name__ == "__main__":
    docxStack, fileNameList, fullPath, lastModifiedAuthors = getDocxsFromFolder("Examples\\test")
    # print len(docxStack)
    # print docxStack[2]