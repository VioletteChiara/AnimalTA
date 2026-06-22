from tkinter import *
from tkinter import ttk
from AnimalTA.D_Tracking_process import Do_the_track, Tracking_method_selection
from AnimalTA.A_General_tools import Function_draw_arenas, UserMessages, Diverse_functions, Color_settings, Message_simple_question as MsgBox, Small_info, Class_loading_Frame
from AnimalTA.E_Post_tracking import Coos_loader_saver as CoosLS
from AnimalTA.E_Post_tracking.b_Analyses import Functions_Analyses_Speed, Interface_sequences, Functions_deformation, Body_part_functions
from AnimalTA.E_Post_tracking.b_Analyses.Functions_analyses import Functions_trajectory_summarise
from functools import partial
import copy
import os
import csv
import numpy as np
import cv2
import math
import shutil
import pickle
import pymsgbox
#import beepy
from tkinter import simpledialog
import traceback
import time

class Extend(Frame):
    """This frame is a list of all the videos. The user can select the ones to be tracked or analysed"""
    def __init__(self, parent, boss, type, any_tracked=False):
        Frame.__init__(self, parent, bd=5)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.boss=boss
        self.boss.unbind_all("<MouseWheel>")#We don't want the mouse wheel to move the project behind
        self.grid()
        self.list_vid=self.boss.liste_of_videos
        self.wait_visibility()
        self.grab_set()

        self.all_sel=False
        self.timer=0
        self.type=type

        #Import messages
        self.Messages = UserMessages.get_dict()
        self.urgent_close = False

        #We load the parameters
        Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
        with open(Param_file, 'rb') as fp:
            self.Params = pickle.load(fp)

        self.cache = False #The program is not minimised

        #The message displayed varies according to whether the user wants to track or analyse videos
        self.sel_state = StringVar()
        if type=="Analyses":
            self.winfo_toplevel().title(self.Messages["Do_anaT"])
            self.Explanation_lab = Label(self, text=self.Messages["Do_ana0"], wraplength=700, **Color_settings.My_colors.Label_Base)
        else:
            self.winfo_toplevel().title(self.Messages["Do_trackT"])
            self.Explanation_lab = Label(self, text=self.Messages["Do_track0"], wraplength=700, **Color_settings.My_colors.Label_Base)

        self.sel_state.set(self.Messages["ExtendB1"])
        self.Explanation_lab.grid(row=0,columnspan=2)

        #We propose the option to do a manual tracking (the program won't track the videos, just create an empty dataframe)
        self.manual_track=BooleanVar()
        if any_tracked or type=="Analyses":
            self.manual_track.set(False)
        else:
            self.manual_track.set(True)

        self.track_body_parts=BooleanVar()
        self.track_body_parts.set(False)


        under_opts=Frame(self,**Color_settings.My_colors.Frame_Base)
        under_opts.grid(row=1,column=0)


        self.Manual_ch=Checkbutton(under_opts, text=self.Messages["Do_track2"],variable=self.manual_track, onvalue=1, offvalue=0, command=partial(self.update_list, type), **Color_settings.My_colors.Checkbutton_Base)
        if type!="Analyses":#If we are using the tracking option, we propose the user to make a manual tracking
            self.Manual_ch.grid(row=0,column=0)
        Small_info.small_info(elem=self.Manual_ch, parent=self ,message=self.Messages["Small_info1"])

        self.Body_part_ch=Checkbutton(under_opts, text=self.Messages["Do_track5"],variable=self.track_body_parts, onvalue=1, offvalue=0, command=partial(self.update_list, type), **Color_settings.My_colors.Checkbutton_Base)
        if type!="Analyses":#If we are using the tracking option, we propose the user to make a manual tracking
            self.Body_part_ch.grid(row=0,column=1)



        #Button to select all
        self.bouton_sel_all=Button(self,textvariable=self.sel_state,command=self.select_all, **Color_settings.My_colors.Button_Base)
        self.bouton_sel_all.grid(row=2,columnspan=2)

        #List of videos
        self.yscrollbar = ttk.Scrollbar(self)
        self.yscrollbar.grid(row=3,column=1, sticky="ns")

        self.Liste=Listbox(self, selectmode = EXTENDED, yscrollcommand=self.yscrollbar.set, **Color_settings.My_colors.ListBox)
        self.Liste.config(height=15, width=150)
        self.yscrollbar.config(command=self.Liste.yview)

        Frame_buttons=Frame(self)
        Frame_buttons.grid(row=4,columnspan=2, column=0)
        self.bouton=Button(Frame_buttons,text=self.Messages["Validate"], width=20,command=self.validate, **Color_settings.My_colors.Button_Base)
        self.bouton.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.bouton.grid(row=0, column=0)

        self.bouton_cancel=Button(Frame_buttons,text=self.Messages["Cancel"], width=20,command=self.cancel, **Color_settings.My_colors.Button_Base)
        self.bouton_cancel.config(background=Color_settings.My_colors.list_colors["Cancel"],fg=Color_settings.My_colors.list_colors["Fg_Cancel"])
        self.bouton_cancel.grid(row=0, column=1)

        self.update_list(type=type)#According to the situation (manual or not, trcaking or analyses), we will propose different lists of videos

        self.Liste.grid(row=3,column=0)

        self.loading_canvas=Frame(self, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.loading_canvas.grid(row=5,columnspan=2)
        self.loading_state=Label(self.loading_canvas, text="", **Color_settings.My_colors.Label_Base)
        self.loading_state.grid(row=0, column=0)

        self.loading_bar=Canvas(self.loading_canvas, height=10, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill=Color_settings.My_colors.list_colors["Loading_before"])
        self.loading_bar.grid(row=0, column=1)

        #Minimize the window which processing
        self.bouton_hide = Button(self, text=self.Messages["Do_track1"], command=self.hide, **Color_settings.My_colors.Button_Base)
        self.focus()

        #Stop all process if the windows is closed
        self.parent.protocol("WM_DELETE_WINDOW", self.close)
        self.running=None#A variable used to determine if the tracking is running and to be able to stop it in the case of urgent close

    def update_list(self, type):
        self.list_vid_minus=[]
        self.Liste.delete(0, 'end')
        for i in range(len(self.list_vid)):#Only video that are ready for tracking can be choose if the user wants to do tracking. If user wants to analyse, only videos which are already tracked.
            if (type=="Tracking" and self.list_vid[i].Track[0]) or self.manual_track.get():
                if self.manual_track.get() or (not self.manual_track.get() and self.list_vid[i].Track[0]): #In case of manual tracking, there is no need for the tracking preparation of the videos
                    self.list_vid_minus.append(self.list_vid[i])
                    self.Liste.insert(i, self.list_vid[i].User_Name)

                    if self.list_vid[i].Tracked:
                        self.Liste.itemconfig(len(self.list_vid_minus)-1, {'fg': Color_settings.My_colors.list_colors["Fg_not_valide"]})
            elif type=="Analyses" and self.list_vid[i].Tracked:
                self.list_vid_minus.append(self.list_vid[i])
                self.Liste.insert(i, self.list_vid[i].User_Name)



    def select_all(self):
        #Sellect all the videos
        if not self.all_sel:
            self.Liste.select_set(0, END)
            self.sel_state.set(self.Messages["ExtendB2"])
            self.all_sel=True
        else:
            self.Liste.selection_clear(0, END)
            self.sel_state.set(self.Messages["ExtendB1"])
            self.all_sel=False

    def hide(self):
        #Minimise the prgram
        self.cache=True
        self.parent.wm_state('iconic')
        self.boss.parent.update_idletasks()
        self.boss.parent.overrideredirect(False)
        self.boss.parent.state('iconic')

    def cancel(self):
        self.boss.update_projects()
        self.boss.update_selections()
        self.boss.focus_set()
        self.boss.bind_all("<MouseWheel>", self.boss.on_mousewheel)
        self.parent.destroy()

    def validate(self):
        deb=time.time()
        #Run the tracking/analyses
        self.boss.save()
        self.grab_set()
        list_item = self.Liste.curselection()
        pos=0
        self.bouton.config(state="disable", **Color_settings.My_colors.Button_Base)
        self.bouton_sel_all.config(state="disable", **Color_settings.My_colors.Button_Base)
        self.Liste.config(state="disable", **Color_settings.My_colors.ListBox)
        self.bouton_cancel.config(state="disable", **Color_settings.My_colors.Button_Base)
        self.bouton_hide.grid(row=6)

        #all_times_dict=dict()

        if self.type=="Tracking":
            cur_vid=0
            for V in list_item:
                deb_unique=time.time()#Debugging!!!!
                try:
                    self.curr_vid=V
                    cleared=self.list_vid_minus[V].clear_files()
                    if self.list_vid_minus[V].Tracked:
                        try:#Old version of the program did not allow to change the number of individuals, also it didi not need to save those data
                            self.list_vid_minus[V].Track[1][6] = self.list_vid_minus[V].saved_repartition.copy()
                        except:
                            pass

                    if cleared:
                        pos+=1
                        self.boss.save()
                        self.grab_set()

                        self.loading_state.config(text= self.Messages["Video"] + " {act}/{tot}".format(act=cur_vid+1,tot=len(list_item)))
                        cur_vid+=1


                        if self.manual_track.get():
                            #If the user wants to make a manual tracking, we just create an empty dataset.
                            self.create_empty(self.list_vid_minus[V])

                            #We must then assign create the identities
                            self.list_vid_minus[V].Identities = []
                            self.list_vid_minus[V].Sequences = []

                            for Ar_inds in range(len(self.list_vid_minus[V].Track[1][6])):
                                for num in range(max(1,self.list_vid_minus[V].Track[1][6][Ar_inds])):
                                    self.list_vid_minus[V].Identities.append([Ar_inds, "Ind" + str(num),Diverse_functions.random_color()[0]])  # 0: identity of target, from 0 to N, 1: in which arene, 2:Name of the target, 3:Color of the target
                                    self.list_vid_minus[V].Sequences.append([Interface_sequences.full_sequence])
                            self.list_vid_minus[V].Tracked = True
                            self.list_vid_minus[V].saved_repartition = copy.deepcopy(self.list_vid_minus[V].Track[1][6])
                            self.list_vid_minus[V].Identities_saved=copy.deepcopy(self.list_vid_minus[V].Identities)
                            self.list_vid_minus[V].Sequences_saved = copy.deepcopy(self.list_vid_minus[V].Sequences)

                        else:
                            if self.list_vid_minus[V].Back[0]==1:
                                if self.list_vid_minus[V].Back[1].shape[0] != self.list_vid_minus[V].shape[0] or self.list_vid_minus[V].Back[1].shape[1] != self.list_vid_minus[V].shape[1]:
                                    self.list_vid_minus[V].Back[1] = cv2.resize(self.list_vid_minus[V].Back[1], [self.list_vid_minus[V].shape[1], self.list_vid_minus[V].shape[0]])

                            if self.list_vid_minus[V].Track[1][6][0]:
                                try:
                                    self.running="Normal"
                                    succeed=Tracking_method_selection.Choose_method(self, Vid=self.list_vid_minus[V], type="fixed", folder=self.boss.folder, head_tail=self.track_body_parts.get())
                                    self.running = None

                                    if succeed:
                                        self.list_vid_minus[V].Identities = []
                                        self.list_vid_minus[V].Sequences = []

                                        for Ar_inds in range(len(self.list_vid_minus[V].Track[1][6])):
                                            if self.track_body_parts.get() and self.list_vid_minus[V].Track[1][6][Ar_inds] == 1:
                                                for body in ["part0","part1"]:
                                                    self.list_vid_minus[V].Identities.append([Ar_inds, "Ind0" + "_"+str(body),Diverse_functions.random_color()[0]])  # 0: identity of target, from 0 to N, 1: in which arene, 2:Name of the target, 3:Color of the target
                                                    self.list_vid_minus[V].Sequences.append([Interface_sequences.full_sequence])
                                            else:
                                                for num in range(self.list_vid_minus[V].Track[1][6][Ar_inds]):
                                                    self.list_vid_minus[V].Identities.append([Ar_inds, "Ind" + str(num),Diverse_functions.random_color()[0]])  # 0: identity of target, from 0 to N, 1: in which arene, 2:Name of the target, 3:Color of the target
                                                    self.list_vid_minus[V].Sequences.append([Interface_sequences.full_sequence])
                                        self.list_vid_minus[V].saved_repartition=copy.deepcopy(self.list_vid_minus[V].Track[1][6])
                                        self.list_vid_minus[V].Identities_saved = copy.deepcopy(self.list_vid_minus[V].Identities)
                                        self.list_vid_minus[V].Sequences_saved = copy.deepcopy( self.list_vid_minus[V].Sequences)
                                        self.list_vid_minus[V].Tracked = True
                                        self.list_vid_minus[V].Track[0] = 1
                                    else:
                                        self.list_vid_minus[V].clear_files()
                                        self.list_vid_minus[V].Tracked=False

                                except Exception as e:
                                    question = MsgBox.Messagebox(parent=self, title=self.Messages["Do_trackWarnT1"],
                                                                 message=self.Messages["Do_trackWarn1"].format(self.list_vid_minus[V].User_Name,e),
                                                                 Possibilities=[self.Messages["Continue"]])
                                    self.wait_window(question)

                            else:
                                try:
                                    self.running = "Variable"
                                    succeed, Nb_targets= Tracking_method_selection.Choose_method(self, Vid=self.list_vid_minus[V], folder=self.boss.folder, type="variable", head_tail=self.track_body_parts.get())
                                    self.running = None
                                    if succeed:
                                        try:#For old version, Track stopped at [1][7]
                                            self.list_vid_minus[V].Track[1][8]=False
                                        except:
                                            self.list_vid_minus[V].Track[1].append(False)

                                        self.list_vid_minus[V].Identities = []
                                        self.list_vid_minus[V].Sequences = []

                                        min_1=False


                                        for Ar_inds in range(len(self.list_vid_minus[V].Track[1][6])):
                                            self.list_vid_minus[V].Track[1][6][Ar_inds]=len(Nb_targets[Ar_inds])
                                            for num in Nb_targets[Ar_inds]:
                                                min_1=True
                                                self.list_vid_minus[V].Identities.append([Ar_inds, "Ind" + str(num),Diverse_functions.random_color()[0]])  # 0: identity of target, from 0 to N, 1: in which arene, 2:Name of the target, 3:Color of the target
                                                self.list_vid_minus[V].Sequences.append([Interface_sequences.full_sequence])
                                        if not min_1:
                                            self.list_vid_minus[V].Identities.append([0, "Ind" + str(0), Diverse_functions.random_color()[0]])
                                            self.list_vid_minus[V].Sequences.append([Interface_sequences.full_sequence])
                                        self.list_vid_minus[V].saved_repartition = copy.deepcopy(self.list_vid_minus[V].Track[1][6])
                                        self.list_vid_minus[V].Identities_saved = copy.deepcopy(self.list_vid_minus[V].Identities)
                                        self.list_vid_minus[V].Sequences_saved = copy.deepcopy(self.list_vid_minus[V].Sequences)
                                        self.list_vid_minus[V].Tracked = True
                                        self.list_vid_minus[V].Track[0] = 1
                                    else:
                                        self.list_vid_minus[V].clear_files()
                                        self.list_vid_minus[V].Tracked=False


                                except Exception as e:
                                    question = MsgBox.Messagebox(parent=self, title=self.Messages["Do_trackWarnT1"],
                                                                 message=self.Messages["Do_trackWarn1"].format(self.list_vid_minus[V].User_Name,e),
                                                                 Possibilities=[self.Messages["Continue"]])
                                    self.wait_window(question)

                    if self.urgent_close:
                        break
                except Exception as e:
                    CustomDialog(self.master,
                                 text="The video couldn't be loaded:" + str(type(e).__name__) + " – " + str(e),
                                 title="Debugging")

                #all_times_dict[self.list_vid_minus[V].User_Name]=round(float(time.time() - deb_unique), 2)#Debuggind



            #Once the tracking is finished, we display a pop-up
            if not self.manual_track.get() and not self.urgent_close:
                try:
                    if self.Params["Sound_alert_track"]:
                        #beepy.beep(sound=6)
                        pass
                except:
                    pass

                try:
                    #For debugging!
                    #if self.Params["Pop_alert_track"]:
                    #    pymsgbox.alert(str(all_times_dict))


                    if self.Params["Pop_alert_track"]:
                        pymsgbox.alert(self.Messages["Do_track3"].format(round(float(time.time()-deb),2)),
                                       self.Messages["Do_track4"])
                except:
                    pass


        if self.type=="Analyses":
            Shapes_infos=dict()
            Time_inside = []

            general = os.path.join(self.list_vid_minus[0].Folder, "Results")
            Cleared1 = True
            if os.path.isdir(general):
                Cleared1=False
                while not Cleared1:
                    try:
                        os.rename(general, general)
                        shutil.rmtree(general)
                        Cleared1=True

                    except PermissionError as e:
                        question = MsgBox.Messagebox(parent=self, title=self.Messages["TError"],
                                                     message=self.Messages["Error_Permission"].format(e.filename),
                                                     Possibilities=[self.Messages["Retry"],
                                                                    self.Messages["Cancel"]])
                        self.wait_window(question)
                        answer = question.result

                        if not answer==0:
                            break

            if Cleared1:
                Cleared2=False
                while not Cleared2:
                    try:
                        os.makedirs(general)
                        Cleared2=True

                    except PermissionError as e:
                        question = MsgBox.Messagebox(parent=self, title=self.Messages["TError"],
                                                     message=self.Messages["Error_Permission"].format(e.filename),
                                                     Possibilities=[self.Messages["Retry"],
                                                                    self.Messages["Cancel"]])
                        self.wait_window(question)
                        answer = question.result

                        if not answer==0:
                            break

            if Cleared1 and Cleared2:
                try:
                    details=os.path.join(general, "Detailed_data")
                    os.makedirs(details)

                    #We first do the analyses by inds:
                    rows_inter_dists=[]
                    row_Arenas_coos=[]

                    #We check for the need of facultative files:
                    nb_cross=0
                    nb_stops_m=0
                    nb_stops_e=0
                    nb_moves_m=0
                    nb_moves_e=0
                    nb_explored = 0
                    for V in list_item:
                        Vid = self.list_vid_minus[V]
                        if Vid.Stops_Moves_options[0]["Mean_dur_stops"]:
                            nb_stops_m+=1
                        if Vid.Stops_Moves_options[0]["Mean_dur_moves"]:
                            nb_moves_m+=1
                        if Vid.Stops_Moves_options[0]["Events_dur_stops"]:
                            nb_stops_e+=1
                        if Vid.Stops_Moves_options[0]["Events_dur_moves"]:
                            nb_moves_e+=1
                        if Vid.Explored_complex:
                            nb_explored+=1


                    if nb_stops_e>0:
                        with open(os.path.join(self.list_vid_minus[0].Folder, "Results", "Stops.csv"), 'a', newline='', encoding="utf-8") as file_sm:
                            writer_sm = csv.writer(file_sm, delimiter=";")
                            writer_sm.writerow(["Video","Arena","Sequence","individual","Begin_stop","Duration_stop","Censored"])

                    if nb_moves_e>0:
                        with open(os.path.join(self.list_vid_minus[0].Folder, "Results", "Moves.csv"), 'a', newline='', encoding="utf-8") as file_sm:
                            writer_sm = csv.writer(file_sm, delimiter=";")
                            writer_sm.writerow(["Video","Arena","Sequence","individual","Begin_move","Duration_move","Censored"])


                    # To save the data chracteristic from the segments crosses
                    if os.path.isfile(os.path.join(self.list_vid_minus[0].Folder, "Results", "Summary_crosses.csv")):
                        os.remove(os.path.join(self.list_vid_minus[0].Folder, "Results", "Summary_crosses.csv"))

                    #Number of videos with morphometric analyses
                    Morpho=np.sum([self.list_vid_minus[V].Morphometrics for V in list_item])

                    try:
                        if Morpho>0:
                            with open(os.path.join(self.list_vid_minus[0].Folder, "Results", "Morphometrics.csv"), 'w',
                                      newline='', encoding="utf-8") as file_morpho:
                                writer_morpho = csv.writer(file_morpho, delimiter=";")
                                first_row = ["Video", "Arena", "Sequence", "Individual", "Area", "SD_Area",
                                             "Perimeter", "SD_Perimeter", "Length", "SD_Length", "Width",
                                             "SD_Width","Skel_length","SD_Skel_length","Sample_size","Skel_Sample_size"]
                                writer_morpho.writerow(first_row)
                    except Exception as e:
                        print(e)
                        pass



                    with open(os.path.join(self.list_vid_minus[0].Folder,"Results","Results_by_ind.csv"), 'w', newline='', encoding="utf-8") as file:
                        writer = csv.writer(file, delimiter=";")
                        columns=["Video", "Arena", "Sequence", "Individual","Beginning_seq","End_seq", "Prop_time_lost", "Smoothing_filter_window","Smoothing_Polyorder",
                                         "Moving_threshold", "Prop_time_moving", "Average_Speed", "Average_Speed_Moving", "Traveled_Dist", "Meander",
                                         "Traveled_Dist_Moving", "Meander_moving","Exploration_absolute_value","Exploration_relative_value","Exploration_method","Exploration_area","Exploration_aspect_param",
                                         "Mean_nb_neighbours", "Prop_time_with_at_least_one_neighbour", "Mean_shortest_interind_distance", "Mean_sum_interind_distances"]
                        if nb_explored>0:
                            columns = columns + ["Proportion_known_area"] + ["Time_spent_knowing_area"]
                        if nb_moves_m>0:
                            columns=columns+["Average_moves_duration"]
                        if nb_stops_m>0:
                            columns=columns+["Average_stops_duration"]

                        writer.writerow(columns)
                        cur_vid=0
                        for V in list_item:
                            self.loading_state.config(text=self.Messages["Video"] + " {act}/{tot}".format(act=cur_vid, tot=len(list_item)))
                            self.Vid=self.list_vid_minus[V]

                            #For old versions:
                            if len(self.Vid.Sequences) == 0:
                                self.Vid.Sequences = [[Interface_sequences.full_sequence.copy()] for id in range(len(self.Vid.Identities))]
                            #Before the self.Vid.Track[1][6][Area] was not matching the self.Vid.Identities (old versions):
                            for Ar in range(len(self.Vid.Track[1][6])):
                                self.Vid.Track[1][6][Ar]=len([i for i in self.Vid.Identities if i[0]==Ar])

                            #We first check if sequences were defined, if not, we create them
                            #We create the calculation class:
                            self.Coos=CoosLS.load_coos(self.Vid, location=self)
                            self.NB_ind = len(self.Vid.Identities)

                            self.Arenas = Function_draw_arenas.get_arenas(self.Vid)
                            chars=Functions_Analyses_Speed.Cnt_characteristics(self.Arenas, self.Vid.Scale[0])
                            for ArCh in range(len(chars)):
                                row_Arenas_coos.append([self.Vid.User_Name, ArCh] + chars[ArCh])

                            if len(self.Vid.Analyses[4][0]) > 0:
                                self.Coos = Functions_deformation.deform_coos(self.Coos, self.Vid.Analyses[4][0])

                            if self.Vid.Smoothed[0] != 0:
                                self.Coos = Diverse_functions.smooth_coos(Coos=self.Coos, window_length=self.Vid.Smoothed[0], polyorder=self.Vid.Smoothed[1])
                            for Area in range(len(self.Vid.Analyses[1])):#For each arena
                                self.loading_state.config( text=self.Messages["Video"] + " {act}/{tot} - ".format(act=cur_vid+1, tot=len(list_item)) +
                                                                self.Messages["Arena"]+ " {are}/{nb_are}".format(are=Area+1,nb_are=len(self.Vid.Analyses[1])))
                                self.timer=(0)
                                list_inds = np.array([[idx,Ind[1]] for idx,Ind in enumerate(self.Vid.Identities) if Ind[0] == Area])
                                self.show_load()

                                if len(list_inds)>0:
                                    if self.Vid.Track[1][6][Area] > 1:#First step is inter-individual distance (saved in "rows_inter_dists"), this is general data
                                        Pts_coos = []
                                        for ind in list_inds[:,0]:
                                            ind=int(ind)
                                            Pts_coos.append(self.Coos[ind])

                                        self.timer = (0.025)
                                        self.show_load()

                                        if len(self.Vid.Analyses)<4:
                                            self.Vid.Analyses.append(0)

                                        self.timer = (0.05)
                                        self.show_load()

                                        _, _, _, _, _, _, _, _, All_inter_dists = \
                                            Functions_Analyses_Speed.calculate_nei(Pts_coos=Pts_coos, ind=0,
                                                                     dist=self.Vid.Analyses[3],
                                                                     Scale=float(self.Vid.Scale[0]),
                                                                     Fr_rate=self.Vid.Frame_rate[1], to_save=True)

                                        # Inter-ind_dists by sequences:
                                        #We first identify the sequences that are similar for all the individuals of the same arena:
                                        list_kep_seqs=[]
                                        numbers_inds=[]
                                        for I in range(self.Vid.Track[1][6][Area]):
                                            ID=int(list_inds[:,0][I])

                                            #!! For old versions, we add general sequences
                                            if len(self.Vid.Sequences)<= ID:
                                                self.Vid.Sequences.append([Interface_sequences.full_sequence.copy()])
                                            if len(self.Vid.Sequences[ID]) == 0:
                                                self.Vid.Sequences[ID] = [Interface_sequences.full_sequence.copy()]

                                            # As we have some auto-sequences:

                                            Sequences_to_do = self.find_sequences(Area, ID)

                                            for Sequence in Sequences_to_do:
                                                if (Sequence[1][0]=="Beg" or Sequence[1][0]=="Time") and (Sequence[2][0]=="End" or Sequence[2][0]=="Time"):#If the sequence is not dependant of the individual's characteristics.
                                                    if Sequence[0] in [See[0] for See in list_kep_seqs]:
                                                        pos=[See[0] for See in list_kep_seqs].index(Sequence[0])
                                                        numbers_inds[pos]+=1
                                                    else:
                                                        list_kep_seqs.append(Sequence)
                                                        numbers_inds.append(1)

                                        self.timer = (0.07)
                                        self.show_load()

                                        if len(numbers_inds)>0:
                                            for S in reversed(list(range(len(numbers_inds)))):
                                                if numbers_inds[S]<self.Vid.Track[1][6][Area]:
                                                    list_kep_seqs.pop(S)

                                            for Sequence in list_kep_seqs:
                                                res, limits = Interface_sequences.find_limits(Sequence, self.Vid, ID, None, [], [])

                                                if res:
                                                    deb, end = limits
                                                    Pts_coos = []
                                                    for ind in list_inds[:, 0]:
                                                        ind = int(ind)
                                                        Pts_coos.append(self.Coos[ind, deb:end + 1])


                                                    if self.Vid.Group_data["Exploration"] or self.Vid.Group_data["Interind_data"]:
                                                        row_for_inter_dists=[self.Vid.User_Name, str(Sequence[0]), Area]

                                                        if self.Vid.Group_data["Interind_data"]:
                                                            Mean, Min, Max = Functions_Analyses_Speed.calculate_all_inter_dists(
                                                                Pts_coos=Pts_coos, Scale=float(self.Vid.Scale[0]))
                                                            row_for_inter_dists=row_for_inter_dists+[Mean, Min, Max]




                                                        #Create a group exploration value
                                                        if self.Vid.Group_data["Exploration"]:
                                                            firstmap=True
                                                            load_frame = Class_loading_Frame.Loading(self, text="Group exploration")  # Progression bar
                                                            load_frame.grid()
                                                            if self.Vid.Analyses[2][0]==0:
                                                                for I in range(len(list_inds)):  # Individual's caracteristics
                                                                    info_load = [load_frame, I, len(list_inds)]
                                                                    ID = int(list_inds[:, 0][I])
                                                                    if not self.Vid.Track[1][8]:
                                                                        save_pos = np.where(self.Coos[ID][:, 0] != -1000)
                                                                        if len(save_pos[0]) > 0:
                                                                            first = save_pos[0][0]
                                                                            last = save_pos[0][-1]
                                                                            This_coos = self.Coos[ID][first:(last + 1)].copy()
                                                                        else:
                                                                            This_coos = self.Coos[ID][0:1].copy()

                                                                    else:
                                                                        first = 0
                                                                        This_coos = self.Coos[ID].copy()

                                                                    new_val, map =Functions_Analyses_Speed.calculate_exploration(self.Vid.Analyses[2],
                                                                                                                   self.Vid, This_coos,
                                                                                                                   deb, end,
                                                                                                                   self.Arenas[Area],show=True, only_vals=False, load_frame=info_load)

                                                                    if firstmap:
                                                                        combined_map=map
                                                                        firstmap=False
                                                                    else:
                                                                        combined_map=cv2.bitwise_or(combined_map,map)

                                                                mask_glob = Function_draw_arenas.draw_mask(self.Vid)
                                                                mask = np.zeros([self.Vid.shape[0], self.Vid.shape[1], 1], np.uint8)
                                                                mask = cv2.drawContours(mask, [self.Arenas[Area]], -1, (255), -1)
                                                                mask = cv2.bitwise_and(mask, mask_glob)

                                                                absolute=np.sum(combined_map > [0]) * (1 / float(self.Vid.Scale[0]) ** 2)  # We want to save the total surface explored (independantly of the size of the arena)
                                                                relative=len(np.where(combined_map > [0])[0]) / len(np.where(mask == [255])[0])  # Now relative to the arena area

                                                            else:
                                                                for I in range(len(list_inds)):  # Individual's caracteristics
                                                                    info_load = [load_frame, I, len(list_inds)]
                                                                    ID = int(list_inds[:, 0][I])
                                                                    if not self.Vid.Track[1][8]:
                                                                        save_pos = np.where(
                                                                            self.Coos[ID][:, 0] != -1000)
                                                                        if len(save_pos[0]) > 0:
                                                                            first = save_pos[0][0]
                                                                            last = save_pos[0][-1]
                                                                            This_coos = self.Coos[ID][
                                                                                        first:(last + 1)].copy()
                                                                        else:
                                                                            This_coos = self.Coos[ID][0:1].copy()

                                                                    else:
                                                                        first = 0
                                                                        This_coos = self.Coos[ID].copy()

                                                                    cells = Functions_Analyses_Speed.calculate_exploration(
                                                                        self.Vid.Analyses[2],
                                                                        self.Vid, This_coos,
                                                                        deb, end,
                                                                        self.Arenas[Area], show=False, only_vals=False,
                                                                        load_frame=info_load, return_cell=True)[1]

                                                                    cells_in=cells[0]

                                                                    XYs = cells_in[~np.isnan(cells_in).any(axis=1)]
                                                                    XYs = np.int32(XYs)
                                                                    unique = np.unique(XYs, axis=0, return_counts=False)

                                                                    if firstmap:
                                                                        combined_cells=unique
                                                                        firstmap=False
                                                                    else:
                                                                        combined_cells= np.vstack((combined_cells, unique))
                                                                        combined_cells=np.unique(combined_cells, axis=0, return_counts=False)

                                                                absolute=len(combined_cells)
                                                                relative=len(combined_cells)/cells[1]


                                                            row_for_inter_dists = row_for_inter_dists + [absolute, relative]
                                                            load_frame.destroy()

                                                        rows_inter_dists.append(row_for_inter_dists)

                                                    liste_nb_nei, liste_is_close, liste_min_dist_nei, sum_dists, table_all_dists, table_is_close, table_nb_contacts, all_events_contacts, All_inter_dists_t = \
                                                        Functions_Analyses_Speed.calculate_nei(Pts_coos=Pts_coos, ind=0, dist=self.Vid.Analyses[3], Scale=float(self.Vid.Scale[0]), Fr_rate=self.Vid.Frame_rate[1], to_save=True)

                                                    main_folder=os.path.join(self.Vid.Folder, "Results","InterInd")
                                                    if not os.path.isdir(main_folder):
                                                        os.makedirs(main_folder)

                                                    vid_folder=os.path.join(main_folder, self.Vid.User_Name)
                                                    if not os.path.isdir(vid_folder):
                                                        os.makedirs(vid_folder)

                                                    Name= "Video_" + str(self.Vid.User_Name) + "__" + "Arena_" + str(Area) + "__Sequence_" + str(Sequence[0]) + "__Distances"
                                                    with open(os.path.join(vid_folder, Name+".csv"), 'w',newline='', encoding="utf-8") as file:
                                                        writerb = csv.writer(file, delimiter=";")
                                                        writerb.writerow(["X"]+list(list_inds[:,1]))
                                                        for row in range(len(table_all_dists)):
                                                            First_cell=[list_inds[:,1][row]]
                                                            Row=list(table_all_dists[row])
                                                            writerb.writerow(First_cell+Row)

                                                    Name= "Video_" + str(self.Vid.User_Name) + "__" + "Arena_" + str(Area) + "__Sequence_" + str(Sequence[0]) + "__PropTime"
                                                    with open(os.path.join(vid_folder, Name+".csv"), 'w',newline='', encoding="utf-8") as file:
                                                        writerb = csv.writer(file, delimiter=";")
                                                        writerb.writerow(["X"]+list(list_inds[:,1]))
                                                        for row in range(len(table_is_close)):
                                                            First_cell=[list_inds[:,1][row]]
                                                            Row=list(table_is_close[row])
                                                            writerb.writerow(First_cell+Row)

                                                    Name= "Video_" + str(self.Vid.User_Name) + "__" + "Arena_" + str(Area) + "__Sequence_" + str(Sequence[0]) + "__Contact_occurences"
                                                    with open(os.path.join(vid_folder, Name+".csv"), 'w',newline='', encoding="utf-8") as file:
                                                        writerb = csv.writer(file, delimiter=";")
                                                        writerb.writerow(["X"]+list(list_inds[:,1]))
                                                        for row in range(len(table_nb_contacts)):
                                                            First_cell=[list_inds[:,1][row]]
                                                            Row=list(table_nb_contacts[row])
                                                            writerb.writerow(First_cell+Row)

                                                    Name= "Video_" + str(self.Vid.User_Name) + "__" + "Arena_" + str(Area) + "__Sequence_" + str(Sequence[0]) + "__Contact_events"
                                                    with open(os.path.join(vid_folder, Name+".csv"), 'w',newline='', encoding="utf-8") as file:
                                                        writerb = csv.writer(file, delimiter=";")
                                                        writerb.writerow(["Ind_P1","Ind_P2","Duration","Beginning"])
                                                        cn=0
                                                        for row in range(len(all_events_contacts)):
                                                            all_events_contacts=sorted(all_events_contacts, key=lambda x: x[3])
                                                            all_events_contacts[row][0],all_events_contacts[row][1]=list_inds[:,1][all_events_contacts[row][0]],list_inds[:,1][all_events_contacts[row][1]]
                                                            writerb.writerow(all_events_contacts[row])
                                                            cn+=1

                                        self.timer = (0.1)
                                        self.show_load()

                                    self.timer = (0.1)
                                    self.show_load()


                                    for I in range(len(list_inds)):#Individual's caracteristics
                                        self.timer = ((I / len(list_inds)) * (7 / 10) + (0.1))
                                        self.show_load()
                                        ID=int(list_inds[:,0][I])


                                        if not self.Vid.Track[1][8]:
                                            save_pos=np.where(self.Coos[ID][:,0] != -1000)
                                            if len(save_pos[0])>0:
                                                first=save_pos[0][0]
                                                last=save_pos[0][-1]
                                                This_coos = self.Coos[ID][first:(last + 1)].copy()
                                            else:
                                                This_coos=self.Coos[ID][0:1].copy()

                                        else:
                                            first=0
                                            This_coos=self.Coos[ID].copy()

                                        #A supprimer!!!
                                        '''                                        
                                        all_vals = Interface_sequences.compute_details_explo(self.Vid.Analyses[2],
                                                                                 Vid=self.Vid, ID=ID,
                                                                                 Coos=self.Coos[0], memory=[0,0.5,1,2,3,4,5,6,7,8,9,10,15,20])

                                        print("Saving")
                                        with open(os.path.join(self.Vid.Folder, "Results_exploration_complete.csv"), 'a', newline='', encoding="utf-8") as file_ex:
                                            writer_ex = csv.writer(file_ex, delimiter=";")
                                            for row in all_vals:
                                                writer_ex.writerow([self.Vid.User_Name,2]+row)
                                        '''

                                        Copy_Coos = np.array(This_coos)
                                        Copy_Coos[np.where(Copy_Coos == -1000)] = np.nan

                                        sub_load = Class_loading_Frame.Loading(self, text=self.Messages["Do_track6"])
                                        sub_load.grid()
                                        Details, State, Dists, Speeds, Meanders, All_explored_values_cum, All_explored_values_bin = Functions_trajectory_summarise.prepare_details(Copy_Coos, Area, self.Vid, first, self.Arenas, loading_frame=sub_load)
                                        sub_load.grid_forget()
                                        del sub_load


                                        Sequences_to_do = self.find_sequences(Area, ID)

                                        if "Explo" in [seq[1][0] for seq in Sequences_to_do] or "Explo" in [seq[2][0] for seq in Sequences_to_do]:
                                            relative_explo, summary_explo=Interface_sequences.compute_explo(
                                                method=self.Vid.Analyses[2], Vid=self.Vid, Coos=np.array(This_coos),
                                                ID=ID, loading_parent=self,send_summary=True, prev_summary=None)
                                        else:
                                            summary_explo=[]

                                        if len(Sequences_to_do)==0:
                                            Sequences_to_do=[Interface_sequences.full_sequence.copy()]

                                        for Sequence in Sequences_to_do:
                                            new_row=[self.Vid.User_Name, Area]
                                            if not self.Vid.Track[1][8]:
                                                res, limits = Interface_sequences.find_limits(Sequence, self.Vid, ID, summary_explo, Copy_Coos, [first,last])
                                            else:
                                                res, limits = Interface_sequences.find_limits(Sequence, self.Vid, ID, summary_explo, Copy_Coos, [])


                                            new_row.append(Sequence[0])
                                            new_row.append(list_inds[I][1])

                                            if res:
                                                deb, end = limits

                                                if not self.Vid.Track[1][8]:
                                                    new_row.append(round((deb+first) / self.Vid.Frame_rate[1],2))
                                                    new_row.append(round((end+first) / self.Vid.Frame_rate[1],2))
                                                else:
                                                    new_row.append(round(deb / self.Vid.Frame_rate[1],2))
                                                    new_row.append(round(end / self.Vid.Frame_rate[1],2))

                                                #Time lost
                                                new_row.append(len(np.where(np.isnan(Copy_Coos[deb:end+1,0]))[0])/ len(Copy_Coos[deb:end+1,0]))

                                                #Smoothing_parameters:
                                                if self.Vid.Smoothed[0]!="NA":
                                                    new_row.append(self.Vid.Smoothed[0])
                                                    new_row.append(self.Vid.Smoothed[1])
                                                else:
                                                    new_row.append("NA")
                                                    new_row.append("NA")

                                                # Moving threshold:
                                                new_row.append(self.Vid.Analyses[0])

                                                #Time moving:
                                                if len(np.where(np.logical_not(np.isnan(State[deb:end+1])))[0])>0:
                                                    new_row.append(len(np.where(State[deb:end+1]>0)[0])/len(np.where(np.logical_not(np.isnan(State[deb:end+1])))[0]))
                                                else:
                                                    new_row.append("NA")

                                                #Average speed:
                                                new_row.append(np.nanmean(Speeds[deb:end+1]))

                                                #Average speed while moving:
                                                new_row.append(np.nanmean(Speeds[deb:end+1][np.where(State[deb:end+1]>0)]))

                                                #distance traveled
                                                new_row.append(np.nansum(Dists[deb:end+1]))
                                                # Meander
                                                new_row.append(np.nanmean(Meanders[deb:end+1]))

                                                #Traveled distance while moving:
                                                new_row.append(np.nansum(Dists[deb:end+1][np.where(State[deb:end+1]>0)]))
                                                # Meander moving
                                                new_row.append(np.nanmean(Meanders[deb:end+1][np.where(State[deb:end+1]>0)]))

                                                #Spatial:
                                                Behav_Shape=[]
                                                #Events_Ind = [Behav for Behav in self.Vid.Events if Behav[1] == ID]
                                                All_crosses = []#For Srikrishna
                                                for Shape in self.Vid.Analyses[1][Area]:
                                                    if Shape[0]!="Line":
                                                        if Shape[0]=="Point":
                                                            Dist_to, Inside = Functions_Analyses_Speed.details_Point(Copy_Coos[:, 0],Copy_Coos[:, 1],Shape,float(self.Vid.Scale[0]))

                                                        elif Shape[0]=="All_borders":
                                                            Dist_to, Inside = Functions_Analyses_Speed.details_All_borders(Copy_Coos[:, 0], Copy_Coos[:, 1],Shape, self.Arenas[Area], float(self.Vid.Scale[0]))

                                                        elif Shape[0]=="Borders":
                                                            Dist_to, Inside = Functions_Analyses_Speed.details_Borders(Copy_Coos[:, 0], Copy_Coos[:, 1],Shape, float(self.Vid.Scale[0]))

                                                        elif Shape[0] == "Ellipse" or Shape[0] == "Rectangle" or Shape[0] == "Polygon":
                                                            Dist_to, Inside = Functions_Analyses_Speed.details_shape(Copy_Coos[:, 0], Copy_Coos[:, 1],Shape, float(self.Vid.Scale[0]), self.Vid, self.Arenas[Area])

                                                        Mean_dist=np.nanmean(Dist_to[deb:end+1])

                                                        if len(np.where(Inside[deb:end+1]>0)[0])>0:
                                                            Latency=np.where(Inside[deb:end+1]>0)[0][0] / self.Vid.Frame_rate[1]
                                                            # If an individual is lost inside and found back inside: was inside during this time
                                                            Inside_fixed = Functions_Analyses_Speed.correct_Inside(Inside, deb, end)

                                                            Absolute_time_inside = len(np.where(Inside_fixed[deb:end+1] > 0)[0]) / \
                                                                                   self.Vid.Frame_rate[1]
                                                            Prop_Time_inside = len(np.where(Inside_fixed[deb:end+1] > 0)[0]) / len(
                                                                np.where(np.logical_not(np.isnan(Inside_fixed[deb:end+1])))[0])
                                                            Nb_entries = len(np.where(np.diff(Inside_fixed[deb:end+1]) > 0)[0])
                                                            if Inside_fixed[deb:end+1][0] > 0:
                                                                Nb_entries += 1

                                                            Prop_Time_lost_in = len(
                                                                np.where(np.isnan(Copy_Coos[deb:end+1, 0][np.where(Inside_fixed[deb:end+1] > 0)[0]]))[
                                                                    0]) / len(Copy_Coos[deb:end+1, 0][np.where(Inside_fixed[deb:end+1] > 0)[0]])

                                                            Inside_transitions = np.append(np.nan, np.diff(Inside[deb:end+1]))

                                                            if len(np.where(np.logical_not(np.isnan(State[deb:end+1][np.where((Inside[deb:end+1] > 0) & (Inside_transitions != 1))])))[0]) >0:
                                                                Mean_time_moving_in = len(
                                                                    np.where(State[deb:end+1][np.where((Inside[deb:end+1] > 0) & (Inside_transitions != 1))] > 0)[
                                                                        0]) / len(np.where(np.logical_not(
                                                                    np.isnan(State[deb:end+1][np.where((Inside[deb:end+1] > 0) & (Inside_transitions != 1))])))[
                                                                                      0])
                                                            else:
                                                                Mean_time_moving_in = "NA"

                                                            Distance_traveled_in = np.nansum(
                                                                Dists[deb:end+1][np.where((Inside[deb:end+1] > 0) & (Inside_transitions != 1))])
                                                            Distance_traveled_moving_in = np.nansum(
                                                                Dists[deb:end+1][np.where((Inside[deb:end+1] > 0) & (Inside_transitions != 1) & (State[deb:end+1] > 0))])

                                                            Speed_in = np.nanmean(
                                                                Speeds[deb:end+1][np.where((Inside[deb:end+1] > 0) & (Inside_transitions != 1))])
                                                            Speed_moving_in = np.nanmean(Speeds[deb:end+1][np.where(
                                                                (Inside[deb:end+1] > 0) & (State[deb:end+1] > 0) & (Inside_transitions != 1))])

                                                            Meander_in = np.nanmean(
                                                                Meanders[deb:end+1][np.where((Inside[deb:end+1] > 0) & (Inside_transitions != 1))])
                                                            Meander_moving_in = np.nanmean(Meanders[deb:end+1][np.where(
                                                                (Inside[deb:end+1] > 0) & (State[deb:end+1] > 0) & (Inside_transitions != 1))])


                                                        else:
                                                            Latency="NA"
                                                            Absolute_time_inside=0
                                                            Prop_Time_inside=0
                                                            Nb_entries=0
                                                            Prop_Time_lost_in="NA"
                                                            Mean_time_moving_in=0
                                                            Distance_traveled_in=0
                                                            Distance_traveled_moving_in=0
                                                            Speed_in="NA"
                                                            Speed_moving_in="NA"
                                                            Meander_in="NA"
                                                            Meander_moving_in="NA"

                                                        res_cnt, Shape_cnt, res_cnt_clean, Shape_cnt_clean=Functions_Analyses_Speed.draw_shape(self.Vid, self.Arenas[Area], Shape)

                                                        if res_cnt_clean:
                                                            Exploration_in = Functions_Analyses_Speed.calculate_exploration(self.Vid.Analyses[2], self.Vid, This_coos, deb, end, Shape_cnt_clean)[0]#Absolute, relative, method, area, param aspect
                                                        else:
                                                            if self.Vid.Analyses[2][0]==0:
                                                                method="Modern"
                                                                param3="NA"
                                                            elif self.Vid.Analyses[2][0]==1:
                                                                method = "Squares_mesh"
                                                                param3 = "NA"
                                                            elif self.Vid.Analyses[2][0]==2:
                                                                method = "Circular_mesh"
                                                                param3 = "NA"

                                                            Exploration_in=["NA","NA", method, self.Vid.Analyses[2][1],param3]

                                                        if Shape[3] in Shapes_infos:
                                                            Shapes_infos[Shape[3]].append([self.Vid.User_Name, Area, Sequence[0], list_inds[I][1], Mean_dist,Latency,Prop_Time_inside, Absolute_time_inside,Nb_entries,Prop_Time_lost_in,Mean_time_moving_in,Distance_traveled_in,Distance_traveled_moving_in,Speed_in,Speed_moving_in,Meander_in,Meander_moving_in]+Exploration_in)
                                                        else:
                                                            Shapes_infos[Shape[3]]=[Shape[0],[self.Vid.User_Name, Area, Sequence[0], list_inds[I][1], Mean_dist, Latency, Prop_Time_inside, Absolute_time_inside,Nb_entries,Prop_Time_lost_in,Mean_time_moving_in,Distance_traveled_in,Distance_traveled_moving_in,Speed_in,Speed_moving_in,Meander_in,Meander_moving_in]+Exploration_in]

                                                        '''
                                                        for Event in Events_Ind:
                                                            ArEv = np.array(Event[2])
                                                            ArEv = np.round(ArEv * self.Vid.Frame_rate[1]).astype(int)
                                                            ArEv=ArEv-self.Vid.Cropped[1][0]
                                                            Behav_Shape.append([Shape[3],Event[0],np.nansum(Inside_fixed[ArEv])])
                                                        '''

                                                    elif Shape[0]=="Line":
                                                        Dist_to_line = Functions_Analyses_Speed.details_line(Copy_Coos[deb:end+1, 0], Copy_Coos[deb:end+1, 1],Shape, float(self.Vid.Scale[0]))
                                                        Mean_dist=np.nanmean(Dist_to_line)
                                                        Nb_cross, Nb_cross_TL_BR, Lat_cross, vertical, list_crosses = Functions_Analyses_Speed.calculate_intersect(self.Vid, Copy_Coos[deb:end + 1], Shape[1])
                                                        All_crosses=All_crosses+[[Shape[3],cross] for cross in list_crosses]#For Srikrishna

                                                        if (Shape[3]) in Shapes_infos:
                                                            Shapes_infos[Shape[3]].append([self.Vid.User_Name, Area, Sequence[0], list_inds[I][1], Mean_dist,Nb_cross, Nb_cross_TL_BR,Nb_cross-Nb_cross_TL_BR,Lat_cross,Shape[1]])
                                                        else:
                                                            Shapes_infos[Shape[3]]=[Shape[0],[self.Vid.User_Name, Area, Sequence[0], list_inds[I][1], Mean_dist,Nb_cross, Nb_cross_TL_BR,Nb_cross-Nb_cross_TL_BR,Lat_cross,Shape[1]]]


                                                if len(All_crosses)>0:#For Srikrishna
                                                    All_crosses.sort(key = lambda x: x[1])#For Srikrishna

                                                # For Srikrishna: compute the order of segments crosses.
                                                if self.Vid.More_ana_Crosses:
                                                    if not os.path.isdir(os.path.join(self.list_vid_minus[0].Folder, "Results","Spatial")):
                                                        os.makedirs(os.path.join(self.list_vid_minus[0].Folder, "Results","Spatial"))

                                                    if os.path.isfile(os.path.join(self.Vid.Folder, "Results","Spatial","Summary_crosses.csv")):
                                                        with open(os.path.join(self.Vid.Folder, "Results","Spatial","Summary_crosses.csv"), 'a', newline='',
                                                                  encoding="utf-8") as file:
                                                            writer_cross = csv.writer(file, delimiter=";")
                                                            for cross in (All_crosses):
                                                                writer_cross.writerow([self.Vid.User_Name, Area, Sequence[0], list_inds[I][1],cross[0], cross[1]])
                                                    else:
                                                        with open(os.path.join(self.Vid.Folder, "Results","Spatial","Summary_crosses.csv"), 'w', newline='',encoding="utf-8") as file:
                                                            writer_cross = csv.writer(file, delimiter=";")
                                                            writer_cross.writerow(
                                                                ["Video", "Arena", "Sequence", "Individual", "Segment", "Time"])
                                                            for cross in (All_crosses):
                                                                writer_cross.writerow([self.Vid.User_Name, Area, Sequence[0], list_inds[I][1],cross[0], cross[1]])
                                                new_row=new_row+Functions_Analyses_Speed.calculate_exploration(self.Vid.Analyses[2], self.Vid, This_coos, deb, end, self.Arenas[Area])[0]

                                                #Interindividual distance:
                                                if self.Vid.Track[1][6][Area] > 1:
                                                    Pts_coos = []
                                                    interest=0
                                                    for ind in list_inds[:, 0]:
                                                        if int(ind)==ID:
                                                            cur_pt_id=interest
                                                        Pts_coos.append(self.Coos[int(ind), (deb+first):(end+first+1)])
                                                        interest+=1

                                                    liste_nb_nei_ind, liste_is_close_ind, liste_min_dist_nei_ind, sum_dists_ind = \
                                                        Functions_Analyses_Speed.calculate_nei(Pts_coos=Pts_coos, ind=cur_pt_id,
                                                                                 dist=self.Vid.Analyses[3],
                                                                                 Scale=float(self.Vid.Scale[0]),
                                                                                 Fr_rate=self.Vid.Frame_rate[1], to_save=False)

                                                    new_row.append(liste_nb_nei_ind)
                                                    new_row.append(liste_is_close_ind)
                                                    new_row.append(liste_min_dist_nei_ind)
                                                    new_row.append(sum_dists_ind)

                                                else:
                                                    new_row.append("NA")
                                                    new_row.append("NA")
                                                    new_row.append("NA")
                                                    new_row.append("NA")

                                                if self.Vid.Analyses[2][0]==0 and self.Vid.Explored_complex:
                                                        new_row.append(np.nanmean(All_explored_values_bin[deb:end+1]))
                                                        new_row.append(np.nanmean(All_explored_values_cum[deb:end+1]))
                                                elif self.Vid.Explored_complex:
                                                        new_row.append("NA")
                                                        new_row.append("NA")



                                                #Optional measurements for the main table:
                                                if self.Vid.Stops_Moves_options[0]["Mean_dur_stops"] or self.Vid.Stops_Moves_options[0]["Events_dur_stops"] or self.Vid.Stops_Moves_options[0]["Mean_dur_moves"] or self.Vid.Stops_Moves_options[0]["Events_dur_moves"]:
                                                    stops_e, moves_e, stops_m, moves_m = Functions_Analyses_Speed.separate_0s_1s_durations_nan(State[deb:end + 1], self.Vid.Frame_rate[1],self.Vid.Stops_Moves_options[1])

                                                    if self.Vid.Stops_Moves_options[0]["Mean_dur_moves"]:
                                                        new_row.append(moves_m)

                                                    if self.Vid.Stops_Moves_options[0]["Mean_dur_stops"]:
                                                        new_row.append(stops_m)

                                                    if self.Vid.Stops_Moves_options[0]["Events_dur_stops"]:
                                                        with open(os.path.join(self.Vid.Folder, "Results", "Stops.csv"), 'a', newline='', encoding="utf-8") as file_sm:
                                                            writer_sm = csv.writer(file_sm, delimiter=";")
                                                            for event in stops_e:
                                                                writer_sm.writerow([self.Vid.User_Name, Area, Sequence[0], list_inds[I][1]] + event)

                                                    if self.Vid.Stops_Moves_options[0]["Events_dur_moves"]:
                                                        with open(os.path.join(self.Vid.Folder, "Results", "Moves.csv"), 'a', newline='', encoding="utf-8") as file_sm:
                                                            writer_sm = csv.writer(file_sm, delimiter=";")
                                                            for event in moves_e:
                                                                writer_sm.writerow([self.Vid.User_Name, Area, Sequence[0], list_inds[I][1]] + event)

                                                else:
                                                    if nb_moves_m>0:
                                                        new_row.append("NA")
                                                    if nb_stops_m>0:
                                                        new_row.append("NA")

                                                #Optional measurements:
                                                #self.Vid.Morphometrics=False
                                                if self.Vid.Morphometrics:
                                                    results_morpho=Body_part_functions.Compute_silhouette(self.Vid, ID, self.Coos[int(ID), (deb+first):(end+first+1)])
                                                    with open(os.path.join(self.Vid.Folder, "Results", "Morphometrics.csv"), 'a', newline='', encoding="utf-8") as file_morpho:
                                                        writer_morpho = csv.writer(file_morpho, delimiter=";")
                                                        writer_morpho.writerow([self.Vid.User_Name, Area, Sequence[0], list_inds[I][1]]+results_morpho)



                                                writer.writerow(new_row)#We add a line with the summary of the individual

                                                '''
                                                events_folder = os.path.join(general, "Events")
                                                if not os.path.isdir(events_folder):
                                                    os.makedirs(events_folder)
                                                
                                                vid_folder=os.path.join(events_folder, self.Vid.User_Name)
                                                if not os.path.isdir(vid_folder):
                                                    os.makedirs(vid_folder)
               
                                                with open(os.path.join(vid_folder, str("Arena_" + str(Area) + list_inds[I][1] + ".csv")), 'w', newline='', encoding="utf-8") as file_behav:
                                                    writer_behav = csv.writer(file_behav, delimiter=";")
    
                                                    first_row=["Event","Occurences","Avg_Speed","Avg_Speed_moving","Prop_in_move"]
                                                    for Shape in self.Vid.Analyses[1][Area]:
                                                        if Shape[0]!="Line":
                                                            first_row=first_row+["Occurences_in_" + Shape[3]]
    
                                                    writer_behav.writerow(first_row)
    
                                                   
                                                    for Event in Events_Ind:
                                                        #Non-tracking events
                                                        Row_behav=[]
    
                                                        #Event name
                                                        Row_behav.append(Event[0])
    
                                                        #Total_number of event
                                                        Row_behav.append(len(Event[2]))
    
                                                        #Speed when event
                                                        ArEv=np.array(Event[2])
                                                        ArEv = np.round(ArEv*self.Vid.Frame_rate[1]).astype(int)
                                                        ArEv = ArEv - self.Vid.Cropped[1][0]
                                                        Row_behav.append(np.nanmean(Speeds[ArEv]))
                                                        Row_behav.append(np.nanmean(Speeds[ArEv][np.where(State[ArEv]>0)]))#Idem when moving
                                                        #PRop time moving
                                                        Row_behav.append(np.nanmean(State[ArEv]))
    
                                                        #Number of events in shapes
                                                        for B in Behav_Shape:
                                                            if B[1]==Event[0]:
                                                                Row_behav.append(B[2])
    
                                                        Det_event = np.zeros(len(Speeds))
                                                        Det_event[ArEv]=1
                                                        Details.append(Det_event)
    
                                                        writer_behav.writerow(Row_behav)
                                                    '''

                                        #We create a new file, in which all the trajectories and characteristics will be saved for this individual
                                        vid_folder=os.path.join(details, self.Vid.User_Name)
                                        if not os.path.isdir(vid_folder):
                                            os.makedirs(vid_folder)

                                        with open(os.path.join(vid_folder, str("Arena_" + str(Area) + list_inds[I][1] + ".csv")), 'w', newline='', encoding="utf-8") as file_detind:
                                            writer_det_ind = csv.writer(file_detind, delimiter=";")

                                            first_row=[]
                                            for name in Diverse_functions.list_details_options:
                                                if self.Vid.Details_options[name]:
                                                    if name=="X-Y_Coordinates":
                                                        if self.Vid.Smoothed[0]:
                                                            first_row += ["X_Smoothed", "Y_Smoothed"]
                                                        else:
                                                            first_row += ["X", "Y"]
                                                    elif name=="Distances_to_elem_interest":
                                                        Shapes = ["Dist_to_" + Sh[3] for Sh in self.Vid.Analyses[1][Area]]
                                                        if len(Shapes) > 0:
                                                            first_row += Shapes
                                                    elif name == "Inter-individual_distances":
                                                        Inds=["Dist_to_"+indT for indT in list_inds[:,1] if indT!=list_inds[I][1]]
                                                        if len(Inds) > 0:
                                                            first_row += Inds
                                                    elif name == "Exploration_data_per_frame":
                                                        first_row += ["Exploration_data"]
                                                        if self.Vid.Explored_complex:
                                                            first_row += ["Exploration_data_cumulative"]

                                                    else:
                                                        first_row+=[name]




                                            '''
                                            Events=[Event[0] for Event in Events_Ind]
                                            if len(Events) > 0:
                                                first_row += Events
                                            '''

                                            save_details=True
                                            if save_details and len(Details)>0:
                                                writer_det_ind.writerow(first_row)
                                                for row in range(len(Details[0])):
                                                    new_row=[Details[Col][row] for Col in range(len(Details))]
                                                    if self.Vid.Track[1][6][Area] > 1 and self.Vid.Details_options["Inter-individual_distances"]:
                                                        new_row=new_row+[All_inter_dists[row][I][i] for i in range(len(All_inter_dists[row][I])) if i !=I]
                                                    writer_det_ind.writerow(new_row)

                                    '''
                                    with open(os.path.join(self.list_vid_minus[0].Folder, "Results", "Morphometrics.csv"),'w', newline='', encoding="utf-8") as file_morpho:
                                    with open(os.path.join(self.list_vid_minus[0].Folder, "Results", "Morphometrics.csv"),'w', newline='', encoding="utf-8") as file_morpho:
                                        writer_morpho = csv.writer(file_morpho, delimiter=";")
                                        writer_morpho.writerow(["Video","Arena","Ind","Number_measures","Area","SD_Area","Periphery","SD_Periphery","Length","SD_Length","Width","SD_Width"])
    
    
                                        for I in range(self.Vid.Track[1][6][Area]):  # Individual's caracteristics
                                            if len(self.Vid.Morphometrics[Area][I])>0:
                                                # Frame of measurement, Area, periphery, length, width
                                                nb_measures=len(self.Vid.Morphometrics[Area][I])
                                                surface=np.mean([measure[1] for measure in self.Vid.Morphometrics[Area][I]])*(1 / float(self.Vid.Scale[0]) ** 2)
                                                surface_sd = np.std([measure[1] for measure in self.Vid.Morphometrics[Area][I]])*(1 / float(self.Vid.Scale[0]) ** 2)
                                                periph = np.mean([measure[2] for measure in self.Vid.Morphometrics[Area][I]])/float(self.Vid.Scale[0])
                                                periph_sd = np.std([measure[2] for measure in self.Vid.Morphometrics[Area][I]]) / float(self.Vid.Scale[0])
                                                length = np.mean([measure[3] for measure in self.Vid.Morphometrics[Area][I]])/float(self.Vid.Scale[0])
                                                length_sd = np.std([measure[3] for measure in self.Vid.Morphometrics[Area][I]]) / float(self.Vid.Scale[0])
                                                width = np.mean([measure[4] for measure in self.Vid.Morphometrics[Area][I]])/float(self.Vid.Scale[0])
                                                width_sd = np.std([measure[4] for measure in self.Vid.Morphometrics[Area][I]]) / float(self.Vid.Scale[0])
                                                new_row_morpho = [self.Vid.User_Name, Area, list_inds[I][1], nb_measures, surface, surface_sd, periph,periph_sd, length, length_sd,width, width_sd]
                                            else:
                                                new_row_morpho = [self.Vid.User_Name, Area, list_inds[I][1], 0, "NA", "NA", "NA", "NA", "NA", "NA","NA", "NA"]
    
                                            writer_morpho.writerow(new_row_morpho)
                                    '''

                                    Ar_coos=[]
                                    for TI in list_inds[:,0]:
                                        to_do=int(TI)
                                        Ar_coos.append(self.Coos[to_do])

                                    #We add a file in which we will save the shapes characteristics
                                    cur_s=0
                                    for Shape in self.Vid.Analyses[1][Area]:
                                        self.timer = ((cur_s / len(self.Vid.Analyses[1][Area])) * (0.1) + (0.8))
                                        self.show_load()
                                        cur_s+=1

                                        Centroid_X,Centroid_Y, Xmin, Xmax, Ymin, Ymax, Surface, Perimeter, Points = Functions_Analyses_Speed.Shape_characteristics(Shape, self.Vid, Area)
                                        if Shape[0]!="Line":
                                            Min,Max,Moy=Functions_Analyses_Speed.calculate_group_inside(Ar_coos, Shape, self.Arenas[Area], self.Vid)
                                        else:
                                            Min="NA"
                                            Max = "NA"
                                            Moy = "NA"

                                        Time_inside.append([self.Vid.User_Name, Area,Shape[3], Min,Max,Moy,Centroid_X,Centroid_Y,Xmin,Xmax,Ymin,Ymax,Surface,Perimeter,Points])


                                    self.timer = 0.9
                                    self.show_load()

                            cur_vid+=1

                    self.loading_state.config(text=self.Messages["Loading_Frame_info1"])
                    self.timer = 0
                    self.show_load()

                    #Analyses related to areas:
                    pos=0
                    if not os.path.isdir(os.path.join(self.list_vid_minus[0].Folder,"Results","Spatial")):
                        os.makedirs(os.path.join(self.list_vid_minus[0].Folder,"Results","Spatial"))

                    count=0
                    self.timer = 0.1
                    self.show_load()

                    cur_s=0
                    for Shape_name in Shapes_infos:
                        self.timer = ((cur_s / len(Shapes_infos)) * (5 / 10) + (0.1))
                        self.show_load()
                        cur_s+=1

                        count+=1
                        self.show_load()
                        pos += 1


                        with open(os.path.join(self.list_vid_minus[0].Folder, "Results","Spatial","Element" + "_" + Shape_name +".csv"), 'w', newline='', encoding="utf-8") as file:
                            writer = csv.writer(file, delimiter=";")

                            if Shapes_infos[Shape_name][0] != "Line":
                                writer.writerow(["Video", "Arena", "Sequence", "Individual", "Mean_Distance", "Latency", "Prop_time_inside", "Time_inside", "Nb_entries","Prop_time_lost","Prop_time_moving","Traveled_Dist","Traveled_Dist_Moving","Average_Speed","Average_Speed_moving","Meander","Meander_moving","Exploration_absolute_value","Exploration_relative_value","Exploration_method","Exploration_area","Exploration_aspect_param"])
                                for Ind_infos in Shapes_infos[Shape_name][1:]:
                                    writer.writerow(Ind_infos)

                            elif Shapes_infos[Shape_name][0] == "Line":
                                Points=Shapes_infos[Shape_name][1][(len(Shapes_infos[Shape_name][1])-1)]
                                if abs(Points[1][0] - Points[0][0]) > abs(Points[1][1] - Points[0][1]):
                                    vertical = True
                                else:
                                    vertical = False

                                if vertical:
                                    TLBR= "Nb_crosses_Top_Bot"
                                    BRTL = "Nb_crosses_Bot_Top"
                                else:
                                    TLBR = "Nb_crosses_Left_Right"
                                    BRTL = "Nb_crosses_Right_Left"
                                writer.writerow(["Video", "Arena", "Sequence", "Individual", "Mean_Distance", "Nb_crosses",TLBR,BRTL, "Lat_cross"])

                                #Arenas=[[0,0] for _ in self.Arenas]
                                for Ind_infos in Shapes_infos[Shape_name][1:]:
                                    #Arenas[Ind_infos[1]][0]+= Ind_infos[5]
                                    #Arenas[Ind_infos[1]][1] += Ind_infos[6]
                                    writer.writerow(Ind_infos[0:(len(Ind_infos)-1)])#We don't want to save the position of the points of the segment
                                #for Ar in range(len(self.Arenas)):
                                    #Time_inside.append([Ind_infos[0],Ar,Shape_name,"NA","NA","NA",Arenas[Ar][0],Arenas[Ar][1]])

                    with open(os.path.join(self.list_vid_minus[0].Folder,"Results","Spatial","General.csv"),'w', newline='', encoding="utf-8") as file:
                        writer = csv.writer(file, delimiter=";")
                        writer.writerow(["Video", "Arena", "Shape", "Min_number_of_targets", "Max_number_of_targets", "Mean_number_of_targets","Element_Center_X","Element_Center_Y","Element_Xmin","Element_Xmax","Element_Ymin","Element_Ymax","Element_Surface","Element_Perimeter","Element_Points"])
                        for Sh in Time_inside:
                            writer.writerow(Sh)

                    self.timer = 0.7
                    self.show_load()

                    with open(os.path.join(self.list_vid_minus[0].Folder, "Results", "Spatial", "Arenas_coordinates.csv"), 'w', newline='', encoding="utf-8") as file:
                        writer = csv.writer(file, delimiter=";")
                        writer.writerow(["Video", "Arena", "Center_X", "Center_Y", "Xmin","Xmax", "Ymin", "Ymax", "Surface", "Perimeter"])
                        for row_ArCh in row_Arenas_coos:
                            writer.writerow(row_ArCh)

                    self.timer = 0.85
                    self.show_load()

                    #Inter-ind_dists:
                    if self.Vid.Group_data["Exploration"] or self.Vid.Group_data["Interind_data"]:
                        first_row =["Video", "Sequence","Arena"]
                        with open(os.path.join(self.list_vid_minus[0].Folder, "Results","Results_InterInd.csv"), 'w', newline='', encoding="utf-8") as file:
                            writer = csv.writer(file, delimiter=";")
                            if self.Vid.Group_data["Interind_data"]:
                                first_row=first_row+["Mean_dist", "Min_dist", "Max_dist"]
                            if self.Vid.Group_data["Exploration"]:
                                first_row = first_row + ["Absolute_exploration","Relative_exploration"]


                            writer.writerow(first_row)
                            for row in rows_inter_dists:
                                writer.writerow(row)

                    self.timer = 1
                    self.show_load()
                    #except Exception as e:
                        #messagebox.showinfo(message=self.Messages["Do_anaWarn1"].format(e),title=self.Messages["Do_anaWarnT1"])
                except Exception as e:
                    CustomDialog(self.master,
                                 text="The video couldn't be loaded:" + str(type(e).__name__) + " – " + str(e) + " - " + traceback.format_exc(),
                                 title="Debugging")


        #Update the main window
        self.boss.update_projects()
        self.boss.update_selections()
        self.boss.focus_set()
        self.boss.bind_all("<MouseWheel>", self.boss.on_mousewheel)
        self.bouton.config(state="normal", background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.bouton_sel_all.config(state="normal")
        self.grab_release()

        if self.cache:#minimize
            self.boss.parent.update_idletasks()
            self.boss.parent.state('normal')
            self.boss.parent.overrideredirect(True)

        self.boss.save()
        self.parent.destroy()

    def show_load(self):
        #Show the progress of the process
        self.loading_bar.delete('all')
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill=Color_settings.My_colors.list_colors["Loading_before"])
        self.loading_bar.create_rectangle(0, 0, self.timer*400, self.loading_bar.cget("height"), fill=Color_settings.My_colors.list_colors["Loading_after"])
        self.loading_bar.update()

    def close(self):
        if self.running == None:
            self.parent.destroy()
        if self.running=="Normal":
            self.urgent_close = True
            Do_the_track.urgent_close(self.list_vid_minus[self.curr_vid])

        elif self.running=="Variable":
            self.urgent_close = True
            Do_the_track.urgent_close(self.list_vid_minus[self.curr_vid])

        self.boss.bind_all("<MouseWheel>", self.boss.on_mousewheel)

    def create_empty(self, Vid):
        #Create an empty data frame to store manual tracking data
        if Vid.Track[0]:
            nb_ind=int(sum(Vid.Track[1][6]))
        else:
            nb_ind=len(Vid.Track[1][6])
            Vid.Track[1][6]=[1 for i in Vid.Track[1][6]]

        Vid.Track[1][8]=True

        nb_ind=max(1,nb_ind)


        one_every = Vid.Frame_rate[0] / Vid.Frame_rate[1]
        all_frames=Vid.Cropped[1][1]-Vid.Cropped[1][0]
        nb_frames=int(all_frames/one_every)
        General_Coos = np.zeros([nb_frames+2, nb_ind*2 +2], dtype="object")
        General_Coos.fill("NA")

        liste_times = list(np.arange(Vid.Cropped[1][0], (nb_frames + 1) * one_every + Vid.Cropped[1][0] + one_every, one_every))
        General_Coos[1:, 0] = liste_times[0:len(General_Coos[1:, 0])]

        tmp = np.array(General_Coos[1:, 0] / one_every / Vid.Frame_rate[1], dtype="float")
        General_Coos[1:, 1] = np.around(tmp, 2)

        if Vid.Track[0]:
            General_Coos[0, :] = ["Frame","Time"]+[Col+"_Arena"+str(Ar)+"_"+str(ind) for Ar in range(len(Vid.Track[1][6])) for ind in range(max(1,Vid.Track[1][6][Ar])) for Col in ["X","Y"]]
        else:
            General_Coos[0, :] = ["Frame", "Time"] + [Col + "_Arena" + str(Ar) + "_0" for Ar in range(nb_ind) for Col in ["X", "Y"]]

        # Where coordinates will be saved, if the folder did not exists, it is created.
        if Vid.User_Name == Vid.Name:
            file_name = Vid.Name
            point_pos = file_name.rfind(".")
            if file_name[point_pos:].lower() != ".avi":
                file_name = Vid.User_Name
            else:
                file_name = file_name[:point_pos]
        else:
            file_name = Vid.User_Name

        if not os.path.isdir(os.path.join(self.boss.folder, "coordinates")):
            os.makedirs(os.path.join(self.boss.folder, "coordinates"))

        To_save = os.path.join(self.boss.folder, "Coordinates", file_name + "_Coordinates.csv")
        np.savetxt(To_save, General_Coos, delimiter=';', encoding="utf-8", fmt='%s')

    def find_sequences(self, Area, ID):
        Sequences_to_do = []
        for seq in self.Vid.Sequences[ID]:
            if seq[1][0] == "Auto":
                if seq[1][2] == "Element of interest" or seq[1][
                    2] == "End":  # Before auto-range sequences were only for elem of interest and old sequences were coded with"end" instead of the type of sequence
                    found_shape=False
                    for Shape in self.Vid.Analyses[1][Area]:
                        if Shape[3] == seq[1][3]:
                            entries, exits = Interface_sequences.find_shape_relation(Shape,
                                                                                     self.Vid,
                                                                                     self.Coos[ID],
                                                                                     ID)
                            found_shape=True
                            break
                    if found_shape:
                        Sequences_to_do= Sequences_to_do + Interface_sequences.do_auto_elem(seq, entries, exits, Shape, self.Vid.Frame_rate[1])

                else:
                    from_ = float(seq[1][1])
                    to_ = float(seq[2][1])
                    each_ = float(seq[1][5])

                    for sub_seq in np.arange(from_, to_, each_):
                        Seq_name = seq[1][2] + "_from_" + str(
                            sub_seq) + "_to_" + str(sub_seq + each_)
                        new_seq = [Seq_name, [seq[1][2], str(sub_seq), "End", "End",
                                              str(sub_seq), "1"],
                                   [seq[1][2], str(sub_seq + each_), "End", "End",
                                    str(sub_seq + each_), "-1"]]
                        Sequences_to_do.append(new_seq)

            else:
                Sequences_to_do.append(seq)
        return(Sequences_to_do)


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

#Code origin: https://stackoverflow.com/questions/35923235/is-there-a-message-box-which-displays-copy-able-text-in-python-2-7
class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, text=None):
        self.data = text
        simpledialog.Dialog.__init__(self, parent, title=title)

    def body(self, parent):
        self.text = Text(self, width=40, height=4)
        self.text.pack(fill="both", expand=True)

        self.text.insert("1.0", self.data)

        return self.text