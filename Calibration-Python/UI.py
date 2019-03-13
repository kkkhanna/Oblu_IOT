import Tkinter
from Tkinter import *
import ttk
from ttk import *


def okbtn():
    stop1 = file("stop", 'w')
    stop1.close()
    root.destroy()

root = Tkinter.Tk()
Label(root,text='Plesase press ok  to stop data logging').pack()
Button(root,text='OK',command=okbtn).pack()

root.mainloop()