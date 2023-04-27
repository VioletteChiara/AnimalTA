from tkinter import *
import os
import cv2
from AnimalTA.A_General_tools import Class_change_vid_menu, Class_Lecteur, UserMessages, User_help, Class_stabilise
import math
import numpy as np
from functools import partial

class Stabilise(Frame):
    """In this Frame, the user can choose which points of interest will be used to stabilise the video (correction for optical flow)"""
    def __init__(self, parent, boss, main_frame, Video_file, speed=0, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.main_frame=main_frame
        self.boss=boss
        self.parent=parent
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.Vid = Video_file
        self.first=True
        self.prev_points=self.Vid.Stab[1]
        if not self.Vid.Stab[0]:
            self.Vid.Stab[0]=True

        #Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        # Name of the vieo and optionmenu to jump from one video to another
        self.choice_menu = Class_change_vid_menu.Change_Vid_Menu(self, self.main_frame, self.Vid, "stab")
        self.choice_menu.grid(row=0, column=0)

        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=100)  ########NEW



        # Information panel for user
        self.HW= User_help.Help_win(self.parent, default_message=self.Messages["Stab1"], width=250)
        self.HW.grid(row=0, column=1,sticky="nsew")


        # Canvas with options
        self.canvas_validate = Canvas(self.parent, bd=2, highlightthickness=1, relief='ridge', background="black")
        self.canvas_validate.grid(row=1, column=1, sticky="sew")
        Grid.columnconfigure(self.canvas_validate, 0, weight=1)

        self.Param1=IntVar()
        Scale_pts_dist=Scale(self.canvas_validate, variable=self.Param1, from_=0, to=1000, resolution=10, orient=HORIZONTAL, label=self.Messages["Stab6"], command=self.redo_opt_pts)
        Scale_pts_dist.grid(row=0,column=0, sticky="new")
        self.Param1.set(self.Vid.Stab[2][0])
        Scale_pts_dist.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Stab10"]))
        Scale_pts_dist.bind("<Leave>", self.HW.remove_tmp_message)


        self.Param2=IntVar()
        Scale_pts_blck=Scale(self.canvas_validate, variable=self.Param2, from_=1, to=50, resolution=1, orient=HORIZONTAL, label=self.Messages["Stab7"], command=self.redo_opt_pts)
        Scale_pts_blck.grid(row=1,column=0, sticky="new")
        self.Param2.set(self.Vid.Stab[2][1])
        Scale_pts_blck.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Stab11"]))
        Scale_pts_blck.bind("<Leave>", self.HW.remove_tmp_message)

        self.Param3=DoubleVar()
        Scale_pts_qua=Scale(self.canvas_validate, variable=self.Param3, from_=0.001, to=0.25, resolution=0.001, orient=HORIZONTAL, label=self.Messages["Stab8"], command=self.redo_opt_pts)
        Scale_pts_qua.grid(row=2,column=0, sticky="new")
        self.Param3.set(self.Vid.Stab[2][2])
        Scale_pts_qua.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Stab12"]))
        Scale_pts_qua.bind("<Leave>", self.HW.remove_tmp_message)

        self.Param4=IntVar()
        Scale_pts_corner=Scale(self.canvas_validate, variable=self.Param4, from_=10, to=300, resolution=10, orient=HORIZONTAL, label=self.Messages["Stab9"], command=self.redo_opt_pts)
        Scale_pts_corner.grid(row=3,column=0, sticky="new")
        self.Param4.set(self.Vid.Stab[2][3])
        Scale_pts_corner.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Stab13"]))
        Scale_pts_corner.bind("<Leave>", self.HW.remove_tmp_message)

        self.B_Validate=Button(self.canvas_validate, text=self.Messages["Validate"],bg="#6AED35", command=self.End_of_window)
        self.B_Validate.grid(row=5,column=0, sticky="new")

        self.B_Validate_NContinue=Button(self.canvas_validate, text=self.Messages["Validate_NC"],bg="#6AED35", command=lambda: self.End_of_window(follow=True))
        self.B_Validate_NContinue.grid(row=6,column=0, sticky="ews")

        # Video reader
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=10)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Vid_Lecteur.speed.set(speed)
        self.Vid_Lecteur.change_speed()
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

    def modif_image(self, img=[], aff=False, **kwargs):
        #Draw the points of interest on the top of the image. Also combine the first image, the original image at the current frame and the stabilised result.
        if len(img) <= 10:
            new_img=np.copy(self.last_empty)
        else:
            self.last_empty = img
            new_img = np.copy(img)

        new_img= Class_stabilise.find_best_position(self.Vid, self.Vid_Lecteur.Prem_image_to_show, new_img, True, prev_pts=self.prev_points, scale=self.Vid_Lecteur.ratio)

        if self.Scrollbar.active_pos>self.Scrollbar.crop_end or self.Scrollbar.active_pos<self.Scrollbar.crop_beg:
            new_img = cv2.addWeighted(new_img, 1, new_img, 0, 1)

        if self.first:
            self.Vid_Lecteur.Size=(new_img.shape[0],new_img.shape[1])
            self.Vid_Lecteur.zoom_sq = [0, 0, new_img.shape[1], new_img.shape[0]]

        self.Vid_Lecteur.afficher_img(new_img)
        self.first = False

    def End_of_window(self, follow=False):
        self.Vid.Stab[1] = self.prev_points

        if follow and self.Vid != self.main_frame.liste_of_videos[-1]:
            for i in range(len(self.main_frame.liste_of_videos)):
                if self.main_frame.liste_of_videos[i]==self.Vid:
                    self.choice_menu.change_vid(self.main_frame.liste_of_videos[i+1].User_Name)
                    break
        else:
            #Properly close this Frame
            self.Vid_Lecteur.proper_close()
            self.unbind_all("<Button-1>")
            self.grab_release()
            self.canvas_validate.grid_forget()
            self.canvas_validate.destroy()
            self.HW.grid_forget()
            self.HW.destroy()
            self.main_frame.return_main()

    def redo_opt_pts(self, event):
        #Look for all points of interest
        minDistance=self.Param1.get()
        blockSize=self.Param2.get()
        quality = self.Param3.get()
        maxCorners = self.Param4.get()

        self.Vid.Stab[2][0]=self.Param1.get()
        self.Vid.Stab[2][1]=self.Param2.get()
        self.Vid.Stab[2][2] = self.Param3.get()
        self.Vid.Stab[2][3] = self.Param4.get()

        self.prev_points= Class_stabilise.find_pts(self.Vid, self.Vid_Lecteur.Prem_image_to_show, minDistance=minDistance, blockSize=blockSize, quality=quality, maxCorners=maxCorners)
        self.modif_image()

    def pressed_can(self, Pt, Shift):
        #If the user click on the image, we check if it was over a point of interest. If it is the case, the point of interest is removed.
        try:
            if self.prev_points==None:
                self.prev_points = Class_stabilise.find_pts(self.Vid, self.Vid_Lecteur.Prem_image_to_show, minDistance=self.Vid.Stab[2][0], blockSize=self.Vid.Stab[2][1], quality=self.Vid.Stab[2][2], maxCorners=self.Vid.Stab[2][3])
        except:
            pass
        
        for pt in range(len(self.prev_points)):
            dist=math.sqrt((self.prev_points[pt][0][0]-Pt[0])**2 + (self.prev_points[pt][0][1]-Pt[1])**2)
            if dist<10:
                self.prev_points=np.delete(self.prev_points, pt, axis=0)
                break
        self.modif_image()

    def moved_can(self, Pt, Shift):
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
