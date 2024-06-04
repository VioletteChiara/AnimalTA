from tkinter import *
from functools import partial
from AnimalTA.A_General_tools import Color_settings, UserMessages
import os

class Messagebox(Toplevel):
    """ This Frame display a list of the videos from the project.
    The user can select some of them to extend some parameters defined for the previously selected video"""
    def __init__(self, parent, title="", message="", Possibilities=[], **kwargs):
        Toplevel.__init__(self, parent)
        self.iconbitmap(UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Logo.ico")))
        self.title(title)
        self.update_idletasks()
        self.config(**Color_settings.My_colors.Frame_Base)
        self.parent=parent
        self.result=None
        self.grab_set()

        if len(Possibilities)==0:
            Possibilities=[self.Messages["Yes"],self.Messages["No"]]

        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 2, weight=1, minsize=2)

        Label(self,text=message, height=5, **Color_settings.My_colors.Label_Base, wraplength=300).grid(row=0, column=0, columnspan=len(Possibilities))


        count=0
        for poss in Possibilities:
            Grid.columnconfigure(self, count, weight=1)
            button=Button(self, text=poss, command=partial(self.return_val, count), **Color_settings.My_colors.Button_Base, padx=10, pady=5)
            button.grid(row=1,column=count, padx=5, pady=5, sticky="ew")
            count+=1

    def return_val(self, val):
        self.result=val
        self.grab_release()
        self.destroy()







