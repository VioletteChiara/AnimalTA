from tkinter import *
import os
import cv2
import numpy as np
from AnimalTA.A_General_tools import Class_change_vid_menu, Class_Lecteur, UserMessages, User_help


class Cropping(Frame):
    """This is a frame in which the user will be able to crop the video. User will indicate what frame will be the first and the last one."""
    def __init__(self, parent, boss,main_frame, proj_pos, Video_file, speed=0, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.proj_pos=proj_pos
        self.main_frame=main_frame
        self.boss=boss
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.Vid = Video_file
        self.moving = None#If the user is moving something on the frame
        self.CSp=self.Vid.Cropped_sp[1].copy()#Where to draw the cropping lines
        self.CSp=[int(val) for val in self.CSp]
        #Importation of the messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language"))), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        self.fr_rate=self.Vid.Frame_rate[1]
        self.one_every=int(round(round(self.Vid.Frame_rate[0],2)/self.Vid.Frame_rate[1]))

        # Name of the video and optionlist to change the current video:
        self.choice_menu= Class_change_vid_menu.Change_Vid_Menu(self, self.main_frame, self.Vid, "crop")
        self.choice_menu.grid(row=0,column=0)

        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)

        # Show video and time-bar
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Vid_Lecteur.speed.set(speed)
        self.Vid_Lecteur.change_speed()
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()

        self.canvas_buttons = Frame(self, bd=2, highlightthickness=1)
        self.canvas_buttons.grid(row=2, column=0, sticky="nsew")

        # Widgets entries and display
        self.canvas_entrie=Frame(self.canvas_buttons, bd=2, highlightthickness=1)
        self.canvas_entrie.grid(row=0, column=0, sticky="ew")

        #Titles:
        self.Begin_Title=Label(self.canvas_entrie,text=self.Messages["Crop5"])
        self.Begin_Title.grid(row=0,column=1,columnspan=2, sticky="ew")
        self.Duration_Title=Label(self.canvas_entrie,text=self.Messages["Crop7"])
        self.Duration_Title.grid(row=0,column=4,columnspan=2, sticky="ew")
        self.End_Title=Label(self.canvas_entrie,text=self.Messages["Crop6"])
        self.End_Title.grid(row=0,column=7,columnspan=2, sticky="ew")

        # Begin:
        regBfr = (self.register(self.Begin_fr_update), '%P', '%V')
        self.Bfrvar = StringVar()
        self.Begin_fr = Entry(self.canvas_entrie, textvariable=self.Bfrvar, validate="all", validatecommand=regBfr, justify="right")
        self.Begin_fr.grid(row=1, column=1, sticky="e")
        self.BegF_label = Label(self.canvas_entrie, text=self.Messages["Crop8"])
        self.BegF_label.grid(row=1, column=2, sticky="w")

        regBsec = (self.register(self.Begin_sec_update), '%P', '%V')
        self.Bsecvar = StringVar()
        self.Begin_sec = Entry(self.canvas_entrie, textvariable=self.Bsecvar, validate="key", validatecommand=regBsec, justify="right")
        self.Begin_sec.config()
        self.Begin_sec.grid(row=2, column=1, sticky="e")
        self.BegS_label = Label(self.canvas_entrie, text=self.Messages["Crop9"])
        self.BegS_label.grid(row=2, column=2, sticky="w")

        # Duration
        self.reg_Lfr = (self.register(self.Len_fr_update), "%P",'%V')
        self.Lfrvar = StringVar()
        self.Len_fr = Entry(self.canvas_entrie, textvariable=self.Lfrvar, validate="key", validatecommand=(self.reg_Lfr), justify="right")
        self.Len_fr.grid(row=1, column=4, sticky="e")
        self.SecL_label = Label(self.canvas_entrie, text=self.Messages["Crop8"])
        self.SecL_label.grid(row=1, column=5, sticky="w")
        self.Len_fr.bind("<Return>", self.remove_focus)

        self.reg_Lsec = (self.register(self.Len_sec_update), "%P", '%V')
        self.Lsecvar = StringVar()
        self.Len_sec = Entry(self.canvas_entrie, textvariable=self.Lsecvar, validate="key", validatecommand=(self.reg_Lsec), justify="right")
        self.Len_sec.grid(row=2, column=4, sticky="e")
        self.SecL_label = Label(self.canvas_entrie, text=self.Messages["Crop9"])
        self.SecL_label.grid(row=2, column=5, sticky="w")

        self.canvas_entrie.grid_columnconfigure((1,2,4,5,7,8), weight=3, uniform="column")
        self.canvas_entrie.grid_columnconfigure((0,3,6,9), weight=1, uniform="column")


        # End:
        self.Efrvar = StringVar()
        self.End_fr = Label(self.canvas_entrie, textvariable=self.Efrvar,
                            background="white")
        self.End_fr.grid(row=1, column=7, sticky="e")
        self.SecF_label = Label(self.canvas_entrie, text=self.Messages["Crop8"])
        self.SecF_label.grid(row=1, column=8, sticky="w")

        self.Esecvar = StringVar()
        self.End_sec = Label(self.canvas_entrie, textvariable=self.Esecvar,
                             background="white")
        self.End_sec.grid(row=2, column=7, sticky="e")
        self.SecE_label = Label(self.canvas_entrie, text=self.Messages["Crop9"])
        self.SecE_label.grid(row=2, column=8, sticky="w")



        #Fix the beg/end
        self.canvas_fix=Frame(self.canvas_buttons, bd=2, highlightthickness=1)
        self.canvas_fix.grid(row=1, column=0, sticky="ew")

        self.B_Begin=Button(self.canvas_fix, text=self.Messages["Crop3"], command=self.fix_begin)
        self.B_Begin.grid(row=0,column=1)
        self.B_End=Button(self.canvas_fix, text=self.Messages["Crop4"], command=self.fix_end)
        self.B_End.grid(row=0,column=3)

        self.canvas_fix.grid_columnconfigure((1,3), weight=3, uniform="column")
        self.canvas_fix.grid_columnconfigure((0,2,4), weight=1, uniform="column")

        self.HW= User_help.Help_win(self.parent, default_message=self.Messages["Crop2"], width=250)
        self.HW.grid(row=0, column=1,sticky="nsew")

        #Validate crop
        self.canvas_validate=Canvas(self.parent, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_validate.grid(row=1, column=1, sticky="sew")
        Grid.columnconfigure(self.canvas_validate, 0, weight=1)

        self.B_Validate=Button(self.canvas_validate, text=self.Messages["Validate"],bg="#6AED35", command=self.Validate_crop)
        self.B_Validate.grid(row=0,column=0, sticky="ews")

        self.B_Validate_NContinue=Button(self.canvas_validate, text=self.Messages["Validate_NC"],bg="#6AED35", command=lambda: self.Validate_crop(follow=True))
        self.B_Validate_NContinue.grid(row=1,column=0, sticky="ews")

        self.update_times()
        self.bind_all("<Button-1>", self.give_focus)

    def give_focus(self,event):
        #Once the user stop to write in the text field, the focus come back  to the video reader
        if event.widget.winfo_class()!="Entry":
            self.Vid_Lecteur.focus_set()

    def remove_focus(self, *arg):
        #Set the focus to the video reader
        self.Vid_Lecteur.focus_set()

    def update_times(self,order="NONE",*arg):
        #Calculate and display all the times (begin, end, duration)
        if order != "Begin_fr":
            self.Bfrvar.set(self.Scrollbar.crop_beg)
        if order != "Begin_sec":
            self.Bsecvar.set(round(self.Scrollbar.crop_beg / self.fr_rate,2))
        if order != "End_fr":
            self.Efrvar.set(self.Scrollbar.crop_end)
        if order != "End_sec":
            self.Esecvar.set(round((self.Scrollbar.crop_end+1) / self.fr_rate,2))
        if order != "Len_fr":
            self.Lfrvar.set(self.Scrollbar.crop_end-self.Scrollbar.crop_beg+1)
        if order != "Len_sec":
            self.Lsecvar.set(round((self.Scrollbar.crop_end-self.Scrollbar.crop_beg+1)/self.fr_rate,2))

    def Begin_fr_update(self, new_val, method):
        #This function is called when the user is writting in the begin frame number entry.
        #It only allows user to write numeric values (changed to int) and update all affected values.
        #For instance, it the beginning of the video is delayed, the duration is shorter.
        if new_val=="" and method!="focusout":
            return True
        elif new_val!="":
            if method == "key":
                try:
                    if int(new_val) >= 0 and int(new_val) < self.Vid.Frame_nb[1]:
                        self.Scrollbar.crop_beg = int(new_val)
                        if int(new_val) >= self.Scrollbar.crop_end:
                            self.Scrollbar.crop_end = self.Vid.Frame_nb[1]-1
                        self.Scrollbar.refresh()
                        self.Bsecvar.set(round(self.Scrollbar.crop_beg / self.fr_rate,2))
                        self.Lsecvar.set(round((self.Scrollbar.crop_end - self.Scrollbar.crop_beg+1) / self.fr_rate, 2))
                        self.Lfrvar.set(int(self.Scrollbar.crop_end - self.Scrollbar.crop_beg+1))
                        self.Efrvar.set(self.Scrollbar.crop_end)
                        self.Esecvar.set(round(self.Scrollbar.crop_end / self.fr_rate, 2))
                        self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)
                    else:
                        return False
                except:
                    return False

            return True
        else:
            self.Begin_fr.focus_force()
            return False

    def Begin_sec_update(self, new_val, method):
        #This function is called when the user is writting in the begin in seconds entry.
        #It only allows user to write numeric values (changed to float) and update all affected values.
        if new_val == "" and method != "focusout":
            return True
        elif new_val != "":
            if method == "key":
                try:
                    if float(new_val) >= 0 and float(new_val) < (self.Vid.Frame_nb[1] / self.fr_rate):
                        self.Scrollbar.crop_beg = int(round(float(new_val) * self.fr_rate))
                        if (float(new_val)*self.fr_rate) >= self.Scrollbar.crop_end:
                            self.Scrollbar.crop_end = self.Vid.Frame_nb[1]-1
                        self.Scrollbar.refresh()
                        self.Bfrvar.set(self.Scrollbar.crop_beg)
                        self.Lsecvar.set(round((self.Scrollbar.crop_end - self.Scrollbar.crop_beg+1) / self.fr_rate, 2))
                        self.Lfrvar.set(int(self.Scrollbar.crop_end - self.Scrollbar.crop_beg+1))
                        self.Efrvar.set(self.Scrollbar.crop_end)
                        self.Esecvar.set(round(self.Scrollbar.crop_end / self.fr_rate, 2))
                        self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)
                    else:
                        return False
                except:
                    return False

            return True
        else:
            self.Begin_sec.focus_force()
            return False


    def Len_fr_update(self, new_val, method):
        #This function is called when the user is writting in the length in frame number entry.
        #It only allows user to write numeric values (changed to int) and update all affected values.
        if new_val == "" and method != "focusout":
            return True
        elif new_val != "":
            if method == "key":
                try:
                    if int(new_val) >= 0 and int(new_val) < self.Vid.Frame_nb[1]:
                        self.Scrollbar.crop_end = min(self.Scrollbar.crop_beg+int(new_val),self.Vid.Frame_nb[1]-1)
                        self.Scrollbar.refresh()
                        self.Lsecvar.set(round((self.Scrollbar.crop_end-self.Scrollbar.crop_beg+1)/self.fr_rate,2))
                        self.Bfrvar.set(self.Scrollbar.crop_beg)
                        self.Bsecvar.set(round(self.Scrollbar.crop_beg / self.fr_rate, 2))
                        self.Efrvar.set(self.Scrollbar.crop_end)
                        self.Esecvar.set(round(self.Scrollbar.crop_end / self.fr_rate, 2))
                        self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)

                    else:
                        return False
                except:
                    return False

            return True
        else:
            self.Begin_fr.focus_force()
            return False


    def Len_sec_update(self, new_val, method):
        #This function is called when the user is writting in the length in seconds entry.
        #It only allows user to write numeric values (changed to float) and update all affected values.
        if new_val == "" and method != "focusout":
            return True
        elif new_val != "":
            if method == "key":
                try:
                    if float(new_val) >= 0 and (float(new_val)*self.fr_rate) < self.Vid.Frame_nb[1]:
                        self.Scrollbar.crop_end = int(min((self.Scrollbar.crop_beg + float(new_val)*self.fr_rate), self.Vid.Frame_nb[1]-1))
                        self.Scrollbar.refresh()
                        self.Lfrvar.set(round((self.Scrollbar.crop_end - self.Scrollbar.crop_beg+1), 2))
                        self.Bfrvar.set(self.Scrollbar.crop_beg)
                        self.Bsecvar.set(round(self.Scrollbar.crop_beg / self.fr_rate, 2))
                        self.Efrvar.set(self.Scrollbar.crop_end)
                        self.Esecvar.set(round(self.Scrollbar.crop_end / self.fr_rate, 2))#########NEW
                        self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)

                    else:
                        return False
                except:
                    return False

            return True
        else:
            self.Begin_fr.focus_force()
            return False


    def fix_begin(self):
        #This function change the left cropping bound of the video to be the current displayed frame
        self.Scrollbar.crop_beg=self.Scrollbar.active_pos
        if self.Scrollbar.active_pos>=self.Scrollbar.crop_end:
            self.Scrollbar.crop_end=self.Scrollbar.video_length
        self.update_times()
        self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)
        self.Scrollbar.refresh()

    def fix_end(self):
        # This function change the right cropping bound of the video to be the current displayed frame
        self.Scrollbar.crop_end = self.Scrollbar.active_pos
        if self.Scrollbar.active_pos<=self.Scrollbar.crop_beg:
            self.Scrollbar.crop_beg=0
        self.update_times()
        self.Vid_Lecteur.update_image(self.Scrollbar.active_pos)
        self.Scrollbar.refresh()

    def modif_image(self, img, **args):
        #Change the image before showing it.
        #Here the modification is adding a black veil on the top of the image of the current frame is outside of the cropping window.
        new_img=np.copy(img)
        self.last_empty = img

        self.Vid_Lecteur.update_ratio()#Ensure the "ratio" (how much the image size should be modified according to available space) is correctly calculated

        if self.Scrollbar.active_pos>self.Scrollbar.crop_end or self.Scrollbar.active_pos<self.Scrollbar.crop_beg:
            new_img = cv2.addWeighted(new_img, 1, new_img, 0, 1)

        #The user can also crop the video (in X and Y), if it is the case, the expected result of the cropping is shown:
        new_img=cv2.line(new_img,[self.CSp[1],0],[self.CSp[1],self.Vid.or_shape[0]],(255,0,0),int(max(1,self.Vid_Lecteur.ratio*2)))
        new_img = cv2.line(new_img, [self.CSp[3], 0], [self.CSp[3], self.Vid.or_shape[0]], (255, 0, 0), int(max(1,self.Vid_Lecteur.ratio*2)))
        new_img = cv2.line(new_img, [0, self.CSp[0]], [self.Vid.or_shape[1], self.CSp[0]],(255, 0, 0), int(max(1,self.Vid_Lecteur.ratio*2)))
        new_img = cv2.line(new_img, [0, self.CSp[2]], [self.Vid.or_shape[1], self.CSp[2]],(255, 0, 0),int(max(1,self.Vid_Lecteur.ratio*2)))
        empty=np.zeros([self.Vid.or_shape[0],self.Vid.or_shape[1],1], np.uint8)
        empty=cv2.rectangle(empty,[self.CSp[1],self.CSp[0]],[self.CSp[3],self.CSp[2]],255,-1)
        new_img_temp=cv2.bitwise_and(new_img,new_img,mask=empty)
        new_img=cv2.addWeighted(new_img, 0.5, new_img_temp, 0.5, 0)
        self.Vid_Lecteur.afficher_img(new_img)

    def Validate_crop(self, follow=False):
        #Save the cropping options.
        #If follow=True, open the next video in the list

        #If the user selected the whole video, we consider there are no cropping
        if round((self.Scrollbar.crop_beg)*self.one_every) ==0 and round((self.Scrollbar.crop_end)*self.one_every)==self.Vid.Frame_nb[0]-1:
            self.Vid.Cropped = [False, [0,self.Vid.Frame_nb[0]-1]]
        else:
            self.Vid.Cropped=[True,[round((self.Scrollbar.crop_beg)*self.one_every),round((self.Scrollbar.crop_end)*self.one_every)]]

        if self.Vid.Cropped_sp[1]!=self.CSp:#If the user changed the spatial cropping (x/y), we remove existing background and arenas
            self.Vid.effacer_back()
            self.Vid.effacer_mask()

        if self.Vid.or_shape[0]==self.CSp[2]-self.CSp[0] and self.Vid.or_shape[1]==self.CSp[3]-self.CSp[1]:
            self.Vid.Cropped_sp=[False,[0,0,self.Vid.or_shape[0],self.Vid.or_shape[1]]]
            self.Vid.shape = self.Vid.or_shape
        else:
            self.Vid.Cropped_sp[0] = True
            self.Vid.Cropped_sp[1]=self.CSp.copy()
            self.Vid.shape=(self.Vid.Cropped_sp[1][2]-self.Vid.Cropped_sp[1][0],self.Vid.Cropped_sp[1][3]-self.Vid.Cropped_sp[1][1])

        if follow and self.Vid != self.main_frame.liste_of_videos[-1]:
            for i in range(len(self.main_frame.liste_of_videos)):
                if self.main_frame.liste_of_videos[i]==self.Vid:
                    self.choice_menu.change_vid(self.main_frame.liste_of_videos[i+1].User_Name)
                    break
        else:
            self.End_of_window()

    def End_of_window(self):
        #Terminate properly ths window
        self.unbind_all("<Button-1>")
        self.Vid_Lecteur.proper_close()
        self.grab_release()
        self.canvas_validate.grid_forget()
        self.canvas_validate.destroy()
        self.HW.grid_forget()
        self.HW.destroy()
        self.main_frame.return_main()


    #If the user try to interact with the frame:
    def pressed_can(self, Pt, Shift):
        #We check if the user was pressing on one of the cropping lines, the moving variable indicates which line is pressed
        if abs(Pt[0]-self.CSp[1])<self.Vid_Lecteur.ratio*7:#If we press on the cropping line:
            self.moving=1

        if abs(Pt[0]-self.CSp[3])<self.Vid_Lecteur.ratio*7:#If we press on the cropping line:
            self.moving=3

        if abs(Pt[1]-self.CSp[0])<self.Vid_Lecteur.ratio*7:#If we press on the cropping line:
            self.moving=0

        if abs(Pt[1]-self.CSp[2])<self.Vid_Lecteur.ratio*7:#If we press on the cropping line:
            self.moving=2


    def moved_can(self, Pt, Shift):
        if self.moving!=None:
            if self.moving==0 or self.moving==2:
                self.CSp[self.moving]=int(Pt[1])
            elif self.moving==1 or self.moving==3:
                self.CSp[self.moving]=int(Pt[0])
            self.modif_image(self.last_empty)

    def released_can(self, Pt):
        TMP=self.CSp.copy()
        self.CSp[0]=min([int(TMP[0]),int(TMP[2])])
        self.CSp[1] = min([int(TMP[1]), int(TMP[3])])
        self.CSp[2]=max([int(TMP[0]),int(TMP[2])])
        self.CSp[3] = max([int(TMP[1]), int(TMP[3])])
        self.modif_image(self.last_empty)
        self.moving=None


"""
root = Tk()
root.geometry("+100+100")
Video_file=Class_Video.Video(File_name="D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01.avi")
interface = Cropping(parent=root, boss=None, Video_file=Video_file)
root.mainloop()

"""