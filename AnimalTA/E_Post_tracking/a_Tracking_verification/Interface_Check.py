from tkinter import *
import cv2
import numpy as np
from AnimalTA.E_Post_tracking.a_Tracking_verification import Interface_portion
from AnimalTA.E_Post_tracking import Coos_loader_saver as CoosLS
from AnimalTA.A_General_tools import Class_change_vid_menu, Class_Lecteur, Function_draw_mask as Dr, UserMessages, \
    User_help, Class_stabilise, Diverse_functions

from tkinter import messagebox
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


    def __init__(self, parent, boss, main_frame, Vid, Video_liste, speed=0, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
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

        #Messages importation
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        self.Messages = UserMessages.Mess[self.Language.get()]
        f.close()

        self.clicked=False
        self.selected_ind = 0 #Which is the selected target
        self.selected_rows= []#List of the rows selected by the user

        self.last_who_is_here=["Beg"]#Save the last size of the displayed table

        # Video name and optionmenu to change the video:
        self.choice_menu= Class_change_vid_menu.Change_Vid_Menu(self, self.main_frame, self.Vid, "check")
        self.choice_menu.grid(row=0, column=0)

        #We load the Arenas shapes to be able to show the user there positions
        mask = Dr.draw_mask(self.Vid)
        self.Arenas, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.Arenas = Dr.Organise_Ars(self.Arenas)

        # Help user and parameters
        self.HW = User_help.Help_win(self.parent, default_message=self.Messages["Control9"])
        self.HW.grid(row=0, column=1, sticky="nsew")

        self.User_params_cont=Frame(self.parent)
        self.User_params_cont.grid(row=1,column=1)

        Traj_param=Frame(self.User_params_cont, highlightbackground = "grey", highlightcolor= "grey",highlightthickness=4)
        Traj_param.grid(row=0, column=0, columnspan=3, sticky="nsew")
        Grid.columnconfigure(Traj_param, 0, weight=1)
        Grid.columnconfigure(Traj_param, 1, weight=1)
        Grid.columnconfigure(Traj_param, 2, weight=1)

        #Scale to allow the user to choose the length of the trajectories' tails he want to see
        self.max_tail=IntVar()
        self.max_tail.set(600)
        self.Scale_tail=Scale(Traj_param, from_=0, to=self.max_tail.get(), resolution=0.5, variable=self.tail_size, orient="horizontal", label=self.Messages["Control4"])
        self.Scale_tail.grid(row=0,column=0, columnspan=3, sticky="ew")
        self.Scale_tail.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control14"]))
        self.Scale_tail.bind("<Leave>", lambda a: self.HW.remove_tmp_message())

        #Button so the user can see all the trajectories at the same time
        self.bouton_show_all_traj=Button(Traj_param, text=self.Messages["Control11"], command=self.show_all_com)
        self.bouton_show_all_traj.grid(row=1,column=1, sticky="nsew")


        F_NAs=Frame(self.User_params_cont, background="red")
        F_NAs.grid(row=1,column=0, columnspan=3, sticky="ewns")
        Grid.columnconfigure(F_NAs, 0, weight=100)
        Grid.columnconfigure(F_NAs, 1, weight=1)

        #Button to look for the next NA values:
        self.B_look_NA=Button(F_NAs, text=self.Messages["Control17"], background="#ffa1a1", command=self.look_for_NA)
        self.B_look_NA.grid(row=0,column=0, sticky="ew")
        self.B_look_NA.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control19"]))
        self.B_look_NA.bind("<Leave>", self.HW.remove_tmp_message)

        #Button to change values for NA
        B_change_for_NA=Button(F_NAs, text=self.Messages["Control20"], command=self.change_for_NA)
        B_change_for_NA.grid(row=0,column=1,sticky="ew")
        B_change_for_NA.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control21"]))
        B_change_for_NA.bind("<Leave>", self.HW.remove_tmp_message)

        #This canvas is used to build a table in which the coordinate sof the targets as a function of time can be viewed
        self.container_table = Canvas(self.User_params_cont, heigh=300, width=300, bd=2, highlightthickness=1, relief='ridge' ,scrollregion=(0,0,500,500))
        self.container_table.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.container_table.grid_propagate(False)
        Grid.columnconfigure(self.container_table, 0, weight=1)

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

        #If the user wants to do a manual tracking, we allow the possibility to add new individuals
        self.bouton_add_new=Button(self.User_params_cont, text=self.Messages["Control22"], command=self.add_ind)
        self.bouton_add_new.grid(row=4, column=1,  sticky="we")
        self.bouton_add_new.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["Control23"]))
        self.bouton_add_new.bind("<Leave>", self.HW.remove_tmp_message)


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
        Frame_ind_ID=Frame(Traj_param)
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


    def On_mousewheel(self, event):
        if (int(self.Scrollbar.active_pos)-int(event.delta / 120) >= round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every)) and event.delta>0) or (event.delta<0 and int(self.Scrollbar.active_pos)-int(event.delta / 120) <= round(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every))):
            self.Scrollbar.active_pos=self.Scrollbar.active_pos-int(event.delta / 120)
            self.Scrollbar.refresh()
            self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)


    def change_ID_name(self, *args):
        # This function check if the name wrote by the user is not already used, it if is the case, we add "_copy" at the end.
        new_val=self.ID_Entry.get()
        if new_val != "":
            if new_val!=self.Vid.Identities[self.selected_ind][1]:
                if new_val in [self.Vid.Identities[ind][1] for ind in range(len(self.Vid.Identities))]:
                    new_val=new_val+"_copy"
                self.Vid.Identities[self.selected_ind][1]=new_val
                self.afficher_table(redo=True)

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
            self.bouton_show_all_traj.config(background="SystemButtonFace")
        else:
            self.show_all = True
            self.bouton_show_all_traj.config(background="grey80")
        self.modif_image()

    def remove_corr(self):
        #If the user wants to remove all the modifications done.
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

        self.load_Vid(self.Vid)
        self.modif_image()


    def redo_tracking(self):
        #Rerun part of the tracking. To do so, a temporary table and a temporary video will be created from the frames to be re-run.
        self.timer=0
        if len(self.selected_rows) > 2:#It works only if we select more than two frames.
            self.Vid_Lecteur.proper_close()#To avoid too much memory consumption, the current video reader is closed until the rerun is done.

            self.first = int(self.selected_rows[0])+int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every)
            self.last = int(self.selected_rows[len(self.selected_rows)-1])+int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every+1)

            self.TMP_Vid=copy.deepcopy(self.Vid)
            self.TMP_Vid.Cropped[0]=1
            self.TMP_Vid.Cropped[1][0] = int(self.first*self.Vid_Lecteur.one_every)
            self.TMP_Vid.Cropped[1][1] = int((self.last-1)*self.Vid_Lecteur.one_every)


            new_Coos=self.Coos[:,(self.first- int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every)):(self.last- int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every)),:].copy()
            CoosLS.save(self.TMP_Vid, new_Coos, TMP=True, location=self)

            #We create a new coordinates file with only the selected frames:
            if self.Vid.Track[1][8]:
                if self.first > self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every:
                    prev_row = [self.first - 1, (self.first - 1) / self.Vid_Lecteur.one_every]  # We also check for the last known coordinates before the re-run to allow target's assigment.
                    for ind in range(self.Coos.shape[0]):
                        prev_row = prev_row + list(self.Coos[ind,self.first - int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every) -1,:])

                    prev_row2=[]
                    for i in prev_row:
                        if i!=-1000:
                            prev_row2.append(i)
                        else:
                            prev_row2.append(-1000)
                    prev_row=prev_row2
                else:
                    prev_row=None
            else:
                pass
            #We open the portion window in which the user will be able to change the parameters of tracking and rerun this part of the video.
            self.PortionWin = Toplevel()
            Interface_portion.Show(parent=self.PortionWin, boss=self, Vid=self.TMP_Vid, Video_liste=self.Video_liste, prev_row=prev_row)

    def redo_Lecteur(self):
        #If the Video reader was destroyed (i.e. redo_tracking function), this function allows to rebuild the video reader.
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=10)
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


    def change_for_corrected(self):
        #After a portion of the tracking has been rerun (see redo_tracking function), this function is called to change the old coordinates by the new ones.
        #We load the temporary table with coordinates from rerunned tracking:
        if self.Vid.User_Name == self.Vid.Name:
            file_name = self.Vid.Name
            point_pos = file_name.rfind(".")
            if file_name[
               point_pos:].lower() != ".avi":  # Old versions of AnimalTA did not allow to rename or duplicate the videos, the name of the video was the file name without the ".avi" extension
                file_name = self.Vid.User_Name
            else:
                file_name = file_name[:point_pos]
        else:
            file_name = self.Vid.User_Name

        path = os.path.join(self.Vid.Folder, "TMP_portion", file_name + "_TMP_portion_Coordinates.csv")
        for ind in range(len(self.Coos)):
            with open(path, encoding="utf-8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                or_table = list(csv_reader)

            or_table = np.asarray(or_table)
            or_table[or_table == "NA"] = -1000
            or_table=or_table[1:,2:]
            for Ind in range(len(self.Vid.Identities)):
                self.Coos[Ind,self.first - self.to_sub : self.first - self.to_sub +len(or_table[:,0]),:] = or_table[:,2 * Ind:2 * Ind + 2]

        self.redo_Lecteur()
        # We place the reader at the last corrected frame
        self.Scrollbar.active_pos = int((self.first +len(or_table[:,0])-1))
        self.Scrollbar.refresh()

        self.last_shown=None
        self.afficher_table()
        os.remove(path)
        self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)
        self.look_for_NA(move_to=False)

    def save(self, follow=False):
        #To save the modifications.
        #If follow=True, we save and open the next video
        self.save_file()
        if follow:
            liste_tracked = [Vid for Vid in self.Video_liste if Vid.Tracked]
            next = [Id + 1 for Id, Video in enumerate(liste_tracked) if Video == self.Vid][0]
            if next < (len(liste_tracked)):
                self.choice_menu.change_vid(liste_tracked[next].User_Name)
                return
        self.End_of_window()

    def End_of_window(self):
        #We destroy the frame and go back to main menu
        self.Vid_Lecteur.proper_close()
        self.grab_release()
        self.User_params_cont.grid_forget()
        self.User_params_cont.destroy()
        self.HW.grid_forget()
        self.HW.destroy()
        self.main_frame.return_main()
        del self

    def save_file(self):
        #Save the new cooridnates in a specific folder (corrected_coordinates)
        CoosLS.save(self.Vid, self.Coos, location=self)
        #If there was a temporary file used, we delete it
        folder = os.path.join(self.main_frame.folder, "TMP_portion")
        if os.path.isdir(folder):
            shutil.rmtree(folder)
        self.Vid.corrected=True

    def pressed_can(self, Pt, Shift=False):
        #If the user press on the image.
        pos=0
        if int(self.Scrollbar.active_pos) >= round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every)) and int(self.Scrollbar.active_pos) <= round(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every)):
            for ind in range(len(self.Coos)):
                center = self.Coos[ind,self.Scrollbar.active_pos-self.to_sub]
                if center[0]!=-1000:
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
                pos+=1

    def echange_traj(self, new_ind):
        #Make a swap between two targets' trajectories from the active farme to the end of the video
        self.Coos[new_ind,(self.Scrollbar.active_pos - self.to_sub):len(self.Coos[new_ind])], \
        self.Coos[self.selected_ind,(self.Scrollbar.active_pos - self.to_sub):len(self.Coos[new_ind])] \
            = \
        self.Coos[self.selected_ind,(self.Scrollbar.active_pos - self.to_sub):len(self.Coos[new_ind])], \
        self.Coos[new_ind,(self.Scrollbar.active_pos - self.to_sub):len(self.Coos[new_ind])].copy()

        self.afficher_table(redo=True)
        self.modif_image()

    def moved_can(self, Pt, Shift):
        #Used to move  a target's position
        #If the user clicked on a target before and if the user does not try to put the target outside of the frame.
        if self.clicked and Pt[0]>=0 and Pt[1]>=0 and Pt[0]<=self.Vid.shape[1] and Pt[1]<=self.Vid.shape[0]:
            #We change the coordinates
            self.Coos[self.selected_ind,self.Scrollbar.active_pos-self.to_sub]=[Pt[0],Pt[1]]
            #Display the new frame
            self.modif_image(self.last_empty)

    def right_click(self, Pt):
        #If the target position was unknown (NA value), the user can create a new position using a right click.
        if self.Coos[self.selected_ind,self.Scrollbar.active_pos-self.to_sub][0]==-1000:
            self.Coos[self.selected_ind, self.Scrollbar.active_pos - self.to_sub] = [Pt[0], Pt[1]]
            self.modif_image(self.last_empty)

            self.Scrollbar.active_pos += 1
            self.Scrollbar.refresh()
            self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)
            self.afficher_table()


    def released_can(self, Pt):
        #We put back the clicked flag to false (user is not moving a target's position)
        self.clicked=False

    def afficher_table(self, actual_pos=None, redo=False):
        #Display the interactive table with all the coordinates of the targets.
        #Headings
        if actual_pos==None:
            actual_pos=self.Scrollbar.active_pos #What are the row to show

        displayed_frame=self.Scrollbar.active_pos - self.to_sub #To avoid that the scrollbar position changes before the table is updated, the position of the displayed frame

        if actual_pos >= round(((self.Vid.Cropped[1][0] - 1) / self.Vid_Lecteur.one_every)) and actual_pos <= int(((self.Vid.Cropped[1][1] - 1) / self.Vid_Lecteur.one_every) + 1):
            if actual_pos - self.to_sub - int(self.table_heigh / 2) < 0:
                deb = -(actual_pos - self.to_sub)
            else:
                deb = -int(self.table_heigh / 2)

            if actual_pos - self.to_sub + int(self.table_heigh / 2) > len(self.Coos[0]):
                redo=True #If there is not enought lines to be displayed, we redo the graph with less rows
                end = len(self.Coos[0]) - (actual_pos - self.to_sub)
                deb = end - self.table_heigh
                if deb<0:
                    deb=0
            else:
                end = deb + self.table_heigh

            Ind_to_show=self.who_is_here[deb + actual_pos - self.to_sub : end + actual_pos - self.to_sub]
            Ind_to_show=[val for sub in Ind_to_show for val in sub]
            Ind_to_show=list(set(Ind_to_show))
            Ind_to_show.sort()

            if self.last_who_is_here!= Ind_to_show or redo:
                redo=True
                try:#If the tree is not created yet
                    self.tree.destroy()
                    del self.tree
                except:
                   pass

               # Fill the table
                self.tree=ttk.Treeview(self.container_table, heigh=self.table_heigh)
                self.tree["columns"]=tuple(["Frame"]+["Ar_" +str(self.Vid.Identities[ind][0])+ " " + str(self.Vid.Identities[ind][1]) for ind in Ind_to_show])
                self.tree.heading('#0', text='', anchor=CENTER)
                self.tree.column('#0', width=0, stretch=NO)
                self.tree.column("Frame", anchor=CENTER, width=int(self.container_table.winfo_width()/(len(self.Coos)+1)), minwidth=80, stretch=True)
                self.tree.heading("Frame", text=self.Messages["Frame"], anchor=CENTER)
                for ind in Ind_to_show:
                    ID = "Ar_" + str(self.Vid.Identities[ind][0]) + " " + str(self.Vid.Identities[ind][1])
                    self.tree.column(ID, anchor=CENTER, width=int(self.container_table.winfo_width() / (
                                len(Ind_to_show) + 1)), minwidth=80,
                                     stretch=True)
                    self.tree.heading(ID, text=ID, anchor=CENTER)
                self.container_table.update()
                self.tree.bind("<MouseWheel>", self.On_mousewheel)


            cnt = 0
            self.vals_in_table = []
            for row in range(deb, end):
                is_current=False
                is_NA=False
                pos_in_coos = row + actual_pos - self.to_sub
                self.vals_in_table.append(pos_in_coos)
                if pos_in_coos==displayed_frame:
                    Rnum="=> " + str(row + actual_pos)
                    is_current=True
                else:
                    Rnum = str(row + actual_pos)

                Pos=[]
                for ind in Ind_to_show:
                    if (ind == self.selected_ind and pos_in_coos==displayed_frame):
                        if self.Coos[ind,row+actual_pos-self.to_sub,0]!=-1000:
                            Pos=Pos+["*" + str(round(self.Coos[ind,row+actual_pos-self.to_sub,0],2)) + " " + str(round(self.Coos[ind,row+actual_pos-self.to_sub,1],2)) + "*"]
                        else:
                            Pos = Pos + ["*NA NA*"]
                            is_NA=True
                    else:
                        if self.Coos[ind, row + actual_pos - self.to_sub, 0] != -1000:
                            Pos=Pos+[str(round(self.Coos[ind,row+actual_pos-self.to_sub,0],2))+" "+str(round(self.Coos[ind,row+actual_pos-self.to_sub,1],2))]
                        else:
                            Pos = Pos + ["NA NA"]
                            is_NA=True

                new_row=[Rnum]+Pos

                try:
                        self.tree.insert(parent='', index=cnt, iid=cnt, text='', values=new_row)
                except:
                    self.tree.item(cnt, text='', values=new_row, tags=('NAs'))

                if is_NA and is_current:
                    self.tree.item(cnt, tags=('NAs','Current'))
                elif is_NA and not is_current:
                    self.tree.item(cnt, tags=('NAs', 'Not_Current'))
                elif not is_NA and is_current:
                    self.tree.item(cnt, tags=('Normal', 'Current'))
                elif not is_NA and not is_current:
                    self.tree.item(cnt, tags=('Normal', 'Not_Current'))

                cnt+=1


            self.tree.tag_configure('NAs', background="#ffa1a1")
            self.tree.tag_configure('Normal', background="white")
            self.tree.tag_configure('Current', font=('Arial', 10, 'bold'))
            self.tree.tag_configure('Not_Current', font=('Arial', 10))


            if redo:
                self.vsbx = ttk.Scrollbar(self.User_params_cont, orient="horizontal", command=self.tree.xview)
                self.vsbx.grid(row=3, column=0, columnspan=3, sticky="ew")
                self.tree.configure(xscrollcommand=self.vsbx.set)

            self.tree.grid(sticky="nsew")

            #Allow interactions with the table
            self.tree.bind("<ButtonRelease>", self.selectItem)
            self.tree.bind("<Shift-ButtonRelease>", partial(self.selectItem,Shift=True))

            self.show_can=Canvas(self.tree, width=10, heigh=10)
            self.show_can.grid(row=0, column=0)
            self.show_can.place(in_=self.tree, x=0, y=0, width=1, heigh=1)

            self.last_who_is_here = Ind_to_show.copy()

            new_sel=[rowID for rowID in range(len(self.vals_in_table)) if self.vals_in_table[rowID] in self.selected_rows]
            self.tree.selection_set(new_sel)


            try:#If it is the first frame, the scrollbar is not created yey so raise an error
                self.vsb.set(actual_pos)#We move the scrollbar to the good position
            except:
                pass

    def move_tree(self, event):
        self.Scrollbar.active_pos=self.vsb.get()
        self.Scrollbar.refresh()
        self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)

    def onFrameConfigure(self, event):
        #Adapt the size of the table to available space
        self.container_table.configure(scrollregion=self.container_table.bbox("all"), width=300, height=300)

    def interpolate(self, *event):
        #The coordinates of the selected target are changed by a straight line between the first and last frames from the selection.
        if len(self.selected_rows)>2:
            if (self.Coos[self.selected_ind,self.selected_rows[0],0]!=-1000 or self.Coos[self.selected_ind,self.selected_rows[-1],0]!=-1000):#Works only if the user selected more than 2 lines and not NAs in both first and last.
                first=int(self.selected_rows[0])
                last=int(self.selected_rows[-1])

                add=0
                if self.Coos[self.selected_ind,self.selected_rows[0],0] == -1000:
                    first=last
                elif self.Coos[self.selected_ind,self.selected_rows[-1],0] == -1000:
                    last=first
                    add = 1

                for raw in self.selected_rows[0:len(self.selected_rows)-1+add]:
                    raw=int(raw)
                    self.Coos[self.selected_ind,raw,0] = (( self.Coos[self.selected_ind,first,0]) + ((( self.Coos[self.selected_ind,last,0]) - ( self.Coos[self.selected_ind,first,0])) * ((raw - first) / (len(self.selected_rows)-1))))
                    self.Coos[self.selected_ind,raw,1] = (( self.Coos[self.selected_ind,first,1]) + ((( self.Coos[self.selected_ind,last,1]) - ( self.Coos[self.selected_ind,first,1])) * ((raw - first) / (len(self.selected_rows)-1))))
                    if self.selected_ind not in self.who_is_here[raw]:
                        self.who_is_here[raw].append(self.selected_ind)

                self.look_for_NA(move_to=False)
                self.modif_image()

        else:
            response=messagebox.askyesno(message=self.Messages["Control2"])
            if response:
                self.correct_NA()

    def look_for_NA(self, move_to=True):
        #If the user want to jump toward the next NA value
        Pos=np.where(self.Coos==-1000)
        lines=Pos[1]
        if len(lines)>0:
            try:
                res = next(val for x, val in enumerate(lines) if val > self.Scrollbar.active_pos-self.to_sub)
            except:#If we passed the last NA, we take the first one
                res=lines[0]

            if move_to:
                self.Scrollbar.active_pos = res +self.to_sub
                self.Scrollbar.refresh()
                self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)

        if len(lines)==0:
            self.B_look_NA.config(state="disable", activebackground="#8de3a4", background="#8de3a4", text=self.Messages["Control18"])
        else:
            self.B_look_NA.config(state="active",activebackground="#ffa1a1", background="#ffa1a1", text=self.Messages["Control17"])

    def change_for_NA(self):
        #If the user wants to attribute NA values:
        self.Coos[self.selected_ind, self.selected_rows, :]=-1000
        self.look_for_NA(move_to=False)
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
        self.Vid_Lecteur.speed.set(self.speed)
        self.Vid_Lecteur.change_speed()
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        if self.Vid.Stab[0]:
            self.prev_pts = self.Vid.Stab[1]

        #Difference in frame between the first frame of the video and the first frame of the table
        if self.Vid.Cropped[0]:
            self.to_sub = round(((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every))
        else:
            self.to_sub = 0

        #We import the coordinates
        self.Coos, self.who_is_here = CoosLS.load_coos(self.Vid, location=self)
        self.selected_ind=0
        self.afficher_table()

        # Associate the vertical scrollbar with the table
        self.vsb = Scale(self.User_params_cont, from_=self.to_sub, to=self.to_sub + len(self.Coos[0]) -1,orient="vertical")
        self.vsb.grid(row=2, column=2, sticky="ns")
        self.vsb.bind("<ButtonRelease-1>", self.move_tree)

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

        #The redo-tracking option is not available for unknown number of targets:
        if self.Vid.Track[1][8] and self.Vid.Track[0]:
            self.bouton_redo_track.grid(row=4, column=1, sticky="we")
            self.bouton_inter.grid(row=4, column=0, sticky="we", columnspan=1)
            self.bouton_add_new.grid_forget()
        elif not self.Vid.Track[0]:#If the user choose manual tracking, we add the possibility to manually add new indivduals
            self.bouton_inter.grid(row=4, column=0, sticky="we", columnspan=1)
            self.bouton_add_new.grid(row=4, column=1, sticky="we", columnspan=1)
            self.bouton_redo_track.grid_forget()
        else:#If it was a variable number of targets.
            self.bouton_inter.grid(row=4, column=0, sticky="we", columnspan=2)
            self.bouton_redo_track.grid_forget()
            self.bouton_add_new.grid_forget()

        self.Check_Bs=[]
        self.look_for_NA(move_to=False)


    def add_ind(self):#If the user wants to add a new individual (only available for manual tracking)
        Arena= self.Vid.Identities[self.selected_ind][0]
        self.Vid.Identities.append([Arena,"Ind"+str(self.Vid.Track[1][6][Arena]),Diverse_functions.random_color()[0]])
        self.Vid.Track[1][6][Arena]+=1

        empty_new_rows=np.zeros([len(self.Coos[0]),2], dtype="object")
        empty_new_rows.fill(-1000)

        shape=self.Coos.shape
        self.Coos=np.append(self.Coos, empty_new_rows)
        self.Coos.shape=(shape[0]+1, shape[1],shape[2])

        self.who_is_here=[list(range(len(self.Vid.Identities)))]*len(self.Coos[0])
        self.afficher_table()


    def correct_NA(self):
        self.Blancs = []
        for col in range(len(self.Coos)):
            self.Blancs.append([])
            pdt_blanc = FALSE
            for raw in range(len(self.Coos[col])):
                if self.Coos[col][raw][0] == -1000:
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

        for col in range(len(self.Coos)):
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
        self.modif_image()


    def modif_image(self, img=[], actual_pos=None, **args):
        #Draw trajectories on teh top of the frame to be displayed
        self.afficher_table(actual_pos=actual_pos)
        self.Vid_Lecteur.update_ratio()
        if len(img) <= 10:
            new_img=np.copy(self.last_empty)
        else:
            self.last_empty = np.copy(img)
            new_img = np.copy(img)

        if self.Vid.Stab[0]:
            new_img = Class_stabilise.find_best_position(Vid=self.Vid, Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=False, prev_pts=self.prev_pts)

        if self.Scrollbar.active_pos >= round(((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= int(((self.Vid.Cropped[1][1])/self.Vid_Lecteur.one_every)):
            if not self.Vid.Track[1][8]:
                cv2.drawContours(new_img, self.Arenas,-1,(150,0,200),max(1,int(2*self.Vid_Lecteur.ratio)))

            for ind in self.who_is_here[self.Scrollbar.active_pos - self.to_sub]:
                color=self.Vid.Identities[ind][2]
                if not self.show_all:
                    for prev in range(min(int(self.tail_size.get()*self.Vid.Frame_rate[1]), int(self.Scrollbar.active_pos - self.to_sub))):
                        if int(self.Scrollbar.active_pos - prev) > round(((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)) and int(self.Scrollbar.active_pos) <= round(((self.Vid.Cropped[1][1])/self.Vid_Lecteur.one_every)):
                            if self.Coos[ind][int(self.Scrollbar.active_pos - 1 - prev - self.to_sub)][0] != -1000 and self.Coos[ind][int(self.Scrollbar.active_pos - prev - self.to_sub)][0] != -1000 :
                                TMP_tail_1 = (int(self.Coos[ind,int(self.Scrollbar.active_pos - 1 - prev - self.to_sub),0]),
                                              int(self.Coos[ind,int(self.Scrollbar.active_pos - 1 - prev - self.to_sub),1]))

                                TMP_tail_2 = (int(self.Coos[ind,int(self.Scrollbar.active_pos - prev - self.to_sub),0]),
                                              int(self.Coos[ind,int(self.Scrollbar.active_pos - prev - self.to_sub),1]))
                                new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, max(int(3*self.Vid_Lecteur.ratio),1))

                else:
                    for prev in range(1,int((self.Vid.Cropped[1][1]-self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)):
                        if self.Coos[ind,int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - 1 - prev - self.to_sub),0] != -1000 and \
                                self.Coos[ind,int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - prev - self.to_sub),
                                    0] != -1000:
                            TMP_tail_1 = (
                            int(self.Coos[ind,int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - 1 - prev - self.to_sub),0]),
                            int(self.Coos[ind,int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - 1 - prev - self.to_sub),1]))

                            TMP_tail_2 = (
                            int(self.Coos[ind,int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - prev - self.to_sub),0]),
                            int(self.Coos[ind,int(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every) - prev - self.to_sub),1]))

                            new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, max(int(3*self.Vid_Lecteur.ratio),1))

                center=self.Coos[ind,self.Scrollbar.active_pos - self.to_sub]
                if center[0]!=-1000:
                    if self.selected_ind==ind:
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=max(int(5*self.Vid_Lecteur.ratio),5), color=(255,255,255),thickness=-1)
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=max(int(6*self.Vid_Lecteur.ratio),3), color=(0,0,0), thickness=-1)
                    new_img=cv2.circle(new_img,(int(center[0]),int(center[1])),radius=max(int(4*self.Vid_Lecteur.ratio),1),color=color,thickness=-1)
        self.Vid_Lecteur.afficher_img(new_img)

    def selectItem(self, event, Shift=False):
        #Triggered when the user click inside the table
        #We move the video reader to the frame on which the user clicked in the table.

        row=self.tree.identify_row(event.y)

        if row!="":#If the user pressed one row which is not the header, we move the video to the corresponding frame and update the selection
            row=int(row)

            self.Scrollbar.active_pos = self.vals_in_table[row]+self.to_sub
            self.Scrollbar.refresh()

            if Shift:
                if self.vals_in_table[row]>min(self.selected_rows):
                    self.selected_rows=list(range(min(self.selected_rows),self.vals_in_table[row]+1))
                else:
                    self.selected_rows=list(range(self.vals_in_table[row], max(self.selected_rows)+1))
            else:
                self.selected_rows=[self.vals_in_table[row]]

            self.Vid_Lecteur.update_image(self.vals_in_table[row] + self.to_sub, actual_pos=int(self.vsb.get()))


        column=int(self.tree.identify_column(event.x)[1:])-2#We then identify which individual was linked to the pressed column
        if column>=0:
            ind = self.last_who_is_here[column]
            if Shift and len(self.selected_rows)<2:
                self.echange_traj(ind)
            else:
                self.selected_ind = ind
                self.ID_Entry.delete(0,END)
                self.ID_Entry.insert(0, self.Vid.Identities[self.selected_ind][1])
                self.Arena_Lab.config(text=self.Vid.Identities[self.selected_ind][0])
                self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])
                self.modif_image()
                self.afficher_table()


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
