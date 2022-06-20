from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
from functools import partial
from tkinter import messagebox

import decord

from BioTrack import Interface_masking, Interface_scaling, UserMessages, Interface_extend, \
    Interface_stabilis, Interface_back, Function_draw_mask as Dr, Interface_cropping
from tkinter import font
import time
import os
import math


class Row_Can(Canvas):
    def __init__(self, Video_file, main_boss,proj_pos, parent=None, **kw):
            Frame.__init__(self, parent, kw)
            self.last_time = time.time()-10
            self.Video=Video_file
            self.main_frame=main_boss
            self.parent=parent
            self.proj_pos=proj_pos
            self.config(width=500)
            self.width_show=600

            self.Language = StringVar()
            f = open("Files/Language", "r")
            self.Language.set(f.read())
            self.LanguageO = self.Language.get()
            f.close()

            self.Messages = UserMessages.Mess[self.Language.get()]

            file_name = os.path.basename(self.Video.File_name)
            point_pos = file_name.rfind(".")
            self.Already_tracked=self.Video.Tracked


            #Draw preparation:
            self.oeuil = cv2.imread("Files/Oeuil.png")
            self.oeuil = cv2.cvtColor(self.oeuil, cv2.COLOR_BGR2RGB)
            self.Size_oe = self.oeuil.shape
            self.oeuil = cv2.resize(self.oeuil, (int(self.Size_oe[1] / 4), int(self.Size_oe[0] / 4)))
            self.oeuil2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.oeuil))

            self.oeuilB = cv2.imread("Files/OeuilB.png")
            self.oeuilB = cv2.cvtColor(self.oeuilB, cv2.COLOR_BGR2RGB)
            self.oeuilB = cv2.resize(self.oeuilB, (int(self.Size_oe[1] / 4), int(self.Size_oe[0] / 4)))
            self.oeuilB2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.oeuilB))


            #Video name and representation:
            self.subcanvas_First = Canvas(self, bd=0, highlightthickness=0, relief='flat')
            self.subcanvas_First.grid(row=0,column=0, sticky="snwe")

            self.isselected=Canvas(self.subcanvas_First,heigh=75, width=15, bg="red")
            self.isselected.grid(row=0,column=0, rowspan=2, sticky="ns")
            self.File_name_txt = StringVar()
            self.font= font.Font(self.master, family='Arial', size=12, weight='bold')
            self.File_name_lab=Label(self.subcanvas_First, textvariable=self.File_name_txt, wraplengt=175, font=self.font)
            self.File_name_lab.grid(row=0,column=1)
            self.File_name_lab.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row9"]))
            self.File_name_lab.bind("<Leave>", self.main_frame.HW.remove_tmp_message)



            self.view_first = Canvas(self.subcanvas_First)
            self.view_first.grid(row=1, column=1, columnspan=2)
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

            original_fps=self.Video.Frame_rate[0]
            self.List_poss_FrRate =[self.Messages["RowL12"]+ " " +str(round(original_fps,2))]
            value=original_fps
            while value > 1:
                value=value/2
                self.List_poss_FrRate.append(round(value,2))
            self.holder=StringVar()
            if self.Video.Frame_rate[1]==self.Video.Frame_rate[0]:
                self.holder.set(self.Messages["RowL12"]+ " " +str(round(original_fps,2)))
            else:
                self.holder.set(self.Video.Frame_rate[1])
            self.bouton_Fr_rate = OptionMenu(self.subcanvas_Fr_rate, self.holder, *self.List_poss_FrRate, command=self.change_fps)
            self.bouton_Fr_rate.grid(row=1, column=0, sticky="we")
            self.bouton_Fr_rate.bind("<Button-1>",self.ask_clear_data)
            self.bouton_Fr_rate.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row0"].format(round(self.Video.Frame_rate[1],2))))
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
            if self.Video.Stab[0]:
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

            self.update_mask()
            self.update_repre()
            self.update_crop()
            self.update_stab()
            self.update_back()
            self.update_scale()
            self.update_size()
            self.update_fps()

            self.File_name_lab.bind('<Configure>', self.resize_font)


    def ask_clear_data(self, event):
        if self.Already_tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response:
                self.clear_data()
            self.update()

    def resize_font(self, _):
        if time.time()-self.last_time>1:
            longueur=(len(self.File_name_lab.cget("text")))
            if longueur < 20:
                height = 15
            elif longueur <25:
                height = 12
            elif longueur <30:
                height = 11
            else:
                height = 10
            self.font['size'] = height
        self.last_time = time.time()



    def update_size(self):
        self.canvas_main.config(width=self.parent.master.winfo_width()-self.subcanvas_First.winfo_width()-50)



    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas_main.configure(scrollregion=self.canvas_main.bbox("all"))

    # Representation
    def update_repre(self):
        self.File_name_txt.set(self.Messages["Video"] + ": " + self.Video.Name)

    def show_first(self, *arg):
        self.main_frame.HW.change_tmp_message(self.Messages["Row9"])
        cv2.namedWindow(" ")  # Create a named window
        ratio = self.width_show / self.Video.shape[1]
        X_Cur=self.master.winfo_pointerx()
        Y_Cur = self.master.winfo_pointery()
        if X_Cur<50+self.width_show+100 and Y_Cur<50+self.Video.shape[0]*ratio:
            X_Pos=X_Cur+100
        else:
            X_Pos=50
        cv2.moveWindow(" ", X_Pos, 50)
        capture = cv2.VideoCapture(self.Video.File_name)#Faster with opencv
        _, Represent = capture.read()
        capture.release()
        cv2.imshow(" ",cv2.resize(Represent,(int(self.Video.shape[1]*ratio),int(self.Video.shape[0]*ratio))))
        cv2.waitKey(1)



    def stop_show_first(self, *arg):
        self.main_frame.HW.remove_tmp_message()
        cv2.destroyAllWindows()

    def select_vid(self,*args):
        if not self.main_frame.wait_for_vid:
            Xpos = self.main_frame.vsh.get()[0]
            self.main_frame.selected_vid=self.Video
            self.main_frame.update_selections()
            self.main_frame.moveX(Xpos)
        else:
            self.main_frame.fusion_two_Vids(self.Video)


    def clear_data(self):
        # On supprime les fichiers associés
        self.Video.clear_files()

    ###########NEW
    #Frame rate
    def update_fps(self):
        self.holder.set(round(self.Video.Frame_rate[1],2))

    def change_fps(self, choice):
        if choice==self.List_poss_FrRate[0]:
            self.Video.Frame_rate[1]=self.Video.Frame_rate[0]
        else:
            self.Video.Frame_rate[1] = choice

        self.Video.Frame_nb[1] = int(self.Video.Frame_nb[0] / round(self.Video.Frame_rate[0] / self.Video.Frame_rate[1]))

        self.update()
        self.bouton_Fr_rate.bind("<Enter>", partial(self.main_frame.HW.change_tmp_message, self.Messages["Row0"].format(round(self.Video.Frame_rate[1], 2))))

    def extend_change_fps(self):
        ratio=round(self.Video.Frame_rate[0] / self.Video.Frame_rate[1])
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=ratio, boss=self.main_frame,
                                            Video_file=self.Video, type="fps")

    #Cropping
    def update_crop(self):
        if self.Video.Cropped[0]:
            self.cropping_button.config(bg="#3aa6ff")
            one_every = int(round(round(self.Video.Frame_rate[0], 2) / self.Video.Frame_rate[1]))
            self.text_crop.set(self.Messages["RowL1"].format(int(self.Video.Cropped[1][0]/one_every), round((self.Video.Cropped[1][0]/one_every) / self.Video.Frame_rate[1],2), \
                                                             int((self.Video.Cropped[1][1]/one_every)), round((int(self.Video.Cropped[1][1]/one_every)+1)/ self.Video.Frame_rate[1],2), \
                                                            int(self.Video.Cropped[1][1]/one_every) - int(self.Video.Cropped[1][0]/one_every) + 1, \
                                                             round((int(self.Video.Cropped[1][1]/one_every) - int(self.Video.Cropped[1][0]/one_every) +1) / self.Video.Frame_rate[1],2)))

            self.crop_it.set(self.Messages["RowB7"])
            self.update_repre()
            self.update_back()

        else:
            self.cropping_button.config(bg="#ff8a33")
            self.text_crop.set(self.Messages["RowL2"].format(self.Video.Frame_nb[1], round(self.Video.Frame_nb[1] / self.Video.Frame_rate[1],2)))
            self.crop_it.set(self.Messages["RowB8"])

        if self.Already_tracked:
            self.cropping_button.config(bg="SystemButtonFace")

    def crop_vid(self):
        if self.Already_tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response:
                self.clear_data()
                self.main_frame.Change_win(Interface_cropping.Cropping(parent=self.main_frame.canvas_main, boss=self, main_frame=self.main_frame, proj_pos=self.proj_pos, Video_file=self.Video))

        else:
            self.main_frame.Change_win(
                Interface_cropping.Cropping(parent=self.main_frame.canvas_main, boss=self, main_frame=self.main_frame,
                                            proj_pos=self.proj_pos, Video_file=self.Video))

    def update(self):
        file_name = os.path.basename(self.Video.File_name)
        point_pos = file_name.rfind(".")
        self.main_frame.Change_win
        self.Already_tracked = self.Video.Tracked
        self.update_scale()
        self.update_stab()
        self.update_mask()
        self.update_back()
        self.update_crop()
        self.update_fps()
        self.update_selection()

    def update_selection(self):
        if self.main_frame.selected_vid==self.Video:
            self.isselected.config(bg="green")
            self.config(bd=10, relief="ridge", highlightthickness=3)
        else:
            self.isselected.config(bg="red")
            self.config(bd=1, relief="ridge", highlightthickness=1)


    #Stabilise
    def update_stab(self):
        if self.Video.Stab[0]:
            self.stab_button.config(bg="#3aa6ff")
            self.text_stab.set(self.Messages["RowL3"])
            self.stab_it.set(self.Messages["RowB9"])
            self.check_stab_button.config(state="active")
            self.extend_stab_button.config(text=self.Messages["RowB18"])
        else:
            self.stab_button.config(bg="#ff8a33")
            self.text_stab.set(self.Messages["RowL4"])
            self.stab_it.set(self.Messages["RowB10"])
            self.check_stab_button.config(state="disable")
            self.extend_stab_button.config(text=self.Messages["RowB17"])

        if self.Already_tracked:
            self.stab_button.config(bg="SystemButtonFace")

    def stab_vid(self):
        if self.Already_tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response:
                self.clear_data()
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

    def check_stab(self):
        self.main_frame.Change_win(
            Interface_stabilis.Stabilise(parent=self.main_frame.canvas_main, boss=self, main_frame=self.main_frame, Video_file=self.Video))

    def extend_stab(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Video.Stab[0], boss=self.main_frame, Video_file=self.Video, do_self=True, type="stab")


    #Background
    def back_vid(self):
        if self.Already_tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response:
                self.clear_data()
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


    def update_back(self):
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

        if self.Already_tracked:
            self.back_button.config(bg="SystemButtonFace")
            self.back_supress_button.config(bg='SystemButtonFace')

    def supress_back(self):
        if self.Already_tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response:
                self.clear_data()
                self.Video.effacer_back()
                self.update()
        else:
            self.Video.effacer_back()
            self.update_back()

    def show_back(self, *arg):
        if self.Video.Back[0]:
            self.main_frame.HW.change_tmp_message(self.Messages["Row14"])
            cv2.namedWindow(" ")  # Create a named window
            cv2.namedWindow(" ")  # Create a named window
            ratio = self.width_show / self.Video.shape[1]
            X_Cur = self.master.winfo_pointerx()
            Y_Cur = self.master.winfo_pointery()
            if X_Cur < 50 + self.width_show + 100 and Y_Cur < 50 + self.Video.shape[0] * ratio:
                X_Pos = X_Cur + 100
            else:
                X_Pos = 50
            cv2.moveWindow(" ", X_Pos, 50)
            cv2.imshow(" ",cv2.resize(self.Video.Back[1],(int(self.Video.shape[1]*ratio),int(self.Video.shape[0]*ratio))))
            cv2.waitKey(1)

    def stop_show_back(self, *arg):
        self.main_frame.HW.remove_tmp_message()
        if self.Video.Back[0]:
            cv2.destroyAllWindows()

    def extend_back(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=None, boss=self.main_frame, Video_file=self.Video, do_self=True, type="back")

    # Mask
    def update_mask(self):
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

        if self.Already_tracked:
            self.mask_button.config(bg="SystemButtonFace")
            self.mask_supress_button.config(bg='SystemButtonFace')

    def supress_mask(self):
        if self.Already_tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response:
                self.clear_data()
                self.Video.effacer_mask()
                self.update()
        else:
            self.Video.effacer_mask()
            self.update_mask()

    def mask_vid(self):
        if self.Already_tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response:
                self.clear_data()
                self.main_frame.Change_win(Interface_masking.Mask(parent=self.main_frame.canvas_main,
                                                                  boss=self, main_frame=self.main_frame, proj_pos=self.proj_pos, Video_file=self.Video))
                self.update()
        else:
            self.main_frame.Change_win(
                Interface_masking.Mask(parent=self.main_frame.canvas_main, boss=self, main_frame=self.main_frame,
                                       proj_pos=self.proj_pos, Video_file=self.Video))
            self.update()

    def show_mask(self, *arg):
        if self.Video.Mask[0]:
            Which_part = 0
            if self.Video.Cropped[0]:
                if len(self.Video.Fusion) > 1:  # Si on a plus d'une video
                    Which_part = [index for index, Fu_inf in enumerate(self.Video.Fusion) if Fu_inf[0] <= self.Video.Cropped[1][0]][-1]

            capture = cv2.VideoCapture(self.Video.Fusion[Which_part][1])  # Faster with opencv
            capture.set(cv2.CAP_PROP_POS_FRAMES, self.Video.Cropped[1][0] - self.Video.Fusion[Which_part][0])
            _, self.Represent = capture.read()
            capture.release()

            self.main_frame.HW.change_tmp_message(self.Messages["Row15"])
            cv2.namedWindow(" ")  # Create a named window
            cv2.namedWindow(" ")  # Create a named window
            ratio = self.width_show / self.Video.shape[1]
            X_Cur = self.master.winfo_pointerx()
            Y_Cur = self.master.winfo_pointery()
            if X_Cur < 50 + self.width_show + 100 and Y_Cur < 50 + self.Video.shape[0] * ratio:
                X_Pos = X_Cur + 100
            else:
                X_Pos = 50
            cv2.moveWindow(" ", X_Pos, 50)
            mask = Dr.draw_mask(self.Video)

            if self.Video.Back[0]:
                mask_to_show=cv2.bitwise_and(self.Video.Back[1],self.Video.Back[1],mask=mask)
            else:
                mask_to_show=cv2.bitwise_and(self.Represent,self.Represent,mask=mask)

            cv2.imshow(" ",cv2.resize(mask_to_show,(int(self.Video.shape[1]*ratio),int(self.Video.shape[0]*ratio))))
            cv2.waitKey(1)

    def stop_show_mask(self, *arg):
        self.main_frame.HW.remove_tmp_message()
        if self.Video.Mask[0]:
            cv2.destroyAllWindows()

    def extend_mask(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Video.Mask[1], boss=self.main_frame, Video_file=self.Video, type="mask")


    # Scale
    def update_scale(self):
        if  self.Video.Scale[0] == 1:
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

        if self.Already_tracked:
            self.scale_button.config(bg="SystemButtonFace")
            self.scale_button.config(bg="SystemButtonFace")


    def supress_scale(self):
        if self.Already_tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response:
                self.clear_data()
                self.Video.Scale[0] = 1
                self.Video.Scale[1] = ""
                self.update_scale()
        else:
            self.Video.Scale[0]=1
            self.Video.Scale[1] = ""
            self.update_scale()

    def scale_vid(self):
        if self.Already_tracked:
            response=messagebox.askyesno(message=self.Messages["GWarn1"])
            if response:
                self.clear_data()
                self.main_frame.Change_win(Interface_scaling.Scale(parent=self.main_frame.canvas_main, boss=self,
                                                                   main_frame=self.main_frame, Video_file=self.Video))
        else:
            self.main_frame.Change_win(Interface_scaling.Scale(parent=self.main_frame.canvas_main, boss=self,
                                                               main_frame=self.main_frame, Video_file=self.Video))

    def extend_scale(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.Video.Scale, boss=self.main_frame, Video_file=self.Video, type="scale")
