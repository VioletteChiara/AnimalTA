from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
import time
import numpy as np
from BioTrack import Class_stabilise, UserMessages, Class_Lecteur, Class_ow_analyses, Analyses_Speed, Interface_smooth_param, Function_draw_mask, Interface_extend
import csv
import math
import random
import os
from scipy.signal import savgol_filter

class Analyse_track(Frame):
    def __init__(self, parent, boss, main_frame, Vid, Video_liste,CheckVar=None, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.main_frame=main_frame
        self.boss=boss
        self.Video_liste=Video_liste
        self.Vid=Vid
        self.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.highlight=False

        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        self.Messages = UserMessages.Mess[self.Language.get()]
        f.close()

        #On crée des classe liées aux différents types d'analyses
        self.Calc_speed = Analyses_Speed.speed_calculations()
        self.Infos_explo = [0,1,2]

        self.final_width=250
        self.zoom_strength=0.3
        self.tool_size=5
        self.tail_size=IntVar()
        self.tail_size.set(10)

        if CheckVar==None:
            self.CheckVar=StringVar()
            self.CheckVar.set(0)
        else:
            self.CheckVar = StringVar(value=CheckVar)

        self.clicked=False
        self.kernel = np.ones((3,3), np.uint8)
        self.liste_ana=[]
        self.overlay=None


        # Nom de la video et changer de video:
        self.canvas_video_name = Canvas(self, bd=2, highlightthickness=1, relief='flat')
        self.canvas_video_name.grid(row=0, column=0, sticky="nsew")

        self.dict_Names = { self.main_frame.list_projects[i].Video.Name : self.main_frame.list_projects[i] for i in range(0, len(self.main_frame.list_projects)) if self.main_frame.list_projects[i].Video.Tracked}

        self.liste_videos_name = [V.Name for V in self.main_frame.liste_of_videos if V.Tracked]
        holder = StringVar()
        holder.set(self.Vid.Name)
        self.bouton_change_vid = OptionMenu(self.canvas_video_name, holder, *self.dict_Names.keys(),
                                         command=self.change_vid)
        self.bouton_change_vid.config(font=("Arial",15))
        self.bouton_change_vid.grid(row=0, column=0, sticky="we")

        self.User_help = Frame(self.parent, width=150,  highlightthickness=4, relief='flat', highlightbackground="RoyalBlue3")
        self.User_help.grid(row=0, column=1, sticky="snew")
        Info_title=Label(self.User_help, text=self.Messages["Info"],  justify=CENTER, background="RoyalBlue3", fg="white", font=("Helvetica", 16, "bold"))
        Info_title.grid(row=0, sticky="nsew")
        Grid.columnconfigure(self.User_help, 0, weight=1)
        self.default_mess=self.Messages["Analyses0"]
        self.displayed_mess=StringVar(value=self.default_mess)
        self.Lab_help=Label(self.User_help, textvariable=self.displayed_mess,justify=LEFT, wraplength=250, anchor="w")
        self.Lab_help.grid(sticky="new")
        #self.User_help.grid_propagate(False)

        self.User_params_cont=Frame(self.parent, width=150)
        self.User_params_cont.grid(row=1,column=1)
        #self.User_params_cont.grid_propagate(False)


        self.Scale_tail=Scale(self.User_params_cont, from_=0, to=600, variable=self.tail_size, orient="horizontal", label=self.Messages["Control4"], command=self.modif_image)
        self.Scale_tail.grid(row=0,column=0, columnspan=3, sticky="ew")
        self.Scale_tail.bind("<Enter>", lambda a:self.displayed_mess.set(self.Messages["Analyses1"]))
        self.Scale_tail.bind("<Leave>", lambda a: self.displayed_mess.set(self.default_mess))


        Fr_smooth=Frame(self.User_params_cont)
        Fr_smooth.grid(row=1, column=0, columnspan=2, sticky="nsew")
        Fr_smooth.columnconfigure(0,weight=10)
        Fr_smooth.columnconfigure(1, weight=1)
        Fr_smooth.bind("<Enter>", lambda a:self.displayed_mess.set(self.Messages["Analyses2"]))
        Fr_smooth.bind("<Leave>", lambda a: self.displayed_mess.set(self.default_mess))
        self.Check_Smoothed=BooleanVar()
        self.Button_Smoothed_track = Checkbutton(Fr_smooth, text=self.Messages["Analyses8"],
                                                 variable=self.Check_Smoothed, onvalue=1, offvalue=0,
                                                 command=lambda: self.change_type_coos(modif=True), anchor="w")
        self.Button_Smoothed_track.grid(row=0, column=0, sticky="w")
        self.Button_Smoothed_param = Button(Fr_smooth, text="P", command=self.modif_param_smoothed,
                                            anchor="w")
        self.Button_Smoothed_param.grid(row=0, column=1, sticky="e")
        self.window_length = 15
        self.polyorder = 2


        bouton_extend_S=Button(Fr_smooth, text=self.Messages["Analyses_B1"],  command=self.extend_glob_smooth)
        bouton_extend_S.grid(row=1, column=0, columnspan=2, sticky="we")
        bouton_extend_S.bind("<Enter>", lambda a:self.displayed_mess.set(self.Messages["Analyses3"]))
        bouton_extend_S.bind("<Leave>", lambda a: self.displayed_mess.set(self.default_mess))

        self.load_Vid(self.Vid)


        self.Add_ana=Label(self.User_params_cont, text=self.Messages["Analyses_Lab1"], background="cornflower blue", height=2)
        self.Add_ana.grid(row=3, columnspan=2, sticky="nsew")

        Liste_analyses=Frame(self.User_params_cont, height=200, width=150, highlightbackground="cornflower blue", highlightthickness=4)
        Liste_analyses.grid(row=4, columnspan=2, sticky="nsew")
        Liste_analyses.columnconfigure(0, weight=1)

        self.liste_ana.append(Class_ow_analyses.Row_Ana(main=self, parent=Liste_analyses, checkvar=self.CheckVar, value="Basics", position=len(self.liste_ana)-1))
        self.liste_ana[len(self.liste_ana)-1].grid(sticky="nsew")
        self.liste_ana[len(self.liste_ana)-1].bind("<Enter>", lambda a:self.displayed_mess.set(self.Messages["Analyses4"].format(self.Vid.Scale[1])))
        self.liste_ana[len(self.liste_ana)-1].bind("<Leave>", lambda a: self.displayed_mess.set(self.default_mess))

        bouton_extend_T = Button(Liste_analyses, text=self.Messages["Analyses_B2"],command=self.extend_glob_thresh)
        bouton_extend_T.grid(columnspan=2, sticky="nswe")
        bouton_extend_T.bind("<Enter>", lambda a:self.displayed_mess.set(self.Messages["Analyses5"]))
        bouton_extend_T.bind("<Leave>", lambda a: self.displayed_mess.set(self.default_mess))

        self.liste_ana.append(Class_ow_analyses.Row_Ana(main=self, parent=Liste_analyses, checkvar=self.CheckVar, value="Spatial", position=len(self.liste_ana)-1))
        self.liste_ana[len(self.liste_ana)-1].grid(sticky="nsew")
        self.liste_ana[len(self.liste_ana)-1].bind("<Enter>", lambda a:self.displayed_mess.set(self.Messages["Analyses6"].format(self.Vid.Scale[1])))
        self.liste_ana[len(self.liste_ana)-1].bind("<Leave>", lambda a: self.displayed_mess.set(self.default_mess))


        self.liste_ana.append(Class_ow_analyses.Row_Ana(main=self, parent=Liste_analyses, checkvar=self.CheckVar, value="InterInd", position=len(self.liste_ana)-1))
        self.liste_ana[len(self.liste_ana)-1].grid(sticky="nsew")
        self.liste_ana[len(self.liste_ana)-1].bind("<Enter>", lambda a:self.displayed_mess.set(self.Messages["Analyses7"].format(self.Vid.Scale[1])))
        self.liste_ana[len(self.liste_ana)-1].bind("<Leave>", lambda a: self.displayed_mess.set(self.default_mess))

        self.liste_ana.append(Class_ow_analyses.Row_Ana(main=self, parent=Liste_analyses, checkvar=self.CheckVar, value="Exploration", position=len(self.liste_ana)-1))
        self.liste_ana[len(self.liste_ana)-1].grid(sticky="nsew")
        self.liste_ana[len(self.liste_ana)-1].bind("<Enter>", lambda a:self.displayed_mess.set(self.Messages["Analyses10"].format(self.Vid.Scale[1])))
        self.liste_ana[len(self.liste_ana)-1].bind("<Leave>", lambda a: self.displayed_mess.set(self.default_mess))

        ######NEW
        bouton_extend_E=Button(Liste_analyses, text=self.Messages["Analyses_B3"],  command=self.extend_glob_explo)
        bouton_extend_E.grid(columnspan=2, sticky="nswe")
        bouton_extend_E.bind("<Enter>", lambda a:self.displayed_mess.set(self.Messages["Analyses9"]))
        bouton_extend_E.bind("<Leave>", lambda a: self.displayed_mess.set(self.default_mess))



        self.bouton_save=Button(self.User_params_cont, text=self.Messages["Control3"], bg="green", command=self.save_And_quit)
        self.bouton_save.grid(row=5, column=0, sticky="we")

        self.bouton_saveNext=Button(self.User_params_cont, text=self.Messages["Control7"], bg="green", command=lambda: self.save_And_quit(follow=True))
        self.bouton_saveNext.grid(row=5, column=1,  sticky="we")


    def extend_glob_smooth(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Vid.Smoothed, boss=self.main_frame, Video_file=self.Vid, type="analyses_smooth")

    def extend_glob_thresh(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Calc_speed.seuil_movement, boss=self.main_frame, Video_file=self.Vid, type="analyses_thresh")

    def extend_glob_explo(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Infos_explo, boss=self.main_frame, Video_file=self.Vid, type="analyses_explo")

    def on_frame_conf(self, *arg):
        self.Liste_analyses.configure(scrollregion=self.Liste_analyses.bbox("all"))

    def change_type_coos(self, modif=False, *arg):
        self.Coos=self.Coos_brutes.copy()
        if self.Check_Smoothed.get():
            self.smooth_coos()
        self.smooth_button()
        if modif:
            self.modif_image()

    def smooth_coos(self):
        for ind in self.Coos_brutes:
            ind_coo=[[np.nan if val=="NA" else val for val in row ] for row in self.Coos_brutes[ind]]
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
            ind_coo=ind_coo.astype(np.float)
            ind_coo=ind_coo.tolist()
            ind_coo=[["NA" if np.isnan(val) else val for val in row] for row in ind_coo]
            self.Coos[ind]=ind_coo


    def smooth_button(self):
        if self.Check_Smoothed.get() == 1:
            self.Button_Smoothed_param.config(state="active")
        else:
            self.Button_Smoothed_param.config(state="disable")



    def bindings(self):
        self.bind_all("<Right>", self.move1)
        self.bind_all("<Left>", self.back1)
        self.bind_all("<space>", lambda x: self.playbacks())
        self.canvas_video.bind("<Control-1>", self.Zoom_in)
        self.canvas_video.bind("<Control-3>", self.Zoom_out)


    def resize(self, event):
        self.Scrollbar.refresh()

    def resize2(self, event):
        self.modif_image()


    def change_vid(self, vid):
        self.save_And_quit()
        self.main_frame.selected_vid = self.dict_Names[vid].Video
        self.main_frame.analyse_track(self.CheckVar.get())

    def change_color_pts(self):
        self.liste_colors=self.random_color(self.NB_ind)
        self.modif_image()

    def save_And_quit(self,follow=False):
        self.save()
        self.End_of_window(follow=follow)

    def save(self):
        self.Vid.Analyses=[0,[],[]]
        self.Vid.Analyses[0] = self.Calc_speed.seuil_movement#We save the movement threshold

        #Pickle does not accept tkinter DoubleVar:
        for Ar in self.Calc_speed.Areas:
            for shape in Ar:
                shape[2]=float(shape[2].get())
        self.Vid.Analyses[1]=self.Calc_speed.Areas
        if self.Check_Smoothed.get():
            self.Vid.Smoothed=[self.window_length,self.polyorder]#We save smooth
        else:
            self.Vid.Smoothed = [0,0]  # We save smooth

        self.Vid.Analyses[2] = self.Infos_explo  # We save the movement threshold

    def pressed_can(self, Pt):
        pass

    def moved_can(self, Pt):
        pass

    def released_can(self, Pt):
        pass


    def End_of_window(self, follow=False):
        self.unbind_all("<Button-1>")
        self.Vid_Lecteur.proper_close()
        self.boss.update()
        self.grab_release()
        self.User_params_cont.grid_forget()
        self.User_params_cont.destroy()
        self.User_help.grid_forget()
        self.User_help.destroy()
        self.main_frame.return_main()



        if follow:
            liste_tracked=[Vid for Vid in self.Video_liste if Vid.Track[0]]
            next=[Id+1 for Id, Video in enumerate(liste_tracked) if Video==self.Vid][0]
            if next<(len(liste_tracked)):
                self.main_frame.selected_vid=liste_tracked[next]
                self.main_frame.analyse_track(self.CheckVar.get())


    def onFrameConfigure(self, event):
        self.container_table.configure(scrollregion=self.container_table.bbox("all"))

    def load_Vid(self, new_Vid):
        if new_Vid != None:
            self.Vid = new_Vid

        # Visualisation de la video et barre de temps
        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=100)  ########NEW

        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        if self.Vid.Cropped[0]:
            self.to_sub = round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every))
        else:
            self.to_sub = 0


        self.load_coos()

        #We show the first frame:
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

        self.Check_Bs = []
        self.CheckVar.set(0)

        mask = Function_draw_mask.draw_mask(self.Vid)
        Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.Arenas = Function_draw_mask.Organise_Ars(Arenas)

        self.one_every=self.Vid_Lecteur.one_every

        try:
            self.Calc_speed.seuil_movement = self.Vid.Analyses[0]
            if len(self.Vid.Analyses[1])>0:
                self.Calc_speed.Areas=self.Vid.Analyses[1]
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



    def load_coos(self):
        self.Coos_brutes={}
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
            self.Coos_brutes["Ind"+str(ind)]=Ind_Coos
        self.liste_colors=self.random_color(self.NB_ind)
        self.Coos=self.Coos_brutes.copy()

        if self.Vid.Smoothed[0]!=0:
            self.window_length=self.Vid.Smoothed[0]
            self.polyorder = self.Vid.Smoothed[1]
            self.Check_Smoothed.set(1)
            self.change_type_coos()


    def random_color(self, ite=1):
        cols=[]
        for replicate in range(ite):
            levels = range(32, 256, 32)
            levels = str(tuple(random.choice(levels) for _ in range(3)))
            cols.append(tuple(int(s) for s in levels.strip("()").split(",")))
        return (cols)


    def modif_param_smoothed(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_smooth_param.Modify(parent=newWindow, boss=self)

    def modif_image(self, img=[], *args):
        if self.Vid.Cropped[0]:
            to_remove = int(round((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every))
        else:
            to_remove=0

        if len(img) <= 10:
            new_img=np.copy(self.last_empty)
        else:
            self.last_empty = img
            new_img = np.copy(img)

        if self.Vid.Stab:
            new_img = (Class_stabilise.find_best_position(Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=False))


        for ind in range(self.NB_ind):
            color=self.liste_colors[ind]
            for prev in range(min(int(self.tail_size.get()*self.Vid.Frame_rate[1]), int(self.Scrollbar.active_pos - to_remove))):
                if int(self.Scrollbar.active_pos - prev) >= round(((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)) and int(self.Scrollbar.active_pos) <= round(((self.Vid.Cropped[1][1])/self.Vid_Lecteur.one_every)):
                    if self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][0] != "NA" and self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - prev - to_remove)][0] != "NA" :
                        TMP_tail_1 = (int(float(self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][0])),
                                      int(float(self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][1])))

                        TMP_tail_2 = (int(float(self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - prev - to_remove)][0])),
                                      int(float(self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - prev - to_remove)][1])))

                        new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, 2)


        Ind_pts=[]
        if self.Scrollbar.active_pos >= round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= int(round((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every)):
            for ind in range(self.NB_ind):
                if self.CheckVar.get() == "InterInd":
                    Ind_pts.append(self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove])

                color = self.liste_colors[ind]
                if self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove][0]!="NA":
                    if self.highlight == "Ind" + str(ind):
                        new_img = cv2.circle(new_img, (int(self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove][0]), int(self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove][1])), radius=9, color=(0,0,0),thickness=-1)
                        new_img = cv2.circle(new_img, (int(self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove][0]), int(self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove][1])), radius=7, color=(255,255,255),thickness=-1)


                    new_img=cv2.circle(new_img,(int(self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove][0]),int(self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove][1])),radius=5,color=color,thickness=-1)
                    # Show speed:
                    if self.CheckVar.get() == "Basics" and self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove-1][0]!="NA" and (self.Scrollbar.active_pos) >= round(((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)+1):
                        speed = self.Calc_speed.calculate_speed(self, ind)
                        if speed<=self.Calc_speed.seuil_movement:
                            col_fond=(255,0,0)
                        else:
                            col_fond=(0,255,0)

                        if not isinstance(speed, str):
                            cv2.putText(new_img, str(round(speed, 2)), (int(self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove][0])+5,int(self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove][1])+5), cv2.FONT_HERSHEY_SIMPLEX, 1, col_fond, 10)
                            cv2.putText(new_img, str(round(speed, 2)), (int(self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove][0])+5,int(self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove][1])+5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            if self.CheckVar.get()=="InterInd":
                for nb_fish in self.Vid.Track[1][6]:
                    if nb_fish>1 :
                        new_img, dist, central = self.Calc_speed.calculate_interind_dist(Pts=Ind_pts[0:nb_fish], Scale=float(self.Vid.Scale[0]), draw=True, img=new_img)
                        if dist!="NA":
                            cv2.putText(new_img, str(round(dist, 3)), central, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 5)
                            cv2.putText(new_img, str(round(dist,3)), central, cv2.FONT_HERSHEY_SIMPLEX,1, (175,0,0), 2)
                        del Ind_pts[0:nb_fish]


        self.img_no_shapes = new_img

        if self.CheckVar.get() == "Spatial" and self.Scrollbar.active_pos >= round(((self.Vid.Cropped[1][0]-1)/self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= int(((self.Vid.Cropped[1][1]-1)/self.Vid_Lecteur.one_every)+1):
            new_img=self.draw_shapes(np.copy(self.img_no_shapes), to_remove)

        if self.CheckVar.get() == "Exploration" and self.Scrollbar.active_pos >= round(((self.Vid.Cropped[1][0] - 1) / self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= int(((self.Vid.Cropped[1][1] - 1) / self.Vid_Lecteur.one_every) + 1):
            new_img = self.draw_explo(np.copy(self.img_no_shapes), to_remove)

        self.Vid_Lecteur.afficher_img(new_img)


    def afficher(self,img,*args):
        if self.Scrollbar.active_pos<self.Scrollbar.crop_beg or self.Scrollbar.active_pos>self.Scrollbar.crop_end:
            img2= cv2.add(img,np.array([-75.0]))
        else:
            img2=img
        self.image_to_show3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img2))
        self.can_import = self.canvas_video.create_image(0, 0, image=self.image_to_show3, anchor=NW)
        self.canvas_video.config(height=self.shape[0],width=self.shape[1])
        self.canvas_video.itemconfig(self.can_import, image=self.image_to_show3)
        self.update()


    def create_overlay(self, img):
        overlay = np.zeros([img.shape[0], img.shape[1], 3], np.uint8)
        for Ar in range(len(self.Arenas)):
            for shape in self.Calc_speed.Areas[Ar]:
                if shape[0] == "Point":
                    cv2.circle(img, shape[1][0], 7, (0, 0, 0), -1)
                    cv2.circle(img, shape[1][0], 5, (0, 0, 175), -1)
                    cv2.circle(img, shape[1][0], int(round(float(shape[2].get()) * float(self.Vid.Scale[0]))),
                               (0, 0, 100), 2)
                    overlay = cv2.circle(overlay, shape[1][0],
                                         int(round(float(shape[2].get()) * float(self.Vid.Scale[0]))), (0, 0, 175), -1)

                if shape[0] == "Line":
                    for pt in shape[1]:
                        cv2.circle(img, pt, 7, (0, 0, 0), -1)
                        cv2.circle(img, pt, 5, (175, 0, 175), -1)
                    if len(shape[1]) > 1:
                        cv2.line(img, shape[1][0], shape[1][1], color=(150, 0, 150), thickness=3)

                if shape[0] == "All_borders":
                    img = cv2.drawContours(img, [self.Arenas[Ar]], -1, (255, 0, 0), 2)

                    if shape[2].get() > 0:
                        empty = np.zeros((img.shape[0], img.shape[1]), np.uint8)
                        border = cv2.drawContours(np.copy(empty), [self.Arenas[Ar]], -1, (255, 255, 255),
                                                  int(round(shape[2].get() * float(self.Vid.Scale[0]) * 2)))
                        area = cv2.drawContours(np.copy(empty), [self.Arenas[Ar]], -1, (255, 255, 255), -1)
                        empty = cv2.bitwise_and(border, border, mask=area)
                        inside_border, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                        img = cv2.drawContours(img, inside_border, -1, (150, 0, 0), 2)
                        overlay = cv2.drawContours(overlay, inside_border, -1, (255, 0, 0), -1)

                if shape[0] == "Borders":
                    for bord in shape[1]:
                        cv2.line(img, bord[0], bord[1], color=(255, 0, 0), thickness=2)

                    empty = np.zeros((img.shape[0], img.shape[1]), np.uint8)
                    border = np.copy(empty)

                    for bord in shape[1]:
                        border = cv2.line(border, bord[0], bord[1], color=(255, 0, 0), thickness=2)
                    cnts, _ = cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                    border = cv2.drawContours(border, cnts, -1, (255, 255, 255),
                                              int(round(shape[2].get() * float(self.Vid.Scale[0]) * 2)))
                    area = cv2.drawContours(np.copy(empty), [self.Arenas[Ar]], -1, (255, 255, 255), -1)
                    empty = cv2.bitwise_and(border, border, mask=area)
                    inside_border, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    img = cv2.drawContours(img, inside_border, -1, (150, 0, 0), 2)
                    overlay = cv2.drawContours(overlay, inside_border, -1, (255, 0, 0), -1)

                if shape[0] == "Ellipse":
                    if len(shape[1]) > 1:
                        Function_draw_mask.Draw_elli(img, [po[0] for po in shape[1]], [po[1] for po in shape[1]],
                                                     (0, 255, 0))
                        Function_draw_mask.Draw_elli(overlay, [po[0] for po in shape[1]], [po[1] for po in shape[1]],
                                                     (0, 255, 0), thick=-1)

                if shape[0] == "Rectangle":
                    if len(shape[1]) > 1:
                        Function_draw_mask.Draw_rect(img, [po[0] for po in shape[1]], [po[1] for po in shape[1]],
                                                     color=(0, 75, 75))
                        Function_draw_mask.Draw_rect(overlay, [po[0] for po in shape[1]], [po[1] for po in shape[1]],
                                                     color=(0, 175, 175), thick=-1)

                if shape[0] == "Poly":
                    if len(shape[1]) > 1:
                        Function_draw_mask.Draw_Poly(img, [po[0] for po in shape[1]], [po[1] for po in shape[1]],
                                                     (75, 75, 0))
                        Function_draw_mask.Draw_Poly(overlay, [po[0] for po in shape[1]], [po[1] for po in shape[1]],
                                                     (150, 150, 0), thick=-1)

        self.overlay=overlay
        self.mask = overlay.astype(bool)



    def draw_shapes(self, img, to_remove):
        self.overlay==None
        self.create_overlay(img)
        #First the ones that will appear transparent:

        for Ar in range(len(self.Arenas)):
            for shape in self.Calc_speed.Areas[Ar]:
                if shape[0] == "Point":
                    for fish in range(self.Vid.Track[1][6][Ar]):
                        if Ar > 0:
                            fish_before = sum(self.Vid.Track[1][6][0:(Ar)])
                        else:
                            fish_before = 0
                        if self.Coos["Ind" + str(fish + fish_before)][self.Scrollbar.active_pos - to_remove][0] != "NA":
                            center = self.Coos["Ind" + str(fish + fish_before)][self.Scrollbar.active_pos - to_remove]
                            cv2.line(img, (int(center[0]), int(center[1])), shape[1][0],
                                     self.liste_colors[fish + fish_before], 2)
                            dist = math.sqrt((float(center[0]) - shape[1][0][0]) ** 2 + (
                                        float(center[1]) - shape[1][0][1]) ** 2) / float(self.Vid.Scale[0])
                            cv2.putText(img, str(round(dist, 3)), (
                            int((float(center[0]) + shape[1][0][0]) / 2), int((float(center[1]) + shape[1][0][1]) / 2)),
                                        cv2.FONT_HERSHEY_DUPLEX, fontScale=1,
                                        color=(0,0,0), thickness=6)

                            cv2.putText(img, str(round(dist, 3)), (
                            int((float(center[0]) + shape[1][0][0]) / 2), int((float(center[1]) + shape[1][0][1]) / 2)),
                                        cv2.FONT_HERSHEY_DUPLEX, fontScale=1,
                                        color=self.liste_colors[fish + fish_before], thickness=2)
                if shape[0] == "Line":
                    for fish in range(self.Vid.Track[1][6][Ar]):
                        if Ar > 0:
                            fish_before = sum(self.Vid.Track[1][6][0:(Ar)])
                        else:
                            fish_before = 0
                        if self.Coos["Ind" + str(fish + fish_before)][self.Scrollbar.active_pos - to_remove][0] != "NA":
                            center = self.Coos["Ind" + str(fish + fish_before)][self.Scrollbar.active_pos - to_remove]
                            center=[int(float(center[0])),int(float(center[1]))]
                            dist,proj=Analyses_Speed.calculate_dist_one_pt_Line(Ligne=shape[1],Pt=center,Scale=float(self.Vid.Scale[0]),get_proj=True)
                            proj=[int(float(proj[0])),int(float(proj[1]))]
                            cv2.line(img, (int(center[0]), int(center[1])), proj,self.liste_colors[fish + fish_before], 2)
                            cv2.putText(img, str(round(dist, 3)), (int((float(center[0])*0.3 + proj[0]*0.7)), int((float(center[1])*0.3 + proj[1]*0.7))),
                                        cv2.FONT_HERSHEY_DUPLEX, fontScale=1,
                                        color=(0,0,0), thickness=6)

                            cv2.putText(img, str(round(dist, 3)), (int((float(center[0])*0.3 + proj[0]*0.7) ), int((float(center[1]*0.3) + proj[1]*0.7))),
                                        cv2.FONT_HERSHEY_DUPLEX, fontScale=1,
                                        color=self.liste_colors[fish + fish_before], thickness=2)

        alpha=0.35
        img[self.mask] = cv2.addWeighted(img, alpha, self.overlay, 1 - alpha, 0)[self.mask]

        return(img)


    def Organise_Ars(self, Arenas):
        heights=[]
        centers=[]
        ID=0
        for Ar in Arenas:
            x,y,w,h=cv2.boundingRect(Ar)
            heights.append(h)
            centers.append([ID,y+(h/2),x+(w/2)])
            ID+=1

        rows=[]
        centers=np.array(centers, dtype=int)
        while len(centers)>0:
            first_row=np.where(((min(centers[:,1])-max(heights)/2)<np.array(centers[:,1])) & (np.array(centers[:,1])<(min(centers[:,1])+max(heights)/2)))
            cur_row=centers[first_row]
            cur_row=cur_row[cur_row[:,2].argsort()] [:,0]
            rows=rows+list(cur_row)
            centers=np.delete(centers, first_row, axis=0)
        return [Arenas[place] for place in rows]


    def draw_explo(self, img, to_remove):
        if self.Infos_explo[0]==0:
            radius = math.sqrt((float(self.Infos_explo[1])) / math.pi)

            for Ar in range(len(self.Arenas)):
                empty = np.zeros((img.shape[0], img.shape[1], 1), np.uint8)
                for fish in range(self.Vid.Track[1][6][Ar]):
                    if Ar > 0:
                        fish_before = sum(self.Vid.Track[1][6][0:(Ar)])
                    else:
                        fish_before = 0
                    pt=self.Coos["Ind" + str(fish + fish_before)][self.Scrollbar.active_pos - to_remove]

                    if pt[0] != "NA":
                        cv2.circle(empty, (int(pt[0]), int(pt[1])), int(radius * float(self.Vid.Scale[0])), (1), -1)


                mask = np.zeros((img.shape[0], img.shape[1], 1), np.uint8)
                mask = cv2.drawContours(mask, [self.Arenas[Ar]], -1, (255), -1)
                empty = cv2.bitwise_and(mask, empty)


                bool_mask = empty.astype(bool)
                empty = cv2.cvtColor(empty, cv2.COLOR_GRAY2RGB)
                empty[:, :, 0] = empty[:, :, 0] * 255



                alpha = 0.5
                img[bool_mask] = cv2.addWeighted(img, alpha, empty, 1 - alpha, 0)[bool_mask]
            return(img)

            # To make an heatmap: (Too slow...)

        elif self.Infos_explo[0]==1:
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
                        int(max(self.Arenas[Ar][:, :, 1]) + decal_y)), color=(0, 0, 0), thickness=1)

                for horz in range(nb_squares_h + 1):
                    img = cv2.line(img, pt1=(int(min(self.Arenas[Ar][:, :, 0]) - decal_x),
                                                           int(min(self.Arenas[Ar][:, :, 1]) - decal_y + horz * (largeur))),
                                          pt2=(int(max(self.Arenas[Ar][:, :, 0]) + decal_x),
                                               int(min(self.Arenas[Ar][:, :, 1]) - decal_y + horz * (largeur))),
                                          color=(0, 0, 0),
                                          thickness=1)
            return(img)

        elif self.Infos_explo[0]==2:
            for Ar in range(len(self.Arenas)):
                M = cv2.moments(self.Arenas[Ar])
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

                max_size = max(list(np.sqrt((self.Arenas[Ar][:, :, 0] - cX) ** 2 + (self.Arenas[Ar][:, :, 1] - cY) ** 2)))

                last_rad = math.sqrt((float(self.Infos_explo[1]) * float(self.Vid.Scale[0]) ** 2) / math.pi)
                last_nb = 1
                list_rads = [last_rad]
                list_nb = [1]
                list_angles = [[0]]

                while last_rad < max_size:
                    new_rad = ((math.sqrt(last_nb) + math.sqrt(self.Infos_explo[2] ** 2)) / math.sqrt(last_nb)) * last_rad
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
                    img = cv2.circle(img, (cX, cY), int(list_rads[circle]), (0, 0, 0), 1)
                    if circle > 0:
                        for cur_angle in list_angles[circle]:
                            pt1 = (int(cX + math.cos(math.pi + cur_angle) * list_rads[circle - 1]),
                                   int(cY + math.sin(math.pi + cur_angle) * list_rads[circle - 1]))
                            pt2 = (int(cX + math.cos(math.pi + cur_angle) * list_rads[circle]),
                                   int(cY + math.sin(math.pi + cur_angle) * list_rads[circle]))
                            img = cv2.line(img, pt1, pt2, (0, 0, 0), 1)  # We draw the limits
                img = cv2.circle(img, (cX, cY), int(last_rad), (0, 0, 0), 1)

            return(img)

