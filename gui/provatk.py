from tkinter import *

root = Tk()
frame = Frame(root,                   # creating frame in root
              width=1440,
              height=900,
              bg="lightblue")
frame.grid(in_=root)                  # add frame in root row=0 column=0 (default)

canv1 = Canvas(frame,                 # creating canvas
               bg="red",
               height=10)
canv2 = Canvas(frame,
               bg="green",
               height=20)
canv3 = Canvas(frame,
               bg="yellow",
               height=30)
canv4 = Canvas(frame,
               bg="blue",
               height=40)

canv1.grid(in_=frame, row=0, column=0, sticky="n") #add canvas in the grid
canv2.grid(in_=frame, row=0, column=1, sticky="n")
canv3.grid(in_=frame, row=0, column=2, sticky="n")
canv4.grid(in_=frame, row=0, column=3, sticky="n")
frame.columnconfigure(0, weight=1)     # set weights
frame.columnconfigure(1, weight=2)
frame.columnconfigure(2, weight=3)
frame.columnconfigure(3, weight=2)

root.mainloop()
