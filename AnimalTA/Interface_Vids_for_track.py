from tkinter import *
from tkinter import messagebox
from AnimalTA import UserMessages,Do_the_track3, Analyses_Speed, Function_draw_mask
import os
import csv
import numpy as np
from scipy.signal import savgol_filter
import cv2
import math
from operator import itemgetter
import time
import shutil
import random

class Extend(Frame):
    """This frame is a list of all the videos. The user can select the ones to be tracked or analysed"""
    def __init__(self, parent, boss, type):
        Frame.__init__(self, parent, bd=5)
        self.parent=parent
        self.boss=boss
        self.grid()
        self.list_vid=self.boss.liste_of_videos
        self.grab_set()
        self.all_sel=False
        self.timer=0
        self.type=type

        #Import messages
        self.Language = StringVar()
        f = open("Files/Language", "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        self.cache =False #The program is not minimised

        #The message displayed varies according to whether the user wants to track or analyse videos
        self.sel_state = StringVar()
        if type=="Analyses":
            self.winfo_toplevel().title(self.Messages["Do_anaT"])
            self.Explanation_lab = Label(self, text=self.Messages["Do_ana0"], wraplength=700)
        else:
            self.winfo_toplevel().title(self.Messages["Do_trackT"])
            self.Explanation_lab = Label(self, text=self.Messages["Do_track0"], wraplength=700)

        self.sel_state.set(self.Messages["ExtendB1"])
        self.Explanation_lab.grid(row=0,columnspan=2)

        #Button to select all
        self.bouton_sel_all=Button(self,textvariable=self.sel_state,command=self.select_all)
        self.bouton_sel_all.grid(row=1,columnspan=2)

        #List of videos
        self.yscrollbar = Scrollbar(self)
        self.yscrollbar.grid(row=2,column=1, sticky="ns")

        self.Liste=Listbox(self, selectmode = EXTENDED, yscrollcommand=self.yscrollbar.set)
        self.Liste.config(height=15, width=150)
        self.yscrollbar.config(command=self.Liste.yview)

        self.bouton=Button(self,text=self.Messages["Validate"],command=self.validate)
        self.bouton.grid(row=3)

        self.list_vid_minus=[]
        for i in range(len(self.list_vid)):#Only video that are ready for tracking can be choose if the user wants to do tracking. If user wants to analyse, only videos which are already tracked.
            if (type=="Tracking" and self.list_vid[i].Track[0]) or (type=="Analyses" and self.list_vid[i].Tracked):
                self.list_vid_minus.append(self.list_vid[i])
                self.Liste.insert(i, self.list_vid[i].File_name)
                if self.list_vid[i].Tracked:
                    self.Liste.itemconfig(len(self.list_vid_minus)-1, {'fg': 'red'})

        self.Liste.grid(row=2,column=0)

        self.loading_canvas=Frame(self)
        self.loading_canvas.grid(row=4,columnspan=2)
        self.loading_state=Label(self.loading_canvas, text="")
        self.loading_state.grid(row=0, column=0)

        self.loading_bar=Canvas(self.loading_canvas, height=10)
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill="red")
        self.loading_bar.grid(row=0, column=1)

        #Minimize the window which processing
        self.bouton_hide = Button(self, text=self.Messages["Do_track1"], command=self.hide)
        self.focus()

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

    def validate(self):
        #Run the tracking/analyses
        self.boss.save()
        list_item = self.Liste.curselection()
        pos=0
        self.bouton.config(state="disable")
        self.bouton_sel_all.config(state="disable")
        self.Liste.config(state="disable")
        self.bouton_hide.grid(row=5)

        if self.type=="Tracking":
            for V in list_item:
                cleared=self.list_vid_minus[V].clear_files()
                if cleared:
                    pos+=1
                    self.list_vid_minus[V].Identities = []
                    for Ar_inds in range(len(self.list_vid_minus[V].Track[1][6])):
                        for num in range(self.list_vid_minus[V].Track[1][6][Ar_inds]):
                            self.list_vid_minus[V].Identities.append([Ar_inds, "Ind" + str(num), self.random_color()[0]])  # 0: identity of target, from 0 to N, 1: in which arene, 2:Name of the target, 3:Color of the target
                    self.boss.save()

                    self.loading_state.config(text= self.Messages["Video"] + " {act}/{tot}".format(act=pos,tot=len(list_item)))
                    try:
                        succeed=Do_the_track3.Do_tracking(self, Vid=self.list_vid_minus[V], folder=self.boss.folder)
                        if succeed:
                            self.list_vid_minus[V].Tracked = True
                    except Exception as e:
                        messagebox.showinfo(message=self.Messages["Do_trackWarn1"].format(self.list_vid_minus[V].Name,e), title=self.Messages["Do_trackWarnT1"])

        if self.type=="Analyses":
            Shapes_infos=dict()
            Time_inside = []

            general = self.list_vid_minus[0].Folder + str("/Results")
            Cleared=True
            if os.path.isdir(general):
                Cleared=False
                while not Cleared:
                    try:
                        os.rename(general, general)
                        shutil.rmtree(general)
                        Cleared=True

                    except PermissionError as e:
                        Response = messagebox.askretrycancel(title=self.Messages["TError"],message=self.Messages["Error_Permission"].format(e.filename))
                        if not Response:
                            break


            if Cleared:
                os.makedirs(general)
                details=general+"/Detailed_data"
                os.makedirs(details)
                #We first do the analyses by inds:
                rows_inter_dists=[]
                with open(self.list_vid_minus[0].Folder+str("/Results/Results_by_ind.csv"), 'w', newline='', encoding="utf-8") as file:
                    writer = csv.writer(file, delimiter=";")
                    writer.writerow(["Video", "Arena", "Individual", "Prop_time_lost", "Smoothing_filter_window","Smoothing_Polyorder",
                                     "Moving_threshold", "Prop_time_moving", "Average_Speed", "Average_Speed_Moving", "Traveled_Dist",
                                     "Traveled_Dist_Moving","Exploration_value","Exploration_method","Exploration_area","Exploration_aspect_param",
                                     "Mean_nb_neighbours", "Prop_time_with_at_least_one_neighbour", "Mean_shortest_dist_neighbour", "Mean_sum_distances_to_neighbours"])
                    pos=0
                    for V in list_item:
                        self.loading_state.config(text="Results by Inds, Video: " + " {act}/{tot}".format(act=pos, tot=len(list_item)))
                        pos += 1
                        self.Vid=self.list_vid_minus[V]
                        #We create the calculation class:
                        Calc_speed = Analyses_Speed.speed_calculations()
                        Calc_speed.seuil_movement=self.Vid.Analyses[0]
                        self.Load_Coos(self.Vid)
                        mask = Function_draw_mask.draw_mask(self.Vid)
                        Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                        self.Arenas = Function_draw_mask.Organise_Ars(Arenas)

                        Ind=0
                        Ind_done = 0
                        Passed_fish = 0
                        for Area in range(len(self.Vid.Analyses[1])):#For each arena
                            self.timer=Area/len(self.Vid.Analyses[1])
                            list_inds = [Ind[1] for Ind in self.Vid.Identities if Ind[0] == Area]
                            self.show_load()

                            liste_nb_nei=["NA"]*self.Vid.Track[1][6][Area]
                            liste_is_close = ["NA"] * self.Vid.Track[1][6][Area]
                            liste_min_dist_nei = ["NA"] * self.Vid.Track[1][6][Area]
                            sum_dists = ["NA"] * self.Vid.Track[1][6][Area]

                            if self.Vid.Track[1][6][Area] > 1:#Frist step is inter-individual distance (saved in "rows_inter_dists")
                                Pts_coos = []
                                for ind in range(self.Vid.Track[1][6][Area]):
                                    Pts_coos.append(self.Coos["Ind" + str(ind + Passed_fish)])

                                Mean, Min, Max = Calc_speed.calculate_all_inter_dists(Pts_coos=Pts_coos,Scale=float(self.Vid.Scale[0]))
                                rows_inter_dists.append([self.Vid.Name, Area, Mean, Min, Max])
                                Passed_fish = Passed_fish + self.Vid.Track[1][6][Area]
                                if len(self.Vid.Analyses)<4:
                                    self.Vid.Analyses.append(0)

                                # Inter-ind_dists:
                                liste_nb_nei, liste_is_close, liste_min_dist_nei, sum_dists, table_all_dists, table_is_close, table_nb_contacts, all_events_contacts, All_inter_dists = \
                                    Calc_speed.calculate_nei(Pts_coos=Pts_coos, ind=0, dist=self.Vid.Analyses[3], Scale=float(self.Vid.Scale[0]), Fr_rate=self.Vid.Frame_rate[1], to_save=True)

                                main_folder=self.Vid.Folder + str("/Results/InterInd")
                                if not os.path.isdir(main_folder):
                                    os.makedirs(main_folder)

                                vid_folder=main_folder + "/"+ self.Vid.Name
                                if not os.path.isdir(vid_folder):
                                    os.makedirs(vid_folder)

                                Name= "Video_" + str(self.Vid.Name) + "__" + "Arena_" + str(Area) + "__Distances"
                                with open(vid_folder + "/" +Name+".csv", 'w',newline='', encoding="utf-8") as file:
                                    writerb = csv.writer(file, delimiter=";")
                                    writerb.writerow(["X"]+list_inds)
                                    for row in range(len(table_all_dists)):
                                        First_cell=[list_inds[row]]
                                        Row=list(table_all_dists[row])
                                        writerb.writerow(First_cell+Row)

                                Name= "Video_" + str(self.Vid.Name) + "__" + "Arena_" + str(Area) + "__PropTime"
                                with open(vid_folder + "/" +Name+".csv", 'w',newline='', encoding="utf-8") as file:
                                    writerb = csv.writer(file, delimiter=";")
                                    writerb.writerow(["X"]+list_inds)
                                    for row in range(len(table_is_close)):
                                        First_cell=[list_inds[row]]
                                        Row=list(table_is_close[row])
                                        writerb.writerow(First_cell+Row)

                                Name= "Video_" + str(self.Vid.Name) + "__" + "Arena_" + str(Area) + "__Contact_occurences"
                                with open(vid_folder + "/" +Name+".csv", 'w',newline='', encoding="utf-8") as file:
                                    writerb = csv.writer(file, delimiter=";")
                                    writerb.writerow(["X"]+list_inds)
                                    for row in range(len(table_nb_contacts)):
                                        First_cell=[list_inds[row]]
                                        Row=list(table_nb_contacts[row])
                                        writerb.writerow(First_cell+Row)

                                Name= "Video_" + str(self.Vid.Name) + "__" + "Arena_" + str(Area) + "__Contact_events"
                                with open(vid_folder + "/" +Name+".csv", 'w',newline='', encoding="utf-8") as file:
                                    writerb = csv.writer(file, delimiter=";")
                                    writerb.writerow(["Ind_P1","Ind_P2","Duration","Beginning"])
                                    for row in range(len(all_events_contacts)):
                                        all_events_contacts[row][0],all_events_contacts[row][1]=list_inds[all_events_contacts[row][0]],list_inds[all_events_contacts[row][1]]
                                        writerb.writerow(all_events_contacts[row])

                            else:
                                Passed_fish += 1

                            for I in range(self.Vid.Track[1][6][Area]):#Individual's caracteristics
                                ID="Ind" + str(Ind)
                                new_row=[self.Vid.Name, Area, list_inds[I]]
                                Details=[]
                                Details.append(list(map(lambda x:round(x/self.Vid.Frame_rate[1],2), range(len(self.Coos[ID])))))
                                Details.append(list(np.array(self.Coos[ID])[:,0]))#We will save here the detailed informations (for each frame)
                                Details.append(list(np.array(self.Coos[ID])[:,1]))
                                Details[1]=list(map(lambda x: float(x)/ float(self.Vid.Scale[0]),Details[1]))
                                Details[2] = list(map(lambda x: float(x) / float(self.Vid.Scale[0]), Details[2]))

                                #Time lost
                                new_row.append(Calc_speed.calculate_lost(parent=self, ind=ID))

                                #Smoothing_parameters:
                                if self.Vid.Smoothed[0]!="NA":
                                    new_row.append(self.Vid.Smoothed[0])
                                    new_row.append(self.Vid.Smoothed[1])
                                else:
                                    new_row.append("NA")
                                    new_row.append("NA")

                                # Moving threshold:
                                new_row.append(Calc_speed.seuil_movement)

                                #Time moving:
                                val, all_dat=Calc_speed.calculate_prop_move(parent=self, ind=ID, return_vals=True)
                                new_row.append(val)
                                Speeds=Calc_speed.get_all_speeds_ind(parent=self, ind=ID, in_move=False, with_NA=True)#We save the speed of ID for each frame
                                Details.append(Speeds)
                                Details.append(all_dat)  # We save the moving state of ID for each frame

                                #Average speed:
                                new_row.append(Calc_speed.calculate_mean_speed(parent=self, ind=ID, in_move=False))

                                #Average speed while moving:
                                new_row.append(Calc_speed.calculate_mean_speed(parent=self, ind=ID, in_move=True))

                                #Traveled distance:
                                Val,all_dat=(Calc_speed.calculate_dist(parent=self, ind=ID, in_move=False,return_vals=True))
                                new_row.append(Val)
                                Details.append(all_dat)  # We save the distance traveled of ID for each frame

                                #Traveled distance while moving:
                                new_row.append(Calc_speed.calculate_dist(parent=self, ind=ID, in_move=True))

                                #Spatial:
                                SHID=0
                                for Shape in self.Vid.Analyses[1][Area]:
                                    if Shape[0]=="Point":
                                        Mean_dist, Latency, Prop_Time, all_dat = Calc_speed.calculate_dist_lat(self, Shape[1][0],ind=ID, Dist=Shape[2], return_vals=True)
                                        if Shape[3] in Shapes_infos:
                                            Shapes_infos[Shape[3]].append([self.Vid.Name, Area, list_inds[I], Mean_dist,Latency,Prop_Time])
                                        else:
                                            Shapes_infos[Shape[3]]=[Shape[0],[self.Vid.Name, Area, list_inds[I], Mean_dist, Latency, Prop_Time]]
                                        Details.append(all_dat)


                                    elif Shape[0]=="Line":
                                        Mean_dist, all_dat = Calc_speed.calculate_dist_line(self, Shape[1],ind=ID, return_vals=True)
                                        Nb_cross, Lat_cross = Calc_speed.calculate_intersect(self, Shape[1], ind=ID)
                                        if (Shape[3]) in Shapes_infos:
                                            Shapes_infos[Shape[3]].append([self.Vid.Name, Area, list_inds[I], Mean_dist,Nb_cross,Lat_cross])
                                        else:
                                            Shapes_infos[Shape[3]]=[Shape[0],[self.Vid.Name, Area, list_inds[I], Mean_dist,Nb_cross,Lat_cross]]
                                        Details.append(all_dat)

                                    elif Shape[0]=="All_borders":
                                        Mean_dist, Prop_inside, all_dat = Calc_speed.calculate_dist_border(self, Area=self.Arenas[Area], ind=ID, shape=Shape, return_vals=True)
                                        if (Shape[3]) in Shapes_infos:
                                            Shapes_infos[Shape[3]].append([self.Vid.Name, Area, list_inds[I], Mean_dist, Prop_inside])
                                        else:
                                            Shapes_infos[Shape[3]]=[Shape[0],[self.Vid.Name, Area, list_inds[I], Mean_dist, Prop_inside]]
                                        Details.append(all_dat)

                                    elif Shape[0]=="Borders":
                                        Mean_dist, Prop_inside, Lat_inside, all_dat = Calc_speed.calculate_dist_sep_border(self, ind=ID, shape=Shape, return_vals=True)
                                        if (Shape[3]) in Shapes_infos:
                                            Shapes_infos[Shape[3]].append([self.Vid.Name, Area, list_inds[I], Mean_dist, Prop_inside, Lat_inside])
                                        else:
                                            Shapes_infos[Shape[3]]=[Shape[0],[self.Vid.Name, Area, list_inds[I], Mean_dist, Prop_inside, Lat_inside]]
                                        Details.append(all_dat)

                                    elif Shape[0]=="Ellipse" or Shape[0] == "Rectangle" or Shape[0] == "Polygon":
                                        if len(Shape[1]) > 0:
                                            empty = np.zeros([self.Vid.Back[1].shape[0], self.Vid.Back[1].shape[1], 1], np.uint8)
                                            if Shape[0] == "Ellipse":
                                                Function_draw_mask.Draw_elli(empty, [po[0] for po in Shape[1]],[po[1] for po in Shape[1]], 255, thick=-1)
                                            elif Shape[0] == "Rectangle":
                                                Function_draw_mask.Draw_rect(empty, [po[0] for po in Shape[1]],[po[1] for po in Shape[1]], 255, thick=-1)
                                            elif Shape[0] == "Polygon":
                                                Function_draw_mask.Draw_Poly(empty, [po[0] for po in Shape[1]],[po[1] for po in Shape[1]], 255, thick=-1)

                                            cnt, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                                        else:
                                            cnt = []

                                        Prop_inside, Lat_inside, all_dat = Calc_speed.calculate_time_inside(parent=self, cnt=cnt,ind=ID, return_vals=True)
                                        if (Shape[3]) in Shapes_infos:
                                            Shapes_infos[Shape[3]].append([self.Vid.Name, Area, list_inds[I], Prop_inside, Lat_inside])
                                        else:
                                            Shapes_infos[Shape[3]] = [Shape[0],[self.Vid.Name, Area, list_inds[I], Prop_inside, Lat_inside]]
                                        Details.append(all_dat)
                                    SHID+=1

                                #Exploration:
                                if self.Vid.Analyses[2][0]==0:#Si c'est method moderne
                                    radius = math.sqrt((float(self.Vid.Analyses[2][1])) / math.pi)

                                    empty = np.zeros((self.Vid.shape[0], self.Vid.shape[1], 1), np.uint8)

                                    for pt in self.Coos[ID]:
                                        if pt[0] != "NA":
                                            cv2.circle(empty, (int(float(pt[0])), int(float(pt[1]))),
                                                       int(radius * float(self.Vid.Scale[0])), (1), -1)

                                    mask = np.zeros([self.Vid.shape[0], self.Vid.shape[1], 1], np.uint8)
                                    mask = cv2.drawContours(mask, [self.Arenas[Area]], -1, (255), -1)
                                    empty = cv2.bitwise_and(mask, empty)


                                    new_row.append(len(np.where(empty > [0])[0]) / len(np.where(mask == [255])[0]))#Value
                                    new_row.append("Modern")#Method
                                    new_row.append(self.Vid.Analyses[2][1])#Area
                                    new_row.append("NA")#Param_aspect

                                elif self.Vid.Analyses[2][0]==1:#Si c'est mesh carré
                                    No_NA_Coos = np.array(self.Coos[ID])
                                    No_NA_Coos = No_NA_Coos[np.all(No_NA_Coos != "NA", axis=1)]
                                    No_NA_Coos = No_NA_Coos.astype('float')
                                    No_NA_Coos = No_NA_Coos.astype('int32')

                                    largeur = math.sqrt(float(self.Vid.Analyses[2][1]) * float(self.Vid.Scale[0]) ** 2)
                                    nb_squares_v = math.ceil((max(self.Arenas[Area][:, :, 0]) - min(self.Arenas[Area][:, :, 0])) / largeur)
                                    nb_squares_h = math.ceil((max(self.Arenas[Area][:, :, 1]) - min(self.Arenas[Area][:, :, 1])) / largeur)

                                    max_x = min(self.Arenas[Area][:, :, 0]) + nb_squares_v * (largeur)
                                    max_y = min(self.Arenas[Area][:, :, 1]) + nb_squares_h * (largeur)

                                    decal_x = (max_x - max(self.Arenas[Area][:, :, 0])) / 2
                                    decal_y = (max_y - max(self.Arenas[Area][:, :, 1])) / 2

                                    Xs = (np.floor((No_NA_Coos[:, 0] - (min(self.Arenas[Area][:, :, 0]) - decal_x)) / largeur))
                                    Ys = (np.floor((No_NA_Coos[:, 1] - (min(self.Arenas[Area][:, :, 1]) - decal_y)) / largeur))

                                    XYs = np.array(list(zip(Xs, Ys)))
                                    unique = np.unique(XYs, axis=0, return_counts=False)

                                    new_row.append(len(unique))#Value
                                    new_row.append("Squares_mesh")#Method
                                    new_row.append(self.Vid.Analyses[2][1])#Area
                                    new_row.append("NA")#Param_aspect

                                elif self.Vid.Analyses[2][0]==2:#Si c'est mesh circulaire
                                    No_NA_Coos = np.array(self.Coos[ID])
                                    No_NA_Coos = No_NA_Coos[np.all(No_NA_Coos != "NA", axis=1)]
                                    No_NA_Coos = No_NA_Coos.astype('float')
                                    No_NA_Coos = No_NA_Coos.astype('int32')


                                    M = cv2.moments(self.Arenas[Area])
                                    cX = int(M["m10"] / M["m00"])
                                    cY = int(M["m01"] / M["m00"])

                                    max_size = max(list(
                                        np.sqrt((self.Arenas[Area][:, :, 0] - cX) ** 2 + (self.Arenas[Area][:, :, 1] - cY) ** 2)))

                                    last_rad = math.sqrt((float(self.Vid.Analyses[2][1]) * float(self.Vid.Scale[0]) ** 2) / math.pi)
                                    last_nb = 1

                                    list_rads = [last_rad]
                                    list_nb = [1]
                                    list_angles = [[0]]

                                    while last_rad < max_size:
                                        new_rad = ((math.sqrt(last_nb) + math.sqrt(self.Vid.Analyses[2][2] ** 2)) / math.sqrt(
                                            last_nb)) * last_rad
                                        new_nb = int(round((math.sqrt(last_nb) + math.sqrt(self.Vid.Analyses[2][2] ** 2)) ** 2))
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

                                    # We summarise the position of the individual:
                                    Dists = list(np.sqrt((No_NA_Coos[:, 0] - cX) ** 2 + (No_NA_Coos[:, 1] - cY) ** 2))
                                    Circles = ([np.argmax(list_rads > dist) for dist in Dists])  # In which circle
                                    Angles = np.arctan2((No_NA_Coos[:, 1] - cY), (No_NA_Coos[:, 0] - cX))
                                    liste_angles_per_I = list(itemgetter(*Circles)(list_angles))
                                    Portions = ([np.argmax(liste_angles_per_I[idx] >= (angle + math.pi)) for idx, angle in
                                                 enumerate(Angles)])  # In which portion

                                    Pos = np.array(list(zip(Circles, Portions)))
                                    unique = np.unique(Pos, axis=0,return_counts=False)  # On regarde ou la bete est et combien de fois

                                    new_row.append(len(unique))#Value
                                    new_row.append("Circular_mesh")#Method
                                    new_row.append(self.Vid.Analyses[2][1])#Area
                                    new_row.append(self.Vid.Analyses[2][2])#Param_aspect

                                #Interindividual distance:
                                new_row.append(liste_nb_nei[I])
                                new_row.append(liste_is_close[I])
                                new_row.append(liste_min_dist_nei[I])
                                new_row.append(sum_dists[I])

                                writer.writerow(new_row)#We add a line with the summary of the individual

                                #We create a new file, in which all the trajectories and characteristics will be saved for this individual
                                vid_folder=details + "/"+ self.Vid.Name
                                if not os.path.isdir(vid_folder):
                                    os.makedirs(vid_folder)

                                with open(vid_folder + "/" +str("Arena_" + str(Area) + list_inds[I] + ".csv"), 'w', newline='', encoding="utf-8") as file_detind:
                                    writer_det_ind = csv.writer(file_detind, delimiter=";")
                                    first_row=["Time"]
                                    if self.Vid.Smoothed[0]:
                                        first_row+=["X_Smoothed","Y_Smoothed"]
                                    else:
                                        first_row+=["X", "Y"]

                                    first_row+=["Speed","Moving","Distance"]
                                    Shapes = ["Dist_to_" + Sh[3] for Sh in self.Vid.Analyses[1][Area]]
                                    if len(Shapes) > 0:
                                        first_row += Shapes

                                    Inds=["Dist_to_"+indT for indT in list_inds if indT!=list_inds[I]]
                                    if len(Inds) > 0:
                                        first_row += Inds

                                    writer_det_ind.writerow(first_row)
                                    for row in range(len(Details[0])):
                                        new_row=[Details[Col][row] for Col in range(len(Details))]
                                        new_row=new_row+[All_inter_dists[row][I][i] for i in range(len(All_inter_dists[row][I])) if i !=I]
                                        writer_det_ind.writerow(new_row)





                                Ind+=1

                            Ar_coos=[]
                            for TI in range(len(list_inds)):
                                Ar_coos.append(self.Coos["Ind"+str(Ind_done)])
                                Ind_done+=1

                            for Shape in self.Vid.Analyses[1][Area]:
                                if Shape[0]!="Line":
                                    Min,Max,Moy=Calc_speed.calculate_group_inside(Ar_coos, Shape, self.Arenas[Area], self.Vid)
                                    Time_inside.append([self.Vid.Name, Area,Shape[3], Min,Max,Moy])

                #Analyses related to areas:
                pos=0
                self.timer=0
                if not os.path.isdir(self.list_vid_minus[0].Folder + str("/Results/Spatial")):
                    os.makedirs(self.list_vid_minus[0].Folder + str("/Results/Spatial"))
                else:
                    files = os.listdir(self.list_vid_minus[0].Folder + str("/Results/Spatial"))
                    for file in range(len(files)):
                        os.remove(self.list_vid_minus[0].Folder + str("/Results/Spatial") + '/' + files[file])



                with open(self.list_vid_minus[0].Folder + str("/Results/Spatial/General.csv"),'w', newline='', encoding="utf-8") as file:
                    writer = csv.writer(file, delimiter=";")
                    writer.writerow(["Video", "Arena", "Shape", "Min_number_of_targets", "Max_number_of_targets", "Mean_number_of_targets"])
                    for Sh in Time_inside:
                        writer.writerow(Sh)



                for Shape_name in Shapes_infos:
                    self.loading_state.config(text="Final step")
                    self.timer=pos/len(Shapes_infos)
                    self.show_load()
                    pos += 1

                    with open(self.list_vid_minus[0].Folder + str("/Results/Spatial/Element"+"_" + Shape_name +".csv"), 'w', newline='', encoding="utf-8") as file:
                        writer = csv.writer(file, delimiter=";")
                        if Shapes_infos[Shape_name][0] == "Point":
                            writer.writerow(["Video", "Arena", "Individual", "Mean_Distance", "Latency", "Prop_time_inside"])
                            for Ind_infos in Shapes_infos[Shape_name][1:]:
                                writer.writerow(Ind_infos)

                        elif Shapes_infos[Shape_name][0] == "Line":
                            writer.writerow(["Video", "Arena", "Individual", "Mean_Distance", "Nb_crosses", "Lat_cross"])
                            for Ind_infos in Shapes_infos[Shape_name][1:]:
                                writer.writerow(Ind_infos)

                        elif Shapes_infos[Shape_name][0] == "All_borders":
                            writer.writerow(["Video", "Arena", "Individual", "Mean_Distance", "Prop_time_inside"])
                            for Ind_infos in Shapes_infos[Shape_name][1:]:
                                writer.writerow(Ind_infos)

                        elif Shapes_infos[Shape_name][0] == "Borders":
                            writer.writerow(["Video", "Arena", "Individual", "Mean_Distance", "Prop_time_inside", "Lat_inside"])
                            for Ind_infos in Shapes_infos[Shape_name][1:]:
                                writer.writerow(Ind_infos)

                        elif Shapes_infos[Shape_name][0] == "Ellipse" or Shapes_infos[Shape_name][0] == "Rectangle" or Shapes_infos[Shape_name][0] == "Polygon":
                            writer.writerow(["Video", "Arena", "Individual", "Prop_time_inside", "Lat_inside"])
                            for Ind_infos in Shapes_infos[Shape_name][1:]:
                                writer.writerow(Ind_infos)

                #Inter-ind_dists:
                with open(self.list_vid_minus[0].Folder + str("/Results/Results_InterInd.csv"), 'w', newline='', encoding="utf-8") as file:
                    writer = csv.writer(file, delimiter=";")
                    writer.writerow(["Video", "Arena", "Mean_dist", "Min_dist", "Max_dist"])
                    for row in rows_inter_dists:
                        writer.writerow(row)

                #except Exception as e:
                    #messagebox.showinfo(message=self.Messages["Do_anaWarn1"].format(e),title=self.Messages["Do_anaWarnT1"])

        #Update the main window
        self.boss.update_projects()
        self.boss.update_selections()
        self.boss.focus_set()
        self.bouton.config(state="active")
        self.bouton_sel_all.config(state="active")
        self.grab_release()

        if self.cache:#minimize
            self.boss.parent.update_idletasks()
            self.boss.parent.state('normal')
            self.boss.parent.overrideredirect(True)

        self.parent.destroy()

    def show_load(self):
        #Show the progress of the process
        self.loading_bar.delete('all')
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill="red")
        self.loading_bar.create_rectangle(0, 0, self.timer*400, self.loading_bar.cget("height"), fill="blue")
        self.loading_bar.update()

    def Load_Coos(self, Vid):
        #Import the coordinates of the tracking
        self.Coos = {}
        self.NB_ind = sum(Vid.Track[1][6])

        file_name = os.path.basename(Vid.File_name)
        point_pos = file_name.rfind(".")
        file_tracked_not_corr = Vid.Folder + "/coordinates/" + file_name[:point_pos] + "_Coordinates.csv"
        file_tracked_corr = Vid.Folder + "/corrected_coordinates/" + file_name[:point_pos] + "_Corrected.csv"

        if os.path.isfile(file_tracked_corr):
            path = file_tracked_corr
        else:
            path = file_tracked_not_corr

        for ind in range(self.NB_ind):
            with open(path, encoding="utf-8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                Ind_Coos = []
                first = True
                for row in csv_reader:
                    if not first:
                        Ind_Coos.append([row[2 + (ind * 2)], row[(3 + (ind * 2))]])
                    else:
                        first = False
            self.Coos["Ind" + str(ind)] = Ind_Coos

        if Vid.Smoothed[0] != 0:
            self.smooth_coos(window_length=Vid.Smoothed[0], polyorder=Vid.Smoothed[1])

    def smooth_coos(self, window_length, polyorder):
        #Apply a smoothing filter
        for ind in self.Coos:
            ind_coo=[[np.nan if val=="NA" else val for val in row ] for row in self.Coos[ind]]
            ind_coo=np.array(ind_coo, dtype=np.float)
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
                        if len(ind_coo[(debuts[seq] + 1):fins[seq], column]) >= window_length:
                            ind_coo[(debuts[seq] + 1):fins[seq], column] = savgol_filter(
                                ind_coo[(debuts[seq] + 1):fins[seq], column], window_length,
                                polyorder, deriv=0, delta=1.0, axis=- 1,
                                mode='interp', cval=0.0)


                else:
                    ind_coo[:, column] = savgol_filter(ind_coo[:, column],
                                                                       window_length,
                                                                       polyorder, deriv=0, delta=1.0, axis=- 1,
                                                                       mode='interp', cval=0.0)
            ind_coo = ind_coo.astype(np.str)
            ind_coo[np.where(ind_coo == "nan")] = "NA"
            ind_coo = ind_coo.tolist()
            self.Coos[ind] = ind_coo

    def random_color(self, ite=1):
        #We associate a color to each target
        cols=[]
        for replicate in range(ite):
            levels = range(32, 256, 32)
            levels = str(tuple(random.choice(levels) for _ in range(3)))
            cols.append(tuple(int(s) for s in levels.strip("()").split(",")))
        return (cols)



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