from tkinter import *
from BioTrack import UserMessages


class Modify(Frame):
    def __init__(self, parent, boss, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.boss=boss
        self.grid()
        self.grab_set()
        self.parent.attributes('-toolwindow', True)

        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()

        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title("Modify parameters of border")


        self.Label_wlen=Label(self, text="Type")
        self.Label_wlen.grid(row=0, columnspan=3)

        self.Type_H=Checkbutton(self,text="Right and Left\n only for quadrilateral arenas", variable=self.boss.Tborder, onvalue=0, width=15, anchor="w")
        self.Type_V=Checkbutton(self,text="Top and Bottom\n only for quadrilateral arenas", variable=self.boss.Tborder, onvalue=1, width=15, anchor="w")
        self.Type_T=Checkbutton(self,text="All borders", variable=self.boss.Tborder, onvalue=2, width=15, anchor="w")
        self.Type_H.grid(row=1, column=0)
        self.Type_V.grid(row=1, column=1)
        self.Type_T.grid(row=1, column=2)

        self.columnconfigure(2, minsize=30)

        self.Label_wlen=Label(self, text="Width")
        self.Label_wlen.grid(row=3, columnspan=3)

        self.Distance_to_cons_entry = Entry(self, textvariable=self.boss.Distance_limit)
        self.Distance_to_cons_entry.grid(row=4, columnspan=2, sticky="nsew")

        self.Show_border=Button(self,text="Show", command=self.show)
        self.Show_border.grid(row=5)

        self.Validate_param=Button(self,text="Validate",command=self.validate)
        self.Validate_param.grid(row=5, column=1)

    def show(self):
        self.boss.find_areas()

    def validate(self):
        self.boss.find_areas()
        self.grab_release()
        self.parent.destroy()

'''
root = Tk()
root.geometry("+100+100")

interface = Modify(parent=root, boss=None)
root.mainloop()
'''