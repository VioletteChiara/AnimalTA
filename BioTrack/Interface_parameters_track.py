import cv2
from tkinter import *
import PIL.Image, PIL.ImageTk
import time
import numpy as np
from BioTrack import Interface_nb_per_Ar, UserMessages, Class_stabilise, Class_Lecteur, Function_draw_mask as Dr
from functools import partial

class Param_definer(Frame):
    def __init__(self, parent, boss, main_frame, Video_file, portion=False, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.main_frame=main_frame
        self.boss=boss
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.Vid = Video_file
        self.portion = portion

        if self.portion:
            Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
            Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW
            self.parent.geometry("1200x750")


        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]
        self.default_message=self.Messages["Track0"]
        self.user_message=StringVar()
        self.user_message.set(self.default_message)

        self.fr_rate=self.Vid.Frame_rate[1]
        self.one_every=int(round(round(self.Vid.Frame_rate[0],2)/self.Vid.Frame_rate[1]))
        self.playing=False
        self.thresh_value = StringVar()
        self.thresh_value.set(self.Vid.Track[1][0])
        self.erode_value = StringVar()
        self.erode_value.set(self.Vid.Track[1][1])
        self.dilate_value = StringVar()
        self.dilate_value.set(self.Vid.Track[1][2])
        self.kernel = np.ones((3, 3), np.uint8)
        self.Scroll_L = 75
        self.min_area_value=StringVar()
        self.max_area_value=StringVar()
        self.min_compact_value=StringVar()
        self.max_compact_value=StringVar()
        self.distance_max_value=StringVar()
        self.units = StringVar()
        width_labels=12

        self.mask = Dr.draw_mask(self.Vid)

        self.Arenas, _ = cv2.findContours(self.mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.Arenas = Dr.Organise_Ars(self.Arenas)

        if self.Vid.Scale[0]==0:
            self.distance_maximum=(max([self.Vid.shape[0],self.Vid.shape[1]])/2)
            self.max_area=float(self.distance_maximum/2)
            self.units.set("px")
        else:
            self.distance_maximum = (max([self.Vid.shape[0],self.Vid.shape[1]]) / 2)/float(self.Vid.Scale[0])
            self.max_area=round(self.distance_maximum/2)


        # Nom de la video et changer de video:
        if not self.portion:
            self.canvas_video_name = Canvas(self, bd=2, highlightthickness=1, relief='flat')
            self.canvas_video_name.grid(row=0, column=0, sticky="nsew")

            self.dict_Names = { self.main_frame.list_projects[i].Video.Name : self.main_frame.list_projects[i] for i in range(0, len(self.main_frame.list_projects) )}

            self.liste_videos_name = [V.Name for V in self.main_frame.liste_of_videos]
            holder = StringVar()
            holder.set(self.Vid.Name)
            self.bouton_change_vid = OptionMenu(self.canvas_video_name, holder, *self.dict_Names.keys(),
                                             command=self.change_vid)
            self.bouton_change_vid.config(font=("Arial",15))

            self.bouton_change_vid.grid(row=0, column=0, sticky="we")

        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=100)  ########NEW

        #Options
        self.canvas_options=Canvas(self.parent, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_options.grid(row=1, column=1, sticky="sew")
        Grid.columnconfigure(self.canvas_options, 0, weight=1)  ########NEW
        self.canvas_options.columnconfigure(0,minsize=400)


        self.CheckVar = IntVar()
        F_Ori=Frame(self.canvas_options, background="white")
        F_Ori.grid(sticky="nsew", columnspan=3)
        Original_vis = Checkbutton(F_Ori, text=self.Messages["Track2"], variable=self.CheckVar,
                                        onvalue=0, offvalue=0, width=width_labels, command=self.modif_image, anchor="w", background="white")
        Original_vis.bind("<Enter>", partial(self.change_msg, self.Messages["Param1"]))
        Original_vis.bind("<Leave>", self.remove_msg)
        Original_vis.grid(sticky="w")

        F_Sub=Frame(self.canvas_options, background="grey80")
        F_Sub.grid(sticky="nsew")
        Subtract_vis = Checkbutton(F_Sub, text=self.Messages["Names7"], variable=self.CheckVar,
                                        onvalue=1, offvalue=0, width=width_labels, command=self.modif_image, anchor="w", background="grey80")
        Subtract_vis.bind("<Enter>", partial(self.change_msg, self.Messages["Param2"]))
        Subtract_vis.bind("<Leave>", self.remove_msg)
        Subtract_vis.grid(sticky="w")

        F_Thresh=Frame(self.canvas_options, background="white")
        F_Thresh.grid(sticky="nsew")

        Threshol_vis = Checkbutton(F_Thresh, text=self.Messages["Names1"], variable=self.CheckVar, onvalue=2, offvalue=0, width=width_labels, command=self.modif_image, anchor="w", background="white")
        Threshol_vis.bind("<Enter>", partial(self.change_msg, self.Messages["Param3"]))
        Threshol_vis.bind("<Leave>", self.remove_msg)
        Threshol_vis.grid(sticky="w")

        Thresh_scroll = Scale(F_Thresh, from_=0, to=255, variable=self.thresh_value, orient=HORIZONTAL, background="white",highlightbackground="white")
        Thresh_scroll.grid(row=0,column=1, sticky="NSEW")

        verif_E_tresh = (self.register(self.verif_E_tresh_fun), '%P', '%V')
        Thresh_entry=Entry(F_Thresh,textvariable=self.thresh_value, width=10, validate="key", validatecommand=verif_E_tresh)
        Thresh_entry.grid(row=0,column=2, sticky="se")

        F_Thresh.grid_columnconfigure(0, weight=1)
        F_Thresh.grid_columnconfigure(1, weight=6)
        F_Thresh.grid_columnconfigure(2, weight=1)

        F_Ero=Frame(self.canvas_options, background="grey80")
        F_Ero.grid(sticky="nsew")

        Erode_vis = Checkbutton(F_Ero, text=self.Messages["Names2"], variable=self.CheckVar,
                                     onvalue=3, offvalue=0, width=width_labels, command=self.modif_image, anchor="w", background="grey80")
        Erode_vis.bind("<Enter>", partial(self.change_msg, self.Messages["Param4"]))
        Erode_vis.bind("<Leave>", self.remove_msg)
        Erode_vis.grid(sticky="w")
        Erode_scroll = Scale(F_Ero, from_=0, to=50, variable=self.erode_value, orient=HORIZONTAL, background="grey80",highlightbackground="grey80")
        Erode_scroll.grid(row=0, column=1, sticky="ew")

        Erode_entry=Entry(F_Ero,textvariable=self.erode_value, width=10, validate="key", validatecommand=verif_E_tresh, background="grey80")
        Erode_entry.grid(row=0,column=2, sticky="se")

        self.erode_value.trace("w", lambda name, index, mode, erode_value=self.erode_value, type=2: self.changed_val(self.erode_value.get(), type=3))


        F_Ero.grid_columnconfigure(0, weight=1)
        F_Ero.grid_columnconfigure(1, weight=6)
        F_Ero.grid_columnconfigure(2, weight=1)

        F_Dil=Frame(self.canvas_options, background="white")
        F_Dil.grid(sticky="nsew")
        F_Dil.grid_columnconfigure(0, weight=1)
        F_Dil.grid_columnconfigure(1, weight=6)
        F_Dil.grid_columnconfigure(2, weight=1)
        Dilate_vis = Checkbutton(F_Dil, text=self.Messages["Names3"], variable=self.CheckVar,
                                      onvalue=4, offvalue=0, width=width_labels, command=self.modif_image, anchor="w", background="white")
        Dilate_vis.bind("<Enter>", partial(self.change_msg, self.Messages["Param5"]))
        Dilate_vis.bind("<Leave>", self.remove_msg)
        Dilate_vis.grid(sticky="w")
        Dilate_scroll = Scale(F_Dil, from_=0, to=50, variable=self.dilate_value, orient=HORIZONTAL, background="white", highlightbackground="white")
        Dilate_scroll.grid(row=0, column=1, sticky="we")

        Dilate_entry=Entry(F_Dil,textvariable=self.dilate_value, width=10, validate="key", validatecommand=verif_E_tresh, background="white")
        Dilate_entry.grid(row=0,column=2, sticky="se")

        self.dilate_value.trace("w", lambda name, index, mode, dilate_value=self.dilate_value, type=2: self.changed_val(self.dilate_value.get(), type=4))


        verif_E_float = (self.register(self.verif_E_float_fun), '%P', '%V')

        F_Area=Frame(self.canvas_options, background="grey80")
        F_Area.grid(sticky="nsew")
        F_Area.grid_columnconfigure(0, weight=1)
        F_Area.grid_columnconfigure(1, weight=1)
        F_Area.grid_columnconfigure(2, weight=9)
        F_Area.grid_columnconfigure(3, weight=1)

        Min_area_vis = Checkbutton(F_Area, text=self.Messages["Names4"], variable=self.CheckVar,
                                        onvalue=5, offvalue=0, width=width_labels, command=self.modif_image, anchor="w", background="grey80")
        Min_area_vis.bind("<Enter>", partial(self.change_msg, self.Messages["Param6"]))
        Min_area_vis.bind("<Leave>", self.remove_msg)
        Min_area_vis.grid(rowspan=2, sticky="w")
        Min_lab=Label(F_Area, text="min:", background="grey80")
        Min_lab.grid(row=0, column=1, sticky="e")
        Min_area_scroll = Scale(F_Area, from_=0.001, to=self.max_area, resolution=0.05, length=self.Scroll_L, variable=self.min_area_value, orient=HORIZONTAL, background="grey80", highlightbackground="grey80")
        Min_area_scroll.grid(row=0, column=2, sticky="ew")

        Min_area_entry=Entry(F_Area,textvariable=self.min_area_value, width=10, validate="key", validatecommand=verif_E_float, background="grey80")
        Min_area_entry.grid(row=0,column=4, sticky="se")

        Max_lab=Label(F_Area, text="max:", background="grey80")
        Max_lab.grid(row=1, column=1, sticky="e")
        Max_area_scroll = Scale(F_Area, from_=0.0, to=self.max_area, resolution=0.05, length=self.Scroll_L,
                                variable=self.max_area_value, orient=HORIZONTAL, background="grey80",
                                highlightbackground="grey80")
        Max_area_scroll.grid(row=1, column=2, sticky="ew")

        Max_area_entry=Entry(F_Area,textvariable=self.max_area_value, width=10, validate="all", validatecommand=verif_E_float, background="grey80")
        Max_area_entry.grid(row=1,column=4, sticky="se")

        Area_units = Label(F_Area, text=self.Vid.Scale[1] + "\u00b2",anchor="w", background="grey80")
        Area_units.grid(row=0, column=3, rowspan=2, sticky="we")

        F_Dist=Frame(self.canvas_options, background="white")
        F_Dist.grid(sticky="nsew")
        F_Dist.grid_columnconfigure(0, weight=1)
        F_Dist.grid_columnconfigure(1, weight=6)
        F_Dist.grid_columnconfigure(2, weight=1)
        Distance_traveled_vis = Checkbutton(F_Dist, text=self.Messages["Names6"],
                                                 variable=self.CheckVar, onvalue=7, offvalue=0, width=width_labels,
                                                 command=self.modif_image, anchor="w", background="white")
        Distance_traveled_vis.bind("<Enter>", partial(self.change_msg, self.Messages["Param7"]))
        Distance_traveled_vis.bind("<Leave>", self.remove_msg)
        Distance_traveled_vis.grid(row=0,column=0, sticky="w")

        Distance_traveled_scroll = Scale(F_Dist, from_=0.0, to=self.distance_maximum, resolution=0.05, length=self.Scroll_L, variable=self.distance_max_value, orient=HORIZONTAL, background="white", highlightbackground="white")
        Distance_traveled_scroll.grid(row=0, column=1, sticky="ew")

        self.Distance_entry=Entry(F_Dist, width=10, validate="all",  textvariable= self.distance_max_value, validatecommand=verif_E_float, background="white")
        self.Distance_entry.grid(row=0,column=3, sticky="se")

        Distance_traveled_units = Label(F_Dist, textvariable=self.units, anchor="w", background="white")
        Distance_traveled_units.grid(row=0, column=2, sticky="w")


        self.KindTVar = IntVar()
        if not self.portion:
            F_Nb=Frame(self.canvas_options, background="grey80")
            F_Nb.grid(sticky="nsew")
            F_Nb.grid_columnconfigure(0, weight=1)
            F_Nb.grid_columnconfigure(1, weight=5)
            F_Nb.grid_columnconfigure(2, weight=1)
            Lab_three_per_Ar = Label(F_Nb, text=self.Messages["Param9"], width=width_labels+3, wraplength=120, background="grey80")
            Lab_three_per_Ar.bind("<Enter>", partial(self.change_msg, self.Messages["Param8"]))
            Lab_three_per_Ar.bind("<Leave>", self.remove_msg)
            Lab_three_per_Ar.grid(row=0, column=0, sticky="w")

            Three_per_Ar = Scale(F_Nb, variable=self.KindTVar,
                                      from_=1, to=20, command=self.change_nb_ar_glob, orient=HORIZONTAL, background="grey80", highlightbackground="grey80")
            Three_per_Ar.grid(row=0, column=1, sticky="we")

            self.KindTVar.set(self.Vid.Track[1][6][0])
            param_nb_per_ar = Button(F_Nb, text="P", command=self.change_nb_ar)
            param_nb_per_ar.grid(row=0, column=2)
            param_nb_per_ar.bind("<Enter>", partial(self.change_msg, self.Messages["TrackB2"]))
            param_nb_per_ar.bind("<Leave>", self.remove_msg)


        if not len(self.Vid.Track[1][6]) == len(self.Arenas):
            self.Vid.Track[1][6] = [self.Vid.Track[1][6][0] for n in self.Arenas]
        self.liste_ind_per_ar = self.Vid.Track[1][6]

        if not len(self.Vid.Analyses[1]) == len(self.Arenas):
            self.Vid.Analyses[1] = [[] for n in self.Arenas]

        self.min_area_value.set(self.Vid.Track[1][3][0])
        self.max_area_value.set(self.Vid.Track[1][3][1])
        self.min_compact_value.set(self.Vid.Track[1][4][0])
        self.max_compact_value.set(self.Vid.Track[1][4][1])
        self.distance_max_value.set(self.Vid.Track[1][5])
        self.units.set(str(self.Vid.Scale[1]))

        self.B_Validate=Button(self.canvas_options, text=self.Messages["Validate"],bg="green", command=self.Validate)#######NEW
        self.B_Validate.grid(row=13,column=0, sticky="ews")#######NEW

        self.canvas_user = Frame(self.parent, width=150,  highlightthickness=4, relief='flat', highlightbackground="RoyalBlue3")
        self.canvas_user.grid(row=0, column=1, sticky="snew")
        Info_title=Label(self.canvas_user, text=self.Messages["Info"],  justify=CENTER, background="RoyalBlue3", fg="white", font=("Helvetica", 16, "bold"))
        Info_title.grid(row=0, sticky="nsew")
        Grid.columnconfigure(self.canvas_user, 0, weight=1)

        self.User_help=Label(self.canvas_user, textvariable=self.user_message, wraplengt=375, borderwidth=2, justify=LEFT)
        self.User_help.grid(sticky="nsew")

        # Visualisation de la video et barre de temps
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=10)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Vid_Lecteur.Scrollbar.refresh()

        self.CheckVar.set(0)
        self.thresh_value.trace("w", lambda name, index, mode, thresh_value=self.thresh_value, type=2: self.changed_val(self.thresh_value.get(), type=2))
        self.distance_max_value.trace("w", lambda name, index, mode, distance_max_value=self.distance_max_value, type=2: self.changed_val(self.distance_max_value.get(), type=7))
        self.max_area_value.trace("w", lambda name, index, mode, max_area_value=self.max_area_value, type=5: self.changed_val(self.max_area_value.get(), type=5))
        self.min_area_value.trace("w", lambda name, index, mode, min_area_value=self.min_area_value, type=5: self.changed_val(self.min_area_value.get(), type=5))

        self.bind_all("<Button-1>", self.give_focus)#######3NEWWWW


    def changed_val(self, new_val, type):
        if len(new_val)>0:
            self.modif_image(self.last_empty, change_track=type)

    def verif_E_tresh_fun(self, value, method):
        if value=="" and method=="key":
            return True
        else:
            try:
                int(value)
                return True
            except:
                return False

    def verif_E_float_fun(self, value, method):
        if method!="forced":
            if value=="" and method=="key":
                return True
            else:
                try:
                    float(value)
                    return True
                except:
                    return False
        else:
            return False


    def change_msg(self,new_message,*arg):
        self.user_message.set(new_message)

    def remove_msg(self,*arg):
        self.user_message.set(self.default_message)

    def change_nb_ar(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_nb_per_Ar.Assign(parent=newWindow, boss=self)

    def change_nb_ar_glob(self, *karg):
        self.liste_ind_per_ar=[self.KindTVar.get() for x in range(len(self.Arenas))]
        self.modif_image()

    def update_thresh(self):
        self.modif_image(img=self.TMP_image_to_show)

    def give_focus(self,event):###############
        if event.widget.winfo_class()!="Entry":################
            self.Vid_Lecteur.focus_set()####################

    def modif_image(self, img=[], aff=True, change_track=None, *arg):
        if change_track!=None:
            self.CheckVar.set(change_track)

        if len(img)==0:
            img=np.copy(self.last_empty)
        else:
            self.last_empty = img

        liste_positions=[]
        actual_pos=self.Scrollbar.active_pos
        if self.Vid.Stab:
            img = Class_stabilise.find_best_position(Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=img, show=False)

        TMP_image_to_show2 = np.copy(img)

        if self.CheckVar.get()>0:
            TMP_image_to_show2=cv2.cvtColor(TMP_image_to_show2,cv2.COLOR_BGR2GRAY)
            if self.Vid.Back[0]:
                TMP_image_to_show2 = cv2.subtract(self.Vid.Back[1],TMP_image_to_show2) + cv2.subtract(TMP_image_to_show2,self.Vid.Back[1])
            else:
                White_screen=np.zeros([TMP_image_to_show2.shape[0],TMP_image_to_show2.shape[1],1], np.uint8)
                White_screen.fill(255)
                TMP_image_to_show2 = cv2.subtract(White_screen, TMP_image_to_show2)

            if self.CheckVar.get()>1:
                _, TMP_image_to_show2=cv2.threshold(TMP_image_to_show2, int(self.thresh_value.get()), 255, cv2.THRESH_BINARY)
                if self.Vid.Mask[0]:
                    TMP_image_to_show2 = cv2.bitwise_and(TMP_image_to_show2, TMP_image_to_show2, mask=self.mask)

                if self.CheckVar.get() > 2:
                    TMP_image_to_show2 = cv2.erode(TMP_image_to_show2,self.kernel,iterations=int(self.erode_value.get()))

                    if self.CheckVar.get() > 3:
                        TMP_image_to_show2 = cv2.dilate(TMP_image_to_show2, self.kernel, iterations=int(self.dilate_value.get()))

                        if self.CheckVar.get() > 4:
                            cnts, _ = cv2.findContours(TMP_image_to_show2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                            TMP_image_to_show2=np.zeros([TMP_image_to_show2.shape[0],TMP_image_to_show2.shape[1],3], np.uint8)
                            for cnt in cnts:
                                cnt_area=cv2.contourArea(cnt)
                                if float(self.Vid.Scale[0])>0:
                                    cnt_area=cnt_area*(1/float(self.Vid.Scale[0]))**2

                                if cnt_area>=float(self.min_area_value.get()) and cnt_area<=float(self.max_area_value.get()):
                                    if self.CheckVar.get() <= 5:
                                        TMP_image_to_show2=cv2.drawContours(TMP_image_to_show2,[cnt],0,(255,255,255),-1)
                                    else:
                                        TMP_image_to_show2=cv2.drawContours(TMP_image_to_show2,[cnt],0,(255,255,255),-1)

                                        if self.CheckVar.get() == 7 and self.Scrollbar.active_pos >= (self.Vid.Cropped[1][0]/self.one_every):
                                            cnt_M = cv2.moments(cnt)
                                            cX = int(cnt_M["m10"] / cnt_M["m00"])
                                            cY = int(cnt_M["m01"] / cnt_M["m00"])
                                            liste_positions.append((cX,cY))

                            if self.CheckVar.get() == 7 and aff:
                                if self.Scrollbar.active_pos > (self.Vid.Cropped[1][0]/self.one_every):
                                    TMP_part = self.Vid_Lecteur.current_part
                                    if self.Vid.Fusion[self.Vid_Lecteur.current_part][0] > ((self.Scrollbar.active_pos-1 )* self.one_every):
                                        self.Vid_Lecteur.capture.release()
                                        TMP_part=self.Vid_Lecteur.current_part-1
                                        self.Vid_Lecteur.capture = cv2.VideoCapture(self.Vid.Fusion[TMP_part][1])


                                    old_img = self.Vid_Lecteur.capture[int((self.Scrollbar.active_pos-1)* self.one_every) - self.Vid.Fusion[TMP_part][0]].asnumpy()
                                    old_img=cv2.cvtColor(old_img, cv2.COLOR_BGR2RGB)

                                    Old_pos=self.modif_image(img=old_img,aff=False)
                                    overlay=np.copy(img)
                                    alpha = 0.25  # Transparency factor.


                                    for Pt in Old_pos:
                                        if float(self.Vid.Scale[0])>0:
                                            overlay=cv2.circle(overlay,Pt,int(round(float(self.distance_max_value.get())*float(self.Vid.Scale[0]))),(0,0,255),-1)
                                        else:
                                            overlay=cv2.circle(overlay,Pt,int(round(float(self.distance_max_value.get()))),(0,0,255),-1)


                                    TMP_image_to_show2=cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

                                else:
                                    TMP_image_to_show2 = np.copy(img)

                                if self.Scrollbar.active_pos >= (self.Vid.Cropped[1][0] / self.one_every):
                                    for Pt in liste_positions:
                                        TMP_image_to_show2 = cv2.circle(TMP_image_to_show2, Pt, 5, (0, 200, 200), -1)

        if self.Vid.Mask[0] and self.CheckVar.get() <2:
            TMP_image_to_show2 = cv2.bitwise_and(TMP_image_to_show2, TMP_image_to_show2, mask=self.mask)

        TMP_image_to_show2 = cv2.drawContours(TMP_image_to_show2, self.Arenas, -1, (255, 0, 0), 4)
        for Ar in range(len(self.Arenas)):
            TMP_image_to_show2 = cv2.putText(TMP_image_to_show2, str(self.liste_ind_per_ar[Ar]), (self.Arenas[Ar][0][0][0]-50, self.Arenas[Ar][0][0][1] + 50),
                              cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 3)

        TMP_image_to_show2=cv2.resize(TMP_image_to_show2,(int(img.shape[1]/1.5),int(img.shape[0]/1.5)))
        if aff:
            self.Vid_Lecteur.afficher_img(TMP_image_to_show2)
        else:
            return(liste_positions)



    def change_vid(self, vid):
        self.End_of_window()
        self.main_frame.selected_vid = self.dict_Names[vid].Video
        self.main_frame.Beg_track()

    def Validate(self, follow=False):
        self.Vid.Track[0] = True
        self.Vid.Track[1][0] = int(self.thresh_value.get())
        self.Vid.Track[1][1] = int(self.erode_value.get())
        self.Vid.Track[1][2] = int(self.dilate_value.get())
        self.Vid.Track[1][3] = [float(self.min_area_value.get()),float(self.max_area_value.get())]
        self.Vid.Track[1][4] = [0,0]
        self.Vid.Track[1][5] = float(self.distance_max_value.get())
        self.Vid.Track[1][6] = self.liste_ind_per_ar
        self.End_of_window()

    def End_of_window(self):
        self.unbind_all("<Button-1>")
        self.Vid_Lecteur.proper_close()
        self.grab_release()
        self.canvas_options.grid_forget()
        self.canvas_options.destroy()
        self.canvas_user.grid_forget()
        self.canvas_user.destroy()

        if not self.portion:
            self.boss.update()
            self.main_frame.update_projects()
            self.main_frame.return_main()
        if self.portion:
            self.parent.destroy()


    def pressed_can(self, Pt):
        pass

    def moved_can(self, Pt):
        pass

    def released_can(self, Pt):
        pass

"""
root = Tk()
root.geometry("+100+100")
Video_file=Class_Video.Video(File_name="D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01.avi")
interface = Cropping(parent=root, boss=None, Video_file=Video_file)
root.mainloop()

"""