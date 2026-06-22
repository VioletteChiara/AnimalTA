from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
import numpy as np
import math
import os
from AnimalTA.A_General_tools import Class_change_vid_menu, Video_loader as VL, UserMessages, User_help, Color_settings, Class_Lecteur, Class_stabilise
from AnimalTA.B_Project_organisation import Class_Row_Videos
import itertools

class Scale(Frame):
    """This Frame allows the user  to define a scale by selecting two points in the video and indicating the distance between them IRL"""
    def __init__(self, parent, boss, main_frame, Video_file, speed, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.boss=boss
        self.main_frame=main_frame
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.Vid = Video_file
        self.first=True

        #Import messages
        self.Messages = UserMessages.get_dict()

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

        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, show_whole_frame=False)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Vid_Lecteur.speed.set(speed)
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=100)

        #Help user and parameters
        self.HW= User_help.Help_win(self.parent, default_message=self.Messages["Scale2"],  width=250,
                                    shortcuts = {self.Messages["Short_Space"]:
                                                     self.Messages["Short_Space_G"],
                                                 self.Messages["Short_Ctrl_click"]:
                                                     self.Messages["Short_Ctrl_click_G"],
                                                 self.Messages["Short_Ctrl_Rclick"]:
                                                     self.Messages["Short_Ctrl_Rclick_G"],
                                                 self.Messages["Short_Ctrl_click_drag"]:
                                                     self.Messages["Short_Ctrl_click_drag_G"],
                                                 self.Messages["Short_RArrow"]:
                                                     self.Messages["Short_RArrow_G"],
                                                 self.Messages["Short_LArrow"]:
                                                     self.Messages["Short_LArrow_G"]})

        self.HW.grid(row=0, column=1,sticky="nsew")

        #Options
        self.canvas_bt_global=Canvas(self.parent, height=10, bd=0, highlightthickness=0, **Color_settings.My_colors.Frame_Base)
        self.canvas_bt_global.grid(row=1,column=1, sticky="nsew")

        #CTXT
        Other_vid_B=Button(self.canvas_bt_global,text="See other 3D Video", command=self.switch_Vid, **Color_settings.My_colors.Button_Base)
        Other_vid_B.grid(row=0, column=0)

        self.Entries=Frame(self.canvas_bt_global, **Color_settings.My_colors.Frame_Base)
        self.Entries.grid(row=1,column=0, sticky="nsew")
        #CTXT
        self.all_Entries=[[],[],[]]
        self.reg_coos = self.register(self.reg_coos_update)
        Label(self.Entries, text="X", **Color_settings.My_colors.Label_Base).grid(row=0, column=1)
        Label(self.Entries, text="Y", **Color_settings.My_colors.Label_Base).grid(row=0, column=2)
        Label(self.Entries, text="Z" , **Color_settings.My_colors.Label_Base).grid(row=0, column=3)

        for pt in range(8):
            Label(self.Entries, text="Pt "+str(pt+1),**Color_settings.My_colors.Label_Base).grid(row=pt+1, column=0)

            self.all_Entries[0].append(Entry(self.Entries, **Color_settings.My_colors.Entry_Base))
            self.all_Entries[0][pt].grid(row=pt+1, column=1)
            self. all_Entries[0][pt].config(validate="focusout", validatecommand=(self.reg_coos, "%P"))

            self.all_Entries[1].append(Entry(self.Entries, **Color_settings.My_colors.Entry_Base))
            self.all_Entries[1][pt].grid(row=pt+1, column=2)
            self.all_Entries[1][pt].config(validate="focusout", validatecommand=(self.reg_coos, "%P"))

            self.all_Entries[2].append(Entry(self.Entries, **Color_settings.My_colors.Entry_Base))
            self.all_Entries[2][pt].grid(row=pt+1, column=3)
            self.all_Entries[2][pt].config(validate="focusout", validatecommand=(self.reg_coos, "%P"))


        self.Check_units=Listbox(self.canvas_bt_global, exportselection=0, **Color_settings.My_colors.ListBox)
        self.Check_units.config(height=3)
        self.Check_units.insert(1, "m")
        self.Check_units.insert(2, "cm")
        self.Check_units.insert(3, "mm")
        self.Check_units.grid(row=2,column=0)
        self.Check_units.bind('<<ListboxSelect>>', self.update_ui)


        #Validate once the scale is defined
        bouton_validate = Button(self.canvas_bt_global, text=self.Messages["Validate"], command=self.validate, **Color_settings.My_colors.Button_Base)
        bouton_validate.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        bouton_validate.grid(row=6, column=0, columnspan=3,sticky="nsew")

        B_Validate_NContinue=Button(self.canvas_bt_global, text=self.Messages["Validate_NC"], command=lambda: self.validate(follow=True), **Color_settings.My_colors.Button_Base)
        B_Validate_NContinue.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        B_Validate_NContinue.grid(row=7,column=0, columnspan=3,sticky="nsew")


        #Parameters to show the image/calculate image reduction and canvas' size
        if len(self.Vid.Scale[2][0])>0:
            for row_widgets, row_values in zip(self.all_Entries, self.Vid.Scale[2][0]):
                for entry_widget, value in zip(row_widgets, row_values):
                    entry_widget.delete(0, END)  # Clear previous value
                    entry_widget.insert(0, value)  # Insert new value
            self.liste_points=self.Vid.Scale[2][1].copy()

            self.Check_units.select_set(["m", "cm", "mm"].index(self.Vid.Scale[1]))
            self.unit = True#True if a unit has already been selected
            self.update_ui()
        else:
            self.liste_points = []
            self.unit = False

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

        self.modif_image()


    def switch_Vid(self):
        self.validate()
        self.main_frame.list_projects.append(
            Class_Row_Videos.Row_Can(parent=self.main_frame.canvas_rows, main_boss=self.main_frame, Video_file=self.Vid.comb_V_3D,
                                     proj_pos=len(self.main_frame.list_projects)))
        self.main_frame.list_projects[-1].scale_vid(self.Vid_Lecteur.speed.get())

    def update_ui(self,event=None):
        #Update the label indicating the units
        self.unit=True
        list_item=self.Check_units.curselection()
        if len(list_item)>0:
            self.ratio_text.set("px/{}".format(["m","cm","mm"][list_item[0]]))

    def reg_coos_update(self, new_val):
        # Recalculates and updates the ratio value
        if new_val == "":
            return False
        else:
            try:
                float(new_val)
                return True
            except:
                return False


    def validate(self, follow=False):
        #Save the new ratio and close the Frame
        list_item = self.Check_units.curselection()

        # if self.Vid.Track[0]:#If the parameters were not defined yet
        #     old_min=float(self.Vid.Track[1][3][0])* float(self.Vid.Scale[0]) ** 2
        #     old_max=float(self.Vid.Track[1][3][1])* float(self.Vid.Scale[0]) ** 2
        #     old_dist = float(self.Vid.Track[1][5] )* float(self.Vid.Scale[0])

        all_entries_num=[[float(entry.get()) for entry in row] for row in self.all_Entries]
        print(all_entries_num)

        max_distance=0
        for p1, p2 in itertools.combinations(range(8), 2):
            distance = math.sqrt(math.pow(all_entries_num[0][p1] - all_entries_num[0][p2],2)+math.pow(all_entries_num[1][p1] - all_entries_num[1][p2],2)+math.pow(all_entries_num[2][p1] - all_entries_num[2][p2],2))

            if distance > max_distance:
                max_distance = distance
                farthest_pair = (p1, p2)




        distance_real=max_distance
        print(self.liste_points)
        distance_pixels=math.sqrt(math.pow(self.liste_points[farthest_pair[0]][0]-self.liste_points[farthest_pair[1]][0],2)+math.pow(self.liste_points[farthest_pair[0]][1]-self.liste_points[farthest_pair[1]][1],2))


        self.Vid.Scale[0] = distance_pixels/distance_real
        self.Vid.Scale[2][0] = all_entries_num
        self.Vid.Scale[2][1] = self.liste_points
        self.Vid.Scale[1] = ["m","cm","mm"][list_item[0]]

        self.Vid.comb_V_3D.Scale[2][0] = [[entry.get() for entry in row] for row in self.all_Entries]
        self.Vid.comb_V_3D.Scale[1] = ["m","cm","mm"][list_item[0]]

        # if self.Vid.Track[0]:
        #     self.Vid.Track[1][3][0]=old_min/ float(self.Vid.Scale[0]) ** 2
        #     self.Vid.Track[1][3][1]=old_max/ float(self.Vid.Scale[0]) ** 2
        #     self.Vid.Track[1][5]=old_dist/ float(self.Vid.Scale[0])

        if follow and self.Vid != self.main_frame.liste_of_videos[-1]:
            for i in range(len(self.main_frame.liste_of_videos)):
                if self.main_frame.liste_of_videos[i] == self.Vid:
                    self.choice_menu.change_vid(self.main_frame.liste_of_videos[i + 1].User_Name)
                    break

        else:
            self.End_of_window()



    def End_of_window(self):
        #Close the window properly
        self.grab_release()
        self.HW.grid_forget()
        self.HW.destroy()
        self.Vid_Lecteur.proper_close()
        self.canvas_bt_global.grid_forget()
        self.canvas_bt_global.destroy()
        self.main_frame.return_main()
        self.boss.select_vid()

    def moved_can(self, Pt, Shift):
        #We move a selected point on the image.
        if self.Pt_select is not None:
            self.liste_points[self.Pt_select]=[int(Pt[0]),int(Pt[1])]
            self.modif_image()

    def released_can(self, *args):
        pass

    def pressed_can(self, Pt, Shift):
        #When user click on the frame:
        if Pt[0]>=0 and Pt[0]<=self.Vid_Lecteur.Size[1] and Pt[1]>=0 and Pt[1]<=self.Vid_Lecteur.Size[0]:
            self.Pt_select = None# we remove potential previous selection
            for j in range(len(self.liste_points)):# Check if a point is under the cursor
                    if math.sqrt((self.liste_points[j][0] - Pt[0]) ** 2 + (self.liste_points[j][1] - Pt[1]) ** 2) < 10:
                        self.Pt_select = j
                        break

            #If not we either replace the last point or create it of there was only one defined
            if len(self.liste_points)<8 and self.Pt_select is None:
                self.liste_points.append([Pt[0], Pt[1]])
                self.Pt_select=len(self.liste_points)-1

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
            pt_id=1
            for pt in self.liste_points:
                new_img=cv2.circle(new_img,tuple(pt),max(1,round(3*self.Vid_Lecteur.ratio)),(255,0,0),-1)
                cv2.putText(new_img,"Pt "+str(pt_id),(int(pt[0]-20*self.Vid_Lecteur.ratio), int(pt[1]-10*self.Vid_Lecteur.ratio)),cv2.FONT_HERSHEY_SIMPLEX,0.5*self.Vid_Lecteur.ratio,(255,255,255),int(3*self.Vid_Lecteur.ratio))
                cv2.putText(new_img, "Pt "+str(pt_id),(int(pt[0] - 20*self.Vid_Lecteur.ratio), int(pt[1] - 10*self.Vid_Lecteur.ratio)), cv2.FONT_HERSHEY_SIMPLEX,0.5 * self.Vid_Lecteur.ratio, (0, 0, 0), int(1*self.Vid_Lecteur.ratio))
                pt_id+=1


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