from tkinter import *
import pyautogui
from tkinter import filedialog
from tkinter import messagebox
import pickle
import shutil
import cv2
from BioTrack import Interface_Check, UserMessages, Interface_extend, Interface_Analyses3, Class_Video, Class_Row_Videos, Interface_Vids_for_track, Interface_parameters_track, Interface_Vids_for_convert, Interface_Save_Vids
import os
from functools import partial
from win32api import GetMonitorInfo, MonitorFromPoint
import math
os.system("")  # enables ansi escape characters in terminal


class Interface(Frame):
    def __init__(self, parent, liste_of_videos=[], **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(background="grey")
        self.parent=parent
        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]
        self.project_name = StringVar()
        self.project_name.set("Untitled")
        self.Distance_limit=2
        #self.grab_set()
        self.fullscreen_status=False##################NEWWWWWWWWWWWWWWWW
        self.pressed_bord = [None,None]################NEWWWWWWWWWWW
        self.changing=False
        self.selected_vid=None
        self.first=True
        self.folder=None
        self.wait_for_vid=False#For fusion process, if we expect the user to select a second vid, = True
        self.liste_of_videos = liste_of_videos
        self.Infos_track=StringVar()
        self.no_track=self.Messages["General7"]
        self.Infos_track.set(self.Messages["General2"])


        self.parent.bind("<Button-1>", self.press_change_size)################NEWWWWWWWWWWW
        self.parent.bind("<B1-Motion>", self.change_size)################NEWWWWWWWWWWW
        self.parent.bind("<Motion>", self.change_cursor)################NEWWWWWWWWWWW
        self.parent.bind("<ButtonRelease-1>", self.release_size)################NEWWWWWWWWWWW


        # Canvas:
        # Barre de titre
        self.canvas_title_bar = Canvas(self, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_title_bar.grid(row=0, column=0, columnspan=3, sticky="new")
        self.canvas_title_bar.columnconfigure(0, weight=1)
        self.canvas_title_bar.columnconfigure(1, weight=1)
        self.canvas_title_bar.columnconfigure(2, weight=100)
        self.canvas_title_bar.columnconfigure(3, weight=1)
        self.canvas_title_bar.columnconfigure(4, weight=1)
        self.canvas_title_bar.bind("<Button-1>", self.press_fenetre)
        self.canvas_title_bar.bind("<B1-Motion>", self.move_fenetre)
        self.default_message=self.Messages["Welcome"]
        Grid.columnconfigure(self, 0, weight=1)########NEW

        # Visualisation de la video et barre de temps
        self.canvas_main = Frame(self,  bd=2, highlightthickness=1, relief='ridge')
        self.canvas_main.grid(row=1, column=0, sticky="nsew")
        Grid.rowconfigure(self, 1, weight=1)########NEW

        self.canvas_show=Frame(self.canvas_main,  bd=2, highlightthickness=1, relief='ridge')
        self.canvas_show.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.rows_optns=Frame(self.canvas_show, bd=2, highlightthickness=1, relief='ridge')
        Grid.columnconfigure(self.canvas_main, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.canvas_main, 0, weight=1)  ########NEW

        Grid.rowconfigure(self.rows_optns, 0, weight=1)  ########NEW

        Grid.columnconfigure(self.rows_optns, 1, weight=1)  ########NEW
        Grid.columnconfigure(self.rows_optns, 2, weight=1)  ########NEW
        Grid.columnconfigure(self.rows_optns, 3, weight=1)  ########NEW
        Grid.columnconfigure(self.rows_optns, 4, weight=1)  ########NEW
        Grid.columnconfigure(self.rows_optns, 5, weight=1)  ########NEW
        Grid.columnconfigure(self.rows_optns, 6, weight=100)  ########NEW
        Grid.columnconfigure(self.rows_optns, 7, weight=1)  ########NEW


        #Widget row options:
        self.Optns_Lab=Entry(self.rows_optns, textvar=self.project_name, bg="darkgrey", relief="ridge", font=("Arial", 14))
        self.Optns_Lab.grid(row=0, column=0, sticky="w")
        self.bouton_Add = Button(self.rows_optns, text=self.Messages["GButton7"], command=self.add_video)
        self.bouton_Add.grid(row=0, column=1, sticky="nswe")
        self.bouton_Supr = Button(self.rows_optns, text=self.Messages["GButton8"], command=self.supr_video)
        self.bouton_Supr.grid(row=0, column=2, sticky="nswe")
        self.bouton_Supr.config(state="disable")
        self.bouton_Fus = Button(self.rows_optns, text=self.Messages["GButton16"], command=self.fus_video)
        self.bouton_Fus.grid(row=0, column=3, sticky="nswe")
        self.bouton_Fus.config(state="disable")
        self.bouton_Fus.bind("<Enter>", partial(self.change_msg, self.Messages["General15"]))
        self.bouton_Fus.bind("<Leave>", self.remove_msg)


        self.bouton_make_track = Button(self.rows_optns, text=self.Messages["GButton10"], command=self.begin_track)
        self.bouton_make_track.grid(row=0, column=4, sticky="nswe")
        self.bouton_make_track.bind("<Enter>", partial(self.change_msg, self.Messages["General19"]))
        self.bouton_make_track.bind("<Leave>", self.remove_msg)

        self.bouton_make_analyses = Button(self.rows_optns, text=self.Messages["GButton15"], command=self.run_analyses)
        self.bouton_make_analyses.grid(row=0, column=5, sticky="nswe")
        self.bouton_make_analyses.bind("<Enter>", partial(self.change_msg, self.Messages["General20"]))
        self.bouton_make_analyses.bind("<Leave>", self.remove_msg)

        self.bouton_save_TVid = Button(self.rows_optns, text=self.Messages["GButton18"], command=self.export_vid)
        self.bouton_save_TVid.grid(row=0, column=7, sticky="nse")
        self.bouton_save_TVid.config(state="disable")
        self.bouton_save_TVid.bind("<Enter>", partial(self.change_msg, self.Messages["GButton19"]))
        self.bouton_save_TVid.bind("<Leave>", self.remove_msg)


        self.canvas_rows = Canvas(self.canvas_show, bd=2, highlightthickness=1, relief='ridge')
        self.Visualise_vids = Frame(self.canvas_rows, background="#ffffff")

        self.vsh = Scrollbar(self.canvas_show, orient="horizontal", command=self.canvas_rows.xview)
        self.vsh.bind("<Motion>",self.first_action)
        self.vsh.grid(row=2, column=0, sticky="we")

        self.canvas_rows.configure(xscrollcommand=self.vsh.set)
        self.canvas_rows.create_window((4,4), window=self.Visualise_vids, anchor="n",tags="self.frame")
        self.canvas_rows.grid(row=1, column=0, sticky="nsew")


        self.vsv = Scale(self.canvas_show, orient="vertical", from_=0, to=0)
        self.vsv.bind("<ButtonRelease-1>", self.afficher_projects)
        self.vsv.grid(row=1, column=1, sticky="ns")


        Grid.columnconfigure(self.canvas_show, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.canvas_show, 1, weight=1)  ########NEW

        self.Visualise_vids.bind("<Configure>", self.onFrameConfigure)
        self.bind_all("<MouseWheel>", self.on_mousewheel)
        self.parent.bind_all("<Button-1>", self.remove_Fus)
        self.bind_all("<Button-1>", self.remove_Fus)


        #Aide à l'utilisateur:
        self.canvas_help = Frame(self.canvas_main, height=100,  highlightthickness=4, relief='flat', highlightbackground="RoyalBlue3")
        self.canvas_help.grid(row=0,column=1, sticky="nsew")
        Info_title=Label(self.canvas_help, text=self.Messages["Info"],  justify=CENTER, background="RoyalBlue3", fg="white", font=("Helvetica", 16, "bold"))
        Info_title.grid(row=0, sticky="new")
        Grid.columnconfigure(self.canvas_help, 0, weight=1)



        # Widgets:
        # Barre de titre
        self.Nom_Logiciel = Label(self.canvas_title_bar, fg="white", text="Bio-Track", bg="purple",
                                  font=("courier new", 12))
        self.Nom_Logiciel.grid(row=0, column=0, sticky="w")


        self.bouton_New = Button(self.canvas_title_bar, text=self.Messages["GButton1"], command=self.new_project)
        self.bouton_New.grid(row=0, column=2, sticky="e")

        self.bouton_Open = Button(self.canvas_title_bar, text=self.Messages["GButton2"], command=self.open_file)
        self.bouton_Open.grid(row=0, column=4, sticky="e")


        self.bouton_Close = Button(self.canvas_title_bar, text=self.Messages["GButton17"], command=self.close_file)
        self.bouton_Close.grid(row=0, column=5, sticky="e")
        self.bouton_Close.config(state="disable")

        self.bouton_Save = Button(self.canvas_title_bar, text=self.Messages["GButton3"], command=self.save)
        self.bouton_Save.grid(row=0, column=6, sticky="e")
        self.bouton_Save.config(state="disable")

        OptionLan = list(UserMessages.Mess.keys())

        self.bouton_Lang = OptionMenu(self.canvas_title_bar, self.Language, *OptionLan, command=self.update_lan)
        self.bouton_Lang.grid(row=0, column=7, sticky="e")
        #####To add language, just add this

        self.canvas_title_bar.columnconfigure(8,minsize=25)

        self.bouton_minimize = Button(self.canvas_title_bar, text="—", command=self.minimize)
        self.bouton_minimize.grid(row=0, column=9, sticky="e")

        self.bouton_fullscreen = Button(self.canvas_title_bar, text=u'\u2B1C', command=self.fullscreen)
        self.bouton_fullscreen.grid(row=0, column=10, sticky="e")


        self.bouton_Fermer = Button(self.canvas_title_bar, text="X", fg="white", bg="red", command=self.fermer)
        self.bouton_Fermer.grid(row=0, column=11, sticky="e")

        # Aide à l'utilisateur
        self.user_message=StringVar()
        self.user_message.set(self.default_message)
        self.User_help=Label(self.canvas_help, textvariable=self.user_message, width=35, wraplengt=200,  justify=LEFT)
        self.User_help.grid(row=1, sticky="new")


        self.canvas_help.rowconfigure(1,min=50)

        self.canvas_next_step=Frame(self.canvas_main)
        self.canvas_next_step.grid(row=1, column=1)
        Grid.rowconfigure(self.canvas_help, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.canvas_help, 1, weight=100)

        self.Beginn_track=Button(self.canvas_next_step, text=self.Messages["GButton4"], command=self.Beg_track)
        self.Beginn_track.config(state="disable")
        self.Beginn_track.bind("<Enter>", partial(self.change_msg, self.Messages["General11"]))
        self.Beginn_track.bind("<Leave>", self.remove_msg)

        self.Show_T_infos=Label(self.canvas_next_step, textvariable=self.Infos_track, wraplength=200)

        self.BExtend_track=Button(self.canvas_next_step, text=self.Messages["GButton5"], command=self.extend_track)
        self.BExtend_track.config(state="disable")
        self.BExtend_track.bind("<Enter>", partial(self.change_msg, self.Messages["General12"]))
        self.BExtend_track.bind("<Leave>", self.remove_msg)

        self.bouton_check_track = Button(self.canvas_next_step, text=self.Messages["GButton13"], command=self.check_track)
        self.bouton_check_track.config(state="disable")
        self.bouton_check_track.bind("<Enter>", partial(self.change_msg, self.Messages["General13"]))
        self.bouton_check_track.bind("<Leave>", self.remove_msg)

        self.bouton_analyse_track = Button(self.canvas_next_step, text=self.Messages["GButton14"], command=self.analyse_track)
        self.bouton_analyse_track.config(state="disable")
        self.bouton_analyse_track.bind("<Enter>", partial(self.change_msg, self.Messages["General14"]))
        self.bouton_analyse_track.bind("<Leave>", self.remove_msg)

        self.get_attention(0)




    def minimize(self):
        self.master.overrideredirect(False)
        self.master.wm_iconify()
        self.master.bind('<FocusIn>', self.on_deiconify)


    def on_deiconify(self, *arg):
        if not self.master.wm_state()=="iconic":
            self.master.overrideredirect(True)
            self.master.set_appwindow(root=self.master)
            self.master.unbind("<FocusIn>")
            if self.fullscreen_status:
                monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
                work_area = monitor_info.get("Work")
                self.parent.geometry("{0}x{1}+0+0".format(work_area[2], work_area[3]))

    def grid_param_track(self):
        self.bouton_analyse_track.grid(row=4, column=0, sticky="swe")
        self.bouton_check_track.grid(row=3, column=0, sticky="swe")
        self.BExtend_track.grid(row=2,sticky="sew")
        self.Show_T_infos.grid(row=1, sticky="sew")
        self.Beginn_track.grid(row=0,sticky="sew")

    def get_attention(self, count):
        curcol=self.User_help.cget("bg")
        if curcol=="red":
            self.User_help.config(bg="SystemButtonFace")
        else:
            self.User_help.config(bg="red")
        if (count)<5:
            count+=1
            self.User_help.after(250, self.get_attention,count)

    def change_msg(self,new_message,*arg):
        self.user_message.set(new_message)

    def remove_msg(self,*arg):
        self.user_message.set(self.default_message)

    def first_action(self, *arg):
        self.first=False

    def press_change_size(self, event):
        largeur=10
        if event.widget==self and not self.fullscreen_status:
            if event.y>self.parent.winfo_height()-largeur and event.y<self.parent.winfo_height():
                self.pressed_bord=[0,pyautogui.position()[1]]#0=bottom, then clockwise
                self.size_before=[self.parent.winfo_width(),self.parent.winfo_height()]

            elif event.x<largeur and event.x>0:
                self.pressed_bord=[1,pyautogui.position()[0]]#0=bottom, then clockwise
                self.size_before=[self.parent.winfo_width(),self.parent.winfo_height()]
                self.parent.win_old_pos = (self.parent.winfo_x(), self.parent.winfo_y())

            elif event.y<largeur and event.y>0:
                self.pressed_bord=[2,pyautogui.position()[1]]#0=bottom, then clockwise
                self.size_before=[self.parent.winfo_width(),self.parent.winfo_height()]
                self.parent.win_old_pos = (self.parent.winfo_x(), self.parent.winfo_y())

            elif event.x>self.parent.winfo_width()-largeur and event.x<self.parent.winfo_width():
                self.pressed_bord=[3,pyautogui.position()[0]]#0=bottom, then clockwise
                self.size_before=[self.parent.winfo_width(),self.parent.winfo_height()]


    def change_cursor(self, event):
        largeur = 10
        if event.widget == self and not self.fullscreen_status:
            if event.y > self.parent.winfo_height() - largeur and event.y < self.parent.winfo_height():
                self.master.config(cursor="sb_v_double_arrow")
            elif  event.y<largeur and event.y>0:
                self.master.config(cursor="sb_v_double_arrow")
            elif event.x > self.parent.winfo_width() - largeur and event.x < self.parent.winfo_width():
                self.master.config(cursor="sb_h_double_arrow")
            elif event.x < largeur and event.x > 0:
                self.master.config(cursor="sb_h_double_arrow")
            else:
                self.master.config(cursor="arrow")
        else:
            self.master.config(cursor="arrow")


    def change_size(self, event):
        if not self.fullscreen_status and event.widget==self:
            if self.pressed_bord[0]==0:
                self.changing = True
                diff=pyautogui.position()[1]-self.pressed_bord[1]
                width_M=self.size_before[0]
                height_M = self.size_before[1]+diff
                self.parent.geometry(str(width_M)+"x"+str(height_M))

            if self.pressed_bord[0]==1:
                self.changing = True
                pos_abs = pyautogui.position()
                diff=pyautogui.position()[0]-self.pressed_bord[1]
                width_M=self.size_before[0]-diff
                height_M = self.size_before[1]
                self.parent.geometry(str(width_M)+"x"+str(height_M))
                deplacement = ("", str(pos_abs[0]),
                               str(self.parent.win_old_pos[1]))
                self.parent.geometry("+".join(deplacement))

            if self.pressed_bord[0]==2:
                self.changing = True
                pos_abs = pyautogui.position()
                diff=pyautogui.position()[1]-self.pressed_bord[1]
                width_M=self.size_before[0]
                height_M = self.size_before[1]-diff
                self.parent.geometry(str(width_M)+"x"+str(height_M))
                deplacement = ("", str(self.parent.win_old_pos[0]), str(pos_abs[1]))
                self.parent.geometry("+".join(deplacement))

            if self.pressed_bord[0] == 3:
                self.changing = True
                diff = pyautogui.position()[0] - self.pressed_bord[1]
                width_M = self.size_before[0] + diff
                height_M = self.size_before[1]
                self.parent.geometry(str(width_M) + "x" + str(height_M))


    def release_size(self, event):
        self.pressed_bord=[None,None]
        if self.changing:
            self.afficher_projects()
        self.changing=False


    def moveX(self, *arg):
        self.canvas_rows.xview_moveto('0.0')

    def on_mousewheel(self, event):
        self.vsv.set(self.vsv.get() + int(-1*(event.delta/120)))
        self.afficher_projects()

    def begin_track(self):
        nb_vid_T=0
        for Vid in self.liste_of_videos:
            if Vid.Track[0]:
                nb_vid_T+=1

        if nb_vid_T>0:
            newWindow = Toplevel(self.parent.master)
            interface = Interface_Vids_for_track.Extend(parent=newWindow, boss=self, type="Tracking")
        else:
            messagebox.showinfo(message=self.Messages["GError1"], title=self.Messages["GErrorT1"])

    def run_analyses(self):
        nb_vid_T = 0
        for Vid in self.liste_of_videos:
            if Vid.Tracked:
                nb_vid_T += 1

        if nb_vid_T>0:
            newWindow = Toplevel(self.parent.master)
            interface = Interface_Vids_for_track.Extend(parent=newWindow, boss=self, type="Analyses")
        else:
            messagebox.showinfo(message="You must before process to video tracking", title="Error, no video ready")

    def export_vid(self):
        if self.selected_vid != None:
            self.Change_win(Interface_Save_Vids.Lecteur(parent=self.canvas_main, main_frame=self, boss=self.parent, Vid=self.selected_vid, Video_liste=self.liste_of_videos))


    def check_track(self):
        if self.selected_vid != None:
            self.Change_win(Interface_Check.Lecteur(parent=self.canvas_main, main_frame=self, boss=self.parent,Vid=self.selected_vid, Video_liste=self.liste_of_videos))


    def analyse_track(self, CheckVar=None):
        if self.selected_vid != None:
            self.Change_win(Interface_Analyses3.Analyse_track(parent=self.canvas_main, main_frame=self, boss=self.parent,Vid=self.selected_vid, Video_liste=self.liste_of_videos, CheckVar=CheckVar))


    def Calc_center(self,x):
        cnt_M = cv2.moments(x)
        cY = int(cnt_M["m01"] / cnt_M["m00"])
        return cY

    def extend_track(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.selected_vid.Track[1], boss=self, Video_file=self.selected_vid, type="track")

    def Beg_track(self):
        if self.selected_vid != None:
            if self.selected_vid.Tracked:
                response = messagebox.askyesno( message=self.Messages["GWarn1"])
                if response:
                    self.selected_vid.clear_files()
                    self.Change_win(Interface_parameters_track.Param_definer(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                                             Video_file=self.selected_vid))
            else:
                self.Change_win(
                    Interface_parameters_track.Param_definer(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                             Video_file=self.selected_vid))

    def Change_win(self, interface):
        #We remove the actual canvas
        self.canvas_show.grid_forget()
        self.canvas_next_step.grid_forget()
        self.canvas_help.grid_forget()
        self.bouton_Lang.config(state="disable")
        self.bouton_New.config(state="disable")
        self.bouton_Save.config(state="disable")
        self.bouton_Add.config(state="disable")
        self.bouton_Open.config(state="disable")
        self.unbind_all("<MouseWheel>")

        # We add the new one
        self.Second_Menu = interface




    def return_main(self):
        # We add the actual canvas
        self.canvas_show.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.canvas_help.grid(row=0, column=1, sticky="nsew")
        self.canvas_next_step.grid(row=1, column=1, sticky="nsew")
        self.update_selections()
        self.bouton_Lang.config(state="active")
        self.bouton_New.config(state="active")
        self.bouton_Save.config(state="active")
        self.bouton_Add.config(state="active")
        self.bouton_Open.config(state="active")
        self.bind_all("<MouseWheel>", self.on_mousewheel)
        self.afficher_projects()

        # We remove the new one
        self.Second_Menu.grid_forget()
        self.Second_Menu.destroy()



    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas_rows.configure(scrollregion=self.canvas_rows.bbox("all"))
        if self.first:
            self.moveX()

    def new_project(self):
        if not self.folder == None:
            answer = messagebox.askyesnocancel(self.Messages["General17"], self.Messages["General18"])
            if answer:
                self.save()
                self.new_project2()
            elif answer == False:
                self.new_project2()
            else:
                pass
        else:
            self.new_project2()

    def new_project2(self):
        try:
            self.file_to_save = filedialog.asksaveasfilename(defaultextension=".btr", initialfile="Untitled_project.btr", filetypes=(("Bio-Track", "*.btr"),))
            if len(self.file_to_save)>0:
                file_name = os.path.basename(self.file_to_save)
                point_pos = file_name.rfind(".")
                self.folder = os.path.dirname(self.file_to_save)+"/Project_folder_"+ file_name[:point_pos]
                if not os.path.isdir(self.folder):
                    os.makedirs(self.folder)
                else:
                    shutil.rmtree(self.folder)
                    os.makedirs(self.folder)
                self.project_name.set(file_name[:-4])
                self.default_message=self.Messages["General0"]
                self.user_message.set(self.default_message)
                self.liste_of_videos=[]
                self.load_projects()
                self.rows_optns.grid(row=0, column=0, sticky="sewn")
                with open(self.file_to_save, 'wb') as fp:
                    data_to_save = dict(Project_name=self.project_name.get(), Folder=self.folder, Videos=self.liste_of_videos)
                    pickle.dump(data_to_save, fp)
                self.bouton_Save.config(state="active")
        except:
            pass

    def add_video(self):
        try:
            videos_to_add = filedialog.askopenfilenames()
            self.list_to_convert = []
            for file in videos_to_add:
                point_pos = file.rfind(".")
                if file[point_pos:].lower() != ".avi":
                    self.list_to_convert.append(file)
                elif file not in [Vid.File_name for Vid in self.liste_of_videos]:
                    self.liste_of_videos.append(Class_Video.Video(File_name=file, Folder=self.folder))

            if len(self.list_to_convert)>0:
                newWindow = Toplevel(self.parent.master)
                interface = Interface_Vids_for_convert.Convert(parent=newWindow, boss=self)

            self.load_projects()
            self.default_message = self.Messages["General1"]
            self.user_message.set(self.default_message)
            self.grid_param_track()

        except:
            self.get_attention(0)
            self.user_message.set(self.Messages["General3"])

        self.update_selections()

    def supr_video(self, Vid="NA"):
        if Vid == "NA":
            Vid_to_supr=self.selected_vid
        else:
            Vid_to_supr=Vid

        if Vid_to_supr != None:
            answer = messagebox.askyesno(self.Messages["GWarnT2"],self.Messages["GWarn2"])
            if answer:
                #On supprime les fichiers associés:
                self.selected_vid.clear_files()
                pos_R=[index for index,Vid_L in enumerate(self.liste_of_videos) if Vid_L==Vid_to_supr]
                self.liste_of_videos.pop(pos_R[0])
                self.load_projects()
                self.selected_vid=None
                self.update_selections()
                self.save()

    def fus_video(self):
        if self.wait_for_vid:
            self.wait_for_vid=False
            self.default_message=self.Messages["General1"]
            self.change_msg(self.Messages["General1"])
            self.bouton_Fus.bind("<Enter>", partial(self.change_msg, self.Messages["General15"]))
            self.bouton_Fus.config(bg="SystemButtonFace", activebackground="SystemButtonFace")
        else:
            self.wait_for_vid=True
            self.default_message=self.Messages["General16"]
            self.change_msg(self.Messages["General16"])
            self.bouton_Fus.bind("<Enter>", partial(self.change_msg, self.Messages["General16"]))
            self.bouton_Fus.config(bg="red", activebackground="red", state="active")

    def remove_Fus(self, event):
        if self.wait_for_vid and event.widget!=self.bouton_Fus:
            self.fus_video()

    def fusion_two_Vids(self, second_Vid):
        if self.selected_vid!=second_Vid:
            if self.selected_vid.shape==second_Vid.shape and self.selected_vid.Frame_rate[0]==second_Vid.Frame_rate[0]:
                self.selected_vid.Fusion.append([self.selected_vid.Frame_nb[0], second_Vid.File_name])

                self.selected_vid.Frame_nb[0] += second_Vid.Frame_nb[0]
                self.selected_vid.Frame_nb[1] = math.floor(self.selected_vid.Frame_nb[0] / round(self.selected_vid.Frame_rate[0] / self.selected_vid.Frame_rate[1]))  ######NEW
                self.selected_vid.Cropped=[False,[0,self.selected_vid.Frame_nb[0]]]
                self.supr_video(second_Vid)
                self.wait_for_vid=False
                self.bouton_Fus.config(bg="SystemButtonFace", activebackground="SystemButtonFace")
                self.afficher_projects()
            else:
                self.wait_for_vid=False
                self.bouton_Fus.config(bg="SystemButtonFace", activebackground="SystemButtonFace")
                messagebox.showinfo(message=self.Messages["GWarn4"], title=self.Messages["GWarnT4"])


    def load_projects(self):
        Ypos=1
        self.list_projects = []
        for Vid in self.liste_of_videos:
            self.list_projects.append(
                Class_Row_Videos.Row_Can(parent=self.Visualise_vids, main_boss=self, Video_file=Vid, proj_pos=Ypos - 1, bd=2, highlightthickness=1, relief='ridge'))
            Ypos+=1
        self.afficher_projects()


    def afficher_projects(self, *arg):

        try:
            for label in self.Visualise_vids.grid_slaves():
                    label.grid_forget()

        except Exception:
            pass

        Ypos = 0
        try:
            if len(self.list_projects)>0:
                central=int(self.vsv.get())
                nb_visibles = self.canvas_show.winfo_height() / (130)
                self.vsv.config(to=len(self.liste_of_videos) - 1)

                for who in range(central,min(len(self.list_projects),int(central+round(nb_visibles))+1)):
                    self.list_projects[who].grid(row=Ypos, column=0, sticky="we")
                    Ypos+=1

        except:
            pass

    def update_projects(self):
        for Row in self.list_projects:
            Row.update()


    def update_selections(self):
        if self.selected_vid==None:
            self.Infos_track.set(self.Messages["General2"])
            self.Beginn_track.config(state="disable")
            self.BExtend_track.config(state="disable")
            self.bouton_check_track.config(state="disable")
            self.bouton_analyse_track.config(state="disable")
            self.bouton_Supr.config(state="disable")
            self.bouton_Fus.config(state="disable")
            self.bouton_save_TVid.config(state="disable")
        else:
            self.bouton_Supr.config(state="active")
            self.bouton_Fus.config(state="active")
            self.bouton_save_TVid.config(state="active")

            if not self.selected_vid.Track[0]:
                self.Beginn_track.config(state="active", activebackground="#ff8a33", bg="#ff8a33")
                self.Infos_track.set(self.no_track)
                self.BExtend_track.config(state="disable")
                self.bouton_check_track.config(state="disable")
                self.bouton_analyse_track.config(state="disable")

            else:
                self.Beginn_track.config(state="active", activebackground="#3aa6ff", bg="#3aa6ff")
                self.BExtend_track.config(state="active")
                self.Infos_track.set(self.Messages["Names1"] + ": " + str(int(self.selected_vid.Track[1][0])) + "\n" +
                                     self.Messages["Names2"] + ": " + str(int(self.selected_vid.Track[1][1])) + "\n" +
                                     self.Messages["Names3"] + ": " + str(int(self.selected_vid.Track[1][2])) + "\n" +
                                     self.Messages["Names4"] + ": " + str(round(float(self.selected_vid.Track[1][3][0]),2)) + "-" + str(round(float(self.selected_vid.Track[1][3][1]),2)) + "\n" +
                                     self.Messages["Names6"] + ": " + str(round(float(self.selected_vid.Track[1][5]),2)) + "\n" +
                                     self.Messages["Names9"] + ": " + str(self.selected_vid.Track[1][6]))


                if not self.selected_vid.Tracked:
                    self.Beginn_track.config(state="active", bg="SystemButtonFace", activebackground="SystemButtonFace")
                    self.bouton_check_track.config(state="disable")
                    self.bouton_analyse_track.config(state="disable")
                else:
                    self.bouton_check_track.config(state="active")
                    point_pos = self.selected_vid.Name.rfind(".")
                    file_tracked_with_corr = self.selected_vid.Folder + "/corrected_coordinates/" + self.selected_vid.Name[:point_pos] + "_Corrected.csv"
                    if os.path.isfile(file_tracked_with_corr):
                        self.bouton_check_track.config(activebackground="#3aa6ff", bg="#3aa6ff")
                    else:
                        self.bouton_check_track.config( activebackground="#ff8a33", bg="#ff8a33")

                    self.bouton_analyse_track.config(state="active")

        for Row in self.list_projects:
            Row.update_selection()

    def press_fenetre(self, event):
        self.press_position = pyautogui.position()
        self.parent.win_old_pos = (self.parent.winfo_x(), self.parent.winfo_y())

    def move_fenetre(self, event):
        if not self.fullscreen_status:
            self.actual_pos = pyautogui.position()
            deplacement = ("", str(self.actual_pos[0] - self.press_position[0] + self.parent.win_old_pos[0]),
                           str(self.actual_pos[1] - self.press_position[1] + self.parent.win_old_pos[1]))
            self.parent.geometry("+".join(deplacement))

    def fermer(self):
        self.quitter = True
        self.parent.destroy()

    def fullscreen(self):
        if not self.fullscreen_status:
            self.fullscreen_status=True
            monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
            work_area = monitor_info.get("Work")
            self.parent.geometry("{0}x{1}+0+0".format(work_area[2], work_area[3]))

        else:
            self.fullscreen_status=False
            self.parent.geometry("1250x720")
        self.update()

        self.afficher_projects()

    def save(self):
        try:
            with open(self.file_to_save, 'wb') as fp:
                data_to_save = dict(Project_name=self.project_name.get(),Folder=self.folder,Videos= self.liste_of_videos)
                pickle.dump(data_to_save, fp)
        except Exception as e:
            print(e)
            messagebox.showinfo(message=self.Messages["GWarn3"], title=self.Messages["GWarnT3"])


    def close_file(self):
        if not self.folder == None:
            answer = messagebox.askyesnocancel(self.Messages["General17"], self.Messages["General18"])
            if answer:
                self.save()
                self.close()
            elif answer == False:
                self.close()
            else:
                pass

    def close(self):
        self.project_name.set("Untitled")
        self.liste_of_videos=[]
        self.list_projects=[]
        self.folder=None

        self.afficher_projects()

        self.rows_optns.grid_forget()
        self.bouton_analyse_track.grid_forget()
        self.bouton_check_track.grid_forget()
        self.BExtend_track.grid_forget()
        self.Show_T_infos.grid_forget()
        self.Beginn_track.grid_forget()
        self.rows_optns.grid_forget()

        self.default_message = self.Messages["Welcome"]
        self.bouton_Save.config(state="disable")
        self.bouton_Close.config(state="disable")



    def open_file(self):
        try:
            if not self.folder==None:
                answer = messagebox.askyesnocancel(self.Messages["General17"], self.Messages["General18"])
                if answer:
                    self.save()
                    self.open_file2()
                elif answer==False:
                    self.open_file2()
                else:
                    pass
            else:
                self.open_file2()
        except:
            self.open_file2()


    def open_file2(self):
        try:
            self.file_to_open = filedialog.askopenfilename(filetypes=(("Bio-Track", "*.btr"),))
            with open(self.file_to_open, 'rb') as fp:
                data_to_load = pickle.load(fp)
                self.project_name.set(data_to_load["Project_name"])
                self.folder = data_to_load["Folder"]
                self.liste_of_videos = data_to_load["Videos"]
            #On vérifie si on a bien les coordonnées:
            for V in self.liste_of_videos:
                V.check_coos()
            self.load_projects()
            self.rows_optns.grid(row=0, column=0, sticky="sewn")
            if len(self.liste_of_videos)>0:
                self.default_message = self.Messages["General1"]
            else :
                self.default_message = self.Messages["General0"]
            self.user_message.set(self.default_message)
            self.file_to_save=self.file_to_open
            self.bouton_Save.config(state="active")
            if len(self.liste_of_videos)>0:
                self.grid_param_track()

            self.bouton_Close.config(state="active")

        except:
            self.default_message = self.Messages["General10"]
            self.user_message.set(self.default_message)

    def stab_all(self):
        for Vid in self.liste_of_videos:
            Vid.Stab=True
            if Vid.Back[0]:
                Vid.Back[0]=False
                Vid.Back[1]=[]
        self.update_projects()

    def update_lan(self,*args):
        try:
            if self.folder!=None:
                answer = messagebox.askyesnocancel(self.Messages["General8"], self.Messages["General9"])
                if answer:
                    f = open("Files/Language", "w")
                    f.write(self.Language.get())
                    f.close()
                    self.save()
                    self.fermer()
                elif answer==False:
                    f = open("Files/Language", "w")
                    f.write(self.Language.get())
                    f.close()
                    self.fermer()
                else:
                    self.Language.set(self.LanguageO)
            else:
                f = open("Files/Language", "w")
                f.write(self.Language.get())
                f.close()
                self.fermer()

        except:
            f = open("Files/Language", "w")
            f.write(self.Language.get())
            f.close()
            self.fermer()
