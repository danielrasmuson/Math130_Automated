import wx, os, time

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
        self.createComments()

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

    def createComments(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.title = wx.StaticText(self.panel, wx.ID_ANY, label="Comments for: <<Student Name>>")
        titlefont = wx.Font(18,wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        self.title.SetFont(titlefont)
        sizer.Add(self.title, proportion=0, flag=wx.ALIGN_CENTER, border=0)

        self.currentComment = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE, value="")
        self.currentComment.Bind(wx.EVT_TEXT, self.saveComment)
        sizer.Add(self.currentComment, 1, flag=wx.ALL|wx.GROW, border=0)

        self.panel.SetSizer(sizer)
        self.Layout()

    def display(self, event):
        w,h = self.parent.GetSizeTuple()
        x,y = self.parent.GetPositionTuple()
        self.SetPosition((w+x,y))
        self.Show()
        self.Raise()