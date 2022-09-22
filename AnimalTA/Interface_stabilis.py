from tkinter import *
import cv2
from AnimalTA import Class_stabilise, UserMessages, Class_Lecteur, User_help
import math
import numpy as np

class Stabilise(Frame):
    """In this Frame, the user can choose which points of interest will be used to stabilise the video (correction for optical flow)"""
    def __init__(self, parent, boss, main_frame, Video_file, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.main_frame=main_frame
        self.boss=boss
        self.parent=parent
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.Vid = Video_file
        self.first=True

        #Import messages
        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        # Name of the vieo and optionmenu to jump from one video to another
        self.canvas_video_name = Canvas(self, bd=2, highlightthickness=1, relief='flat')
        self.canvas_video_name.grid(row=0, column=0, sticky="ew")

        self.dict_Names = {Video.Name: Video for Video in self.main_frame.liste_of_videos if Video.Stab[0]}

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


        # Video reader
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=10)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

        # Information panel for user
        self.HW=User_help.Help_win(self.parent, default_message=self.Messages["Stab1"], width=250)
        self.HW.grid(row=0, column=1,sticky="nsew")

        # Validate
        self.canvas_validate = Canvas(self.parent, bd=2, highlightthickness=1, relief='ridge', background="black")
        self.canvas_validate.grid(row=1, column=1, sticky="sew")
        Grid.columnconfigure(self.canvas_validate, 0, weight=1)
        self.B_Validate=Button(self.canvas_validate, text=self.Messages["Validate"],bg="#6AED35", command=self.End_of_window)
        self.B_Validate.grid(row=1,column=0, sticky="new")

        # Look for all points of interest
        self.B_redo_pts=Button(self.canvas_validate, text=self.Messages["Stab2"], command=self.redo_opt_pts)
        self.B_redo_pts.grid(row=0,column=0, sticky="new")

    def change_vid(self, vid):
        #Close this frame and open another one for another video
        for V in self.main_frame.list_projects:
            if V.Video==self.dict_Names[vid] and V.Video!=self.Vid:
                self.End_of_window()
                V.check_stab()
                break

    def modif_image(self, img=[], aff=False, **kwargs):
        #Draw the points of interest on the top of the image. Also combine the first image, the original image at the current frame and the stabilised result.
        if len(img) <= 10:
            new_img=np.copy(self.last_empty)
        else:
            self.last_empty = img
            new_img = np.copy(img)

        new_img = Class_stabilise.find_best_position(Vid=self.Vid, Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=True, scale=self.Vid_Lecteur.ratio)

        if self.Scrollbar.active_pos>self.Scrollbar.crop_end or self.Scrollbar.active_pos<self.Scrollbar.crop_beg:
            new_img = cv2.addWeighted(new_img, 1, new_img, 0, 1)

        if self.first:
            self.Vid_Lecteur.Size=(new_img.shape[0],new_img.shape[1])
            self.Vid_Lecteur.zoom_sq = [0, 0, new_img.shape[1], new_img.shape[0]]

        self.Vid_Lecteur.afficher_img(new_img)
        self.first = False

    def End_of_window(self):
        #Properly close tthis Frame
        self.Vid_Lecteur.proper_close()
        self.unbind_all("<Button-1>")
        self.boss.update()
        self.grab_release()
        self.canvas_validate.grid_forget()
        self.canvas_validate.destroy()
        self.HW.grid_forget()
        self.HW.destroy()
        self.main_frame.return_main()

    def redo_opt_pts(self):
        #Look for all points of interest
        Class_stabilise.find_pts(self.Vid, self.Vid_Lecteur.Prem_image_to_show)
        self.modif_image()

    def pressed_can(self, Pt, Shift):
        #If the user click on the image, we check if it was over a point of interest. If it is the case, the point of interest is removed.
        for pt in range(len(self.Vid.Stab[1])):
            dist=math.sqrt((self.Vid.Stab[1][pt][0][0]-Pt[0])**2 + (self.Vid.Stab[1][pt][0][1]-Pt[1])**2)
            if dist<10:
                self.Vid.Stab[1]=np.delete(self.Vid.Stab[1], pt, axis=0)
                break
        self.modif_image()

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
