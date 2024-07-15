from tkinter import *
import os
from AnimalTA.E_Post_tracking import Coos_loader_saver as CoosLS
from AnimalTA.E_Post_tracking.b_Analyses import Functions_deformation, Functions_Analyses_Speed
from AnimalTA.A_General_tools import Class_Lecteur, Function_draw_mask as Dr, UserMessages, Class_stabilise, Color_settings, Class_loading_Frame, Function_draw_mask, Interface_extend
import numpy as np
import cv2
from scipy.signal import savgol_filter
from tkinter import filedialog
from PIL import ImageFont, ImageDraw, Image
import pickle

class Lecteur(Frame):
    """This Frame allow the user to export a video that has been modified by AnimalTA.
    The video can be the original one, the stabilised one or with the trajectories displayed.
    The trajectories can be the original ones of the smoothed ones.
    The Identity of the individuals can also be displayed.
    """
    def __init__(self, parent, boss, main_frame, Vid, Video_liste, params_export=None, auto=False, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.main_frame=main_frame
        self.boss=boss
        self.Video_liste=Video_liste
        self.Vid=Vid
        self.Pos = []
        self.cache=False
        self.show_ID=False
        self.show_track=False
        self.show_smooth=False
        self.show_expo=False
        self.show_deform=False
        self.deformed = False
        self.smoothed=False
        self.tail_size = DoubleVar(value=10)
        self.mask = Dr.draw_mask(Vid)
        self.kernel = np.ones((3, 3), np.uint8)
        self.params_export=params_export
        self.auto=auto

        if self.auto:
            self.winfo_toplevel().title(self.Vid.User_Name)



        self.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")

        mask = Function_draw_mask.draw_mask(self.Vid)
        Arenas, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.Arenas = Function_draw_mask.Organise_Ars(Arenas)

        Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
        with open(Param_file, 'rb') as fp:
            self.Params = pickle.load(fp)

        if self.Vid.Track[1][10][0] == 0:
            try:
                self.TMP_back=cv2.cvtColor(self.Vid.Back[1].copy(), cv2.COLOR_BGR2GRAY)
            except:
                self.TMP_back=self.Vid.Back[1].copy()
        else:
            try:
                self.TMP_back = cv2.cvtColor(self.Vid.Back[1].copy(), cv2.COLOR_GRAY2BGR)
            except:
                self.TMP_back=self.Vid.Back[1].copy()


        #Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        self.Messages = UserMessages.Mess[self.Language.get()]
        f.close()

        Right_Frame=Frame(self, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        Right_Frame.grid(row=0, column=1, sticky="nsew")

        self.CheckVar=IntVar(value=0)

        if self.Vid.Back[0]:
            self.Or_back=self.Vid.Back[1].copy()

        #No modification except cropping
        Only_cropped=Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=0, text=self.Messages["Save_Vid1"], command=self.change_type,**Color_settings.My_colors.Checkbutton_Base)
        Only_cropped.grid(row=2, sticky="w")
        if auto and self.params_export["CheckVar"]>=0:
            self.CheckVar.set(0)

        #Stabilization
        if self.Vid.Stab[0]:
            Stab=Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=1, text=self.Messages["Save_Vid2"], command=self.change_type,**Color_settings.My_colors.Checkbutton_Base)
            Stab.grid(row=3, sticky="w")
            if auto and self.params_export["CheckVar"] >= 1:
                self.CheckVar.set(1)

        #Greyscaled
        if self.Vid.Track[1][10][0] == 0:
            Grey=Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=2, text=self.Messages["Track3"], command=self.change_type,**Color_settings.My_colors.Checkbutton_Base)
            Grey.grid(row=4, sticky="w")
            if auto and self.params_export["CheckVar"] >= 2:
                self.CheckVar.set(2)

        #Flicker correction
        if self.Vid.Track[1][9]:
            Flicker_Corr=Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=3, text=self.Messages["Param14"], command=self.change_type,**Color_settings.My_colors.Checkbutton_Base)
            Flicker_Corr.grid(row=5, sticky="w")
            if auto and self.params_export["CheckVar"] >= 3:
                self.CheckVar.set(3)


        #Light correction
        if self.Vid.Track[1][7]:
            Light_Corr=Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=4, text=self.Messages["Param10"], command=self.change_type,**Color_settings.My_colors.Checkbutton_Base)
            Light_Corr.grid(row=6, sticky="w")
            if auto and self.params_export["CheckVar"] >= 4:
                self.CheckVar.set(4)

        #Background substraction
        if self.Vid.Back[0]==1:
            Back=Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=5, text=self.Messages["Names7"], command=self.change_type,**Color_settings.My_colors.Checkbutton_Base)
            Back.grid(row=7, sticky="w")
            if auto and self.params_export["CheckVar"] >= 5:
                self.CheckVar.set(5)

        #Threshold
        Thresh=Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=6, text=self.Messages["Names1"], command=self.change_type,**Color_settings.My_colors.Checkbutton_Base)
        Thresh.grid(row=8, sticky="w")
        if auto and self.params_export["CheckVar"]>=6:
            self.CheckVar.set(6)

        #Erosion
        if self.Vid.Track[1][1]>0:
            Erosion=Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=7, text=self.Messages["Names2"], command=self.change_type,**Color_settings.My_colors.Checkbutton_Base)
            Erosion.grid(row=9, sticky="w")
            if auto and self.params_export["CheckVar"] >= 7:
                self.CheckVar.set(7)

        #Dilation
        if self.Vid.Track[1][2] > 0:
            Dilation=Checkbutton(Right_Frame, variable=self.CheckVar, onvalue=8, text=self.Messages["Names3"], command=self.change_type,**Color_settings.My_colors.Checkbutton_Base)
            Dilation.grid(row=10, sticky="w")
            if auto and self.params_export["CheckVar"] >= 8:
                self.CheckVar.set(8)


        #Display trajectories
        if self.Vid.Tracked:
            self.show_track_B=Button(Right_Frame, text=self.Messages["Save_Vid3"], command=self.change_track,**Color_settings.My_colors.Button_Base)
            self.show_track_B.grid(row=0, column=0, sticky="ew")

            self.Coos_brutes, self.who_is_here = CoosLS.load_coos(self.Vid, location=self)
            self.Coos=self.Coos_brutes.copy()
            self.NB_ind=len(self.Vid.Identities)

            # Whether the identity should appear on the video or not
            self.Show_ID_B = Button(Right_Frame, text=self.Messages["Save_Vid5"], command=self.change_show_ID,**Color_settings.My_colors.Button_Base)
            self.Show_ID_B.grid(row=1, column=0, sticky="ew")

            #If the trajectories were smoothed, we propose to display smoothed trajectories
            self.show_Explo_B = Button(Right_Frame, text=self.Messages["Sequences_Explo"], command=self.change_explo,**Color_settings.My_colors.Button_Base)
            self.show_Explo_B.grid(row=0, column=1, sticky="ew")

            self.show_smooth_B = Button(Right_Frame, text=self.Messages["Save_Vid4"], command=self.change_smooth,
                                        **Color_settings.My_colors.Button_Base)


            #If the perspective was transformed, we propose this option
            if len(self.Vid.Analyses[4][0])>0:
                self.show_deform_B = Button(Right_Frame, text=self.Messages["Analyses12"], command=self.change_deform,**Color_settings.My_colors.Button_Base)
                self.show_deform_B.grid(row=1, column=1, sticky="ew")


            #Length of trajectories tail can also be modified
            self.max_tail = IntVar()
            self.max_tail.set(min([self.Vid.Frame_nb[1]/self.Vid.Frame_rate[1], 600]))
            self.Scale_tail = Scale(Right_Frame, from_=0, to=self.max_tail.get(), variable=self.tail_size, resolution=0.5, orient="horizontal", label=self.Messages["Control4"], command=self.modif_image,**Color_settings.My_colors.Scale_Base)


        #Save the video
        self.Save_Vid_Button=Button(Right_Frame, text=self.Messages["GButton18"], command=self.save_vid, **Color_settings.My_colors.Button_Base)
        self.Save_Vid_Button.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.Save_Vid_Button.grid(row=12, column=0)

        self.Save_multi_Vid_Button=Button(Right_Frame, text="Export multiple videos", command=self.save_multi_vid, **Color_settings.My_colors.Button_Base)
        self.Save_multi_Vid_Button.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.Save_multi_Vid_Button.grid(row=12, column=1)

        #Return to the main menu without saving
        self.Save_Return_Button=Button(Right_Frame, text=self.Messages["GButton11"], command=self.End_of_window, **Color_settings.My_colors.Button_Base)
        self.Save_Return_Button.config(background=Color_settings.My_colors.list_colors["Cancel"],
                                    fg=Color_settings.My_colors.list_colors["Fg_Cancel"])
        self.Save_Return_Button.grid(row=16, column=0, columnspan=2)

        #Video reader

        self.Vid_Lecteur= Class_Lecteur.Lecteur(self, self.Vid)
        if not self.auto:
            self.Vid_Lecteur.grid(row=0, column=0, sticky="nsew")
        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1, minsize=150)

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        if self.Vid.Cropped[0]:
            self.to_sub = round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every)
        else:
            self.to_sub = 0


        self.loading_canvas=Frame(Right_Frame, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.loading_canvas.grid(row=13, column=0, columnspan=2)

        self.bouton_hide = Button(Right_Frame, text=self.Messages["Do_track1"], command=self.hide, **Color_settings.My_colors.Button_Base)


        if self.auto:
            if self.Vid.Tracked:
                self.change_track(forced=self.params_export["show_track"])
                self.change_smooth(forced=self.params_export["show_smooth"])
                self.change_show_ID(forced=self.params_export["show_ID"])
                self.change_explo(forced=self.params_export["show_explo"])
                if len(self.Vid.Analyses[4][0]) > 0:
                    self.change_deform(forced=self.params_export["show_deform"])
                self.tail_size.set(self.params_export["tail_size"])

            self.Vid_Lecteur.speed.set(self.params_export["speed"])
            self.save_vid(self.params_export["dir"])
            self.End_of_window()


    def change_track(self, forced=None):
        if forced!=None:
            self.show_track= not forced
        #Should the trajectories be displayed.
        if self.show_track:
            self.show_track=False
            self.show_track_B.config(**Color_settings.My_colors.Button_Base)
        else:
            self.show_track=True
            self.show_track_B.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.change_type()

    def change_smooth(self, forced=None):
        if forced!=None:
            self.show_smooth= not forced
        #Should the trajectories be displayed.
        if self.show_smooth:
            self.show_smooth=False
            self.show_smooth_B.config(**Color_settings.My_colors.Button_Base)
        elif self.Vid.Smoothed[0]>0:
            self.show_smooth=True
            self.show_smooth_B.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])


    def change_explo(self, forced=None):
        if forced!=None:
            self.show_expo= not forced
        #Should the exploration be displayed.
        if self.show_expo:
            self.show_expo=False
            self.show_Explo_B.config(**Color_settings.My_colors.Button_Base)
        else:
            self.show_expo=True
            self.show_Explo_B.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.change_type()

    def change_deform(self, forced=None):
        if forced!=None:
            self.show_deform= not forced
        #Should the trajectories be displayed.
        if self.show_deform:
            self.show_deform=False
            self.show_deform_B.config(**Color_settings.My_colors.Button_Base)
        else:
            self.show_deform=True
            self.show_deform_B.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.change_type()

    def change_show_ID(self, forced=None):
        if forced!=None:
            self.show_ID= not forced
        #Whether the identities should appear or not
        if self.show_ID:
            self.show_ID=False
            self.Show_ID_B.config(**Color_settings.My_colors.Button_Base)
        else:
            self.show_ID=True
            self.Show_ID_B.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.modif_image()

    def hide(self):
        #To minimise the window
        self.cache = True
        self.boss.update_idletasks()
        self.boss.overrideredirect(False)
        self.boss.state('iconic')


    def save_multi_vid(self):
        Export_params={"CheckVar":self.CheckVar.get(),
                       "show_track":self.show_track,
                       "show_smooth":self.show_smooth,
                       "show_explo":self.show_expo,
                       "show_deform":self.show_deform,
                       "show_ID":self.show_ID,
                       "speed":self.Vid_Lecteur.speed.get(),
                       "tail_size":self.tail_size.get()}


        newWindow = Toplevel(self.parent)
        interface = Interface_extend.Extend(parent=newWindow, value=Export_params, boss=self.main_frame,
                                            Video_file=self.Vid, type="export", do_self=True, to_close=self)

    def save_vid(self, file_to_save=None):
        #Export the video. To that aim, the video is played and every image is changed according to the parameters set by user.
        #The resulting video is saved in a file defined by user
        self.Vid_Lecteur.stop()
        self.Vid_Lecteur.unbindings()
        #Ask user where to save the video
        if file_to_save==None:
            file_to_save = filedialog.asksaveasfilename(defaultextension=".avi", initialfile="Untitled_video.avi", filetypes=(("Video", "*.avi"),))
        else:
            file_to_save=file_to_save+"/"+self.Vid.User_Name+"_exported.avi"


        if len(file_to_save)>0:

            self.loading_bar = Class_loading_Frame.Loading(self.loading_canvas)
            self.loading_bar.grid()
            self.bouton_hide.grid(row=20, column=0, columnspan=2)#Button allowing to minimise the window
            self.bouton_hide.grab_set()

            if self.Vid.Cropped[0]:
                start = self.Vid.Cropped[1][0]
                end = self.Vid.Cropped[1][1]
                self.Vid_Lecteur.Scrollbar.active_pos = round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every) - 1
            else:
                start = 0
                end = self.Vid.Frame_nb[1] - 1
                self.Vid_Lecteur.Scrollbar.active_pos=0

            frame_width = int(self.Vid.shape[1])
            frame_height = int(self.Vid.shape[0])
            speed=self.Vid_Lecteur.speed.get()
            if speed < 0:#We allow the user to change the frame rate of the video saved
                frame_rate = (self.Vid.Frame_rate[1]) / (abs(speed))
            elif speed>0 :
                frame_rate = (self.Vid.Frame_rate[1]) * abs(speed + 1)
            else:
                frame_rate = self.Vid.Frame_rate[1]

            size = (frame_width, frame_height)
            result = cv2.VideoWriter(file_to_save, cv2.VideoWriter_fourcc(*'XVID'), frame_rate, size)#We save the video in teh chosen file

            for frame in np.arange(int(start), int(end) + self.Vid_Lecteur.one_every, self.Vid_Lecteur.one_every):
                frame=int(frame)
                try:
                    self.loading_bar.show_load((frame - start) / ((end+ self.Vid_Lecteur.one_every )- start - 1))
                    new_img=self.Vid_Lecteur.move1(aff=False)
                    new_img=cv2.cvtColor(new_img,cv2.COLOR_BGR2RGB)
                    result.write(new_img)

                except:
                    pass
            result.release()

            #In the end, the Frame is destroyed and we go back to main menu
            self.loading_bar.destroy()
            if self.cache:
                self.boss.update_idletasks()
                self.boss.state('normal')
                self.boss.overrideredirect(True)

            self.End_of_window()

        return(True)

    def End_of_window(self):
        #Propoer close pf the Frame
        self.unbind_all("<Button-1>")
        try:
            self.Vid_Lecteur.proper_close()
        except:
            pass
        self.grab_release()
        if not self.auto:
            self.main_frame.return_main()
        else:
            self.boss.destroy()

    def modif_image(self, img=[], aff=True, **kwargs):
        if self.auto:
            aff=False

        #Change the image according to the parameters set by user
        if len(img) <= 10:
            new_img=np.copy(self.last_empty)
        else:
            self.last_empty = img
            new_img = np.copy(img)

        #Stabilise
        if self.CheckVar.get()>0 and self.Vid.Stab[0]:
            new_img = Class_stabilise.find_best_position(Vid=self.Vid, Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=False)

        if self.Vid.Back[0]:
            self.TMP_back = self.Or_back.copy()


        #Greyscale
        if self.CheckVar.get()>1:

            if self.Vid.Track[1][10][0] == 0:
                new_img = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)

                if self.Vid.Back[0] == 1 and len(self.TMP_back.shape) == 3:
                    self.TMP_back = cv2.cvtColor(self.TMP_back, cv2.COLOR_BGR2GRAY)

        #Correct flicker
        if self.CheckVar.get()>2 and self.Vid.Track[1][9] and int(self.Scrollbar.active_pos) > round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every):
            diff = round(self.Scrollbar.active_pos - (self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every))
            for elem in range(self.Scrollbar.active_pos - min(2, diff), self.Scrollbar.active_pos):
                last_img = cv2.cvtColor(self.Vid_Lecteur.update_image(elem, return_img=True), cv2.COLOR_BGR2GRAY)
                new_img = cv2.addWeighted(last_img, 0.5, new_img, 1 - 0.5, 0)

        #Light_correction
        if self.CheckVar.get()>3 and self.Vid.Track[1][7]:
            grey = np.copy(new_img)
            if self.Vid.Mask[0]:
                bool_mask = self.mask[:, :].astype(bool)
            else:
                bool_mask = np.full(grey.shape, True)
            grey2 = grey[bool_mask]

            # Inspired from: https://stackoverflow.com/questions/57030125/automatically-adjusting-brightness-of-image-with-opencv
            brightness = np.sum(grey2) / (255 * grey2.size)  # Mean value
            ratio = brightness / self.Vid_Lecteur.or_bright
            new_img = cv2.convertScaleAbs(grey, alpha=1 / ratio, beta=0)

        #Background
        if self.CheckVar.get()>4:
            # Show background subtraction

            if self.Vid.Back[0] == 2:
                prog_back = cv2.createBackgroundSubtractorMOG2(history=1000, varThreshold= self.Vid.Track[1][0], detectShadows=False)
                # Create a background based on 3 frames:
                frames = []
                nb_passed = min(self.Scrollbar.active_pos, 1000)
                for imgID in range(nb_passed, 1, min([-1, -int(nb_passed / 5)])):
                    batch_img = self.Vid_Lecteur.update_image(frame=self.Scrollbar.active_pos - self.to_sub - imgID,
                                                              first=False, actual_pos=None, return_img=True)

                    if self.Vid.Stab[0]:
                        batch_img = Class_stabilise.find_best_position(Vid=self.Vid,
                                                                       Prem_Im=self.Vid_Lecteur.Prem_image_to_show,
                                                                       frame=batch_img, show=False,
                                                                       prev_pts=self.Vid.Stab[1])

                    batch_img = cv2.cvtColor(batch_img, cv2.COLOR_BGR2GRAY)

                    # Correct flicker
                    if self.Vid.Track[1][9] and self.Scrollbar.active_pos + imgID > round(self.Vid.Cropped[1][0] / self.one_every):
                        diff = int(self.Scrollbar.active_pos + imgID - round(self.Vid.Cropped[1][0] / self.one_every))
                        for elem in range(self.Scrollbar.active_pos + imgID - min(2, diff),
                                          self.Scrollbar.active_pos + imgID):
                            last_img = cv2.cvtColor(self.Vid_Lecteur.update_image(elem, return_img=True),
                                                    cv2.COLOR_BGR2GRAY)
                            batch_img = cv2.addWeighted(last_img, 0.5, batch_img, 1 - 0.5, 0)


                    if self.Vid.Track[1][7]:
                        grey = np.copy(batch_img)
                        if self.Vid.Mask[0]:
                            bool_mask = self.mask[:, :].astype(bool)
                        else:
                            bool_mask = np.full(grey.shape, True)
                        grey2 = grey[bool_mask]
                        brightness = np.sum(grey2) / (255 * grey2.size)  # Mean value

                        # Inspired from: https://stackoverflow.com/questions/57030125/automatically-adjusting-brightness-of-image-with-opencv
                        ratio = brightness / self.Vid_Lecteur.or_bright
                        batch_img = cv2.convertScaleAbs(grey, alpha=1 / ratio, beta=0)

                    prog_back.apply(batch_img)

                self.TMP_back = prog_back.getBackgroundImage()

            if self.TMP_back is None:
                self.TMP_back = new_img.copy()


            if self.Vid.Back[0] == 1 or self.Vid.Back[0] == 2:
                if self.Vid.Track[1][10][1]== 0:
                    new_img = cv2.absdiff(self.TMP_back, new_img)
                elif self.Vid.Track[1][10][1] == 1:
                    new_img = cv2.subtract(self.TMP_back, new_img)
                elif self.Vid.Track[1][10][1] == 2:
                    new_img = cv2.subtract(new_img, self.TMP_back)

                if self.Vid.Track[1][10][2] == 1:
                    new_img = new_img.astype(np.uint16)
                    new_img = (new_img * 255) // self.TMP_back
                    new_img = new_img.astype(np.uint8)

                if self.Vid.Track[1][10][0] == 1:
                    new_img = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)


            elif not self.Vid.Back[1]==3 and self.Vid.Track[1][10][0] == 1:
                new_img = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)


        if self.CheckVar.get()>5 and self.CheckVar.get()!=9:
            if self.Vid.Back[0]==1 or self.Vid.Back[0]==2:
                _, new_img = cv2.threshold(new_img, self.Vid.Track[1][0], 255, cv2.THRESH_BINARY)
            elif self.Vid.Back[0]==0:
                if self.Vid.Track[1][10][1] == 2:
                    new_img = cv2.bitwise_not(new_img)

                new_img = cv2.adaptiveThreshold(new_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV,
                                                self.Vid.Track[1][0] + 1 , 10)


            # Mask
            if self.Vid.Mask[0]:
                new_img = cv2.bitwise_and(new_img, new_img, mask=self.mask)

        # Erosion
        if self.CheckVar.get()>6 and self.Vid.Track[1][1] > 0:
            new_img = cv2.erode(new_img,self.kernel, iterations=self.Vid.Track[1][1])

        # Dilation
        if self.CheckVar.get()>7 and self.Vid.Track[1][2] > 0:
            new_img = cv2.dilate(new_img, self.kernel, iterations=self.Vid.Track[1][2])

        if self.show_deform:
            new_img = cv2.warpPerspective(new_img, self.Vid.Analyses[4][0], (new_img.shape[1], new_img.shape[0]))

        #Show trajectories
        if self.show_track or self.show_ID or self.show_expo:
            if len(new_img.shape)<3:
                new_img=cv2.cvtColor(new_img, cv2.COLOR_GRAY2BGR)

            if self.Vid.Cropped[0]:
                to_remove = round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every)
            else:
                to_remove = 0

            for ind in range(self.NB_ind):
                color = self.Vid.Identities[ind][2]
                if self.show_expo:
                    if self.Vid.Analyses[2][0] == 0:
                        Exploration_in, empty = Functions_Analyses_Speed.calculate_exploration(self.Vid.Analyses[2],self.Vid, self.Coos[ind][ 0:int(self.Scrollbar.active_pos - to_remove + 1)],                                                                                           0,
                                                                                               int(self.Scrollbar.active_pos - to_remove + 1),
                                                                                               self.Arenas[self.Vid.Identities[ind][0]], show=True)  #

                        bool_mask = empty.astype(bool)
                        empty = cv2.cvtColor(empty, cv2.COLOR_GRAY2RGB)
                        empty[np.where((empty == [255, 255, 255]).all(axis=2))] = [255, 0, 0]

                        alpha = 0.5
                        new_img[bool_mask] = cv2.addWeighted(new_img, alpha, empty, 1 - alpha, 0)[bool_mask]

                    else:
                        Exploration_in, new_img = Functions_Analyses_Speed.calculate_exploration(self.Vid.Analyses[2],self.Vid, self.Coos[ind][0:int(self.Scrollbar.active_pos - to_remove + 1)],
                                                                                                 0,int(self.Scrollbar.active_pos - to_remove + 1),self.Arenas[self.Vid.Identities[ind][0]],show=True, image=new_img)

                if self.show_track:
                    for prev in range(min(int(self.tail_size.get() * self.Vid.Frame_rate[1]), int(self.Scrollbar.active_pos - to_remove))):
                        if int(self.Scrollbar.active_pos - prev) > round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every) and int(self.Scrollbar.active_pos) <= round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every):
                            if self.Coos[ind][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][
                                0] != -1000 and  self.Coos[ind][int(self.Scrollbar.active_pos - prev - to_remove)][
                                        0] != -1000:

                                if self.show_track:

                                    TMP_tail_1 = (int(
                                        self.Coos[ind][int(self.Scrollbar.active_pos - 1 - prev - to_remove)][
                                            0]),
                                                  int(self.Coos[ind][
                                                          int(self.Scrollbar.active_pos - 1 - prev - to_remove)][1]))

                                    TMP_tail_2 = (
                                    int(self.Coos[ind][int(self.Scrollbar.active_pos - prev - to_remove)][0]),
                                    int(self.Coos[ind][int(self.Scrollbar.active_pos - prev - to_remove)][1]))
                                    new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, max(int(3*self.Vid_Lecteur.ratio),1))

                if self.Scrollbar.active_pos >= round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every) and self.Scrollbar.active_pos < (round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every) + 1):
                    center = self.Coos[ind][self.Scrollbar.active_pos - to_remove]
                    if center[0] != -1000:
                        if self.show_track:
                            new_img = cv2.circle(new_img, (int(center[0]), int(center[1])),radius=max(int(4 * self.Vid_Lecteur.ratio), 1), color=color, thickness=-1)
                        if self.show_ID:
                            fontpath = os.path.join(".","simsun.ttc")
                            if self.Vid_Lecteur.ratio < 10:
                                font = ImageFont.truetype(fontpath, max(1, int(self.Vid_Lecteur.ratio * 30)))
                                stroke_width = max(1, int(self.Vid_Lecteur.ratio * 1))
                            else:
                                font = ImageFont.truetype(fontpath, 1)
                                stroke_width = 1
                            new_img = Image.fromarray(new_img)
                            draw = ImageDraw.Draw(new_img)
                            draw.text((int(float(center[0])+10*self.Vid_Lecteur.ratio), int(float(center[1])+10*self.Vid_Lecteur.ratio)), self.Vid.Identities[ind][1], font=font, fill=(255, 255, 255, 0), stroke_width=stroke_width)
                            draw.text((int(float(center[0])+10*self.Vid_Lecteur.ratio), int(float(center[1])+10*self.Vid_Lecteur.ratio)), self.Vid.Identities[ind][1], font=font, fill=(color ))
                            new_img = np.array(new_img)
        if aff:
            self.Vid_Lecteur.afficher_img(new_img)
        else:
            return(new_img)

    def change_type(self):
        #Update the options available according to what kind of video the user want as an output
        if self.show_track :#If user there is a tracking done, we allow to choose for tail size
            self.Scale_tail.grid(row=1, column=1,rowspan=8, columnspan=2)
            if self.Vid.Smoothed[0]>0:
                self.show_smooth_B.grid(row=1, column=1, sticky="ew")
        else:
            try:
                self.Scale_tail.grid_forget()
                self.show_smooth_B.grid_forget()
            except:
                pass


        if (self.deformed and not self.show_deform) or (not self.deformed and self.show_deform) or (self.show_smooth and not self.smoothed) or (not self.show_smooth and self.smoothed):
            self.Coos = self.Coos_brutes

            if self.show_deform:
                self.Coos=Functions_deformation.deform_coos(self.Coos, self.Vid.Analyses[4][0])

            if self.show_smooth:#If user wants original trajectories
                self.Coos=self.smooth_coos(self.Coos)

            self.deformed = self.show_deform
            self.smoothed = self.show_smooth

        self.modif_image()

    def smooth_coos(self,data):
        #Apply the smoothing filter to the trajectories
        tmp_coos=data.copy()
        for ind in range(len(self.Coos_brutes)):
            ind_coo=[[np.nan if val==-1000 else val for val in row ] for row in tmp_coos[ind]]
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
            ind_coo=[[-1000 if np.isnan(val) else val for val in row] for row in ind_coo]
            tmp_coos[ind]=ind_coo
        return(tmp_coos)

    def pressed_can(self, Pt, *args):
        pass

    def moved_can(self, Pt, Shift):
        pass

    def released_can(self, Pt):
        pass