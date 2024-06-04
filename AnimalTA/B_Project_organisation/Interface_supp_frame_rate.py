from tkinter import *
from AnimalTA.A_General_tools import Color_settings, UserMessages
import math
import PIL
import numpy as np

class Details_fps(Frame):
    """ This is a small Frame in which the user can define the nomber of targets per arena, in the case the number is variable between arenas."""
    def __init__(self, parent, boss, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.boss=boss
        self.grid(sticky="nsew")
        self.config(**Color_settings.My_colors.Frame_Base)
        self.grab_set()

        Grid.columnconfigure(self.parent,0,weight=1)
        Grid.rowconfigure(self.parent, 0, weight=1)

        Grid.columnconfigure(self,0,weight=1)
        Grid.rowconfigure(self, 0, weight=10)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 2, weight=1)


        #Message importation
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        self.Messages = UserMessages.Mess[self.Language.get()]
        f.close()


        warning=Label(self,text=self.Messages["Change_Fps1"],**Color_settings.My_colors.Label_Base)
        warning.grid(row=0,column=0, columnspan=4)
        warning.bind('<Configure>', lambda e: warning.config(wraplength=self.parent.winfo_width()))
        self.new_val_fps=StringVar()
        self.Entry_fps=Entry(self,textvariable=self.new_val_fps,**Color_settings.My_colors.Entry_Base)
        self.Entry_fps.grid(row=1, column=0)

        Label(self, text=self.Messages["fps"]+"   <>   "+self.Messages["frame_every"],**Color_settings.My_colors.Label_Base).grid(row=1, column=1)

        self.new_val_spf = StringVar()
        self.Entry_spf=Entry(self,textvariable=self.new_val_spf, **Color_settings.My_colors.Entry_Base)
        self.Entry_spf.grid(row=1, column=2)
        Label(self, text=self.Messages["Crop9"],**Color_settings.My_colors.Label_Base).grid(row=1, column=3)

        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title("")

        #Validation button
        self.B_validate = Button(self, text=self.Messages["Validate"], command=self.validate, **Color_settings.My_colors.Button_Base)
        self.B_validate.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.B_validate.grid(columnspan=4, sticky="ew")

        self.new_val_fps.trace('w', self.change_fps)
        self.new_val_spf.trace('w', self.change_spf)
        self.new_val_fps.set(self.boss.Video.Frame_rate[0])


    def change_fps(self, *args):
        try:
            new_spf=1/float(self.new_val_fps.get())
            if new_spf<0:
                raise ValueError('The user choose a negative value.')

            if new_spf!=self.new_val_spf.get():
                self.new_val_spf.set(new_spf)

            self.Entry_fps.config(**Color_settings.My_colors.Entry_Base)
            self.Entry_spf.config(**Color_settings.My_colors.Entry_Base)
            self.B_validate.config(state="normal",background=Color_settings.My_colors.list_colors["Validate"],
                                   fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        except:
            self.Entry_fps.config(**Color_settings.My_colors.Entry_error)
            self.B_validate.config(state="disable",**Color_settings.My_colors.Button_Base)


    def change_spf(self, *args):

        try:
            new_fps = 1 / float(self.new_val_spf.get())

            if new_fps<0:
                raise ValueError('The user choose a negative value.')

            if new_fps != self.new_val_fps.get():
                self.new_val_fps.set(new_fps)

                self.Entry_fps.config(**Color_settings.My_colors.Entry_Base)
                self.Entry_spf.config(**Color_settings.My_colors.Entry_Base)
                self.B_validate.config(state="normal", background=Color_settings.My_colors.list_colors["Validate"],
                                       fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        except:
            self.Entry_spf.config(**Color_settings.My_colors.Entry_error)
            self.B_validate.config(state="disabled",**Color_settings.My_colors.Button_Base)


    def validate(self):
        try:
            new_frame_rate = float(self.new_val_fps.get())

            one_every = self.boss.Video.Frame_rate[0] / new_frame_rate
            new_frame_nb=int(self.boss.Video.Frame_nb[0] / (self.boss.Video.Frame_rate[0] / new_frame_rate))

            if new_frame_nb>=10:
                self.boss.Video.Cropped[1][0] = round(round(self.boss.Video.Cropped[1][0] / one_every) * one_every)  # Avoid to try to open un-existing frames after changes in frame-rate
                self.boss.Video.Cropped[1][1] = round(round(self.boss.Video.Cropped[1][1] / one_every) * one_every)
                self.boss.Video.Frame_rate[1]=new_frame_rate
                self.boss.Video.Frame_nb[1] = new_frame_nb

                #Save and destroy the parent window
                self.boss.update()
                self.grab_release()
                self.parent.destroy()

        except:
            pass





