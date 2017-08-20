from tkinter import *

root = Tk()
frame1 = []
frame2 = []
c = 0
numberofboxes = 8 #change this to increase the number of boxes

for i in range(numberofboxes):
    if i % 4 == 0: #checks if the current box is the fourth in row
        c = c + 1 #if the current box is the forth in the row then this runs and increases a counter which we later use to determine the row
    if len(frame1) != c: #checks if the number of rows currently existing matches the number there should be
        frame1.append(Frame(root)) #if the numbers don't match this runs and creates a new frame which acts as another row
        frame1[c-1].pack(expand="True", fill="both") #packs the new row
    frame2.append(Frame(frame1[c-1], bg="green")) #this is where the boxes are created
    frame2[i].pack(ipadx="50", ipady="50", side="left", padx="10", pady="10", expand="True", fill="both") #this is where the boxes are placed on the screen

for i in range(len(frame2)): #this for loop places the items inside each box, all of this can be replaced with whatever is needed
    Label(frame2[i], text="CO"+str(i), bg="green", fg="white").pack(side="top", anchor="w")
    Label(frame2[i], text="12165.1"+str(i), bg="green", fg="white").pack(side="top", anchor="w")
    Label(frame2[i], text="+60.7"+str(i), bg="green", fg="white").pack(side="bottom", anchor="e")
    Label(frame2[i], text="+1.2"+str(i)+"%", bg="green", fg="white").pack(side="bottom", anchor="e")

root.mainloop()
