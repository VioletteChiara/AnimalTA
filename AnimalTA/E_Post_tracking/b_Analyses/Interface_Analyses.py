from tkinter import *
import cv2
import numpy as np
from AnimalTA.E_Post_tracking import Coos_loader_saver as CoosLS
from AnimalTA.E_Post_tracking.b_Analyses import Functions_Analyses_Speed, Class_rows_analyses, Interface_smooth_param, Interface_deformation, Functions_deformation
from AnimalTA.A_General_tools import Class_change_vid_menu, Class_Lecteur, Function_draw_mask, Interface_extend, \
    UserMessages, User_help, Class_stabilise, Class_loading_Frame, Color_settings
import copy
import math
from scipy.signal import savgol_filter


class Analyse_track(Frame):
    """
    Once the videos have been tracked and that trackings have been corrected, this section will allow the user to define the analyses he wants to perform.
    """

    def __init__(self, parent, boss, main_frame, Vid, Video_liste, CheckVar=None, speed=0, **kwargs):
        """
        :param parent: The container of this frame
        :param boss/main_frame: The upper level objects
        :param Vid: The concerned video
        :param Video_liste: The list of all videos
        :param CheckVar: Which type of analyses we want to show when the window is opened
        :param speed: at which speed we want the video reader to be initiated
        """
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base)
        self.parent = parent
        self.main_frame = main_frame
        self.boss = boss
        self.Video_liste = Video_liste
        self.Vid = Vid
        self.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.highlight = False
        self.show_all = False
        self.speed=speed

        # Messages importation
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        self.Messages = UserMessages.Mess[self.Language.get()]
        f.close()

        self.Calc_speed = Functions_Analyses_Speed.speed_calculations()  # We create classes linked to the different kind of analyses

        self.Infos_explo = [0, 1, 2]  # Characteristics of the exploration parameters
        self.Infos_inter = 0  # Threshold under which two targets are considered as neighbors

        # How long is the displayed trajectory?
        self.tail_size = IntVar()
        self.tail_size.set(10)

        if CheckVar == None: # If there was no special analyses to display, we display the forst one
            self.CheckVar = StringVar()
            self.CheckVar.set(0)
        else:
            self.CheckVar = StringVar(value=CheckVar)

        self.liste_ana = []# List of possible analyses
        self.overlay = None # An image that will added on the top of the video image that will show what we are looking at (for instantce the areas of interest).

        # Name of the video and option menu to change the current video

        self.choice_menu= Class_change_vid_menu.Change_Vid_Menu(self, self.main_frame, self.Vid, "analysis")
        self.choice_menu.grid(row=0,column=0)

        #Help panel
        self.HW = User_help.Help_win(self.parent, default_message=self.Messages["Analyses0"],
                                     shortcuts={self.Messages["Short_Space"]: self.Messages["Short_Space_G"],
                                               self.Messages["Short_Ctrl_click"]:self.Messages["Short_Ctrl_click_G"],
                                               self.Messages["Short_Ctrl_Rclick"]: self.Messages["Short_Ctrl_Rclick_G"],
                                               self.Messages["Short_Ctrl_click_drag"]: self.Messages["Short_Ctrl_click_drag_G"],
                                               self.Messages["Short_RArrow"]: self.Messages["Short_RArrow_G"],
                                               self.Messages["Short_LArrow"]: self.Messages[ "Short_LArrow_G"]})

        self.HW.grid(row=0, column=1, sticky="nsew")

        #The panel for user options
        self.User_params_cont = Frame(self.parent, width=150, **Color_settings.My_colors.Frame_Base)
        self.User_params_cont.grid(row=1, column=1)

        # Length of displayed trajectories
        self.Scale_tail = Scale(self.User_params_cont, from_=0, to=600, variable=self.tail_size, orient="horizontal",
                                label=self.Messages["Control4"], command=self.modif_image, **Color_settings.My_colors.Scale_Base)
        self.Scale_tail.grid(row=0, column=0, sticky="ew")
        self.Scale_tail.bind("<Enter>", lambda a: self.HW.change_tmp_message(self.Messages["Analyses1"]))
        self.Scale_tail.bind("<Leave>", lambda a: self.HW.remove_tmp_message())


        #Button so the user can see all the trajectories at the same time
        self.bouton_show_all_traj=Button(self.User_params_cont, text=self.Messages["Control11"], command=self.show_all_com, **Color_settings.My_colors.Button_Base)
        self.bouton_show_all_traj.grid(row=0,column=1, sticky="nsew")

        Canvas(self.User_params_cont, height=2.5, **Color_settings.My_colors.Frame_Base).grid(row=1,columnspan=2)


        #Correct deformation of the camera/angle:
        Deformation=Button(self.User_params_cont, text=self.Messages["Analyses12"], command=self.deform, **Color_settings.My_colors.Button_Base)
        Deformation.grid(row=2, column=0, sticky="nsew")
        Deformation.bind("<Enter>", lambda a: self.HW.change_tmp_message(self.Messages["Analyses13"]))
        Deformation.bind("<Leave>", self.HW.remove_tmp_message)
        #Apply similar deformation to other videos

        bouton_extend_Deformation = Button(self.User_params_cont, text=self.Messages["Analyses_B1"], command=self.extend_deform, **Color_settings.My_colors.Button_Base)
        bouton_extend_Deformation.grid(row=2, column=1, sticky="we")

        Canvas(self.User_params_cont, height=2.5, **Color_settings.My_colors.Frame_Base).grid(row=3, columnspan=2)

        # Apply smoothing filter
        Fr_smooth = Frame(self.User_params_cont, **Color_settings.My_colors.Frame_Base)
        Fr_smooth.grid(row=4, column=0, columnspan=2, sticky="nsew")
        Fr_smooth.columnconfigure(0, weight=10)
        Fr_smooth.columnconfigure(1, weight=1)


        self.Check_Smoothed = BooleanVar()
        self.Button_Smoothed_track = Checkbutton(Fr_smooth, text=self.Messages["Analyses8"],
                                                 variable=self.Check_Smoothed, onvalue=1, offvalue=0,
                                                 command=lambda: self.change_type_coos(modif=True), anchor="w", **Color_settings.My_colors.Checkbutton_Base)
        self.Button_Smoothed_track.grid(row=0, column=0, sticky="w")
        self.Button_Smoothed_track.bind("<Enter>", lambda a: self.HW.change_tmp_message(self.Messages["Analyses2"]))
        self.Button_Smoothed_track.bind("<Leave>", lambda a: self.HW.remove_tmp_message())

        self.Button_Smoothed_param = Button(Fr_smooth, text="P", command=self.modif_param_smoothed, anchor="w", **Color_settings.My_colors.Button_Base)
        self.Button_Smoothed_param.grid(row=0, column=1, sticky="e")
        self.Button_Smoothed_param.bind("<Enter>", lambda a: self.HW.change_tmp_message(self.Messages["Analyses2"]))
        self.Button_Smoothed_param.bind("<Leave>", lambda a: self.HW.remove_tmp_message())


        self.window_length = 15
        self.polyorder = 2

        # Apply similar smoothing values to other videos
        bouton_extend_S = Button(Fr_smooth, text=self.Messages["Analyses_B1"], command=self.extend_glob_smooth, **Color_settings.My_colors.Button_Base)
        bouton_extend_S.grid(row=0, column=2, sticky="we")
        bouton_extend_S.bind("<Enter>", lambda a: self.HW.change_tmp_message(self.Messages["Analyses3"]))
        bouton_extend_S.bind("<Leave>", lambda a: self.HW.remove_tmp_message())

        Canvas(self.User_params_cont, height=2.5, **Color_settings.My_colors.Frame_Base).grid(row=5, columnspan=2)


        #Load the video
        self.load_Vid(self.Vid)

        #Load the different kind of analyses
        self.Add_ana = Label(self.User_params_cont, text=self.Messages["Analyses_Lab1"],font=("Helvetica",13,"bold"),
                             height=1, **Color_settings.My_colors.Label_Base)
        self.Add_ana.config(background=Color_settings.My_colors.list_colors["Title_ana"], fg=Color_settings.My_colors.list_colors["Fg_Title1"])
        self.Add_ana.grid(row=6, columnspan=2, sticky="nsew")


        Liste_analyses = Frame(self.User_params_cont, height=200, width=150,
                               highlightthickness=4, **Color_settings.My_colors.Frame_Base)
        Liste_analyses.config(highlightbackground=Color_settings.My_colors.list_colors["Title_ana"])
        Liste_analyses.grid(row=7, columnspan=2, sticky="nsew")
        Liste_analyses.columnconfigure(0, weight=1)

        self.liste_ana.append(
            Class_rows_analyses.Row_Ana(main=self, parent=Liste_analyses, checkvar=self.CheckVar, value="Basics",
                                      position=len(self.liste_ana)*2 - 1))
        self.liste_ana[len(self.liste_ana) - 1].grid(sticky="nsew")
        self.liste_ana[len(self.liste_ana) - 1].bind("<Enter>", lambda a: self.HW.change_tmp_message(
            self.Messages["Analyses4"].format(self.Vid.Scale[1])))
        self.liste_ana[len(self.liste_ana) - 1].bind("<Leave>", self.HW.remove_tmp_message)

        bouton_extend_T = Button(Liste_analyses, text=self.Messages["Analyses_B1"], command=self.extend_glob_thresh, **Color_settings.My_colors.Button_Base)
        bouton_extend_T.grid(row=(len(self.liste_ana) - 1)*2, column=1, sticky="nswe")
        bouton_extend_T.bind("<Enter>", lambda a: self.HW.change_tmp_message(self.Messages["Analyses5"]))
        bouton_extend_T.bind("<Leave>", self.HW.remove_tmp_message)

        Canvas(Liste_analyses, height=1, **Color_settings.My_colors.Frame_Base).grid(row=len(self.liste_ana)*2, columnspan=2)

        self.liste_ana.append(
            Class_rows_analyses.Row_Ana(main=self, parent=Liste_analyses, checkvar=self.CheckVar, value="Exploration",
                                        position=len(self.liste_ana)*2 - 1))
        self.liste_ana[len(self.liste_ana) - 1].grid(sticky="nsew")
        self.liste_ana[len(self.liste_ana) - 1].bind("<Enter>", lambda a: self.HW.change_tmp_message(
            self.Messages["Analyses10"].format(self.Vid.Scale[1])))
        self.liste_ana[len(self.liste_ana) - 1].bind("<Leave>", self.HW.remove_tmp_message)


        bouton_extend_E = Button(Liste_analyses, text=self.Messages["Analyses_B1"], command=self.extend_glob_explo, **Color_settings.My_colors.Button_Base)
        bouton_extend_E.grid(row=len(self.liste_ana)*2 - 1, column=1, sticky="nswe")
        bouton_extend_E.bind("<Enter>", lambda a: self.HW.change_tmp_message(self.Messages["Analyses9"]))
        bouton_extend_E.bind("<Leave>", self.HW.remove_tmp_message)

        Canvas(Liste_analyses, height=1, **Color_settings.My_colors.Frame_Base).grid(row=len(self.liste_ana) * 2, columnspan=2)

        self.liste_ana.append(
            Class_rows_analyses.Row_Ana(main=self, parent=Liste_analyses, checkvar=self.CheckVar, value="InterInd",
                                      position=len(self.liste_ana)*2 - 1))
        self.liste_ana[len(self.liste_ana) - 1].grid(sticky="nsew")
        self.liste_ana[len(self.liste_ana) - 1].bind("<Enter>", lambda a: self.HW.change_tmp_message(
            self.Messages["Analyses7"].format(self.Vid.Scale[1])))
        self.liste_ana[len(self.liste_ana) - 1].bind("<Leave>", self.HW.remove_tmp_message)

        bouton_extend_I = Button(Liste_analyses, text=self.Messages["Analyses_B1"], command=self.extend_glob_inter, **Color_settings.My_colors.Button_Base)
        bouton_extend_I.grid(row=len(self.liste_ana)*2 - 1,column=1, sticky="nswe")
        bouton_extend_I.bind("<Enter>", lambda a: self.HW.change_tmp_message(self.Messages["Analyses11"]))
        bouton_extend_I.bind("<Leave>", self.HW.remove_tmp_message)

        Canvas(Liste_analyses, height=1, **Color_settings.My_colors.Frame_Base).grid(row=len(self.liste_ana) * 2, columnspan=2)

        self.liste_ana.append(
            Class_rows_analyses.Row_Ana(main=self, parent=Liste_analyses, checkvar=self.CheckVar, value="Spatial",
                                      position=len(self.liste_ana)*2 - 1))
        self.liste_ana[len(self.liste_ana) - 1].grid(sticky="nsew")
        self.liste_ana[len(self.liste_ana) - 1].bind("<Enter>", lambda a: self.HW.change_tmp_message(
            self.Messages["Analyses6"].format(self.Vid.Scale[1])))
        self.liste_ana[len(self.liste_ana) - 1].bind("<Leave>", self.HW.remove_tmp_message)


        Canvas(Liste_analyses, height=1, **Color_settings.My_colors.Frame_Base).grid(row=len(self.liste_ana) * 2, columnspan=2)

        self.liste_ana.append(
            Class_rows_analyses.Row_Ana(main=self, parent=Liste_analyses, checkvar=self.CheckVar, value="Sequences",
                                      position=len(self.liste_ana)*2 - 1))
        self.liste_ana[len(self.liste_ana) - 1].grid(sticky="nsew")
        self.liste_ana[len(self.liste_ana) - 1].bind("<Enter>", lambda a: self.HW.change_tmp_message(self.Messages["Analyses14"]))
        self.liste_ana[len(self.liste_ana) - 1].bind("<Leave>", self.HW.remove_tmp_message)


        # Navigation buttons
        self.bouton_save = Button(self.User_params_cont, text=self.Messages["Control3"],
                                  command=self.save_And_quit, **Color_settings.My_colors.Button_Base)
        self.bouton_save.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.bouton_save.grid(row=8, column=0, sticky="we")

        self.bouton_saveNext = Button(self.User_params_cont, text=self.Messages["Control7"],
                                      command=lambda: self.save_And_quit(follow=True), **Color_settings.My_colors.Button_Base)
        self.bouton_saveNext.config(background=Color_settings.My_colors.list_colors["Validate"],
                                fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.bouton_saveNext.grid(row=8, column=1, sticky="we")


    def deform(self):
        newWindow = Toplevel(self.master)
        interface = Interface_deformation.Deformation(parent=newWindow, Video_file= self.Vid, main_frame=self)

    def extend_glob_smooth(self):
        """ Extend the parameters of smoothong filter to other videos"""
        newWindow = Toplevel(self.parent.master)
        if self.Check_Smoothed.get():
            val = [self.window_length, self.polyorder]
        else:
            val = [0, 0]
        interface = Interface_extend.Extend(parent=newWindow, value=val, boss=self.main_frame, Video_file=self.Vid,
                                            type="analyses_smooth")

    def extend_glob_thresh(self):
        """ Extend the movement threshold to other videos"""
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Calc_speed.seuil_movement,
                                            boss=self.main_frame, Video_file=self.Vid, type="analyses_thresh")

    def extend_glob_explo(self):
        """Extend the exploration parameters to other videos"""
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Infos_explo, boss=self.main_frame,
                                            Video_file=self.Vid, type="analyses_explo")

    def extend_glob_inter(self):
        """Extend the interactions parameters to other videos"""
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Infos_inter, boss=self.main_frame,
                                            Video_file=self.Vid, type="analyses_inter")
    def extend_deform(self):
        """Extend the deformation parameters to other videos"""
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Vid.Analyses[4].copy(), boss=self.main_frame,
                                            Video_file=self.Vid, type="analyses_deform")
    def on_frame_conf(self, *arg):
        # Change canvas' size according to the main window size
        self.Liste_analyses.configure(scrollregion=self.Liste_analyses.bbox("all"))

    def change_type_coos(self, modif=False, *arg):
        # Change displayed coordiantes from smoothed to brut ones
        self.load_frame = Class_loading_Frame.Loading(self)  # Progression bar
        self.load_frame.grid()
        self.load_frame.show_load(0)
        self.Coos = self.Coos_brutes.copy()
        if len(self.Vid.Analyses[4][0]) > 0:
            self.Coos=Functions_deformation.deform_coos(self.Coos, self.Vid.Analyses[4][0])
        if self.Check_Smoothed.get():
            self.Coos = self.smooth_coos(self.Coos)
        self.smooth_button()

        mask = Function_draw_mask.draw_mask(self.Vid)
        Arenas, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.Arenas = Function_draw_mask.Organise_Ars(Arenas)

        if modif:
            self.modif_image()

        self.load_frame.destroy()


    def deform_coos(self, coos):
        if self.Check_Smoothed.get():
            progress=0.5
        else:
            progress=1

        if len(self.Vid.Analyses[4][0])>0:
            coos=Functions_deformation.deform_coos(self.Coos, self.Vid.Analyses[4][0])

        return(coos)

    def smooth_coos(self, coos):
        if len(self.Vid.Analyses[4][0]) > 0:
            progress = 0.5
        else:
            progress = 0
        """Apply the savgol_filter to smoothen the trajectories"""
        for ind in range(self.NB_ind):
            self.load_frame.show_load(progress+((ind / self.NB_ind) * (1-progress)))
            ind_coo = [[np.nan if val == -1000 else val for val in row] for row in coos[ind]]
            ind_coo = np.array(ind_coo, dtype=np.float)
            for column in range(2):
                Pos_NA = np.where(np.isnan(ind_coo[:, column]))[0]
                debuts = [0]
                fins = []
                if len(Pos_NA) > 0:
                    diff = ([Pos_NA[ele] - Pos_NA[ele - 1] for ele in range(1, len(Pos_NA))])
                    fins.append(Pos_NA[0])
                    for moment in range(len(diff)):
                        if diff[moment] > 1:
                            fins.append(Pos_NA[moment + 1])
                            debuts.append(Pos_NA[moment])
                    debuts.append(Pos_NA[len(Pos_NA) - 1])
                    fins.append(len(ind_coo[:, column]))

                    for seq in range(len(debuts)):
                        if len(ind_coo[(debuts[seq] + 1):fins[seq], column]) >= self.window_length:
                            ind_coo[(debuts[seq] + 1):fins[seq], column] = savgol_filter(
                                ind_coo[(debuts[seq] + 1):fins[seq], column], self.window_length,
                                self.polyorder, deriv=0, delta=1.0, axis=- 1,
                                mode='interp', cval=0.0)


                else:
                    ind_coo[:, column] = savgol_filter(ind_coo[:, column],
                                                       self.window_length,
                                                       self.polyorder, deriv=0, delta=1.0, axis=- 1,
                                                       mode='interp', cval=0.0)


            ind_coo[np.where(np.isnan(ind_coo))] = -1000
            ind_coo = ind_coo.astype(dtype=float)
            coos[ind] = ind_coo.copy()
        return(coos)

    def smooth_button(self):
        # Change the state of the button for changing the parameters of smooth filter
        if self.Check_Smoothed.get() == 1:# If the user chose to apply a smoothing parameter
            self.Button_Smoothed_param.config(state="normal")
        else:
            self.Button_Smoothed_param.config(state="disable")

    def resize(self, event):
        #Adapt the size of the Scrollbar to the size of the window
        self.Scrollbar.refresh()

    def resize2(self, event):
        #Change the image according to the size of the window
        self.modif_image()

    def save_And_quit(self, follow=False):
        #Save the parameters and close the window
        self.save()
        if follow:# If the user want to see the next video
            liste_tracked = [Vid for Vid in self.Video_liste if Vid.Tracked]
            next = [Id + 1 for Id, Video in enumerate(liste_tracked) if Video == self.Vid][0]
            if next < (len(liste_tracked)):
                self.choice_menu.change_vid(liste_tracked[next].User_Name)
                return
        self.End_of_window()

    def End_of_window(self):
        self.unbind_all("<Button-1>")
        self.Vid_Lecteur.proper_close()
        self.grab_release()
        self.User_params_cont.grid_forget()
        self.User_params_cont.destroy()
        self.HW.grid_forget()
        self.HW.destroy()
        self.main_frame.return_main()
        del self

    def save(self):
        # Save the parameters
        self.Vid.Analyses[0] = self.Calc_speed.seuil_movement  # We save the movement threshold

        # Pickle does not accept tkinter DoubleVar:
        for Ar in self.Calc_speed.Areas:
            for shape in Ar:
                shape[2] = float(shape[2].get())
        self.Vid.Analyses[1] = copy.deepcopy(self.Calc_speed.Areas)
        if self.Check_Smoothed.get():
            self.Vid.Smoothed = [self.window_length, self.polyorder]  # We save smooth
        else:
            self.Vid.Smoothed = [0, 0]  # We save smooth

        self.Vid.Analyses[2] = self.Infos_explo  # We save the movement threshold
        self.Vid.Analyses[3] = self.Infos_inter  # We save the movement threshold

    #What happen when the user interacts with the frame canvas
    def pressed_can(self, Pt, *args):
        pass

    def moved_can(self, Pt, Shift):
        pass

    def released_can(self, Pt):
        pass

    def load_Vid(self, new_Vid):
        if new_Vid != None:
            self.Vid = new_Vid

        # Frame organization
        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=100)

        #Find the arenas defined by the user
        mask = Function_draw_mask.draw_mask(self.Vid)
        Arenas, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.Arenas = Function_draw_mask.Organise_Ars(Arenas)

        try:
            self.Calc_speed.seuil_movement = self.Vid.Analyses[0]
            if len(self.Vid.Analyses[1]) > 0:
                self.Calc_speed.Areas = copy.deepcopy(self.Vid.Analyses[1])
                # Pickle does not accept tkinter DoubleVar:
                for Ar in self.Calc_speed.Areas:
                    for shape in Ar:
                        shape[2] = DoubleVar(value=shape[2])
        except Exception as e:
            print(e)
            pass

        try:
            self.Infos_explo = self.Vid.Analyses[2]
        except:
            pass

        try:
            self.Infos_inter = self.Vid.Analyses[3]
        except:
            pass

        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=0)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Vid_Lecteur.speed.set(self.speed)
        self.Vid_Lecteur.change_speed()
        self.Scrollbar = self.Vid_Lecteur.Scrollbar


        if self.Vid.Stab[0]:
            self.prev_pts = self.Vid.Stab[1]

        if self.Vid.Cropped[0]:
            self.to_sub = round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every))
        else:
            self.to_sub = 0

        self.Coos_brutes, _ = CoosLS.load_coos(self.Vid, location=self)
        self.Coos=self.Coos_brutes.copy()
        self.NB_ind = len(self.Vid.Identities)




        if self.Vid.Smoothed[0] != 0: #If the video was already associated with video smoothing
            self.window_length = self.Vid.Smoothed[0]
            self.polyorder = self.Vid.Smoothed[1]
            self.Check_Smoothed.set(1)
            self.change_type_coos()
        elif len(self.Vid.Analyses[4][0])>0:
            self.change_type_coos()

        # We show the first frame:
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

        self.Check_Bs = []
        self.one_every = self.Vid_Lecteur.one_every

    def redo_reader(self):
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=0)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Vid_Lecteur.speed.set(self.speed)
        self.Vid_Lecteur.change_speed()

        self.Scrollbar = self.Vid_Lecteur.Scrollbar

        if self.Vid.Stab[0]:
            self.prev_pts = self.Vid.Stab[1]

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

    def modif_param_smoothed(self):
        #Open a new window to change the smoothing parameters
        newWindow = Toplevel(self.parent.master)
        interface = Interface_smooth_param.Modify(parent=newWindow, boss=self)


    def show_all_com(self):
        #This show/hide the complete trajectories of the targets
        if self.show_all:
            self.show_all = False
            self.bouton_show_all_traj.config(**Color_settings.My_colors.Button_Base)
        else:
            self.show_all = True
            self.bouton_show_all_traj.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.modif_image()

    def modif_image(self, img=[], **args):
        #Draw the illustration of the analyses on the top of the image
        if self.Vid.Cropped[0]:
            to_remove = round(round((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every))
        else:
            to_remove = 0

        if len(img) <= 10:
            new_img = np.copy(self.last_empty)
        else:
            self.last_empty = img
            new_img = np.copy(img)


        # Image stabilisation
        if self.Vid.Stab[0]:
            new_img = (Class_stabilise.find_best_position(Vid=self.Vid, Prem_Im=self.Vid_Lecteur.Prem_image_to_show,
                                                          frame=new_img, show=False, prev_pts=self.prev_pts))


        if len(self.Vid.Analyses[4][0])>0:
            new_img =  cv2.warpPerspective(new_img, self.Vid.Analyses[4][0], (new_img.shape[1], new_img.shape[0]))

        for ind in range(self.NB_ind): #For each target
            color = self.Vid.Identities[ind][2]
            if not self.show_all:
                #We draw the trajectories:
                for prev in range(min(int(self.tail_size.get() * self.Vid.Frame_rate[1]),
                                      int(self.Scrollbar.active_pos - to_remove))):
                    if int(self.Scrollbar.active_pos - prev) >= round(
                            ((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every)) and int(
                            self.Scrollbar.active_pos) <= round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every):
                        if self.Coos[ind,int(self.Scrollbar.active_pos - 1 - prev - to_remove),0] != -1000 and \
                                self.Coos[ind,int(self.Scrollbar.active_pos - prev - to_remove),0] != -1000:
                            TMP_tail_1 = (int(float(
                                self.Coos[ind,int(self.Scrollbar.active_pos - 1 - prev - to_remove),0])),
                                          int(float(self.Coos[ind,
                                                        int(self.Scrollbar.active_pos - 1 - prev - to_remove),1])))

                            TMP_tail_2 = (
                            int(float(self.Coos[ind,int(self.Scrollbar.active_pos - prev - to_remove),0])),
                            int(float(self.Coos[ind,int(self.Scrollbar.active_pos - prev - to_remove),1])))

                            new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color,
                                               max(int(3 * self.Vid_Lecteur.ratio), 1))
            else:
                for prev in range(1,int((self.Vid.Cropped[1][1]-self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)):
                    if self.Coos[ind, int(((self.Vid.Cropped[1][
                        1]) / self.Vid_Lecteur.one_every) - 1 - prev - self.to_sub), 0] != -1000 and \
                            self.Coos[
                                ind, round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) - prev - self.to_sub,
                                0] != -1000:
                        TMP_tail_1 = (
                            int(self.Coos[ind, round(
                                (self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) - 1 - prev - self.to_sub), 0]),
                            int(self.Coos[ind, round(
                                (self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) - 1 - prev - self.to_sub), 1]))

                        TMP_tail_2 = (
                            int(self.Coos[ind, round(
                                (self.Vid.Cropped[1][1]/ self.Vid_Lecteur.one_every) - prev - self.to_sub), 0]),
                            int(self.Coos[ind, round(
                                (self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) - prev - self.to_sub), 1]))

                        new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color,
                                           max(int(3 * self.Vid_Lecteur.ratio), 1))


        Ind_pts = []
        self.img_no_shapes = new_img
        #We draw a circle for each target with an highligh on the selected one
        if self.Scrollbar.active_pos >= round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every) and self.Scrollbar.active_pos <= round(
                round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every)):
            for ind in range(self.NB_ind):
                #If we are watching interactions analyses
                if self.CheckVar.get() == "InterInd":
                    Ind_pts.append(self.Coos[ind,self.Scrollbar.active_pos - to_remove])

                color = self.Vid.Identities[ind][2]
                if self.Coos[ind,self.Scrollbar.active_pos - to_remove,0] != -1000:
                    if self.highlight == ind:
                        new_img = cv2.circle(new_img, (
                        int(float(self.Coos[ind,self.Scrollbar.active_pos - to_remove,0])),
                        int(float(self.Coos[ind,self.Scrollbar.active_pos - to_remove,1]))),
                                             radius=max(int(5 * self.Vid_Lecteur.ratio), 2), color=(0, 0, 0),
                                             thickness=-1)
                        new_img = cv2.circle(new_img, (
                        int(float(self.Coos[ind,self.Scrollbar.active_pos - to_remove,0])),
                        int(float(self.Coos[ind,self.Scrollbar.active_pos - to_remove,1]))),
                                             radius=max(int(2 * self.Vid_Lecteur.ratio), 3), color=(255, 255, 255),
                                             thickness=-1)

                    new_img = cv2.circle(new_img, (
                    int(float(self.Coos[ind,self.Scrollbar.active_pos - to_remove,0])),
                    int(float(self.Coos[ind,self.Scrollbar.active_pos - to_remove,1]))),
                                         radius=max(int(4 * self.Vid_Lecteur.ratio), 1), color=color, thickness=-1)
                    # Show speed:
                    if self.CheckVar.get() == "Basics" and \
                            self.Coos[ind,self.Scrollbar.active_pos - to_remove - 1,0] != -1000 and (
                    self.Scrollbar.active_pos) >= round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every) + 1):
                        speed = self.Calc_speed.calculate_speed(self, ind)
                        if speed <= self.Calc_speed.seuil_movement:
                            col_fond = (255, 0, 0)
                        else:
                            col_fond = (0, 255, 0)

                        if not isinstance(speed, str):
                            cv2.putText(new_img, str(round(speed, 2)), (
                            int(float(self.Coos[ind,self.Scrollbar.active_pos - to_remove,0])) + 5,
                            int(float(self.Coos[ind,self.Scrollbar.active_pos - to_remove,1])) + 5),
                                        cv2.FONT_HERSHEY_SIMPLEX, max(0.5, self.Vid_Lecteur.ratio), col_fond,
                                        max(2, int(self.Vid_Lecteur.ratio * 7)))
                            cv2.putText(new_img, str(round(speed, 2)), (
                            int(float(self.Coos[ind,self.Scrollbar.active_pos - to_remove,0])) + 5,
                            int(float(self.Coos[ind,self.Scrollbar.active_pos - to_remove,1])) + 5),
                                        cv2.FONT_HERSHEY_SIMPLEX, max(0.5, self.Vid_Lecteur.ratio), color,
                                        max(1, int(self.Vid_Lecteur.ratio * 3)))

            self.img_no_shapes = new_img

            if self.CheckVar.get() == "InterInd":#If we are watching interactions analyses
                for Cur_ar in range(len(self.Vid.Track[1][6])):
                    TMP_Ind_pts = [Ind_pts[idx] for idx, info in enumerate(self.Vid.Identities) if
                                   info[0] == Cur_ar and Ind_pts[idx][0] != -1000]
                    if self.Vid.Track[1][6][Cur_ar] > 1 and len(TMP_Ind_pts)>1:


                        new_img, dist, central = self.Calc_speed.calculate_interind_dist(Pts=TMP_Ind_pts,
                                                                                         Scale=float(self.Vid.Scale[0]),
                                                                                         draw=True, img=new_img,
                                                                                         thick=max(1,
                                                                                                   int(self.Vid_Lecteur.ratio * 3)))


                        if dist != "NA":
                            cv2.putText(new_img, str(round(dist, 3)), central, cv2.FONT_HERSHEY_SIMPLEX,
                                        max(0.5, self.Vid_Lecteur.ratio), (0, 0, 0),
                                        max(2, int(self.Vid_Lecteur.ratio * 5)))
                            cv2.putText(new_img, str(round(dist, 3)), central, cv2.FONT_HERSHEY_SIMPLEX,
                                        max(0.5, self.Vid_Lecteur.ratio), (175, 0, 0),
                                        max(1, int(self.Vid_Lecteur.ratio * 3)))


            # If we are watching spacial analyses (i.e. elements of interest)
            if self.CheckVar.get() == "Spatial" and self.Scrollbar.active_pos >= round(
                    ((self.Vid.Cropped[1][0] - 1) / self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= round(
                    ((self.Vid.Cropped[1][1] - 1) / self.Vid_Lecteur.one_every) + 1):
                new_img = self.draw_shapes(np.copy(self.img_no_shapes), to_remove)

            # If we are watching exploration analyses (i.e. elements of interest)
            if self.CheckVar.get() == "Exploration" and self.Scrollbar.active_pos >= round(
                    ((self.Vid.Cropped[1][0] - 1) / self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= round(
                    ((self.Vid.Cropped[1][1] - 1) / self.Vid_Lecteur.one_every) + 1):
                new_img = self.draw_explo(np.copy(self.img_no_shapes), to_remove)
        #We finally display the image

        for ind in range(len(self.Coos)):
            if self.Scrollbar.active_pos - min(int(self.tail_size.get() * self.Vid.Frame_rate[1]),
                                               int(self.Scrollbar.active_pos - self.to_sub)) == round(
                    self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every) or self.show_all:
                if self.Coos[ind][0][0] != -1000:
                    new_img = cv2.circle(new_img, (int(self.Coos[ind][0][0]), int(self.Coos[ind][0][1])),
                                         radius=max(int(2 * self.Vid_Lecteur.ratio), 1), color=(0, 255, 0),
                                         thickness=-1)

            if self.Scrollbar.active_pos == round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) or self.show_all:
                if self.Coos[ind][len(self.Coos[0]) - 1][0] != -1000:
                    new_img = cv2.circle(new_img, (
                    int(self.Coos[ind][len(self.Coos[0]) - 1][0]), int(self.Coos[ind][len(self.Coos[0]) - 1][1])),
                                         radius=max(int(2 * self.Vid_Lecteur.ratio), 1), color=(183, 28, 28),
                                         thickness=-1)

        self.Vid_Lecteur.afficher_img(new_img)

    def create_overlay(self, img):
        #We crate an image that will be used as a transparent in which we see all the elements of interest
        overlay = np.zeros([img.shape[0], img.shape[1], 3], np.uint8)
        for Ar in range(len(self.Arenas)):
            for shape in self.Calc_speed.Areas[Ar]:
                if shape[0] == "Point":
                    cv2.circle(img, shape[1][0], max(2, int(self.Vid_Lecteur.ratio * 5)), (0, 0, 0), -1)
                    cv2.circle(img, shape[1][0], max(1, int(self.Vid_Lecteur.ratio * 3)), (0, 0, 175), -1)
                    cv2.circle(img, shape[1][0], int(round(float(shape[2].get()) * float(self.Vid.Scale[0]))),
                               (0, 0, 100), max(1, int(self.Vid_Lecteur.ratio * 3)))
                    overlay = cv2.circle(overlay, shape[1][0],
                                         int(round(float(shape[2].get()) * float(self.Vid.Scale[0]))), (0, 0, 100), -1)

                if shape[0] == "Line":
                    for pt in shape[1]:
                        cv2.circle(img, pt, max(2, int(self.Vid_Lecteur.ratio * 5)), (0, 0, 0), -1)
                        cv2.circle(img, pt, max(1, int(self.Vid_Lecteur.ratio * 3)), (175, 0, 175), -1)
                    if len(shape[1]) > 1:
                        cv2.line(img, shape[1][0], shape[1][1], color=(150, 0, 150),
                                 thickness=max(1, int(self.Vid_Lecteur.ratio * 3)))

                if shape[0] == "All_borders":
                    img = cv2.drawContours(img, [self.Arenas[Ar]], -1, (255, 0, 0),
                                           max(1, int(self.Vid_Lecteur.ratio * 3)))

                    if shape[2].get() > 0:
                        empty = np.zeros((img.shape[0], img.shape[1]), np.uint8)
                        border = cv2.drawContours(np.copy(empty), [self.Arenas[Ar]], -1, (255, 255, 255),
                                                  int(round(shape[2].get() * float(self.Vid.Scale[0]) * 2)))
                        area = cv2.drawContours(np.copy(empty), [self.Arenas[Ar]], -1, (255, 255, 255), -1)
                        empty = cv2.bitwise_and(border, border, mask=area)
                        inside_border, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                        img = cv2.drawContours(img, inside_border, -1, (150, 0, 0),
                                               max(1, int(self.Vid_Lecteur.ratio * 3)))
                        overlay = cv2.drawContours(overlay, inside_border, -1, (255, 0, 0), -1)

                if shape[0] == "Borders":
                    for bord in shape[1]:
                        cv2.line(img, bord[0], bord[1], color=(255, 0, 0),
                                 thickness=max(1, int(self.Vid_Lecteur.ratio * 3)))

                    empty = np.zeros((img.shape[0], img.shape[1]), np.uint8)
                    border = np.copy(empty)

                    for bord in shape[1]:
                        border = cv2.line(border, bord[0], bord[1], color=(255, 0, 0),
                                          thickness=max(1, int(self.Vid_Lecteur.ratio * 3)))
                    cnts, _ = cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                    border = cv2.drawContours(border, cnts, -1, (255, 255, 255),
                                              int(round(shape[2].get() * float(self.Vid.Scale[0]) * 2)))
                    area = cv2.drawContours(np.copy(empty), [self.Arenas[Ar]], -1, (255, 255, 255), -1)
                    empty = cv2.bitwise_and(border, border, mask=area)
                    inside_border, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    img = cv2.drawContours(img, inside_border, -1, (150, 0, 0), max(1, int(self.Vid_Lecteur.ratio * 3)))
                    overlay = cv2.drawContours(overlay, inside_border, -1, (255, 0, 0), -1)

                if shape[0] == "Ellipse":
                    if len(shape[1]) > 1:
                        Function_draw_mask.Draw_elli(img, [po[0] for po in shape[1]], [po[1] for po in shape[1]],
                                                     (0, 255, 0), thick=max(1, int(self.Vid_Lecteur.ratio * 3)))
                        Function_draw_mask.Draw_elli(overlay, [po[0] for po in shape[1]], [po[1] for po in shape[1]],
                                                     (0, 255, 0), thick=-1)

                if shape[0] == "Rectangle":
                    if len(shape[1]) > 1:
                        Function_draw_mask.Draw_rect(img, [po[0] for po in shape[1]], [po[1] for po in shape[1]],
                                                     color=(0, 75, 75), thick=max(1, int(self.Vid_Lecteur.ratio * 3)))
                        Function_draw_mask.Draw_rect(overlay, [po[0] for po in shape[1]], [po[1] for po in shape[1]],
                                                     color=(0, 100, 100), thick=-1)

                if shape[0] == "Polygon":
                    if len(shape[1]) > 1:
                        Function_draw_mask.Draw_Poly(img, [po[0] for po in shape[1]], [po[1] for po in shape[1]],
                                                     (75, 75, 0), thick=max(1, int(self.Vid_Lecteur.ratio * 3)))
                        Function_draw_mask.Draw_Poly(overlay, [po[0] for po in shape[1]], [po[1] for po in shape[1]],
                                                     (150, 150, 0), thick=-1)

        grey = cv2.cvtColor(overlay, cv2.COLOR_BGR2GRAY)
        self.mask = np.where(grey > 0)
        self.overlay = overlay

    def draw_shapes(self, img, to_remove):
        self.create_overlay(img)

        # First the ones that will not appear transparent:
        for Ar in range(len(self.Arenas)):
            for shape in self.Calc_speed.Areas[Ar]:
                if shape[0] == "Point":
                    for ind in [idx for idx,ident in enumerate(self.Vid.Identities) if ident[0]==Ar]:
                        if self.Coos[ind,self.Scrollbar.active_pos - to_remove,0] != -1000:
                            center = self.Coos[ind,self.Scrollbar.active_pos - to_remove]
                            center = [float(val) for val in center]
                            cv2.line(img, (int(center[0]), int(center[1])), shape[1][0],
                                     self.Vid.Identities[ind][2],
                                     max(1, int(self.Vid_Lecteur.ratio * 3)))
                            dist = math.sqrt((float(center[0]) - shape[1][0][0]) ** 2 + (
                                    float(center[1]) - shape[1][0][1]) ** 2) / float(self.Vid.Scale[0])
                            cv2.putText(img, str(round(dist, 3)), (
                                int((float(center[0]) + shape[1][0][0]) / 2),
                                int((float(center[1]) + shape[1][0][1]) / 2)),
                                        cv2.FONT_HERSHEY_DUPLEX, max(0.5, self.Vid_Lecteur.ratio),
                                        color=(0, 0, 0), thickness=max(2, int(self.Vid_Lecteur.ratio * 5)))

                            cv2.putText(img, str(round(dist, 3)), (
                                int((float(center[0]) + shape[1][0][0]) / 2),
                                int((float(center[1]) + shape[1][0][1]) / 2)),
                                        cv2.FONT_HERSHEY_DUPLEX, max(0.5, self.Vid_Lecteur.ratio),
                                        color=self.Vid.Identities[ind][2],
                                        thickness=max(1, int(self.Vid_Lecteur.ratio * 3)))
                if shape[0] == "Line":
                    for ind in [idx for idx,ident in enumerate(self.Vid.Identities) if ident[0]==Ar]:
                        if self.Coos[ind,self.Scrollbar.active_pos - to_remove,0] != -1000:
                            center = self.Coos[ind,self.Scrollbar.active_pos - to_remove]
                            center = [int(float(center[0])), int(float(center[1]))]
                            dist, proj = Functions_Analyses_Speed.calculate_dist_one_pt_Line(Ligne=shape[1], Pt=center,
                                                                                   Scale=float(self.Vid.Scale[0]),
                                                                                   get_proj=True)
                            proj = [int(float(proj[0])), int(float(proj[1]))]
                            cv2.line(img, (int(center[0]), int(center[1])), proj,
                                     self.Vid.Identities[ind][2],
                                     max(1, int(self.Vid_Lecteur.ratio * 3)))
                            cv2.putText(img, str(round(dist, 3)), (int((float(center[0]) * 0.3 + proj[0] * 0.7)),
                                                                   int((float(center[1]) * 0.3 + proj[1] * 0.7))),
                                        cv2.FONT_HERSHEY_DUPLEX, max(0.5, self.Vid_Lecteur.ratio),
                                        color=(0, 0, 0), thickness=max(1, int(self.Vid_Lecteur.ratio * 5)))

                            cv2.putText(img, str(round(dist, 3)), (int((float(center[0]) * 0.3 + proj[0] * 0.7)),
                                                                   int((float(center[1] * 0.3) + proj[1] * 0.7))),
                                        cv2.FONT_HERSHEY_DUPLEX, max(0.5, self.Vid_Lecteur.ratio),
                                        color=self.Vid.Identities[ind][2],
                                        thickness=max(1, int(self.Vid_Lecteur.ratio * 3)))

        #Add the transparent elements
        img[self.mask] = cv2.addWeighted(img, 0.5, self.overlay, 0.5, 0)[self.mask]
        return (img)

    def draw_explo(self, img, to_remove):
        if self.Infos_explo[0] == 0:#If we use the modern method
            #We draw a circle above the targets to show how much space we consider they are exploring
            radius = math.sqrt((float(self.Infos_explo[1])) / math.pi)

            for Ar in range(len(self.Arenas)):
                empty = np.zeros((img.shape[0], img.shape[1], 1), np.uint8)
                for fish in [idx for idx,info in enumerate(self.Vid.Identities) if info[0]==Ar]:
                    pt = self.Coos[fish,self.Scrollbar.active_pos - to_remove]

                    if pt[0] != -1000:
                        cv2.circle(empty, (int(float(pt[0])), int(float(pt[1]))),
                                   int(radius * float(self.Vid.Scale[0])), (1), -1)

                mask_glob = Function_draw_mask.draw_mask(self.Vid)
                mask = np.zeros((img.shape[0], img.shape[1], 1), np.uint8)
                mask = cv2.drawContours(mask, [self.Arenas[Ar]], -1, (255), -1)
                mask = cv2.bitwise_and(mask, mask_glob)
                empty = cv2.bitwise_and(mask, empty)

                bool_mask = empty.astype(bool)
                empty = cv2.cvtColor(empty, cv2.COLOR_GRAY2RGB)
                empty[:, :, 0] = empty[:, :, 0] * 255

                alpha = 0.5
                img[bool_mask] = cv2.addWeighted(img, alpha, empty, 1 - alpha, 0)[bool_mask]
            return (img)


        elif self.Infos_explo[0] == 1:#If we use a mesh (rectangular)
            # We draw the mesh
            largeur = math.sqrt(float(self.Infos_explo[1]) * float(self.Vid.Scale[0]) ** 2)
            for Ar in range(len(self.Arenas)):
                nb_squares_v = math.ceil((max(self.Arenas[Ar][:, :, 0]) - min(self.Arenas[Ar][:, :, 0])) / largeur)
                nb_squares_h = math.ceil((max(self.Arenas[Ar][:, :, 1]) - min(self.Arenas[Ar][:, :, 1])) / largeur)

                max_x = min(self.Arenas[Ar][:, :, 0]) + nb_squares_v * (largeur)
                max_y = min(self.Arenas[Ar][:, :, 1]) + nb_squares_h * (largeur)

                decal_x = (max_x - max(self.Arenas[Ar][:, :, 0])) / 2
                decal_y = (max_y - max(self.Arenas[Ar][:, :, 1])) / 2

                for vert in range(nb_squares_v + 1):
                    img = cv2.line(img, pt1=(int(min(self.Arenas[Ar][:, :, 0]) - decal_x + vert * (largeur)),
                                             int(min(self.Arenas[Ar][:, :, 1]) - decal_y)), pt2=(
                        int(min(self.Arenas[Ar][:, :, 0]) - decal_x + vert * (largeur)),
                        int(max(self.Arenas[Ar][:, :, 1]) + decal_y)), color=(0, 0, 0),
                                   thickness=max(1, int(self.Vid_Lecteur.ratio * 3)))

                for horz in range(nb_squares_h + 1):
                    img = cv2.line(img, pt1=(int(min(self.Arenas[Ar][:, :, 0]) - decal_x),
                                             int(min(self.Arenas[Ar][:, :, 1]) - decal_y + horz * (largeur))),
                                   pt2=(int(max(self.Arenas[Ar][:, :, 0]) + decal_x),
                                        int(min(self.Arenas[Ar][:, :, 1]) - decal_y + horz * (largeur))),
                                   color=(0, 0, 0),
                                   thickness=max(1, int(self.Vid_Lecteur.ratio * 3)))
            return (img)

        elif self.Infos_explo[0] == 2:#If we use a mesh (circular)
            # We draw the mesh
            for Ar in range(len(self.Arenas)):
                M = cv2.moments(self.Arenas[Ar])
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

                max_size = max(
                    list(np.sqrt((self.Arenas[Ar][:, :, 0] - cX) ** 2 + (self.Arenas[Ar][:, :, 1] - cY) ** 2)))

                last_rad = math.sqrt((float(self.Infos_explo[1]) * float(self.Vid.Scale[0]) ** 2) / math.pi)
                last_nb = 1
                list_rads = [last_rad]
                list_nb = [1]
                list_angles = [[0]]

                while last_rad < max_size:
                    new_rad = ((math.sqrt(last_nb) + math.sqrt(self.Infos_explo[2] ** 2)) / math.sqrt(
                        last_nb)) * last_rad
                    new_nb = int(round((math.sqrt(last_nb) + math.sqrt(self.Infos_explo[2] ** 2)) ** 2))
                    cur_nb = new_nb - last_nb

                    list_nb.append(cur_nb)

                    one_angle = (2 * math.pi) / cur_nb
                    cur_angle = 0
                    tmp_angles = [0]
                    for angle in range(cur_nb):
                        cur_angle += one_angle
                        tmp_angles.append(cur_angle)

                    list_angles.append(tmp_angles)
                    list_rads.append(new_rad)

                    last_rad = new_rad
                    last_nb = new_nb

                for circle in range(len(list_rads)):
                    img = cv2.circle(img, (cX, cY), int(list_rads[circle]), (0, 0, 0),
                                     max(1, int(self.Vid_Lecteur.ratio * 3)))
                    if circle > 0:
                        for cur_angle in list_angles[circle]:
                            pt1 = (int(cX + math.cos(math.pi + cur_angle) * list_rads[circle - 1]),
                                   int(cY + math.sin(math.pi + cur_angle) * list_rads[circle - 1]))
                            pt2 = (int(cX + math.cos(math.pi + cur_angle) * list_rads[circle]),
                                   int(cY + math.sin(math.pi + cur_angle) * list_rads[circle]))
                            img = cv2.line(img, pt1, pt2, (0, 0, 0),
                                           max(1, int(self.Vid_Lecteur.ratio * 3)))  # We draw the limits
                img = cv2.circle(img, (cX, cY), int(last_rad), (0, 0, 0), max(1, int(self.Vid_Lecteur.ratio * 3)))

            return (img)
