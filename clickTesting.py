from Tkinter import *

string = "Daniel"
def callback():
    w = Label(text=string)
    w.pack()

b = Button(text="click me", command=callback)
b.pack()

mainloop()