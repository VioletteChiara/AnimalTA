from tkinter import *
from functools import partial
from AnimalTA.A_General_tools import Color_settings, UserMessages
import os

class Messagebox(Toplevel):
    """ This Frame display a question and a list of possible answers (Possibilities).
    The user can select some of them. Some options cab be hilighted using the "hilight" option and giving a list of possibilities index to be hilighted"""
    def __init__(self, parent, title="", message="", Possibilities=[], entry=False, hilight=[], **kwargs):
        Toplevel.__init__(self, parent)
        self.geometry("400x200")
        self.iconbitmap(UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Logo.ico")))
        self.title(title)
        self.update_idletasks()
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.result=None
        self.grab_set()
        self.entry=entry

        if len(Possibilities)==0:
            Possibilities=[self.Messages["Yes"],
                           self.Messages["No"]]





        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 2, weight=1, minsize=2)
        Grid.columnconfigure(self, 0, weight=1)

        row=0
        self.label=Label(self,text=message, height=5, **Color_settings.My_colors.Label_Base, wraplength=300)
        self.label.grid(row=row, column=0, columnspan=len(Possibilities), sticky="nsew")
        row += 1

        if self.entry:
            self.entry_val=StringVar()
            Entry(self, textvariable=self.entry_val, **Color_settings.My_colors.Entry_Base).grid(row=row, column=0, columnspan=len(Possibilities))
            row+=1


        count=0
        column=0
        for poss in Possibilities:
            Grid.columnconfigure(self, column, weight=1)
            if count in hilight:
                row+=1
                column=0
                button = Button(self, text=poss, command=partial(self.return_val, count),**Color_settings.My_colors.Button_Base, padx=10, pady=5)
                button.grid(row=row, column=column, columnspan=3, padx=2, pady=2, sticky="ew")
                row += 1
            else:
                button=Button(self, text=poss, command=partial(self.return_val, count), **Color_settings.My_colors.Button_Base, padx=10, pady=5)
                button.grid(row=row,column=column, padx=2, pady=2, sticky="ew")

            column +=1
            if count>0 and count%2==0:
                row+=1
                column=0

            count+=1

        row += 1

        self.bind('<Configure>', self.resize)

    def resize(self,event):
        self.label.config(wraplength=event.width)




    def return_val(self, val):
        if self.entry:
            if self.entry_val.get()!="":
                self.result=[val, self.entry_val.get()]
            else:
                return()
        else:
            self.result=val
        self.grab_release()
        self.destroy()







