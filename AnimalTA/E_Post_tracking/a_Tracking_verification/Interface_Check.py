from tkinter import *
import cv2
import numpy as np
from AnimalTA.E_Post_tracking.a_Tracking_verification import Interface_portion, Interpolate_all, Interface_extend_Check
from AnimalTA.E_Post_tracking.b_Analyses import Interface_sequences, Functions_Analyses_Speed
from AnimalTA.E_Post_tracking import Coos_loader_saver as CoosLS
from AnimalTA.A_General_tools import Class_change_vid_menu, Class_Lecteur, Function_draw_arenas as Dr, UserMessages, \
    User_help, Class_stabilise, Diverse_functions, Interface_extend, Color_settings, Message_simple_question as MsgBox, Small_info
from AnimalTA.B_Project_organisation import Interface_pretracking
import csv
import math
from tkinter import ttk
import copy
import shutil
import os
from functools import partial
import PIL
import pickle

class Lecteur(Frame):
    """This frame is used to show the results of the trackings.
    The user will also be able to:
     1. Correct tracking mistake
     2. Re-run part of the tracking with changes in the tracking parameters
     3. Add information about the identity of the targets and/or change their color representation
    """
    def __init__(self, parent, boss, main_frame, Vid, Video_liste, speed=0, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.main_frame=main_frame
        self.boss=boss
        self.Video_liste=Video_liste
        self.Vid=Vid
        self.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.show_all=False
        self.tail_size=DoubleVar()
        self.tail_size.set(5)
        self.table_heigh=14#Number of rows displayed in the table
        self.speed=speed
        self.Xpos = IntVar()
        self.Xpos.set(1)
        self.copied_cells=[]


        try:
            self.table_order=self.Vid.Table_order.copy()
        except:
            self.table_order=list(range(len(self.Vid.Identities)))#In which order should the columns of the table be shown
            self.Vid.Table_order=self.table_order.copy()

        self.column_catch = None#A column is being dragged

        self.windowed = False
        self.resize=False
        self.locked_view=False

        self.searching=False#Afre we searching for a specific column?

        #We save the state of the indviduals at the moment of opening:
        self.opening_Identities = copy.deepcopy(self.Vid.Identities)
        self.opening_Sequences = copy.deepcopy(self.Vid.Sequences)
        self.opening_Track= copy.deepcopy(self.Vid.Track[1][6])

        #Whether the individuals absent on the current frame should be hidden or not
        Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
        with open(Param_file, 'rb') as fp:
            Params = pickle.load(fp)
            self.hide_missing = Params["Check_hide_missing"]

        #Messages importation
        self.Messages = UserMessages.get_dict()

        self.clicked=False #The user clicked on a target
        self.moved = False #The user moved a target
        self.selected_ind = self.table_order[0] #Which is the selected target
        self.selected_rows= []#List of the rows selected by the user
        self.column_to_hide=[]#List of the individuals the user want's to hide
        self.column_to_show=[]#List of the individuals the user want's to see

        self.last_Ind_to_show=["Beg"]#Save the last size of the displayed table

        self.save_changes=[]#We will keep here the changes performed by the user so it can be Ctrl+Z

        #For options
        Option_frame=Frame(self, **Color_settings.My_colors.Frame_Base)
        Option_frame.grid(row=0,column=0)

        Option_frame.grid_rowconfigure(0,weight=1)
        Option_frame.grid_rowconfigure(1, weight=1)
        Option_frame.grid_columnconfigure(0,weight=1)
        Option_frame.grid_columnconfigure(1,weight=1)
        Option_frame.grid_columnconfigure(2, weight=1)

        # Video name and optionmenu to change the video:
        self.choice_menu= Class_change_vid_menu.Change_Vid_Menu(Option_frame, self.main_frame, self.Vid, "check", other_parent=self)
        self.choice_menu.grid(row=0, column=0, columnspan=6)


        #We add a menu for more choices of data removal:
        save_data=Button(Option_frame, text=self.Messages["Control31"], command=self.save_file,**Color_settings.My_colors.Button_Base)
        save_data.grid(row=1, column=0, sticky="nsew")
        Small_info.small_info(elem=save_data, parent=self, message=self.Messages["Control32"])


        #We add a menu for more choices or interpolation
        self.interpo_holder = StringVar()
        self.interpo_holder.set(self.Messages["Control33"])

        self.inter_options_list=[
                            self.Messages["Control34"],
                            "   -" + self.Messages["Control35"],
                            "   -" + self.Messages["Control36"],
                            "   -" + self.Messages["Control37"],
                            self.Messages["Control38"],
                            "    -" + self.Messages["Control35"],
                            "    -" + self.Messages["Control36"],
                            "    -" + self.Messages["Control37"],
                            "    -" + self.Messages["Control39"]
                            ]


        self.interpolate_options= OptionMenu(Option_frame, self.interpo_holder, *self.inter_options_list, command=self.interpolate_smth)
        self.interpolate_options["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
        self.interpolate_options.config(**Color_settings.My_colors.Button_Base)
        self.interpolate_options['menu'].entryconfigure(self.Messages["Control34"],
                                                        background=Color_settings.My_colors.list_colors["Table1"],
                                                        activebackground=Color_settings.My_colors.list_colors["Table1"],
                                                        foreground=Color_settings.My_colors.list_colors["Fg_T1"],
                                                        activeforeground=Color_settings.My_colors.list_colors["Fg_T1"])

        self.interpolate_options['menu'].entryconfigure(self.Messages["Control38"],
                                                        background=Color_settings.My_colors.list_colors["Table1"],
                                                        activebackground=Color_settings.My_colors.list_colors["Table1"],
                                                        foreground=Color_settings.My_colors.list_colors["Fg_T1"],
                                                        activeforeground=Color_settings.My_colors.list_colors["Fg_T1"])


        self.interpolate_options.grid(row=1, column=1, sticky="nsew")


        #We add a menu for more choices of data removal:
        self.remove_coo_holder = StringVar()
        self.remove_coo_holder.set(self.Messages["Control40"])

        self.remove_coo_options_list=[
                            self.Messages["Control34"],
                            "   -" + self.Messages["Control35"],
                            "   -" + self.Messages["Control36"],
                            "   -" + self.Messages["Control37"],
                            self.Messages["Control41"]
                            ]


        self.remove_coo_options= OptionMenu(Option_frame, self.remove_coo_holder, *self.remove_coo_options_list, command=self.remove_coos_smth)
        self.remove_coo_options["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
        self.remove_coo_options.config(**Color_settings.My_colors.Button_Base)
        self.remove_coo_options['menu'].entryconfigure(self.Messages["Control34"],
                                                        background=Color_settings.My_colors.list_colors["Table1"],
                                                        activebackground=Color_settings.My_colors.list_colors["Table1"],
                                                        foreground=Color_settings.My_colors.list_colors["Fg_T1"],
                                                        activeforeground=Color_settings.My_colors.list_colors["Fg_T1"])
        self.remove_coo_options.grid(row=1, column=2, sticky="nsew")
        Small_info.small_info_spe_menus(menu=self.remove_coo_options, entries=[4], parent=self, messages=[self.Messages["Control49"]])


        #We add a menu for more choices of data removal:
        self.remove_ind_holder = StringVar()
        self.remove_ind_holder.set(self.Messages["Control42"])

        self.remove_ind_options_list=[
                            self.Messages["Control35"],
                            self.Messages["Control36"],
                            self.Messages["Control37"],
                            self.Messages["Row20"]
                            ]
        self.remove_ind_options= OptionMenu(Option_frame, self.remove_ind_holder, *self.remove_ind_options_list, command=self.remove_inds_smth)
        self.remove_ind_options["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
        self.remove_ind_options.config(**Color_settings.My_colors.Button_Base)

        self.remove_ind_options.grid(row=1, column=3, sticky="nsew")


        #We add a menu for table organisation
        self.table_holder = StringVar()
        self.table_holder.set(self.Messages["Control43"])

        self.table_options_list=[self.Messages["Control44"],
                                 self.Messages["Short_Ctrl_W_Ch"],
                                 self.Messages["Control45"]]

        self.table_options= OptionMenu(Option_frame, self.table_holder, *self.table_options_list, command=self.table_smth)
        self.table_options["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
        self.table_options.config(**Color_settings.My_colors.Button_Base)
        Small_info.small_info_spe_menus(menu=self.table_options, entries=[1], parent=self, messages=[self.Messages["Control50"]])

        self.table_options.grid(row=1, column=4, sticky="nsew")


        #We add a menu for view
        self.view_holder = StringVar()
        self.view_holder.set(self.Messages["Mask2"])

        self.view_options_list=[self.Messages["Short_L_Ch"],
                                 self.Messages["Short_A_Ch"],
                                 self.Messages["Control46"],
                                 self.Messages["Short_Ctrl_Rclick_G"]]

        self.view_options= OptionMenu(Option_frame, self.view_holder, *self.view_options_list, command=self.view_smth)
        self.view_options["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
        self.view_options.config(**Color_settings.My_colors.Button_Base)
        Small_info.small_info_spe_menus(menu=self.view_options, entries=[0,1], parent=self,
                                        messages=[self.Messages["Control47"],
                                                  self.Messages["Control48"]])

        self.view_options.grid(row=1, column=5, sticky="nsew")



        #We load the Arenas shapes to be able to show the user there positions
        self.Arenas_with_holes = Dr.get_arenas(self.Vid)


        # Help user and parameters
        self.HW = User_help.Help_win(self.parent, default_message=self.Messages["Control9"],
                                     shortcuts={self.Messages["Short_Ctrl_Z"]:
                                                    self.Messages["Short_Ctrl_Z_Ch"],
                                                self.Messages["Short_Shift_clickT"]:
                                                    self.Messages["Short_Shift_clickT_Ch"],
                                                self.Messages["Short_Shift_Ctrl_clickT"]:
                                                    self.Messages["Short_Shift_Ctrl_clickT_Ch"],
                                                self.Messages["Short_A"]:
                                                    self.Messages["Short_A_Ch"],
                                                self.Messages["Short_L"]:
                                                    self.Messages["Short_L_Ch"],
                                                self.Messages["Short_N"]:
                                                    self.Messages["Short_N_Ch"],
                                                self.Messages["Short_E"]:
                                                    self.Messages["Short_E_Ch"],
                                                self.Messages["Short_Alt_Click"]:
                                                    self.Messages["Short_Alt_Click_Ch"],
                                                self.Messages["Short_S"]:
                                                    self.Messages["Short_S_Ch"],
                                                self.Messages["Short_Tab"]:
                                                    self.Messages["Short_Tab_Ch"],
                                                self.Messages["Short_Return"]:
                                                    self.Messages["Short_Return_Ch"],

                                                self.Messages["Short_Alt_C"]:
                                                    self.Messages["Short_Alt_C_Ch"],
                                                self.Messages["Short_Ctrl_F"]:
                                                    self.Messages["Short_Ctrl_F_Ch"],
                                                self.Messages["Short_Right_column"]:
                                                    self.Messages["Short_Right_column_Ch"],
                                                self.Messages["Short_Ctrl_W"]:
                                                    self.Messages["Short_Ctrl_W_Ch"],
                                                self.Messages["Short_Ctrl_C"]:
                                                    self.Messages["Short_Ctrl_C_Ch"],
                                                self.Messages["Short_Ctrl_V"]:
                                                    self.Messages["Short_Ctrl_V_Ch"],
                                                self.Messages["Short_Space"]:
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

        self.HW.grid(row=0, column=1, sticky="nsew")

        self.User_params_cont=Frame(self.parent, **Color_settings.My_colors.Frame_Base)
        self.User_params_cont.grid(row=1,column=1)

        Grid.columnconfigure(self.User_params_cont, 0, weight=1)
        Grid.rowconfigure(self.User_params_cont, 0, weight=1)
        Grid.rowconfigure(self.User_params_cont, 1, weight=1)
        Grid.rowconfigure(self.User_params_cont, 2, weight=1)

        Frame(self.User_params_cont, **Color_settings.My_colors.Frame_Base, height=10).grid(row=1,columnspan=3)



        self.show_arenas = False

        Traj_param=Frame(self.User_params_cont, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        Traj_param.grid(row=0, column=0, columnspan=3, sticky="nsew")
        Grid.columnconfigure(Traj_param, 0, weight=1)
        Grid.columnconfigure(Traj_param, 1, weight=1)


        #Scale to allow the user to choose the length of the trajectories' tails he want to see
        self.max_tail=IntVar()
        self.max_tail.set(600)
        self.Scale_tail=Scale(Traj_param, from_=0, to=self.max_tail.get(), resolution=0.5, variable=self.tail_size, orient="horizontal", label=self.Messages["Control4"], **Color_settings.My_colors.Scale_Base)
        self.Scale_tail.grid(row=0,column=0, columnspan=2, sticky="ew")
        self.Scale_tail.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control14"]))
        self.Scale_tail.bind("<Leave>", lambda a: self.HW.remove_tmp_message())

        #Button so the user can see all the trajectories at the same time
        self.bouton_show_all_traj=Button(Traj_param, text=self.Messages["Control11"], command=self.show_all_com, **Color_settings.My_colors.Button_Base)
        self.bouton_show_all_traj.grid(row=1,column=1, sticky="nsew")

        self.Frame_ind_ID=Frame(Traj_param, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.Frame_ind_ID.grid(row=1,column=0, sticky="nsew")


        self.F_NAs=Frame(self.User_params_cont, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.F_NAs.grid(row=2,column=0, columnspan=4, sticky="ewns")
        Grid.columnconfigure(self.F_NAs, 0, weight=100)
        Grid.columnconfigure(self.F_NAs, 1, weight=1)

        self.Frame_last_row=Frame(self.User_params_cont, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.Frame_last_row.grid(row=5, column=0, columnspan=4, sticky="sewn")
        Grid.columnconfigure(self.Frame_last_row, 0, weight=1)
        Grid.columnconfigure(self.Frame_last_row, 1, weight=0)
        Grid.columnconfigure(self.Frame_last_row, 2, weight=0)
        Grid.columnconfigure(self.Frame_last_row, 3, weight=0)
        #Save the modified coordinates

        Frame_save_quit=Frame(self.User_params_cont, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        Frame_save_quit.grid(row=6, column=0, columnspan=4, sticky="sewn")
        Grid.columnconfigure(Frame_save_quit, 0, weight=1)
        Grid.columnconfigure(Frame_save_quit, 1, weight=1)

        self.bouton_save=Button(Frame_save_quit, text=self.Messages["Control3"], command=self.save, **Color_settings.My_colors.Button_Base)
        self.bouton_save.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.bouton_save.grid(row=0, column=0, sticky="we")

        #Save coordinates and jump to next video
        self.bouton_saveNext=Button(Frame_save_quit, text=self.Messages["Control7"], command=lambda: self.save(follow=True), **Color_settings.My_colors.Button_Base)
        self.bouton_saveNext.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.bouton_saveNext.grid(row=0, column=1,  sticky="we")

        #Cancel and return to menu without applying the changes
        self.bouton_Cancel=Button(Frame_save_quit, text=self.Messages["Cancel_N_return"], wraplength=150, command=self.cancel, **Color_settings.My_colors.Button_Base)
        self.bouton_Cancel.config(background=Color_settings.My_colors.list_colors["Cancel"], fg=Color_settings.My_colors.list_colors["Fg_Cancel"])
        self.bouton_Cancel.grid(row=1, column=0,  sticky="nswe")

        #Remove all the correction and come back to the original trackings coordinates
        self.bouton_remove_corrections=Button(Frame_save_quit, text=self.Messages["Control8"], command=self.remove_corr, **Color_settings.My_colors.Button_Base)
        self.bouton_remove_corrections.grid(row=1, column=1, sticky="nswe")
        self.bouton_remove_corrections.config(bg=Color_settings.My_colors.list_colors["Danger"],fg=Color_settings.My_colors.list_colors["Fg_Danger"])

        #Load the video
        self.create_container()
        self.load_Vid(self.Vid)
        self.create_options()



        #The redo-tracking option is not available for unknown number of targets:
        if self.Vid.Track[1][8] and self.Vid.Track[0]:#If the user choose manual tracking or variable number of target no possibility to add/remove inds
            self.bouton_redo_track.grid(row=0, column=1, sticky="we")
        else:
            self.bouton_redo_track.grid_forget()
        self.calculate_NA()

        self.find_stops()#CTXT

        self.bind_all_win()



    def bind_all_win(self):
        self.bind_all("<Shift-space>", self.play_and_select)
        self.bind_all("<Control-z>", self.remove_last)
        self.bind_all("<Control-f>", self.ind_table_search)
        self.bind_all("<Control-w>", self.reset_view)
        self.bind_all("<Return>", self.change_ID_name)
        self.bind_all("<Tab>", self.go_next_ID)
        self.bind_all("<KeyPress>", self.keypress)
        self.bind_all("<KeyRelease>", self.keyrelease)
        self.bind_all("<Alt-c>",self.copy_IDs)

        def bind_to_children(widget):
            try:
                widget.bind("<Tab>", self.go_next_ID)
            except AttributeError:
                # Some widgets may not support binding
                pass
            for child in widget.winfo_children():
                bind_to_children(child)

        # Start binding from the root window
        bind_to_children(self.boss)

    def bind_all_tree(self):
        self.tree.bind("<Button-1>", self.Initiate_drag, add=False)
        self.tree.bind("<ButtonRelease>", self.selectItem, add=False)
        self.tree.bind("<Motion>", self.mouse_over_tree, add=False)
        self.tree.bind("<Leave>", self.remove_info, add=False)
        self.tree.bind("<Shift-ButtonRelease>", self.selectItem, add=False)
        self.tree.bind("<Control-Shift-ButtonRelease>", self.selectItem, add=False)
        self.tree.bind("<Button-3>", partial(self.selectItem, Right=True), add=False)
        self.tree.bind("<MouseWheel>", self.On_mousewheel, add=False)
        self.tree.bind("<Control-c>", self.copy_data, add=False)
        self.tree.bind("<Control-v>", self.paste_data, add=False)

    def unbind_all_tree(self):
        self.tree.unbind("<Button-1>")
        self.tree.unbind("<ButtonRelease>")
        self.tree.unbind("<Motion>")
        self.tree.unbind("<Leave>")
        self.tree.unbind("<Shift-ButtonRelease>")
        self.tree.unbind("<Control-Shift-ButtonRelease>")
        self.tree.unbind("<Button-3>")
        self.tree.unbind("<MouseWheel>")
        self.tree.unbind("<Control-c>")
        self.tree.unbind("<Control-v>")


    def unbind_all_win(self):
        self.unbind_all("<Shift-space>")
        self.unbind_all("<Control-z>")
        self.unbind_all("<Control-v>")
        self.unbind_all("<Control-w>")
        self.bind_all("<Control-f>")
        self.unbind_all("<Alt-c>")
        self.unbind_all("<Return>")
        self.unbind_all("<KeyPress>")
        self.unbind_all("<KeyRelease>")
        self.unbind_all("<Tab>")

    def reset_order(self, *args):
        self.table_order=list(range(len(self.Vid.Identities)))
        self.afficher_table(redo=True)

    def hide_some(self, *args):
        self.list_inds_returned=[]
        newWindow = Toplevel(self.parent.master)
        Interface_extend_Check.Lists(parent=newWindow, boss=self, Vid=self.Vid)
        self.wait_window(newWindow)

        for ind in sorted(self.list_inds_returned, reverse=True):
            self.hide_col(self.table_order.index(ind))

        self.list_inds_returned = []


    def table_smth(self, choice):
        self.table_holder.set(self.Messages["Control43"])
        if choice==self.table_options_list[0]:#Reset original order
            self.reset_order()
        elif choice == self.table_options_list[1]:  # Reset original order
            self.reset_view()
        elif choice == self.table_options_list[2]:  # Reset original order
            self.hide_some()


    def interpolate_smth(self, choice):
        self.interpo_holder.set(self.Messages["Control33"])
        if choice==self.inter_options_list[1]:#"Selected frames" > "Selected individual"
            self.interpolate(forced_type=0)
        elif choice==self.inter_options_list[2]:#"Selected frames" > "Selected arena"
            self.interpolate(forced_type=5)
        elif choice==self.inter_options_list[3]:#"Selected frames" > "Video"
            self.interpolate(forced_type=6)
        elif choice==self.inter_options_list[5]:#"All missing frames" > "Selected individual"
            self.interpolate(forced_type=1)
        elif choice==self.inter_options_list[6]:#"All missing frames > selected arena":
            self.interpolate(forced_type=4)
        elif choice == self.inter_options_list[7]:#"All missing frames > video":
            self.interpolate(forced_type=2)
        elif choice == self.inter_options_list[8]:#"All missing frames > all the videos":
            self.interpolate(forced_type=3)

    def remove_coos_smth(self, choice):
        self.remove_coo_holder.set(self.Messages["Control40"])
        if choice == self.remove_coo_options_list[1]:  #  "Selected individual"
            self.change_for_NA(type=0)
        elif choice == self.remove_coo_options_list[2]:  # "Selected arena"
            self.change_for_NA(type=1)
        elif choice == self.remove_coo_options_list[3]:  #  "Video"
            self.change_for_NA(type=2)
        elif choice == self.remove_coo_options_list[4]:  #  "Draw spatially"
            self.change_spatial_removal_state()
            self.modif_image()

    def remove_inds_smth(self, choice):
        self.remove_ind_holder.set(self.Messages["Control42"])
        if choice == self.remove_ind_options_list[0]:  #  "Selected individual"
            self.del_ind(self.selected_ind)
        elif choice == self.remove_ind_options_list[1]:  # Arena
            list_inds = [idx for idx, Ind in enumerate(self.Vid.Identities) if Ind[0] == self.Vid.Identities[self.selected_ind][0]]  # Selected frames, Arena
            for ind in sorted(list_inds, reverse=True):
                self.del_ind(ind)
        elif choice == self.remove_ind_options_list[2]:  # Video
            list_inds = [idx for idx, Ind in enumerate(self.Vid.Identities)]  # Selected frames, Arena
            for ind in sorted(list_inds, reverse=True):
                self.del_ind(ind)

        elif choice == self.remove_ind_options_list[3]:  # Personalised
            self.list_inds_returned=[]
            newWindow = Toplevel(self.parent.master)
            Interface_extend_Check.Lists(parent=newWindow, boss=self, Vid=self.Vid)
            self.wait_window(newWindow)

            for ind in sorted(self.list_inds_returned, reverse=True):
                self.del_ind(ind)

            self.list_inds_returned=[]

    def view_smth(self, choice):
        self.view_holder.set(self.Messages["Mask2"])
        if choice == self.view_options_list[0]:  #  Lock view
            self.change_lock_view_state()
            self.modif_image()
        elif choice == self.view_options_list[1]:  # Show arenas
            self.show_arenas = not self.show_arenas
            if self.show_arenas:
                self.view_options['menu'].entryconfigure(self.view_options_list[1],
                                                         background=Color_settings.My_colors.list_colors["Title1"],
                                                         foreground=Color_settings.My_colors.list_colors["Fg_Title1"])
            else:
                self.view_options['menu'].entryconfigure(self.view_options_list[1],
                                                         background=Color_settings.My_colors.list_colors["Base"],
                                                         foreground=Color_settings.My_colors.list_colors["Fg_Base"])
            self.modif_image()
        elif choice == self.view_options_list[2]:  # Separate coordinates table
            self.Coos_new_windows()
        elif choice == self.view_options_list[3]:  # Zoom out
            self.Vid_Lecteur.Zoom_out()


    def copy_data(self, event):
        if event.widget==self.tree and len(self.selected_rows)>0:
            self.copied_cells=[self.selected_ind,self.selected_rows]

            for_clipboard=self.Coos[self.selected_ind, self.selected_rows, :].copy()
            for_clipboard = '\n'.join(['\t'.join(map(str, row)) for row in for_clipboard])
            self.clipboard_clear()
            self.clipboard_append(for_clipboard)

        self.afficher_table()


    def paste_data(self, event):
        if event.widget==self.tree:
            if len(self.copied_cells)>0:
                if len(self.copied_cells[1])==1:
                    old = self.Coos[self.selected_ind, self.selected_rows, :].copy()
                    nb_rows=len(self.selected_rows)
                    self.Coos[self.selected_ind, self.selected_rows, :] = self.Coos[self.copied_cells[0], self.copied_cells[1], :]
                else:
                    nb_rows=min(len(self.selected_rows), len(self.copied_cells[1]))
                    old = self.Coos[self.selected_ind, self.selected_rows[0:(nb_rows)], :].copy()
                    self.Coos[self.selected_ind, self.selected_rows[0:(nb_rows)], :] = self.Coos[self.copied_cells[0], self.copied_cells[1][0:(nb_rows)], :]

                self.add_change("replaced", self.selected_ind, self.selected_rows[0:nb_rows], old)
                self.afficher_table()

    def copy_IDs(self, *args):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Vid.Identities, boss=self.main_frame,
                                            Video_file=self.Vid, type="IDs", do_self=False)

    def keypress(self, event):
        if (event.char=="a" or event.char=="A") and event.widget.winfo_class()!="Entry":
            self.show_arenas=True
            self.modif_image()

        if (event.char=="l" or event.char=="L") and event.widget.winfo_class()!="Entry":
            self.change_lock_view_state()
            self.modif_image()

        if (event.char=="n" or event.char=="N") and event.widget.winfo_class()!="Entry":
            self.next_NA()

        if (event.char=="e" or event.char=="E") and event.widget.winfo_class()!="Entry":
            self.change_spatial_removal_state()
            self.modif_image()

        if (event.char=="d" or event.char=="D") and event.widget.winfo_class()!="Entry":
            self.add_selected_as_stop()
            self.modif_image()

        if (event.char=="s" or event.char=="S") and event.widget.winfo_class()!="Entry":
            self.save_file()

    def change_lock_view_state(self):
        self.locked_view = not self.locked_view
        if self.locked_view:
            self.view_options['menu'].entryconfigure(self.view_options_list[0],
                                                           background=Color_settings.My_colors.list_colors["Title1"],
                                                           foreground=Color_settings.My_colors.list_colors["Fg_Title1"])
        else:
            self.view_options['menu'].entryconfigure(self.view_options_list[0],
                                                           background=Color_settings.My_colors.list_colors["Base"],
                                                           foreground=Color_settings.My_colors.list_colors["Fg_Base"])

    def change_spatial_removal_state(self):
        self.Vid_Lecteur.no_zoom = not self.Vid_Lecteur.no_zoom
        if self.Vid_Lecteur.no_zoom:
            self.remove_coo_options['menu'].entryconfigure(self.remove_coo_options_list[4],
                                                           background=Color_settings.My_colors.list_colors["Title1"],
                                                           foreground=Color_settings.My_colors.list_colors["Fg_Title1"])
        else:
            self.remove_coo_options['menu'].entryconfigure(self.remove_coo_options_list[4],
                                                           background=Color_settings.My_colors.list_colors["Base"],
                                                           foreground=Color_settings.My_colors.list_colors["Fg_Base"])

    def keyrelease(self, event):
        if (event.char == "a" or event.char == "A") and event.widget.winfo_class()!="Entry":
            self.show_arenas = False
            self.modif_image()

        elif (event.char == "q" or event.char == "Q") and event.widget.winfo_class()!="Entry":
            self.go_next_stop()



    def go_next_stop(self):#CTXT
        if len(self.all_stops)>0:
            next_stop=self.all_stops[0]
            for stop in self.all_stops:
                if (self.Scrollbar.active_pos + self.to_sub) < round(stop):
                    next_stop=round(stop)
                    break

            self.Scrollbar.active_pos = next_stop + self.to_sub
            self.Scrollbar.refresh()

            self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)

            self.afficher_table()
            self.Xpos.set(self.table_order.index(self.selected_ind)+ 1)
            self.modif_image(img=self.last_empty, redo=True)

    def add_selected_as_stop(self):
        try:
            self.all_stops_verif
        except:
            self.all_stops_verif=[]

        for rID in self.selected_rows:
            if rID not in self.all_stops_verif:
                self.all_stops_verif.append(rID)
            else:
                self.all_stops_verif.remove(rID)
        self.modif_image()
        #print(self.all_stops_verif)

    def On_mousewheel(self, event):
        if (int(self.Scrollbar.active_pos)-int(event.delta / 120) >= round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every) and event.delta>0) or (event.delta<0 and int(self.Scrollbar.active_pos)-int(event.delta / 120) <= round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every)):
            self.Scrollbar.active_pos=self.Scrollbar.active_pos-int(event.delta / 120)
            self.Scrollbar.refresh()
            self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)

    def go_next_ID(self, *args):
        if self.table_order.index(self.selected_ind) + 1 >=len(self.table_order):
            self.selected_ind=self.table_order[0]
        else:
            self.selected_ind = self.table_order[self.table_order.index(self.selected_ind) + 1]

        self.calculate_NA()

        self.ID_Entry.delete(0, END)
        self.ID_Entry.insert(0, self.Vid.Identities[self.selected_ind][1])  # Write the name of the target
        self.Arena_Lab.config(text=self.Vid.Identities[self.selected_ind][0])  # Write the name of the Arena
        self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])  # indicate the color of the new selected target

        self.Xpos.set(self.table_order.index(self.selected_ind)+ 1)
        self.modif_image(img=self.last_empty, redo=True)
        return "break"


    def change_ID_name(self,  *args):
        # This function check if the name wrote by the user is not already used, it if is the case, we add "_copy" at the end.
        focus=self.master.focus_get()==self.ID_Entry
        if focus:
            new_val=self.ID_Entry.get()
            if new_val != "":
                if new_val!=self.Vid.Identities[self.selected_ind][1]:
                    if new_val in [ident[1] for ident in self.Vid.Identities if ident[0]==self.Vid.Identities[self.selected_ind][0]]:
                        new_val=new_val+"_copy"
                    self.Vid.Identities[self.selected_ind][1]=new_val
                    self.afficher_table(redo=True)
            self.parent.focus()
        else:
            self.ID_Entry.focus_set()

    def change_color(self, event):
        #This will open a color chart to choose the color the user wants to associate with the target.
        color_choice = Toplevel()
        Canvas_colors(parent=color_choice, boss=self, ind=self.selected_ind)

    def play_and_select(self, event):
        #This allows to select all the frames displayed while playing the video.
        if not self.Vid_Lecteur.playing:
            begin = self.Scrollbar.active_pos - self.to_sub

            if len(self.selected_rows)==0:self.selected_rows=[begin]

            if int(max(self.selected_rows)) == int(begin):
                begin=min(self.selected_rows)

            self.Vid_Lecteur.play(select=True, begin=begin)
        else:
            self.Vid_Lecteur.stop()

    def show_all_com(self):
        #This show/hide the complete trajectories of the targets
        if self.show_all:
            self.show_all = False
            self.bouton_show_all_traj.config(**Color_settings.My_colors.Button_Base)
        else:
            self.show_all = True
            self.bouton_show_all_traj.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.modif_image()

    def remove_corr(self):
        #If the user wants to remove all the modifications done.
        question = MsgBox.Messagebox(parent=self, title="",
                                     message=self.Messages["Control26"],
                                     Possibilities=[self.Messages["Yes"],
                                                    self.Messages["No"]])
        self.wait_window(question)
        answer = question.result

        if answer==0:
            if self.Vid.User_Name == self.Vid.Name:
                file_name = self.Vid.Name
                point_pos = file_name.rfind(".")
                if file_name[point_pos:].lower() != ".avi":
                    file_name = self.Vid.User_Name
                else:
                    file_name = file_name[:point_pos]
            else:
                file_name = self.Vid.User_Name

            if os.path.isfile(os.path.join(self.Vid.Folder,"corrected_coordinates",file_name + "_Corrected.csv")):
                os.remove(os.path.join(self.Vid.Folder,"corrected_coordinates",file_name + "_Corrected.csv"))

            self.Vid.Identities=copy.deepcopy(self.Vid.Identities_saved)
            self.Vid.Sequences=copy.deepcopy(self.Vid.Sequences_saved)
            #self.Vid.Morphometrics = copy.deepcopy(self.Vid.Morphometrics)
            self.Vid.Track[1][6]= copy.deepcopy(self.Vid.saved_repartition)
            self.load_Vid(self.Vid)
            # The redo-tracking option is not available for unknown number of targets:
            if self.Vid.Track[1][8] and self.Vid.Track[
                0]:  # If the user choose manual tracking or variable number of target no possibility to add/remove inds
                self.bouton_redo_track.grid(row=0, column=1, sticky="we")
            else:
                self.bouton_redo_track.grid_forget()
            self.calculate_NA()
            self.save_changes=[]
            self.copied_cells = []
            self.calculate_NA()
            self.modif_image()


    def redo_tracking(self):
        if len(self.selected_rows) > 2:
            #Rerun part of the tracking. To do so, a temporary table and a temporary video will be created from the frames to be re-run.
            self.timer=0

            if len(self.Arenas_with_holes)>1:
                question = MsgBox.Messagebox(parent=self, title="",
                                             message=self.Messages["Control27"],
                                             Possibilities=[self.Messages["Yes"], self.Messages["No"], self.Messages["Cancel"]])
                self.wait_window(question)
                answer = question.result

            else:
                answer=0

            if answer <2:
                self.Vid_Lecteur.proper_close()  # To avoid too much memory consumption, the current video reader is closed until the rerun is done.
                self.first = int(self.selected_rows[0]) + round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every)
                self.last = int(self.selected_rows[len(self.selected_rows) - 1]) + round(
                    self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every + 1)


                self.TMP_Vid = copy.deepcopy(self.Vid)
                self.TMP_Vid.Cropped[0] = 1
                self.TMP_Vid.Cropped[1][0] = round(self.first * self.Vid_Lecteur.one_every)
                self.TMP_Vid.Cropped[1][1] = round((self.last - 1) * self.Vid_Lecteur.one_every)

                if len(self.selected_rows) > 2:  # It works only if we select more than two frames.
                    if answer==1:
                        self.inds_portion = range(len(self.Vid.Identities))#We will do it for all individuals
                        new_Coos=self.Coos[:,(self.first- round(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every)):(self.last- round(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every)),:].copy()
                        CoosLS.save(self.TMP_Vid, new_Coos, TMP=True, location=self)

                        #We create a new coordinates file with only the selected frames:
                        if self.Vid.Track[1][8]:
                            if self.first > self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every:
                                prev_row = [self.first - 1, (self.first - 1) / self.Vid_Lecteur.one_every]  # We also check for the last known coordinates before to re-run to allow target's assigment.
                                for ind in range(self.Coos.shape[0]):
                                    prev_row = prev_row + list(self.Coos[ind,self.first - round(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every) -1,:])

                                prev_row2=[]
                                for i in prev_row:
                                    if i!=-1000:
                                        prev_row2.append(i)
                                    else:
                                        prev_row2.append("NA")
                                prev_row=prev_row2
                            else:
                                prev_row=None
                        else:
                            pass

                        #We open the portion window in which the user will be able to change the parameters of tracking and rerun this part of the video.
                        self.PortionWin = Toplevel()
                        Interface_portion.Show(parent=self.PortionWin, boss=self, Vid=self.TMP_Vid, Video_liste=self.Video_liste, prev_row=prev_row, Arena=None, First_frame=self.Vid.Cropped[1][0])


                    elif answer==0:
                        self.inds_portion = [idx for idx,ind in enumerate(self.Vid.Identities) if ind[0] == self.Vid.Identities[self.selected_ind][0]]
                        new_Coos = self.Coos[self.inds_portion, (self.first - round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every)):(self.last - round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every)), :].copy()

                        self.TMP_Vid.Identities = [ind for ind in self.Vid.Identities if ind[0] == self.Vid.Identities[self.selected_ind][0]]
                        self.TMP_Vid.Track[1][6]=[len(self.inds_portion)]

                        CoosLS.save(self.TMP_Vid, new_Coos, TMP=True, location=self)

                        # We create a new coordinates file with only the selected frames:
                        if self.Vid.Track[1][8]:
                            if self.first > self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every:
                                prev_row = [self.first - 1, (self.first - 1) / self.Vid_Lecteur.one_every]  # We also check for the last known coordinates before to re-run to allow target's assigment.

                                for ind in range(self.Coos.shape[0]):
                                    if ind in self.inds_portion:
                                        prev_row = prev_row + list(self.Coos[ind, self.first - int(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every) - 1, :])

                                prev_row2 = []
                                for i in prev_row:
                                    if i != -1000:
                                        prev_row2.append(i)
                                    else:
                                        prev_row2.append("NA")
                                prev_row = prev_row2
                            else:
                                prev_row = None
                        else:
                            pass

                        #We open the portion window in which the user will be able to change the parameters of tracking and rerun this part of the video.
                        self.PortionWin = Toplevel()
                        Interface_portion.Show(parent=self.PortionWin, boss=self, Vid=self.TMP_Vid, Video_liste=self.Video_liste, prev_row=prev_row, Arena=self.Vid.Identities[self.selected_ind][0], First_frame=self.Vid.Cropped[1][0])

    def redo_Lecteur(self):
        #If the Video reader was destroyed (i.e. redo_tracking function), this function allows to rebuild the video reader.
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=0)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Vid_Lecteur.speed.set(self.speed)
        self.Vid_Lecteur.change_speed()
        self.Scrollbar=self.Vid_Lecteur.Scrollbar


        if self.Vid.Stab[0]:
            self.prev_pts = self.Vid.Stab[1]

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()
        self.calculate_NA()


    def change_for_corrected(self):
        #After a portion of the tracking has been rerun (see redo_tracking function), this function is called to change the old coordinates by the new ones.
        #We load the temporary table with coordinates from rerunned tracking:
        if self.Vid.User_Name == self.Vid.Name:
            file_name = self.Vid.Name
            point_pos = file_name.rfind(".")
            if file_name[point_pos:].lower() != ".avi":  # Old versions of AnimalTA did not allow to rename or duplicate the videos, the name of the video was the file name without the ".avi" extension
                file_name = self.Vid.User_Name
            else:
                file_name = file_name[:point_pos]
        else:
            file_name = self.Vid.User_Name

        path = os.path.join(self.Vid.Folder, "TMP_portion", file_name + "_TMP_portion_Coordinates.csv")


        with open(path, encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            or_table = list(csv_reader)

        or_table = np.asarray(or_table)
        or_table[or_table == "NA"] = -1000
        or_table = or_table[1:, 2:]

        debut=self.first - self.to_sub
        fin=self.first - self.to_sub + len(or_table[:, 0])
        self.add_change("redo_track", self.inds_portion, [debut, fin], self.Coos[self.inds_portion, debut: fin,:].copy())

        changed=0
        for Ind in range(len(self.Vid.Identities)):
            if self.inds_portion==None or Ind in self.inds_portion:
                self.Coos[Ind,self.first - self.to_sub : self.first - self.to_sub +len(or_table[:,0]),:] = or_table[:,2 * changed:2 * changed + 2]
                #self.Vid.Morphometrics[Ind] = [morpho for morpho in self.Vid.Morphometrics[Ind] if (morpho[0]<debut or morpho>fin)]
                changed += 1

        self.redo_Lecteur()
        # We place the reader at the last corrected frame
        self.Scrollbar.active_pos = int((self.first +len(or_table[:,0])-1))
        self.Scrollbar.refresh()

        self.last_shown=None
        self.afficher_table()
        os.remove(path)
        self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)
        self.calculate_NA()


    def cancel(self):
        self.Vid.Identities=self.opening_Identities
        self.Vid.Sequences = self.opening_Sequences
        self.Vid.Track[1][6]=self.opening_Track
        self.End_of_window()

    def save(self, follow=False):
        #To save the modifications.
        #If follow=True, we save and open the next video
        try:
            self.save_file()
        except Exception as e:
            Interface_pretracking.CustomDialog(self.main_frame.master,
                         text="An exception occurred while saving the file:" + str(type(e).__name__) + " – " + str(e),
                         title="Debugging")
        try:
            self.main_frame.save()
        except Exception as e:
            Interface_pretracking.CustomDialog(self.main_frame.master,
                         text="An exception occurred while saving the main_frame:" + str(type(e).__name__) + " – " + str(e),
                         title="Debugging")

        if follow:
            liste_tracked = [Vid for Vid in self.Video_liste if Vid.Tracked]
            next = [Id + 1 for Id, Video in enumerate(liste_tracked) if Video == self.Vid][0]
            if next < (len(liste_tracked)):
                self.choice_menu.change_vid(liste_tracked[next].User_Name)
                return
        try:
            self.End_of_window()
        except Exception as e:
            Interface_pretracking.CustomDialog(self.main_frame.master,
                         text="An exception occurred while closing the window:" + str(type(e).__name__) + " – " + str(e),
                         title="Debugging")

    def End_of_window(self):
        #We destroy the frame and go back to main menu
        try:
            self.Vid_Lecteur.proper_close()
        except Exception as e:
            Interface_pretracking.CustomDialog(self.main_frame.master,
                         text="An exception occurred while closing the video reader:" + str(type(e).__name__) + " – " + str(e),
                         title="Debugging")

        self.unbind_all_win()
        self.unbind_all_tree()

        self.grab_release()
        self.User_params_cont.grid_forget()
        self.User_params_cont.destroy()
        self.HW.grid_forget()
        self.HW.destroy()




        def unbind_from_children(widget):
            try:
                widget.unbind("<Tab>")  # Remove the Tab binding
            except AttributeError:
                pass  # Some widgets may not support unbinding
            for child in widget.winfo_children():
                unbind_from_children(child)

        # Start unbinding from the root window
        unbind_from_children(self.boss)






        self.main_frame.return_main()
        self.main_frame.selected_vid = self.Vid
        self.main_frame.update_projects
        del self

    def save_file(self):
        #Save the new cooridnates in a specific folder (corrected_coordinates)
        CoosLS.save(self.Vid, self.Coos, location=self)
        #If there was a temporary file used, we delete it
        folder = os.path.join(self.main_frame.folder, "TMP_portion")
        if os.path.isdir(folder):
            shutil.rmtree(folder)

        self.Vid.Table_order = self.table_order.copy()
        self.Vid.corrected=True

    def pressed_can(self, Pt, event=""):
        #If the user press on the image.
        Ctrl = bool(event.state & 0x4)
        Shift = bool(event.state & 0x1)
        Alt = bool(event.state & 0x20000)


        pos=0
        if int(self.Scrollbar.active_pos) >= round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every) and int(self.Scrollbar.active_pos) <= round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every):
            if Alt:
                old_pos=self.Coos[self.selected_ind, self.Scrollbar.active_pos - self.to_sub].copy()
                self.Coos[self.selected_ind, self.Scrollbar.active_pos - self.to_sub]=Pt
                self.add_change("move", self.selected_ind, self.Scrollbar.active_pos - self.to_sub, old_pos)
                self.modif_image(img=self.last_empty, redo=True)  # Display the changes

            else:
                for ind in range(len(self.Coos)):
                    center = self.Coos[ind,self.Scrollbar.active_pos-self.to_sub]
                    if center[0]!=-1000:
                        dist_clic=math.sqrt((int(center[0])-Pt[0])**2+(int(center[1])-Pt[1])**2) #If user pressed on the position of a target
                        if dist_clic<max(2,(10*self.Vid_Lecteur.ratio)):
                            if Shift and not Ctrl:#If user pressed Shift key, the trajectories of the current target and of the previously selected one are swaped from the current frame to the end of the video.
                                self.echange_traj(self.selected_ind, ind, self.Scrollbar.active_pos - self.to_sub)
                            elif Shift and Ctrl:
                                if ind != self.selected_ind:
                                    self.fus_inds(self.selected_ind, ind)
                            else: #If not, the clicked pont is the new selected target
                                self.selected_ind = ind
                                self.ID_Entry.delete(0, END)
                                self.ID_Entry.insert(0, self.Vid.Identities[self.selected_ind][1])# Write the name of the target
                                self.Arena_Lab.config(text=self.Vid.Identities[self.selected_ind][0])# Write the name of the Arena
                                self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])# indicate the color of the new selected target
                                self.old_pos=self.Coos[self.selected_ind,self.Scrollbar.active_pos-self.to_sub].copy()
                                self.clicked = True  # If th user wants to move the target, this flag is used to know that user is pressing left.

                            self.Xpos.set(self.table_order.index(self.selected_ind)+ 1)
                            self.modif_image(img=self.last_empty, redo=True) # Display the changes


                            break
                    pos+=1

    def echange_traj(self, ind1, ind2, frame, save=True):
        #Make a swap between two targets' trajectories from the active farme to the end of the video
        self.Coos[ind2,frame:len(self.Coos[ind2])], self.Coos[ind1,frame:len(self.Coos[ind2])]  = self.Coos[ind1,frame:len(self.Coos[ind2])], self.Coos[ind2,frame:len(self.Coos[ind2])].copy()


        #ind1_out = [morpho for morpho in self.Vid.Morphometrics[ind1] if(morpho[0] < frame or morpho > len(self.Coos[ind1]))]
        #ind1_in = [morpho for morpho in self.Vid.Morphometrics[ind1] if (morpho[0] >= frame and morpho <= len(self.Coos[ind1]))]

        #ind2_out = [morpho for morpho in self.Vid.Morphometrics[ind2] if(morpho[0] < frame or morpho > len(self.Coos[ind2]))]
        #ind2_in = [morpho for morpho in self.Vid.Morphometrics[ind2] if (morpho[0] >= frame and morpho <= len(self.Coos[ind2]))]

        #self.Vid.Morphometrics[ind1]=ind1_out+ind2_in
        #self.Vid.Morphometrics[ind2] = ind2_out + ind1_in

        self.afficher_table(redo=True)
        if save:
            self.add_change("swap",ind1,self.Scrollbar.active_pos - self.to_sub,ind2)

        self.calculate_NA()
        self.modif_image()

    def fus_inds(self, ind1, ind2):
        question = MsgBox.Messagebox(parent=self, title="",
                                     message=self.Messages["Control28"].format(self.Vid.Identities[ind1][1],self.Vid.Identities[ind2][1]),
                                     Possibilities=[self.Messages["Yes"], self.Messages["Cancel"]])
        self.wait_window(question)
        answer = question.result

        if answer==0:
            to_change=self.Coos[ind1]==-1000
            self.Coos[ind1,to_change]=self.Coos[ind2,to_change]

            #lignes_change=np.where(to_change[:,0])[0]
            #self.Vid.Morphometrics[ind1] = [morpho for morpho in self.Vid.Morphometrics[ind1] if (morpho[0] not in lignes_change)] + [morpho for morpho in self.Vid.Morphometrics[ind2] if (morpho[0] in lignes_change)]

            self.del_ind(ind2, add_save=False, fus=True)

            self.vsbx.config(to=len(self.Vid.Identities))
            self.selected_ind = ind1
            self.ID_Entry.delete(0, END)
            self.ID_Entry.insert(0, self.Vid.Identities[self.selected_ind][1])  # Write the name of the target
            self.Arena_Lab.config(text=self.Vid.Identities[self.selected_ind][0])  # Write the name of the Arena
            self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])  # indicate the color of the new selected target
            self.save_changes = []
            if ind1 == self.copied_cells[0] or ind2==self.copied_cells[0]:
                self.copied_cells = []


    def find_stops(self):#CTXT
        try:
            smoothed_coos=Diverse_functions.smooth_coos(Coos=self.Coos.copy(), window_length=11, polyorder=2)
            sub_coos=smoothed_coos[self.selected_ind]

            Dists = np.sqrt(np.diff(sub_coos[:, 0]) ** 2 + np.diff(sub_coos[:, 1]) ** 2) / float(self.Vid.Scale[0])
            Dists = np.append(np.nan, Dists)
            Speeds = Dists / (1 / self.Vid.Frame_rate[1])
            State = np.zeros(len(Speeds))
            State[np.where(Speeds > 15)] = 1
            State[np.where(np.isnan(Speeds))] = np.nan

            #self.all_stops=self.find_inactive()
        except:
            pass


    def find_inactive(self):#Only for me, to delete later
        try:
            window_length=int(5*(self.Vid.Frame_rate[1])) #Duration of the window
            threshold=50#mm if the fished moved less than X

            points_end=self.Coos[self.selected_ind,window_length:]
            points_beg = self.Coos[self.selected_ind,:-window_length]
            dist = np.linalg.norm(points_end - points_beg, axis=1) / float(self.Vid.Scale[0])
            mask = dist <= threshold
            windows=np.where(mask)[0]
            #print(windows)
            window_diff = np.diff(windows)
            window_diff = np.concatenate(([0], window_diff))  # prepend 0 for first window
            mask_diff = window_diff >= window_length  # True if this is start of new window

            # Extract start indices of merged windows
            valid_windows = windows[mask_diff]

            return(valid_windows)
        except:
            pass


    def moved_can(self, Pt, Shift):
        #Used to move  a target's position
        #If the user clicked on a target before and if the user does not try to put the target outside of the frame.
        if self.clicked and Pt[0]>=0 and Pt[1]>=0 and Pt[0]<=self.Vid.shape[1] and Pt[1]<=self.Vid.shape[0]:
            #We change the coordinates
            self.Coos[self.selected_ind,self.Scrollbar.active_pos-self.to_sub]=[Pt[0],Pt[1]]

            #Display the new frame
            self.modif_image(self.last_empty)
            self.moved=True

    def right_click(self, Pt):
        #If the target position was unknown (NA value), the user can create a new position using a right click.
        if self.Coos[self.selected_ind,self.Scrollbar.active_pos-self.to_sub][0]==-1000:
            self.add_change("add_coos",self.selected_ind,self.Scrollbar.active_pos-self.to_sub,self.Coos[self.selected_ind,self.Scrollbar.active_pos-self.to_sub][0])

            self.Coos[self.selected_ind, self.Scrollbar.active_pos - self.to_sub] = [Pt[0], Pt[1]]
            self.calculate_NA()
            self.modif_image(self.last_empty)


            if (self.Scrollbar.active_pos - self.to_sub +1) < (len(self.Coos[self.selected_ind,])):
                self.Scrollbar.active_pos += 1
            else:
                self.Scrollbar.active_pos = self.to_sub
                self.go_next_ID()

            self.Scrollbar.refresh()
            self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)
            self.afficher_table()


    def released_can(self, Pt):
        #We put back the clicked flag to false (user is not moving a target's position)
        if self.clicked and self.moved:
            #We change the coordinates
            self.add_change("move", self.selected_ind, self.Scrollbar.active_pos - self.to_sub, self.old_pos)
            #self.Vid.Morphometrics[self.selected_ind] = [morpho for morpho in self.Vid.Morphometrics[self.selected_ind] if (morpho[0] != self.Scrollbar.active_pos - self.to_sub)]

        self.clicked=False
        self.moved=False


    def add_change(self,type, ind, frames, old):
        self.save_changes.append([type, ind, frames, old])
        if len(self.save_changes)>30:
            self.save_changes.pop(0)

        if len(self.copied_cells)>0:
            if type == "move" or type == "add_coos" or type == "removed" or type == "replaced":
                if not isinstance(frames, list):
                    frames=[frames]
                if self.copied_cells[0] == ind and not set(frames).isdisjoint(self.copied_cells[1]):
                    self.copied_cells = []

            if type=="swap":
                if self.copied_cells[0] == ind and not min(self.copied_cells[1])>=frames:
                    self.copied_cells = []

            if type=="interpolate" or type=="redo_track":
                if not isinstance(ind, list):
                    ind=[ind]
                if self.copied_cells[0] in ind and not set(list(range(frames[0]+1,frames[1]+1))).isdisjoint(self.copied_cells[1]):
                    self.copied_cells = []

            if type=="delete_ind":
                if self.copied_cells[0] == ind:
                    self.copied_cells = []
                else:
                    if ind<self.copied_cells[0]:
                        self.copied_cells[0]-=1

        if not type=="delete_ind":
            self.afficher_table()

    def remove_last(self, *args):
        if len(self.save_changes)>0:
            type, ind, frames, old = self.save_changes[-1]
            if type=="move" or type=="add_coos":
                self.Coos[ind,frames]=old
                #self.Vid.Morphometrics[ind] = old[1]
            elif type=="interpolate":
                self.Coos[ind,frames[0]:frames[1]]=old
                #self.Vid.Morphometrics[ind]=old[1]
            elif type=="color":
                self.Vid.Identities[ind][2]=old
                self.Can_Col.config(background="#%02x%02x%02x" % old)
            elif type=="removed":
                self.Coos[ind,frames]=old
            elif type=="replaced":
                self.Coos[ind,frames]=old
            elif type=="swap":
                self.echange_traj(ind, old, frames, save=False)#We swap the IDs back but do not add a new swap
            elif type=="add_ind":
                self.del_ind(ind, add_save=False)
            elif type=="delete_ind":
                self.add_ind(pos=ind, old_dat=old[0], old_ID=old[1], add_save=False)
            elif type=="redo_track":
                changed=0
                for I in ind:
                    self.Coos[I,frames[0]:frames[1]]=old[changed]
                    #self.Vid.Morphometrics[I]=old[1][changed]
                    changed+=1
            self.modif_image()
            self.calculate_NA()
            self.save_changes.pop(-1)
            self.copied_cells=[]


    def Coos_new_windows(self):
        if not self.windowed:
            self.view_options['menu'].entryconfigure(self.view_options_list[2],  # We update the button in the optionmenu to indicate that this option is selected
                                                           background=Color_settings.My_colors.list_colors["Title1"],
                                                           foreground=Color_settings.My_colors.list_colors["Fg_Title1"])

            self.Top_lvl=Toplevel(self.parent.master, **Color_settings.My_colors.Frame_Base, borderwidth=10)
            self.Top_lvl.propagate(False)
            self.Top_lvl.protocol("WM_DELETE_WINDOW", self.Coos_old_window)

            Grid.columnconfigure(self.Top_lvl, 0, weight=100)  ########NEW
            Grid.rowconfigure(self.Top_lvl, 0, weight=1)  ########NEW
            Grid.rowconfigure(self.Top_lvl, 1, weight=1)  ########NEW
            Grid.rowconfigure(self.Top_lvl, 2, weight=100)  ########NEW
            Grid.rowconfigure(self.Top_lvl, 3, weight=1)  ########NEW

            self.Frame_ID=Frame(self.Top_lvl, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
            self.Frame_ID.grid(row=0, column=0,sticky="nsw")

            Grid.columnconfigure(self.Frame_ID, 0, weight=1)  ########NEW
            Grid.columnconfigure(self.Frame_ID, 1, weight=1)  ########NEW
            Grid.columnconfigure(self.Frame_ID, 2, weight=1)  ########NEW
            Grid.rowconfigure(self.Frame_ID, 0, weight=1)  ########NEW
            Grid.rowconfigure(self.Frame_ID, 1, weight=1)  ########NEW

            self.Frame_options=Frame(self.Top_lvl, **Color_settings.My_colors.Frame_Base)
            self.Frame_options.grid(row=1, column=0,sticky="nsew")
            Grid.columnconfigure(self.Frame_options, 0, weight=1)  ########NEW
            Grid.columnconfigure(self.Frame_options, 1, weight=1)  ########NEW

            Grid.rowconfigure(self.Frame_options, 0, weight=1)  ########NEW

            self.Frame_coos=Frame(self.Top_lvl, **Color_settings.My_colors.Frame_Base)
            self.Frame_coos.grid(row=2, column=0,sticky="nsew")

            Grid.columnconfigure(self.Frame_coos, 0, weight=1)
            Grid.columnconfigure(self.Frame_coos, 1, weight=1)
            Grid.rowconfigure(self.Frame_coos, 0, weight=1)
            Grid.rowconfigure(self.Frame_coos, 1, weight=1)
            Grid.rowconfigure(self.Frame_coos, 2, weight=1)
            Grid.rowconfigure(self.Frame_coos, 3, weight=100)

            self.Frame_options2=Frame(self.Top_lvl, **Color_settings.My_colors.Frame_Base)
            self.Frame_options2.grid(row=3, column=0,sticky="nsew")
            Grid.columnconfigure(self.Frame_options2, 0, weight=1)  ########NEW
            Grid.columnconfigure(self.Frame_options2, 1, weight=1)  ########NEW
            Grid.columnconfigure(self.Frame_options2, 2, weight=1)  ########NEW
            Grid.columnconfigure(self.Frame_options2, 3, weight=1)  ########NEW

            self.windowed=True
            self.create_container()
            self.create_options()
            self.afficher_table(redo=True)
        else:
            self.view_options['menu'].entryconfigure(self.view_options_list[2],  # We update the button in the optionmenu to indicate that this option is selected
                                                           background=Color_settings.My_colors.list_colors["Base"],
                                                           foreground=Color_settings.My_colors.list_colors["Fg_Base"])
            self.Coos_old_window()

    def Coos_old_window(self):
        self.table_heigh=14
        self.windowed=False
        self.Top_lvl.destroy()
        self.create_container()
        self.create_options()
        self.afficher_table(redo=True)

    def create_container(self):
        if not self.windowed:
            table=self.User_params_cont
        else:
            table=self.Frame_coos

        self.container_table = Canvas(table, heigh=300, width=300, bd=2, highlightthickness=1, relief='ridge' ,scrollregion=(0,0,500,500), **Color_settings.My_colors.Frame_Base)
        self.container_table.grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.container_table.grid_propagate(False)
        self.container_table.bind("<Configure>", self.resize_fr)
        Grid.columnconfigure(self.container_table, 0, weight=1)

    def resize_fr(self, event):
        self.afficher_table(redo=True)

    def create_options(self):
        try:
            self.vsb.destroy()
            self.B_look_NA.destroy()
            self.vsbx.destroy()
            self.bouton_inter.destroy()
            self.bouton_redo_track.destroy()
            self.bouton_add_new.destroy()
            self.bouton_del_ind.destroy()
            self.B_change_for_NA.destroy()
            self.separate_coos.destroy()
            self.Arena_Lab0.destroy()
            self.Arena_Lab.destroy()
            self.ID_Entry.destroy()
            self.Val_button.destroy()
            self.Can_Col.destroy()

        except:
            pass

        if not self.windowed:
            table=self.User_params_cont
            options1=self.F_NAs
            options2=self.Frame_last_row
            naming = self.Frame_ind_ID
        else:
            table=self.Frame_coos
            options1=self.Frame_options
            options2=self.Frame_options2
            naming=self.Frame_ID


        #We create a frame that will contain all the widgets allowing to re-name a target and change its color of representation
        self.Arena_Lab0 = Label(naming, text=self.Messages["Arena_short"], **Color_settings.My_colors.Label_Base)
        self.Arena_Lab0.grid(row=0, column=0, sticky="nsew")
        self.Arena_Lab0.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control15"]))
        self.Arena_Lab0.bind("<Leave>", lambda a: self.HW.remove_tmp_message())
        self.Arena_Lab=Label(naming, text=str(self.Vid.Identities[self.selected_ind][0])+" ", **Color_settings.My_colors.Label_Base)
        self.Arena_Lab.grid(row=0, column=1, sticky="nsew")
        self.Arena_Lab.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control15"]))
        self.Arena_Lab.bind("<Leave>", lambda a: self.HW.remove_tmp_message())
        #Target name
        self.ID_Entry=Entry(naming, **Color_settings.My_colors.Entry_Base)
        self.ID_Entry.grid(row=0, column=2, sticky="nsew")
        self.ID_Entry.insert(0,self.Vid.Identities[self.selected_ind][1])
        self.ID_Entry.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control16"]))
        self.ID_Entry.bind("<Leave>", lambda a: self.HW.remove_tmp_message())
        self.Val_button=Button(naming, text=self.Messages["Validate"], command=self.change_ID_name, **Color_settings.My_colors.Button_Base)
        self.Val_button.grid(row=1, column=2, sticky="nsew")
        self.Val_button.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control16"]))
        self.Val_button.bind("<Leave>", lambda a: self.HW.remove_tmp_message())

        #Target color
        self.Can_Col=Canvas(naming, **Color_settings.My_colors.Frame_Base, height=15, width=20)
        self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])
        self.Can_Col.grid(row=0, column=3, sticky="nsew")
        self.Can_Col.bind("<Button-1>", self.change_color)
        self.Can_Col.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control1"]))
        self.Can_Col.bind("<Leave>", lambda a: self.HW.remove_tmp_message())

        #Button to get the coordinates table in another window
        self.separate_coos=Button(table, text="⧉", command=self.Coos_new_windows, **Color_settings.My_colors.Button_Base)
        self.separate_coos.grid(row=4,column=2, sticky="snwe")

        #vertical scroll bar
        self.vsb = Scale(table, from_=self.to_sub, to=self.to_sub + len(self.Coos[0]) - 1, orient="vertical",
                         **Color_settings.My_colors.Scale_Base)
        self.vsb.grid(row=3, column=2, sticky="ns")
        self.vsb.bind("<ButtonRelease-1>", self.move_tree)

        self.vsbx = Scale(table, orient="horizontal",
                          command=partial(self.afficher_table, None, True), variable=self.Xpos, from_=1,
                          to=len(self.Vid.Identities), **Color_settings.My_colors.Scale_Base)
        self.vsbx.config()
        self.vsbx.grid(row=4, column=0, columnspan=2, sticky="ew")

        #NA button
        self.B_look_NA = Button(options1, text=self.Messages["Control17"], command=self.next_NA,
                                **Color_settings.My_colors.Button_Base)
        self.B_look_NA.config(background=Color_settings.My_colors.list_colors["NA_present"],
                              fg=Color_settings.My_colors.list_colors["Fg_NA_present"])
        self.B_look_NA.grid(row=0, column=0, sticky="ew")
        self.B_look_NA.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control19"]))
        self.B_look_NA.bind("<Leave>", self.HW.remove_tmp_message)
        self.calculate_NA()



        self.B_look_No_NA = Button(options1, text=self.Messages["Control_31"], command=lambda :self.next_NA(reverse=True),
                                **Color_settings.My_colors.Button_Base)
        self.B_look_No_NA.grid(row=0, column=1, sticky="ew")
        self.B_look_No_NA.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control_31_expl"]))
        self.B_look_No_NA.bind("<Leave>", self.HW.remove_tmp_message)


        #Button to change values for NA
        self.B_change_for_NA=Button(options1, text=self.Messages["Control20"], command=self.change_for_NA, **Color_settings.My_colors.Button_Base)
        self.B_change_for_NA.grid(row=1,columnspan=2,sticky="ew")
        self.B_change_for_NA.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control21"]))
        self.B_change_for_NA.bind("<Leave>", self.HW.remove_tmp_message)

        # Once the user selected a bunch of frames and a target, this button will create an interpolation of the target's coordinates over the selected frames.
        self.bouton_inter = Button(options2, text=self.Messages["Control5"], command=self.interpolate,
                                   **Color_settings.My_colors.Button_Base)
        self.bouton_inter.grid(row=0, column=0, sticky="we")
        self.bouton_inter.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control12"]))
        self.bouton_inter.bind("<Leave>", self.HW.remove_tmp_message)

        # After selecting a bunch of frames, this button will open a new window in which the user will be able to re-run part of the tracking with different parameters
        self.bouton_redo_track = Button(options2, text=self.Messages["Control6"], command=self.redo_tracking,
                                        **Color_settings.My_colors.Button_Base)
        self.bouton_redo_track.grid(row=0, column=1, sticky="we")
        self.bouton_redo_track.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control13"]))
        self.bouton_redo_track.bind("<Leave>", self.HW.remove_tmp_message)

        # If the user wants to do a manual tracking, we allow the possibility to add new individuals
        self.bouton_add_new = Button(options2, text=self.Messages["Control22"], command=self.add_ind,
                                     **Color_settings.My_colors.Button_Base)
        self.bouton_add_new.grid(row=0, column=2, sticky="we")
        self.bouton_add_new.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control23"]))
        self.bouton_add_new.bind("<Leave>", self.HW.remove_tmp_message)

        self.bouton_del_ind = Button(options2, text=self.Messages["Control24"],
                                     command=lambda: self.del_ind(ind=self.selected_ind),
                                     **Color_settings.My_colors.Button_Base)
        self.bouton_del_ind.grid(row=0, column=3, sticky="we")
        self.bouton_del_ind.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control25"]))
        self.bouton_del_ind.bind("<Leave>", self.HW.remove_tmp_message)

        #This allow to jump to potential problematic frame allowing user to treat the data faster
        self.bouton_next_pb = Button(options2, text=self.Messages["Control_32"],
                                     command=self.next_pb,
                                     **Color_settings.My_colors.Button_Base)
        self.bouton_next_pb.grid(row=0, column=4, sticky="we")
        self.bouton_next_pb.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control_32_expl"]))
        self.bouton_next_pb.bind("<Leave>", self.HW.remove_tmp_message)

        #

    def next_pb(self):
        Inds_to_check0=list(range(self.table_order[self.selected_ind],len(self.table_order)))+list(range(0, self.table_order[self.selected_ind]))+[self.table_order[self.selected_ind]]
        Inds_to_check=[self.table_order[ind] for ind in Inds_to_check0]
        found=0
        first=True
        for ind in Inds_to_check:
            Copy_Coos = self.Coos[ind].copy()
            if first:
                Copy_Coos = Copy_Coos[(self.Scrollbar.active_pos - self.to_sub + 1):len(Copy_Coos)]
                add=self.Scrollbar.active_pos - self.to_sub + 1
            else:
                add=0

            Copy_Coos[np.where(Copy_Coos == -1000)] = np.nan
            Dists = np.sqrt(np.diff(Copy_Coos[:, 0]) ** 2 + np.diff(Copy_Coos[:, 1]) ** 2) / float(self.Vid.Scale[0])
            Dists = np.append(np.nan, Dists)

            val=np.nanstd(Dists)/10

            Missing=[]

            kf = cv2.KalmanFilter(4, 1)
            kf.measurementMatrix = np.array([[1, 0, 0, 0]], np.float32)
            kf.transitionMatrix = np.array(
                [[1, 0, 1, 0], [0, 1, 0, 1], [0, 0,1, 0], [0, 0, 0, 1]], np.float32
            )
            kf.processNoiseCov = np.array(
                [[val, 0, 0, 0], [0, val, 0, 0], [0, 0, val, 0], [0, 0, 0, val]], np.float32
            ) * 0.5
            kf.measurementNoiseCov = np.array([[val]], np.float32)  # Adjusted noise covariance

            kf.statePre = np.zeros((4, 1), np.float32)
            kf.errorCovPre = np.eye(4, dtype=np.float32)

            for dist in range(len(Dists)-1):
                # Predict the next state
                kf.predict()
                if not np.isnan(Dists[dist]):
                    measurement=np.array([Dists[dist]], np.float32).reshape(1, 1)
                    kf.correct(measurement)
                    estimate = kf.statePost
                    estimate[0]=max(0, estimate[0])

                    # Calculate 95% confidence interval
                    P = kf.errorCovPost
                    error = P[0, 0]  # Standard deviation for x

                    if Dists[dist+1] > estimate[0] + (error * 100):
                        Missing.append(dist+1)
                        found=1
                        next_pos=Missing[0]-1 + add
                        new_ind=ind

                if found:
                    break

            first=False

        if found:
            self.Scrollbar.active_pos = next_pos + self.to_sub +1
            self.Scrollbar.refresh()
            self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)

            self.selected_ind=new_ind
            self.calculate_NA()
            self.ID_Entry.delete(0, END)
            self.ID_Entry.insert(0, self.Vid.Identities[self.selected_ind][1])  # Write the name of the target
            self.Arena_Lab.config(text=self.Vid.Identities[self.selected_ind][0])  # Write the name of the Arena
            self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])  # indicate the color of the new selected target

            self.afficher_table()
            self.Xpos.set(self.table_order.index(self.selected_ind)+ 1)
            self.modif_image(img=self.last_empty, redo=True)



    def afficher_table(self, actual_pos=None, redo=False, windowing=False, *args):
        #Display the interactive table with all the coordinates of the targets.
        #Headings
        try:
            self.tree
        except Exception as e:
            redo=True

        try:
            self.update_idletasks()
        except:
            pass

        self.table_heigh = round(self.container_table.winfo_height() / 20)

        if actual_pos==None:
            actual_pos=self.Scrollbar.active_pos #What are the row to show

        displayed_frame=self.Scrollbar.active_pos - self.to_sub #To avoid that the scrollbar position changes before the table is updated, the position of the displayed frame

        if actual_pos >= round(((self.Vid.Cropped[1][0] - 1) / self.Vid_Lecteur.one_every)) and actual_pos <= round(((self.Vid.Cropped[1][1] - 1) / self.Vid_Lecteur.one_every) + 1):
            if actual_pos - self.to_sub - int(self.table_heigh / 2) < 0:
                deb = -(actual_pos - self.to_sub)
            else:
                deb = -int(self.table_heigh / 2)

            if actual_pos - self.to_sub + int(self.table_heigh) > len(self.Coos[0]):
                redo=True #If there is not enought lines to be displayed, we redo the table with less rows
                end = len(self.Coos[0]) - (actual_pos - self.to_sub)
                deb = end - self.table_heigh
                if deb<0:
                    deb=0
            else:
                end = deb + self.table_heigh

            inds_to_show=list(range(self.Xpos.get()-1,min(self.Xpos.get()+10, len(self.table_order))))
            Present_now = np.where(self.Coos[:,(deb + actual_pos - self.to_sub ): (end + actual_pos - self.to_sub),0]>=0)[0]
            Present_now = list(np.unique(Present_now))

            if self.hide_missing:
                Present_now.sort()
                self.columns_to_hide_tmp=self.column_to_hide+[ind_supp for ind_supp in inds_to_show if ind_supp not in Present_now and ind_supp not in self.column_to_hide and ind_supp not in self.column_to_show]
                to_add=[ind_supp for ind_supp in inds_to_show if ind_supp not in Present_now and ind_supp in self.column_to_show and ind_supp]
                to_add.sort()
                Present_now = to_add + [P for P in Present_now if P in inds_to_show]
                Ind_to_show = Present_now + [ind_supp for ind_supp in inds_to_show if ind_supp not in Present_now]

            else:
                self.columns_to_hide_tmp=self.column_to_hide.copy()
                Ind_to_show = inds_to_show


            if redo:
                self.resize=False
                try:#If the tree is not created yet
                    self.tree.destroy()
                    self.tree.unbind_all("<Control-c>")
                    del self.tree
                except:
                   pass

               # Fill the table
                self.tree=ttk.Treeview(self.container_table, heigh=self.table_heigh)

                if windowing==1:
                    self.create_options()

                self.tree["columns"]=tuple(["Frame"]+["Ar_" +str(self.Vid.Identities[self.table_order[ind]][0])+ " " + str(self.Vid.Identities[self.table_order[ind]][1]) for ind in inds_to_show])
                self.tree.heading('#0', text='', anchor=CENTER)
                self.tree.column('#0', width=0, stretch=NO)
                self.tree.column("Frame", anchor=CENTER, width=int(self.container_table.winfo_width()/(len(self.Coos)+1)), minwidth=80, stretch=True)
                self.tree.heading("Frame", text=self.Messages["Frame"]+" | 🔍", anchor=CENTER)



            for ind in inds_to_show:
                ID = "Ar_" + str(self.Vid.Identities[self.table_order[ind]][0]) + " " + str(self.Vid.Identities[self.table_order[ind]][1])
                if ind in self.columns_to_hide_tmp:
                    self.tree.column(ID, anchor=CENTER, width=10, stretch=False)
                else:
                    self.tree.column(ID, anchor=CENTER, width=int(self.container_table.winfo_width() / (len(inds_to_show) + 1)), minwidth=120,stretch=True)

                self.tree.heading(ID, text=ID, anchor=CENTER)


            cnt = 0
            self.vals_in_table = []
            for row in range(deb, end):
                is_current=False
                is_NA=False
                is_stopped=False
                pos_in_coos = row + actual_pos - self.to_sub
                self.vals_in_table.append(pos_in_coos)
                if pos_in_coos==displayed_frame:
                    Rnum="=> " + str(row + actual_pos)
                    is_current=True
                else:
                    Rnum = str(row + actual_pos)

                try:
                    if row+actual_pos-self.to_sub in self.all_stops_verif:
                        is_stopped=True
                except:
                    pass




                Pos=[]
                for ind in inds_to_show:
                    if len(self.copied_cells)>0 and self.table_order[ind] == self.copied_cells[0] and pos_in_coos in self.copied_cells[1]:
                        copy_info=" ¦ "
                    else:
                        copy_info=""

                    if (self.table_order[ind] == self.selected_ind and pos_in_coos==displayed_frame):
                        if self.Coos[self.table_order[ind],row+actual_pos-self.to_sub,0]!=-1000:
                            Pos=Pos+["*" +copy_info+ str(round(self.Coos[self.table_order[ind],row+actual_pos-self.to_sub,0],2)) + " " + str(round(self.Coos[self.table_order[ind],row+actual_pos-self.to_sub,1],2)) +copy_info+ "*"]# + " - " + str(self.Coos[ind,row+actual_pos-self.to_sub,2])
                        else:
                            Pos = Pos + ["*"+copy_info+"NA NA"+copy_info+"*" ]#+ " - " + str(self.Coos[ind,row+actual_pos-self.to_sub,2])
                            is_NA=True
                    else:
                        if self.Coos[self.table_order[ind], row + actual_pos - self.to_sub, 0] != -1000:
                            Pos=Pos+[copy_info+str(round(self.Coos[self.table_order[ind],row+actual_pos-self.to_sub,0],2))+" "+str(round(self.Coos[self.table_order[ind],row+actual_pos-self.to_sub,1],2))+copy_info]#+ " - " + str(self.Coos[ind,row+actual_pos-self.to_sub,2])
                        else:
                            Pos = Pos + [copy_info+"NA NA"+copy_info ]#+ " - " + str(self.Coos[ind,row+actual_pos-self.to_sub,2])
                            is_NA=True

                new_row=[Rnum]+Pos

                try:
                    self.tree.insert(parent='', index=cnt, iid=cnt, text='', values=new_row)
                except:
                    self.tree.item(cnt, text='', values=new_row, tags=('NAs'))


                tags=[]
                if is_NA and not is_stopped:
                    tags.append("NAs")
                elif is_NA and is_stopped:
                    tags.append("Stopped_NA")
                elif not is_NA and is_stopped:
                    tags.append("Stopped")
                else:
                    tags.append("Normal")

                if is_current:
                    tags.append("Current")
                else:
                    tags.append("Not_Current")



                self.tree.item(cnt, tags=tags)

                cnt+=1


            if self.last_Ind_to_show!= Ind_to_show or redo:
                self.tree["displaycolumns"]=["Frame"]+["Ar_" + str(self.Vid.Identities[self.table_order[int(Ind_s)]][0]) + " " + str(self.Vid.Identities[self.table_order[int(Ind_s)]][1]) for Ind_s in Ind_to_show]

            self.tree.tag_configure('NAs', background=Color_settings.My_colors.list_colors["NAs"], foreground=Color_settings.My_colors.list_colors["Fg_NAs"])
            self.tree.tag_configure('Stopped_NA', background=Color_settings.My_colors.list_colors["Stopped_NA"],foreground=Color_settings.My_colors.list_colors["Fg_NAs"])
            self.tree.tag_configure('Stopped', background=Color_settings.My_colors.list_colors["Stopped"],foreground=Color_settings.My_colors.list_colors["Fg_NAs"])

            self.tree.tag_configure('Normal', background=Color_settings.My_colors.list_colors["Table1"], foreground=Color_settings.My_colors.list_colors["Fg_T1"])
            self.tree.tag_configure('Current', font=('Arial', 10, 'bold'))
            self.tree.tag_configure('Not_Current', font=('Arial', 10))
            self.tree.grid(row=0, column=0, sticky="nsew")


            #Allow interactions with the table
            self.bind_all_tree()
            self.tree.focus_set()

            self.show_can=Canvas(self.tree, width=10, heigh=10)
            self.show_can.grid(row=0, column=0)
            self.show_can.place(in_=self.tree, x=0, y=0, width=1, heigh=1)

            self.last_Ind_to_show = Ind_to_show.copy()

            new_sel=[rowID for rowID in range(len(self.vals_in_table)) if self.vals_in_table[rowID] in self.selected_rows]
            self.tree.selection_set(new_sel)

            self.update_idletasks()

            try:#If it is the first frame, the scrollbar is not created yey so raise an error
                self.vsb.set(actual_pos)#We move the scrollbar to the good position
            except:
                pass

    def hide_col(self, column):
        if column in self.columns_to_hide_tmp:
            try:
                self.column_to_hide.remove(column)
            except:
                pass
            self.column_to_show.append(column)

        else:
            self.column_to_hide.append(column)
            try:
                self.column_to_show.remove(column)
            except:
                pass
        self.afficher_table(redo=True)

    def reset_view(self, *args):
        self.column_to_show=[]
        self.column_to_hide = []
        self.afficher_table(redo=True)

    def move_tree(self, event):
        self.Scrollbar.active_pos=self.vsb.get()
        self.Scrollbar.refresh()
        self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)

    def interpolate(self, event=None, forced_type=-1):
        #The coordinates of the selected target are changed by a straight line between the first and last frames from the selection.
        if len(self.selected_rows)>2 and (forced_type==-1 or forced_type==0 or forced_type==5 or forced_type==6):
            if forced_type == 5:  # Selected frames, Arena
                list_inds= [idx for idx, Ind in enumerate(self.Vid.Identities) if Ind[0] == self.Vid.Identities[self.selected_ind][0]]

            elif forced_type == 6:  # Selected frames, Video
                list_inds= [idx for idx, Ind in enumerate(self.Vid.Identities)]

            else:
                list_inds=[self.selected_ind]

            for ind in list_inds:
                if (self.Coos[ind,self.selected_rows[0],0]!=-1000 or self.Coos[ind,self.selected_rows[-1],0]!=-1000):#Works only if the user selected more than 2 lines and not NAs in both first and last.
                    first=int(self.selected_rows[0])
                    last=int(self.selected_rows[-1])

                    add=0
                    if self.Coos[ind,self.selected_rows[0],0] == -1000:
                        first=last
                    elif self.Coos[ind,self.selected_rows[-1],0] == -1000:
                        last=first
                        add = 1

                    self.add_change("interpolate", ind, [first,last], self.Coos[ind,first:last].copy())

                    raws = np.asarray(self.selected_rows[0:len(self.selected_rows) - 1 + add], dtype=int)
                    den = (len(self.selected_rows) - 1)
                    t = (raws - first) / den
                    c_first = self.Coos[ind, first]
                    c_last = self.Coos[ind, last]

                    self.Coos[ind, raws, 0] = c_first[0] + (c_last[0] - c_first[0]) * t
                    self.Coos[ind, raws, 1] = c_first[1] + (c_last[1] - c_first[1]) * t

            self.calculate_NA()
            self.modif_image()

        elif len(self.selected_rows)<=2 or (forced_type>0 and forced_type<5):
            if forced_type<0:
                question = MsgBox.Messagebox(parent=self.main_frame.master,
                                                              message=self.Messages["Control29"],
                                                              Possibilities=[self.Messages["Control29A"],
                                                                             self.Messages["Control29B"],
                                                                             self.Messages["Control29C"]])
                self.wait_window(question)
                response=question.result
            else:
                response=forced_type-1

            if response==0:
                self.correct_NA(self.selected_ind)
            elif response==1:
                self.correct_NA()
            elif response==2:
                question = MsgBox.Messagebox(parent=self, title="",
                                             message=self.Messages["Control30"],
                                             Possibilities=[self.Messages["Yes"], self.Messages["No"]])
                self.wait_window(question)
                answer = question.result

                if answer==0:
                    for Vid in self.main_frame.liste_of_videos:
                        if Vid.Tracked:
                            Interpolate_all.interpolate_all(Vid)
                            self.Coos = CoosLS.load_coos(self.Vid, location=self)
                            self.selected_ind = 0
                            self.afficher_table(redo=True)
                            self.modif_image()

            elif response==3:
                for Ind in [idx for idx,Ind in enumerate(self.Vid.Identities) if Ind[0]==self.Vid.Identities[self.selected_ind][0]]:
                    self.correct_NA(Ind)

    def look_next(self, block, reverse):
        if not reverse:
            try:
                next_pb = block.index(-1000)
            except:
                next_pb = None

        else:
            try:
                next_pb = np.flatnonzero(np.array(block) > -1)[0]
            except:
                next_pb = None

        return(next_pb)


    def next_NA(self, reverse=False):
        # If the user want to jump toward the next NA value, move_to =True
        found = False
        first=True
        ind_done = 0
        skip_one=[False,False]
        cur_ind = self.selected_ind

        if (self.Coos[self.selected_ind, self.Scrollbar.active_pos - self.to_sub, 0]<-1 and not reverse) or (self.Coos[self.selected_ind, self.Scrollbar.active_pos - self.to_sub, 0]>-1 and reverse):
            skip_one=[True,False]

        while found == False and ind_done <= len(self.Coos):
            n0, n1, n2 = self.Coos.shape
            chunk_size = 10000
            if cur_ind==self.selected_ind and first:
                range_rows=range(self.Scrollbar.active_pos - self.to_sub+1,n1,chunk_size)
                first=False
            else:
                range_rows = range(0, n1, chunk_size)

            for i in range_rows:
                block = list(self.Coos[cur_ind, i:i + chunk_size, 0])  # only this part is loaded

                if not skip_one[0] or (skip_one[0] and skip_one[1]):
                    next_pb = self.look_next(block, reverse)
                else:
                    next_pb = self.look_next(block, not reverse)

                if not next_pb is None and skip_one[0] and not skip_one[1]:
                    skip_one[1]=True
                    tmp_next_pb=next_pb
                    next_pb = self.look_next(block[tmp_next_pb:len(block)], reverse)
                    if not next_pb is None:
                        next_pb+=tmp_next_pb

                if not next_pb is None:
                    next_pb+=i
                    new_ind=cur_ind
                    found=True
                    break

            ind_done += 1

            if self.table_order.index(cur_ind) + 1 >= len(self.table_order):
                cur_ind = self.table_order[0]
            else:
                cur_ind = self.table_order[self.table_order.index(cur_ind) + 1]

        if found:
            self.Scrollbar.active_pos = next_pb + self.to_sub
            self.Scrollbar.refresh()
            self.selected_ind=new_ind
            self.calculate_NA()

            self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)

            self.ID_Entry.delete(0, END)
            self.ID_Entry.insert(0, self.Vid.Identities[self.selected_ind][1])  # Write the name of the target
            self.Arena_Lab.config(text=self.Vid.Identities[self.selected_ind][0])  # Write the name of the Arena
            self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])  # indicate the color of the new selected target

            self.afficher_table()
            self.Xpos.set(self.table_order.index(self.selected_ind)+ 1)
            self.modif_image(img=self.last_empty, redo=True)

    def center_on_target(self):
        Zwidth = abs(self.Vid_Lecteur.zoom_sq[0] - self.Vid_Lecteur.zoom_sq[2])
        Zheight = abs(self.Vid_Lecteur.zoom_sq[1] - self.Vid_Lecteur.zoom_sq[3])
        non_na_indices = np.where(self.Coos[self.selected_ind,0:self.Scrollbar.active_pos - self.to_sub ,0] > -100)[0]

        if len(non_na_indices)>0:
            center = self.Coos[self.selected_ind, non_na_indices[-1]]
            #if (abs(center[0] -  round((self.Vid_Lecteur.zoom_sq[0] + self.Vid_Lecteur.zoom_sq[2]) / 2))> (Zwidth/4) )or (abs(center[1] -  round((self.Vid_Lecteur.zoom_sq[1] + self.Vid_Lecteur.zoom_sq[3]) / 2))> (Zheight/4)):
            if center[0] + round(Zwidth / 2) > self.Vid.shape[1]:
                self.Vid_Lecteur.zoom_sq[2] = self.Vid.shape[1]
                self.Vid_Lecteur.zoom_sq[0] = self.Vid.shape[1] - Zwidth
            elif center[0] - round(Zwidth / 2) < 0:
                self.Vid_Lecteur.zoom_sq[2] = Zwidth
                self.Vid_Lecteur.zoom_sq[0] = 0
            else:
                self.Vid_Lecteur.zoom_sq[0] = int(center[0] - round(Zwidth / 2))
                self.Vid_Lecteur.zoom_sq[2] = int(center[0] + round(Zwidth / 2))

            if center[1] + round(Zheight / 2) > self.Vid.shape[0]:
                self.Vid_Lecteur.zoom_sq[3] = self.Vid.shape[0]
                self.Vid_Lecteur.zoom_sq[1] = self.Vid.shape[0] - Zheight
            elif center[1] - round(Zheight / 2) < 0:
                self.Vid_Lecteur.zoom_sq[3] = Zheight
                self.Vid_Lecteur.zoom_sq[1] = 0
            else:
                self.Vid_Lecteur.zoom_sq[1] = int(center[1] - round(Zheight / 2))
                self.Vid_Lecteur.zoom_sq[3] = int(center[1] + round(Zheight / 2))

    def calculate_NA(self):
        try:  # Old versions of AnimalTA did not had the possibility to have a variable number of targets, this is to avoid compatibility problems
            if self.Vid.Track[1][8]:
                fixed = True
            else:
                fixed = False
        except:
            self.Vid.Track[1].append(False)
            fixed = True


        # If the user want to know how much NA there are
        positions = 0
        if fixed:
            possible_pos=len(self.Coos[0]*len(self.Coos))
        else:
            possible_pos=0

        for ind in range(len(self.Coos)):
            mask = self.Coos[ind,:,0] < -1  # only this part is loaded
            if not fixed:
                if mask.any():
                    first = mask.argmin()
                    last = len(mask) - 1 - mask[::-1].argmin()
                else:
                    first = last = None
                if first is None:
                    pass
                else:
                    possible_pos+=last-first
                    positions += np.sum(mask[first:last])
            else:
                positions += np.sum(mask)


        try:
            if positions == 0:
                self.B_look_NA.config(state="disable",fg=Color_settings.My_colors.list_colors["Fg_NA_absent"], activebackground=Color_settings.My_colors.list_colors["NA_absent"], background=Color_settings.My_colors.list_colors["NA_absent"], text=self.Messages["Control18"], disabledforeground=Color_settings.My_colors.list_colors["Fg_NA_absent"])
            else:
                self.B_look_NA.config(state="normal", fg=Color_settings.My_colors.list_colors["Fg_NA_present"], activebackground=Color_settings.My_colors.list_colors["NA_present"], background=Color_settings.My_colors.list_colors["NA_present"], text=self.Messages["Control17"].format(positions,possible_pos))
        except:
            pass


    def change_for_NA(self, type=0):
        if type==0:
            list_inds=[self.selected_ind]
        elif type==1:
            list_inds= [idx for idx, Ind in enumerate(self.Vid.Identities) if Ind[0] == self.Vid.Identities[self.selected_ind][0]] # Selected frames, Arena
        elif type == 2:
            list_inds = [idx for idx, Ind in enumerate(self.Vid.Identities)]  # Selected frames, Arena



        for ind in list_inds:
            #If the user wants to attribute NA values:
            old=self.Coos[ind, self.selected_rows, :].copy()
            self.Coos[ind, self.selected_rows, 0:2]=-1000
            self.calculate_NA()
            self.add_change("removed", ind, self.selected_rows,old)


        self.modif_image()
        self.afficher_table()

    def select_no_zoom(self, limits):
        selected_coords = self.Coos[self.selected_ind]

        condition = (
                (selected_coords[:, 0] > limits[0]) &
                (selected_coords[:, 0] < limits[2]) &
                (selected_coords[:, 1] > limits[1]) &
                (selected_coords[:, 1] < limits[3])
        )

        # Update the coordinates at these indices
        old = self.Coos[self.selected_ind][np.where(condition)[0]].copy()
        self.Coos[self.selected_ind][np.where(condition)[0]] = -1000
        self.add_change("removed", self.selected_ind, np.where(condition)[0], old)

        self.calculate_NA()
        self.afficher_table()
        self.modif_image(img=self.last_empty, redo=True)



    def load_Vid(self, new_Vid):
        #Load a video
        self.last_shown = None
        self.curcolumn = None

        try:#If there was already a video reader open, we close it
            self.Vid_Lecteur.proper_close()
        except:
            pass

        # Video and time-bar
        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=100)  ########NEW

        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=0)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Vid_Lecteur.speed.set(self.speed)
        self.Vid_Lecteur.change_speed()
        self.Scrollbar=self.Vid_Lecteur.Scrollbar
        self.last_empty = self.Vid_Lecteur.last_img.copy()

        if self.Vid.Stab[0]:
            self.prev_pts = self.Vid.Stab[1]

        #Difference in frame between the first frame of the video and the first frame of the table
        if self.Vid.Cropped[0]:
            self.to_sub = round(((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every))
        else:
            self.to_sub = 0

        #We import the coordinates
        self.Coos = CoosLS.load_coos(self.Vid, location=self)
        self.selected_ind=self.table_order[0]
        self.afficher_table(redo=True)

        #Representation of the tail
        if new_Vid!=None:
            self.Vid = new_Vid
        self.max_tail.set((self.Vid.Cropped[1][1]-self.Vid.Cropped[1][0])/self.Vid.Frame_rate[0])

        #We show the first frame:
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.to_sub)
        self.Scrollbar.active_pos=self.to_sub
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

        #Display new image when we change the size of the tail
        self.Scale_tail.config(to=self.max_tail.get(), command=self.modif_image)




    def add_ind(self, pos=-1, old_dat=[], old_ID=None, add_save=True):#If the user wants to add a new individual (only available for manual tracking)
        if old_ID==None:
            Arena = self.Vid.Identities[self.selected_ind][0]
            new_name=0
            all_names=[ind[1] for ind in self.Vid.Identities if ind[0]==Arena]

            found=False
            while not found:
                if "Ind" + str(new_name) not in all_names:
                    found=True
                else:
                    new_name+=1

            pos=0
            for Ind_pos in range(len(self.Vid.Identities)):
                if (self.Vid.Identities[Ind_pos][0]==Arena and pos==(len(self.Vid.Identities)-1)) or (self.Vid.Identities[Ind_pos][0]==Arena and self.Vid.Identities[Ind_pos+1][0]!=Arena):
                    pos += 1
                    break
                pos+=1

            self.Vid.Identities.insert(pos, [Arena,"Ind"+str(new_name),Diverse_functions.random_color()[0]])
            self.Vid.Sequences.insert(pos, [Interface_sequences.full_sequence])
            self.table_order.insert(pos, pos)
            #self.Vid.Morphometrics.insert(pos, [])
        else:
            Arena = old_ID[0][0]
            self.Vid.Identities.insert(pos, old_ID[0])
            self.Vid.Sequences.insert(pos, old_ID[1])
            for i in range(0, len(self.table_order)):
                if self.table_order[i]>=pos:
                    self.table_order[i] += 1
            self.table_order.insert(pos, pos)
            #self.Vid.Morphometrics.insert(pos, old_ID[2])


        if old_ID==None:
            empty_new_rows=np.zeros([len(self.Coos[0]),2], dtype="object")
            empty_new_rows.fill(-1000)
        else:
            empty_new_rows = old_dat

        self.Vid.Track[1][6][Arena]+=1
        self.Coos=np.insert(self.Coos, pos, empty_new_rows, axis=0)
        self.column_to_show.append(pos)
        self.selected_ind=pos
        self.calculate_NA()

        self.ID_Entry.delete(0, END)
        self.ID_Entry.insert(0, self.Vid.Identities[self.selected_ind][1])  # Write the name of the target
        self.Arena_Lab.config(text=self.Vid.Identities[self.selected_ind][0])  # Write the name of the Arena
        self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])  # indicate the color of the new selected target

        self.afficher_table(redo=True)
        self.vsbx.config(to=len(self.Vid.Identities))

        if add_save:
            self.add_change("add_ind",pos,None,None)

    def del_ind(self, ind, add_save=True, fus=False):
        self.column_to_hide=[col if (col<ind) else col-1 for col in self.column_to_hide if col != ind]
        self.column_to_show=[col if (col<ind) else col-1 for col in self.column_to_show if col != ind]

        Arena = self.Vid.Identities[ind][0]
        if len(self.Vid.Identities)>1:
            old=self.Coos[ind].copy()

            if add_save:
                self.add_change("delete_ind",ind,None,[old, [self.Vid.Identities[ind].copy(), self.Vid.Sequences[ind].copy()]])

            self.Vid.Identities.pop(ind)
            self.Vid.Sequences.pop(ind)
            for i in range(0, len(self.table_order)):
                if self.table_order[i]>self.table_order[ind]:
                    self.table_order[i] -= 1
            self.table_order.pop(ind)
            #self.Vid.Morphometrics.pop(ind)

            self.Vid.Track[1][6][Arena]-=1
            self.Coos=np.delete(self.Coos,ind,0)

            if not fus:
                self.selected_ind=ind
                if self.selected_ind >= len(self.Coos):
                    self.selected_ind = 0
                self.ID_Entry.delete(0, END)
                self.ID_Entry.insert(0, self.Vid.Identities[self.selected_ind][1])  # Write the name of the target
                self.Arena_Lab.config(text=self.Vid.Identities[self.selected_ind][0])  # Write the name of the Arena
                self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])  # indicate the color of the new selected target


            self.vsbx.config(to=len(self.Vid.Identities))
            self.Xpos.set(self.table_order.index(self.selected_ind)+ 1)


            self.calculate_NA()
            self.afficher_table(redo=True)

            self.modif_image()

    def do_Blancs(self, to_do):
        try:  # Old versions of AnimalTA did not had the possibility to have a variable number of targets, this is to avoid compatibility problems
            if self.Vid.Track[1][8]:
                fixed=True
            else:
                fixed=False
        except:
            self.Vid.Track[1].append(False)
            fixed=True

        self.Blancs = []

        pos = 0
        for col in to_do:
            self.Blancs.append([])
            pdt_blanc = FALSE
            for raw in range(len(self.Coos[col])):
                if self.Coos[col][raw][0] == -1000:
                    if pdt_blanc == FALSE:
                        Deb = raw
                        pdt_blanc = TRUE
                else:
                    if pdt_blanc:
                        self.Blancs[pos].append((Deb, raw))
                        pdt_blanc = FALSE
                if raw == (len(self.Coos[col]) - 1) and pdt_blanc:
                    self.Blancs[pos].append((int(Deb), int(raw)))
                    pdt_blanc = FALSE

            if not fixed and len(self.Blancs[pos]) > 0:
                if self.Blancs[pos][0][0] == 0:
                    self.Blancs[pos].pop(0)

                if len(self.Blancs[pos]) > 0:
                    if self.Blancs[pos][-1][1] == len(self.Coos[col]) - 1:
                        self.Blancs[pos].pop(-1)
            pos += 1

    def correct_NA(self, ind=None):
        if ind == None:
            to_do = range(len(self.Coos))
        else:
            to_do = [ind]

        self.do_Blancs(to_do)

        pos=0
        for col in to_do:
            for correct in self.Blancs[pos]:
                nb_raws = int(correct[1] - correct[0])
                if correct[0] != 0 and correct[1] != (len(self.Coos[col])-1):
                    for raw in range(correct[0], correct[1]+1):
                        self.Coos[col][raw][0] = self.Coos[col][correct[0] - 1][0] + ((self.Coos[col][correct[1]][0] - self.Coos[col][correct[0] - 1][0]) * ((raw - correct[0]) / nb_raws))
                        self.Coos[col][raw][1] = self.Coos[col][correct[0] - 1][1] + ((self.Coos[col][correct[1]][1] - self.Coos[col][correct[0] - 1][1]) * ((raw - correct[0]) / nb_raws))

                elif correct[0] == 0 and correct[1]!=(len(self.Coos[col])-1):
                    for raw in range(correct[0], correct[1]+1):
                        self.Coos[col][raw][0] = self.Coos[col][correct[1]][0]
                        self.Coos[col][raw][1] = self.Coos[col][correct[1]][1]

                elif correct[0] != 0 and correct[1]==(len(self.Coos[col])-1):
                    for raw in range(correct[0], correct[1]+1):
                        self.Coos[col][raw][0] = self.Coos[col][correct[0]-1][0]
                        self.Coos[col][raw][1] = self.Coos[col][correct[0]-1][1]
            pos+=1

        self.modif_image()
        self.calculate_NA()
        self.save_changes=[]
        self.copied_cells = []


    def draw_over(self, img, Xadd,Yadd,ratio):
        if self.Scrollbar.active_pos >= round(((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= round(self.Vid.Cropped[1][1]/self.Vid_Lecteur.one_every):
            if not self.Vid.Track[1][8]:
                corr_Ars=[]
                for Ar in self.Arenas_with_holes:
                    new_ar=Ar.copy()
                    new_ar=new_ar.reshape(-1, 2)
                    new_ar[:, 0]  +=Xadd
                    new_ar[:, 1] += Yadd
                    new_ar=new_ar/ratio
                    corr_Ars.append(new_ar.reshape(-1, 1, 2).astype(np.int32))
                cv2.drawContours(img, corr_Ars,-1,(150,0,200),3)

            window_length=min(int(self.tail_size.get()*self.Vid.Frame_rate[1]), int(self.Scrollbar.active_pos - self.to_sub))
            all_ind_available=np.where(self.Coos[:,self.Scrollbar.active_pos - self.to_sub-window_length:int(self.Scrollbar.active_pos - self.to_sub+1),0]>=0)[0]
            unique_inds = list(np.unique(all_ind_available))


            for ind in unique_inds:
                color=self.Vid.Identities[ind][2]

                if not self.show_all:
                    for prev in range(min(int(self.tail_size.get()*self.Vid.Frame_rate[1]), int(self.Scrollbar.active_pos - self.to_sub))):
                        if int(self.Scrollbar.active_pos - prev) > round(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every) and int(self.Scrollbar.active_pos) <= round(self.Vid.Cropped[1][1]/self.Vid_Lecteur.one_every):
                            if self.Coos[ind,int(self.Scrollbar.active_pos - 1 - prev - self.to_sub),0] != -1000 and self.Coos[ind,int(self.Scrollbar.active_pos - prev - self.to_sub),0] != -1000 :
                                TMP_tail_1 = (int((self.Coos[ind,int(self.Scrollbar.active_pos - 1 - prev - self.to_sub),0]+Xadd)/ratio),
                                              int((self.Coos[ind,int(self.Scrollbar.active_pos - 1 - prev - self.to_sub),1]+Yadd)/ratio))

                                TMP_tail_2 = (int((self.Coos[ind,int(self.Scrollbar.active_pos - prev - self.to_sub),0]+Xadd)/ratio),
                                              int((self.Coos[ind,int(self.Scrollbar.active_pos - prev - self.to_sub),1]+Yadd)/ratio))
                                cv2.line(img, TMP_tail_1, TMP_tail_2, color, 2)

                else:
                    for prev in range(1,int((self.Vid.Cropped[1][1]-self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)):
                        if self.Coos[ind,int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - 1 - prev - self.to_sub),0] != -1000 and \
                                self.Coos[ind,int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - prev - self.to_sub),0] != -1000:

                            TMP_tail_1 = (
                            int((self.Coos[ind,int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - 1 - prev - self.to_sub),0]+Xadd)/ratio),
                            int((self.Coos[ind,int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - 1 - prev - self.to_sub),1]+Yadd)/ratio))

                            TMP_tail_2 = (
                            int((self.Coos[ind,int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - prev - self.to_sub),0]+Xadd)/ratio),
                            int((self.Coos[ind,int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - prev - self.to_sub),1]+Yadd)/ratio))

                            cv2.line(img, TMP_tail_1, TMP_tail_2, color, 2)

                center=self.Coos[ind,self.Scrollbar.active_pos - self.to_sub].copy()
                if center[0]!=-1000:
                    center[0] = (center[0] + Xadd) / ratio
                    center[1] = (center[1] + Yadd) / ratio
                    if self.selected_ind==ind:
                        cv2.circle(img, (int(center[0]), int(center[1])), radius=6, color=(255,255,255),thickness=-1)
                        cv2.circle(img, (int(center[0]), int(center[1])), radius=5, color=(0,0,0), thickness=-1)
                    cv2.circle(img,(int(center[0]),int(center[1])),radius=3,color=color,thickness=-1)

            all_ind_available=np.where(self.Coos[:,self.Scrollbar.active_pos - self.to_sub,0]>=0)[0]
            all_ind_available = list(np.unique(all_ind_available))
            for ind in all_ind_available:
                if self.Scrollbar.active_pos - min(int(self.tail_size.get()*self.Vid.Frame_rate[1]), int(self.Scrollbar.active_pos - self.to_sub)) == round(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every) or self.show_all:
                    if self.Coos[ind,0,0]!=-1000:
                        cv2.circle(img,(int((self.Coos[ind,0,0]+Xadd)/ratio),int((self.Coos[ind,0,1]+Yadd)/ratio)),radius=1,color=(0,255,0),thickness=-1)

                if self.Scrollbar.active_pos  == round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) or self.show_all:
                    if self.Coos[ind,len(self.Coos[0])-1,0] != -1000:
                        cv2.circle(img, (int((self.Coos[ind,len(self.Coos[0])-1,0]+Xadd)/ratio), int((self.Coos[ind,len(self.Coos[0])-1,1]+Yadd)/ratio)),
                                             radius=1,color=(183,28,28), thickness=-1)


        if self.show_arenas:
            corr_Ars = []
            for Ar in self.Arenas_with_holes:
                new_ar = Ar.copy()
                new_ar = new_ar.reshape(-1, 2)
                new_ar[:, 0] += Xadd
                new_ar[:, 1] += Yadd
                new_ar = new_ar / ratio
                corr_Ars.append(new_ar.reshape(-1, 1, 2).astype(np.int32))

            cv2.drawContours(img, corr_Ars, -1, (255, 255, 255), 2)
            cv2.drawContours(img, corr_Ars, -1, (150, 0, 0), 2)
            for Ar in range(len(corr_Ars)):
                x, y, w, h = cv2.boundingRect(corr_Ars[Ar])
                (wT, hT), _ = cv2.getTextSize(str(Ar), fontFace=cv2.FONT_HERSHEY_DUPLEX,
                                            fontScale=1, thickness=4)
                # Name of arenas is written here
                cv2.putText(img, str(Ar), (
                x + int(w/2) - int(wT/2) + Xadd, y + int(h/2) + Yadd),
                                                 cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255),4)

                cv2.putText(img, str(Ar), (
                x + int(w/2) - int(wT/2) + Xadd, y + int(h/2)+ Yadd) ,
                                                 cv2.FONT_HERSHEY_DUPLEX, 1, (150, 0, 0),2)

        self.calculate_NA()




    def modif_image(self, img=[], actual_pos=None, redo=False, **args):
        #Draw trajectories on teh top of the frame to be displayed
        self.afficher_table(actual_pos=actual_pos, redo=redo)
        if self.locked_view:
            self.center_on_target()

        self.Vid_Lecteur.update_ratio()
        if len(img) <= 10:
            new_img=np.copy(self.last_empty)
        else:
            self.last_empty = np.copy(img)
            new_img = np.copy(img)

        if self.Vid.Stab[0]:
            new_img = Class_stabilise.find_best_position(Vid=self.Vid, Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=False, prev_pts=self.prev_pts)

        self.Vid_Lecteur.afficher_img(new_img, locked=self.locked_view)


    def mouse_over_tree(self, event):
        #This function allow to show the name of the column on top of which the user has the mouse
        self.remove_info()

        column = self.tree.identify_column(event.x)[1:]  # We identify which individual was linked to the mouseover column
        if column != "":
            columnint = int(column) - 2
            if self.column_catch is None:#If we are not moving a column
                if columnint >=0:
                    ind = int(self.last_Ind_to_show[columnint])
                    if ind in self.columns_to_hide_tmp:
                        self.info = Toplevel(self)
                        self.info.wm_overrideredirect(1)
                        self.info.wm_geometry("+%d+%d" % (self.tree.winfo_rootx()+event.x+20,self.tree.winfo_rooty()+event.y-20))
                        label = Label(self.info, text="Ar_" +str(self.Vid.Identities[self.table_order[ind]][0])+ " " + str(self.Vid.Identities[self.table_order[ind]][1]), justify=LEFT,
                                      background="#ffffe0", relief=SOLID, borderwidth=1,
                                      font=("tahoma", "8", "normal"))
                        label.grid()


    def remove_info(self, *args):
        try:
            self.info.destroy()
        except:
            pass

    def Initiate_drag(self, event):
        row=self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)[1:]
        if row == "" and int(column) !=1:
            self.column_catch= int(self.last_Ind_to_show[int(column)-2])

    def selectItem(self, event, Right=False, *args):
        #Triggered when the user click inside the table
        #We move the video reader to the frame on which the user clicked in the table.
        Ctrl = bool(event.state & 0x4)
        Shift = bool(event.state & 0x1)

        row=self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)[1:]  # We then identify which individual was linked to the pressed column
        if self.column_catch is None:
            if row!="" and not Right:#If the user pressed one row which is not the header, we move the video to the corresponding frame and update the selection
                row=int(row)

                self.Scrollbar.active_pos = self.vals_in_table[row]+self.to_sub
                self.Scrollbar.refresh()

                if Shift and not Ctrl:
                    if self.vals_in_table[row]>min(self.selected_rows):
                        self.selected_rows=list(range(min(self.selected_rows),self.vals_in_table[row]+1))
                    else:
                        self.selected_rows=list(range(self.vals_in_table[row], max(self.selected_rows)+1))
                else:
                    self.selected_rows=[self.vals_in_table[row]]

                self.Vid_Lecteur.update_image(self.vals_in_table[row] + self.to_sub, actual_pos=int(self.vsb.get()))

            if column!="":
                column=int(column)-2
                if column>=0:
                    ind = int(self.last_Ind_to_show[column])
                    if Right:#If right click on teh column name, we hide/show teh column
                        self.hide_col(ind)
                    elif Shift and not Ctrl and len(self.selected_rows)<2:
                        self.echange_traj(self.selected_ind,self.table_order[ind],self.Scrollbar.active_pos - self.to_sub)
                    elif Shift and Ctrl:
                        self.fus_inds(self.selected_ind,self.table_order[ind])
                    else:
                        self.selected_ind = self.table_order[ind]
                        self.ID_Entry.delete(0,END)
                        self.ID_Entry.insert(0, self.Vid.Identities[self.selected_ind][1])
                        self.Arena_Lab.config(text=self.Vid.Identities[self.selected_ind][0])
                        self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])
                        self.modif_image()
                        self.afficher_table()

                elif column==-1 and row=="":
                    self.ind_table_search()

        elif column!="":
            bbox = self.tree.bbox(0, int(column)-1)
            x_col, y_col, width, height = bbox
            relative_x = event.x - x_col
            percentage = relative_x / width  # value between 0.0 and 1.0
            new_pos=round(percentage+int(self.last_Ind_to_show[int(column)-2]))

            if new_pos<0:
                new_pos=0
            if new_pos!=self.column_catch:
                deleted_one=self.table_order[self.column_catch]
                self.table_order.pop(self.column_catch)

                if new_pos<self.column_catch:
                    self.table_order.insert(new_pos,deleted_one)
                else:
                    self.table_order.insert(new_pos-1, deleted_one)

                self.modif_image(redo=True)


        self.column_catch=None

    def ind_table_search(self, *args):
        if not self.searching:
            self.unbind_all_win()
            self.unbind_all_tree()
            self.Vid_Lecteur.unbindings()

            self.searching=True
            newWindow = Toplevel(self.parent.master)
            newWindow.wm_overrideredirect(1)
            newWindow.attributes("-topmost", True)
            x = self.master.winfo_pointerx()
            y = self.master.winfo_pointery()+15

            # Position Toplevel at the mouse
            newWindow.geometry(f"+{x}+{y}")

            def show_ind(*args):
                posible_inds = [idx for idx, ind in enumerate(self.Vid.Identities) if ind[0]==cur_arena.get() and var_name.get() in ind[1]]
                if len(posible_inds)>0:
                    self.Xpos.set(self.table_order.index(posible_inds[0])+ 1)
                    self.modif_image(img=self.last_empty, redo=True)

            Label(newWindow, text=self.Messages["Arena"]).grid(row=0, column=0)
            cur_arena=IntVar()
            cur_arena.set(0)
            spin = Spinbox(newWindow, from_=0, to=len(self.Arenas_with_holes)-1, textvariable=cur_arena, width=5, command=show_ind)
            spin.grid(row=0, column=1)

            Label(newWindow, text=self.Messages["Individual_short"]).grid(row=0, column=2)
            var_name=StringVar()
            entry=Entry(newWindow, textvariable=var_name)
            entry.grid(row=0, column=3)
            entry.focus_force()

            var_name.trace_add("write", show_ind)

            newWindow.bind("<Return>", lambda *args: newWindow.destroy())
            newWindow.grab_set()
            self.wait_window(newWindow)

            self.bind_all_win()
            self.bind_all_tree()
            self.Vid_Lecteur.bindings()
        self.searching=False




class Canvas_colors(Canvas):
    #This is a small canvas displaying a color chart for the user to select a color.
    def __init__(self, parent, ind, boss, **kwargs):
        Canvas.__init__(self, parent, bd=5, **kwargs)
        self.ind=ind
        self.boss=boss
        self.parent=parent
        self.parent.attributes('-toolwindow', True)

        #Paint the canvas with color chart
        H = np.array(list(range(180)), dtype="uint8")
        repetitions = 510
        H = np.transpose([H] * repetitions)

        S= np.array(list(range(0,255,1))+[255]*255, dtype="uint8")
        repetitions = 180
        S = np.tile(S, (repetitions, 1))

        V= np.array([255]*255 + list(range(255,0,-1)), dtype="uint8")
        repetitions = 180
        V = np.tile(V, (repetitions, 1))
        hsv = np.transpose([H, S, V], (1, 2, 0))
        bgr=cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        bgr=np.rot90(bgr, axes=(1,0))

        #Resize
        self.bgr=cv2.resize(bgr,(int(bgr.shape[0]/2),int(bgr.shape[1])))
        self.bgr2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.bgr))

        #Display color chart
        self.can_import = self.create_image(0,0, image=self.bgr2, anchor=NW)
        self.config(height=self.bgr.shape[0],width=self.bgr.shape[1])
        self.itemconfig(self.can_import, image=self.bgr2)
        self.update_idletasks()
        parent.update_idletasks()
        self.bind("<Button-1>", self.send)
        self.grid(sticky="nsew")

        self.stay_on_top()

    def send(self, event):
        #If the user click on the canvas, the coor of the pixel under the mouse at that moment is returned and the color chart is destroyed
        if event.y<self.bgr.shape[0] and event.x<self.bgr.shape[1]:
            old_col=self.boss.Vid.Identities[self.ind][2]
            self.boss.Vid.Identities[self.ind][2]=tuple([int(BGR) for BGR in self.bgr[event.y,event.x]])
            self.boss.modif_image()
            self.boss.Can_Col.config(background="#%02x%02x%02x" % self.boss.Vid.Identities[self.ind][2])
            self.boss.add_change("color", self.boss.selected_ind, None, old_col)
            self.unbind("<Button-1>")
            self.parent.destroy()

    def stay_on_top(self):
        #We want this window to always be on the top
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)
