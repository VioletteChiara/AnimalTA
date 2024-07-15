from tkinter import *
import cv2
from AnimalTA.A_General_tools import Color_settings, Class_Lecteur, UserMessages, User_help, Class_stabilise
from AnimalTA.E_Post_tracking.b_Analyses import Functions_deformation
import math
import numpy as np
import os


class Deformation(Frame):
    """In this Frame, the user can choose which points of interest will be used to stabilise the video (correction for optical flow)"""

    def __init__(self, parent, Video_file, main_frame, speed=0, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.main_frame = main_frame
        self.parent = parent
        self.grid(rowspan=2, sticky="nsew")
        self.Vid = Video_file
        self.first = True
        if self.Vid.Stab[0]:
            self.prev_pts = self.Vid.Stab[1]

        self.parent.geometry("1200x750")

        self.or_positions=self.Vid.Analyses[4][1]#List of points used as reference
        self.corr_positions = self.Vid.Analyses[4][2]#List of points with corrected coordinates
        self.selected=None#If tye user click on a point, the id of the point is saved here

        # Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        Grid.columnconfigure(self.parent, 0, weight=1)
        Grid.rowconfigure(self.parent, 0, weight=1)
        Grid.columnconfigure(self.parent, 1, weight=1)

        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)

        Grid.rowconfigure(self, 1, weight=1)

        # Information panel for user
        self.HW = User_help.Help_win(self.parent, default_message=self.Messages["Ana_deform"], width=250)
        self.HW.grid(row=0, column=1, sticky="nsew")

        # Canvas with options
        self.canvas_validate = Canvas(self.parent, bd=2, highlightthickness=1, **Color_settings.My_colors.Frame_Base)
        self.canvas_validate.grid(row=1, column=1, sticky="sew")
        Grid.columnconfigure(self.canvas_validate, 0, weight=1)

        self.Delete_all = Button(self.canvas_validate, text=self.Messages["Mask8"], **Color_settings.My_colors.Button_Base,
                                 command=self.del_all)
        self.Delete_all.config(background=Color_settings.My_colors.list_colors["Danger"],fg=Color_settings.My_colors.list_colors["Fg_Danger"])
        self.Delete_all.grid(row=5, column=0, sticky="new")

        self.B_Validate = Button(self.canvas_validate, text=self.Messages["Validate"], **Color_settings.My_colors.Button_Base,
                                 command=self.End_of_window)
        self.B_Validate.config(background=Color_settings.My_colors.list_colors["Validate"],
                               fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.B_Validate.grid(row=6, column=0, sticky="new")


        # Video reader
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=0)
        self.Vid_Lecteur.grid(row=1, column=0, rowspan=2, sticky="nsew")
        self.Vid_Lecteur.speed.set(speed)
        self.Vid_Lecteur.change_speed()
        self.Scrollbar = self.Vid_Lecteur.Scrollbar

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

        self.bind_all("<Key>", self.suppress_pt)

        self.parent.protocol("WM_DELETE_WINDOW", self.leave)
        self.modif_image()

    def suppress_pt(self, event):
        if event.keysym == "Delete" and self.selected!=None:
            self.or_positions.pop(self.selected[1])
            self.corr_positions.pop(self.selected[1])
            self.selected=None
            self.modif_image()

    def del_all(self):
        self.or_positions=[]
        self.corr_positions=[]
        self.selected = None
        self.modif_image()


    def modif_image(self, img=[], aff=False, **kwargs):
        # Draw the points of interest on the top of the image. Also combine the first image, the original image at the current frame and the stabilised result.
        if len(img) <= 10:
            new_img = np.copy(self.last_empty)
        else:
            self.last_empty = img
            new_img = np.copy(img)

        # Image stabilisation
        if self.Vid.Stab[0]:
            new_img = (Class_stabilise.find_best_position(Vid=self.Vid, Prem_Im=self.Vid_Lecteur.Prem_image_to_show,
                                                          frame=new_img, show=False, prev_pts=self.prev_pts))

        new_img = Functions_deformation.correct(curr_img=new_img, ref_img=self.Vid_Lecteur.Prem_image_to_show,  or_pts=self.or_positions, corr_pts=self.corr_positions, ratio=self.Vid_Lecteur.ratio, selected=self.selected, scale=self.Vid.Scale[0])

        if self.Scrollbar.active_pos > self.Scrollbar.crop_end or self.Scrollbar.active_pos < self.Scrollbar.crop_beg:
            new_img = cv2.addWeighted(new_img, 1, new_img, 0, 1)

        if self.first:
            self.Vid_Lecteur.Size = (new_img.shape[0], new_img.shape[1])
            self.Vid_Lecteur.zoom_sq = [0, 0, new_img.shape[1], new_img.shape[0]]

        self.Vid_Lecteur.afficher_img(new_img)
        self.first = False


    def leave(self):
        self.Vid_Lecteur.proper_close()
        self.main_frame.Vid_Lecteur.bindings()
        self.grab_release()
        self.HW.grid_forget()
        self.HW.destroy()
        self.destroy()
        self.main_frame.change_type_coos(modif=True)
        self.main_frame.modif_image()
        self.parent.destroy()

    def End_of_window(self, follow=False):
        # Properly close this Frame
        self.Vid_Lecteur.proper_close()
        if len(self.or_positions) >= 4 and len(self.or_positions) == len(self.corr_positions):
            or_pts = np.float32(self.or_positions)
            corr_pts = np.float32(self.corr_positions)
            M, mask = cv2.findHomography(or_pts, corr_pts)
        else:
            M=[]
        self.Vid.Analyses[4]=[M,self.or_positions,self.corr_positions]
        self.main_frame.Vid_Lecteur.bindings()
        self.grab_release()
        self.HW.grid_forget()
        self.HW.destroy()
        self.destroy()
        self.main_frame.change_type_coos(modif=True)
        self.main_frame.modif_image()
        self.parent.destroy()


    def pressed_can(self, Pt, *args):
        # If the user click on the image, we add a corresponding point of interest, this point is added in both reference and correction frames.

        #If we press on the reference image
        if Pt[0]<self.Vid.shape[1] and Pt[0]>0 and Pt[1]<self.Vid.shape[0] and Pt[1]>0:
            clicked=False
            for pt in range(len(self.or_positions)):
                dist= math.sqrt((Pt[0]-self.or_positions[pt][0])**2 + (Pt[1]-self.or_positions[pt][1])**2)
                if dist<3*self.Vid_Lecteur.ratio:
                    self.selected=[0,pt, Pt]
                    clicked=True
                    break

            if not clicked:
                self.or_positions.append(Pt)
                self.corr_positions.append(Pt)


        elif Pt[0]<self.Vid.shape[1]*2 and Pt[0]>self.Vid.shape[1]+1 and Pt[1]<self.Vid.shape[0] and Pt[1]>0:
            clicked = False
            for pt in range(len(self.corr_positions)):
                dist= math.sqrt((Pt[0]-self.Vid.shape[1]-self.corr_positions[pt][0])**2 + (Pt[1]-self.corr_positions[pt][1])**2)
                if dist<3*self.Vid_Lecteur.ratio:
                    clicked=True
                    self.selected=[1,pt,Pt]
                    break

            if not clicked:
                self.selected = None

        self.modif_image()

    def moved_can(self, Pt, Shift):
        if self.selected!=None:
            if self.selected[0]==0:
                if not Shift:
                    self.or_positions[self.selected[1]]=Pt
                else:
                    Pt=list(Pt)
                    self.or_positions[self.selected[1]]=list(self.or_positions[self.selected[1]])
                    if abs(self.selected[2][0]-Pt[0])>abs(self.selected[2][1]-Pt[1]):
                        self.or_positions[self.selected[1]][0] = Pt[0]
                        self.or_positions[self.selected[1]][1] = self.selected[2][1]
                    else:
                        self.or_positions[self.selected[1]][1] = Pt[1]
                        self.or_positions[self.selected[1]][0] = self.selected[2][0]
            else:
                if not Shift:
                    self.corr_positions[self.selected[1]]=[Pt[0]-self.Vid.shape[1],Pt[1]]
                else:
                    Pt=list(Pt)
                    self.corr_positions[self.selected[1]]=list(self.corr_positions[self.selected[1]])
                    if abs(self.selected[2][0]-Pt[0])>abs(self.selected[2][1]-Pt[1]):
                        self.corr_positions[self.selected[1]][0] = Pt[0]-self.Vid.shape[1]
                        self.corr_positions[self.selected[1]][1] = self.selected[2][1]
                    else:
                        self.corr_positions[self.selected[1]][1] = Pt[1]
                        self.corr_positions[self.selected[1]][0] = self.selected[2][0]-self.Vid.shape[1]
            self.modif_image()

    def released_can(self, Pt):
        pass

