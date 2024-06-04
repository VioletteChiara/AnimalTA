from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
import numpy as np
import math
import os
from AnimalTA.A_General_tools import Class_change_vid_menu, Video_loader as VL, UserMessages, User_help, Color_settings, Class_Lecteur, Class_stabilise


class Scale(Frame):
    """This Frame allows the user  to define a scale by selecting two points in the video and indicating the distance between them IRL"""
    def __init__(self, parent, boss, main_frame, Video_file, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base)
        self.parent=parent
        self.boss=boss
        self.main_frame=main_frame
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.Vid = Video_file
        self.first=True

        #Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        #Open video and take the first frame (after cropping)
        Which_part = 0
        if self.Vid.Cropped[0]:
            if len(self.Vid.Fusion) > 1:  # Si on a plus d'une video
                Which_part = [index for index, Fu_inf in enumerate(self.Vid.Fusion) if Fu_inf[0] <= self.Vid.Cropped[1][0]][-1]

        self.Pt_select=None
        self.dist=0

        self.Mem_size="NA"
        self.Mem_ratio="NA"
        self.ratio_val=StringVar()#Value calculated from the informations gave by user
        self.ratio_val.set("NA")
        self.ratio_text=StringVar()#Units of the ratio
        self.ratio_text.set("px/?")


        # Name of the video and optionlist to change the current video:
        self.choice_menu= Class_change_vid_menu.Change_Vid_Menu(self, self.main_frame, self.Vid, "scale")
        self.choice_menu.grid(row=0,column=0)

        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, show_whole_frame=True)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Scrollbar=self.Vid_Lecteur.Scrollbar
        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=100)

        #Help user and parameters
        self.HW= User_help.Help_win(self.parent, default_message=self.Messages["Scale2"],  width=250,
                                    shortcuts = {self.Messages["Short_Space"]: self.Messages["Short_Space_G"],
                                                 self.Messages["Short_Ctrl_click"]: self.Messages["Short_Ctrl_click_G"],
                                                 self.Messages["Short_Ctrl_Rclick"]: self.Messages["Short_Ctrl_Rclick_G"],
                                                 self.Messages["Short_Ctrl_click_drag"]: self.Messages["Short_Ctrl_click_drag_G"],
                                                 self.Messages["Short_RArrow"]: self.Messages["Short_RArrow_G"],
                                                 self.Messages["Short_LArrow"]: self.Messages["Short_LArrow_G"]})

        self.HW.grid(row=0, column=1,sticky="nsew")

        #Options
        self.canvas_bt_global=Canvas(self.parent, height=10, bd=0, highlightthickness=0, **Color_settings.My_colors.Frame_Base)
        self.canvas_bt_global.grid(row=1,column=1, sticky="nsew")

        self.UI_Size_label = Label(self.canvas_bt_global,text=self.Messages["Scale3"], **Color_settings.My_colors.Label_Base)
        self.UI_Size_label.grid(row=2,column=0)
        self.UI_Size=Entry(self.canvas_bt_global, **Color_settings.My_colors.Entry_Base)
        self.regUI_Size = self.register(self.UI_Size_update)
        self.UI_Size.config(validate="focusout", validatecommand=(self.regUI_Size,"%P"))
        self.UI_Size.grid(row=2,column=1)

        self.Check_units=Listbox(self.canvas_bt_global, exportselection=0, **Color_settings.My_colors.ListBox)
        self.Check_units.config(height=3)
        self.Check_units.insert(1, "m")
        self.Check_units.insert(2, "cm")
        self.Check_units.insert(3, "mm")
        self.Check_units.grid(row=2,column=2)
        self.Check_units.bind('<<ListboxSelect>>', self.update_ui)

        self.UI_ratio_label = Label(self.canvas_bt_global,text=self.Messages["Scale7"], **Color_settings.My_colors.Label_Base)
        self.UI_ratio_label.grid(row=4,column=0)

        self.ratio_val_ent = Entry(self.canvas_bt_global,textvariable=self.ratio_val, **Color_settings.My_colors.Entry_Base)
        self.ratio_val_ent.grid(row=4,column=1)
        self.regUI_ratio = self.register(self.UI_Ratio_update)
        self.ratio_val_ent.config(validate="focusout", validatecommand=(self.regUI_ratio,"%P"))

        self.ratio_post_label = Label(self.canvas_bt_global,textvariable=self.ratio_text, **Color_settings.My_colors.Label_Base)
        self.ratio_post_label.grid(row=4,column=2)

        #Validate once the scale is defined
        bouton_validate = Button(self.canvas_bt_global, text=self.Messages["Validate"], command=self.validate, **Color_settings.My_colors.Button_Base)
        bouton_validate.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        bouton_validate.grid(row=6, column=0, columnspan=3,sticky="nsew")

        B_Validate_NContinue=Button(self.canvas_bt_global, text=self.Messages["Validate_NC"], command=lambda: self.validate(follow=True), **Color_settings.My_colors.Button_Base)
        B_Validate_NContinue.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        B_Validate_NContinue.grid(row=7,column=0, columnspan=3,sticky="nsew")


        #Parameters to show the image/calculate image reduction and canvas' size
        self.liste_points = []

        #If the sacle was already defined, we load previous parameters
        self.UI_Size.insert(0, "NA")

        if self.Vid.Scale[0]!=1:
            self.Mem_ratio=self.Vid.Scale[0]
            self.UI_Ratio_update(self.Mem_ratio)
            self.Check_units.select_set(["m", "cm", "mm"].index(self.Vid.Scale[1]))
            self.unit = True#True if a unit has already been selected
            self.update_ui()
        else:
            self.unit = False

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()


    def update_ui(self,event=None):
        #Update the label indicating the units
        self.unit=True
        list_item=self.Check_units.curselection()
        if len(list_item)>0:
            self.ratio_text.set("px/{}".format(["m","cm","mm"][list_item[0]]))

    def UI_Ratio_update(self, new_val):
        # Recalculates and updates the ratio value
        if new_val == "":
            self.ratio_val_ent.delete(0, END)
            self.ratio_val_ent.insert(0, self.Mem_size)
            return False
        else:
            try:
                float(new_val)
                self.Mem_ratio = float(new_val)
                new_size=(round(float(self.dist) / float(self.Mem_ratio), 2))
                self.UI_Size.delete(0, END)
                self.UI_Size.insert(0, new_size)
                self.Mem_size = new_size
                self.modif_image()
                return True
            except:
                self.ratio_val_ent.delete(0, END)
                self.ratio_val_ent.insert(0, self.Mem_ratio)
                return False


    def UI_Size_update(self, new_val):
        #Recalculates and updates the ratio value
        if new_val=="":
            self.UI_Size.delete(0, END)
            self.UI_Size.insert(0, self.Mem_size)
            return False
        else:
            try:
                float(new_val)
                self.Mem_size=new_val

                new_ratio=round(float(self.dist)/float(self.Mem_size),2)

                self.ratio_val_ent.delete(0, END)
                self.ratio_val_ent.insert(0, new_ratio)

                self.Mem_ratio = new_ratio
                self.modif_image()
                return True
            except:
                self.UI_Size.delete(0, END)
                self.UI_Size.insert(0, self.Mem_size)
                return False


    def validate(self, follow=False):
        #Save the new ratio and close the Frame
        self.UI_Size_update(self.UI_Size.get())
        self.UI_Ratio_update(self.ratio_val_ent.get())
        if self.Mem_ratio != "NA" and self.unit and self.Mem_ratio>0: #We check that user filed all the boxes
            list_item = self.Check_units.curselection()

            if self.Vid.Track[0]:#If the parameters were not defined yet
                old_min=float(self.Vid.Track[1][3][0])* float(self.Vid.Scale[0]) ** 2
                old_max=float(self.Vid.Track[1][3][1])* float(self.Vid.Scale[0]) ** 2
                old_dist = float(self.Vid.Track[1][5] )* float(self.Vid.Scale[0])
            self.Vid.Scale[0] = float(self.Mem_ratio)
            self.Vid.Scale[1] = ["m","cm","mm"][list_item[0]]

            if self.Vid.Track[0]:
                self.Vid.Track[1][3][0]=old_min/ float(self.Vid.Scale[0]) ** 2
                self.Vid.Track[1][3][1]=old_max/ float(self.Vid.Scale[0]) ** 2
                self.Vid.Track[1][5]=old_dist/ float(self.Vid.Scale[0])

            if follow and self.Vid != self.main_frame.liste_of_videos[-1]:
                for i in range(len(self.main_frame.liste_of_videos)):
                    if self.main_frame.liste_of_videos[i] == self.Vid:
                        self.choice_menu.change_vid(self.main_frame.liste_of_videos[i + 1].User_Name)
                        break

            else:
                self.End_of_window()

        #If some info are missing, a message will ask the user to do fill them.
        elif self.Mem_ratio == "NA":
            self.HW.change_default_message(self.Messages["Scale4"])
            self.HW.get_attention(0)
        elif not self.unit:
            self.HW.change_default_message(self.Messages["Scale5"])
            self.HW.get_attention(0)
        elif self.dist==0:
            self.HW.change_default_message(self.Messages["Scale6"])
            self.HW.get_attention(0)


    def End_of_window(self):
        #Close the window properly
        self.grab_release()
        self.HW.grid_forget()
        self.HW.destroy()
        self.Vid_Lecteur.proper_close()
        self.canvas_bt_global.grid_forget()
        self.canvas_bt_global.destroy()
        self.main_frame.return_main()

    def moved_can(self, Pt, Shift):
        #We move a selected point on the image.
        if self.Pt_select is not None:
            self.liste_points[self.Pt_select]=[int(Pt[0]),int(Pt[1])]
            self.UI_Size_update(self.UI_Size.get())
            self.modif_image()

    def released_can(self, *args):
        pass

    def pressed_can(self, Pt, Shift):
        #When user click on the frame:
        if Pt[0]>=0 and Pt[0]<=self.Vid_Lecteur.Size[1] and Pt[1]>=0 and Pt[1]<=self.Vid_Lecteur.Size[0]:
            if len(self.liste_points)<1: #If it is the first point
                self.liste_points.append([Pt[0],Pt[1]])
                self.Pt_select=0

            elif len(self.liste_points)<=2: #If there is already at least one point:
                self.Pt_select = None# we remove potential previous selection
                for j in range(len(self.liste_points)):# Check if a point is under the cursor
                        if math.sqrt((self.liste_points[j][0] - Pt[0]) ** 2 + (self.liste_points[j][1] - Pt[1]) ** 2) < 10:
                            self.Pt_select = j
                            break

                #If not we either replace the last point or create it of there was only one defined
                if len(self.liste_points)<2 and self.Pt_select is None:
                    self.liste_points.append([Pt[0], Pt[1]])
                    self.Pt_select=len(self.liste_points)-1

                if len(self.liste_points)==2 and self.Pt_select is None:
                    self.liste_points.pop(1)
                    self.liste_points.append([Pt[0], Pt[1]])
                    self.Pt_select=1

            self.UI_Size_update(self.UI_Size.get())
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
            new_img = (Class_stabilise.find_best_position(Vid=self.Vid, Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=False))

        if len(self.liste_points)>0:
            for pt in self.liste_points:
                new_img=cv2.circle(new_img,tuple(pt),max(1,round(3*self.Vid_Lecteur.ratio)),(255,0,0),-1)

        if len(self.liste_points)==2:
            self.dist=math.sqrt((self.liste_points[0][0]-self.liste_points[1][0])**2+(self.liste_points[0][1]-self.liste_points[1][1])**2)
            new_img=cv2.line(new_img,tuple(self.liste_points[0]),tuple(self.liste_points[1]),(255,0,0),max(1,round(1.5*self.Vid_Lecteur.ratio)))
            cv2.putText(new_img,str(round(self.dist,1))+" px",(self.liste_points[1][0]-50,self.liste_points[1][1]-25),cv2.FONT_HERSHEY_SIMPLEX,1*self.Vid_Lecteur.ratio,(255,255,255),int(6*self.Vid_Lecteur.ratio))
            cv2.putText(new_img, str(round(self.dist, 1)) + " px",(self.liste_points[1][0] - 50, self.liste_points[1][1] - 25), cv2.FONT_HERSHEY_SIMPLEX,1 * self.Vid_Lecteur.ratio, (0, 0, 0), int(3*self.Vid_Lecteur.ratio))

        if self.Scrollbar.active_pos > self.Scrollbar.crop_end or self.Scrollbar.active_pos < self.Scrollbar.crop_beg:
            new_img = cv2.addWeighted(new_img, 1, new_img, 0, 1)

        if self.first:
            self.Vid_Lecteur.Size = (new_img.shape[0], new_img.shape[1])
            self.Vid_Lecteur.zoom_sq = [0, 0, new_img.shape[1], new_img.shape[0]]

        self.Vid_Lecteur.afficher_img(new_img)
        self.first = False




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