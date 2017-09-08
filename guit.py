from tkinter import *


class ValueAverage:

    def __init__(self, master):
        frame = Frame(master)
        frame.pack

        self.valueLab = Label(master, text = 'value', bg = 'green')
        self.averageLab = Label(master, text = 'average', bg = 'yellow')
        self.valueLab.grid(row = 0, sticky=NE)
        self.averageLab.grid(row = 1, sticky=NE)
        Grid.columnconfigure(frame, 1, weight=1)
        Grid.columnconfigure(frame, 0, weight=1)

root = Tk()


name = Label(root, text='SPX.i')
price = Label(root, text='2451.54')
frame_1 = Frame(root)
frame_2 = Frame(root)
range52 = Canvas(root, height = 3, bg='red')
a = ValueAverage(frame_1)
b = ValueAverage(frame_2)

frame_1.pack()



root.mainloop()
