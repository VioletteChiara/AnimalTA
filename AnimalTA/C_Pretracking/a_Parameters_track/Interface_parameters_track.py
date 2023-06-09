import cv2
from tkinter import *
import numpy as np
from AnimalTA.C_Pretracking.a_Parameters_track import Interface_nb_per_Ar, Draw_entrance
from AnimalTA.A_General_tools import Class_change_vid_menu, Class_Lecteur, Function_draw_mask as Dr, UserMessages, \
    User_help, Class_stabilise
from functools import partial

class Param_definer(Frame):
    #This Frame show the video and how the tracking parameters are affecting it.
    #It allos user to modify these parameters according to teh videos
    def __init__(self, parent, boss, main_frame, Video_file, portion=False, speed=0, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.main_frame=main_frame
        self.boss=boss
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.Vid = Video_file
        self.portion = portion
        self.cnts_entrance=self.Vid.Entrance#By defaults, there is no entrance area (known number of individuals)


        if self.portion:
            Grid.columnconfigure(self.parent, 0, weight=1)
            Grid.rowconfigure(self.parent, 0, weight=1)
            self.parent.geometry("1200x750")

        #Importation of the messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        self.fr_rate=self.Vid.Frame_rate[1]
        self.one_every=int(round(round(self.Vid.Frame_rate[0],2)/self.Vid.Frame_rate[1]))
        self.playing=False
        try:#This option was not present in the old version of AnimalTA, an exception is raised if we are working with old version files.
            self.correct_light=self.Vid.Track[1][7]
        except:
            self.correct_light = False

        try:#This option was not present in the old version of AnimalTA, an exception is raised if we are working with old version files.
            self.correct_flicker=self.Vid.Track[1][9]
        except:
            self.correct_flicker = False

        self.thresh_value = StringVar()
        self.thresh_value.set(self.Vid.Track[1][0])
        self.erode_value = StringVar()
        self.erode_value.set(self.Vid.Track[1][1])
        self.dilate_value = StringVar()
        self.dilate_value.set(self.Vid.Track[1][2])
        self.kernel = np.ones((3,3), np.uint8)
        self.Scroll_L = 75
        self.min_area_value=StringVar()
        self.max_area_value=StringVar()
        self.min_compact_value=StringVar()
        self.max_compact_value=StringVar()
        self.distance_max_value=StringVar()
        self.units = StringVar()
        width_labels=12

        self.mask = Dr.draw_mask(self.Vid)

        #We look for the arenas
        self.Arenas, _ = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.Arenas = Dr.Organise_Ars(self.Arenas)

        #We set here a maximum distance to avoid user to put too high distances
        if self.Vid.Scale[0]==0:
            self.distance_maximum=(max([self.Vid.shape[0],self.Vid.shape[1]])/2)
            self.max_area=float(self.Vid.shape[0]*self.Vid.shape[1])/10
            self.units.set("px")
        else:
            self.distance_maximum = (max([self.Vid.shape[0],self.Vid.shape[1]]) / 2)/float(self.Vid.Scale[0])
            self.max_area=((self.Vid.shape[0]/float(self.Vid.Scale[0])) * (self.Vid.shape[1]/float(self.Vid.Scale[0])))/10


        # Name of the current video and possibility to chnage from one to the other:
        if not self.portion:
            self.choice_menu = Class_change_vid_menu.Change_Vid_Menu(self, self.main_frame, self.Vid, "param")
            self.choice_menu.grid(row=0, column=0)

        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=100)  ########NEW

        #Help user and parameters
        self.HW= User_help.Help_win(self.parent, default_message=self.Messages["Track0"])
        self.HW.grid(row=0, column=1,sticky="nsew")

        ###Different options
        self.canvas_options=Canvas(self.parent, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_options.grid(row=1, column=1, sticky="sew")
        Grid.columnconfigure(self.canvas_options, 0, weight=1)  ########NEW
        self.canvas_options.columnconfigure(0,minsize=400)

        #Original image
        self.CheckVar = IntVar()
        F_Ori=Frame(self.canvas_options, background="white")
        F_Ori.grid(sticky="nsew", columnspan=3)
        Original_vis = Checkbutton(F_Ori, text=self.Messages["Track2"], variable=self.CheckVar,
                                        onvalue=0, offvalue=0, width=width_labels, command=self.modif_image, anchor="w", background="white")
        F_Ori.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Param1"]))
        F_Ori.bind("<Leave>", self.HW.remove_tmp_message)
        Original_vis.grid(sticky="w")

        # Greyscaled image
        F_Grey = Frame(self.canvas_options, background="white")
        F_Grey.grid(sticky="wnse", columnspan=3)
        Greyed_vis = Checkbutton(F_Grey, text=self.Messages["Track3"], variable=self.CheckVar,
                                   onvalue=1, offvalue=0, width=width_labels, command=self.modif_image, anchor="w",
                                   background="white")

        self.Button_grey=Button(F_Grey, text=self.Messages["Param10"], command=self.change_bright_corr)
        if self.correct_light:
            self.Button_grey.config(background="grey")
        else:
            self.Button_grey.config(background="SystemButtonFace")
        self.Button_grey.grid(sticky="snwe", row=0, column=1)
        self.Button_grey.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Param11"]))
        self.Button_grey.bind("<Leave>", self.HW.remove_tmp_message)
        Greyed_vis.grid(sticky="w", row=0,column=0)

        self.Button_flicker=Button(F_Grey, text=self.Messages["Param14"], command=self.change_flicker_corr)
        if self.correct_flicker:
            self.Button_flicker.config(background="grey")
        else:
            self.Button_flicker.config(background="SystemButtonFace")
        self.Button_flicker.grid(sticky="snwe", row=0, column=2)
        self.Button_flicker.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Param17"]))
        self.Button_flicker.bind("<Leave>", self.HW.remove_tmp_message)


        # Subtracked background greyscale
        if self.Vid.Back[0]:
            F_Sub=Frame(self.canvas_options, background="grey80")
            F_Sub.grid(sticky="nsew")
            Subtract_vis = Checkbutton(F_Sub, text=self.Messages["Names7"], variable=self.CheckVar,
                                            onvalue=2, offvalue=0, width=width_labels, command=self.modif_image, anchor="w", background="grey80")
            F_Sub.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Param2"]))
            F_Sub.bind("<Leave>", self.HW.remove_tmp_message)
            Subtract_vis.grid(sticky="w")

        # Thresholded image
        F_Thresh=Frame(self.canvas_options, background="white")
        F_Thresh.grid(sticky="nsew")

        Threshol_vis = Checkbutton(F_Thresh, text=self.Messages["Names1"], variable=self.CheckVar, onvalue=3, offvalue=0, width=width_labels, command=self.modif_image, anchor="w", background="white")
        F_Thresh.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Param3"]))
        F_Thresh.bind("<Leave>", self.HW.remove_tmp_message)
        Threshol_vis.grid(sticky="w")

        if self.Vid.Back[0]:
            Thresh_scroll = Scale(F_Thresh, from_=0, to=255, variable=self.thresh_value, orient=HORIZONTAL, background="white",highlightbackground="white")
        else:
            if (int(self.thresh_value.get()) % 2) == 0:
                self.thresh_value.set(int(self.thresh_value.get())+1)

            Thresh_scroll = Scale(F_Thresh, from_=2, to=1000, resolution=2, variable=self.thresh_value, orient=HORIZONTAL,background="white", highlightbackground="white")
        Thresh_scroll.grid(row=0,column=1, sticky="NSEW")

        verif_E_tresh = (self.register(self.verif_E_tresh_fun), '%P', '%V')
        Thresh_entry=Entry(F_Thresh,textvariable=self.thresh_value, width=10, validate="key", validatecommand=verif_E_tresh)
        Thresh_entry.grid(row=0,column=2, sticky="se")

        F_Thresh.grid_columnconfigure(0, weight=1)
        F_Thresh.grid_columnconfigure(1, weight=6)
        F_Thresh.grid_columnconfigure(2, weight=1)

        #Eroded image
        F_Ero=Frame(self.canvas_options, background="grey80")
        F_Ero.grid(sticky="nsew")

        Erode_vis = Checkbutton(F_Ero, text=self.Messages["Names2"], variable=self.CheckVar,
                                     onvalue=4, offvalue=0, width=width_labels, command=self.modif_image, anchor="w", background="grey80")
        F_Ero.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Param4"]))
        F_Ero.bind("<Leave>", self.HW.remove_tmp_message)
        Erode_vis.grid(sticky="w")
        Erode_scroll = Scale(F_Ero, from_=0, to=50, variable=self.erode_value, orient=HORIZONTAL, background="grey80",highlightbackground="grey80")
        Erode_scroll.grid(row=0, column=1, sticky="ew")

        Erode_entry=Entry(F_Ero,textvariable=self.erode_value, width=10, validate="key", validatecommand=verif_E_tresh, background="grey80")
        Erode_entry.grid(row=0,column=2, sticky="se")

        self.erode_value.trace("w", lambda name, index, mode, erode_value=self.erode_value, type=2: self.changed_val(self.erode_value.get(), type=4))

        F_Ero.grid_columnconfigure(0, weight=1)
        F_Ero.grid_columnconfigure(1, weight=6)
        F_Ero.grid_columnconfigure(2, weight=1)

        #Dilated image
        F_Dil=Frame(self.canvas_options, background="white")
        F_Dil.grid(sticky="nsew")
        F_Dil.grid_columnconfigure(0, weight=1)
        F_Dil.grid_columnconfigure(1, weight=6)
        F_Dil.grid_columnconfigure(2, weight=1)
        Dilate_vis = Checkbutton(F_Dil, text=self.Messages["Names3"], variable=self.CheckVar,
                                      onvalue=5, offvalue=0, width=width_labels, command=self.modif_image, anchor="w", background="white")
        F_Dil.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Param5"]))
        F_Dil.bind("<Leave>", self.HW.remove_tmp_message)
        Dilate_vis.grid(sticky="w")
        Dilate_scroll = Scale(F_Dil, from_=0, to=50, variable=self.dilate_value, orient=HORIZONTAL, background="white", highlightbackground="white")
        Dilate_scroll.grid(row=0, column=1, sticky="we")

        Dilate_entry=Entry(F_Dil,textvariable=self.dilate_value, width=10, validate="key", validatecommand=verif_E_tresh, background="white")
        Dilate_entry.grid(row=0,column=2, sticky="se")

        self.dilate_value.trace("w", lambda name, index, mode, dilate_value=self.dilate_value, type=2: self.changed_val(self.dilate_value.get(), type=5))

        #Contours filtered by area
        verif_E_float = (self.register(self.verif_E_float_fun), '%P', '%V')

        F_Area=Frame(self.canvas_options, background="grey80")
        F_Area.grid(sticky="nsew")
        F_Area.grid_columnconfigure(0, weight=1)
        F_Area.grid_columnconfigure(1, weight=1)
        F_Area.grid_columnconfigure(2, weight=9)
        F_Area.grid_columnconfigure(3, weight=1)

        Min_area_vis = Checkbutton(F_Area, text=self.Messages["Names4"], variable=self.CheckVar,
                                        onvalue=6, offvalue=0, width=width_labels, command=self.modif_image, anchor="w", background="grey80")
        F_Area.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Param6"]))
        F_Area.bind("<Leave>", self.HW.remove_tmp_message)
        Min_area_vis.grid(rowspan=2, sticky="w")
        Min_lab=Label(F_Area, text=self.Messages["Param15"]+":", background="grey80")
        Min_lab.grid(row=0, column=1, sticky="e")
        Min_area_scroll = Scale(F_Area, from_=0.001, to=self.max_area, resolution=0.05, length=self.Scroll_L, variable=self.min_area_value, orient=HORIZONTAL, background="grey80", highlightbackground="grey80")
        Min_area_scroll.grid(row=0, column=2, sticky="ew")

        Min_area_entry=Entry(F_Area,textvariable=self.min_area_value, width=10, validate="key", validatecommand=verif_E_float, background="grey80")
        Min_area_entry.grid(row=0,column=4, sticky="se")

        Max_lab=Label(F_Area, text=self.Messages["Param16"]+":", background="grey80")
        Max_lab.grid(row=1, column=1, sticky="e")
        Max_area_scroll = Scale(F_Area, from_=0.0, to=self.max_area, resolution=0.05, length=self.Scroll_L,
                                variable=self.max_area_value, orient=HORIZONTAL, background="grey80",
                                highlightbackground="grey80")
        Max_area_scroll.grid(row=1, column=2, sticky="ew")

        Max_area_entry=Entry(F_Area,textvariable=self.max_area_value, width=10, validate="all", validatecommand=verif_E_float, background="grey80")
        Max_area_entry.grid(row=1,column=4, sticky="se")

        Area_units = Label(F_Area, text=self.Vid.Scale[1] + "\u00b2",anchor="w", background="grey80")
        Area_units.grid(row=0, column=3, rowspan=2, sticky="we")

        #Image + representation of movement threshold
        F_Dist=Frame(self.canvas_options, background="white")
        F_Dist.grid(sticky="nsew")
        F_Dist.grid_columnconfigure(0, weight=1)
        F_Dist.grid_columnconfigure(1, weight=6)
        F_Dist.grid_columnconfigure(2, weight=1)
        Distance_traveled_vis = Checkbutton(F_Dist, text=self.Messages["Names6"],
                                                 variable=self.CheckVar, onvalue=8, offvalue=0, width=width_labels,
                                                 command=self.modif_image, anchor="w", background="white")
        F_Dist.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Param7"]))
        F_Dist.bind("<Leave>", self.HW.remove_tmp_message)
        Distance_traveled_vis.grid(row=0,column=0, sticky="w")

        Distance_traveled_scroll = Scale(F_Dist, from_=0.0, to=self.distance_maximum, resolution=0.05, length=self.Scroll_L, variable=self.distance_max_value, orient=HORIZONTAL, background="white", highlightbackground="white")
        Distance_traveled_scroll.grid(row=0, column=1, sticky="ew")

        self.Distance_entry=Entry(F_Dist, width=10, validate="all",  textvariable= self.distance_max_value, validatecommand=verif_E_float, background="white")
        self.Distance_entry.grid(row=0,column=3, sticky="se")

        Distance_traveled_units = Label(F_Dist, textvariable=self.units, anchor="w", background="white")
        Distance_traveled_units.grid(row=0, column=2, sticky="w")

        #Number of targets per arena
        self.KindTVar = IntVar()
        if not self.portion:
            F_Nb=Frame(self.canvas_options, background="grey80")
            F_Nb.grid(sticky="nsew")
            F_Nb.grid_columnconfigure(0, weight=1)
            self.Sub_F_Nb = Frame(F_Nb, background="grey80")


            #For the next update: proposes to track videos with unknown number of individuals.
            #self.Unknown_Nb_B=Button(F_Nb, text=self.Messages["Param12"], command=self.change_var_nb)#We allow the user to determine wether he knows how much targets they are or not
            #self.Sub_V_Nb = Frame(F_Nb, background="grey80")

            #This is for the next update: alloww to redraw the areas throught which targets can enter the arenas
            #self.draw_ent_B=Button(self.Sub_V_Nb, text="Redraw entrance area", command=self.redo_ent, background="grey80")
            #self.draw_ent_B.grid(sticky="nsew")
            #self.Sub_V_Nb.grid_columnconfigure(0, weight=1)


            self.Sub_F_Nb.grid_columnconfigure(0, weight=1)
            self.Sub_F_Nb.grid_columnconfigure(1, weight=5)
            self.Sub_F_Nb.grid_columnconfigure(2, weight=1)

            Lab_three_per_Ar = Label(self.Sub_F_Nb, text=self.Messages["Param9"], width=width_labels+3, wraplength=120, background="grey80")
            Lab_three_per_Ar.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Param8"]))
            Lab_three_per_Ar.bind("<Leave>", self.HW.remove_tmp_message)
            Lab_three_per_Ar.grid(row=0, column=0, sticky="w")

            NB_per_ar = Scale(self.Sub_F_Nb, variable=self.KindTVar,
                                      from_=1, to=100, command=self.change_nb_ar_glob, orient=HORIZONTAL, background="grey80", highlightbackground="grey80")
            NB_per_ar.grid(row=0, column=1, sticky="we")

            self.KindTVar.set(self.Vid.Track[1][6][0])
            param_nb_per_ar = Button(self.Sub_F_Nb, text="P", command=self.change_nb_ar)
            param_nb_per_ar.grid(row=0, column=2)
            param_nb_per_ar.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["TrackB2"]))
            param_nb_per_ar.bind("<Leave>", self.HW.remove_tmp_message)

            self.Sub_F_Nb.grid(row=1, column=0, sticky="nsew")#To be replaced by next lines when update

            #Add this part of code to unlock the possibility of variable number of targets tracking
            '''
            if self.Vid.Track[1][6][0]:
                self.Unknown_Nb_B.config(background="grey80")
                self.Sub_F_Nb.grid(row=1, column=0, sticky="nsew")
            else:
                self.Unknown_Nb_B.config(background="grey")
                self.Sub_V_Nb.grid(row=1, column=0, sticky="nsew")
            self.Unknown_Nb_B.grid(row=0,column=0)
            '''

        if not len(self.Vid.Track[1][6]) == len(self.Arenas):
            self.Vid.Track[1][6] = [self.Vid.Track[1][6][0] for n in self.Arenas]
        self.liste_ind_per_ar = self.Vid.Track[1][6]

        if not len(self.Vid.Analyses[1]) == len(self.Arenas):
            self.Vid.Analyses[1] = []*len(self.Arenas)

        self.min_area_value.set(self.Vid.Track[1][3][0])
        self.max_area_value.set(self.Vid.Track[1][3][1])
        self.min_compact_value.set(self.Vid.Track[1][4][0])
        self.max_compact_value.set(self.Vid.Track[1][4][1])
        self.distance_max_value.set(self.Vid.Track[1][5])
        self.units.set(str(self.Vid.Scale[1]))

        self.B_Validate=Button(self.canvas_options, text=self.Messages["Validate"],bg="#6AED35", command=self.Validate)#######NEW
        self.B_Validate.grid(row=13,column=0, sticky="ews")

        self.B_Validate_NContinue=Button(self.canvas_options, text=self.Messages["Validate_NC"],bg="#6AED35", command=lambda: self.Validate(follow=True))
        self.B_Validate_NContinue.grid(row=14,column=0, sticky="ews")

        # Show video and time-bar
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=10)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Vid_Lecteur.speed.set(speed)
        self.Vid_Lecteur.change_speed()
        self.Scrollbar=self.Vid_Lecteur.Scrollbar
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

        self.CheckVar.set(0)
        self.thresh_value.trace("w", lambda name, index, mode, thresh_value=self.thresh_value, type=2: self.changed_val(self.thresh_value.get(), type=3))
        self.distance_max_value.trace("w", lambda name, index, mode, distance_max_value=self.distance_max_value, type=2: self.changed_val(self.distance_max_value.get(), type=8))
        self.max_area_value.trace("w", lambda name, index, mode, max_area_value=self.max_area_value, type=5: self.changed_val(self.max_area_value.get(), type=6))
        self.min_area_value.trace("w", lambda name, index, mode, min_area_value=self.min_area_value, type=5: self.changed_val(self.min_area_value.get(), type=6))

        self.bind_all("<Button-1>", self.give_focus)
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)

    def redo_ent(self):
        self.Draw_Ent = Toplevel()
        Draw_entrance.Draw_ent(self.Draw_Ent, Img=self.last_empty, Entrances=self.cnts_entrance, Arenas=self.Arenas, boss=self, scale=self.Vid.Scale[0])
        self.unbind_all("<Button-1>")

    def change_var_nb(self):#Change between fixed number of targets to unknown number of targets
        if not self.liste_ind_per_ar[0]: #If we change from a variable to a fixed number of targets
            self.liste_ind_per_ar=[1]*len(self.liste_ind_per_ar)
            self.Unknown_Nb_B.config(background="grey80")
            self.Sub_F_Nb.grid(row=1, column=0, sticky="nsew")
            self.Sub_V_Nb.grid_forget()
            self.KindTVar.set(self.Vid.Track[1][6][0])
        else:#If we change from a fixed to a variable number of targets
            self.liste_ind_per_ar = [0] * len(self.liste_ind_per_ar)
            self.Unknown_Nb_B.config(background="grey")
            self.Sub_F_Nb.grid_forget()
            self.Sub_V_Nb.grid(row=1, column=0, sticky="nsew")

            if self.cnts_entrance==[]:#If no entrance area have ever been determined, we propose the external borders of the arena as entrance area.
                for Ar in self.Arenas:
                    empty=np.zeros([self.Vid.shape[0],self.Vid.shape[1],1], np.uint8)
                    empty=cv2.drawContours(empty,[Ar],-1,255,int(round(float(self.distance_max_value.get())*float(self.Vid.Scale[0])))*4)#The width of the entrance area depends of the movemnet threshold of individuals
                    empty = cv2.drawContours(empty, [Ar], -1, 0,-1)
                    cnts,_=cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    self.cnts_entrance.append(cnts)

        self.modif_image()

    def change_bright_corr(self):
        #Change the state of lightning correction from true to false and modify button accordingly
        self.correct_light = not self.correct_light
        if self.correct_light:
            self.Button_grey.config(background="grey")
        else:
            self.Button_grey.config(background="SystemButtonFace")
        self.modif_image()

    def change_flicker_corr(self):
        #Change the state of lightning correction from true to false and modify button accordingly
        self.correct_flicker = not self.correct_flicker
        if self.correct_flicker:
            self.Button_flicker.config(background="grey")
        else:
            self.Button_flicker.config(background="SystemButtonFace")
        self.modif_image()

    def changed_val(self, new_val, type):
        #If one of the values is modified by user, we check the value is not null and apply the modifications
        if len(new_val)>0 and new_val!="":
            self.modif_image(self.last_empty, change_track=type)

    def verif_E_tresh_fun(self, value, method):
        #We only allow user to write numerical values
        if value=="" and method=="key":
            return True
        else:
            try:
                int(value)
                return True
            except:
                return False

    def verif_E_float_fun(self, value, method):
        # We only allow user to write numerical values
        if method!="forced":
            if value=="" and method=="key":
                return True
            else:
                try:
                    float(value)
                    return True
                except:
                    return False
        else:
            return False

    def change_nb_ar(self):
        #This will open a small window in which the user can choose the number of expected targets in each arena
        newWindow = Toplevel(self.parent.master)
        interface = Interface_nb_per_Ar.Assign(parent=newWindow, boss=self)

    def change_nb_ar_glob(self, *karg):
        #Change the number of targets per arenas with the same number for all arenas
        self.liste_ind_per_ar=[self.KindTVar.get() for x in range(len(self.Arenas))]
        self.modif_image()

    def give_focus(self,event):
        #Ensure that the video reader always get the focus when the user is not typing in Entry boxes
        if event.widget.winfo_class()!="Entry":
            self.Vid_Lecteur.focus_set()

    def modif_image(self, img=[], affi=True, change_track=None, **arg):
        #Change the original image accordingly to the parameters defined by user
        if change_track!=None:
            self.CheckVar.set(change_track)

        if len(img)==0:
            img=np.copy(self.last_empty)
        else:
            self.last_empty = np.copy(img)

        liste_positions=[]

        #Stabilisation
        if self.Vid.Stab[0]:
            img = Class_stabilise.find_best_position(Vid=self.Vid, Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=img, show=False, prev_pts=self.Vid.Stab[1])

        TMP_image_to_show2 = np.copy(img)
        #Convert to greyscale
        if self.CheckVar.get()>0:
            TMP_image_to_show2=cv2.cvtColor(TMP_image_to_show2,cv2.COLOR_BGR2GRAY)

            #Correct flicker
            if self.correct_flicker and self.Scrollbar.active_pos > (self.Vid.Cropped[1][0]/self.one_every):
                diff=int(self.Scrollbar.active_pos - (self.Vid.Cropped[1][0]/self.one_every))
                for elem in range(self.Scrollbar.active_pos-min(2,diff),self.Scrollbar.active_pos):
                    last_img=cv2.cvtColor(self.Vid_Lecteur.update_image(elem,return_img=True),cv2.COLOR_BGR2GRAY)
                    TMP_image_to_show2 = cv2.addWeighted(last_img, 0.5, TMP_image_to_show2, 1 - 0.5, 0)


            #Correct lightning
            if self.correct_light:
                grey = np.copy(TMP_image_to_show2)
                if self.Vid.Mask[0]:
                    bool_mask = self.mask[:, :, 0].astype(bool)
                else:
                    bool_mask=np.full(grey.shape, True)
                grey2=grey[bool_mask]
                brightness = np.sum(grey2) / (255 * grey2.size)  # Mean value

                #Inspired from: https://stackoverflow.com/questions/57030125/automatically-adjusting-brightness-of-image-with-opencv
                ratio = brightness / self.Vid_Lecteur.or_bright
                TMP_image_to_show2 = cv2.convertScaleAbs(grey, alpha=1 / ratio, beta=0)


            if self.CheckVar.get() > 1:
                #Show background subtraction
                if self.Vid.Back[0]:
                    TMP_image_to_show2 = cv2.subtract(self.Vid.Back[1],TMP_image_to_show2) + cv2.subtract(TMP_image_to_show2,self.Vid.Back[1])

                if self.CheckVar.get()>2:
                    #Show thersholding and masking (remove outside of arenas)
                    if self.Vid.Back[0]:
                        _, TMP_image_to_show2=cv2.threshold(TMP_image_to_show2, int(self.thresh_value.get()), 255, cv2.THRESH_BINARY)
                    else:
                        TMP_image_to_show2 = cv2.adaptiveThreshold(TMP_image_to_show2, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, int(self.thresh_value.get())+1,10)
                    if self.Vid.Mask[0]:
                        TMP_image_to_show2 = cv2.bitwise_and(TMP_image_to_show2, TMP_image_to_show2, mask=self.mask)

                    if self.CheckVar.get() > 3:
                        #Erosion
                        TMP_image_to_show2 = cv2.erode(TMP_image_to_show2,self.kernel,iterations=int(self.erode_value.get()))

                        if self.CheckVar.get() > 4:
                            #Dilation
                            TMP_image_to_show2 = cv2.dilate(TMP_image_to_show2, self.kernel, iterations=int(self.dilate_value.get()))

                            if self.CheckVar.get() > 5:
                                #Filter contour by area
                                cnts, _ = cv2.findContours(TMP_image_to_show2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                TMP_image_to_show2=np.zeros([TMP_image_to_show2.shape[0],TMP_image_to_show2.shape[1],3], np.uint8)
                                for cnt in cnts:
                                    cnt_area=cv2.contourArea(cnt)
                                    if float(self.Vid.Scale[0])>0:
                                        cnt_area=cnt_area*(1/float(self.Vid.Scale[0]))**2

                                    if cnt_area>=float(self.min_area_value.get()) and cnt_area<=float(self.max_area_value.get()):
                                        if self.CheckVar.get() <= 6:
                                            TMP_image_to_show2=cv2.drawContours(TMP_image_to_show2,[cnt],0,(255,255,255),-1)
                                        else:
                                            TMP_image_to_show2=cv2.drawContours(TMP_image_to_show2,[cnt],0,(255,255,255),-1)

                                            if self.CheckVar.get() == 8 and self.Scrollbar.active_pos >= (self.Vid.Cropped[1][0]/self.one_every):
                                                #Show the distance threshold
                                                cnt_M = cv2.moments(cnt)
                                                if cnt_M["m00"]>0:
                                                    cX = int(cnt_M["m10"] / cnt_M["m00"])
                                                    cY = int(cnt_M["m01"] / cnt_M["m00"])
                                                    liste_positions.append((cX,cY))

                                if self.CheckVar.get() == 8 and affi:
                                    #To show the distance threshold, we must find the position of the target for the previous frame:
                                    if self.Scrollbar.active_pos > (self.Vid.Cropped[1][0]/self.one_every):
                                        old_img = self.Vid_Lecteur.update_image(int((self.Scrollbar.active_pos-1)),return_img=True)
                                        Old_pos=self.modif_image(img=old_img,affi=False)
                                        overlay=np.copy(img)
                                        alpha = 0.25  # Transparency factor.

                                        for Pt in Old_pos:
                                            if float(self.Vid.Scale[0])>0:
                                                overlay=cv2.circle(overlay,Pt,int(round(float(self.distance_max_value.get())*float(self.Vid.Scale[0]))),(0,0,255),-1)
                                            else:
                                                overlay=cv2.circle(overlay,Pt,int(round(float(self.distance_max_value.get()))),(0,0,255),-1)
                                        TMP_image_to_show2=cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)


                                    else:
                                        TMP_image_to_show2 = np.copy(img)

                                    if self.Scrollbar.active_pos >= (self.Vid.Cropped[1][0] / self.one_every):
                                        for Pt in liste_positions:#dra a circle on the top of the target's position
                                            TMP_image_to_show2 = cv2.circle(TMP_image_to_show2, Pt, max(int(5* self.Vid_Lecteur.ratio),1), (0, 200, 200), -1)

        #We draw the contours of the arenas
        TMP_image_to_show2 = cv2.drawContours(TMP_image_to_show2, self.Arenas, -1, (255, 0, 0), max(int(3* self.Vid_Lecteur.ratio),1))
        for Ar in range(len(self.Arenas)):
            x,y,w,h =cv2.boundingRect(self.Arenas[Ar])
            (w, h), _ = cv2.getTextSize(str(self.liste_ind_per_ar[Ar]), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=self.Vid_Lecteur.ratio, thickness=1)
            #Number of  target expected in each contour is written here
            TMP_image_to_show2 = cv2.putText(TMP_image_to_show2, str(self.liste_ind_per_ar[Ar]), (x+max(int(2* self.Vid_Lecteur.ratio),1), y + h + max(int(2* self.Vid_Lecteur.ratio),1)),
                              cv2.FONT_HERSHEY_DUPLEX,  self.Vid_Lecteur.ratio, (255, 0, 0), max(int(3* self.Vid_Lecteur.ratio),1))

        #If we have an unknown number of targets, we show the entrance area:
        if not self.liste_ind_per_ar[0] and self.CheckVar.get() == 8 and affi:
            overlay = TMP_image_to_show2.copy()
            for Ar in range(len(self.Arenas)):
                overlay = cv2.drawContours(overlay, self.cnts_entrance[Ar],-1, (255, 255, 0),-1)
            TMP_image_to_show2=cv2.addWeighted(TMP_image_to_show2,0.5,overlay,0.5,1)

        if affi:#If we want to  show the positions
            self.Vid_Lecteur.afficher_img(TMP_image_to_show2)
        else:# If we just wanted to get the positions of the targets but not displaying the image (look for previous frame target's positions)
            return(liste_positions)


    def Validate(self, follow=False):
        #Save and return to main menu
        self.Vid.Track[0] = True
        self.Vid.Track[1][0] = int(self.thresh_value.get())
        self.Vid.Track[1][1] = int(self.erode_value.get())
        self.Vid.Track[1][2] = int(self.dilate_value.get())
        self.Vid.Track[1][3] = [float(self.min_area_value.get()),float(self.max_area_value.get())]
        self.Vid.Track[1][4] = [0,0]
        self.Vid.Track[1][5] = float(self.distance_max_value.get())
        self.Vid.Track[1][6] = self.liste_ind_per_ar
        self.Vid.Entrance=self.cnts_entrance

        try: #This is an option not present in old AnimalTA versions, this is to avoid error
            self.Vid.Track[1][7] = self.correct_light
        except:
            self.Vid.Track[1].append(self.correct_light)

        try:  # This is an option not present in old AnimalTA versions, this is to avoid error
            self.Vid.Track[1][8] = self.Vid.Track[1][6][0]!=0
        except:
            self.Vid.Track[1].append(self.Vid.Track[1][6][0]!=0)

        try: #This is an option not present in old AnimalTA versions, this is to avoid error
            self.Vid.Track[1][9] = self.correct_flicker
        except:
            self.Vid.Track[1].append(self.correct_flicker)

        try:  # This is an option not present in old AnimalTA versions, this is to avoid error
            self.Vid.Track[1][8] = self.Vid.Track[1][6][0]!=0
        except:
            self.Vid.Track[1].append(self.Vid.Track[1][6][0]!=0)

        if follow and self.Vid != self.main_frame.liste_of_videos[-1]:
            for i in range(len(self.main_frame.liste_of_videos)):
                if self.main_frame.liste_of_videos[i]==self.Vid:
                    self.choice_menu.change_vid(self.main_frame.liste_of_videos[i+1].User_Name)
                    break
        else:
            self.End_of_window()

    def End_of_window(self):
        #Close properly
        self.unbind_all("<Button-1>")
        self.Vid_Lecteur.proper_close()
        self.grab_release()
        self.canvas_options.grid_forget()
        self.canvas_options.destroy()
        self.HW.grid_forget()
        self.HW.destroy()

        if not self.portion:
            self.main_frame.update_projects()
            self.main_frame.return_main()
        if self.portion:
            self.parent.destroy()


    def pressed_can(self, Pt, Shift):
        pass

    def moved_can(self, Pt, Shift):
        pass

    def released_can(self, Pt):
        pass

"""
root = Tk()
root.geometry("+100+100")
Video_file=Class_Video.Video(File_name="D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01.avi")
interface = Cropping(parent=root, boss=None, Video_file=Video_file)
root.mainloop()

"""