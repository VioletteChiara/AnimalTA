from tkinter import *
from BioTrack import  UserMessages, Class_Lecteur, Class_stabilise
import numpy as np
import os
import csv
import cv2
import random
import math
from scipy.signal import savgol_filter
import PIL
from tkinter import filedialog
import decord

class Lecteur(Frame):
    def __init__(self, parent, boss, main_frame, Vid, Video_liste, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.main_frame=main_frame
        self.boss=boss
        self.Video_liste=Video_liste
        self.Vid=Vid
        self.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.Pos = []
        self.timer=0
        self.cache=False

        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        self.Messages = UserMessages.Mess[self.Language.get()]
        f.close()

        Right_Frame=Frame(self)
        Right_Frame.grid(row=0, column=1)

        self.CheckVar=IntVar(value=0)

        Only_cropped=Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=0, text=self.Messages["Save_Vid1"], command=self.change_type)
        Only_cropped.grid(row=0, sticky="w")

        if self.Vid.Stab:
            Stab=Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=1, text=self.Messages["Save_Vid2"], command=self.change_type)
            Stab.grid(row=1, sticky="w")

        if self.Vid.Tracked:
            With_track=Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=2, text=self.Messages["Save_Vid3"], command=self.change_type)
            With_track.grid(row=2, sticky="w")

            self.load_coos()

            if self.Vid.Smoothed[0]>0:
                self.smooth_coos()
                With_track_smooth = Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=3, text=self.Messages["Save_Vid4"], command=self.change_type)
                With_track_smooth.grid(row=3, sticky="w")

            self.tail_size = IntVar(value=10)
            self.max_tail = IntVar()
            self.max_tail.set(min([self.Vid.Frame_nb[1], 600]))
            self.Scale_tail = Scale(Right_Frame, from_=0, to=self.max_tail.get(), variable=self.tail_size, orient="horizontal", label=self.Messages["Control4"], command=self.modif_image)
            self.Selected_pt = 0
            self.canvs_col = Canvas(Right_Frame, width=35, height=25, background="#%02x%02x%02x" % self.liste_colors[0])


        self.Save_Vid_Button=Button(Right_Frame, text=self.Messages["GButton18"], command=self.save_vid, background="green")
        self.Save_Vid_Button.grid(row=6)

        self.Save_Return_Button=Button(Right_Frame, text=self.Messages["GButton11"], command=self.End_of_window, background="red")
        self.Save_Return_Button.grid(row=10)


        self.Vid_Lecteur=Class_Lecteur.Lecteur(self, self.Vid)
        self.Vid_Lecteur.grid(row=0, column=0, sticky="nsew")
        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        if self.Vid.Cropped[0]:
            self.to_sub = round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every))
        else:
            self.to_sub = 0


        self.loading_canvas=Frame(Right_Frame)
        self.loading_canvas.grid(row=7)
        self.loading_state=Label(self.loading_canvas, text="")
        self.loading_state.grid(row=0, column=0)

        self.loading_bar=Canvas(self.loading_canvas, height=10)
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill="red")
        self.loading_bar.grid(row=0, column=1)

        self.bouton_hide = Button(Right_Frame, text=self.Messages["Do_track1"], command=self.hide)


    def hide(self):
        self.cache = True
        self.boss.update_idletasks()
        self.boss.overrideredirect(False)
        self.boss.state('iconic')

    def show_load(self):
        self.loading_bar.delete('all')
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill="red")
        self.loading_bar.create_rectangle(0, 0, self.timer*400, self.loading_bar.cget("height"), fill="blue")
        self.loading_bar.update()

    def change_color(self, event):
        color_choice = Toplevel()
        Canvas_colors(parent=color_choice, boss=self, ind=self.Selected_pt)

    def pressed_can(self, Pt):
        if self.Vid.Tracked:
            if int(self.Scrollbar.active_pos) >= round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every)) and int(
                    self.Scrollbar.active_pos) <= round(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every)):
                for col in range(self.NB_ind):
                    center = self.Coos["Ind" + str(col)][self.Scrollbar.active_pos - self.to_sub]
                    dist_clic = math.sqrt((int(center[0]) - Pt[0]) ** 2 + (int(center[1]) - Pt[1]) ** 2)
                    if dist_clic < 10:
                        self.Selected_pt=col
                        self.modif_image()
                        self.canvs_col.config(background="#%02x%02x%02x" % self.liste_colors[self.Selected_pt])
                        break


    def save_vid(self):
        file_to_save = filedialog.asksaveasfilename(defaultextension=".avi", initialfile="Untitled_video.avi", filetypes=(("Video", "*.avi"),))

        if len(file_to_save)>0:
            self.bouton_hide.grid(row=8)
            cap = cv2.VideoCapture(self.Vid.File_name)
            frame_width = int(cap.get(3))
            frame_height = int(cap.get(4))
            frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
            size = (frame_width, frame_height)
            self.bouton_hide.grab_set()

            cap = decord.VideoReader(self.Vid.File_name)

            if self.Vid.Cropped[0]:
                start = self.Vid.Cropped[1][0]
                end = self.Vid.Cropped[1][1]
                self.Scrollbar.active_pos = int(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every) - 1

                Which_part = 0
                if self.Vid.Cropped[0]:
                    if len(self.Vid.Fusion) > 1:  # Si on a plus d'une video
                        Which_part = [index for index, Fu_inf in enumerate(self.Vid.Fusion) if Fu_inf[0] <= start][-1]
                        if Which_part != 0:  # si on est pas dans la première partie de la vidéo
                            cap = cv2.VideoReader(self.Vid.Fusion[Which_part][1])
            else:
                start = 0
                end = self.Vid.Frame_nb[1] - 1


            result = cv2.VideoWriter(file_to_save, cv2.VideoWriter_fourcc(*'XVID'), frame_rate, size)
            for frame in range(start, end + self.Vid_Lecteur.one_every, self.Vid_Lecteur.one_every):
                self.timer = (frame - start) / (end - start - 1)
                self.show_load()
                self.Scrollbar.active_pos += 1

                if len(self.Vid.Fusion) > 1 and Which_part < (len(self.Vid.Fusion) - 1) and frame >= (self.Vid.Fusion[Which_part + 1][0]):
                    Which_part += 1
                    cap = decord.VideoReader(self.Vid.Fusion[Which_part][1], ctx=decord.cpu(0))

                img = cap[frame - self.Vid.Fusion[Which_part][0]].asnumpy()

                new_img=self.modif_image(img, aff=False)
                new_img=cv2.cvtColor(new_img,cv2.COLOR_BGR2RGB)
                result.write(new_img)


            self.End_of_window()
            self.loading_bar.grab_release()
            if self.cache:
                self.boss.update_idletasks()
                self.boss.state('normal')
                self.boss.overrideredirect(True)
            result.release()




    def End_of_window(self):
        self.unbind_all("<Button-1>")
        self.Vid_Lecteur.proper_close()
        self.grab_release()
        self.main_frame.return_main()


    def moved_can(self, Pt):
        pass

    def released_can(self, Pt):
        pass

    def modif_image(self, img=[], aff=True):
        if len(img) <= 10:
            new_img=np.copy(self.last_empty)
        else:
            self.last_empty = img
            new_img = np.copy(img)
        if self.CheckVar.get()>0 and self.Vid.Stab:
            new_img = Class_stabilise.find_best_position(Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=False)
        if self.CheckVar.get()>1:
            if self.Vid.Cropped[0]:
                to_remove = int(round((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every))
            else:
                to_remove = 0

            if self.Vid.Stab:
                new_img = Class_stabilise.find_best_position(Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img,
                                                             show=False)

            for ind in range(self.NB_ind):
                color = self.liste_colors[ind]
                for prev in range(min(int(self.tail_size.get() * self.Vid.Frame_rate[1]), int(self.Scrollbar.active_pos - to_remove))):
                    if int(self.Scrollbar.active_pos - prev) > round(((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every)) and int(self.Scrollbar.active_pos) <= round(((self.Vid.Cropped[1][1]) / self.Vid_Lecteur.one_every)):
                        if self.Coos["Ind" + str(ind)][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][
                            0] != "NA" and \
                                self.Coos["Ind" + str(ind)][int(self.Scrollbar.active_pos - prev - to_remove)][
                                    0] != "NA":
                            TMP_tail_1 = (int(
                                self.Coos["Ind" + str(ind)][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][
                                    0]),
                                          int(self.Coos["Ind" + str(ind)][
                                                  int(self.Scrollbar.active_pos - 1 - prev - to_remove)][1]))

                            TMP_tail_2 = (
                            int(self.Coos["Ind" + str(ind)][int(self.Scrollbar.active_pos - prev - to_remove)][0]),
                            int(self.Coos["Ind" + str(ind)][int(self.Scrollbar.active_pos - prev - to_remove)][1]))
                            new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, 2)

                if self.Scrollbar.active_pos > round(((self.Vid.Cropped[1][0] - 1) / self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= int(((self.Vid.Cropped[1][1] - 1) / self.Vid_Lecteur.one_every) + 1):
                    center = self.Coos["Ind" + str(ind)][self.Scrollbar.active_pos - to_remove]
                    if center[0] != "NA":
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=5, color=color,
                                             thickness=-1)
                        if self.Selected_pt == int(ind) and aff:
                            new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=7,
                                                 color=(255, 255, 255), thickness=3)
                            new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=7, color=(0, 0, 0),
                                                 thickness=2)
        if aff:
            self.Vid_Lecteur.afficher_img(new_img)
        else:
            return(new_img)


    def change_type(self):
        if self.CheckVar.get() > 1:
            self.Scale_tail.grid(row=4)
            self.canvs_col.grid(row=5)
            self.canvs_col.bind("<Button-1>", self.change_color)
        elif self.Vid.Tracked:
            self.Scale_tail.grid_forget()
            self.canvs_col.grid_forget()

        if self.CheckVar.get()==2:
            self.Coos=self.Coos_brutes
        elif self.CheckVar.get()==3:
            self.Coos=self.Coos_smoothed
        self.modif_image()


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
        self.Coos=self.Coos_brutes


    def smooth_coos(self):
        self.Coos_smoothed=self.Coos.copy()
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
                        if len(ind_coo[(debuts[seq] + 1):fins[seq], column]) >= self.Vid.Smoothed[0]:
                            ind_coo[(debuts[seq] + 1):fins[seq], column] = savgol_filter(
                                ind_coo[(debuts[seq] + 1):fins[seq], column], self.Vid.Smoothed[0],
                                self.Vid.Smoothed[1], deriv=0, delta=1.0, axis=- 1,
                                mode='interp', cval=0.0)


                else:
                    ind_coo[:, column] = savgol_filter(ind_coo[:, column],
                                                                       self.Vid.Smoothed[0],
                                                                       self.Vid.Smoothed[1], deriv=0, delta=1.0, axis=- 1,
                                                                       mode='interp', cval=0.0)
            ind_coo=ind_coo.astype(np.float)
            ind_coo=ind_coo.tolist()
            ind_coo=[["NA" if np.isnan(val) else val for val in row] for row in ind_coo]
            self.Coos_smoothed[ind]=ind_coo



    def random_color(self, ite=1):
        cols=[]
        for replicate in range(ite):
            levels = range(32, 256, 32)
            levels = str(tuple(random.choice(levels) for _ in range(3)))
            cols.append(tuple(int(s) for s in levels.strip("()").split(",")))
        return (cols)


class Canvas_colors(Canvas):
    def __init__(self, parent, ind, boss, **kwargs):
        Canvas.__init__(self, parent, bd=5, **kwargs)
        self.ind=ind
        self.boss=boss
        self.parent=parent
        self.parent.attributes('-toolwindow', True)

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


        self.bgr=cv2.resize(bgr,(int(bgr.shape[0]/2),int(bgr.shape[1])))

        self.bgr2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.bgr))

        self.can_import = self.create_image(0,0, image=self.bgr2, anchor=NW)
        self.config(height=self.bgr.shape[0],width=self.bgr.shape[1])
        self.itemconfig(self.can_import, image=self.bgr2)
        self.update_idletasks()
        parent.update_idletasks()
        self.bind("<Button-1>", self.send)
        self.grid(sticky="nsew")

        self.stay_on_top()

    def send(self, event):
        if event.y<self.bgr.shape[0] and event.x<self.bgr.shape[1]:
            self.boss.liste_colors[self.ind]=tuple([int(BGR) for BGR in self.bgr[event.y,event.x]])
            self.boss.modif_image()
            self.boss.canvs_col.config(background="#%02x%02x%02x" % self.boss.liste_colors[self.ind])
            self.unbind("<Button-1>")
            self.parent.destroy()

    def stay_on_top(self):
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)
