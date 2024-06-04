from tkinter import *
from tkinter import ttk
import os
from AnimalTA.A_General_tools import UserMessages, Color_settings
import math
import cv2
from copy import deepcopy
from tkinter import messagebox

class Extend(Frame):
    """ This Frame display a list of the videos from the project.
    The user can select some of them to extend some parameters defined for the previously selected video"""
    def __init__(self, parent, boss, Video_file, file, **kwargs):
        #value=the value of the parameter
        #type= the type of parameter (arenas, fps, tracking preparation, etc)
        #if do_self = True, the selected video will also be modified
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.grid(sticky="nsew")
        self.boss=boss
        self.parent=parent
        self.Vid = Video_file
        self.file=file

        #Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()

        Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW

        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title("Select individual")

        self.yscrollbar = ttk.Scrollbar(self)
        self.yscrollbar.grid(row=1,column=1, sticky="ns")
        self.Liste=Listbox(self, selectmode = BROWSE, width=100, yscrollcommand=self.yscrollbar.set)
        self.yscrollbar.config(command=self.Liste.yview)

        Delay_Fr=Frame(self)
        Delay_Fr.grid(row=2,column=0,columnspan=2, sticky="ew")

        self.Delay_Label = Label(Delay_Fr, text="Delay between video and imported file (sec):")
        self.Delay_Label.grid(row=0, column=0, sticky="ns")
        self.Delay_val=DoubleVar()
        self.Delay_val.set(0)
        self.Delay=Entry(Delay_Fr, textvariable=self.Delay_val)
        self.Delay.grid(row=0, column=1, sticky="ns")

        #To validate and share the parameters
        self.bouton=Button(self,text=self.Messages["Validate"],command=self.validate)
        self.bouton.grid(row=3, sticky="nsew")

        #We add all the individuals
        for i in range(len(self.Vid.Identities)):
            self.Liste.insert(i, "Arena: " + str(self.Vid.Identities[i][0]) + " Ind: " + str(self.Vid.Identities[i][1]))

        self.Liste.grid(row=1,column=0, sticky="nsew")

        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=100)  ########NEW

        self.grab_set()
        self.parent.protocol("WM_DELETE_WINDOW", self.parent.destroy)


    def validate(self):
        if len(self.Liste.curselection())>0:
            self.boss.load_file(self.file, self.Liste.curselection()[0], self.Delay_val.get())
            self.parent.destroy()




"""
root = Tk()
root.geometry("+100+100")
Video_file=Class_Video.Video(File_name="D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01.avi")
Video_file.Back[0]=True

im=cv2.imread("D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01_background.bmp")
im=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
Video_file.Back[1]=im
interface = Scale(parent=root, boss=None, Video_file=Video_file)
root.mainloop()
"""