from tkinter import *
import cv2
import numpy as np
from AnimalTA import Class_stabilise, UserMessages, Interface_portion, Class_Lecteur, User_help
import csv
import math
from tkinter import ttk
import copy
import shutil
import os
from functools import partial
import PIL


class Lecteur(Frame):
    """This frame is used to show the results of the trackings.
    The user will also be able to:
     1. Correct tracking mistake
     2. Re-run part of the tracking with changes in the tracking parameters
     3. Add information about the identity of the targets and/or change their color representation
    """
    def __init__(self, parent, boss, main_frame, Vid, Video_liste, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.main_frame=main_frame
        self.boss=boss
        self.Video_liste=Video_liste
        self.Vid=Vid
        self.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.show_all=False
        self.tail_size=DoubleVar()
        self.tail_size.set(10)

        #Messages importation
        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        self.Messages = UserMessages.Mess[self.Language.get()]
        f.close()

        self.clicked=False
        self.selected_ind = 0 #Which is the selected target


        # Video name and optionmenu to change the video:
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

        # Help user and parameters
        self.HW = User_help.Help_win(self.parent, default_message=self.Messages["Control9"])
        self.HW.grid(row=0, column=1, sticky="nsew")

        self.User_params_cont=Frame(self.parent, width=150)
        self.User_params_cont.grid(row=1,column=1)

        #Scale to allow the user to choose the length of the trajectories' tails he want to see
        self.max_tail=IntVar()
        self.max_tail.set(600)
        self.Scale_tail=Scale(self.User_params_cont, from_=0, to=self.max_tail.get(), resolution=0.5, variable=self.tail_size, orient="horizontal", label=self.Messages["Control4"])
        self.Scale_tail.grid(row=0,column=0, columnspan=3, sticky="ew")
        self.Scale_tail.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control14"]))
        self.Scale_tail.bind("<Leave>", lambda a: self.HW.remove_tmp_message())

        #Button so the user can see all the trajectories at the same time
        self.bouton_show_all_traj=Button(self.User_params_cont, text=self.Messages["Control11"], command=self.show_all_com)
        self.bouton_show_all_traj.grid(row=1,column=1, sticky="nsew")

        #This canvas is used to build a table in which the coordinate sof the targets as a function of time can be viewed
        self.container_table = Canvas(self.User_params_cont, heigh=300, width=300, bd=2, highlightthickness=1, relief='ridge' ,scrollregion=(0,0,500,500))
        self.container_table.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.container_table.grid_propagate(False)
        Grid.columnconfigure(self.container_table, 0, weight=1)  ########NEW

        #Once the user selected a bunch of frames and a target, this button will create an interpolation of the target's coordinates over the selected frames.
        self.bouton_inter = Button(self.User_params_cont, text=self.Messages["Control5"], command=self.interpolate)
        self.bouton_inter.grid(row=4, column=0, sticky="we")
        self.bouton_inter.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control12"]))
        self.bouton_inter.bind("<Leave>", self.HW.remove_tmp_message)

        #After selecting a bunch of frames, this button will open a new window in which the user will be able to re-run part of the tracking with different parameters
        self.bouton_redo_track=Button(self.User_params_cont, text=self.Messages["Control6"], command=self.redo_tracking)
        self.bouton_redo_track.grid(row=4, column=1,  sticky="we")
        self.bouton_redo_track.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control13"]))
        self.bouton_redo_track.bind("<Leave>", self.HW.remove_tmp_message)

        #Save the modified coordinates
        self.bouton_save=Button(self.User_params_cont, text=self.Messages["Control3"], bg="#6AED35", command=self.save)
        self.bouton_save.grid(row=5, column=0, sticky="we")

        #Save coordinates and jump to next video
        self.bouton_saveNext=Button(self.User_params_cont, text=self.Messages["Control7"], bg="#6AED35", command=lambda: self.save(follow=True))
        self.bouton_saveNext.grid(row=5, column=1,  sticky="we")

        #Remove all the correction and come back to the original trackings coordinates
        self.bouton_remove_corrections=Button(self.User_params_cont, text=self.Messages["Control8"], command=self.remove_corr)
        self.bouton_remove_corrections.grid(row=6, column=0, columnspan=2,  sticky="we")
        self.bouton_remove_corrections.config(bg="red")

        #Load the video
        self.load_Vid(self.Vid)
        self.bind_all("<Shift-space>", self.play_and_select)

        #We create a frame that will contain all the widgets allowing to re-name a target and change its color of representation
        Frame_ind_ID=Frame(self.User_params_cont)
        Frame_ind_ID.grid(row=1,column=0, sticky="nsew")
        Arena_Lab0 = Label(Frame_ind_ID, text=self.Messages["Arena_short"])
        Arena_Lab0.grid(row=0, column=0, sticky="nsew")
        Arena_Lab0.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control15"]))
        Arena_Lab0.bind("<Leave>", lambda a: self.HW.remove_tmp_message())
        self.Arena_Lab=Label(Frame_ind_ID, text=str(self.Vid.Identities[self.selected_ind][0])+" ")
        self.Arena_Lab.grid(row=0, column=1, sticky="nsew")
        self.Arena_Lab.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control15"]))
        self.Arena_Lab.bind("<Leave>", lambda a: self.HW.remove_tmp_message())
        #Target name
        self.ID_Entry=Entry(Frame_ind_ID)
        self.ID_Entry.grid(row=0, column=2, sticky="nsew")
        self.ID_Entry.insert(0,self.Vid.Identities[self.selected_ind][1])
        self.ID_Entry.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control16"]))
        self.ID_Entry.bind("<Leave>", lambda a: self.HW.remove_tmp_message())
        Val_button=Button(Frame_ind_ID, text=self.Messages["Validate"], command=self.change_ID_name)
        Val_button.grid(row=1, column=2, sticky="nsew")
        Val_button.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control16"]))
        Val_button.bind("<Leave>", lambda a: self.HW.remove_tmp_message())
        #Targte color
        self.Can_Col=Canvas(Frame_ind_ID, background="#%02x%02x%02x" % self.Vid.Identities[0][2], height=15, width=20)
        self.Can_Col.grid(row=0, column=3, sticky="nsew")
        self.Can_Col.bind("<Button-1>", self.change_color)
        self.Can_Col.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control1"]))
        self.Can_Col.bind("<Leave>", lambda a: self.HW.remove_tmp_message())

    def change_ID_name(self, *args):
        # This function check if the name wrote by the user is not already used, it if is the case, we add "_copy" at the end.
        new_val=self.ID_Entry.get()
        if new_val != "":
            if new_val!=self.Vid.Identities[self.selected_ind][1]:
                if new_val in [self.Vid.Identities[ind][1] for ind in range(len(self.Vid.Identities))]:
                    new_val=new_val+"_copy"
                self.Vid.Identities[self.selected_ind][1]=new_val
                self.changer_tree()

    def change_color(self, event):
        #This will open a color chart to choose the color the user wants to associate with the target.
        color_choice = Toplevel()
        Canvas_colors(parent=color_choice, boss=self, ind=self.selected_ind)

    def play_and_select(self, event):
        #This allows to select all the frames displayed while playing the video.
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

    def show_all_com(self):
        #This show/hide the complete trajectories of the targets
        if self.show_all:
            self.show_all = False
            self.bouton_show_all_traj.config(background="SystemButtonFace")
        else:
            self.show_all = True
            self.bouton_show_all_traj.config(background="grey80")
        self.modif_image()

    def remove_corr(self):
        #If the user wants to remove all the modifications done.
        if os.path.isfile(self.Vid.File_name + "_Corrected.csv"):
            os.remove(self.Vid.File_name + "_Corrected.csv")
        self.load_Vid(self.Vid)
        self.update_tree_pos()
        self.modif_image()

    def change_vid(self, vid):
        #Change the working video
        self.End_of_window()
        self.main_frame.selected_vid = self.dict_Names[vid].Video
        self.main_frame.check_track()

    def redo_tracking(self):
        #Rerun part of the tracking. To do so, a temporary table and a temporary video will be created from the frames to be re-run.
        selected_lines = self.tree.selection()

        self.timer=0
        if len(selected_lines) > 2:#It works only if we select more than two frames.
            self.Vid_Lecteur.proper_close()#To avoid too much memory consumption, the current video reader is closed until the rerun is done.

            self.first = int(selected_lines[0])+int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every)
            self.last = int(selected_lines[len(selected_lines)-1])+int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every+1)

            self.TMP_Vid=copy.deepcopy(self.Vid)
            self.TMP_Vid.Cropped[0]=1
            self.TMP_Vid.Cropped[1][0] = int(self.first*self.Vid_Lecteur.one_every)
            self.TMP_Vid.Cropped[1][1] = int((self.last-1)*self.Vid_Lecteur.one_every)

            #We create a new coordinates file with onle the selected frames:
            if not os.path.isdir(self.Vid.Folder + str("/TMP_portion")):
                os.makedirs(self.Vid.Folder + str("/TMP_portion"))
            file_name = os.path.basename(self.Vid.File_name)
            point_pos = file_name.rfind(".")
            with open(self.Vid.Folder + "/TMP_portion/" + file_name[:point_pos] + "_TMP_portion_Coordinates.csv", 'w', newline='') as file:
                writer = csv.writer(file, delimiter=";")
                for time in range(self.last-self.first):
                    new_row=[self.first+time, (self.first+time)*self.Vid.Frame_rate[1]]
                    for ind in range(len(self.Coos)):
                        new_row=new_row+self.Coos[ind][int(time+self.first- int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every))]
                    writer.writerow(new_row)

                prev_row=[self.first-1, (self.first-1)/self.Vid_Lecteur.one_every]#We also check for the last known coordinates before the re-run to allow target's assigment.
                if self.first > self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every:
                    for ind in range(len(self.Coos)):
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

            #We open the portion window in which the user will be able to change the parameters of tracking and rerun this part of the video.
            self.PortionWin = Toplevel()
            Interface_portion.Show(parent=self.PortionWin, boss=self, Vid=self.TMP_Vid, Video_liste=self.Video_liste, prev_row=prev_row)


    def redo_Lecteur(self):
        #If the Video reader was destroyed (i.e. redo_tracking function), this function allows to rebuild the video reader.
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=10)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

    def change_for_corrected(self):
        #After a portion of the tracking has been rerun (see redo_tracking function), this function is called to change the old coordinates by the new ones.
        self.redo_Lecteur()
        file_name = os.path.basename(self.Vid.File_name)
        point_pos = file_name.rfind(".")
        #We load the temporary table with coordinates from rerunned tracking:
        path = self.Vid.Folder + "/TMP_portion/" + file_name[:point_pos] + "_TMP_portion_Coordinates.csv"
        for ind in range(len(self.Coos)):
            with open(path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                time=0
                #We make the change
                for row in csv_reader:
                    self.Coos[ind][int(round(time + self.first - self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every))]=[row[2 + (ind * 2)], row[(3 + (ind * 2))]]
                    time+=1

        #We place the reader at the last corrected frame
        self.Scrollbar.active_pos = int((time + self.first - self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every)
        self.Scrollbar.refresh()

        self.last_shown=None
        self.changer_tree()
        self.modif_image()
        os.remove(path)
        self.Vid_Lecteur.update_image(time + self.first - self.Vid.Cropped[1][0])

    def save(self, follow=False):
        #To save the modifications.
        #If follow=True, we save and open the next video
        self.save_file()
        self.End_of_window()
        if follow:
            liste_tracked=[Vid for Vid in self.Video_liste if Vid.Track[0]]
            next=[Id+1 for Id, Video in enumerate(liste_tracked) if Video==self.Vid][0]
            if next<(len(liste_tracked)):
                self.main_frame.selected_vid=liste_tracked[next]
                self.main_frame.check_track()
        del self

    def End_of_window(self):
        #We destroy the frame and go back to main menu
        self.Vid_Lecteur.proper_close()
        self.boss.update()
        self.grab_release()
        self.User_params_cont.grid_forget()
        self.User_params_cont.destroy()
        self.HW.grid_forget()
        self.HW.destroy()
        self.main_frame.return_main()

    def save_file(self):
        #Save the new cooridnates in a specific folder (corrected_coordinates)
        if self.last_shown != None:
            self.tree.item(self.last_shown, values=(self.before_row))

        file_name = os.path.basename(self.Vid.File_name)
        point_pos = file_name.rfind(".")

        if not os.path.isdir(self.main_frame.folder + str("/corrected_coordinates")):
            os.makedirs(self.main_frame.folder + str("/corrected_coordinates"))

        path_to_save= self.main_frame.folder + str("/corrected_coordinates/")+file_name[:point_pos]+"_Corrected.csv"
        with open(path_to_save, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=";")
            First_row = ["Frame","Time"]
            for ind in range(len(self.Coos)):
                First_row.append("X_Arena"+str(self.Vid.Identities[ind][0])+"_"+str(self.Vid.Identities[ind][1]))
                First_row.append("Y_Arena"+str(self.Vid.Identities[ind][0])+"_"+str(self.Vid.Identities[ind][1]))
            writer.writerow(First_row)

            for child in self.tree.get_children():
                new_row=[int(child)]
                new_row.append(int(child)/self.Vid.Frame_rate[1])
                vals=self.tree.item(child)["values"]
                for val in vals[1:]:
                    new_row=new_row+val.split()
                writer.writerow(new_row)

        #If there was a temporary file used, we delete it
        folder = self.main_frame.folder + str("/TMP_portion")
        if os.path.isdir(folder):
            shutil.rmtree(folder)
        self.Vid.corrected=True

    def pressed_can(self, Pt, Shift=False):
        #If the user press on the image.

        pos=0
        if int(self.Scrollbar.active_pos) >= round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every)) and int(self.Scrollbar.active_pos) <= round(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every)):
            for ind in range(len(self.Coos)):
                center = self.Coos[ind][self.Scrollbar.active_pos-self.to_sub]
                if center[0]!="NA":
                    dist_clic=math.sqrt((int(center[0])-Pt[0])**2+(int(center[1])-Pt[1])**2) #If user pressed on the position of a target
                    if dist_clic<max(2,(10*self.Vid_Lecteur.ratio)):
                        if Shift:#If user pressed Shift key, the trajectories of the current target and of the previously selected one are swaped from the current frame to the end of the video.
                            self.echange_traj(ind)
                        else: #If not, the clicked pont is the new selected target
                            self.selected_ind = ind
                            self.ID_Entry.delete(0, END)
                            self.ID_Entry.insert(0, self.Vid.Identities[self.selected_ind][1])# Write the name of the target
                            self.Arena_Lab.config(text=self.Vid.Identities[self.selected_ind][0])# Write the name of the Arena
                            self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])# indicate the color of the new selected target
                        self.modif_image(self.last_empty) # Display the changes
                        self.clicked=True# If th user wants to move the target, this flag is used to know that user is pressing left.
                        self.update_tree_pos()
                pos+=1

    def echange_traj(self, new_ind):
        #Make a swap between two targets' trajectories from the active farme to the end of the video
        self.Coos[new_ind][(self.Scrollbar.active_pos - self.to_sub):len(self.Coos[new_ind])], \
        self.Coos[self.selected_ind][(self.Scrollbar.active_pos - self.to_sub):len(self.Coos[new_ind])] \
            = \
        self.Coos[self.selected_ind][(self.Scrollbar.active_pos - self.to_sub):len(self.Coos[new_ind])], \
        self.Coos[new_ind][(self.Scrollbar.active_pos - self.to_sub):len(self.Coos[new_ind])]
        self.changer_tree()

    def moved_can(self, Pt):
        #Used to move  a target's position

        #If the user clicked on a target before and if the user does not try to put the target outside of the frame.
        if self.clicked and Pt[0]>=0 and Pt[1]>=0 and Pt[0]<=self.Vid.shape[1] and Pt[1]<=self.Vid.shape[0]:
            #We change the coordinates
            self.Coos[self.selected_ind][self.Scrollbar.active_pos-self.to_sub]=[Pt[0],Pt[1]]
            #Update the table
            new_tree_R = self.tree.item(self.Scrollbar.active_pos-self.to_sub)
            new_tree_R = (new_tree_R["values"])
            column = int([idx for idx, element in enumerate(self.tree["columns"]) if element == "Ar_" +str(self.Vid.Identities[self.selected_ind][0])+ " " + str(self.Vid.Identities[self.selected_ind][1])][0])
            self.before_row[column] = str(round(self.Coos[self.selected_ind][self.Scrollbar.active_pos-self.to_sub][0])) + " " + str(round(self.Coos[self.selected_ind][self.Scrollbar.active_pos-self.to_sub][1]))
            new_tree_R[column] = "*" + str(round(self.Coos[self.selected_ind][self.Scrollbar.active_pos-self.to_sub][0])) + " " + str(round(self.Coos[self.selected_ind][self.Scrollbar.active_pos-self.to_sub][1])) + "*"
            self.tree.item(self.Scrollbar.active_pos-self.to_sub, text="", values=new_tree_R)
            self.tree.update_idletasks()
            #Display the new frame
            self.modif_image(self.last_empty)

    def released_can(self, Pt):
        #We put back the clicked flag to false (user is not moving a target's position)
        self.clicked=False

    def changer_tree(self):
        #This function is used to redo the table
        self.tree.destroy()
        self.afficher_table()
        self.update_tree_pos(move=True)


    def afficher_table(self):
        #Display the interactive table with all the coordinates of the targets.
        #Headings
        self.tree=ttk.Treeview(self.container_table, heigh=14)
        self.tree["columns"]=tuple(["Frame"]+["Ar_" +str(self.Vid.Identities[ind][0])+ " " + str(self.Vid.Identities[ind][1]) for ind in range(len(self.Coos))])
        self.tree.heading('#0', text='', anchor=CENTER)
        self.tree.column('#0', width=0, stretch=NO)
        self.tree.column("Frame", anchor=CENTER, width=int(self.container_table.winfo_width()/(len(self.Coos)+1)), minwidth=80, stretch=True)
        self.tree.heading("Frame", text=self.Messages["Frame"], anchor=CENTER)
        for ind in range(len(self.Coos)):
            ID="Ar_" +str(self.Vid.Identities[ind][0])+ " " + str(self.Vid.Identities[ind][1])
            self.container_table.update()
            self.tree.column(ID, anchor=CENTER, width=int(self.container_table.winfo_width()/(len(self.Coos)+1)), minwidth=80, stretch=True)
            self.tree.heading(ID, text=ID, anchor=CENTER)

        # Fill the table
        for row in range(len(self.Coos[0])):
            new_row=[row+self.to_sub]+[self.Coos[ind][row] for ind in range(len(self.Coos))]
            self.tree.insert(parent='', index=row, iid=row, text='', values=new_row)

        self.tree.grid(sticky="nsew")

        #Associate the scrollbars
        self.vsb = ttk.Scrollbar(self.User_params_cont, orient="vertical", command=self.tree.yview)
        self.vsb.grid(row=2,column=2, sticky="ns")
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.vsbx = ttk.Scrollbar(self.User_params_cont, orient="horizontal", command=self.tree.xview)
        self.vsbx.grid(row=3,column=0, columnspan=3, sticky="ew")
        self.tree.configure(xscrollcommand=self.vsbx.set)

        #Allow interactions with the table
        self.tree.focus(self.tree.get_children()[0])
        self.tree.selection_set(self.tree.get_children()[0])
        self.tree.bind("<ButtonRelease>", self.selectItem)

        self.show_can=Canvas(self.tree, width=10, heigh=10)
        self.show_can.grid(row=0, column=0)
        self.show_can.place(in_=self.tree, x=0, y=0, width=1, heigh=1)

    def onFrameConfigure(self, event):
        #Adapt the size of the table to available space
        self.container_table.configure(scrollregion=self.container_table.bbox("all"))

    def interpolate(self, *event):
        #The coordinates of the selected target are changed by a straight line between the first and last frames from the selection.
        selected_lines=self.tree.selection()
        if len(selected_lines)>2:#Works only if the user selected more than 2 lines.
            first=int(selected_lines[0])
            last=int(selected_lines[len(selected_lines)-1])
            for raw in selected_lines[0:(len(selected_lines)-1)]:
                raw=int(raw)
                self.Coos[self.selected_ind][raw][0] = int(round(int( self.Coos[self.selected_ind][first][0]) + ((int( self.Coos[self.selected_ind][last][0]) - int( self.Coos[self.selected_ind][first][0])) * ((raw - first) / (len(selected_lines)-1))),0))
                self.Coos[self.selected_ind][raw][1] = int(round(int( self.Coos[self.selected_ind][first][1]) + ((int( self.Coos[self.selected_ind][last][1]) - int( self.Coos[self.selected_ind][first][1])) * ((raw - first) / (len(selected_lines)-1))),0))
                new_tree_R=self.tree.item(raw)
                new_tree_R=(new_tree_R["values"])
                column=int([idx for idx, element in enumerate(self.tree["columns"]) if element=="Ar_" +str(self.Vid.Identities[self.selected_ind][0])+ " " + str(self.Vid.Identities[self.selected_ind][1])][0])
                new_tree_R[column]=str(round(self.Coos[self.selected_ind][raw][0])) + " " + str(round(self.Coos[self.selected_ind][raw][1]))
                self.tree.item(raw, text="", values=new_tree_R)
            self.modif_image()

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

        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=10)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        #Difference in frame between the first frame of the video and the first frame of the table
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

        #We show the first frame:
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

        #Display new image when we change the size of the tail
        self.Scale_tail.config(to=self.max_tail.get(), command=self.modif_image)

        self.Check_Bs=[]

    def load_coos(self):
        #Importation of the coordinates associated with the current video
        self.Coos=[]

        file_name = os.path.basename(self.Vid.File_name)
        point_pos = file_name.rfind(".")
        file_tracked_not_corr = self.main_frame.folder + "/coordinates/" + file_name[:point_pos] + "_Coordinates.csv"
        file_tracked_corr = self.main_frame.folder + "/corrected_coordinates/" + file_name[:point_pos] + "_Corrected.csv"

        if os.path.isfile(file_tracked_corr):
            path = file_tracked_corr
        else:
            path = file_tracked_not_corr

        pos=0
        for ind in range(len(self.Vid.Identities)):
            with open(path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                Ind_Coos=[]
                first=True
                for row in csv_reader:
                    if not first:
                        Ind_Coos.append([row[2+(pos*2)],row[(3+(pos*2))]])
                    else:
                        first=False

            self.Coos.append(Ind_Coos)
            pos+=1

        self.selected_ind=0

        try:#If there was already a table, we destroy it.
            self.tree.destroy()
        except:
            pass
        self.afficher_table()
        self.update_tree_pos()

    def correct_NA(self):
        #####Not used anymore#######
        #This function can be used to fill all NA values with interpolations. This option is not available anymore.
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
                if correct[0] != 0 and correct[1] != (len(self.Coos[col])-1):
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
        #Hilight with "*" the cell corresponding to the selected target at the displayed frame.
        if int(self.Scrollbar.active_pos) >= round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every)) and int(self.Scrollbar.active_pos) <= round(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every)):
            if self.last_shown!= None:
                self.tree.item(self.last_shown, values=(self.before_row))
            self.before_row=self.tree.item(self.Scrollbar.active_pos-self.to_sub)["values"]
            self.last_shown=self.Scrollbar.active_pos-self.to_sub
            new_row=self.before_row.copy()
            new_row[0]="> " + str(self.before_row[0])
            new_row[self.selected_ind+1]="*" + str(self.before_row[self.selected_ind+1]) + "*"
            self.tree.item(self.Scrollbar.active_pos-self.to_sub, values=(new_row))

            #Move the yview of the table to make it match with the displayed frame.
            if move:
                self.tree.yview_moveto((self.Scrollbar.active_pos - 5 - self.to_sub) / len(self.tree.get_children()))

    def modif_image(self, img=[], **args):
        #Draw trajectories on teh top of the frame to be displayed
        self.update_tree_pos(move=True)
        if len(img) <= 10:
            new_img=np.copy(self.last_empty)
        else:
            self.last_empty = np.copy(img)
            new_img = np.copy(img)

        if self.Vid.Cropped[0]:
            to_remove = int(round((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every))
        else:
            to_remove=0

        if self.Vid.Stab[0]:
            new_img = Class_stabilise.find_best_position(Vid=self.Vid, Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=False)

        for ind in range(len(self.Coos)):
            color=self.Vid.Identities[ind][2]
            if not self.show_all:
                for prev in range(min(int(self.tail_size.get()*self.Vid.Frame_rate[1]), int(self.Scrollbar.active_pos - to_remove))):
                    if int(self.Scrollbar.active_pos - prev) > round(((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)) and int(self.Scrollbar.active_pos) <= round(((self.Vid.Cropped[1][1])/self.Vid_Lecteur.one_every)):
                        if self.Coos[ind][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][0] != "NA" and self.Coos[ind][int(self.Scrollbar.active_pos - prev - to_remove)][0] != "NA" :
                            TMP_tail_1 = (int(self.Coos[ind][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][0]),
                                          int(self.Coos[ind][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][1]))

                            TMP_tail_2 = (int(self.Coos[ind][int(self.Scrollbar.active_pos - prev - to_remove)][0]),
                                          int(self.Coos[ind][int(self.Scrollbar.active_pos - prev - to_remove)][1]))
                            new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, max(int(3*self.Vid_Lecteur.ratio),1))

            else:
                for prev in range(1,int((self.Vid.Cropped[1][1]-self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)):
                    if self.Coos[ind][int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - 1 - prev - to_remove)][0] != "NA" and \
                            self.Coos[ind][int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - prev - to_remove)][
                                0] != "NA":
                        TMP_tail_1 = (
                        int(self.Coos[ind][int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - 1 - prev - to_remove)][0]),
                        int(self.Coos[ind][int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - 1 - prev - to_remove)][1]))

                        TMP_tail_2 = (
                        int(self.Coos[ind][int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - prev - to_remove)][0]),
                        int(self.Coos[ind][int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - prev - to_remove)][1]))

                        new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, max(int(3*self.Vid_Lecteur.ratio),1))

            if self.Scrollbar.active_pos >= round(((self.Vid.Cropped[1][0]-1)/self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= int(((self.Vid.Cropped[1][1]-1)/self.Vid_Lecteur.one_every)+1):
                center=self.Coos[ind][self.Scrollbar.active_pos - to_remove]
                if center[0]!="NA":
                    if self.selected_ind==ind:
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=max(int(5*self.Vid_Lecteur.ratio),5), color=(255,255,255),thickness=-1)
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=max(int(6*self.Vid_Lecteur.ratio),3), color=(0,0,0), thickness=-1)
                    new_img=cv2.circle(new_img,(int(center[0]),int(center[1])),radius=max(int(4*self.Vid_Lecteur.ratio),1),color=color,thickness=-1)
        self.Vid_Lecteur.afficher_img(new_img)

    def selectItem(self, event):
        #Change the selected target according to where the user clicked in the table.
        column=int(self.tree.identify_column(event.x)[1:])-2
        if column>=0:
            for ind in range(len(self.Coos)):
                if ind==column:
                    self.selected_ind=ind
                    self.ID_Entry.delete(0,END)
                    self.ID_Entry.insert(0, self.Vid.Identities[ind][1])
                    self.Arena_Lab.config(text=self.Vid.Identities[self.selected_ind][0])
                    self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])

        curItems=self.tree.selection()
        #We move the video reader to the frame on which the user clicked in the table.
        self.Scrollbar.active_pos = int(curItems[len(curItems)-1])+self.to_sub
        self.Scrollbar.refresh()
        self.Vid_Lecteur.update_image(int(curItems[len(curItems)-1])+self.to_sub)

        self.update_tree_pos(move=False)

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
            self.boss.Vid.Identities[self.ind][2]=tuple([int(BGR) for BGR in self.bgr[event.y,event.x]])
            self.boss.modif_image()
            self.boss.Can_Col.config(background="#%02x%02x%02x" % self.boss.Vid.Identities[self.ind][2])
            self.unbind("<Button-1>")
            self.parent.destroy()

    def stay_on_top(self):
        #We want this window to always be on the top
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)
