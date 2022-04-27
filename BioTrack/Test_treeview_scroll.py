from tkinter import *
from tkinter import ttk

root=Tk()
frame=Frame(root,width=300,height=300)
frame.pack(expand=True, fill=BOTH) #.grid(row=0,column=0)
canvas=Canvas(frame,bg='#FFFFFF',width=500,height=300)
canvas.grid()

tree=ttk.Treeview(canvas, heigh=25)
tree["columns"]=tuple(["Frame"]+[k for k in range(5)])
tree.heading('#0', text='', anchor=CENTER)
tree.column('#0', width=0, stretch=NO)
tree.column("Frame", anchor=CENTER, width=80)
tree.heading("Frame", text="Frame", anchor=CENTER)
tree.place(width=300)

hbar=Scrollbar(frame,orient=HORIZONTAL)
hbar.grid(sticky="ew")
hbar.config(command=tree.xview)
vbar=Scrollbar(frame,orient=VERTICAL)
vbar.grid()
vbar.config(command=tree.yview)
tree.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

root.mainloop()