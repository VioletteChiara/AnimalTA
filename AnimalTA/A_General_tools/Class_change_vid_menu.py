from tkinter import *
from AnimalTA.B_Project_organisation import Class_Row_Videos
from AnimalTA.A_General_tools import Color_settings


"This Frame is used to propose the OptionMenu with all available videos, so the user can jump from one video to another without going back to the main menu"
class Change_Vid_Menu(Frame):
    def __init__(self, parent, main_frame, Vid, func):
        Frame.__init__(self, parent, bd=2, highlightthickness=1, relief='flat', **Color_settings.My_colors.Frame_Base)
        self.main_frame=main_frame
        self.Vid=Vid
        self.parent=parent
        self.func=func

        #All videos are available for pretracking processes, but only tracked videos are available for post-tracking processes
        if self.func!="analysis" and self.func!="check" and self.func!="event":
            self.dict_Names = {Video.User_Name: Video for Video in self.main_frame.liste_of_videos}
        else:
            self.dict_Names = {Video.User_Name: Video for Video in self.main_frame.liste_of_videos if Video.Tracked}
        holder = StringVar()
        holder.set(self.Vid.User_Name)
        self.bouton_change_vid = OptionMenu(self, holder, *self.dict_Names.keys(), command=self.change_vid)
        self.bouton_change_vid["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
        self.bouton_change_vid.config(**Color_settings.My_colors.Button_Base)
        self.bouton_change_vid.grid(row=0, column=0, sticky="we")


    def change_vid(self, vid):
        #Change the current video for another one (vid)
        #The speed info indicates at which speed the Video-Reader should be opened (to avoid that the user needs to change each time when changing the vidéo)
        if self.func != "mask" and self.func!="scale":
            speed=self.parent.Vid_Lecteur.speed.get()
        if self.func =="analysis":
            CheckVar=self.parent.CheckVar.get()
        for V in self.main_frame.liste_of_videos:
            if V==self.dict_Names[vid] and V!=self.Vid:
                self.parent.End_of_window()
                self.main_frame.list_projects.append(Class_Row_Videos.Row_Can(parent=self.main_frame.canvas_rows, main_boss=self.main_frame, Video_file=V, proj_pos=len(self.main_frame.list_projects)))
                if self.func=="crop":
                    self.main_frame.list_projects[-1].crop_vid(speed)
                elif self.func=="mask":
                    self.main_frame.list_projects[-1].mask_vid()
                elif self.func == "stab":
                    self.main_frame.list_projects[-1].check_stab(speed)
                elif self.func == "scale":
                    self.main_frame.list_projects[-1].scale_vid()
                elif self.func=="param":
                    self.main_frame.selected_vid = self.dict_Names[vid]
                    self.main_frame.Beg_track(speed)
                elif self.func=="analysis":
                    self.main_frame.selected_vid = self.dict_Names[vid]
                    self.main_frame.analyse_track(CheckVar, speed)
                elif self.func=="check":
                    self.main_frame.selected_vid = self.dict_Names[vid]
                    self.main_frame.check_track(speed)
                elif self.func=="event":
                    self.main_frame.selected_vid = self.dict_Names[vid]
                    self.main_frame.add_events(speed)
                elif self.func=="seq":
                    self.main_frame.selected_vid = self.dict_Names[vid]
                    self.main_frame.add_events(speed)
                break