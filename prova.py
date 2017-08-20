import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# Base size
normal_width = 1920
normal_height = 1080

# Get screen size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Get percentage of screen size from Base size
percentage_width = screen_width / (normal_width / 100)
percentage_height = screen_height / (normal_height / 100)

# Make a scaling factor, this is bases on average percentage from
# width and height.
scale_factor = ((percentage_width + percentage_height) / 2) / 100

# Set the fontsize based on scale_factor,
# if the fontsize is less than minimum_size
# it is set to the minimum size
fontsize = int(14 * scale_factor)
minimum_size = 8
if fontsize < minimum_size:
    fontsize = minimum_size

# Create a style and configure for ttk.Button widget
default_style = ttk.Style()
default_style.configure('New.TButton', font=("Helvetica", fontsize))

frame = ttk.Frame(root)
button = ttk.Button(frame, text="Test", style='New.TButton')

frame.grid(column=0, row=0)
button.grid(column=0, row=0)

root.mainloop()
