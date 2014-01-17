# -*- coding: utf-8 -*-
import win32com.client as win32
import os,glob
os.system('cls' if os.name=='nt' else 'clear')

def get_files(document_extension="docx"):
    return glob.glob("*."+str(document_extension))

if __name__ == "__main__":
    word = win32.gencache.EnsureDispatch('Word.Application')
    word.Visible = 0
    for infile in get_files():
        doc = word.Documents.Open(os.getcwd()+'\\'+infile)
        string = doc.Content.Text.encode('utf8')
        
        # print len(string)
        print "begin:\n"
        print string
        print "\nend"
    word.Application.Quit(-1)