from tkinter import *
import os
import cv2
import PIL.Image, PIL.ImageTk
import numpy as np
import math
import random
from AnimalTA.E_Post_tracking.b_Analyses import Function_extend_elements
from AnimalTA.A_General_tools import Class_change_vid_menu, Function_draw_mask as Dr, Video_loader as VL, UserMessages, \
    User_help, Color_settings
from copy import deepcopy

class Mask(Frame):
    """In this Frame, the user will have the possibility to indicate the arenas in which the targets can be found. It will later work as a mask and facilitate target's identification."""
    def __init__(self, parent, boss, main_frame, proj_pos, Video_file,portion=False, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.proj_pos=proj_pos
        self.main_frame=main_frame
        self.boss=boss
        self.portion=portion
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.Rpressed=False
        self.Fpressed = False
        self.Ctrlpressed = False
        self.Shiftpressed = False
        self.Which_ar = None


        if self.portion:#If we are just changing the arenas for a part of the video (during corrections)
            Grid.columnconfigure(self.parent, 0, weight=1)
            Grid.rowconfigure(self.parent, 0, weight=1)
            self.parent.geometry("1200x750")

        #Import messages
        self.Vid = Video_file
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        #Relative to size of the image
        self.zoom_sq=[0,0,self.Vid.shape[1],self.Vid.shape[0]]
        self.zoom_strength = 0.3


        self.liste_points=[]
        ##This is a list of all the Arenas, the structure is the following:
        #[
        # [[Xs], [Ys], (R, G, B), Shape], --> Arena 1, Xs and Ys are the coordinates of the points used to define the arenas. Shape can be: ellipse, rectangle or polygon
        # [[Xs], [Ys], (R, G, B), Shape], --> Arena 2
        # ...]

        self.Pt_select=[]
        #Indicate which is the selected point. Structure:
        #[ArenaID, PtID] with IDs being integers from 0

        #If a background was defined, the user will draw over it.
        if self.Vid.Back[0]==1:
            self.background=self.Vid.Back[1]

        else:#If not, we take the first frame as image (after cropping).
            Which_part = 0
            if self.Vid.Cropped[0]:
                if len(self.Vid.Fusion) > 1:  # Si on a plus d'une video
                    Which_part = [index for index, Fu_inf in enumerate(self.Vid.Fusion) if Fu_inf[0] <= self.Vid.Cropped[1][0]][-1]

            self.capture = VL.Video_Loader(self.Vid, self.Vid.Fusion[Which_part][1])
            self.background = self.capture[self.Vid.Cropped[1][0] - self.Vid.Fusion[Which_part][0]]
            del self.capture

        self.image_to_show=np.copy(self.background)

        self.Shape_ar = IntVar(self)# When opening the window, which kind of shape should be first selected?
        try:
            self.Shape_ar.set(self.main_frame.mask_shape)#If there was info about that, we take the saved kind of shape
        except:
            self.Shape_ar.set(1)#Else, we put the first one (ellipse)
        self.view_mask = False

        # Video name and option menu to jump from one video to the other:
        if not self.portion:
            self.choice_menu = Class_change_vid_menu.Change_Vid_Menu(self, self.main_frame, self.Vid, "mask")
            self.choice_menu.grid(row=0, column=0)

        Grid.rowconfigure(self, 0, weight=1)


        #Canvas to show img
        self.canvas_img = Canvas(self, bd=0, highlightthickness=0, **Color_settings.My_colors.Frame_Base)
        self.canvas_img.grid(row=1, column=0, rowspan=2, sticky="nsew")
        self.canvas_img.bind("<Control-1>", self.Zoom_in)
        self.canvas_img.bind("<Control-3>", self.Zoom_out)
        self.canvas_img.bind('<Return>', self.New_ar_mask)
        self.canvas_img.bind("<Button-1>", self.callback_mask)
        self.canvas_img.bind("<Button-3>", self.Right_click)
        self.canvas_img.bind("<B3-Motion>", self.move_pt_mask)
        self.canvas_img.bind("<B1-Motion>", self.move_pt_mask)
        self.canvas_img.bind("<Key>", self.keypress)
        self.canvas_img.bind("<KeyRelease>", self.keyrelease)
        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=1)  ########NEW
        self.ratio=1
        self.final_width=750
        self.Size = self.Vid.shape


        #Help user and parameters
        self.HW= User_help.Help_win(self.parent, default_message=self.Messages["Mask10"],
                                    shortcuts={self.Messages["Short_left_click"]:self.Messages["Short_left_click_Ar"],
                                               self.Messages["Short_Return"]:self.Messages["Short_Return_Ar"],
                                               self.Messages["Short_right_click"]:self.Messages["Short_right_click_Ar"],
                                               self.Messages["Short_del"]:self.Messages["Short_del_Ar"],
                                               self.Messages["Short_left_drag"]:self.Messages["Short_left_drag_Ar"],
                                               self.Messages["Short_Shift_left_drag"]:self.Messages["Short_Shift_left_drag_Ar"],
                                               self.Messages["Short_Shift_right_drag"]:self.Messages["Short_Shift_right_drag_Ar"],
                                               self.Messages["Short_Shift_right_drag"]: self.Messages["Short_Shift_right_drag_Ar"],
                                               self.Messages["Short_R_right_drag"]: self.Messages["Short_R_right_drag_Ar"],
                                               self.Messages["Short_Ctrl_click"]: self.Messages["Short_Ctrl_click_G"],
                                               self.Messages["Short_Ctrl_Rclick"]: self.Messages["Short_Ctrl_Rclick_G"],})
        self.HW.grid(row=0, column=1,sticky="nsew")

        ##Parameters
        self.canvas_User_params = Canvas(self.parent, width=200, height=0, bd=0, highlightthickness=0, **Color_settings.My_colors.Frame_Base)
        self.canvas_User_params.grid(row=1,column=1, sticky="nsew")

        #Widgets
        self.bouton_efface = Button(self.canvas_User_params, text=self.Messages["Mask2"], command=self.remove_ind, **Color_settings.My_colors.Button_Base)

        self.bouton_add_mask_ar = Button(self.canvas_User_params, text=self.Messages["Mask7"], command=self.New_ar_mask, **Color_settings.My_colors.Button_Base)
        self.bouton_remove_mask_ar = Button(self.canvas_User_params, text=self.Messages["Mask8"],  command=self.Remove_ar_mask, **Color_settings.My_colors.Button_Base)
        self.bouton_remove_mask_one_ar = Button(self.canvas_User_params, text=self.Messages["Mask9"], command=self.suppress_one_ar_mask, **Color_settings.My_colors.Button_Base)

        self.bouton_validate = Button(self.canvas_User_params, text=self.Messages["Validate"], command=self.validate, **Color_settings.My_colors.Button_Base)
        self.bouton_validate.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.B_Validate_NContinue=Button(self.canvas_User_params, text=self.Messages["Validate_NC"], **Color_settings.My_colors.Button_Base, command=lambda: self.validate(follow=True))
        self.B_Validate_NContinue.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.NB_Arenas=StringVar(value="0")
        Label_nb_Arenas=Label(self.canvas_User_params, text=self.Messages["Mask11"], **Color_settings.My_colors.Label_Base)
        nb_Arenas = Label(self.canvas_User_params, textvariable=self.NB_Arenas, **Color_settings.My_colors.Label_Base)

        self.Label_shapes = Label(self.canvas_User_params, text=self.Messages["Mask3"], **Color_settings.My_colors.Label_Base)

        self.shape1 = Radiobutton(self.canvas_User_params, text=self.Messages["Mask4"],indicatoron=0, width=25, variable=self.Shape_ar, value=1,
                                  command=lambda : self.Change_SM_val(self.Shape_ar,1), **Color_settings.My_colors.Radiobutton_Base)

        self.shape2 = Radiobutton(self.canvas_User_params, text=self.Messages["Mask5"],indicatoron=0, width=25,
                                  variable=self.Shape_ar, value=2, command=lambda : self.Change_SM_val(self.Shape_ar,2), **Color_settings.My_colors.Radiobutton_Base)

        self.shape3 = Radiobutton(self.canvas_User_params, text=self.Messages["Mask6"],indicatoron=0, width=25,
                                  variable=self.Shape_ar, value=3, command=lambda : self.Change_SM_val(self.Shape_ar,3), **Color_settings.My_colors.Radiobutton_Base)



        #Grids
        Label_nb_Arenas.grid(row=0, column=0, sticky="e")
        nb_Arenas.grid(row=0, column=1, sticky="w")

        self.Label_shapes.grid(row=1, columnspan=2)
        self.shape1.grid(row=2, columnspan=2)
        self.shape2.grid(row=3, columnspan=2)
        self.shape3.grid(row=4, columnspan=2)

        self.bouton_add_mask_ar.grid(row=5, column=0)
        self.bouton_remove_mask_one_ar.grid(row=5, column=1)
        self.bouton_remove_mask_ar.grid(row=6, columnspan=2)
        self.bouton_efface.grid(row=7, columnspan=2)
        self.bouton_validate.grid(row=8, columnspan=2,sticky="nsew")
        if not self.portion:
            self.B_Validate_NContinue.grid(row=9,columnspan=2, sticky="ewsn")

        self.canvas_User_params.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9), weight=3, uniform="row")

        self.canvas_img.update()
        self.final_width = self.canvas_img.winfo_width()
        self.ratio = self.Size[1] / self.final_width
        self.canvas_img.focus_force()

        if not self.Vid.Mask[0]:#If there were no arenas defined yet
            self.liste_points = [[[], [], (0, 0, 0), 0, True]]
        else:
            self.liste_points = self.Vid.Mask[1] # else, we draw the existing shapes
            self.dessiner_Formes()
            if len(self.liste_points)>0:#If there were no shapes (i.e. user went in this option but did not change anything)
                self.Which_ar=len(self.liste_points)-1
            else:
                self.liste_points = [[[], [], (0, 0, 0), 0, True]]

        self.canvas_img.bind("<Configure>", self.afficher)
        self.afficher()

    def Zoom_in(self, event):
        #Zoom in in the image
        self.new_zoom_sq=[0,0,0,0]
        PX=event.x/((self.zoom_sq[2]-self.zoom_sq[0])/self.ratio)
        PY=event.y/((self.zoom_sq[3]-self.zoom_sq[1])/self.ratio)

        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]
        ZWX = (self.zoom_sq[2]-self.zoom_sq[0])*(1-self.zoom_strength)
        ZWY = (self.zoom_sq[3]-self.zoom_sq[1])*(1-self.zoom_strength)

        if ZWX>100:
            self.new_zoom_sq[0] = int(event.x-PX*ZWX)
            self.new_zoom_sq[2] = int(event.x+(1-PX)*ZWX)
            self.new_zoom_sq[1] = int(event.y - PY*ZWY)
            self.new_zoom_sq[3] = int(event.y + (1-PY)*ZWY)

            self.ratio=ZWX/self.final_width
            self.zoom_sq=self.new_zoom_sq
            self.zooming = True
            self.dessiner_Formes()
            self.afficher()

    def Zoom_out(self, event):
        #Zoom out from the image
        self.new_zoom_sq = [0, 0, 0, 0]
        PX = event.x / ((self.zoom_sq[2] - self.zoom_sq[0]) / self.ratio)
        PY = event.y / ((self.zoom_sq[3] - self.zoom_sq[1]) / self.ratio)

        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]

        ZWX = (self.zoom_sq[2] - self.zoom_sq[0]) * (1 + self.zoom_strength)
        ZWY = (self.zoom_sq[3] - self.zoom_sq[1]) * (1 + self.zoom_strength)


        if ZWX<self.Size[1] and ZWY<self.Size[0]:
            if int(event.x - PX * ZWX)>=0 and int(event.x + (1 - PX) * ZWX)<=self.Size[1]:
                self.new_zoom_sq[0] = int(event.x - PX * ZWX)
                self.new_zoom_sq[2] = int(event.x + (1 - PX) * ZWX)
            elif int(event.x + (1 - PX) * ZWX)>self.Size[1]:
                self.new_zoom_sq[0] = int(self.Size[1]-ZWX)
                self.new_zoom_sq[2] = int(self.Size[1])
            elif int(event.x - PX * ZWX)<0:
                self.new_zoom_sq[0] = 0
                self.new_zoom_sq[2] = int(ZWX)

            if int(event.y - PY * ZWY)>=0 and int(event.y + (1 - PY) * ZWY)<=self.Size[0]:
                self.new_zoom_sq[1] = int(event.y - PY * ZWY)
                self.new_zoom_sq[3] = self.new_zoom_sq[1] + int(ZWY)

            elif int(event.y + (1 - PY) * ZWY)>self.Size[0]:
                self.new_zoom_sq[1] = int(self.Size[0]-ZWY)
                self.new_zoom_sq[3] = int(self.Size[0])
            elif int(event.y - PY * ZWY)<0:
                self.new_zoom_sq[1] = 0
                self.new_zoom_sq[3] = int(ZWY)
            self.ratio = ZWX / self.final_width


        else:
            self.new_zoom_sq=[0,0,self.Vid.shape[1],self.Vid.shape[0]]
            self.ratio=self.Size[1]/self.final_width

        self.zoom_sq = self.new_zoom_sq
        self.zooming = False
        self.dessiner_Formes()
        self.afficher()

    def validate(self, follow=False):
        #Save the information about arenas defined and delete this frame. If follow=True, a new frame with the next video is opened
        self.Vid.Mask[0] = True# The mask is done
        if len(self.liste_points)>0 and not len(self.liste_points[len(self.liste_points)-1][0])>1:
            self.liste_points.pop()# We remove the last point (not associated with coordinates yet)

        if not self.portion:
            self.Vid.Mask[1] = self.liste_points
            #We count the number of Arenas defined
            mask = Dr.draw_mask(self.Vid)
            Arenas, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if len(Arenas) < len(self.Vid.Track[1][6]):#We update the number of arenas to be tracked
                self.Vid.Track[1][6]=self.Vid.Track[1][6][0:(len(Arenas))]
            elif len(Arenas) > len(self.Vid.Track[1][6]):
                self.Vid.Track[1][6] = self.Vid.Track[1][6]+ [self.Vid.Track[1][6][-1]]*(len(Arenas) - len(self.Vid.Track[1][6]))
            self.Vid.draw_entrance()#This is for next update

        if self.portion:
            self.boss.PortionWin.grab_set()

        if follow and self.Vid != self.main_frame.liste_of_videos[-1]:
            for i in range(len(self.main_frame.liste_of_videos)):
                if self.main_frame.liste_of_videos[i]==self.Vid:
                    self.choice_menu.change_vid(self.main_frame.liste_of_videos[i+1].User_Name)
                    break
        else:
            self.End_of_window()

        self.main_frame.mask_shape=self.Shape_ar.get()

    def End_of_window(self):
        #Close the Frame properly
        self.unbind_all("<Button-1>")
        self.grab_release()
        self.canvas_User_params.grid_forget()
        self.canvas_User_params.destroy()
        self.HW.grid_forget()
        self.HW.destroy()
        if not self.portion:
            self.main_frame.return_main()
        if self.portion:
            self.parent.destroy()

    def suppress_one_ar_mask(self):
        #Supress the current arena
        if len(self.Pt_select) > 0 : #If there are no point selected yet, nothing happen
            if len(self.liste_points)<2:#If there was only one arena, the list of points is emptied
                self.liste_points = [[[], [], (0,0,0) ,0, True]]
                self.Which_ar=None
            else:#Else, only the current arena is removed
                self.liste_points[self.Pt_select[0]]=[[],[],(0,0,0),0, True]

            self.Pt_select=[]
            self.dessiner_Formes()#We show the arenas
            self.afficher()

    def Remove_ar_mask(self):
        #Remove all the arenas
        self.liste_points = [[[], [], (0,0,0),0, True]]
        self.image_to_show = self.background
        self.Pt_select=[]
        self.afficher()
        self.Which_ar = None

    def keypress(self, event):
        #Remove the selected point
        if event.keysym == "Delete" and len(self.Pt_select) > 0:
            del self.liste_points[self.Pt_select[0]][0][self.Pt_select[1]]
            del self.liste_points[self.Pt_select[0]][1][self.Pt_select[1]]
            self.Pt_select=[]
            self.dessiner_Formes()#Show the result
            self.afficher()
        elif event.keysym == "r" or event.keysym == "R":
            self.Rpressed=True
        elif event.keysym == "f" or event.keysym == "F":
            self.Fpressed=True
        elif event.keysym == "Control_L" or event.keysym == "Control_R":
            self.Ctrlpressed=True
        elif event.keysym == "Shift_L" or event.keysym == "Shift_R":
            self.Shiftpressed=True


    def keyrelease(self, event):
        self.Rpressed = False
        self.Fpressed = False
        self.Ctrlpressed = False
        self.Shiftpressed = False


    def Rotate_Ar(self, event):
        event.x = int(event.x * self.ratio + self.zoom_sq[0])
        event.y = int(event.y * self.ratio + self.zoom_sq[1])

        angle = math.atan2(event.y - self.selected_shapes[0][1], event.x - self.selected_shapes[0][0])
        angle=angle*180/math.pi


        dist=(event.x - self.selected_shapes[0][0])

        points_list=[]
        for sh in range(len(self.selected_shapes[1])):
            for pt in range(len(self.selected_shapes[2][sh][0])):
                points_list.append([self.selected_shapes[2][sh][0][pt],self.selected_shapes[2][sh][1][pt]])

        points_list=np.array(points_list)
        pts_norm = points_list - self.selected_shapes[3]

        if self.Rpressed:
            coordinates = pts_norm
            Ptxs, Ptys = coordinates[:, 0], coordinates[:, 1]
            thetas, rhos = Function_extend_elements.cart2pol(Ptxs, Ptys)
            thetas = np.rad2deg(thetas)
            thetas = (thetas + angle) % 360
            thetas = np.deg2rad(thetas)

            Ptxs, Ptys = Function_extend_elements.pol2cart(thetas, rhos)
            pts_norm[:, 0] = Ptxs
            pts_norm[:, 1] = Ptys

        if self.Shiftpressed:
            pts_norm=pts_norm*((((dist/self.ratio))/100)+1)

        if self.Fpressed:
            pts_norm[:, 0] =  pts_norm[:, 0] * -1

        pts_rotated = pts_norm + self.selected_shapes[3]

        count=0
        for sh in range(len(self.selected_shapes[1])):
            for pt in range(len(self.selected_shapes[2][sh][0])):
                self.liste_points[self.selected_shapes[1][sh]][0][pt]=pts_rotated[count][0]
                self.liste_points[self.selected_shapes[1][sh]][1][pt]=pts_rotated[count][1]
                count+=1
        self.dessiner_Formes()  # Show the result
        self.afficher()


    def move_pt_mask(self, event):
        if not self.Ctrlpressed:
            #Move a selected point
            if len(self.Pt_select) > 0:
                self.liste_points[self.Pt_select[0]][0][self.Pt_select[1]]=event.x * self.ratio + self.zoom_sq[0]
                self.liste_points[self.Pt_select[0]][1][self.Pt_select[1]]=event.y * self.ratio + self.zoom_sq[1]
                self.dessiner_Formes()#Show the result
                self.afficher()

            elif len(self.selected_shapes[1]) > 0 and not self.Rpressed and (event.state==264 or event.state==265):
                # Move a shape
                transla = [int((event.x * self.ratio + self.zoom_sq[0]) - self.selected_shapes[0][0]),
                           int((event.y * self.ratio + self.zoom_sq[1]) - self.selected_shapes[0][1])]
                for sh in range(len(self.selected_shapes[1])):
                    for pt in range(len(self.selected_shapes[2][sh][0])):
                        self.liste_points[self.selected_shapes[1][sh]][0][pt] = self.selected_shapes[2][sh][0][pt] + \
                                                                                transla[0]
                        self.liste_points[self.selected_shapes[1][sh]][1][pt] = self.selected_shapes[2][sh][1][pt] + \
                                                                                transla[1]

                self.dessiner_Formes()  # Show the result
                self.afficher()


            elif len(self.selected_shapes[1]) > 0 and (self.Rpressed or self.Shiftpressed or self.Fpressed):
                self.Rotate_Ar(event)


    def New_ar_mask(self, b="_"):
        #Create a new arena (i.e. indicates that the last one is finished)
        if self.Which_ar != None:
            if len(self.liste_points[self.Which_ar][0])<2:#If the current arena was not defined (i.e. user add les than two points)
                self.liste_points[self.Which_ar]=[[],[], self.random_color(),0,True] #We continue on the same, just remove the point if there was one and change the color
            else: #If not, we create a new arena
                self.Which_ar = len(self.liste_points)
                self.liste_points.append([[], [],self.random_color(),self.Shape_ar.get(), True])

        self.Pt_select=[]
        self.dessiner_Formes()
        self.afficher()

    def dessiner_Formes(self):
        #Prepare empty image
        if self.Vid.Back[0] and len(self.Vid.Back[1].shape)==2:
            self.image_to_show = cv2.cvtColor(self.background, cv2.COLOR_GRAY2RGB)
        else:
            self.image_to_show=self.background.copy()

        #Draw the shapes
        for j in range(len(self.liste_points)):
            if self.liste_points[j][3]==1:
                if len(self.liste_points[j][0]) > 1:
                    self.image_to_show, _ = Dr.Draw_elli(self.image_to_show, self.liste_points[j][0], self.liste_points[j][1],self.liste_points[j][2],thick=round(2*self.ratio))

            elif self.liste_points[j][3]==2:
                if len(self.liste_points[j][0])>1:
                    self.image_to_show, _= Dr.Draw_rect(self.image_to_show, self.liste_points[j][0], self.liste_points[j][1],self.liste_points[j][2],thick=round(2*self.ratio))

            elif self.liste_points[j][3]==3:
                if len(self.liste_points[j][0])>1:
                    self.image_to_show, _ = Dr.Draw_Poly(self.image_to_show, self.liste_points[j][0], self.liste_points[j][1],self.liste_points[j][2],thick=round(2*self.ratio))

            for i in range(len(self.liste_points[j][0])):
                if self.liste_points[j][4]:  # If this is filled shape
                    self.image_to_show = cv2.circle(self.image_to_show, (
                    int(self.liste_points[j][0][i]), int(self.liste_points[j][1][i])), max(2,round(5 * self.ratio)),
                                                    self.liste_points[j][2], -1)
                else:  # If this is empty shape
                    self.image_to_show = cv2.line(self.image_to_show,
                        (int(self.liste_points[j][0][i]-round(3 * self.ratio)), int(self.liste_points[j][1][i]-round(3 * self.ratio))),
                        (int(self.liste_points[j][0][i] + round(3 * self.ratio)), int(self.liste_points[j][1][i] + round(3 * self.ratio))),
                        self.liste_points[j][2], round(3 * self.ratio))
                    self.image_to_show = cv2.line(self.image_to_show,
                        (int(self.liste_points[j][0][i]+round(3 * self.ratio)), int(self.liste_points[j][1][i]-round(3 * self.ratio))),
                        (int(self.liste_points[j][0][i] - round(3 * self.ratio)), int(self.liste_points[j][1][i] + round(3 * self.ratio))),
                        self.liste_points[j][2], round(3 * self.ratio))

        if len(self.Pt_select) > 0:#Selected point is highlighted
            if self.liste_points[self.Pt_select[0]][4]:  # If this is filled shape
                self.image_to_show = cv2.circle(self.image_to_show,(int(self.liste_points[self.Pt_select[0]][0][self.Pt_select[1]]), int(self.liste_points[self.Pt_select[0]][1][self.Pt_select[1]])), max(3,round(4*self.ratio)),(0,0,0), round(2*self.ratio))


            else:
                self.image_to_show = cv2.circle(self.image_to_show, (
                int(self.liste_points[self.Pt_select[0]][0][self.Pt_select[1]]),
                int(self.liste_points[self.Pt_select[0]][1][self.Pt_select[1]])), max(3,round(7 * self.ratio)), (255,255,255), -1)

                self.image_to_show = cv2.circle(self.image_to_show, (
                int(self.liste_points[self.Pt_select[0]][0][self.Pt_select[1]]),
                int(self.liste_points[self.Pt_select[0]][1][self.Pt_select[1]])), max(2,round(6 * self.ratio)), (0, 0, 0),
                                                round(2 * self.ratio))

                self.image_to_show = cv2.line(self.image_to_show,
                                              (int(self.liste_points[self.Pt_select[0]][0][self.Pt_select[1]] - round(3 * self.ratio)),
                                               int(self.liste_points[self.Pt_select[0]][1][self.Pt_select[1]] - round(3 * self.ratio))),
                                              (int(self.liste_points[self.Pt_select[0]][0][self.Pt_select[1]] + round(3 * self.ratio)),
                                               int(self.liste_points[self.Pt_select[0]][1][self.Pt_select[1]] + round(3 * self.ratio))),
                                              self.liste_points[self.Pt_select[0]][2], round(3 * self.ratio))

                self.image_to_show = cv2.line(self.image_to_show,
                                              (int(self.liste_points[self.Pt_select[0]][0][self.Pt_select[1]] + round(3 * self.ratio)),
                                               int(self.liste_points[self.Pt_select[0]][1][self.Pt_select[1]] - round(3 * self.ratio))),
                                              (int(self.liste_points[self.Pt_select[0]][0][self.Pt_select[1]] - round(3 * self.ratio)),
                                               int(self.liste_points[self.Pt_select[0]][1][self.Pt_select[1]] + round(3 * self.ratio))),
                                              self.liste_points[self.Pt_select[0]][2], round(3 * self.ratio))

    def Right_click(self, event):
        self.callback_mask(event=event, add=False)

    def callback_mask(self, event, add=True):
        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]
        self.selected_shapes = [[event.x,event.y],[],[],[]]

        if self.Which_ar == None:#If it is the first point created
            self.Which_ar = 0
            self.liste_points[self.Which_ar][2]=self.random_color()
            self.liste_points[self.Which_ar][3] = self.Shape_ar.get()
            self.liste_points[self.Which_ar][4] = add

        else:# We check if the user clicked on an existing point
            self.Pt_select=[]
            for j in range(len(self.liste_points)):
                if len(self.Pt_select)>0:
                    break
                for i in range(len(self.liste_points[j][0])):
                    if math.sqrt((self.liste_points[j][0][i]-event.x)**2 + (self.liste_points[j][1][i]-event.y)**2)<7*self.ratio:
                        self.Pt_select=(j,i)#Selected point is part of Arena j and is point i
                        self.Which_ar=j
                        self.Shape_ar.set(self.liste_points[j][3])
                        break

            if len(self.Pt_select) < 1: #And we are not clicking on an existing arena
                empty = np.zeros([self.image_to_show.shape[0], self.image_to_show.shape[1], 1], np.uint8)
                empty2=self.draw_binaries(empty, thick=int(self.ratio * 7))

                if empty2[int(event.y),int(event.x)]==255:
                    empty = np.zeros([self.image_to_show.shape[0], self.image_to_show.shape[1], 1], np.uint8)
                    empty = self.draw_binaries(empty, thick=-1)
                    empty = self.draw_binaries(empty, thick=int(self.ratio * 7))
                    cnts,_ = cv2.findContours(empty, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

                    main_cnt_found=False
                    cnt_cnt=0

                    for cnt in cnts:
                        cnt_cnt+=1
                        res=cv2.pointPolygonTest(cnt, (int(event.x),int(event.y)), False)
                        if res>=0:
                            main_cnt_found=True
                            M = cv2.moments(cnt)
                            Cnt_center=[int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])]

                            for shape in range(len(self.liste_points)):
                                if len(self.liste_points[shape][0])>0:
                                    Shape_center = (int(np.mean(self.liste_points[shape][0])),int(np.mean(self.liste_points[shape][1])))
                                    res2 = cv2.pointPolygonTest(cnt, Shape_center, False)
                                    if res2>=0:
                                        self.selected_shapes[1].append(shape)
                                        self.selected_shapes[2].append(deepcopy(self.liste_points[shape]))


                        if main_cnt_found:
                            self.selected_shapes[3] = Cnt_center
                            break

                if self.Shiftpressed and len(self.selected_shapes[1])>0 and event.num==1:
                    new_selection=[]
                    for sh in self.selected_shapes[1]:
                        self.liste_points.append(deepcopy(self.liste_points[sh]))
                        self.liste_points[-1][2]=self.random_color()
                        new_selection.append(len(self.liste_points)-1)
                    self.selected_shapes[1]=new_selection

        #If we did not press on an existing point or shape, we add a new one
        if len(self.Pt_select)<1 and len(self.selected_shapes[1])<1 and not self.Shiftpressed and not self.Rpressed and not self.Ctrlpressed:
            self.liste_points[self.Which_ar][0].append(event.x)
            self.liste_points[self.Which_ar][1].append(event.y)
            self.Pt_select=(self.Which_ar,len(self.liste_points[self.Which_ar][0])-1)
            if len(self.liste_points[self.Which_ar][0])<2:
                self.liste_points[self.Which_ar][3]=self.Shape_ar.get()
            if len(self.liste_points[self.Which_ar][0])==1:
                self.liste_points[self.Which_ar][4] = add

        self.dessiner_Formes()#Show the result
        self.afficher()

    def Change_SM_val(self, var, val):
        #Change the sahpe of an existing shape
        var.set(val)
        if len(self.Pt_select)>0:
            self.liste_points[self.Pt_select[0]][3]=val
        elif self.Which_ar!=None:
            self.liste_points[self.Which_ar][3] = val

        self.dessiner_Formes()
        self.afficher()

    def afficher(self, *args):
        #Show the image
        self.TMP_image_to_show=np.copy(self.image_to_show)
        best_ratio = max(self.Size[1] / (self.canvas_img.winfo_width()),
                         self.Size[0] / (self.canvas_img.winfo_height()))
        prev_final_width=self.final_width
        self.final_width=int(self.Size[1]/best_ratio)
        self.ratio=self.ratio*(prev_final_width/self.final_width)

        self.image_to_show2 = self.TMP_image_to_show[self.zoom_sq[1]:self.zoom_sq[3], self.zoom_sq[0]:self.zoom_sq[2]]
        self.TMP_image_to_show2 = cv2.resize(self.image_to_show2, (self.final_width, int(self.final_width * (self.Size[0] / self.Size[1]))))
        self.image_to_show3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP_image_to_show2))
        self.canvas_img.create_image(0, 0, image=self.image_to_show3, anchor=NW)
        self.canvas_img.config(width=self.final_width, height=int(self.final_width * (self.Size[0] / self.Size[1])))

        empty=np.zeros([self.image_to_show.shape[0],self.image_to_show.shape[1],1],np.uint8)
        self.draw_binaries(empty)

    def draw_binaries(self, img_or, thick=-1, shapes=-1):
        #Draw a binary image (the mask)
        img=np.copy(img_or)

        if img.shape[2]>1:
            img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        if shapes==-1:
            list_to_draw=range(len(self.liste_points))
        else:
            list_to_draw=shapes


        for col in [255, 0]:
            for i in list_to_draw:
                if (col==255 and self.liste_points[i][4]) or (col==0 and not self.liste_points[i][4]):
                    if len(self.liste_points[i][0]) > 0:
                        if self.liste_points[i][3] == 1:
                            img, _ = Dr.Draw_elli(img, self.liste_points[i][0],
                                                                 self.liste_points[i][1], col, thick)

                        elif self.liste_points[i][3] == 2 and len(self.liste_points[i][0]) > 1:
                            img, _ = Dr.Draw_rect(img, self.liste_points[i][0],
                                                                 self.liste_points[i][1], col, thick)

                        elif self.liste_points[i][3] == 3 and len(self.liste_points[i][0]) > 1:
                            img, _ = Dr.Draw_Poly(img, self.liste_points[i][0],
                                                                 self.liste_points[i][1], col, thick)

        if np.any(img[:,:]>0):
            Arenas, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            self.NB_Arenas.set(len(Arenas))
        else:
            self.NB_Arenas.set(1)
        return(img)

    def remove_ind(self):
        #Show the binary image if it wasn't visible, else return to normal view
        if not self.view_mask:
            self.New_ar_mask()
            self.image_to_show = np.zeros_like(self.background)
            self.image_to_show =self.draw_binaries(self.image_to_show)

            self.view_mask=True
            self.afficher()
        else:
            if self.background.shape[2]==1:
                self.image_to_show = cv2.cvtColor(self.background, cv2.COLOR_GRAY2RGB)
            self.view_mask = False
            self.dessiner_Formes()
            self.afficher()

    def random_color(self):
        #Choose a random color to be assigned to the shape
        levels = range(32, 256, 32)
        levels = str(tuple(random.choice(levels) for _ in range(3)))
        return (tuple(int(s) for s in levels.strip("()").split(",")))


'''
root = Tk()
root.geometry("+100+100")
Video_file=Class_Video.Video(File_name="D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01.avi")
Video_file.Back[0]=True
im=cv2.imread("D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01_background.bmp")
im=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
Video_file.Back[1]=im
interface = Mask(parent=root, main_frame=root,proj_pos=1, boss=None, Video_file=Video_file)
root.mainloop()
'''