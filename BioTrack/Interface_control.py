from tkinter import *
import PIL.Image, PIL.ImageTk
import time
from BioTrack import UserMessages, Class_Scroll_crop
import cv2
import csv
import numpy as np
import random

class Check_track(Frame):
    def __init__(self, parent, main_frame, vid, liste_of_videos, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.grid(sticky="nsew")
        self.Vid=vid
        self.main_frame=main_frame
        self.liste_of_videos=liste_of_videos

        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()

        self.tail_length=IntVar()
        self.tail_length.set(5)
        self.NA_found=False


        self.Messages = UserMessages.Mess[self.Language.get()]

        self.capture = cv2.VideoCapture(self.Vid.File_name)
        if self.Vid.Cropped[0]:
            self.capture.set(1, self.Vid.Cropped[1][0])
            self.Video_length =int((self.Vid.Cropped[1][1]-self.Vid.Cropped[1][0])/self.Vid.Frame_rate)
        else:
            self.Video_length=int(self.Vid.Frame_nb/self.Vid.Frame_rate)
        self.ret, self.TMP_image_to_show = self.capture.read()

        self.fr_rate = self.Vid.Frame_rate
        self.playing = False




        # Visualisation de la video et barre de temps
        self.canvas_video = Canvas(self, height=800, width=1000, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_video.grid(row=0, column=0)
        self.bind_all("<Right>", self.move1)
        self.bind_all("<Left>", self.back1)
        self.bind_all("<space>", self.playbacks)

        self.Scrollbar = Class_Scroll_crop.Pers_Scroll(parent=self, container=self, height=100, width=800, bd=2,
                                                       highlightthickness=1, relief='ridge')
        self.Scrollbar.grid(row=2, column=0, sticky="we")

        self.canvas_buttons = Canvas(self, bd=2, highlightthickness=1)
        self.canvas_buttons.grid(row=3, column=0)

        self.canvas_options = Frame(self, bd=2, highlightthickness=1, width=50)
        self.canvas_options.grid(row=0, column=1, sticky="nsew")


        self.message_user=Label(self.canvas_options, text=self.Messages["Control0"], width=35, wraplengt=200, borderwidth=2, justify=LEFT)
        self.message_user.grid(row=0,column=0,sticky="nsew")



        self.bouton_change_col=Button(self.canvas_options, text=self.Messages["Control1"], command=self.change_colors)
        self.bouton_change_col.grid(row=1,sticky="nsew")

        self.Tail_length_scroll = Scale(self.canvas_options, from_=0, to=self.Video_length, label="Tail length (sec)", variable=self.tail_length,
                                   length=50, command=self.modif_image, orient=HORIZONTAL)
        self.Tail_length_scroll.grid(row=3,sticky="nsew")

        self.Label_fill_NA=Label(self.canvas_options, text=self.Messages["Control2"])
        self.Label_fill_NA.grid(row=5,sticky="sw")
        self.scale_fill_NA = Scale(self.canvas_options, length=100, from_=0, to=1,orient=HORIZONTAL, command=self.fill_NA, troughcolor="red")
        self.scale_fill_NA.grid(row=6,sticky="nsw")
        # self.user_message.set(self.Messages["Track0"])

        self.canvas_options.rowconfigure(2,weight=1)
        self.canvas_options.rowconfigure(4, weight=1)


        self.bouton_Validate_check = Button(self.canvas_options, text=self.Messages["Control3"], command=self.validate_corrections)
        self.bouton_Validate_check.grid(sticky="sew")
        # self.user_message.set(self.Messages["Track0"])

        # Widgets:
        self.bouton_Play = Button(self.canvas_buttons, text=self.Messages["PlayB1"], command=self.play)
        self.bouton_Play.grid(row=4, column=0, sticky="we")
        self.bouton_Stop = Button(self.canvas_buttons, text=self.Messages["PlayB2"], command=self.stop)
        self.bouton_Stop.grid(row=4, column=1, sticky="we")
        self.bouton_GTBeg = Button(self.canvas_buttons, text=self.Messages["PlayB3"], command=self.GotoBeg)
        self.bouton_GTBeg.grid(row=4, column=2, sticky="we")
        self.bouton_GTEnd = Button(self.canvas_buttons, text=self.Messages["PlayB4"], command=self.GotoEnd)
        self.bouton_GTEnd.grid(row=4, column=3, sticky="we")

        #Importation des coos:
        self.list_coos = []
        with open(self.Vid.File_name + "_Coordinates.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                self.list_coos.append(row)

        self.NB_tracked=int((len(self.list_coos[0])-1)/2)

        self.liste_of_cols=self.random_color(self.NB_tracked)
        self.modif_image()

    def validate_corrections(self):
        with open(self.Vid.File_name + "_Coordinates.csv", 'w', newline='') as file:
            writer = csv.writer(file, delimiter=";")
            for row in self.list_coos:
                writer.writerow(row)
        self.main_frame.return_main()

    def fill_NA(self, value):
        if not self.NA_found:
            self.Blancs=self.find_NA()

        if int(value)==1:
            for ind_blc in range(len(self.Blancs)):
                for hole in self.Blancs[ind_blc]:
                    Deb=hole[0]
                    Fin=hole[1]
                    if Deb>0:
                        Prem_X=int(self.list_coos[Deb-1][1+ind_blc*2])
                        Prem_Y=int(self.list_coos[Deb-1][2+ind_blc*2])
                    else:
                        Prem_X=int(self.list_coos[Fin][1+ind_blc*2])
                        Prem_Y=int(self.list_coos[Fin][2+ind_blc*2])

                    if Fin<(len(self.list_coos)-1):
                        Last_X = int(self.list_coos[Fin][1 + ind_blc * 2])
                        Last_Y = int(self.list_coos[Fin][2 + ind_blc * 2])
                    else:
                        Last_X = int(self.list_coos[Deb - 1][1 + ind_blc * 2])
                        Last_Y = int(self.list_coos[Deb - 1][2 + ind_blc * 2])


                    for row in range(len(self.list_coos[Deb:(Fin+1)])):
                        self.list_coos[row+Deb][1+ind_blc*2]= int(Prem_X - (((row+1)*(Last_X-Prem_X))/(Deb-Fin)))
                        self.list_coos[row+Deb][2 + ind_blc * 2] = int(Prem_Y - (((row + 1) * (Last_Y - Prem_Y)) / (Deb - Fin)))


        elif int(value)==0:
            for ind_blc in range(len(self.Blancs)):
                for hole in self.Blancs[ind_blc]:
                    Deb=hole[0]
                    Fin=hole[1]
                    for row in range(len(self.list_coos[Deb:(Fin+1)])):
                        self.list_coos[row+Deb][1+ind_blc*2]= "NA"
                        self.list_coos[row+Deb][2 + ind_blc * 2] = "NA"

        self.modif_image()




    def find_NA(self):
        Blancs=list()
        pdt_blanc=False
        for ind in range(self.NB_tracked):
            Blancs.append([])
            for raw in range(len(self.list_coos)):
                if self.list_coos[raw][(1 + ind * 2)] == "NA":
                    if pdt_blanc == False:
                        Deb = raw
                        pdt_blanc = True
                else:
                    if pdt_blanc:
                        Blancs[ind].append((Deb, raw))
                        pdt_blanc = False
                if raw == (len(self.list_coos) - 1) and pdt_blanc:
                    Blancs[ind].append((int(Deb), int(raw)))
                    pdt_blanc = False
        self.NA_found = True
        return(Blancs)


    def change_colors(self):
        self.liste_of_cols=self.random_color(self.NB_tracked)
        self.modif_image()

    def update_image(self,frame):
        self.capture.set(1, int(frame))
        self.ret, self.TMP_image_to_show = self.capture.read()
        self.modif_image()


    def modif_image(self, *arg):
        self.TMP2_image_to_show = cv2.cvtColor(self.TMP_image_to_show, cv2.COLOR_BGR2RGB)
        if self.Scrollbar.active_pos<self.Scrollbar.crop_beg or self.Scrollbar.active_pos>self.Scrollbar.crop_end:
            self.TMP2_image_to_show= cv2.add(self.TMP2_image_to_show,np.array([-75.0]))

        else:
            coos=self.list_coos[self.Scrollbar.active_pos-self.Vid.Cropped[1][0]]
            for ind in range(self.NB_tracked):
                X=coos[ind*2+1]
                Y=coos[ind*2+2]
                if X != "NA" and Y != "NA":
                    self.TMP2_image_to_show=cv2.circle(self.TMP2_image_to_show,(int(X),int(Y)),13-ind*2,self.liste_of_cols[ind],-1)

                    for fr in range(int(self.tail_length.get()*self.Vid.Frame_rate)):
                        if (self.Scrollbar.active_pos - fr)>self.Scrollbar.crop_beg:
                            coos_av = ((self.list_coos[self.Scrollbar.active_pos - self.Vid.Cropped[1][0]- (fr+1)][ind*2+1]),(self.list_coos[self.Scrollbar.active_pos - self.Vid.Cropped[1][0]- (fr+1)][(ind*2+2)]))
                            coos_ap = ((self.list_coos[self.Scrollbar.active_pos - self.Vid.Cropped[1][0]- (fr+1)+1][ind*2+1]),(self.list_coos[self.Scrollbar.active_pos - self.Vid.Cropped[1][0]-(fr+1)+1][ind*2+2]))
                            if coos_av[0]!="NA" and coos_ap[0]!="NA":
                                self.TMP2_image_to_show=cv2.line(self.TMP2_image_to_show,(int(coos_av[0]),int(coos_av[1])),(int(coos_ap[0]),int(coos_ap[1])),self.liste_of_cols[ind],3)



        self.TMP2_image_to_show=cv2.resize(self.TMP2_image_to_show,(int(self.TMP2_image_to_show.shape[1]/2),int(self.TMP2_image_to_show.shape[0]/2)))
        self.shape= self.TMP2_image_to_show.shape

        self.afficher()

    def afficher(self):
        self.image_to_show2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP2_image_to_show))

        self.can_import = self.canvas_video.create_image(0, 0, image=self.image_to_show2, anchor=NW)
        self.canvas_video.config(height=self.shape[0],width=self.shape[1])
        self.canvas_video.itemconfig(self.can_import, image=self.image_to_show2)
        self.update()

    def GotoBeg(self):
        if self.Vid.Cropped[0]:
            self.capture.set(1, self.Vid.Cropped[1][0])
            self.Scrollbar.active_pos = self.Vid.Cropped[1][0]
        else:
            self.capture.set(1,0)
            self.Scrollbar.active_pos = 0

        self.ret, self.TMP_image_to_show = self.capture.read()
        self.Scrollbar.refresh()
        self.modif_image()

    def GotoEnd(self):
        if self.Vid.Cropped[0]:
            self.capture.set(1, self.Vid.Cropped[1][1])
            self.Scrollbar.active_pos = self.Vid.Cropped[1][1]
        else:
            self.capture.set(1,self.Vid.Frame_nb-1)
            self.Scrollbar.active_pos = self.Vid.Frame_nb
        self.ret, self.TMP_image_to_show = self.capture.read()
        self.Scrollbar.refresh()
        self.modif_image()


    def playbacks(self, *arg):
        if self.playing:
            self.stop()
        else:
            self.play()

    def back1(self, *arg):
        if self.Scrollbar.active_pos>0:
            self.Scrollbar.active_pos=self.Scrollbar.active_pos-1
            self.Scrollbar.refresh()
            self.capture.set(1, self.Scrollbar.active_pos)
            self.ret, self.TMP_image_to_show = self.capture.read()
            self.modif_image()

    def move1(self, *arg):
        if self.Scrollbar.active_pos<(self.Vid.Frame_nb-2):
            self.ret=True
        if self.ret:
            self.Scrollbar.active_pos+=1
            self.Scrollbar.refresh()
            self.ret, self.TMP_image_to_show = self.capture.read()
            if self.ret:
                self.modif_image()

    def play(self):
        if self.Scrollbar.active_pos<(self.Vid.Frame_nb-2):
            self.ret=True
            self.playing=True
        while self.ret:
            time.sleep(1 / (self.fr_rate*2))
            self.Scrollbar.active_pos+=1
            self.Scrollbar.refresh()
            self.ret, self.TMP_image_to_show = self.capture.read()
            if self.ret:
                self.modif_image()

    def stop(self):
        self.ret=False
        self.playing = False

    def random_color(self, ite=1):
        cols=[]
        for replicate in range(ite):
            levels = range(32, 256, 32)
            levels = str(tuple(random.choice(levels) for _ in range(3)))
            cols.append(tuple(int(s) for s in levels.strip("()").split(",")))
        return (cols)

