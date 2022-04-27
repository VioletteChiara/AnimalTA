from tkinter import *
import cv2
import numpy as np
import csv
import random
import os
from BioTrack import Interface_masking, Class_stabilise, UserMessages, Interface_back, Class_Lecteur, Interface_parameters_track, Do_the_track3

class Show(Frame):
    def __init__(self, parent, boss, Vid, Video_liste, prev_row=None, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent = parent
        self.boss = boss
        self.grid(sticky="nsew")
        self.Video_liste = Video_liste
        self.Vid=Vid
        self.boss.PortionWin.grab_set()
        self.prev_row=prev_row

        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.tail_size=5

        Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW

        self.Folder=self.Vid.Folder

        self.CheckVar = IntVar()
        self.ecart=10#hOW MUCH FRAME WE ADD AT the timeline

        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Portion0"])

        Right_part=Frame(self)
        Right_part.grid(row=0, column=1)

        self.User_help = Frame(Right_part)
        self.User_help.grid(row=0, column=0, sticky="new")
        self.Lab_help=Label(self.User_help, text=self.Messages["Portion11"], wraplength=300)
        self.Lab_help.grid()

        self.User_buttons = Frame(Right_part)
        self.User_buttons.grid(row=1, rowspan=3, column=0, sticky="sew")

        self.bouton_change_col=Button(self.User_buttons, text=self.Messages["Portion1"], command=self.change_color_pts)
        self.bouton_change_col.grid(row=0,column=0, columnspan=2, sticky="ew")

        self.text_stab=StringVar()
        if self.Vid.Stab:
            self.text_stab.set(self.Messages["Portion2"])
        else:
            self.text_stab.set(self.Messages["Portion3"])

        self.B_change_stab=Button(self.User_buttons, textvariable=self.text_stab, command=self.change_stab)
        self.B_change_stab.grid(row=1,column=0, columnspan=2, sticky="ew")

        self.B_change_mask=Button(self.User_buttons, text=self.Messages["Portion4"], command=self.change_mask)
        self.B_change_mask.grid(row=2,column=0, columnspan=2, sticky="ew")

        self.B_change_back=Button(self.User_buttons, text=self.Messages["Portion5"], command=self.change_back)
        self.B_change_back.grid(row=3,column=0, columnspan=2, sticky="ew")

        self.B_change_params = Button(self.User_buttons, text=self.Messages["Portion6"], command=self.change_params)
        self.B_change_params.grid(row=4,column=0, columnspan=2, sticky="ew")

        self.B_redo_track = Button(self.User_buttons, text=self.Messages["Portion7"], command=self.redo_track)
        self.B_redo_track.grid(row=5,column=0, columnspan=2, sticky="ew")

        self.loading_lab = Label(self.User_buttons, text="", height=10)
        self.loading_lab.grid(row=6,column=0)
        self.loading_bar = Canvas(self.User_buttons, height=10)
        self.loading_bar.grid(row=6,column=0, columnspan=2)

        self.B_validate_track = Button(self.User_buttons, text=self.Messages["Portion8"], command=self.validate_correction)
        self.B_validate_track.grid(row=7, column=0, columnspan=2)

        self.load_coos()

        self.parent.protocol("WM_DELETE_WINDOW", self.leave)

    def leave(self):
        self.boss.PortionWin.grab_release()
        self.boss.PortionWin.destroy()
        self.destroy()
        self.Vid_Lecteur.proper_close()
        self.boss.Vid_Lecteur.bindings()

    def validate_correction(self):
        self.boss.PortionWin.grab_release()
        self.boss.PortionWin.destroy()
        self.destroy()
        self.Vid_Lecteur.proper_close()
        self.boss.Vid_Lecteur.bindings()
        self.boss.change_for_corrected()

    def change_stab(self):
        self.Vid.Stab=1-self.Vid.Stab
        if self.Vid.Stab:
            self.text_stab.set(self.Messages["Portion2"])
        else:
            self.text_stab.set(self.Messages["Portion3"])

    def change_mask(self):
        self.boss.PortionWin.grab_release()
        newWindow = Toplevel(self.parent.master)
        interface = Interface_masking.Mask(parent=newWindow, boss=self.boss, main_frame=self, proj_pos=0, Video_file=self.Vid, portion=True)

    def change_back(self):
        self.boss.PortionWin.grab_release()
        newWindow = Toplevel(self.parent.master)
        interface = Interface_back.Background(parent=newWindow, boss=self.boss, main_frame=self, Video_file=self.Vid, portion=True)

    def change_params(self):
        self.boss.PortionWin.grab_release()
        newWindow = Toplevel(self.parent.master)
        interface= Interface_parameters_track.Param_definer(parent=newWindow, boss=self.boss, main_frame=self, Video_file=self.Vid, portion=True)


    def load_coos(self):
        self.Coos={}
        self.NB_ind = sum(self.Vid.Track[1][6])
        file_name = os.path.basename(self.Vid.File_name)
        point_pos = file_name.rfind(".")
        path=self.Folder + "/TMP_portion/" +file_name[:point_pos]+"_TMP_portion_Coordinates.csv"
        for ind in range(self.NB_ind):
            with open(path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                Ind_Coos=[]
                for row in csv_reader:
                    Ind_Coos.append([row[1+(ind*2)],row[(2+(ind*2))]])
            self.Coos["Ind"+str(ind)]=Ind_Coos

        self.liste_colors=self.random_color(self.NB_ind)

        # Visualisation de la video et barre de temps
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=10)
        self.Vid_Lecteur.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.Scrollbar = self.Vid_Lecteur.Scrollbar

        # Visualisation de la video et barre de temps
        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW

        # We show the first frame:
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(int(self.Vid.Cropped[1][0]/self.Vid_Lecteur.one_every))
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()


    def pressed_can(self, Pt):
        pass

    def moved_can(self, Pt):
        pass

    def released_can(self, Pt):
        pass

    def redo_track(self):
        self.B_change_stab.config(state="disable")
        self.B_change_back.config(state="disable")
        self.B_change_mask.config(state="disable")
        self.B_change_params.config(state="disable")
        self.bouton_change_col.config(state="disable")
        self.B_redo_track.config(state="disable")
        self.B_validate_track.config(state="disable")

        Do_the_track3.Do_tracking(self, self.Vid, self.Folder , portion=True, prev_row=self.prev_row)
        self.load_coos()
        self.B_change_stab.config(state="active")
        self.B_change_back.config(state="active")
        self.B_change_mask.config(state="active")
        self.B_change_params.config(state="active")
        self.bouton_change_col.config(state="active")
        self.B_redo_track.config(state="active")
        self.B_validate_track.config(state="active")

    def change_color_pts(self):
        self.liste_colors=self.random_color(self.NB_ind)
        self.modif_image()

    def show_load(self):
        self.loading_lab.config(text=self.Messages["Loading"])
        self.loading_lab.update()
        self.loading_bar.delete('all')
        self.loading_bar.create_rectangle(0, 0, 200, self.loading_bar.cget("height"), fill="red")
        self.loading_bar.create_rectangle(0, 0, self.timer * 200, self.loading_bar.cget("height"), fill="blue")
        self.loading_bar.update()

    def validate_track(self):
        self.Vid.Track[0] = True
        self.Vid.Track[1][0] = self.Params.Can_1I_1A.thresh_value.get()
        self.Vid.Track[1][1] = self.Params.Can_1I_1A.erode_value.get()
        self.Vid.Track[1][2] = self.Params.Can_1I_1A.dilate_value.get()
        self.Vid.Track[1][3] = [self.Params.Can_1I_1A.min_area_value.get(),
                                         self.Params.Can_1I_1A.max_area_value.get()]
        self.Vid.Track[1][4] = [self.Params.Can_1I_1A.min_compact_value.get(),
                                         self.Params.Can_1I_1A.max_compact_value.get()]
        self.Vid.Track[1][5] = self.Params.Can_1I_1A.distance_max_value.get()
        self.Vid.Track[1][6] = self.Params.Can_1I_1A.liste_ind_per_ar
        self.ParamsW.destroy()
        self.boss.PortionWin.grab_set()
        self.Vid_Lecteur.proper_close()


    def modif_image(self, img=[], *args):
        if len(img)==0:
            new_img=np.copy(self.last_empty)
        else:
            self.last_empty = img
            new_img = np.copy(img)

        if self.Vid.Cropped[0]:
            to_remove = int(round((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every))
        else:
            to_remove=0

        if self.Vid.Stab:
            new_img = (Class_stabilise.find_best_position(Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=False))


        for ind in range(self.NB_ind):
            color=self.liste_colors[ind]
            for prev in range(min(int(self.tail_size*self.Vid.Frame_rate[1]), int(self.Scrollbar.active_pos - to_remove))):
                if int(self.Scrollbar.active_pos - prev) >= round(((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)) and int(self.Scrollbar.active_pos) <= round(((self.Vid.Cropped[1][1])/self.Vid_Lecteur.one_every)):
                    if self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][0] != "NA" and self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - prev - to_remove)][0] != "NA" :
                        TMP_tail_1 = (int(self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][0]),
                                      int(self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][1]))

                        TMP_tail_2 = (int(self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - prev - to_remove)][0]),
                                      int(self.Coos["Ind"+str(ind)][int(self.Scrollbar.active_pos - prev - to_remove)][1]))

                        new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, 2)

            if self.Scrollbar.active_pos >= round(((self.Vid.Cropped[1][0]-1)/self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= int(((self.Vid.Cropped[1][1]-1)/self.Vid_Lecteur.one_every)+1):
                center=self.Coos["Ind"+str(ind)][self.Scrollbar.active_pos - to_remove]
                if center[0]!="NA":
                    new_img=cv2.circle(new_img,(int(center[0]),int(center[1])),radius=5,color=color,thickness=-1)
                    if self.CheckVar.get()==int(ind):
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=7, color=(255,255,255),thickness=3)
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=7, color=(0,0,0), thickness=2)

        new_img = cv2.putText(new_img, self.Vid.Name, (10, self.Vid.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 2,
                          (255, 255, 255), 5)
        new_img = cv2.putText(new_img, self.Vid.Name, (10, self.Vid.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 2,
                          (0, 0, 0), 3)

        self.Vid_Lecteur.afficher_img(new_img)

    def random_color(self, ite=1):
        cols=[]
        for replicate in range(ite):
            levels = range(32, 256, 32)
            levels = str(tuple(random.choice(levels) for _ in range(3)))
            cols.append(tuple(int(s) for s in levels.strip("()").split(",")))
        return (cols)

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
