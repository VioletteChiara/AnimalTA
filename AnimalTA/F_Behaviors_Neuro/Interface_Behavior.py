from tkinter import *
from tkinter import ttk
import cv2
import numpy as np
from AnimalTA.F_Behaviors_Neuro import Class_Scroll_behav, Select_ind
from AnimalTA.E_Post_tracking import Coos_loader_saver as CoosLS
from AnimalTA.A_General_tools import Class_change_vid_menu, Class_Lecteur, Function_draw_mask as Dr, UserMessages, \
    User_help, Class_stabilise, Diverse_functions
from tkinter import filedialog
import csv
import math
import pandas as pd
import os


class Add_Behavior(Frame):
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
        self.speed=speed

        self.All_Behav=self.Vid.Events.copy()
        self.All_scrolls=[]

        #Messages importation
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        self.Messages = UserMessages.Mess[self.Language.get()]
        f.close()

        self.selected_ind = 0 #Which is the selected target

        # Video name and optionmenu to change the video:
        self.choice_menu= Class_change_vid_menu.Change_Vid_Menu(self, self.main_frame, self.Vid, "event")
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

        Traj_param=Frame(self.User_params_cont, highlightbackground = "#f0f0f0", highlightcolor= "#f0f0f0",highlightthickness=4)
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


        #Frame showing the events:

        self.Canvas_Events = Canvas(self, height=150)

        v = ttk.Scrollbar(self, orient='vertical', command=self.Canvas_Events.yview)
        v.grid(row=1, column=1, sticky="ns")



        self.Frame_Events = Frame(self.Canvas_Events)
        self.Frame_Events.bind("<Configure>",lambda e: self.Canvas_Events.configure(scrollregion=self.Canvas_Events.bbox("all")))

        Grid.columnconfigure(self.Canvas_Events, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.Canvas_Events, 0, weight=1)  ########NEW
        Grid.columnconfigure(self.Frame_Events, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.Frame_Events, 0, weight=1)  ########NEW


        self.Frame_Events.grid(sticky="nsew")
        self.Frame_Events_id = self.Canvas_Events.create_window((0, 0), window=self.Frame_Events, anchor="nw")
        self.Canvas_Events.configure(yscrollcommand=v.set)
        self.Canvas_Events.bind('<Configure>',lambda e: self.Canvas_Events.itemconfigure(self.Frame_Events_id, width=e.width))


        self.Canvas_Events.grid(row=1, sticky="nsew")
        self.Canvas_Events.propagate=False


        #Load the video
        self.load_Vid(self.Vid)

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
        self.ID_Entry=Label(Frame_ind_ID)
        self.ID_Entry.grid(row=0, column=2, sticky="nsew")
        self.ID_Entry["text"]=self.Vid.Identities[self.selected_ind][1]
        self.ID_Entry.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Control16"]))
        self.ID_Entry.bind("<Leave>", lambda a: self.HW.remove_tmp_message())

        #Targte color
        self.Can_Col=Canvas(Frame_ind_ID, background="#%02x%02x%02x" % self.Vid.Identities[0][2], height=15, width=20)
        self.Can_Col.grid(row=0, column=3, sticky="nsew")

        self.bouton_add_punctual = Button(self.User_params_cont, text=self.Messages["Events2"], command=self.add_punctual)
        self.bouton_add_punctual.grid(row=2, column=0, columnspan=3, sticky="we")

        self.bouton_save = Button(self.User_params_cont, text=self.Messages["Control3"], bg="#6AED35", command=self.save)
        self.bouton_save.grid(row=3, column=0, columnspan=3, sticky="we")

        self.afficher_events()

    def add_punctual(self):
        behavior_file = filedialog.askopenfilenames(filetypes=(("CSV", "*.csv"),("Excel", "*.xlsx"),("Excel", "*.xls"),))
        for file in behavior_file:
            newWindow = Toplevel(self)
            interface = Select_ind.Extend(parent=newWindow,  boss=self, Video_file=self.Vid, file=file)


    def load_file(self, file, ind, delay):
        _,ext= os.path.splitext(file)
        if ext.lower()==".csv":
            all_data = pd.read_csv(file, sep=";").to_numpy()
        else:
            all_data = pd.read_excel(file).to_numpy()

        all_data=all_data[1:len(all_data),:]
        try:
            delay=float(delay)
        except:
            delay=0

        for Comp in np.unique(all_data[:,1]):
            times = np.float32(all_data[np.where(all_data[:, 1] == Comp)][:, 0])
            times=times + delay
            times=times[np.where((times>=((self.Vid.Cropped[1][0])/self.Vid.Frame_rate[0])) & (times<=((self.Vid.Cropped[1][1])/self.Vid.Frame_rate[0])))]
            self.All_Behav.append([Comp, ind, list(times)])

        self.afficher_events()


    def afficher_events(self):
        for Scroll in self.All_scrolls:
            Scroll.grid_forget()
            Scroll.destroy()

        self.All_scrolls=[]
        pos=0
        for Comp in self.All_Behav:
            self.All_scrolls.append(Class_Scroll_behav.Pers_Scroll(self.Frame_Events, container=self, events=Comp[2], bd=2,
                                                           highlightthickness=1, relief='ridge',
                                                           ecart=self.Vid_Lecteur.ecart, ind=str(self.Vid.Identities[Comp[1]][1]), behav=Comp[0], behav_ID=pos,
                                                                   arena=str(self.Vid.Identities[Comp[1]][0]), color='#%02x%02x%02x' % self.Vid.Identities[Comp[1]][2]))
            pos+=1


        for Scroll in self.All_scrolls:
            Scroll.grid(sticky="nsew")


    def update_image(self, frame):
        self.Scrollbar.active_pos=frame
        self.Vid_Lecteur.update_image(frame)


    def show_all_com(self):
        #This show/hide the complete trajectories of the targets
        if self.show_all:
            self.show_all = False
            self.bouton_show_all_traj.config(background="#f0f0f0")
        else:
            self.show_all = True
            self.bouton_show_all_traj.config(background="grey80")
        self.modif_image()

    def remove_event(self, ID):
        self.All_Behav.pop(ID)
        self.afficher_events()


    def save(self, follow=False):
        #To save the modifications.
        #If follow=True, we save and open the next video
        self.Vid.Events=self.All_Behav

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


    def pressed_can(self, Pt, *args):
        #If the user press on the image.
        if int(self.Scrollbar.active_pos) >= round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every) and int(self.Scrollbar.active_pos) <= round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every):
            for ind in range(len(self.Coos)):
                center = self.Coos[ind,self.Scrollbar.active_pos-self.to_sub]
                if center[0]!=-1000:
                    dist_clic=math.sqrt((int(center[0])-Pt[0])**2+(int(center[1])-Pt[1])**2) #If user pressed on the position of a target
                    if dist_clic<max(2,(10*self.Vid_Lecteur.ratio)):
                        self.selected_ind = ind
                        self.ID_Entry["text"]=self.Vid.Identities[self.selected_ind][1]# Write the name of the target
                        self.Arena_Lab.config(text=self.Vid.Identities[self.selected_ind][0])# Write the name of the Arena
                        self.Can_Col.config(background="#%02x%02x%02x" % self.Vid.Identities[self.selected_ind][2])# indicate the color of the new selected target
                        self.modif_image(self.last_empty) # Display the changes
                        break

    def released_can(self, Pt):
        #We put back the clicked flag to false (user is not moving a target's position)
        pass

    def moved_can(self, Pt, Shift=False):
        #We put back the clicked flag to false (user is not moving a target's position)
        pass

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
        Grid.rowconfigure(self, 1, weight=1)  ########NEW
        Grid.rowconfigure(self, 2, weight=100)  ########NEW

        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=10)
        self.Vid_Lecteur.grid(row=2, column=0, sticky="nsew")
        self.Vid_Lecteur.speed.set(self.speed)
        self.Vid_Lecteur.change_speed()
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        if self.Vid.Stab[0]:
            self.prev_pts = self.Vid.Stab[1]

        #Difference in frame between the first frame of the video and the first frame of the table
        if self.Vid.Cropped[0]:
            self.to_sub = round(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every)
        else:
            self.to_sub = 0

        #We import the coordinates
        self.Coos, self.who_is_here = CoosLS.load_coos(self.Vid, location=self)
        if self.Vid.Smoothed[0] != 0:
            self.Coos=Diverse_functions.smooth_coos(self.Coos,window_length=self.Vid.Smoothed[0], polyorder=self.Vid.Smoothed[1])

        self.selected_ind=0

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


    def modif_image(self, img=[], actual_pos=None, **args):
        #Draw trajectories on teh top of the frame to be displayed
        self.Vid_Lecteur.Scrollbar.refresh()
        try:#If we loaded behavs
            for Scroll in self.All_scrolls:
                Scroll.active_pos=self.Scrollbar.active_pos
                Scroll.refresh()
        except:
            pass

        self.Vid_Lecteur.update_ratio()
        if len(img) <= 10:
            new_img=np.copy(self.last_empty)
        else:
            self.last_empty = np.copy(img)
            new_img = np.copy(img)

        if self.Vid.Stab[0]:
            new_img = Class_stabilise.find_best_position(Vid=self.Vid, Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=False, prev_pts=self.prev_pts)

        if self.Scrollbar.active_pos >= round(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every) and self.Scrollbar.active_pos <= round(self.Vid.Cropped[1][1]/self.Vid_Lecteur.one_every):
            if not self.Vid.Track[1][8]:
                cv2.drawContours(new_img, self.Arenas,-1,(150,0,200),max(1,int(2*self.Vid_Lecteur.ratio)))

            for ind in self.who_is_here[self.Scrollbar.active_pos - self.to_sub]:
                color=self.Vid.Identities[ind][2]
                if not self.show_all:
                    for prev in range(min(int(self.tail_size.get()*self.Vid.Frame_rate[1]), int(self.Scrollbar.active_pos - self.to_sub))):
                        if int(self.Scrollbar.active_pos - prev) > round(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every) and int(self.Scrollbar.active_pos) <= round(self.Vid.Cropped[1][1]/self.Vid_Lecteur.one_every):
                            if self.Coos[ind][int(self.Scrollbar.active_pos - 1 - prev - self.to_sub)][0] != -1000 and self.Coos[ind][int(self.Scrollbar.active_pos - prev - self.to_sub)][0] != -1000 :
                                TMP_tail_1 = (int(self.Coos[ind,int(self.Scrollbar.active_pos - 1 - prev - self.to_sub),0]),
                                              int(self.Coos[ind,int(self.Scrollbar.active_pos - 1 - prev - self.to_sub),1]))

                                TMP_tail_2 = (int(self.Coos[ind,int(self.Scrollbar.active_pos - prev - self.to_sub),0]),
                                              int(self.Coos[ind,int(self.Scrollbar.active_pos - prev - self.to_sub),1]))
                                new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, max(int(3*self.Vid_Lecteur.ratio),1))

                else:
                    for prev in range(1,round((self.Vid.Cropped[1][1]-self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)):
                        if self.Coos[ind,int(round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) - 1 - prev - self.to_sub),0] != -1000 and \
                                self.Coos[ind,int(round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) - prev - self.to_sub),
                                    0] != -1000:
                            TMP_tail_1 = (
                            int(self.Coos[ind,int(round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) - 1 - prev - self.to_sub),0]),
                            int(self.Coos[ind,int(round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) - 1 - prev - self.to_sub),1]))

                            TMP_tail_2 = (
                            int(self.Coos[ind,int(round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) - prev - self.to_sub),0]),
                            int(self.Coos[ind,int(round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) - prev - self.to_sub),1]))

                            new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, max(int(3*self.Vid_Lecteur.ratio),1))

                center=self.Coos[ind,self.Scrollbar.active_pos - self.to_sub]
                if center[0]!=-1000:
                    if self.selected_ind==ind:
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=max(int(5*self.Vid_Lecteur.ratio),5), color=(255,255,255),thickness=-1)
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=max(int(6*self.Vid_Lecteur.ratio),3), color=(0,0,0), thickness=-1)
                    new_img=cv2.circle(new_img,(int(center[0]),int(center[1])),radius=max(int(4*self.Vid_Lecteur.ratio),1),color=color,thickness=-1)
        self.Vid_Lecteur.afficher_img(new_img)

