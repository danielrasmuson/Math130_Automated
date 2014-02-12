import wx, win32clipboard, smtplib

class CommentBrowser(wx.Frame):
    def __init__(self, parent, initialPosition, initialSize, database):
        wx.Frame.__init__(self, parent, title='Comment Browser', pos=initialPosition, size=initialSize)
        self.panel = wx.Panel(self)
        self.parent = parent
        self.database = database

        def onClose(event):
            self.Hide()
        self.Bind(wx.EVT_CLOSE, onClose)

        self.commentsDict = {}

        self.selectedStudent = "<<Student Name>>"
        self.createCommentsWindow()

        #for email
        self.username = False
        self.password = False
        self.emailDict = False

    def setStudent(self, student):
        self.selectedStudent = student
        self.title.SetLabel("Comments for: "+self.selectedStudent)
        if student in self.commentsDict.keys():
            self.currentComment.ChangeValue(self.commentsDict[student])
        else:
            self.defaultCommentButton("")

    def saveCommentsToDisk(self, event):
        dlg = wx.FileDialog(self.parent, "Choose where to save file:",defaultFile="comments.txt", style=wx.FD_SAVE)
        dlg.SetWildcard("Text File (*.txt)|*.txt")
        if dlg.ShowModal() == wx.ID_OK:
            f = open(dlg.GetPath(), "wb")
            for student in sorted(self.commentsDict.keys()):
                if "Everything looked great, but if you've got questions feel free to email me" not in self.commentsDict[student]:
                    f.write("~~~~~~~~~~~~~ "+student+" ~~~~~~~~~~~~~\n")
                    f.write(self.commentsDict[student])
                    f.write("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
            f.close()
            wx.MessageBox("Successfully saved comments to "+dlg.GetPath(), "Done", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()

    def autoSaveComment(self, event):
        self.commentsDict[self.selectedStudent] = self.currentComment.GetValue()

    def addComment(self, comment):
        self.currentComment.AppendText(comment)

    def createCommentsWindow(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.title = wx.StaticText(self.panel, wx.ID_ANY, label="Comments for: <<Student Name>>")
        self.titlefont = wx.Font(18,wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        self.title.SetFont(self.titlefont)
        sizer.Add(self.title, proportion=0, flag=wx.ALIGN_CENTER, border=0)

        self.currentComment = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE|wx.TE_RICH, value="")
        self.currentComment.Bind(wx.EVT_TEXT, self.autoSaveComment)


        #default comments
        b_default = wx.Button(self.panel, wx.ID_ANY, "Default\nComment")
        b_default.SetToolTipString("Loads the default comments using the wrong answers from the student.")
        b_default.Bind(wx.EVT_BUTTON, self.defaultCommentButton)
        bsizer.Add(b_default, 0, flag=wx.ALL, border=5)

        #copy comments
        b_copy = wx.Button(self.panel, wx.ID_ANY, "Copy\nComment")
        b_copy.SetToolTipString("Copies the current comment to the clipboard.")
        b_copy.Bind(wx.EVT_BUTTON, self.copyComment)
        bsizer.Add(b_copy, 0, flag=wx.ALL, border=5)

        #save comments
        b_save = wx.Button(self.panel, wx.ID_ANY, "Save All\nComments")
        b_save.SetToolTipString("Saves the coments to disk.")
        b_save.Bind(wx.EVT_BUTTON, self.saveCommentsToDisk)
        bsizer.Add(b_save, 0, flag=wx.ALL, border=5)

        #email comments
        b_email = wx.Button(self.panel, wx.ID_ANY, "Email\nComments")
        b_email.SetToolTipString("Once Email List has been loaded it will send this to a students email.")
        b_email.Bind(wx.EVT_BUTTON, self.sendEmail)
        bsizer.Add(b_email, 0, flag=wx.ALL, border=5)

        bsizer.AddStretchSpacer(1)

        #reset comments
        b_reset = wx.Button(self.panel, wx.ID_ANY, "Reset\nComment")
        b_reset.SetToolTipString("Clears the comments area to start again fresh.")
        b_reset.Bind(wx.EVT_BUTTON, self.resetComment)
        bsizer.Add(b_reset, 0, flag=wx.ALL, border=5)


        sizer.Add(self.currentComment, 1, flag=wx.ALL|wx.GROW, border=0)
        sizer.Add(bsizer,0,flag=wx.ALIGN_CENTER|wx.ALL|wx.GROW,border=0)

        self.panel.SetSizer(sizer)
        self.Layout()

    def resetComment(self, event):
        self.currentComment.SetValue("")

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

    def defaultCommentButton(self, event):
        self.currentComment.SetValue("Hi "+self.selectedStudent.split()[0]+",\n")
        for qNum in sorted(self.database.getQuestionKeys()):
            if (len(self.database.getReason(qNum)) > 0) & (self.database.getStudentQuestionScore(self.selectedStudent,qNum) != self.database.getQuestionPoints(qNum)):
                self.addComment("\nFor question #" + str(qNum) + " (" + str(self.database.getStudentQuestionScore(self.selectedStudent,qNum)) + " / " + str(self.database.getQuestionPoints(qNum)) + " points):\n"+self.database.getReason(qNum)+"\n")
            elif (len(self.database.getAnswer(qNum)) > 0) & (self.database.getStudentQuestionScore(self.selectedStudent,qNum) != self.database.getQuestionPoints(qNum)):
                self.addComment("\nFor question #" + str(qNum) + " (" + str(self.database.getStudentQuestionScore(self.selectedStudent,qNum)) + " / " + str(self.database.getQuestionPoints(qNum)) + " points):\nThe answer should have been: "+str(self.database.getAnswer(qNum))+"\n")
        if "For question #" in self.currentComment.GetValue():
            self.addComment("\nIf something isn't clear feel free to email me.\n")
        else:
            self.addComment("\nEverything looked great, but if you've got questions feel free to email me.\n")

    def sendEmail(self, event):
        def getEmailCredentials(self):
            dlg = wx.TextEntryDialog(self.panel, 'MNSU Email Address:',"Email Credentials","", style=wx.OK)
            dlg.ShowModal()
            self.username = dlg.GetValue()
            dlg.Destroy()

            dlg = wx.TextEntryDialog(self.panel, 'MNSU Star ID:',"Email Credentials","", style=wx.OK)
            dlg.ShowModal()
            self.starid = dlg.GetValue()
            dlg.Destroy()

            dlg = wx.PasswordEntryDialog(self.panel, 'Email password:',"Email Credentials","", style=wx.OK)
            dlg.ShowModal()
            self.password = dlg.GetValue()
            dlg.Destroy()

        def loadEmailList(self):
            dummyString = '"Matthew Priem" <'+self.username+'>;"Andrew Chase" <'+self.username+'>;"Tikhon Esaulenko" <'+self.username+'>;"Samuel Drummer" <'+self.username+'>;"James Lucas" <'+self.username+'>;"Jordan Pierce" <'+self.username+'>;"Tiana Johnson" <'+self.username+'>;"Emily Kasparek" <'+self.username+'>;"Trent Walters" <'+self.username+'>;"Ryan Neubauer" <'+self.username+'>;"Wesley Otto" <'+self.username+'>;"Genesis Garcia" <'+self.username+'>;"Amy Holscher" <'+self.username+'>;"Kaila Tomczik" <'+self.username+'>;"Philip Bowman" <'+self.username+'>;"Rahziya Akeem" <'+self.username+'>;"Joel Randall" <'+self.username+'>;"Daniel Rasmuson" <'+self.username+'>;"Joshua Musabyimana" <'+self.username+'>;"Samantha Sharp-Madson" <samantha.'+self.username+'>;"Richard Litchfield" <'+self.username+'>;"Raelin Setrum" <'+self.username+'>;"Zachary Cave" <'+self.username+'>;"Matthew Vandermark" <'+self.username+'>;"Isaac Noah" <'+self.username+'>;"Joshua Mikiska" <'+self.username+'>;"Edwig Vyncke" <'+self.username+'>'

            #asks for email list
            dlg = wx.TextEntryDialog(self.panel, 'Class List Email (d2l > class list > email > bcc field):',"Student Email List", dummyString, style=wx.OK)
            dlg.ShowModal()
            userEmailString = dlg.GetValue()
            dlg.Destroy()

            # pareses
            # ex "Matthew Priem" <'+self.username+'>;
            self.emailDict = {}
            for person in userEmailString.split(";"):
                email = person.split('<')[-1].replace(">","")
                name = person.split('"')[1]
                self.emailDict[name] = email

        def send(self):
            # Lab 1 - Score 27/30 - Math 130
            lab = self.database.getLab()
            score = self.parent.questionsArea.si_score.GetValue()
            subject = lab + " - Score " + str(score) +" - Math 130" #make this the lab name

            message = 'Subject: %s\n\n%s' % (subject, self.currentComment.GetValue())
            fromaddr = self.username
            toaddrs = self.emailDict[self.selectedStudent] #this would come from the list

            # The actual mail send
            try:
                server = smtplib.SMTP('smtp.office365.com', 587)
                server.starttls()
                server.login(self.starid + "@campus.mnsu.edu", self.password)
                server.sendmail(fromaddr, toaddrs, message)
                server.quit()

                # confirmation
                wx.MessageBox('Email Sent', '', wx.OK | wx.ICON_INFORMATION)
            except smtplib.SMTPAuthenticationError:
                # Error
                wx.MessageBox('Error - Email Credentials', '', wx.OK | wx.ICON_INFORMATION)

        if self.username == False or self.password == False:
            getEmailCredentials(self)

        if self.emailDict == False:
            loadEmailList(self)

        send(self)
