from tkinter import *
import cv2
import numpy as np
from BioTrack import Class_stabilise, UserMessages, Interface_portion, Class_Lecteur
import csv
import math
from tkinter import ttk
import random
import copy
import shutil
import os
from functools import partial


class Lecteur(Frame):
    def __init__(self, parent, boss, main_frame, Vid, Video_liste, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.main_frame=main_frame
        self.boss=boss
        self.Video_liste=Video_liste
        self.Vid=Vid
        self.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.show_all=False

        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        self.Messages = UserMessages.Mess[self.Language.get()]
        f.close()

        self.final_width=250
        self.zoom_strength=0.3
        self.tool_size=5
        self.tail_size=IntVar()
        self.tail_size.set(10)
        self.CheckVar=IntVar()
        self.clicked=False
        self.kernel = np.ones((3,3), np.uint8)


        # Nom de la video et changer de video:
        self.canvas_video_name = Canvas(self, bd=2, highlightthickness=1, relief='flat')
        self.canvas_video_name.grid(row=0, column=0, sticky="nsew")

        self.dict_Names = { self.main_frame.list_projects[i].Video.Name : self.main_frame.list_projects[i] for i in range(0, len(self.main_frame.list_projects)) if self.main_frame.list_projects[i].Video.Tracked}

        self.liste_videos_name = [V.Name for V in self.main_frame.liste_of_videos]
        holder = StringVar()
        holder.set(self.Vid.Name)
        self.bouton_change_vid = OptionMenu(self.canvas_video_name, holder, *self.dict_Names.keys(),
                                         command=self.change_vid)
        self.bouton_change_vid.config(font=("Arial",15))

        self.bouton_change_vid.grid(row=0, column=0, sticky="we")

        # Visualisation de la video et barre de temps
        self.User_help = Frame(self.parent, width=150,  highlightthickness=4, relief='flat', highlightbackground="RoyalBlue3")
        self.User_help.grid(row=0, column=1, sticky="snew")
        Info_title=Label(self.User_help, text=self.Messages["Info"],  justify=CENTER, background="RoyalBlue3", fg="white", font=("Helvetica", 16, "bold"))
        Info_title.grid(row=0, sticky="nsew")
        Grid.columnconfigure(self.User_help, 0, weight=1)

        self.default_message=self.Messages["Control9"]
        self.user_message=StringVar(value=self.default_message)

        self.Lab_help=Label(self.User_help, textvariable=self.user_message,justify=LEFT, wraplength=275)
        self.Lab_help.grid(sticky="new")
        #self.User_help.grid_propagate(False)

        self.User_params_cont=Frame(self.parent, width=150)
        self.User_params_cont.grid(row=1,column=1)
        #self.User_params_cont.grid_propagate(False)

        self.max_tail=IntVar()
        self.max_tail.set(600)
        self.Scale_tail=Scale(self.User_params_cont, from_=0, to=self.max_tail.get(), variable=self.tail_size, orient="horizontal", label=self.Messages["Control4"], command=self.modif_image)
        self.Scale_tail.grid(row=0,column=0, columnspan=3, sticky="ew")

        self.bouton_change_col=Button(self.User_params_cont, text=self.Messages["Control1"], command=self.change_color_pts)
        self.bouton_change_col.grid(row=1,column=0, sticky="ew")

        self.bouton_show_all_traj=Button(self.User_params_cont, text=self.Messages["Control11"], command=self.show_all_com)
        self.bouton_show_all_traj.grid(row=1,column=1, sticky="ew")

        self.container_table = Canvas(self.User_params_cont, heigh=300, width=300, bd=2, highlightthickness=1, relief='ridge' ,scrollregion=(0,0,500,500))
        self.container_table.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.container_table.grid_propagate(False)
        Grid.columnconfigure(self.container_table, 0, weight=1)  ########NEW


        self.bouton_inter = Button(self.User_params_cont, text=self.Messages["Control5"], command=self.interpolate)
        self.bouton_inter.grid(row=4, column=0, sticky="we")
        self.bouton_inter.bind("<Enter>", partial(self.change_msg, self.Messages["General12"]))
        self.bouton_inter.bind("<Leave>", self.remove_msg)

        self.bouton_redo_track=Button(self.User_params_cont, text=self.Messages["Control6"], command=self.redo_tracking)
        self.bouton_redo_track.grid(row=4, column=1,  sticky="we")
        self.bouton_redo_track.bind("<Enter>", partial(self.change_msg, self.Messages["General13"]))
        self.bouton_redo_track.bind("<Leave>", self.remove_msg)

        self.bouton_save=Button(self.User_params_cont, text=self.Messages["Control3"], bg="green", command=self.save)
        self.bouton_save.grid(row=5, column=0, sticky="we")

        self.bouton_saveNext=Button(self.User_params_cont, text=self.Messages["Control7"], bg="green", command=lambda: self.save(follow=True))
        self.bouton_saveNext.grid(row=5, column=1,  sticky="we")

        self.bouton_remove_corrections=Button(self.User_params_cont, text=self.Messages["Control8"], command=self.remove_corr)
        self.bouton_remove_corrections.grid(row=6, column=0, columnspan=2,  sticky="we")
        self.bouton_remove_corrections.config(bg="red")

        self.load_Vid(self.Vid)
        self.bind_all("<Shift-space>", self.play_and_select)


    def play_and_select(self, event):
        if not self.Vid_Lecteur.playing:
            begin = self.Scrollbar.active_pos - self.to_sub
            curItems = self.tree.selection()
            remove_select = True

            curItems=[int(item) for item in curItems]
            if int(max(curItems)) == int(begin):
                remove_select = False

            self.Vid_Lecteur.play(select=True, remove_select=remove_select, begin=begin)
        else:
            self.Vid_Lecteur.stop()

    def change_msg(self,new_message,*arg):
        self.user_message.set(new_message)


    def remove_msg(self,*arg):
        self.user_message.set(self.default_message)

    def show_all_com(self):
        if self.show_all:
            self.show_all = False
            self.bouton_show_all_traj.config(background="SystemButtonFace")
        else:
            self.show_all = True
            self.bouton_show_all_traj.config(background="grey80")
        self.modif_image()


    def remove_corr(self):
        if os.path.isfile(self.Vid.File_name + "_Corrected.csv"):
            os.remove(self.Vid.File_name + "_Corrected.csv")
        self.load_Vid(self.Vid)
        self.update_tree_pos()
        self.modif_image()


    def change_vid(self, vid):
        self.End_of_window()
        self.main_frame.selected_vid = self.dict_Names[vid].Video
        self.main_frame.check_track()

    def redo_tracking(self):
        selected_lines = self.tree.selection()
        col = "Ind"+str(self.CheckVar.get())
        self.timer=0
        if len(selected_lines) > 2 and col != 0:
            self.first = int(selected_lines[0])+int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every)
            self.last = int(selected_lines[len(selected_lines)-1])+int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every+1)

            self.TMP_Vid=copy.deepcopy(self.Vid)
            self.TMP_Vid.Cropped[0]=1
            self.TMP_Vid.Cropped[1][0] = int(self.first*self.Vid_Lecteur.one_every)
            self.TMP_Vid.Cropped[1][1] = int((self.last-1)*self.Vid_Lecteur.one_every)

            #On crée un nouveau fichier avec seulement la partie qui nous interesse:
            if not os.path.isdir(self.Vid.Folder + str("/TMP_portion")):
                os.makedirs(self.Vid.Folder + str("/TMP_portion"))
            file_name = os.path.basename(self.Vid.File_name)
            point_pos = file_name.rfind(".")
            with open(self.Vid.Folder + "/TMP_portion/" + file_name[:point_pos] + "_TMP_portion_Coordinates.csv", 'w', newline='') as file:
                writer = csv.writer(file, delimiter=";")
                for time in range(self.last-self.first):
                    new_row=[self.first+time]
                    for ind in self.Coos:
                        new_row=new_row+self.Coos[ind][int(time+self.first- int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every))]
                    writer.writerow(new_row)

                prev_row=[self.first-1]
                if self.first > self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every:
                    for ind in self.Coos:
                        prev_row = prev_row + self.Coos[ind][self.first - int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every) -1]

                    prev_row2=[]
                    for i in prev_row:
                        if i!="NA":
                            prev_row2.append(i)
                        else:
                            prev_row2.append("NA")
                    prev_row=prev_row2

                else:
                    prev_row=None

            self.PortionWin = Toplevel()
            Interface_portion.Show(parent=self.PortionWin, boss=self, Vid=self.TMP_Vid, Video_liste=self.Video_liste, prev_row=prev_row)

        self.correct_NA()
        self.modif_image()

    def change_for_corrected(self):
        file_name = os.path.basename(self.Vid.File_name)
        point_pos = file_name.rfind(".")
        path = self.Vid.Folder + "/TMP_portion/" + file_name[:point_pos] + "_TMP_portion_Coordinates.csv"
        for ind in range(self.NB_ind):
            with open(path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                time=0
                for row in csv_reader:
                    self.Coos["Ind" + str(ind)][int(round(time + self.first - self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every))]=[row[1 + (ind * 2)], row[(2 + (ind * 2))]]
                    time+=1

        if self.Vid.Cropped[0]:
            self.Vid_Lecteur.update_image(self.Vid.Cropped[1][0])
        else:
            self.Vid_Lecteur.update_image(0)

        self.Scrollbar.active_pos=self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every
        self.last_shown=None
        self.changer_tree()
        self.modif_image()
        self.Scrollbar.refresh()
        os.remove(path)

    def change_color_pts(self):
        self.liste_colors=self.random_color(self.NB_ind)
        self.modif_image()

    def save(self, follow=False):
        self.save_file()
        self.End_of_window()
        if follow:
            liste_tracked=[Vid for Vid in self.Video_liste if Vid.Track[0]]
            next=[Id+1 for Id, Video in enumerate(liste_tracked) if Video==self.Vid][0]
            if next<(len(liste_tracked)):
                self.main_frame.selected_vid=liste_tracked[next]
                self.main_frame.check_track()

    def End_of_window(self):
        self.Vid_Lecteur.proper_close()
        self.boss.update()
        self.grab_release()
        self.capture.release()
        self.User_params_cont.grid_forget()
        self.User_params_cont.destroy()
        self.User_help.grid_forget()
        self.User_help.destroy()
        self.main_frame.return_main()

    def save_file(self):
        if self.last_shown != None:
            self.tree.item(self.last_shown, values=(self.before_row))

        file_name = os.path.basename(self.Vid.File_name)
        point_pos = file_name.rfind(".")

        if not os.path.isdir(self.main_frame.folder + str("/corrected_coordinates")):
            os.makedirs(self.main_frame.folder + str("/corrected_coordinates"))


        path_to_save= self.main_frame.folder + str("/corrected_coordinates/")+file_name[:point_pos]+"_Corrected.csv"
        with open(path_to_save, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=";")

            First_row = ["Frame"]
            for ID_AR in range(len(self.Vid.Track[1][6])):
                for ID_Ind in range(self.Vid.Track[1][6][ID_AR]):
                    First_row.append("X_Arena"+str(ID_AR)+"_Ind"+str(ID_Ind))
                    First_row.append("Y_Arena"+str(ID_AR)+"_Ind"+str(ID_Ind))
            writer.writerow(First_row)

            for child in self.tree.get_children():
                new_row=[int(child)]
                vals=self.tree.item(child)["values"]
                for val in vals[1:]:
                    new_row=new_row+val.split()
                writer.writerow(new_row)



        folder = self.main_frame.folder + str("/TMP_portion")
        if os.path.isdir(folder):
            shutil.rmtree(folder)
        self.Vid.corrected=True

    def pressed_can(self, Pt):
        if int(self.Scrollbar.active_pos) >= round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every)) and int(self.Scrollbar.active_pos) <= round(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every)):
            for col in range(self.NB_ind):
                center = self.Coos["Ind"+str(col)][self.Scrollbar.active_pos-self.to_sub]
                dist_clic=math.sqrt((int(center[0])-Pt[0])**2+(int(center[1])-Pt[1])**2)
                if dist_clic<10:
                    self.CheckVar.set(col)
                    self.modif_image(self.last_empty)
                    self.clicked=True
                    self.update_tree_pos()

    def moved_can(self, Pt):
        if self.clicked and Pt[0]>=0 and Pt[1]>=0 and Pt[0]<=self.Vid.shape[1] and Pt[1]<=self.Vid.shape[0]:
            self.Coos["Ind"+str(self.CheckVar.get())][self.Scrollbar.active_pos-self.to_sub]=[Pt[0],Pt[1]]
            new_tree_R = self.tree.item(self.Scrollbar.active_pos-self.to_sub)
            new_tree_R = (new_tree_R["values"])
            column = int([idx for idx, element in enumerate(self.tree["columns"]) if element == ("Ind"+str(self.CheckVar.get()))][0])
            self.before_row[column] = str(round(self.Coos[("Ind"+str(self.CheckVar.get()))][self.Scrollbar.active_pos-self.to_sub][0])) + " " + str(round(self.Coos[("Ind"+str(self.CheckVar.get()))][self.Scrollbar.active_pos-self.to_sub][1]))
            new_tree_R[column] = "*" + str(round(self.Coos[("Ind"+str(self.CheckVar.get()))][self.Scrollbar.active_pos-self.to_sub][0])) + " " + str(round(self.Coos[("Ind"+str(self.CheckVar.get()))][self.Scrollbar.active_pos-self.to_sub][1])) + "*"
            self.tree.item(self.Scrollbar.active_pos-self.to_sub, text="", values=new_tree_R)
            self.tree.update_idletasks()
            self.modif_image(self.last_empty)


    def released_can(self, Pt):
        self.clicked=False

    def End_of_window(self):
        self.unbind_all("<Button-1>")
        self.boss.update()
        self.grab_release()
        self.User_help.grid_forget()
        self.User_help.destroy()
        self.User_params_cont.grid_forget()
        self.User_params_cont.destroy()
        self.main_frame.return_main()

    def changer_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for col in self.Coos:
            self.container_table.update()
            self.tree.column(col, anchor=CENTER, width=int(self.container_table.winfo_width()/(len(self.Coos)+1)), minwidth=80, stretch=True)
            self.tree.heading(col, text=col, anchor=CENTER)
        for row in range(len(self.Coos[col])):
            new_row=[row+self.to_sub]+[self.Coos[k][row] for k in self.Coos]
            self.tree.insert(parent='', index=row, iid=row, text='', values=new_row)
        self.Scrollbar.active_pos=int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every)
        self.tree.selection_set(self.tree.get_children()[0])
        self.tree.update()

    def afficher_table(self):
        self.tree=ttk.Treeview(self.container_table, heigh=14)
        self.tree["columns"]=tuple(["Frame"]+[k for k in self.Coos])
        self.tree.heading('#0', text='', anchor=CENTER)
        self.tree.column('#0', width=0, stretch=NO)
        self.tree.column("Frame", anchor=CENTER, width=int(self.container_table.winfo_width()/(len(self.Coos)+1)), minwidth=80, stretch=True)
        self.tree.heading("Frame", text=self.Messages["Frame"], anchor=CENTER)

        for col in self.Coos:
            self.container_table.update()
            self.tree.column(col, anchor=CENTER, width=int(self.container_table.winfo_width()/(len(self.Coos)+1)), minwidth=80, stretch=True)
            self.tree.heading(col, text=col, anchor=CENTER)
        for row in range(len(self.Coos[col])):
            new_row=[row+self.to_sub]+[self.Coos[k][row] for k in self.Coos]
            self.tree.insert(parent='', index=row, iid=row, text='', values=new_row)
        self.tree.grid(sticky="nsew")

        self.vsb = ttk.Scrollbar(self.User_params_cont, orient="vertical", command=self.tree.yview)
        self.vsb.grid(row=2,column=2, sticky="ns")
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.vsbx = ttk.Scrollbar(self.User_params_cont, orient="horizontal", command=self.tree.xview)
        self.vsbx.grid(row=3,column=0, columnspan=3, sticky="ew")
        self.tree.configure(xscrollcommand=self.vsbx.set)

        self.tree.focus(self.tree.get_children()[0])
        self.tree.selection_set(self.tree.get_children()[0])
        self.tree.bind("<ButtonRelease>", self.selectItem)

        self.show_can=Canvas(self.tree, width=10, heigh=10)
        self.show_can.grid(row=0, column=0)
        self.show_can.place(in_=self.tree, x=0, y=0, width=1, heigh=1)

    def onFrameConfigure(self, event):
        self.container_table.configure(scrollregion=self.container_table.bbox("all"))

    def interpolate(self, *event):
        selected_lines=self.tree.selection()
        col="Ind"+str(self.CheckVar.get())
        if len(selected_lines)>2 and col!=0:
            first=int(selected_lines[0])
            last=int(selected_lines[len(selected_lines)-1])
            for raw in selected_lines[0:(len(selected_lines)-1)]:
                raw=int(raw)
                self.Coos[col][raw][0] = int(round(int(self.Coos[col][first][0]) + ((int(self.Coos[col][last][0]) - int(self.Coos[col][first][0])) * ((raw - first) / (len(selected_lines)-1))),0))
                self.Coos[col][raw][1] = int(round(int(self.Coos[col][first][1]) + ((int(self.Coos[col][last][1]) - int(self.Coos[col][first][1])) * ((raw - first) / (len(selected_lines)-1))),0))
                new_tree_R=self.tree.item(raw)
                new_tree_R=(new_tree_R["values"])
                column=int([idx for idx, element in enumerate(self.tree["columns"]) if element==col][0])
                new_tree_R[column]=str(round(self.Coos[col][raw][0])) + " " + str(round(self.Coos[col][raw][1]))
                self.tree.item(raw, text="", values=new_tree_R)
            self.modif_image()

    def load_Vid(self, new_Vid):
        self.last_shown = None
        self.curcolumn = None

        # Visualisation de la video et barre de temps
        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=100)  ########NEW

        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        #Difference in frame between the first frame of the vidéo and the first frame of the table
        if self.Vid.Cropped[0]:
            self.to_sub=round(((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every))
        else:
            self.to_sub = 0

        #We import the coordinates
        self.load_coos()

        #Representation of the tail
        if new_Vid!=None:
            self.Vid = new_Vid
        self.max_tail.set((self.Vid.Cropped[1][1]-self.Vid.Cropped[1][0])/self.Vid.Frame_rate[0])
        self.Scale_tail.config(to=self.max_tail.get())


        #We show the first frame:
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

        self.Check_Bs=[]
        self.CheckVar.set(0)

    def load_coos(self):
        self.Coos={}
        self.NB_ind = sum(self.Vid.Track[1][6])

        file_name = os.path.basename(self.Vid.File_name)
        point_pos = file_name.rfind(".")
        file_tracked_not_corr = self.main_frame.folder + "/coordinates/" + file_name[:point_pos] + "_Coordinates.csv"
        file_tracked_corr = self.main_frame.folder + "/corrected_coordinates/" + file_name[:point_pos] + "_Corrected.csv"

        if os.path.isfile(file_tracked_corr):
            path = file_tracked_corr
        else:
            path = file_tracked_not_corr

        for ind in range(self.NB_ind):
            with open(path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                Ind_Coos=[]
                first=True
                for row in csv_reader:
                    if not first:
                        Ind_Coos.append([row[1+(ind*2)],row[(2+(ind*2))]])
                    else:
                        first=False
            self.Coos["Ind"+str(ind)]=Ind_Coos
        self.liste_colors=self.random_color(self.NB_ind)

        try:
            self.tree.destroy()
        except:
            pass
        self.afficher_table()
        self.update_tree_pos()

    def random_color(self, ite=1):
        cols=[]
        for replicate in range(ite):
            levels = range(32, 256, 32)
            levels = str(tuple(random.choice(levels) for _ in range(3)))
            cols.append(tuple(int(s) for s in levels.strip("()").split(",")))
        return (cols)

    def correct_NA(self):
        self.NB_ind = len(self.Coos)
        self.Blancs = {}
        for col in self.Coos:
            self.Blancs[col] = []
            pdt_blanc = FALSE
            for raw in range(len(self.Coos[col])):
                if self.Coos[col][raw][0] == "NA":
                    if pdt_blanc == FALSE:
                        Deb = raw
                        pdt_blanc = TRUE
                else:
                    if pdt_blanc:
                        self.Blancs[col].append((Deb, raw))
                        pdt_blanc = FALSE
                if raw == (len(self.Coos[col])-1) and pdt_blanc:
                    self.Blancs[col].append((int(Deb), int(raw)))
                    pdt_blanc = FALSE


        for col in self.Coos:
            for correct in self.Blancs[col]:
                nb_raws = int(correct[1] - correct[0])
                if correct[0] != 0 and correct[1]!=(len(self.Coos[col])-1):
                    for raw in range(correct[0], correct[1]+1):
                        self.Coos[col][raw][0] = int(round(int(self.Coos[col][correct[0] - 1][0]) + ((int(self.Coos[col][correct[1]][0]) - int(self.Coos[col][correct[0] - 1][0])) * ((raw - correct[0]) / nb_raws)), 0))
                        self.Coos[col][raw][1] = int(round(int(self.Coos[col][correct[0] - 1][1]) + ((int(self.Coos[col][correct[1]][1]) - int(self.Coos[col][correct[0] - 1][1])) * ((raw - correct[0]) / nb_raws)), 0))

                elif correct[0] == 0 and correct[1]!=(len(self.Coos[col])-1):
                    for raw in range(correct[0], correct[1]+1):
                        self.Coos[col][raw][0] = int(round(int(self.Coos[col][correct[1]][0]), 0))
                        self.Coos[col][raw][1] = int(round(int(self.Coos[col][correct[1]][1]), 0))

                elif correct[0] != 0 and correct[1]==(len(self.Coos[col])-1):
                    for raw in range(correct[0], correct[1]+1):
                        self.Coos[col][raw][0] = int(round(int(self.Coos[col][correct[0]-1][0]), 0))
                        self.Coos[col][raw][1] = int(round(int(self.Coos[col][correct[0]-1][1]), 0))
                elif correct[0] == 0 and correct[1]==(len(self.Coos[col])-1):
                    for raw in range(correct[0], correct[1]+1):
                        self.Coos[col][raw][0] = 10
                        self.Coos[col][raw][1] = 10


            for raw in range(len(self.Coos[col])):
                new_tree_R = self.tree.item(raw)
                new_tree_R = (new_tree_R["values"])
                column = int([idx for idx, element in enumerate(self.tree["columns"]) if element == col][0])
                new_tree_R[column] = str(self.Coos[col][raw][0]) + " " + str(self.Coos[col][raw][1])
                self.tree.item(raw, text="", values=new_tree_R)

    def update_tree_pos(self, move=False):
        if int(self.Scrollbar.active_pos) >= round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every)) and int(self.Scrollbar.active_pos) <= round(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every)):
            if self.last_shown!= None:
                self.tree.item(self.last_shown, values=(self.before_row))
            self.before_row=self.tree.item(self.Scrollbar.active_pos-self.to_sub)["values"]
            self.last_shown=self.Scrollbar.active_pos-self.to_sub
            new_row=self.before_row.copy()
            new_row[0]="> " + str(self.before_row[0])
            new_row[self.CheckVar.get()+1]="*" + str(self.before_row[self.CheckVar.get()+1]) + "*"
            self.tree.item(self.Scrollbar.active_pos-self.to_sub, values=(new_row))
            if move:
                self.tree.yview_moveto((self.Scrollbar.active_pos - 5 - self.to_sub) / len(self.tree.get_children()))

    def modif_image(self, img=[], *args):
        self.update_tree_pos(move=True)
        if len(img) <= 10:
            new_img=np.copy(self.last_empty)
        else:
            self.last_empty = img
            new_img = np.copy(img)

        if self.Vid.Cropped[0]:
            to_remove = int(round((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every))
        else:
            to_remove=0

        if self.Vid.Stab:
            new_img = Class_stabilise.find_best_position(Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=False)


        for ind in range(self.NB_ind):
            color=self.liste_colors[ind]
            if not self.show_all:
                for prev in range(min(int(self.tail_size.get()*self.Vid.Frame_rate[1]), int(self.Scrollbar.active_pos - to_remove))):
                    if int(self.Scrollbar.active_pos - prev) > round(((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)) and int(self.Scrollbar.active_pos) <= round(((self.Vid.Cropped[1][1])/self.Vid_Lecteur.one_every)):
                        if self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][0] != "NA" and self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - prev - to_remove)][0] != "NA" :
                            TMP_tail_1 = (int(self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][0]),
                                          int(self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][1]))

                            TMP_tail_2 = (int(self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - prev - to_remove)][0]),
                                          int(self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - prev - to_remove)][1]))
                            new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, 2)

            else:
                for prev in range(1,int((self.Vid.Cropped[1][1]-self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)):
                    if self.Coos["Ind" + str(ind)][int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - 1 - prev - to_remove)][0] != "NA" and \
                            self.Coos["Ind" + str(ind)][int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - prev - to_remove)][
                                0] != "NA":
                        TMP_tail_1 = (
                        int(self.Coos["Ind" + str(ind)][int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - 1 - prev - to_remove)][0]),
                        int(self.Coos["Ind" + str(ind)][int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - 1 - prev - to_remove)][1]))

                        TMP_tail_2 = (
                        int(self.Coos["Ind" + str(ind)][int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - prev - to_remove)][0]),
                        int(self.Coos["Ind" + str(ind)][int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - prev - to_remove)][1]))

                        new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, 2)

            if self.Scrollbar.active_pos >= round(((self.Vid.Cropped[1][0]-1)/self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= int(((self.Vid.Cropped[1][1]-1)/self.Vid_Lecteur.one_every)+1):
                center=self.Coos["Ind"+str(ind)][self.Scrollbar.active_pos - to_remove]
                if center[0]!="NA":
                    new_img=cv2.circle(new_img,(int(center[0]),int(center[1])),radius=5,color=color,thickness=-1)
                    if self.CheckVar.get()==int(ind):
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=7, color=(255,255,255),thickness=3)
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=7, color=(0,0,0), thickness=2)

        self.Vid_Lecteur.afficher_img(new_img)

    def selectItem(self, event):
        column=int(self.tree.identify_column(event.x)[1:])-2
        if column>=0:
            self.CheckVar.set(column)
        curItems=self.tree.selection()
        self.Scrollbar.active_pos = int(curItems[len(curItems)-1])+self.to_sub
        self.Scrollbar.refresh()
        self.Vid_Lecteur.update_image(int(curItems[len(curItems)-1])+self.to_sub)
        self.update_tree_pos(move=False)


"""
root = Tk()
root.geometry("+100+100")
file_to_open="D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/To_Roi/Tracked/14_12_01.btr"
with open(file_to_open, 'rb') as fp:
    print(file_to_open)
    Video_liste = pickle.load(fp)
interface = Stabilise(parent=root, boss="none", Video_liste=Video_liste)
root.mainloop()
"""
