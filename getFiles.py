import os, glob, zipfile, lxml.etree
from html2text import *
from pydocx import *

def getDocxStr(docxFile):
    """ Gets the document string from the file using a little bit of trickery with docx2html and html2text. """
    # We can deal just fine with unicode and probably should, so that we get better formatted answers.
    newText = docx2html(docxFile)
    fileStr = html2text(newText)
    fileStr = fileStr.replace(u"\u2013","-")
    return fileStr

def getDocxsFromFolder(folderPath):
    fileList = []
    fileNameList = []
    fullPath = []
    lastModifiedAuthors = []
    excelFiles = {}

    for filePath in glob.glob(folderPath+"\*.docx"):
        fileNameList.append(filePath.split("\\")[-1])
        excelFiles[fileNameList[-1].split("-")[0]] = glob.glob(folderPath+"\\"+fileNameList[-1].split("-")[0]+"*.xlsx")
        fileStr = getDocxStr(filePath)
        fileList.append(fileStr)
        fullPath.append(filePath)

        zf = zipfile.ZipFile(filePath)
        doc = lxml.etree.fromstring(zf.read('docProps/core.xml'))
        ns = {"cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"}
        lastModifiedAuthors.append(doc.xpath("//cp:lastModifiedBy", namespaces=ns)[0].text)
    return fileList, fileNameList, fullPath, lastModifiedAuthors, excelFiles


if __name__ == "__main__":
    docxStack, fileNameList, fullPath, lastModifiedAuthors, excelFiles = getDocxsFromFolder("Examples\\test")
    # print len(docxStack)
    # print docxStack[2]