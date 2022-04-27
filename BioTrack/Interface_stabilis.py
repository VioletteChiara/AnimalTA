from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
import time
import numpy as np
from BioTrack import Class_stabilise, UserMessages, Class_Lecteur


class Stabilise(Frame):
    def __init__(self, parent, boss, main_frame, Video_file, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.main_frame=main_frame
        self.boss=boss
        self.parent=parent
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.Vid = Video_file
        self.first=True

        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]


        # Nom de la video et changer de video:
        self.canvas_video_name = Canvas(self, bd=2, highlightthickness=1, relief='flat')
        self.canvas_video_name.grid(row=0, column=0, sticky="ew")

        self.dict_Names = {self.main_frame.list_projects[i].Video.Name: self.main_frame.list_projects[i] for i in range(0, len(self.main_frame.list_projects)) if self.main_frame.list_projects[i].Video.Stab}

        self.liste_videos_name = [V.Name for V in self.main_frame.liste_of_videos]
        holder = StringVar()
        holder.set(self.Vid.Name)
        self.bouton_change_vid = OptionMenu(self.canvas_video_name, holder, *self.dict_Names.keys(),
                                            command=self.change_vid)
        self.bouton_change_vid.config(font=("Arial", 15))
        self.bouton_change_vid.grid(row=0, column=0, sticky="we")

        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=100)  ########NEW


        # Visualisation de la video et barre de temps
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()


        #Pour l'utilisateur:
        self.canvas_user = Frame(self.parent,  highlightthickness=4, relief='flat', highlightbackground="RoyalBlue3")
        self.canvas_user.grid(row=0, column=1, sticky="new")
        Info_title=Label(self.canvas_user, text=self.Messages["Info"],  justify=CENTER, background="RoyalBlue3", fg="white", font=("Helvetica", 16, "bold"))
        Info_title.grid(row=0, sticky="new")
        self.user_message = StringVar()
        self.user_message.set(self.Messages["Stab1"])
        self.User_help = Label(self.canvas_user, textvariable=self.user_message, width=35, wraplengt=200, borderwidth=2,
                               justify=LEFT)
        self.User_help.grid(sticky="nsew")

        # Validate
        self.canvas_validate = Canvas(self.parent, bd=2, highlightthickness=1, relief='ridge', background="black")
        self.canvas_validate.grid(row=1, column=1, sticky="sew")
        Grid.columnconfigure(self.canvas_validate, 0, weight=1)  ########NEW
        self.B_Validate=Button(self.canvas_validate, text=self.Messages["Validate"],bg="green", command=self.End_of_window)#######NEW
        self.B_Validate.grid(row=0,column=0, sticky="new")#######NEW


    def change_vid(self, vid):
        self.End_of_window()
        self.dict_Names[vid].check_stab()


    def modif_image(self, img):
        new_img = (Class_stabilise.find_best_position(Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=img, show=True))
        if self.Scrollbar.active_pos>self.Scrollbar.crop_end or self.Scrollbar.active_pos<self.Scrollbar.crop_beg:
            new_img = cv2.addWeighted(new_img, 1, new_img, 0, 1)

        if self.first:
            self.Vid_Lecteur.Size=(new_img.shape[0],new_img.shape[1])
            self.Vid_Lecteur.zoom_sq = [0, 0, new_img.shape[1], new_img.shape[0]]

        self.Vid_Lecteur.afficher_img(new_img)
        self.first = False

    def End_of_window(self):
        self.Vid_Lecteur.proper_close()
        self.unbind_all("<Button-1>")
        self.boss.update()
        self.grab_release()
        self.canvas_validate.grid_forget()
        self.canvas_validate.destroy()
        self.canvas_user.grid_forget()
        self.canvas_user.destroy()
        self.main_frame.return_main()


    def pressed_can(self, Pt):
        pass

    def moved_can(self, Pt):
        pass

    def released_can(self, Pt):
        pass




"""
root = Tk()
root.geometry("+100+100")
Video=Class_Video.Video(File_name="D:/Araignees_Sociales/Videos_Guyane/Videos_converties/Anelosimus_011019 (1).avi")
Video.Cropped=[1,[0,10000]]
interface = Stabilise(parent=root, boss="none", Video_file=Video)
root.mainloop()
"""
