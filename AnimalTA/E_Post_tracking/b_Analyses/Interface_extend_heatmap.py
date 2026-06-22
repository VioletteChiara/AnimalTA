import math
from tkinter import *
from tkinter import ttk
from AnimalTA.E_Post_tracking.b_Analyses import Interface_sequences, Functions_deformation, Functions_Analyses_Speed
from AnimalTA.E_Post_tracking import Coos_loader_saver as CoosLS
from AnimalTA.A_General_tools import Function_draw_arenas, UserMessages, Class_loading_Frame, Color_settings, Diverse_functions, Message_simple_question
import cv2
import numpy as np
import PIL
import os


class Lists(Frame):
    """ This Frame displays a list of the videos and their arenas from the project that have been tracked.
    The user can select some arenas to copy-paste there the elements of interest from the current arena"""
    def __init__(self, parent, boss,detail_explo_parent, liste_videos, Current_Vid, Current_Area, Current_Ind, infos_explo, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.boss=boss
        self.grid(sticky="nsew")
        self.Current_Vid=Current_Vid
        self.Current_Area=Current_Area
        self.Current_Ind=Current_Ind
        self.liste_videos=liste_videos
        self.method, self.surface, self.circle_param=infos_explo
        self.detail_explo_parent=detail_explo_parent

        #Import messages
        self.Messages = UserMessages.get_dict()

        Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW

        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW

        self.winfo_toplevel().title(self.Messages["Extend_Ana0"])


        #User help
        User_help=Label(self,text=self.Messages["Extend_Ana1"], wraplength=800, justify=LEFT, **Color_settings.My_colors.Label_Base)
        User_help.grid(row=0, column=0, columnspan=3)

        # Listbox of other arenas
        self.Button_sel_al_o=Button(self,text=self.Messages["ExtendB1"], command=self.select_all_areas, **Color_settings.My_colors.Button_Base)
        self.Button_sel_al_o.grid(row=1, column=0, columnspan=2)
        self.all_sel_areas=False
        self.yscrollbar2 = ttk.Scrollbar(self)
        self.yscrollbar2.grid(row=2, column=1, sticky="ns")
        self.Liste_Vids = Listbox(self, selectmode = EXTENDED, width=50, exportselection=0, yscrollcommand=self.yscrollbar2.set, **Color_settings.My_colors.ListBox)
        self.yscrollbar2.config(command=self.Liste_Vids.yview)

        self.to_remove_sel=[]#The Video cannot be selecetd, only the arenas
        self.pointers=[]#To then allow to associate the text in the list to the arenas
        for Vid in liste_videos:
            if Vid.Tracked:#We consider only tracked videos
                if Vid == Current_Vid:  # We highlight in red the current Vid and it will be placed in the top of the list
                    self.Liste_Vids.insert(0, self.Messages["Video"] + ": " + Vid.User_Name)
                    self.Liste_Vids.itemconfig(0, fg=Color_settings.My_colors.list_colors["Fg_not_valide"], bg=Color_settings.My_colors.list_colors["Table2"])
                    self.to_remove_sel=[val+1 for val in self.to_remove_sel]
                    self.to_remove_sel.append(0)
                    self.pointers.insert(0,[Vid, None, None])
                else:
                    self.Liste_Vids.insert(END, self.Messages["Video"] +": "+Vid.User_Name)
                    self.Liste_Vids.itemconfig("end", fg=Color_settings.My_colors.list_colors["Fg_T2"], bg=Color_settings.My_colors.list_colors["Table2"])
                    self.to_remove_sel.append(self.Liste_Vids.size()-1)
                    self.pointers.append([Vid,None, None])

                Ar_cur_vid=1
                for IndID in range(len(Vid.Identities)):
                    if Vid == Current_Vid:
                        self.Liste_Vids.insert(Ar_cur_vid, "  -" + self.Messages["Arena"] + "_" + str( Vid.Identities[IndID][0]) + "_" + Vid.Identities[IndID][1])
                        self.pointers.insert(Ar_cur_vid, [Vid, Vid.Identities[IndID][0], IndID])
                        self.Liste_Vids.itemconfig(Ar_cur_vid, fg=Color_settings.My_colors.list_colors["Fg_T1"],
                                                   bg=Color_settings.My_colors.list_colors["Table1"])
                        self.to_remove_sel = [0] + [val + 1 for val in self.to_remove_sel if val>0]
                        Ar_cur_vid += 1
                    else:
                        self.Liste_Vids.insert(END, "  -"+ self.Messages["Arena"]+"_" + str( Vid.Identities[IndID][0]) + "_" + Vid.Identities[IndID][1])
                        self.Liste_Vids.itemconfig("end", fg=Color_settings.My_colors.list_colors["Fg_T1"],
                                                   bg=Color_settings.My_colors.list_colors["Table1"])
                        self.pointers.append([Vid,Vid.Identities[IndID][0], IndID])


        self.Liste_Vids.grid(row=2, column=0, sticky="nsew")
        self.Liste_Vids.bind('<<ListboxSelect>>',self.remove_sel)
        self.Liste_Vids.bind("<Motion>", self.show_Arenas)
        self.Liste_Vids.bind("<Leave>", self.stop_show_Arenas)

        self.Validate_button=Button(self, text=self.Messages["Validate"], command=self.validate, **Color_settings.My_colors.Button_Base)
        self.Validate_button.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.Validate_button.grid(row=3, columnspan=3, sticky="nsew")
        self.Validate_button.config(state="disable")

        self.parent.update()
        self.max_can_height = self.parent.winfo_height()
        self.max_can_width = self.parent.winfo_screenwidth()-self.parent.winfo_width()-200

        #In this canves, we will show the video and position of arenas
        self.Canvas_shaow_Ar=Canvas(self, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.Canvas_shaow_Ar.grid(row=0, column=3, rowspan=4, sticky="nsew")

        self.grab_set()
        self.boss.ready=False
        self.parent.protocol("WM_DELETE_WINDOW", self.close)

    def select_all_areas(self):
        #Select/unselect all arenas
        if not self.all_sel_areas:
            self.Liste_Vids.select_set(0, END)
            self.Button_sel_al_o.config(text=self.Messages["ExtendB2"])
            self.all_sel_areas=True
        else:
            self.Liste_Vids.selection_clear(0, END)
            self.Button_sel_al_o.config(text=self.Messages["ExtendB1"])
            self.all_sel_areas=False

        for index in range(len(self.to_remove_sel)): #The video names cannot be selected.
            self.Liste_Vids.selection_clear(self.to_remove_sel[index])

        self.check_button()#On actualise le bouton de validation

    def select_all_objs(self):
        #Select all the elements of interest inside the current arena
        if not self.all_sel_objs:
            self.Liste_objects.select_set(0, END)
            self.Button_sel_al.config(text=self.Messages["ExtendB2"])
            self.all_sel_objs=True
        else:
            self.Liste_objects.selection_clear(0, END)
            self.Button_sel_al.config(text=self.Messages["ExtendB1"])
            self.all_sel_objs=False
        self.check_button()#On actualise le bouton de validation

    def close(self):
        #Close this window properly
        self.parent.destroy()
        self.boss.ready=True

    def validate(self):
        question = Message_simple_question.Messagebox(parent=self, title=self.Messages["Warning"],
                                     message=self.Messages["Heatmap_warn"],
                                     Possibilities=[self.Messages["Continue"],
                                                    self.Messages["Cancel"]])

        self.wait_window(question)
        response = question.result

        if response==0:
            Load_show=Class_loading_Frame.Loading(self, text=self.Messages["Do_Heatmap"])
            Load_show.grid(row=6,column=0,columnspan=6)


            Np_style_pts=np.array([self.pointers[i] for i in self.Liste_Vids.curselection()])
            list_of_vids =[]
            for Vid in Np_style_pts[:,0]:#Look for all videos with at least one selected arena
                if Vid not in list_of_vids:
                    list_of_vids.append(Vid)

            mask_kept=None

            nb_I=0
            all_heats = []
            all_centers = []
            for Vid in list_of_vids:#For each of these videos, we look for the arenas
                Load_show.show_load(nb_I/len(list_of_vids))#Show the progress
                # Load Coos:
                Coos = CoosLS.load_coos(Vid, location=self)
                if len(Vid.Analyses[4][0]) > 0:
                    Coos = Functions_deformation.deform_coos(Coos, Vid.Analyses[4][0])

                if Vid == self.Current_Vid:
                    if self.boss.Check_Smoothed.get():
                        Coos = self.boss.smooth_coos(Coos)
                else:
                    if Vid.Smoothed[0] != 0:
                        Coos = Diverse_functions.smooth_coos(Coos=Coos,
                                                             window_length=Vid.Smoothed[0],
                                                             polyorder=Vid.Smoothed[1])

                for IndID in range(len(Vid.Identities)):
                    if IndID in [self.pointers[i][2] for i in self.Liste_Vids.curselection() if self.pointers[i][0]==Vid]:#If the individual was selected
                        #Prepare the Arena:
                        Area = Vid.Identities[IndID][0]
                        Arenas = Function_draw_arenas.get_arenas(Vid)

                        rectangle, mask = Function_draw_arenas.enclosing_rectangle(Area, Vid, ret=True)
                        cropx, cropy, width, heigh = rectangle
                        mask = mask[cropy:(cropy + heigh), cropx:(cropx + width)]
                        Arena_pts = Arenas[Area]

                        if Vid==self.Current_Vid:
                            mask_kept = mask.copy()

                        #Prepare the image
                        Repre=Vid.extract_repre_img()
                        new_val, values_img_tmp, center = Functions_Analyses_Speed.calculate_exploration(
                            method=[self.method, self.surface, self.circle_param], Vid=Vid,
                            Coos=Coos[IndID], deb=0,
                            end=len(Coos[IndID]) - 1,
                            Arena=Arena_pts, image=Repre,
                            show=True, subsample=True, only_vals=True, load_frame=[Load_show, nb_I,len(self.Liste_Vids.curselection())])


                        values_img_tmp = values_img_tmp[cropy:(cropy + heigh), cropx:(cropx + width)]

                        all_heats.append(values_img_tmp)
                        all_centers.append(center)
                        nb_I+=1

            #We now need to combine all the heatmaps together.
            max_height = max(arr.shape[0] for arr in all_heats)
            max_width = max(arr.shape[1] for arr in all_heats)

            summed_heat = np.zeros((max_height, max_width), dtype=np.float64)
            pos=0
            for heat in all_heats:
                if self.method == 1:#If method=rectangular, we make the top left corner match
                    diff_x=int(all_centers[0][0]-all_centers[pos][0])
                    diff_y = int(all_centers[0][1] - all_centers[pos][1])

                    print(diff_x)

                    move_array=heat.copy()
                    if diff_x>0:
                        zeros_x = np.zeros((heat.shape[0], diff_x, heat.shape[2]), dtype=heat.dtype)  # one column of zeros
                        move_array = np.hstack((zeros_x, move_array))
                    elif diff_x<0:
                        move_array=move_array[:,diff_x:]
                    add_x= np.zeros((heat.shape[0], max(0,max_width-move_array.shape[1]), heat.shape[2]), dtype=heat.dtype)  # one column of zeros
                    move_array = np.hstack((move_array, add_x))


                    if diff_y>0:
                        zeros_y = np.zeros((diff_y, move_array.shape[1], heat.shape[2]), dtype=heat.dtype)  # one column of zeros
                        move_array = np.vstack((zeros_y, move_array))
                    elif diff_y<0:
                        move_array=move_array[diff_y:,:]
                    add_y=np.zeros((max(0,max_height-move_array.shape[0]), move_array.shape[1], heat.shape[2]), dtype=heat.dtype)  # one column of zeros
                    move_array = np.vstack((move_array, add_y))

                    move_array=move_array[0:(max_height),0:(max_width),0]

                elif self.method == 2 or self.method==0: #If method = modern or circular mesh, we center based on the center
                    diff_y=int(math.ceil((max_height-heat.shape[0])/2))
                    diff_x = int(math.ceil((max_width-heat.shape[1]) / 2))
                    zeros_x = np.zeros((heat.shape[0], diff_x,  heat.shape[2]), dtype=heat.dtype)  # one column of zeros
                    move_array = np.hstack((zeros_x, heat, zeros_x))
                    zeros_y = np.zeros((diff_y, move_array.shape[1], heat.shape[2]), dtype=heat.dtype)  # one column of zeros
                    move_array = np.vstack((zeros_y, move_array,zeros_y))
                    move_array=move_array[0:(max_height),0:(max_width),0]

                summed_heat += move_array
                pos+=1

            if mask_kept is None:
                mask_kept=mask
            mask_kept = cv2.resize(mask_kept, (max_width, max_height), interpolation=cv2.INTER_LINEAR)
            summed_heat[np.where(mask_kept == 0)] = -1
            summed_heat = np.ma.masked_where(summed_heat < 0, summed_heat)
            Load_show.destroy()
            #
            self.detail_explo_parent.open_heatmap(summed_heat)

        self.parent.destroy()


    def check_button(self, *arg):
        #The user can validate only if at least one element and one arena were selected
        if len(self.Liste_Vids.curselection())>0:
            self.Validate_button.config(state="normal", background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])


    def show_Arenas(self, event):
        #This function display an image of the video over which the cursor is in the list.
        #The contours of arenas are highlighted and if the cursor is over a specifi arena, this arena is highlighted itself
        index = self.Liste_Vids.index("@%s,%s" % (event.x, event.y))
        Which_part = 0
        if self.pointers[index][0].Cropped[0]:
            if len(self.pointers[index][0].Fusion) > 1:  # If the video result from a concatenation of two videos
                Which_part = [index0 for index0, Fu_inf in enumerate(self.pointers[index][0].Fusion) if Fu_inf[0] <= self.pointers[index][0].Cropped[1][0]][-1]

        if self.pointers[index][0].type=="Video":
            capture = cv2.VideoCapture(self.pointers[index][0].Fusion[Which_part][1])  # Faster with opencv and the accuracy is not highly important here
            capture.set(cv2.CAP_PROP_POS_FRAMES, self.pointers[index][0].Cropped[1][0] - self.pointers[index][0].Fusion[Which_part][0])
            _, img = capture.read()
            del capture
        else:
            img = cv2.imread(os.path.join(self.pointers[index][0].Fusion[Which_part][1], self.pointers[index][0].img_list[self.pointers[index][0].Cropped[1][0] - self.pointers[index][0].Fusion[Which_part][0]]))

        img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if self.pointers[index][0].Cropped_sp[0]:
            img = img[self.pointers[index][0].Cropped_sp[1][0]:self.pointers[index][0].Cropped_sp[1][2], self.pointers[index][0].Cropped_sp[1][1]:self.pointers[index][0].Cropped_sp[1][3]]

        self.Arenas = Function_draw_arenas.get_arenas(self.pointers[index][0])

        for Ar in range(len(self.Arenas)):
            cnt_M=cv2.moments(self.Arenas[Ar])
            if cnt_M["m00"] > 0:
                cX = int(cnt_M["m10"] / cnt_M["m00"])
                cY = int(cnt_M["m01"] / cnt_M["m00"])

                if Ar==self.pointers[index][1]:
                    img=cv2.putText(img, str(Ar), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    img=cv2.drawContours(img, self.Arenas, Ar, (0, 0, 0), 6)
                    img = cv2.drawContours(img, self.Arenas, Ar, (0, 0, 255), 2)

                else:
                    img=cv2.drawContours(img, self.Arenas, Ar,(255,0,0),2)
                    img=cv2.putText(img,str(Ar),(cX,cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

        ratio=max(img.shape[1]/self.max_can_width, img.shape[0]/self.max_can_height)
        img=cv2.resize(img,(int(img.shape[1]/ratio),int(img.shape[0]/ratio)))
        img2=self.image_to_show3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img))
        self.Canvas_shaow_Ar.create_image(0, 0, image=img2, anchor=NW)
        self.Canvas_shaow_Ar.config(height=img.shape[0], width=img.shape[1])

    def stop_show_Arenas(self, event):
        cv2.destroyAllWindows()

    def remove_sel(self,*arg):
        #Avoid that user can select a vido.
        selection=self.Liste_Vids.curselection()
        for index in range(len(self.to_remove_sel)):
            if self.to_remove_sel[index] in selection:
                try:
                    next=self.to_remove_sel[index+1]
                except:
                    next=self.Liste_Vids.size()

                was_sel=0
                for elem_to_add in range(self.to_remove_sel[index]+1, next):
                    if elem_to_add not in selection:
                        was_sel +=1
                        self.Liste_Vids.select_set(elem_to_add)
                if was_sel==0:
                    for elem_to_add in range(self.to_remove_sel[index] + 1, next):
                        self.Liste_Vids.selection_clear(elem_to_add)
                self.Liste_Vids.selection_clear(self.to_remove_sel[index])
        self.check_button()


