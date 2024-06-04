import math
import os
from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
from functools import partial
from AnimalTA.A_General_tools import Function_draw_mask as Dr, Interface_extend, UserMessages, Color_settings, Message_simple_question as MsgBox
from AnimalTA.C_Pretracking import Interface_cropping, Interface_back, Interface_arenas, Interface_scaling, \
    Interface_stabilis
from AnimalTA.B_Project_organisation import Interface_supp_frame_rate
from tkinter import font
from tkinter import filedialog
import pickle

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
            self.config(width=500,**Color_settings.My_colors.Frame_Base, pady=2)

            self.list_colors = Color_settings.My_colors.list_colors

            Grid.columnconfigure(self, 0, weight=1)
            Grid.columnconfigure(self, 1, weight=100)


            Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
            with open(Param_file, 'rb') as fp:
                self.Params = pickle.load(fp)

            self.width_show = self.Params["Size_img_display"]  # How big are the displayed frames


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

            self.Supr_im = PIL.Image.open(UserMessages.resource_path(os.path.join("AnimalTA","Files","cross.png")))
            self.Supr_im = PIL.ImageTk.PhotoImage(self.Supr_im)

            self.Copy_im = PIL.Image.open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Copy.png")))
            self.Copy_im = PIL.ImageTk.PhotoImage(self.Copy_im)

            self.Concat_im = PIL.Image.open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Concat.png")))
            self.Concat_im = PIL.ImageTk.PhotoImage(self.Concat_im)

            #Video name and representation:
            self.subcanvas_First = Canvas(self, bd=0, highlightthickness=0, relief='flat', width=275, height=10,**Color_settings.My_colors.Frame_Base)
            self.subcanvas_First.grid(row=0,column=0, sticky="snwe")
            self.subcanvas_First.grid_propagate(0)
            Grid.columnconfigure(self.subcanvas_First, 0, weight=1)
            Grid.columnconfigure(self.subcanvas_First, 1, weight=1)
            Grid.columnconfigure(self.subcanvas_First, 2, weight=100)
            Grid.rowconfigure(self.subcanvas_First, 0, weight=1)
            Grid.rowconfigure(self.subcanvas_First, 1, weight=1)

            #If the video is selected, this appears green
            self.isselected=Canvas(self.subcanvas_First,heigh=75, width=15, bg=self.list_colors["Not_selected_main"],**Color_settings.My_colors.Frame_Base)
            self.isselected.grid(row=0,column=0, sticky="nsw")
            self.isselected.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row9"]))
            self.isselected.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            #The name of the video is displayed and can be changed by the user
            self.File_name_lab = Label(self.subcanvas_First, text=self.Messages["Video"] + ": ", font=font.Font(self.master, family='Arial', size=12, weight='bold'),**Color_settings.My_colors.Label_Base)
            self.File_name_lab.grid(row=0,column=1, sticky="nsw")
            self.File_name_lab.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row9"]))
            self.File_name_lab.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            self.File_name_var = StringVar()
            self.File_name_var.trace_add('write', self.change_vid_name)
            self.File_name_ent=Entry(self.subcanvas_First, textvariable=self.File_name_var, font= ('Arial', 12, 'bold'), **Color_settings.My_colors.Entry_Base)
            self.File_name_ent.grid(row=0,column=2, sticky="nsew")
            self.File_name_ent.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row17"]))
            self.File_name_ent.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            #Button to reset the name of the video to its original value (i.e. file name)
            self.BReset_name=Button(self.subcanvas_First,text="x", command=self.Reset_name,**Color_settings.My_colors.Button_Base)
            self.BReset_name.grid(row=0,column=3, sticky="nsew")
            self.BReset_name.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row16"]))
            self.BReset_name.bind("<Leave>", self.main_frame.HW.remove_tmp_message)


            #Add three buttons:
            Three_buttons=Frame(self.subcanvas_First,**Color_settings.My_colors.Frame_Base)
            Three_buttons.grid(row=1,column=0,columnspan=2)

            #Suppress the video
            self.sBsupr=Button(Three_buttons, image=self.Supr_im, command=partial(self.main_frame.supr_video, self.Video), width=22, height=22)
            self.sBsupr.grid(row=0,column=0)
            self.sBsupr.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["GButton8"]))
            self.sBsupr.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            self.sBsupr.config(**Color_settings.My_colors.Button_Base)

            #Duplicate the video
            self.Bcopy=Button(Three_buttons, image=self.Copy_im, command=partial(self.main_frame.dupli_video, self.Video), width=22, height=22)
            self.Bcopy.grid(row=0,column=1)
            self.Bcopy.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["General21"]))
            self.Bcopy.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            self.Bcopy.config(**Color_settings.My_colors.Button_Base)

            #Concatenate the video
            Bconcat=Button(Three_buttons, image=self.Concat_im, command=self.concat, width=22, height=22)
            Bconcat.grid(row=0,column=2)
            Bconcat.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["General15"]))
            Bconcat.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            Bconcat.config(**Color_settings.My_colors.Button_Base)

            self.view_and_rot=Frame(self.subcanvas_First,**Color_settings.My_colors.Frame_Base)
            self.view_and_rot.grid(row=1, column=2)

            self.view_first = Canvas(self.view_and_rot, **Color_settings.My_colors.Frame_Base)


            #we allow to roatet the video
            self.Rotate_clock = Button(self.view_and_rot, text="⤹", command=partial(self.rotate, -1),**Color_settings.My_colors.Button_Base)
            self.Rotate_clock.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row21"]))
            self.Rotate_clock.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            self.Rotate_clock.grid(row=0, column=0, sticky="e")

            self.Rotate_clockanti = Button(self.view_and_rot, text="⤸", command=partial(self.rotate, 1),**Color_settings.My_colors.Button_Base)
            self.Rotate_clockanti.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row21"]))
            self.Rotate_clockanti.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            self.Rotate_clockanti.grid(row=0, column=2, sticky="w")

            #Options of pretracking:
            self.Wrapper=Canvas(self, heigh = 125, relief='ridge',**Color_settings.My_colors.Frame_Base)
            self.Wrapper.grid(row=0, column=1, sticky="ew")
            self.canvas_main = Frame(self.Wrapper, heigh = 125, relief='ridge',**Color_settings.My_colors.Frame_Base)
            self.canvas_main.grid(row=0, column=0, sticky="ew")

            Pos_col=1
            #Frame_rate
            self.subcanvas_Fr_rate = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='flat',**Color_settings.My_colors.Frame_Base)
            self.subcanvas_Fr_rate.grid(row=0,column=Pos_col, sticky="we")
            self.subcanvas_Fr_rate.columnconfigure(0,weight=1)
            self.Frame_rate_status=Label(self.subcanvas_Fr_rate,text=self.Messages["RowL11"], **Color_settings.My_colors.Label_Base)
            self.Frame_rate_status.grid(row=0,column=0, sticky="we")

            self.Fr_rate=[60,60]
            self.Fr_nb=1
            if self.Video!=None:#In some cases we won't have a video set while creating the row(will never be shown to user)
                self.Fr_rate[0]=self.Video.Frame_rate[0]
                self.Fr_rate[1] = self.Video.Frame_rate[1]
                self.Fr_nb = self.Video.Frame_nb[0]


            self.List_poss_FrRate =[self.Messages["RowL12"]+ " " +str(round(self.Fr_rate[0],2))]
            value=self.Fr_rate[0]
            while value > 0.01 and (self.Fr_nb / round(self.Fr_rate[0] / value))>50: #We put a minimum number of frames displayed per video to avoid later problems
                value=value/2
                if value>1:
                    self.List_poss_FrRate.append(round(value,2))
                elif value>0.1:# we adapt the round to the value size
                    self.List_poss_FrRate.append(round(value, 3))
                else:
                    self.List_poss_FrRate.append(round(value, 4))
            self.holder=StringVar()

            if self.Fr_rate[0]==self.Fr_rate[1]:
                self.holder.set(self.Messages["RowL12"]+ " " +str(round(self.Fr_rate[0],2)))
            else:
                self.holder.set(self.Fr_rate[1])
            self.bouton_Fr_rate = OptionMenu(self.subcanvas_Fr_rate, self.holder, *self.List_poss_FrRate, command=self.change_fps)
            self.bouton_Fr_rate["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
            self.bouton_Fr_rate.config(**Color_settings.My_colors.Button_Base)
            self.bouton_Fr_rate.grid(row=1, column=0, sticky="we")
            self.bouton_Fr_rate.bind("<Button-1>",self.ask_clear_data)
            self.bouton_Fr_rate.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row0"].format(round(self.Fr_rate[1],2))))
            self.bouton_Fr_rate.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            self.bouton_extend_Fr_rate=Button(self.subcanvas_Fr_rate, text=self.Messages["Row0_ExB"], command=self.extend_change_fps, **Color_settings.My_colors.Button_Base)
            self.bouton_extend_Fr_rate.grid(row=2, column=0)
            self.bouton_extend_Fr_rate.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row0_Ex"]))
            self.bouton_extend_Fr_rate.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            Pos_col+=2

            #Video cropped
            self.subcanvas_Cropping = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='flat', **Color_settings.My_colors.Frame_Base)
            self.subcanvas_Cropping.grid(row=0,column=Pos_col, sticky="we")
            self.subcanvas_Cropping.columnconfigure(0,weight=1)
            self.text_crop=StringVar()
            self.crop_it=StringVar()
            self.cropped_status=Label(self.subcanvas_Cropping,textvariable=self.text_crop, **Color_settings.My_colors.Label_Base)
            self.cropped_status.grid(row=0,column=0, sticky="we")
            self.cropping_button=Button(self.subcanvas_Cropping, textvariable=self.crop_it, command=self.crop_vid, **Color_settings.My_colors.Button_Base)
            self.cropping_button.grid(row=1, column=0, sticky="we")
            self.cropping_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row1"]))
            self.cropping_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            self.bouton_extend_crop=Button(self.subcanvas_Cropping, text=self.Messages["Row0_ExB"], command=self.extend_crop, **Color_settings.My_colors.Button_Base)
            self.bouton_extend_crop.grid(row=2, column=0)
            self.bouton_extend_crop.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row0_Ex"]))
            self.bouton_extend_crop.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            Pos_col+=2

            #Video stabilised
            self.subcanvas_Stab = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='flat', **Color_settings.My_colors.Frame_Base)
            self.subcanvas_Stab.grid(row=0,column=Pos_col, sticky="ew")
            self.subcanvas_Stab.columnconfigure(0, weight=1)
            self.subcanvas_Stab.columnconfigure(1, weight=1)
            self.subcanvas_Stab.columnconfigure(0, minsize=150)
            self.text_stab=StringVar()
            self.stab_it=StringVar()
            self.stab_status=Label(self.subcanvas_Stab,textvariable=self.text_stab, **Color_settings.My_colors.Label_Base)
            self.stab_status.grid(row=0,column=0,columnspan=2, sticky="we")
            self.stab_button=Button(self.subcanvas_Stab, textvariable=self.stab_it, command=self.stab_vid, **Color_settings.My_colors.Button_Base)
            self.stab_button.grid(row=1, column=0, sticky="we")
            self.stab_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row2"]))
            self.stab_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            self.check_stab_button=Button(self.subcanvas_Stab, text=self.Messages["RowB1"], command=self.check_stab, **Color_settings.My_colors.Button_Base)
            self.check_stab_button.grid(row=1, column=1, sticky="we")
            self.check_stab_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row3"]))
            self.check_stab_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            self.extend_stab_button=Button(self.subcanvas_Stab, text=self.Messages["RowB17"], command=self.extend_stab, **Color_settings.My_colors.Button_Base)
            self.extend_stab_button.grid(row=2, columnspan=2, sticky="we")
            if self.Video!=None and self.Video.Stab[0]:
                self.extend_stab_button.config(text=self.Messages["RowB18"])

            Pos_col+=2

            #Create background
            self.subcanvas_Back = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='flat', **Color_settings.My_colors.Frame_Base)
            self.subcanvas_Back.grid(row=0,column=Pos_col, sticky="ew")
            self.text_back=StringVar()
            self.back_it=StringVar()
            self.back_status=Label(self.subcanvas_Back,textvariable=self.text_back, **Color_settings.My_colors.Label_Base)
            self.back_status.grid(row=0,column=0,columnspan=2, sticky="we")
            self.back_button=Button(self.subcanvas_Back, textvariable=self.back_it, command=self.back_vid, **Color_settings.My_colors.Button_Base)
            self.back_button.grid(row=1, column=0, sticky="we")
            self.back_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row4"]))
            self.back_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            self.back_supress_button=Button(self.subcanvas_Back, text=self.Messages["RowB2"], command=self.supress_back, **Color_settings.My_colors.Button_Base)
            self.back_supress_button.grid(row=1, column=1, sticky="we")

            Frame_view_back=Frame(self.subcanvas_Back, **Color_settings.My_colors.Frame_Base)
            Frame_view_back.grid(row=2, column=0, columnspan=2)
            self.view_back=Canvas(Frame_view_back, **Color_settings.My_colors.Frame_Base)
            self.view_back.grid(row=0, column=0)
            self.view_back.bind("<Enter>", self.show_back)
            self.view_back.bind("<Leave>", self.stop_show_back)
            self.save_back_button= Button(Frame_view_back, text="\U0001f4be", command=self.save_back_img, borderwidth=0, **Color_settings.My_colors.Button_Base)
            self.save_back_button.grid(row=0, column=1)
            self.save_back_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message,self.Messages["Row18"]))
            self.save_back_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            #"Add here an explanation about saving the back"
            self.extend_back_button=Button(self.subcanvas_Back, text=self.Messages["RowB19"], command=self.extend_back, **Color_settings.My_colors.Button_Base)
            self.extend_back_button.grid(row=3, column=0, columnspan=2, sticky="we")

            Pos_col+=2

            #Create mask:
            self.subcanvas_Mask = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='flat', **Color_settings.My_colors.Frame_Base)
            self.subcanvas_Mask.grid(row=0, column=Pos_col, sticky="ew")
            self.text_mask = StringVar()
            self.mask_it = StringVar()
            self.mask_status = Label(self.subcanvas_Mask, textvariable=self.text_mask, **Color_settings.My_colors.Label_Base)
            self.mask_status.grid(row=0, column=0, columnspan=2, sticky="we")
            self.mask_button = Button(self.subcanvas_Mask, textvariable=self.mask_it, command=self.mask_vid, **Color_settings.My_colors.Button_Base)
            self.mask_button.grid(row=1, column=0, sticky="we")
            self.mask_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row5"]))
            self.mask_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)

            self.mask_supress_button=Button(self.subcanvas_Mask, text=self.Messages["RowB3"], command=self.supress_mask, **Color_settings.My_colors.Button_Base)
            self.mask_supress_button.grid(row=1, column=1, sticky="we")

            Frame_view_mask=Frame(self.subcanvas_Mask, **Color_settings.My_colors.Frame_Base)
            Frame_view_mask.grid(row=2, column=0, columnspan=2)
            self.view_mask = Canvas(Frame_view_mask, **Color_settings.My_colors.Frame_Base)
            self.view_mask.grid(row=0, column=0)
            self.view_mask.bind("<Enter>", self.show_mask)
            self.view_mask.bind("<Leave>", self.stop_show_mask)
            # "Add here an explanation about saving the arena image"
            self.save_mask_button= Button(Frame_view_mask, text="\U0001f4be", command=self.save_are_img, borderwidth=0, **Color_settings.My_colors.Button_Base)
            self.save_mask_button.grid(row=0, column=1)
            self.save_mask_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message,self.Messages["Row19"]))
            self.save_mask_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)


            self.mask_extend_button = Button(self.subcanvas_Mask, text=self.Messages["RowB4"], command=self.extend_mask, **Color_settings.My_colors.Button_Base)
            self.mask_extend_button.grid(row=3, column=0,columnspan=2, sticky="we")
            self.mask_extend_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message,self.Messages["Row6"]))
            self.mask_extend_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            Pos_col+=2

            # Create scale:
            self.subcanvas_Scale = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='ridge', **Color_settings.My_colors.Frame_Base)
            self.subcanvas_Scale.grid(row=0, column=Pos_col, sticky="ew")
            self.text_scale = StringVar()
            self.scale_it = StringVar()
            self.scale_status = Label(self.subcanvas_Scale, textvariable=self.text_scale, **Color_settings.My_colors.Label_Base)
            self.scale_status.grid(row=0, column=0, columnspan=2, sticky="we")
            self.scale_button = Button(self.subcanvas_Scale, textvariable=self.scale_it, command=self.scale_vid, **Color_settings.My_colors.Button_Base)
            self.scale_button.grid(row=1, column=0, sticky="we")

            self.scale_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message,self.Messages["Row7"]))
            self.scale_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            self.scale_supress_button = Button(self.subcanvas_Scale, text=self.Messages["RowB5"], command=self.supress_scale, **Color_settings.My_colors.Button_Base)
            self.scale_supress_button.grid(row=1, column=1, sticky="we")

            self.scale_extend_button = Button(self.subcanvas_Scale, text=self.Messages["RowB6"], command=self.extend_scale, **Color_settings.My_colors.Button_Base)
            self.scale_extend_button.grid(row=2, column=0,columnspan=2, sticky="we")
            self.scale_extend_button.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message,self.Messages["Row8"]))
            self.scale_extend_button.bind("<Leave>", self.main_frame.HW.remove_tmp_message)
            Pos_col+=2

            #Aerate a little !
            self.grid_columnconfigure(0,minsize=200)
            for row in range(Pos_col):
                self.canvas_main.grid_columnconfigure(row, minsize=20)


            #we show the eye to see the first image of the video
            self.view_first.grid(row=0,column=1)
            self.view_first.create_image(0, 0, image=self.oeuil2, anchor=NW)
            self.view_first.config(width=int(self.Size_oe[1]/4), height=int(self.Size_oe[0]/4))
            self.view_first.bind("<Enter>", self.show_first)
            self.view_first.bind("<Leave>", self.stop_show_first)
            self.subcanvas_First.bind("<Button-1>", self.select_vid)
            self.File_name_lab.bind("<Button-1>", self.select_vid)
            self.bind("<Button-1>", self.select_vid)
            self.Wrapper.bind("<Button-1>", self.select_vid)

            self.canvas_main.bind("<Button-1>", self.select_vid)
            for child in self.canvas_main.winfo_children():
                child.bind("<Button-1>", self.select_vid)
            self.isselected.bind("<Button-1>", self.select_vid)



            if self.Video!=None:
                self.update_mask()
                self.update_repre()
                self.update_crop()
                self.update_stab()
                self.update_back()
                self.update_scale()
                self.update_fps()
                self.update_name()

            self.main_frame.canvas_main.bind('<Configure>', self.resize_font)

    def save_back_img(self):
        file=filedialog.asksaveasfilename(defaultextension=".png", initialfile=self.Video.User_Name+"_"+self.Messages["Names7"]+".png", filetypes=(("Image", "*.png"),))
        if file!="":
            cv2.imwrite(file,self.Video.Back[1])

    def save_are_img(self):
        file=filedialog.asksaveasfilename(defaultextension=".png", initialfile=self.Video.User_Name+"_"+self.Messages["Names8"]+".png", filetypes=(("Image", "*.png"),))
        if file!="":
            cv2.imwrite(file,self.do_mask())


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
        self.isselected.config(bg=self.list_colors["Fusion_main"])
        self.main_frame.HW.change_default_message(self.Messages["General16"])
        self.main_frame.HW.change_tmp_message(self.Messages["General16"])

    def Reset_name(self):
        self.File_name_var.set(self.Video.Name)

    def change_vid_name(self, var, indx, mode):
        if self.File_name_var.get() not in [Vid.User_Name for Vid in self.main_frame.liste_of_videos if Vid != self.Video] and self.File_name_var.get()!="":
            self.Video.User_Name = self.File_name_var.get()
            self.File_name_ent.config(**Color_settings.My_colors.Entry_Base)
        else:
            self.File_name_ent.config(**Color_settings.My_colors.Entry_error)

        self.resize_font("")

    def ask_clear_data(self, event):
        '''Display a warning message to the user to ensure that he agrees on deleting the data'''
        if self.Video.Tracked:
            question = MsgBox.Messagebox(parent=self, title="",
                                         message=self.Messages["GWarn1"],
                                         Possibilities=[self.Messages["Yes"],self.Messages["No"]])
            self.wait_window(question)
            answer = question.result

            if answer==0:
                self.Video.clear_files()
            self.update()

    def resize_font(self, _):
        #Change the size of the displayed name of the video (according to the length of the title)
        font_tmp = font.Font(family='Helvetica', size=12, weight='bold')
        while font_tmp.measure(self.File_name_var.get())>175 and font_tmp["size"]>7:
            font_tmp["size"] -= 1

        self.File_name_ent.config(font=font_tmp)

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
        if X_Cur<50+self.width_show+50 and Y_Cur<50+self.Video.or_shape[0]*ratio:
            X_Pos=X_Cur+50
        else:
            X_Pos=50
        cv2.moveWindow(" ", X_Pos, 50)
        capture = cv2.VideoCapture(self.Video.File_name)#Faster with opencv
        _, Represent = capture.read()
        capture.release()

        if self.Video.Rotation == 1:
            Represent = cv2.rotate(Represent, cv2.ROTATE_90_CLOCKWISE)
        elif self.Video.Rotation == 2:
            Represent = cv2.rotate(Represent, cv2.ROTATE_180)
        if self.Video.Rotation == 3:
            Represent = cv2.rotate(Represent, cv2.ROTATE_90_COUNTERCLOCKWISE)

        self.main_frame.HW.change_tmp_message(self.Messages["Row22"])
        cv2.imshow(" ",cv2.resize(Represent,(int(self.Video.or_shape[1]*ratio),int(self.Video.or_shape[0]*ratio))))
        cv2.waitKey(1)




    def stop_show_first(self, *arg):
        '''Stop the display of the first image.'''
        self.main_frame.HW.remove_tmp_message()
        cv2.destroyAllWindows()
        self.main_frame.HW.remove_tmp_message

    def select_vid(self,event):
        '''When the user select a video.'''
        if not self.main_frame.wait_for_vid:
            self.main_frame.selected_vid=self.Video
            self.main_frame.update_selections()
            self.main_frame.moveX()
        else:
            self.main_frame.fusion_two_Vids(self.Video)
            self.main_frame.update_selections()

    def rotate(self, dir):
        if self.Video.Tracked:
            question = MsgBox.Messagebox(parent=self, title="",
                                         message=self.Messages["GWarn1"],
                                         Possibilities=[self.Messages["Yes"],self.Messages["No"]])
            self.wait_window(question)
            answer = question.result

            if answer==0 and self.Video.clear_files():
                # Apply a 90º rotation to the video
                if self.Video.Rotation == 3 and dir == 1:
                    self.Video.Rotation = 0
                elif self.Video.Rotation == 0 and dir == -1:
                    self.Video.Rotation = 3
                else:
                    self.Video.Rotation = self.Video.Rotation + dir

                list_shape = list(self.Video.or_shape)
                list_shape[0], list_shape[1] = list_shape[1], list_shape[0]
                self.Video.or_shape = tuple(list_shape)
                self.Video.shape=self.Video.or_shape
                self.Video.Cropped_sp = [False, [0, 0, self.Video.or_shape[0], self.Video.or_shape[1]]]
                self.Video.effacer_back()
                self.Video.effacer_mask()
                self.update()

        else:
            # Apply a 90º rotation to the video
            if self.Video.Rotation == 3 and dir == 1:
                self.Video.Rotation = 0
            elif self.Video.Rotation == 0 and dir == -1:
                self.Video.Rotation = 3
            else:
                self.Video.Rotation = self.Video.Rotation + dir

            list_shape = list(self.Video.or_shape)
            list_shape[0], list_shape[1] = list_shape[1], list_shape[0]
            self.Video.or_shape = tuple(list_shape)
            self.Video.shape = self.Video.or_shape
            self.Video.Cropped_sp = [False, [0, 0, self.Video.or_shape[0], self.Video.or_shape[1]]]
            self.Video.effacer_back()
            self.Video.effacer_mask()
            self.update()

    def update_fps(self):
        # We change the displayed fps
        self.Fr_rate = [-1, -1]
        self.Fr_nb = 1
        if self.Video != None:
            self.Fr_rate[0] = self.Video.Frame_rate[0]
            self.Fr_rate[1] = self.Video.Frame_rate[1]
            self.Fr_nb = self.Video.Frame_nb[0]

        self.List_poss_FrRate = [self.Messages["RowL12"] + " " + str(round(self.Fr_rate[0], 2))]
        value = self.Fr_rate[0]

        while value > 0.01 and (self.Fr_nb / round(self.Fr_rate[0] / value))>50:
            value = value / 2
            if value > 1:
                self.List_poss_FrRate.append(round(value, 2))
            elif value > 0.1:
                self.List_poss_FrRate.append(round(value, 3))
            else:
                self.List_poss_FrRate.append(round(value, 4))

        self.List_poss_FrRate.append(self.Messages["Row20"])

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
        if choice==self.List_poss_FrRate[0] or choice==self.Messages["Row20"]:
            self.Video.Frame_rate[1]=self.Video.Frame_rate[0]
        else:
            self.Video.Frame_rate[1] = choice

        if choice==self.Messages["Row20"]:
            newWindow = Toplevel(self.parent.master)
            interface = Interface_supp_frame_rate.Details_fps(parent=newWindow, boss=self)

        else:
            one_every = self.Video.Frame_rate[0] / self.Video.Frame_rate[1]
            self.Video.Cropped[1][0] = round(round(self.Video.Cropped[1][0] / one_every) * one_every)  # Avoid to try to open un-existing frames after changes in frame-rate
            self.Video.Cropped[1][1] = round(round(self.Video.Cropped[1][1] / one_every) * one_every)
            self.Video.Frame_nb[1] = int(self.Video.Frame_nb[0] / round(self.Video.Frame_rate[0] / self.Video.Frame_rate[1]))

        self.update()
        self.bouton_Fr_rate.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row0"].format(round(self.Video.Frame_rate[1], 2))))

    def extend_change_fps(self):
        # Open a new window to extend the frame rate at several videos
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Video.Frame_rate[1], boss=self.main_frame, Video_file=self.Video, type="fps")

    def update_crop(self):
        # Show the details about video duration (with cropping) and spatial cropping
        if self.Video.Cropped[0] and self.Video.Cropped_sp[0]:
            self.cropping_button.config(bg=self.list_colors["Button_done"],fg=self.list_colors["Fg_Button_done"])
            one_every = self.Video.Frame_rate[0] / self.Video.Frame_rate[1]
            self.text_crop.set(self.Messages["RowL1"].format(round(self.Video.Cropped[1][0]/one_every), round((self.Video.Cropped[1][0]/one_every) / self.Video.Frame_rate[1],2), \
                                                             round((self.Video.Cropped[1][1]/one_every)), round((int(self.Video.Cropped[1][1]/one_every)+1)/ self.Video.Frame_rate[1],2), \
                                                            round(self.Video.Cropped[1][1]/one_every) - round(self.Video.Cropped[1][0]/one_every) + 1, \
                                                             round((int(self.Video.Cropped[1][1]/one_every) - round(self.Video.Cropped[1][0]/one_every) +1) / self.Video.Frame_rate[1],2)))
            self.crop_it.set(self.Messages["RowB7"])

        elif self.Video.Cropped[0] and not self.Video.Cropped_sp[0]:
            self.cropping_button.config(bg=self.list_colors["Button_half"],fg=self.list_colors["Fg_Button_half"])
            one_every = self.Video.Frame_rate[0] / self.Video.Frame_rate[1]
            self.text_crop.set(self.Messages["RowL1"].format(round(self.Video.Cropped[1][0]/one_every), round((self.Video.Cropped[1][0]/one_every) / self.Video.Frame_rate[1],2), \
                                                             round(self.Video.Cropped[1][1]/one_every), round((round(self.Video.Cropped[1][1]/one_every)+1)/ self.Video.Frame_rate[1],2), \
                                                            round(self.Video.Cropped[1][1]/one_every) - round(self.Video.Cropped[1][0]/one_every) + 1, \
                                                             round((round(self.Video.Cropped[1][1]/one_every) - round(self.Video.Cropped[1][0]/one_every) +1) / self.Video.Frame_rate[1],2)))
            self.crop_it.set(self.Messages["RowB7"])

        elif not self.Video.Cropped[0] and self.Video.Cropped_sp[0]:
            self.cropping_button.config(bg=self.list_colors["Button_half"],fg=self.list_colors["Fg_Button_half"])
            self.text_crop.set(self.Messages["RowL2"].format(self.Video.Frame_nb[1], round(self.Video.Frame_nb[1] / self.Video.Frame_rate[1],2)))
            self.crop_it.set(self.Messages["RowB8"])
            self.update_repre()
            self.update_back()
        else:
            self.cropping_button.config(bg=self.list_colors["Button_ready"], fg=self.list_colors["Fg_Button_ready"])
            self.text_crop.set(self.Messages["RowL2"].format(self.Video.Frame_nb[1], round(self.Video.Frame_nb[1] / self.Video.Frame_rate[1],2)))
            self.crop_it.set(self.Messages["RowB8"])

        if self.Video.Tracked:
            self.cropping_button.config(**Color_settings.My_colors.Button_Base)

    def crop_vid(self, speed=0):
        # Open the cropping window
        if self.Video.Tracked:
            question = MsgBox.Messagebox(parent=self, title="",
                                         message=self.Messages["GWarn1"],
                                         Possibilities=[self.Messages["Yes"],self.Messages["No"]])
            self.wait_window(question)
            answer = question.result

            if answer==0 and self.Video.clear_files():
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
        #Update the view according to the parameters:
        Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
        with open(Param_file, 'rb') as fp:
            self.Params = pickle.load(fp)
        self.width_show = self.Params["Size_img_display"]  # How big are the displayed frames

        #Update the states of the video
        self.main_frame.update_selections()
        self.main_frame.update_row_display()
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
            self.isselected.config(bg=self.list_colors["Selected_main"])
            self.config(bd=10, relief="ridge", highlightthickness=3)
        else:
            self.isselected.config(bg=self.list_colors["Not_selected_main"])
            self.config(bd=1, relief="ridge", highlightthickness=1)

    def update_stab(self):
        # Update the color/info of the stabilisation cell
        if self.Video.Stab[0]:
            self.stab_button.config(bg=self.list_colors["Button_done"],fg=self.list_colors["Fg_Button_done"])
            self.text_stab.set(self.Messages["RowL3"])
            self.stab_it.set(self.Messages["RowB9"])
            self.check_stab_button.config(state="normal")
            self.extend_stab_button.config(text=self.Messages["RowB17"])
        else:
            self.stab_button.config(bg=self.list_colors["Button_ready"], fg=self.list_colors["Fg_Button_ready"])
            self.text_stab.set(self.Messages["RowL4"])
            self.stab_it.set(self.Messages["RowB10"])
            self.check_stab_button.config(state="disable")
            self.extend_stab_button.config(text=self.Messages["RowB18"])

        if self.Video.Tracked:
            self.stab_button.config(**Color_settings.My_colors.Button_Base)

    def stab_vid(self):
        # Add/Remove the stabilization
        if self.Video.Tracked:
            question = MsgBox.Messagebox(parent=self, title="",
                                         message=self.Messages["GWarn1"],
                                         Possibilities=[self.Messages["Yes"],self.Messages["No"]])
            self.wait_window(question)
            answer = question.result
            if answer==0 and self.Video.clear_files():
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
            question = MsgBox.Messagebox(parent=self, title="",
                                         message=self.Messages["GWarn1"],
                                         Possibilities=[self.Messages["Yes"],self.Messages["No"]])
            self.wait_window(question)
            answer = question.result
            if answer==0 and self.Video.clear_files():
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
            question = MsgBox.Messagebox(parent=self, title="",
                                         message=self.Messages["GWarn1"],
                                         Possibilities=[self.Messages["Yes"],self.Messages["No"]])
            self.wait_window(question)
            answer = question.result
            if answer==0 and self.Video.clear_files():
                if self.Video.Back[0]!=1:
                    self.Video.make_back()
                    self.update_back()

                elif self.Video.Back[0]==1:
                    self.main_frame.Change_win(Interface_back.Background(parent=self.main_frame.canvas_main, boss=self,
                                                                         main_frame=self.main_frame, Video_file=self.Video))

        else:
            if self.Video.Back[0]!=1:
                self.Video.make_back()
                self.update_back()

            elif self.Video.Back[0]==1:
                self.main_frame.Change_win(Interface_back.Background(parent=self.main_frame.canvas_main, boss=self,
                                                                     main_frame=self.main_frame, Video_file=self.Video))
        self.update()

    def update_name(self):
        if self.Video.Tracked:
            self.File_name_ent.config(state="disable")
            self.BReset_name.config(state="disable")
        else:
            self.File_name_ent.config(state="normal")
            self.BReset_name.config(state="normal")

    def update_back(self):
        # Update the color/info of the background cell
        if self.Video.Back[0]!=1:
            self.text_back.set(self.Messages["RowL5"])
            self.back_it.set(self.Messages["RowB11"])
            self.back_button.config(bg=self.list_colors["Button_ready"], fg=self.list_colors["Fg_Button_ready"])
            self.back_supress_button.config(state="disable")
            #self.view_back.create_image(0, 0, image=self.oeuilB2, anchor=NW)
            self.view_back.config(width=1, height=1)
            self.save_back_button.grid_forget()
        else:
            self.text_back.set(self.Messages["RowL6"])
            self.back_it.set(self.Messages["RowB12"])
            self.back_button.config(bg=self.list_colors["Button_done"],fg=self.list_colors["Fg_Button_done"])
            self.back_supress_button.config(state="normal")
            self.save_back_button.grid(row=0, column=1)
            self.view_back.create_image(0, 0, image=self.oeuil2, anchor=NW)
            self.view_back.config(width=int(self.Size_oe[1]/4), height=int(self.Size_oe[0]/4))

        if self.Video.Tracked:
            self.back_button.config(**Color_settings.My_colors.Button_Base)
            self.back_supress_button.config(bg='SystemButtonFace')

    def supress_back(self):
        # Remove existing background
        if self.Video.Tracked:
            question = MsgBox.Messagebox(parent=self, title="",
                                         message=self.Messages["GWarn1"],
                                         Possibilities=[self.Messages["Yes"],self.Messages["No"]])
            self.wait_window(question)
            answer = question.result
            if answer==0 and self.Video.clear_files():
                self.Video.effacer_back()
                self.update()
        else:
            self.Video.effacer_back()
            self.update_back()

    def show_back(self, *arg):
        # Display an image of the background on a temporary window
        if self.Video.Back[0]==1:
            self.main_frame.HW.change_tmp_message(self.Messages["Row14"])
            cv2.namedWindow(" ")
            ratio = self.width_show / self.Video.shape[1]
            X_Cur = self.master.winfo_pointerx()
            Y_Cur = self.master.winfo_pointery()
            #To avoid that the window appears on the top of the cursor
            if X_Cur < 50 + self.width_show + 50 and Y_Cur < 50 + self.Video.shape[0] * ratio:
                X_Pos = X_Cur + 50
            else:
                X_Pos = 50
            cv2.moveWindow(" ", X_Pos, 50)
            self.main_frame.HW.change_tmp_message(self.Messages["Row23"])
            cv2.imshow(" ",cv2.resize(cv2.cvtColor(self.Video.Back[1], cv2.COLOR_BGR2RGB),(int(self.Video.shape[1]*ratio),int(self.Video.shape[0]*ratio))))
            cv2.waitKey(1)




    def stop_show_back(self, *arg):
        # Remove the displayed image of the background
        self.main_frame.HW.remove_tmp_message()
        if self.Video.Back[0]==1:
            cv2.destroyAllWindows()
        self.main_frame.HW.remove_tmp_message

    def extend_back(self):
        # Open a new window to extend the automatique background at several videos
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=None, boss=self.main_frame, Video_file=self.Video, do_self=True, type="back")

    def update_mask(self):
        # Update the color/info of the arenas cell
        if not self.Video.Mask[0]:
            self.text_mask.set(self.Messages["RowL7"])
            self.mask_it.set(self.Messages["RowB13"])
            self.mask_button.config(bg=self.list_colors["Button_ready"], fg=self.list_colors["Fg_Button_ready"])
            self.mask_supress_button.config(state="disable")
            self.mask_extend_button.config(state="disable")
            #self.view_mask.create_image(0, 0, image=self.oeuilB2, anchor=NW)
            self.view_mask.config(width=1, height=1)
            self.save_mask_button.grid_forget()
        else:
            self.text_mask.set(self.Messages["RowL8"])
            self.mask_it.set(self.Messages["RowB14"])
            self.mask_button.config(bg=self.list_colors["Button_done"],fg=self.list_colors["Fg_Button_done"])
            self.mask_supress_button.config(state="normal")
            self.mask_extend_button.config(state="normal")
            self.view_mask.create_image(0, 0, image=self.oeuil2, anchor=NW)
            self.view_mask.config(width=int(self.Size_oe[1]/4), height=int(self.Size_oe[0]/4))
            self.save_mask_button.grid(row=0,column=1)
        if self.Video.Tracked:
            self.mask_button.config(**Color_settings.My_colors.Button_Base)
            self.mask_supress_button.config(**Color_settings.My_colors.Button_Base)

    def supress_mask(self):
        # Remove existing arenas
        if self.Video.Tracked:
            question = MsgBox.Messagebox(parent=self, title="",
                                         message=self.Messages["GWarn1"],
                                         Possibilities=[self.Messages["Yes"],self.Messages["No"]])
            self.wait_window(question)
            answer = question.result
            if answer==0 and self.Video.clear_files():
                self.Video.effacer_mask()
                self.update()
        else:
            self.Video.effacer_mask()
            self.update_mask()

    def mask_vid(self):
        # Open the window to define the arenas in which the targets can be found
        if self.Video.Tracked:
            question = MsgBox.Messagebox(parent=self, title="",
                                         message=self.Messages["GWarn1"],
                                         Possibilities=[self.Messages["Yes"],self.Messages["No"]])
            self.wait_window(question)
            answer = question.result
            if answer==0 and self.Video.clear_files():
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

            self.main_frame.HW.change_tmp_message(self.Messages["Row15"])
            cv2.namedWindow(" ")  # Create a named window
            ratio = self.width_show / self.Video.shape[1]

            #To avoid the window to appear on the top of the cursor
            X_Cur = self.master.winfo_pointerx()
            Y_Cur = self.master.winfo_pointery()
            if X_Cur < 50 + self.width_show + 50 and Y_Cur < 50 + self.Video.shape[0] * ratio:
                X_Pos = X_Cur + 50
            else:
                X_Pos = 50
            cv2.moveWindow(" ", X_Pos, 50)

            mask_to_show=self.do_mask()
            self.main_frame.HW.change_tmp_message(self.Messages["Row24"])
            cv2.imshow(" ",cv2.resize(mask_to_show,(int(self.Video.shape[1]*ratio),int(self.Video.shape[0]*ratio))))
            cv2.waitKey(1)



    def do_mask(self):
        Which_part = 0
        if self.Video.Cropped[0]:
            if len(self.Video.Fusion) > 1:  # If there was a concatenation
                Which_part = \
                [index for index, Fu_inf in enumerate(self.Video.Fusion) if Fu_inf[0] <= self.Video.Cropped[1][0]][-1]

        capture = cv2.VideoCapture(self.Video.Fusion[Which_part][1])  # Faster with opencv
        capture.set(cv2.CAP_PROP_POS_FRAMES, self.Video.Cropped[1][0] - self.Video.Fusion[Which_part][0])
        _, Represent = capture.read()
        capture.release()

        if self.Video.Rotation == 1:
            Represent = cv2.rotate(Represent, cv2.ROTATE_90_CLOCKWISE)
        elif self.Video.Rotation == 2:
            Represent = cv2.rotate(Represent, cv2.ROTATE_180)
        if self.Video.Rotation == 3:
            Represent = cv2.rotate(Represent, cv2.ROTATE_90_COUNTERCLOCKWISE)

        mask = Dr.draw_mask(self.Video)

        if self.Video.Back[0] == 1:  # Create the image

            if len(self.Video.Back[1].shape) > 2:
                mask_to_show = cv2.bitwise_and(cv2.cvtColor(self.Video.Back[1], cv2.COLOR_BGR2RGB),
                                               cv2.cvtColor(self.Video.Back[1], cv2.COLOR_BGR2RGB), mask=mask)
            else:
                mask_to_show = cv2.bitwise_and(self.Video.Back[1], self.Video.Back[1], mask=mask)
        else:
            if self.Video.Cropped_sp[0]:
                repre_c = Represent[self.Video.Cropped_sp[1][0]:self.Video.Cropped_sp[1][2],
                          self.Video.Cropped_sp[1][1]:self.Video.Cropped_sp[1][3]]
                mask_to_show = cv2.bitwise_and(repre_c, repre_c, mask=mask)
            else:
                mask_to_show = cv2.bitwise_and(Represent, Represent, mask=mask)
        return(mask_to_show)

    def stop_show_mask(self, *arg):
        # Remove the temporary image with arenas
        self.main_frame.HW.remove_tmp_message()
        if self.Video.Mask[0]:
            cv2.destroyAllWindows()
        self.main_frame.HW.remove_tmp_message

    def extend_mask(self):
        # Open a window to expend the position of the arenas to other videos
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Video.Mask[1], boss=self.main_frame, Video_file=self.Video, type="mask")

    def update_scale(self):
        # Update the color/info of the scale cell
        if self.Video.Scale[0] == 1:
            self.text_scale.set(self.Messages["RowL9"])
            self.scale_it.set(self.Messages["RowB15"])
            self.scale_button.config(bg=self.list_colors["Button_ready"], fg=self.list_colors["Fg_Button_ready"])
            self.scale_supress_button.config(state="disable")
            self.scale_extend_button.config(state="disable")
        else:
            self.text_scale.set(self.Messages["RowL10"].format(self.Video.Scale[0],self.Video.Scale[1]))
            self.scale_it.set(self.Messages["RowB16"])
            self.scale_button.config(bg=self.list_colors["Button_done"],fg=self.list_colors["Fg_Button_done"])
            self.scale_supress_button.config(state="normal")
            self.scale_extend_button.config(state="normal")
        if self.Video.Tracked:
            self.scale_button.config(**Color_settings.My_colors.Button_Base)
            self.scale_button.config(**Color_settings.My_colors.Button_Base)

    def supress_scale(self):
        # Remove the scale associated with the video
        if self.Video.Tracked:
            question = MsgBox.Messagebox(parent=self, title="",
                                         message=self.Messages["GWarn1"],
                                         Possibilities=[self.Messages["Yes"],self.Messages["No"]])
            self.wait_window(question)
            answer = question.result
            if answer==0 and self.Video.clear_files():
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
            question = MsgBox.Messagebox(parent=self, title="",
                                         message=self.Messages["GWarn1"],
                                         Possibilities=[self.Messages["Yes"],self.Messages["No"]])
            self.wait_window(question)
            answer = question.result
            if answer==0 and self.Video.clear_files():
                self.main_frame.Change_win(Interface_scaling.Scale(parent=self.main_frame.canvas_main, boss=self,
                                                                   main_frame=self.main_frame, Video_file=self.Video))
        else:
            self.main_frame.Change_win(Interface_scaling.Scale(parent=self.main_frame.canvas_main, boss=self,
                                                               main_frame=self.main_frame, Video_file=self.Video))

    def extend_scale(self):
        # Open a window to expend the scale of this video to others
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Video.Scale, boss=self.main_frame, Video_file=self.Video, type="scale")
