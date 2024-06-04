from tkinter import *
import cv2
import numpy as np
from AnimalTA.D_Tracking_process import Do_the_track
from AnimalTA.E_Post_tracking import Coos_loader_saver as CoosLS
from AnimalTA.A_General_tools import Class_Lecteur, UserMessages, Class_stabilise, Color_settings
from AnimalTA.C_Pretracking import Interface_back, Interface_arenas
from AnimalTA.C_Pretracking.a_Parameters_track import Interface_parameters_track


class Show(Frame):
    """This Frame is used to rerun the tracking over a portion of the video, to correct potential tracking mistakes.
    To this aim, the user can define temporary tracking parameters that will be used for this portion only."""
    def __init__(self, parent, boss, Vid, Video_liste, prev_row=None, Arena=None, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base)
        self.parent = parent
        self.boss = boss
        self.grid(sticky="nsew")
        self.parent.geometry("1050x620")
        self.Video_liste = Video_liste
        self.Vid=Vid
        self.boss.PortionWin.grab_set()
        self.prev_row=prev_row
        self.Arena=Arena

        #Import language
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.tail_size=5

        Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW

        self.Folder=self.Vid.Folder

        self.CheckVar = IntVar()
        self.ecart=10#Esthetical point, we add some frames out of the portion before and after so the user can have a context

        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Portion0"])

        #Where the options are displayed
        Right_part=Frame(self, **Color_settings.My_colors.Frame_Base)
        Right_part.grid(row=0, column=1)

        self.User_help = Frame(Right_part, **Color_settings.My_colors.Frame_Base)
        self.User_help.grid(row=0, column=0, sticky="new")
        self.Lab_help=Label(self.User_help, text=self.Messages["Portion11"], wraplength=300, **Color_settings.My_colors.Label_Base)
        self.Lab_help.grid()

        self.User_buttons = Frame(Right_part, **Color_settings.My_colors.Frame_Base)
        self.User_buttons.grid(row=1, rowspan=3, column=0, sticky="sew")

        self.text_stab=StringVar()
        if self.Vid.Stab[0]:
            self.text_stab.set(self.Messages["Portion2"])
        else:
            self.text_stab.set(self.Messages["Portion3"])
        #Stabilisation
        self.B_change_stab=Button(self.User_buttons, textvariable=self.text_stab, command=self.change_stab, **Color_settings.My_colors.Button_Base)
        self.B_change_stab.grid(row=1,column=0, columnspan=2, sticky="ew")

        #Arenas definition
        self.B_change_mask=Button(self.User_buttons, text=self.Messages["Portion4"], command=self.change_mask, **Color_settings.My_colors.Button_Base)
        self.B_change_mask.grid(row=2,column=0, columnspan=2, sticky="ew")

        #Background
        self.B_change_back=Button(self.User_buttons, text=self.Messages["Portion5"], command=self.change_back, **Color_settings.My_colors.Button_Base)
        if self.Vid.Back[0]==1:
            self.B_change_back.grid(row=3,column=0, columnspan=2, sticky="ew")

        #Tracking parameters
        self.B_change_params = Button(self.User_buttons, text=self.Messages["Portion6"], command=self.change_params, **Color_settings.My_colors.Button_Base)
        self.B_change_params.grid(row=4,column=0, columnspan=2, sticky="ew")

        #Ruen the track
        self.B_redo_track = Button(self.User_buttons, text=self.Messages["Portion0"], command=self.redo_track, **Color_settings.My_colors.Button_Base)
        self.B_redo_track.config(background=Color_settings.My_colors.list_colors["Button_ready"], fg=Color_settings.My_colors.list_colors["Fg_Button_ready"])
        self.B_redo_track.grid(row=5,column=0, columnspan=2, sticky="ew")

        #Show the progression of the tracking
        self.loading_lab = Label(self.User_buttons, text="", height=10, **Color_settings.My_colors.Label_Base)
        self.loading_lab.grid(row=6,column=0)
        self.loading_bar = Canvas(self.User_buttons, height=10, **Color_settings.My_colors.Frame_Base)
        self.loading_bar.grid(row=6,column=0, columnspan=3, sticky="ew")

        self.B_validate_track = Button(self.User_buttons, text=self.Messages["Portion8"], command=self.validate_correction, **Color_settings.My_colors.Button_Base)
        self.B_validate_track.config(state="disable")
        self.B_validate_track.grid(row=7, column=0, sticky="nsew")

        self.B_cancel = Button(self.User_buttons, text=self.Messages["Cancel"], command=self.End_of_window, **Color_settings.My_colors.Button_Base)
        self.B_cancel.config(background=Color_settings.My_colors.list_colors["Cancel"],fg=Color_settings.My_colors.list_colors["Fg_Cancel"])
        self.B_cancel.grid(row=7, column=1, sticky="nsew")


        self.Coos, _ = CoosLS.load_coos(self.Vid, TMP=True, location=self)
        self.NB_ind = len(self.Vid.Identities)

        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=5)
        self.Vid_Lecteur.grid(row=0, column=0, sticky="nsew")
        self.Scrollbar = self.Vid_Lecteur.Scrollbar
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub+1)
        self.Vid_Lecteur.bindings()
        self.Scrollbar.refresh()

        self.parent.protocol("WM_DELETE_WINDOW", self.leave)

    def leave(self):
        #Close without applying any modifications to the original trackings
        self.Vid_Lecteur.proper_close()
        self.boss.PortionWin.grab_release()
        self.boss.PortionWin.destroy()
        self.boss.redo_Lecteur()
        self.destroy()

    def End_of_window(self):
        self.leave()

    def validate_correction(self):
        #Apply the new tracking results and close this Frame
        self.Vid_Lecteur.proper_close()
        self.boss.PortionWin.grab_release()
        self.boss.PortionWin.destroy()
        self.boss.change_for_corrected()
        self.destroy()

    def redo_track(self):
        #Re-run the tracking
        self.B_change_stab.config(state="disable")
        self.B_change_back.config(state="disable")
        self.B_change_mask.config(state="disable")
        self.B_change_params.config(state="disable")
        self.B_redo_track.config(state="disable")
        self.B_validate_track.config(state="disable")
        self.B_cancel.config(state="disable")
        self.Vid_Lecteur.proper_close()#We ensure the last decord is well closed

        if self.Vid.Track[1][8]:
            Do_the_track.Do_tracking(self, self.Vid, self.Folder, type="fixed", portion=True, prev_row=self.prev_row, arena_interest=self.Arena)
        else:
            Do_the_track.Do_tracking(self, self.Vid, self.Folder, type="variable", portion=True, prev_row=self.prev_row, arena_interest=self.Arena)

        self.Coos, _ = CoosLS.load_coos(self.Vid, TMP=True, location=self)

        self.B_change_stab.config(state="normal")
        self.B_change_back.config(state="normal")
        self.B_change_mask.config(state="normal")
        self.B_change_params.config(state="normal")
        self.B_cancel.config(state="normal")

        self.B_redo_track.config(state="normal")
        self.B_validate_track.config(background=Color_settings.My_colors.list_colors["Button_done"], fg=Color_settings.My_colors.list_colors["Fg_Button_done"])

        self.B_validate_track.config(state="normal")
        self.B_validate_track.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])

        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=5)
        self.Vid_Lecteur.grid(row=0, column=0, sticky="nsew")
        self.Scrollbar = self.Vid_Lecteur.Scrollbar
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub+1)
        self.Vid_Lecteur.bindings()
        self.Scrollbar.refresh()

    def show_load(self):
        #Show the progress of the tracking process
        self.loading_lab.config(text=self.Messages["Loading"])
        self.loading_lab.update()
        self.loading_bar.delete('all')
        self.loading_bar.create_rectangle(0, 0, 300, self.loading_bar.cget("height"), fill=Color_settings.My_colors.list_colors["Loading_before"])
        self.loading_bar.create_rectangle(0, 0, self.timer * 300, self.loading_bar.cget("height"), fill=Color_settings.My_colors.list_colors["Loading_after"])
        self.loading_bar.update()

    def modif_image(self, img=[], aff=False, move=True, actual_pos=None, *args):
        #draw the target's potition and trajectories on the image
        if len(img)==0:
            new_img=np.copy(self.last_empty)
        else:
            self.last_empty = img
            new_img = np.copy(img)

        self.Vid_Lecteur.update_ratio()

        if self.Vid.Cropped[0]:
            to_remove = round(round((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every))
        else:
            to_remove=0

        if self.Vid.Stab[0]:
            new_img = (Class_stabilise.find_best_position(Vid=self.Vid, Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=False))

        for ind in range(self.NB_ind):
            color=self.Vid.Identities[ind][2]
            for prev in range(min(int(self.tail_size*self.Vid.Frame_rate[1]), int(self.Scrollbar.active_pos - to_remove))):
                if int(self.Scrollbar.active_pos - prev) > round(((self.Vid.Cropped[1][0])/self.Vid_Lecteur.one_every)) and int(self.Scrollbar.active_pos) <= round(self.Vid.Cropped[1][1]/self.Vid_Lecteur.one_every):
                    if self.Coos[ind,int(self.Scrollbar.active_pos - 1 - prev - to_remove),0] != -1000 and self.Coos[ind,int(self.Scrollbar.active_pos - prev - to_remove),0] != -1000 :
                        TMP_tail_1 = (int(self.Coos[ind,int(self.Scrollbar.active_pos - 1 - prev - to_remove),0]),
                                      int(self.Coos[ind,int(self.Scrollbar.active_pos - 1 - prev - to_remove),1]))

                        TMP_tail_2 = (int(self.Coos[ind,int(self.Scrollbar.active_pos - prev - to_remove),0]),
                                      int(self.Coos[ind,int(self.Scrollbar.active_pos - prev - to_remove),1]))

                        new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, color, max(int(3*self.Vid_Lecteur.ratio),1))

            if self.Scrollbar.active_pos > round(((self.Vid.Cropped[1][0]-1)/self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= round(((self.Vid.Cropped[1][1]-1)/self.Vid_Lecteur.one_every)+1):
                center=self.Coos[ind,self.Scrollbar.active_pos - to_remove]
                if center[0]!=-1000:
                    if self.CheckVar.get()==int(ind):
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=max(int(5*self.Vid_Lecteur.ratio),5), color=(255,255,255),thickness=-1)
                        new_img = cv2.circle(new_img, (int(center[0]), int(center[1])), radius=max(int(6*self.Vid_Lecteur.ratio),3), color=(0,0,0), thickness=-1)
                    new_img=cv2.circle(new_img,(int(center[0]),int(center[1])),radius=max(int(4*self.Vid_Lecteur.ratio),1),color=color,thickness=-1)

        self.Vid_Lecteur.afficher_img(new_img)

    def pressed_can(self, Pt, *args):
        pass

    def moved_can(self, Pt, Shift):
        pass

    def released_can(self, Pt):
        pass

    ##All the functions bellow open the Frame corresponding to the parameters to change
    #stab=stabilisation
    #mask=arena definition
    #back=background modification
    #params=tracking parameters
    def change_stab(self):
        self.Vid.Stab[0]=1-self.Vid.Stab[0]
        if self.Vid.Stab[0]:
            self.text_stab.set(self.Messages["Portion2"])
        else:
            self.text_stab.set(self.Messages["Portion3"])

    def change_mask(self):
        self.boss.PortionWin.grab_release()
        newWindow = Toplevel(self.parent.master)
        interface = Interface_arenas.Mask(parent=newWindow, boss=self.boss, main_frame=self, proj_pos=0, Video_file=self.Vid, portion=True)

    def change_back(self):
        self.boss.PortionWin.grab_release()
        newWindow = Toplevel(self.parent.master)
        interface = Interface_back.Background(parent=newWindow, boss=self.boss, main_frame=self, Video_file=self.Vid, portion=True)

    def change_params(self):
        self.boss.PortionWin.grab_release()
        newWindow = Toplevel(self.parent.master)
        interface= Interface_parameters_track.Param_definer(parent=newWindow, boss=self.boss, main_frame=self, Video_file=self.Vid, portion=True)

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
