import wx, os, time, win32clipboard 

class CommentBrowser(wx.Frame):
    def __init__(self, parent, initialPosition, initialSize):
        wx.Frame.__init__(self, parent, title='Comment Browser', pos=initialPosition, size=initialSize)
        self.panel = wx.Panel(self)
        self.parent = parent

        def onClose(event):
            self.Hide()
        self.Bind(wx.EVT_CLOSE, onClose)

        self.commentsDict = {}

        self.selectedStudent = "<<Student Name>>"
        self.createCommentsWindow()

    def setStudent(self, student):
        if student not in self.commentsDict.keys():
            defaultText = "Hi "+student.split()[0]+",\n\n"
            self.commentsDict[student] = defaultText
        self.selectedStudent = student
        self.title.SetLabel("Comments for: "+self.selectedStudent)
        self.currentComment.ChangeValue(self.commentsDict[student])

    def saveComment(self, event):
        self.commentsDict[self.selectedStudent] = self.currentComment.GetValue()

    def addComment(self, comment, redundentCheck=False):
        if comment not in self.currentComment.GetValue():
            original = self.currentComment.GetValue()
            self.currentComment.SetValue(original + comment)

    def createCommentsWindow(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.title = wx.StaticText(self.panel, wx.ID_ANY, label="Comments for: <<Student Name>>")
        self.titlefont = wx.Font(18,wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        self.title.SetFont(self.titlefont)
        sizer.Add(self.title, proportion=0, flag=wx.ALIGN_CENTER, border=0)

        self.currentComment = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE, value="")
        self.currentComment.Bind(wx.EVT_TEXT, self.saveComment)


        b_copy = wx.Button(self.panel, wx.ID_ANY, "Copy Comment")
        b_copy.SetToolTipString("Copies the current comment to the clipboard.")
        b_copy.Bind(wx.EVT_BUTTON, self.copyComment)
        bsizer.Add(b_copy, 1, flag=wx.GROW|wx.ALL, border=5)

        sizer.Add(self.currentComment, 1, flag=wx.ALL|wx.GROW, border=0)
        sizer.Add(bsizer,0,flag=wx.ALL|wx.GROW,border=0)

        self.panel.SetSizer(sizer)
        self.Layout()

    def display(self, event):
        w,h = self.parent.GetSizeTuple()
        x,y = self.parent.GetPositionTuple()
        self.SetPosition((w+x,y))
        self.Show()
        self.Raise()

    def copyComment(self, event):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(self.currentComment.GetValue())
        win32clipboard.CloseClipboard()