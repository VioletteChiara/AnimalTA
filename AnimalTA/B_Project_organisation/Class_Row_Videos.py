import math
import os
from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
from functools import partial
from tkinter import messagebox
from AnimalTA.A_General_tools import Function_draw_mask as Dr, Interface_extend, UserMessages
from AnimalTA.C_Pretracking import Interface_cropping, Interface_back, Interface_arenas, Interface_scaling, \
    Interface_stabilis
from tkinter import font
import numpy as np
from watchpoints import watch


class Row_Can(Canvas):
    '''
    In the main window, the videos are presented as rows of a table.
    This class is the Frame that contains one row.
    '''
    def __init__(self, Video_file, main_boss,proj_pos, parent=None, **kw):
            Frame.__init__(self, parent, kw)

            self.Video=Video_file
            self.main_frame=main_boss
            self.parent=parent
            self.proj_pos=proj_pos #The position of the row in the table
            self.config(width=500)
            self.width_show=600


            self.Language = StringVar()
            f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
            self.Language.set(f.read())
            self.LanguageO = self.Language.get()
            f.close()

            self.Messages = UserMessages.Mess[self.Language.get()]

            #Draw preparation:
            self.oeuil = cv2.imread(UserMessages.resource_path(os.path.join("AnimalTA","Files","Oeuil.png")))
            self.oeuil = cv2.cvtColor(self.oeuil, cv2.COLOR_BGR2RGB)
            self.Size_oe = self.oeuil.shape
            self.oeuil = cv2.resize(self.oeuil, (int(self.Size_oe[1] / 4), int(self.Size_oe[0] / 4)))
            self.oeuil2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.oeuil))

            self.oeuilB = cv2.imread(UserMessages.resource_path(os.path.join("AnimalTA","Files","OeuilB.png")))
            self.oeuilB = cv2.cvtColor(self.oeuilB, cv2.COLOR_BGR2RGB)
            self.oeuilB = cv2.resize(self.oeuilB, (int(self.Size_oe[1] / 4), int(self.Size_oe[0] / 4)))
            self.oeuilB2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.oeuilB))

            self.Supr_im = PIL.Image.open(UserMessages.resource_path(os.path.join("AnimalTA","Files","cross.png")))
            self.Supr_im = PIL.ImageTk.PhotoImage(self.Supr_im)

            self.Copy_im = PIL.Image.open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Copy.png")))
            self.Copy_im = PIL.ImageTk.PhotoImage(self.Copy_im)

            self.Concat_im = PIL.Image.open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Concat.png")))
            self.Concat_im = PIL.ImageTk.PhotoImage(self.Concat_im)


            #Video name and representation:
            self.subcanvas_First = Canvas(self, bd=0, highlightthickness=0, relief='flat', width=300, height=10)
            self.subcanvas_First.grid(row=0,column=0, sticky="snwe")
            self.subcanvas_First.grid_propagate(0)
            Grid.columnconfigure(self.subcanvas_First, 0, weight=1)
            Grid.columnconfigure(self.subcanvas_First, 1, weight=1)
            Grid.columnconfigure(self.subcanvas_First, 2, weight=100)
            Grid.rowconfigure(self.subcanvas_First, 0, weight=1)
            Grid.rowconfigure(self.subcanvas_First, 1, weight=1)

            #If the video is selected, this appears green
            self.isselected=Canvas(self.subcanvas_First,heigh=75, width=15, bg="red")
            self.isselected.grid(row=0,column=0, sticky="nsw")

            #The name of the video is displayed and can be changed by the user
            self.font= font.Font(self.master, family='Arial', size=12, weight='bold')
            self.File_name_lab = Label(self.subcanvas_First, text=self.Messages["Video"] + ": ", font=font.Font(self.master, family='Arial', size=12, weight='bold'))
            self.File_name_lab.grid(row=0,column=1, sticky="nsw")
            self.File_name_lab.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row9"]))
            self.File_name_lab.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            self.File_name_var = StringVar()
            self.File_name_var.trace_add('write', self.change_vid_name)
            self.File_name_ent=Entry(self.subcanvas_First, textvariable=self.File_name_var, font=self.font)
            self.File_name_ent.grid(row=0,column=2, sticky="nsew")
            self.File_name_ent.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row17"]))
            self.File_name_ent.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            #Button to reset the name of the video to its original value (i.e. file name)
            self.BReset_name=Button(self.subcanvas_First,text="x", command=self.Reset_name)
            self.BReset_name.grid(row=0,column=3, sticky="nsew")
            self.BReset_name.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row16"]))
            self.BReset_name.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            #Add three buttons:
            Three_buttons=Frame(self.subcanvas_First)
            Three_buttons.grid(row=1,column=0,columnspan=2)

            #Suppress the video
            self.sBsupr=Button(Three_buttons, image=self.Supr_im, command=partial(self.main_frame.supr_video, self.Video), width=22, height=22)
            self.sBsupr.grid(row=0,column=0)
            self.sBsupr.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["GButton8"]))
            self.sBsupr.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            #Duplicate the video
            self.Bcopy=Button(Three_buttons, image=self.Copy_im, command=partial(self.main_frame.dupli_video, self.Video), width=22, height=22)
            self.Bcopy.grid(row=0,column=1)
            self.Bcopy.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["General21"]))
            self.Bcopy.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            #Concatenate the video
            Bconcat=Button(Three_buttons, image=self.Concat_im, command=self.concat, width=22, height=22)
            Bconcat.grid(row=0,column=2)
            Bconcat.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["General15"]))
            Bconcat.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            Bconcat.config(bg="SystemButtonFace", activebackground="SystemButtonFace")

            self.view_first = Canvas(self.subcanvas_First)
            self.view_first.grid(row=1, column=2)
            self.view_first.create_image(0, 0, image=self.oeuil2, anchor=NW)
            self.view_first.config(width=int(self.Size_oe[1]/4), height=int(self.Size_oe[0]/4))
            self.view_first.bind("<Enter>", self.show_first)
            self.view_first.bind("<Leave>", self.stop_show_first)
            self.subcanvas_First.bind("<Button-1>", self.select_vid)
            self.File_name_lab.bind("<Button-1>", self.select_vid)
            self.bind("<Button-1>", self.select_vid)
            self.isselected.bind("<Button-1>", self.select_vid)

            #Options of pretracking:
            self.canvas_main = Canvas(self, heigh = 150, relief='ridge')
            self.canvas_main.grid(row=0, column=1, sticky="ew")
            self.canvas_main.bind("<Button-1>", self.select_vid)

            Pos_col=1
            #Frame_rate
            self.subcanvas_Fr_rate = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='flat')
            self.subcanvas_Fr_rate.grid(row=0,column=Pos_col, sticky="we")
            self.subcanvas_Fr_rate.columnconfigure(0,weight=1)
            self.Frame_rate_status=Label(self.subcanvas_Fr_rate,text=self.Messages["RowL11"])
            self.Frame_rate_status.grid(row=0,column=0, sticky="we")



            self.Fr_rate=[60,60]
            if self.Video!=None:
                self.Fr_rate[0]=self.Video.Frame_rate[0]
                self.Fr_rate[1] = self.Video.Frame_rate[1]

            self.List_poss_FrRate =[self.Messages["RowL12"]+ " " +str(round(self.Fr_rate[0],2))]
            value=self.Fr_rate[0]
            while value > 1:
                value=value/2
                self.List_poss_FrRate.append(round(value,2))
            self.holder=StringVar()

            if self.Fr_rate[0]==self.Fr_rate[1]:
                self.holder.set(self.Messages["RowL12"]+ " " +str(round(self.Fr_rate[0],2)))
            else:
                self.holder.set(self.Fr_rate[1])
            self.bouton_Fr_rate = OptionMenu(self.subcanvas_Fr_rate, self.holder, *self.List_poss_FrRate, command=self.change_fps)
            self.bouton_Fr_rate.grid(row=1, column=0, sticky="we")
            self.bouton_Fr_rate.bind("<Button-1>",self.ask_clear_data)
            self.bouton_Fr_rate.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row0"].format(round(self.Fr_rate[1],2))))
            self.bouton_Fr_rate.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            self.bouton_extend_Fr_rate=Button(self.subcanvas_Fr_rate, text=self.Messages["Row0_ExB"], command=self.extend_change_fps)
            self.bouton_extend_Fr_rate.grid(row=2, column=0)
            self.bouton_extend_Fr_rate.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row0_Ex"]))
            self.bouton_extend_Fr_rate.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            Pos_col+=2

            #Video cropped
            self.subcanvas_Cropping = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='flat')
            self.subcanvas_Cropping.grid(row=0,column=Pos_col, sticky="we")
            self.subcanvas_Cropping.columnconfigure(0,weight=1)
            self.text_crop=StringVar()
            self.crop_it=StringVar()
            self.cropped_status=Label(self.subcanvas_Cropping,textvariable=self.text_crop)
            self.cropped_status.grid(row=0,column=0, sticky="we")
            self.cropping_button=Button(self.subcanvas_Cropping, textvariable=self.crop_it, command=self.crop_vid)
            self.cropping_button.grid(row=1, column=0, sticky="we")
            self.cropping_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row1"]))
            self.cropping_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            self.bouton_extend_crop=Button(self.subcanvas_Cropping, text=self.Messages["Row0_ExB"], command=self.extend_crop)
            self.bouton_extend_crop.grid(row=2, column=0)
            self.bouton_extend_crop.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row0_Ex"]))
            self.bouton_extend_crop.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            Pos_col+=2

            #Video stabilised
            self.subcanvas_Stab = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='flat')
            self.subcanvas_Stab.grid(row=0,column=Pos_col, sticky="ew")
            self.subcanvas_Stab.columnconfigure(0, weight=1)
            self.subcanvas_Stab.columnconfigure(1, weight=1)
            self.subcanvas_Stab.columnconfigure(0, minsize=150)
            self.text_stab=StringVar()
            self.stab_it=StringVar()
            self.stab_status=Label(self.subcanvas_Stab,textvariable=self.text_stab)
            self.stab_status.grid(row=0,column=0,columnspan=2, sticky="we")
            self.stab_button=Button(self.subcanvas_Stab, textvariable=self.stab_it, command=self.stab_vid)
            self.stab_button.grid(row=1, column=0, sticky="we")
            self.stab_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row2"]))
            self.stab_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            self.check_stab_button=Button(self.subcanvas_Stab, text=self.Messages["RowB1"], command=self.check_stab)
            self.check_stab_button.grid(row=1, column=1, sticky="we")
            self.check_stab_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row3"]))
            self.check_stab_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            self.extend_stab_button=Button(self.subcanvas_Stab, text=self.Messages["RowB17"], command=self.extend_stab)
            self.extend_stab_button.grid(row=2, columnspan=2, sticky="we")
            if self.Video!=None and self.Video.Stab[0]:
                self.extend_stab_button.config(text=self.Messages["RowB18"])

            Pos_col+=2

            #Create background
            self.subcanvas_Back = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='flat')
            self.subcanvas_Back.grid(row=0,column=Pos_col, sticky="ew")
            self.text_back=StringVar()
            self.back_it=StringVar()
            self.back_status=Label(self.subcanvas_Back,textvariable=self.text_back)
            self.back_status.grid(row=0,column=0,columnspan=2, sticky="we")
            self.back_button=Button(self.subcanvas_Back, textvariable=self.back_it, command=self.back_vid)
            self.back_button.grid(row=1, column=0, sticky="we")
            self.back_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row4"]))
            self.back_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            self.back_supress_button=Button(self.subcanvas_Back, text=self.Messages["RowB2"], command=self.supress_back)
            self.back_supress_button.grid(row=1, column=1, sticky="we")
            self.view_back=Canvas(self.subcanvas_Back)
            self.view_back.grid(row=2, column=0, columnspan=2)
            self.view_back.bind("<Enter>", self.show_back)
            self.view_back.bind("<Leave>", self.stop_show_back)
            self.extend_back_button=Button(self.subcanvas_Back, text=self.Messages["RowB19"], command=self.extend_back)
            self.extend_back_button.grid(row=3, column=0, columnspan=2, sticky="we")

            Pos_col+=2

            #Create mask:
            self.subcanvas_Mask = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='flat')
            self.subcanvas_Mask.grid(row=0, column=Pos_col, sticky="ew")
            self.text_mask = StringVar()
            self.mask_it = StringVar()
            self.mask_status = Label(self.subcanvas_Mask, textvariable=self.text_mask)
            self.mask_status.grid(row=0, column=0, columnspan=2, sticky="we")
            self.mask_button = Button(self.subcanvas_Mask, textvariable=self.mask_it, command=self.mask_vid)
            self.mask_button.grid(row=1, column=0, sticky="we")
            self.mask_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row5"]))
            self.mask_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            self.mask_supress_button=Button(self.subcanvas_Mask, text=self.Messages["RowB3"], command=self.supress_mask)
            self.mask_supress_button.grid(row=1, column=1, sticky="we")

            self.view_mask = Canvas(self.subcanvas_Mask)
            self.view_mask.grid(row=2, column=0, columnspan=2)
            self.view_mask.bind("<Enter>", self.show_mask)
            self.view_mask.bind("<Leave>", self.stop_show_mask)

            self.mask_extend_button = Button(self.subcanvas_Mask, text=self.Messages["RowB4"], command=self.extend_mask)
            self.mask_extend_button.grid(row=3, column=0,columnspan=2, sticky="we")
            self.mask_extend_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message,self.Messages["Row6"]))
            self.mask_extend_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            Pos_col+=2

            # Create scale:
            self.subcanvas_Scale = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='flat')
            self.subcanvas_Scale.grid(row=0, column=Pos_col, sticky="ew")
            self.text_scale = StringVar()
            self.scale_it = StringVar()
            self.scale_status = Label(self.subcanvas_Scale, textvariable=self.text_scale)
            self.scale_status.grid(row=0, column=0, columnspan=2, sticky="we")
            self.scale_button = Button(self.subcanvas_Scale, textvariable=self.scale_it, command=self.scale_vid)
            self.scale_button.grid(row=1, column=0, sticky="we")

            self.scale_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message,self.Messages["Row7"]))
            self.scale_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            self.scale_supress_button = Button(self.subcanvas_Scale, text=self.Messages["RowB5"], command=self.supress_scale)
            self.scale_supress_button.grid(row=1, column=1, sticky="we")

            self.scale_extend_button = Button(self.subcanvas_Scale, text=self.Messages["RowB6"], command=self.extend_scale)
            self.scale_extend_button.grid(row=2, column=0,columnspan=2, sticky="we")
            self.scale_extend_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message,self.Messages["Row8"]))
            self.scale_extend_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            Pos_col+=2

            #Aerate a little !
            self.grid_columnconfigure(0,minsize=200)
            for row in range(Pos_col):
                self.canvas_main.grid_columnconfigure(row, minsize=20)

            if self.Video!=None:
                self.update_mask()
                self.update_repre()
                self.update_crop()
                self.update_stab()
                self.update_back()
                self.update_scale()
                self.update_size()
                self.update_fps()
                self.update_name()

            self.File_name_ent.bind('<Configure>', self.resize_font)


    def change_vid(self,new_vid,proj_pos):
        self.Video = new_vid
        self.proj_pos = proj_pos
        self.sBsupr.config(command=partial(self.main_frame.supr_video, self.Video))
        self.Bcopy.config(command=partial(self.main_frame.dupli_video, self.Video))
        self.File_name_var.set(self.Video.User_Name)
        self.update()

    def concat(self):
        self.main_frame.selected_vid=self.Video
        self.main_frame.fus_video()
        self.main_frame.update_selections()
        self.isselected.config(bg="blue")
        self.main_frame.HW.change_default_message(self.Messages["General16"])
        self.main_frame.HW.change_tmp_message(self.Messages["General16"])

    def Reset_name(self):
        self.File_name_var.set(self.Video.Name)

    def change_vid_name(self, var, indx, mode):
        self.resize_font("")
        if self.File_name_var.get() not in [Vid.User_Name for Vid in self.main_frame.liste_of_videos if Vid != self.Video] and self.File_name_var.get()!="":
            self.Video.User_Name = self.File_name_var.get()
            self.File_name_ent.config(bg="white")
        else:
            self.File_name_ent.config(bg="red")

    def ask_clear_data(self, event):
        '''Display a warning message to the user to ensure that he agrees on deleting the data'''
        if self.Video.Tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response:
                self.Video.clear_files()
            self.update()

    def resize_font(self, _):
        '''Change the size of the displayed name of the video (according to the length of the title)'''
        height=12
        self.font['size'] = height
        while self.font.measure(self.File_name_var.get())>200 and height>7:
            self.font['size'] = height
            height -= 1
        self.File_name_ent.grid_forget()
        self.File_name_ent.grid(row=0, column=2, sticky="nsew")

    def update_size(self):
        '''If we resize the main windows, we update the size of the canvas.'''
        self.canvas_main.config(width=self.parent.master.winfo_width()-self.subcanvas_First.winfo_width()-50)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame.'''
        self.canvas_main.configure(scrollregion=self.canvas_main.bbox("all"))

    def update_repre(self):
        '''Update the name of the video.'''
        self.File_name_var.set(self.Video.User_Name)

    def show_first(self, *arg):
        '''Display the first image of the video in a temporary window.'''
        self.main_frame.HW.change_tmp_message(self.Messages["Row9"])
        cv2.namedWindow(" ")  # Create a named window
        ratio = self.width_show / self.Video.or_shape[1]
        X_Cur=self.master.winfo_pointerx()
        Y_Cur = self.master.winfo_pointery()

        #To avoid the image to appear above the cursor
        if X_Cur<50+self.width_show+100 and Y_Cur<50+self.Video.or_shape[0]*ratio:
            X_Pos=X_Cur+100
        else:
            X_Pos=50
        cv2.moveWindow(" ", X_Pos, 50)
        capture = cv2.VideoCapture(self.Video.File_name)#Faster with opencv
        _, Represent = capture.read()
        capture.release()
        cv2.imshow(" ",cv2.resize(Represent,(int(self.Video.or_shape[1]*ratio),int(self.Video.or_shape[0]*ratio))))
        cv2.waitKey(1)


    def stop_show_first(self, *arg):
        '''Stop the display of the first image.'''
        self.main_frame.HW.remove_tmp_message()
        cv2.destroyAllWindows()

    def select_vid(self,*args):
        '''When the user select a video.'''
        if not self.main_frame.wait_for_vid:
            self.main_frame.selected_vid=self.Video
            self.main_frame.update_selections()
            self.main_frame.moveX()
        else:
            self.main_frame.fusion_two_Vids(self.Video)
            self.main_frame.update_selections()

    def update_fps(self):
        # We change the displayed fps
        self.Fr_rate = [-1, -1]
        if self.Video != None:
            self.Fr_rate[0] = self.Video.Frame_rate[0]
            self.Fr_rate[1] = self.Video.Frame_rate[1]

        self.List_poss_FrRate = [self.Messages["RowL12"] + " " + str(round(self.Fr_rate[0], 2))]
        value = self.Fr_rate[0]
        while value > 1:
            value = value / 2
            self.List_poss_FrRate.append(round(value, 2))

        menu = self.bouton_Fr_rate["menu"]
        menu.delete(0, "end")
        for elem in self.List_poss_FrRate:
            menu.add_command(label=elem, command=lambda value=elem: self.change_fps(value))

        self.bouton_Fr_rate.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message,self.Messages["Row0"].format(round(self.Fr_rate[1], 2))))

        if self.Fr_rate[0] == self.Fr_rate[1]:
            self.holder.set(self.Messages["RowL12"] + " " + str(round(self.Fr_rate[0], 2)))
        else:
            self.holder.set(self.Fr_rate[1])

    def change_fps(self, choice):
        # We change the frame rate
        if choice==self.List_poss_FrRate[0]:
            self.Video.Frame_rate[1]=self.Video.Frame_rate[0]
        else:
            self.Video.Frame_rate[1] = choice

        one_every=int(round(round(self.Video.Frame_rate[0]) / self.Video.Frame_rate[1]))

        self.Video.Cropped[1][0]= int(math.floor(self.Video.Cropped[1][0]/one_every) * one_every)#Avoid to try to open un-existing frames after changes in frame-rate
        self.Video.Cropped[1][1] = int(math.floor(self.Video.Cropped[1][1]/one_every) * one_every)

        self.Video.Frame_nb[1] = int(self.Video.Frame_nb[0] / round(self.Video.Frame_rate[0] / self.Video.Frame_rate[1]))
        self.update()
        self.bouton_Fr_rate.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row0"].format(round(self.Video.Frame_rate[1], 2))))


    def extend_change_fps(self):
        # Open a new window to extend the frame rate at several videos
        ratio=round(self.Video.Frame_rate[0] / self.Video.Frame_rate[1])
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=ratio, boss=self.main_frame, Video_file=self.Video, type="fps")

    def update_crop(self):
        # Show the details about video duration (with cropping) and spatial cropping
        if self.Video.Cropped[0] and self.Video.Cropped_sp[0]:
            self.cropping_button.config(bg="#3aa6ff")
            one_every = int(round(round(self.Video.Frame_rate[0], 2) / self.Video.Frame_rate[1]))
            self.text_crop.set(self.Messages["RowL1"].format(int(self.Video.Cropped[1][0]/one_every), round((self.Video.Cropped[1][0]/one_every) / self.Video.Frame_rate[1],2), \
                                                             int((self.Video.Cropped[1][1]/one_every)), round((int(self.Video.Cropped[1][1]/one_every)+1)/ self.Video.Frame_rate[1],2), \
                                                            int(self.Video.Cropped[1][1]/one_every) - int(self.Video.Cropped[1][0]/one_every) + 1, \
                                                             round((int(self.Video.Cropped[1][1]/one_every) - int(self.Video.Cropped[1][0]/one_every) +1) / self.Video.Frame_rate[1],2)))
            self.crop_it.set(self.Messages["RowB7"])

        elif self.Video.Cropped[0] and not self.Video.Cropped_sp[0]:
            self.cropping_button.config(bg="#bfe62b")
            one_every = int(round(round(self.Video.Frame_rate[0], 2) / self.Video.Frame_rate[1]))
            self.text_crop.set(self.Messages["RowL1"].format(int(self.Video.Cropped[1][0]/one_every), round((self.Video.Cropped[1][0]/one_every) / self.Video.Frame_rate[1],2), \
                                                             int((self.Video.Cropped[1][1]/one_every)), round((int(self.Video.Cropped[1][1]/one_every)+1)/ self.Video.Frame_rate[1],2), \
                                                            int(self.Video.Cropped[1][1]/one_every) - int(self.Video.Cropped[1][0]/one_every) + 1, \
                                                             round((int(self.Video.Cropped[1][1]/one_every) - int(self.Video.Cropped[1][0]/one_every) +1) / self.Video.Frame_rate[1],2)))
            self.crop_it.set(self.Messages["RowB7"])

        elif not self.Video.Cropped[0] and self.Video.Cropped_sp[0]:
            self.cropping_button.config(bg="#bfe62b")
            self.text_crop.set(self.Messages["RowL2"].format(self.Video.Frame_nb[1], round(self.Video.Frame_nb[1] / self.Video.Frame_rate[1],2)))
            self.crop_it.set(self.Messages["RowB8"])
            self.update_repre()
            self.update_back()
        else:
            self.cropping_button.config(bg="#ff8a33")
            self.text_crop.set(self.Messages["RowL2"].format(self.Video.Frame_nb[1], round(self.Video.Frame_nb[1] / self.Video.Frame_rate[1],2)))
            self.crop_it.set(self.Messages["RowB8"])

        if self.Video.Tracked:
            self.cropping_button.config(bg="SystemButtonFace")


    def crop_vid(self, speed=0):
        # Open the cropping window
        if self.Video.Tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])#Remove the
            if response and self.Video.clear_files():
                self.main_frame.Change_win(Interface_cropping.Cropping(parent=self.main_frame.canvas_main, boss=self, main_frame=self.main_frame, proj_pos=self.proj_pos, Video_file=self.Video, speed=speed))
        else:
            self.main_frame.Change_win(
                Interface_cropping.Cropping(parent=self.main_frame.canvas_main, boss=self, main_frame=self.main_frame, proj_pos=self.proj_pos, Video_file=self.Video, speed=speed))


    def extend_crop(self):
        # Open a new window to extend the frame rate at several videos
        crop=[self.Video.Cropped.copy(), self.Video.Cropped_sp.copy()]
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=crop, boss=self.main_frame, Video_file=self.Video, type="crop")

    def update(self):
        #Update the states of the video
        self.main_frame.Change_win
        self.update_scale()
        self.update_stab()
        self.update_mask()
        self.update_back()
        self.update_crop()
        self.update_fps()
        self.update_name()
        self.update_selection()

    def update_selection(self):
        #Change the color/shape of the row to indicate it is/is not selected
        if self.main_frame.selected_vid==self.Video:
            self.isselected.config(bg="#6AED35")
            self.config(bd=10, relief="ridge", highlightthickness=3)
        else:
            self.isselected.config(bg="red")
            self.config(bd=1, relief="ridge", highlightthickness=1)


    def update_stab(self):
        # Update the color/info of the stabilisation cell
        if self.Video.Stab[0]:
            self.stab_button.config(bg="#3aa6ff")
            self.text_stab.set(self.Messages["RowL3"])
            self.stab_it.set(self.Messages["RowB9"])
            self.check_stab_button.config(state="active")
            self.extend_stab_button.config(text=self.Messages["RowB17"])
        else:
            self.stab_button.config(bg="#ff8a33")
            self.text_stab.set(self.Messages["RowL4"])
            self.stab_it.set(self.Messages["RowB10"])
            self.check_stab_button.config(state="disable")
            self.extend_stab_button.config(text=self.Messages["RowB18"])

        if self.Video.Tracked:
            self.stab_button.config(bg="SystemButtonFace")

    def stab_vid(self):
        # Add/Remove the stabilization
        if self.Video.Tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response and self.Video.clear_files():
                    if self.Video.Stab[0]:
                        self.Video.Stab[0]=False
                    else:
                        self.Video.Stab[0]=True
        else:
            if self.Video.Stab[0]:
                self.Video.Stab[0] = False
            else:
                self.Video.Stab[0] = True
        self.update()

    def check_stab(self, speed=0):
        #Speed is the video reader speed, to avoid that user need to change it each time between videos
        #Open the window to change the parameters of the stabilization
        if self.Video.Tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])#Remove the
            if response and self.Video.clear_files():
                self.main_frame.Change_win(Interface_stabilis.Stabilise(parent=self.main_frame.canvas_main, boss=self, main_frame=self.main_frame, Video_file=self.Video, speed=speed))
        else:
            self.main_frame.Change_win(
                Interface_stabilis.Stabilise(parent=self.main_frame.canvas_main, boss=self, main_frame=self.main_frame, Video_file=self.Video, speed=speed))

    def extend_stab(self):
        # Open a window to expend the stabilization to other videos
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Video.Stab, boss=self.main_frame, Video_file=self.Video, do_self=False, type="stab")

    def back_vid(self):
        # Create the automatique background or open the window to change an existing background
        if self.Video.Tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response and self.Video.clear_files():
                if not self.Video.Back[0]:
                    self.Video.make_back()
                    self.update_back()

                elif self.Video.Back[0]:
                    self.main_frame.Change_win(Interface_back.Background(parent=self.main_frame.canvas_main, boss=self,
                                                                         main_frame=self.main_frame, Video_file=self.Video))

        else:
            if not self.Video.Back[0]:
                self.Video.make_back()
                self.update_back()

            elif self.Video.Back[0]:
                self.main_frame.Change_win(Interface_back.Background(parent=self.main_frame.canvas_main, boss=self,
                                                                     main_frame=self.main_frame, Video_file=self.Video))
        self.update()

    def update_name(self):
        if self.Video.Tracked:
            self.File_name_ent.config(state="disable")
            self.BReset_name.config(state="disable")
        else:
            self.File_name_ent.config(state="normal")
            self.BReset_name.config(state="active")

    def update_back(self):
        # Update the color/info of the background cell
        if not self.Video.Back[0]:
            self.text_back.set(self.Messages["RowL5"])
            self.back_it.set(self.Messages["RowB11"])
            self.back_button.config( bg="#ff8a33")
            self.back_supress_button.config(state="disable")
            self.view_back.create_image(0, 0, image=self.oeuilB2, anchor=NW)
            self.view_back.config(width=int(self.Size_oe[1]/4), height=int(self.Size_oe[0]/4))
        else:
            self.text_back.set(self.Messages["RowL6"])
            self.back_it.set(self.Messages["RowB12"])
            self.back_button.config( bg="#3aa6ff")
            self.back_supress_button.config(state="active")
            self.view_back.create_image(0, 0, image=self.oeuil2, anchor=NW)
            self.view_back.config(width=int(self.Size_oe[1]/4), height=int(self.Size_oe[0]/4))

        if self.Video.Tracked:
            self.back_button.config(bg="SystemButtonFace")
            self.back_supress_button.config(bg='SystemButtonFace')

    def supress_back(self):
        # Remove existing background
        if self.Video.Tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response and self.Video.clear_files():
                self.Video.effacer_back()
                self.update()
        else:
            self.Video.effacer_back()
            self.update_back()

    def show_back(self, *arg):
        # Display an image of the background on a temporary window
        if self.Video.Back[0]:
            self.main_frame.HW.change_tmp_message(self.Messages["Row14"])
            cv2.namedWindow(" ")
            ratio = self.width_show / self.Video.shape[1]
            X_Cur = self.master.winfo_pointerx()
            Y_Cur = self.master.winfo_pointery()
            #To avoid that the window appears on the top of the cursor
            if X_Cur < 50 + self.width_show + 100 and Y_Cur < 50 + self.Video.shape[0] * ratio:
                X_Pos = X_Cur + 100
            else:
                X_Pos = 50
            cv2.moveWindow(" ", X_Pos, 50)
            cv2.imshow(" ",cv2.resize(self.Video.Back[1],(int(self.Video.shape[1]*ratio),int(self.Video.shape[0]*ratio))))
            cv2.waitKey(1)

    def stop_show_back(self, *arg):
        # Remove the displayed image of the background
        self.main_frame.HW.remove_tmp_message()
        if self.Video.Back[0]:
            cv2.destroyAllWindows()

    def extend_back(self):
        # Open a new window to extend the automatique background at several videos
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=None, boss=self.main_frame, Video_file=self.Video, do_self=True, type="back")

    def update_mask(self):
        # Update the color/info of the arenas cell
        if not self.Video.Mask[0]:
            self.text_mask.set(self.Messages["RowL7"])
            self.mask_it.set(self.Messages["RowB13"])
            self.mask_button.config( bg="#ff8a33")
            self.mask_supress_button.config(state="disable")
            self.mask_extend_button.config(state="disable")
            self.view_mask.create_image(0, 0, image=self.oeuilB2, anchor=NW)
            self.view_mask.config(width=int(self.Size_oe[1]/4), height=int(self.Size_oe[0]/4))
        else:
            self.text_mask.set(self.Messages["RowL8"])
            self.mask_it.set(self.Messages["RowB14"])
            self.mask_button.config( bg="#3aa6ff")
            self.mask_supress_button.config(state="active")
            self.mask_extend_button.config(state="active")
            self.view_mask.create_image(0, 0, image=self.oeuil2, anchor=NW)
            self.view_mask.config(width=int(self.Size_oe[1]/4), height=int(self.Size_oe[0]/4))
        if self.Video.Tracked:
            self.mask_button.config(bg="SystemButtonFace")
            self.mask_supress_button.config(bg='SystemButtonFace')

    def supress_mask(self):
        # Remove existing arenas
        if self.Video.Tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response and self.Video.clear_files():
                self.Video.effacer_mask()
                self.update()
        else:
            self.Video.effacer_mask()
            self.update_mask()

    def mask_vid(self):
        # Open the window to define the arenas in which the targets can be found
        if self.Video.Tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response and self.Video.clear_files():
                self.main_frame.Change_win(Interface_arenas.Mask(parent=self.main_frame.canvas_main,
                                                                  boss=self, main_frame=self.main_frame, proj_pos=self.proj_pos, Video_file=self.Video))
                self.update()
        else:
            self.main_frame.Change_win(
                Interface_arenas.Mask(parent=self.main_frame.canvas_main, boss=self, main_frame=self.main_frame,
                                       proj_pos=self.proj_pos, Video_file=self.Video))
            self.update()

    def show_mask(self, *arg):
        # Display a temporary image of the image with the arenas visible
        if self.Video.Mask[0]:
            Which_part = 0
            if self.Video.Cropped[0]:
                if len(self.Video.Fusion) > 1:  # If there was a concatenation
                    Which_part = [index for index, Fu_inf in enumerate(self.Video.Fusion) if Fu_inf[0] <= self.Video.Cropped[1][0]][-1]

            capture = cv2.VideoCapture(self.Video.Fusion[Which_part][1])  # Faster with opencv
            capture.set(cv2.CAP_PROP_POS_FRAMES, self.Video.Cropped[1][0] - self.Video.Fusion[Which_part][0])
            _, self.Represent = capture.read()
            capture.release()

            self.main_frame.HW.change_tmp_message(self.Messages["Row15"])
            cv2.namedWindow(" ")  # Create a named window
            ratio = self.width_show / self.Video.shape[1]

            #To avoid the window to appear on the top of the cursor
            X_Cur = self.master.winfo_pointerx()
            Y_Cur = self.master.winfo_pointery()
            if X_Cur < 50 + self.width_show + 100 and Y_Cur < 50 + self.Video.shape[0] * ratio:
                X_Pos = X_Cur + 100
            else:
                X_Pos = 50
            cv2.moveWindow(" ", X_Pos, 50)
            mask = Dr.draw_mask(self.Video)

            if self.Video.Back[0]:#Create the image
                mask_to_show=cv2.bitwise_and(self.Video.Back[1],self.Video.Back[1],mask=mask)
            else:
                if self.Video.Cropped_sp[0]:
                    repre_c = self.Represent[self.Video.Cropped_sp[1][0]:self.Video.Cropped_sp[1][2], self.Video.Cropped_sp[1][1]:self.Video.Cropped_sp[1][3]]
                    mask_to_show=cv2.bitwise_and(repre_c,repre_c,mask=mask)
                else:
                    mask_to_show=cv2.bitwise_and(self.Represent,self.Represent,mask=mask)
            cv2.imshow(" ",cv2.resize(mask_to_show,(int(self.Video.shape[1]*ratio),int(self.Video.shape[0]*ratio))))
            cv2.waitKey(1)

    def stop_show_mask(self, *arg):
        # Remove the temporary image with arenas
        self.main_frame.HW.remove_tmp_message()
        if self.Video.Mask[0]:
            cv2.destroyAllWindows()

    def extend_mask(self):
        # Open a window to expend the position of the arenas to other videos
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Video.Mask[1], boss=self.main_frame, Video_file=self.Video, type="mask")

    def update_scale(self):
        # Update the color/info of the scale cell
        if self.Video.Scale[0] == 1:
            self.text_scale.set(self.Messages["RowL9"])
            self.scale_it.set(self.Messages["RowB15"])
            self.scale_button.config(bg="#ff8a33")
            self.scale_supress_button.config(state="disable")
            self.scale_extend_button.config(state="disable")
        else:
            self.text_scale.set(self.Messages["RowL10"].format(self.Video.Scale[0],self.Video.Scale[1]))
            self.scale_it.set(self.Messages["RowB16"])
            self.scale_button.config(bg="#3aa6ff")
            self.scale_supress_button.config(state="active")
            self.scale_extend_button.config(state="active")
        if self.Video.Tracked:
            self.scale_button.config(bg="SystemButtonFace")
            self.scale_button.config(bg="SystemButtonFace")

    def supress_scale(self):
        # Remove the scale associated with the video
        if self.Video.Tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response and self.Video.clear_files():
                self.Video.Scale[0] = 1
                self.Video.Scale[1] = ""
                self.update_scale()
        else:
            self.Video.Scale[0]=1
            self.Video.Scale[1] = ""
            self.update_scale()

    def scale_vid(self):
        # Open the window in which the scale can be defined
        if self.Video.Tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response and self.Video.clear_files():
                self.main_frame.Change_win(Interface_scaling.Scale(parent=self.main_frame.canvas_main, boss=self,
                                                                   main_frame=self.main_frame, Video_file=self.Video))
        else:
            self.main_frame.Change_win(Interface_scaling.Scale(parent=self.main_frame.canvas_main, boss=self,
                                                               main_frame=self.main_frame, Video_file=self.Video))

    def extend_scale(self):
        # Open a window to expend the scale of this video to others
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Video.Scale, boss=self.main_frame, Video_file=self.Video, type="scale")
