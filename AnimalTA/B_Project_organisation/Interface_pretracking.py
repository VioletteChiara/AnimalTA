import datetime
import ntpath
import pyautogui
from tkinter import *
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import ttk
import pickle
import shutil
from AnimalTA.C_Pretracking.a_Parameters_track import Interface_parameters_track
from AnimalTA.A_General_tools import Interface_extend, Interface_Save_Vids, Interface_Vids_for_convert, UserMessages, \
    User_help, Interface_selection_track_and_analyses, Class_loading_Frame, Interface_info, \
    Interface_settings, Interface_Change_Folder, Color_settings, Message_simple_question as MsgBox
from AnimalTA.E_Post_tracking.a_Tracking_verification import Interface_Check
from AnimalTA.E_Post_tracking.b_Analyses import Interface_Analyses, Interface_sequences
from AnimalTA.F_Behaviors_Neuro import Interface_Behavior
from AnimalTA.B_Project_organisation import Class_Row_Videos, Table_summary, Import_data
from AnimalTA.G_Specials import Extension_Roi
import time
from AnimalTA import Class_Video
import os
from functools import partial
import decord
from copy import deepcopy
from ctypes import windll
from django.utils.crypto import get_random_string
import copy



class Interface(Frame):
    """This is the main Frame of the project, it contains:
    1. A homemade menu option to allow to add, remove video, change the language, save projectes, open projects...
    2. A table with one row per video (see Class_Row_Videos
    3. A set of options to set tracking parameters, correct the trajectories or analyses them."""
    def __init__(self, parent, current_version, new_update, liste_of_videos=[], **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.list_colors = Color_settings.My_colors.list_colors
        self.config(background=Color_settings.My_colors.list_colors["Main_cnt"], bd=3, highlightthickness=0)
        self.parent = parent
        self.current_version=current_version
        self.posX=0#At the beginning, horizontal scrollbar is at location 0

        if new_update!=None:
            self.show_infos(new_update)

        # Import language
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        # Window's management
        self.project_name = StringVar()
        self.project_name.set(self.Messages["Untitled"])
        self.fullscreen_status = False
        self.pressed_bord = [None, None] #To allow user to change the window size
        self.changing = False# A flag to determine whether the user is changing the size of the window or not
        self.list_projects=[]#The list of videos to be displayed

        self.selected_vid = None
        self.Current_capture=None
        self.first = True #If an action have already be done or not

        self.folder = None #Where is the current directory

        self.import_values = {"Sep": "\t", "Header": 0, "Fr_col":"", "Time_col":"","Ind_col":True,"ID_col":"","Col_x":"", "Col_y":""}#The defaults value for importing data

        self.wait_for_vid = False  # For fusion process, if we expect the user to select a second vid, = True
        self.liste_of_videos = liste_of_videos
        self.Infos_track = StringVar()
        self.no_track = self.Messages["General7"]
        self.Infos_track.set(self.Messages["General2"])
        self.moving_proj_speed=0#How fast the row of videos is moving when pressing Up/Down keys
        self.liste_speeds=[0]
        val=0
        for i in range(10):
            self.liste_speeds.append(val+10-i)
            val=val+10-i

        self.parent.bind("<Button-1>", self.press_change_size)
        self.parent.bind("<B1-Motion>", self.change_size)
        self.parent.bind("<Motion>", self.change_cursor)
        self.parent.bind("<ButtonRelease-1>", self.release_size)

        # Canvas:
        # Main canvas
        self.canvas_title_bar = Canvas(self, bd=2, highlightthickness=1, relief='ridge', **Color_settings.My_colors.Frame_Base)
        self.canvas_title_bar.grid(row=0, column=0, columnspan=3, sticky="new")
        self.canvas_title_bar.columnconfigure(0, weight=1)
        self.canvas_title_bar.columnconfigure(1, weight=1)
        self.canvas_title_bar.columnconfigure(2, weight=100)
        self.canvas_title_bar.columnconfigure(3, weight=1)
        self.canvas_title_bar.columnconfigure(4, weight=1)
        self.canvas_title_bar.bind("<Button-1>", self.press_fenetre)
        self.canvas_title_bar.bind("<B1-Motion>", self.move_fenetre)

        # Frame containing options and the table of videos
        self.canvas_main = Frame(self, bd=2, highlightthickness=1, relief='ridge', **Color_settings.My_colors.Frame_Base)
        self.canvas_main.grid(row=1, column=0, sticky="nsew")
        Grid.rowconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 0, weight=1)

        # User help:
        self.HW = User_help.Help_win(self.canvas_main, default_message=self.Messages["Welcome"], legend={self.Messages["General23"]:self.list_colors["Button_ready"],self.Messages["General24"]:self.list_colors["Button_half"],self.Messages["General25"]:self.list_colors["Button_done"]},
                                     shortcuts={self.Messages["Short_Mousewheel"]:self.Messages["Short_Mousewheel_G"],
                                                self.Messages["Short_arrows"]:self.Messages["Short_arrows_G"],
                                                self.Messages["Short_del"]:self.Messages["Short_del_G"],
                                                self.Messages["Short_shift_del"]: self.Messages["Short_multi_del"], }, width=250)
        self.HW.grid(row=0, column=1, sticky="nsew")

        self.canvas_show = Frame(self.canvas_main, bd=0, highlightthickness=0, relief='ridge', **Color_settings.My_colors.Frame_Base)
        self.canvas_show.grid(row=0, column=0, rowspan=2, sticky="nsew")

        self.Sub_table=Frame(self.canvas_main, bd=0, highlightthickness=0, **Color_settings.My_colors.Frame_Base)
        Grid.columnconfigure(self.Sub_table,0,weight=1)
        Grid.columnconfigure(self.Sub_table, 1, weight=10000)
        Grid.columnconfigure(self.Sub_table, 2, weight=1)


        Summary_B=Button(self.Sub_table, text=self.Messages["GButton20"], command=self.show_summary,**Color_settings.My_colors.Button_Base)
        Summary_B.grid(row=0, column=1, sticky="nsew")
        Summary_B.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["GButton22"]))
        Summary_B.bind("<Leave>", self.HW.remove_tmp_message)


        self.move_up_button=Button(self.Sub_table, text="↑",command=self.move_up,**Color_settings.My_colors.Button_Base)
        self.move_down_button=Button(self.Sub_table, text="↓", command=self.move_down,**Color_settings.My_colors.Button_Base)
        self.move_up_button.grid(row=0, column=0, sticky="nsew")
        self.move_down_button.grid(row=0, column=2, sticky="nsew")

        self.move_up_button.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["GButton23"]))
        self.move_up_button.bind("<Leave>", self.HW.remove_tmp_message)

        self.move_down_button.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["GButton23"]))
        self.move_down_button.bind("<Leave>", self.HW.remove_tmp_message)



        self.rows_optns = Frame(self.canvas_show, bd=0, highlightthickness=0, relief='ridge', **Color_settings.My_colors.Frame_Base)
        Grid.rowconfigure(self.rows_optns, 0, weight=1)
        Grid.columnconfigure(self.rows_optns, 1, weight=1)
        Grid.columnconfigure(self.rows_optns, 2, weight=1)
        Grid.columnconfigure(self.rows_optns, 3, weight=1)
        Grid.columnconfigure(self.rows_optns, 4, weight=1)
        Grid.columnconfigure(self.rows_optns, 5, weight=1)
        Grid.columnconfigure(self.rows_optns, 6, weight=100)
        Grid.columnconfigure(self.rows_optns, 7, weight=1)


        self.canvas_next_step = Frame(self.canvas_main, bd=0, highlightthickness=0, **Color_settings.My_colors.Frame_Base)
        self.canvas_next_step.grid(row=1, column=1, rowspan=2, sticky="nsew")
        Grid.columnconfigure(self.canvas_next_step, 0, weight=1)

        Grid.columnconfigure(self.canvas_main, 0, weight=1000)
        Grid.columnconfigure(self.canvas_main, 1, weight=1, minsize=300)
        Grid.rowconfigure(self.canvas_main, 0, weight=1000)
        Grid.rowconfigure(self.canvas_main, 1, weight=1)

        # Options to interact with the project:
        self.Optns_Lab = Entry(self.rows_optns, textvar=self.project_name, relief="ridge", font=("Arial", 14), **Color_settings.My_colors.Entry_Base)
        self.Optns_Lab.grid(row=0, column=0, sticky="w")
        #Add a video
        self.bouton_Add = Button(self.rows_optns, text=self.Messages["GButton7"], command=self.add_video,**Color_settings.My_colors.Button_Base)
        self.bouton_Add.grid(row=0, column=1, sticky="nswe")
        #Do the tracking of some videos
        self.bouton_make_track = Button(self.rows_optns, text=self.Messages["GButton10"], command=self.begin_track,**Color_settings.My_colors.Button_Base)
        self.bouton_make_track.grid(row=0, column=4, sticky="nswe")
        self.bouton_make_track.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General19"]))
        self.bouton_make_track.bind("<Leave>", self.HW.remove_tmp_message)
        #Run the analyses of trajectories
        self.bouton_make_analyses = Button(self.rows_optns, text=self.Messages["GButton15"], command=self.run_analyses,**Color_settings.My_colors.Button_Base)
        self.bouton_make_analyses.grid(row=0, column=5, sticky="nswe")
        self.bouton_make_analyses.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General20"]))
        self.bouton_make_analyses.bind("<Leave>", self.HW.remove_tmp_message)


        #For a future update
        #Import data from other trackings
        self.bouton_import_dat = Button(self.rows_optns, text=self.Messages["Import_data0"], command=self.import_dat,**Color_settings.My_colors.Button_Base)
        #self.bouton_import_dat.grid(row=0, column=7, sticky="nse")
        self.bouton_import_dat.config(state="disable")
        self.bouton_import_dat.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General26"]))
        self.bouton_import_dat.bind("<Leave>", self.HW.remove_tmp_message)

        #Export selected video
        self.bouton_save_TVid = Button(self.rows_optns, text=self.Messages["GButton18"], command=self.export_vid,**Color_settings.My_colors.Button_Base)
        self.bouton_save_TVid.grid(row=0, column=8, sticky="nse")
        self.bouton_save_TVid.config(state="disable")
        self.bouton_save_TVid.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["GButton19"]))
        self.bouton_save_TVid.bind("<Leave>", self.HW.remove_tmp_message)

        #Special feature, not to be distributed
        #self.bouton_Roi = Button(self.rows_optns, text="Heart Beat", command=self.Roi_extension, background="yellow")
        #self.bouton_Roi.grid(row=0, column=9, sticky="nse")

        #The video table is created here and is associated with a scrollbar
        self.canvas_rows = Frame(self.canvas_show, bd=0, highlightthickness=0, relief='ridge', **Color_settings.My_colors.Frame_Base)
        Grid.columnconfigure(self.canvas_rows,0,weight=1)


        self.vsh = ttk.Scrollbar(self.canvas_show, orient="horizontal", command=self.update_posX)
        self.vsh.bind("<Motion>", self.first_action)
        self.vsh.grid(row=2, column=0, sticky="we")
        self.canvas_rows.grid(row=1, column=0, sticky="nsew")
        self.vsv = Scale(self.canvas_show, orient="vertical", from_=0, to=0, **Color_settings.My_colors.Scale_Base)
        self.vsv.bind("<ButtonRelease-1>", self.afficher_projects)
        self.vsv.grid(row=1, column=1, sticky="ns")

        Grid.columnconfigure(self.canvas_show, 0, weight=1)
        Grid.rowconfigure(self.canvas_show, 1, weight=1)

        self.canvas_rows.bind("<Configure>", self.onFrameConfigure)
        self.bind_everything()

        # Widgets:
        # Title bar
        #Name of the program
        self.Nom_Logiciel = Label(self.canvas_title_bar, fg="#fff3ca", text="AnimalTA", bg="#882ecc",
                                  font=("Noto Sans", 12, "bold"))
        self.Nom_Logiciel.grid(row=0, column=0, sticky="w")
        #More information about AnimalTA:
        B_info=Button(self.canvas_title_bar, text="?",command=partial(self.show_infos, new_update),**Color_settings.My_colors.Button_Base)
        B_info.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General28"]))
        B_info.bind("<Leave>", self.HW.remove_tmp_message)
        B_info.grid(row=0, column=1, sticky="w")

        self.B_settings=Button(self.canvas_title_bar, text="...",command=self.show_settings,**Color_settings.My_colors.Button_Base)
        self.B_settings.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General29"]))
        self.B_settings.bind("<Leave>", self.HW.remove_tmp_message)
        self.B_settings.grid(row=0, column=2, sticky="w")

        #Create new project
        self.bouton_New = Button(self.canvas_title_bar, text=self.Messages["GButton1"], command=self.new_project,**Color_settings.My_colors.Button_Base)
        self.bouton_New.grid(row=0, column=3, sticky="e")
        #Open existing project
        self.bouton_Open = Button(self.canvas_title_bar, text=self.Messages["GButton2"], command=self.open_file,**Color_settings.My_colors.Button_Base)
        self.bouton_Open.grid(row=0, column=4, sticky="e")
        #Close the current project
        self.bouton_Close = Button(self.canvas_title_bar, text=self.Messages["GButton17"], command=self.close_file,**Color_settings.My_colors.Button_Base)
        self.bouton_Close.grid(row=0, column=5, sticky="e")
        self.bouton_Close.config(state="disable")#Only if there is a project open
        # Save the current project
        self.bouton_Save = Button(self.canvas_title_bar, text=self.Messages["GButton3"], command=self.save,**Color_settings.My_colors.Button_Base)
        self.bouton_Save.grid(row=0, column=6, sticky="e")
        self.bouton_Save.config(state="disable")#Only if there is a project open
        #Change the language
        OptionLan = list(UserMessages.Mess.keys())
        self.bouton_Lang = OptionMenu(self.canvas_title_bar, self.Language, *OptionLan, command=self.update_lan)
        self.bouton_Lang["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
        self.bouton_Lang.config(**Color_settings.My_colors.Button_Base)
        self.bouton_Lang.grid(row=0, column=7, sticky="e")
        self.canvas_title_bar.columnconfigure(8, minsize=25)
        #Minimize the program
        self.bouton_minimize = Button(self.canvas_title_bar, text="—", command=self.minimize,**Color_settings.My_colors.Button_Base)
        self.bouton_minimize.grid(row=0, column=9, sticky="e")
        #Fullscreen
        self.bouton_fullscreen = Button(self.canvas_title_bar, text=u'\u2B1C', command=self.fullscreen,**Color_settings.My_colors.Button_Base)
        self.bouton_fullscreen.grid(row=0, column=10, sticky="e")
        #Close AnimalTA
        self.bouton_Fermer = Button(self.canvas_title_bar, text="X", fg="white", bg="red", command=self.fermer)
        self.bouton_Fermer.grid(row=0, column=11, sticky="e")

        #Options for the videos outside of the table
        #Define the optiosn for tracking
        self.Beginn_track = Button(self.canvas_next_step, text=self.Messages["GButton4"], command=self.Beg_track,**Color_settings.My_colors.Button_Base)
        self.Beginn_track.config(state="disable")
        self.Beginn_track.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General11"]))
        self.Beginn_track.bind("<Leave>", self.HW.remove_tmp_message)
        #Show the defined options
        self.Show_T_infos = Label(self.canvas_next_step, textvariable=self.Infos_track, wraplength=250, **Color_settings.My_colors.Label_Base, bd=0, highlightthickness=0)
        #Apply the tracking parameters to other videos
        self.BExtend_track = Button(self.canvas_next_step, text=self.Messages["GButton5"], command=self.extend_track,**Color_settings.My_colors.Button_Base)
        self.BExtend_track.config(state="disable")
        self.BExtend_track.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General12"]))
        self.BExtend_track.bind("<Leave>", self.HW.remove_tmp_message)
        #Correct the trajectories
        self.bouton_check_track = Button(self.canvas_next_step, text=self.Messages["GButton13"],
                                         command=self.check_track,**Color_settings.My_colors.Button_Base)
        self.bouton_check_track.config(state="disable")
        self.bouton_check_track.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General13"]))
        self.bouton_check_track.bind("<Leave>", self.HW.remove_tmp_message)
        #Prepare the analyses of the trajectories
        self.bouton_analyse_track = Button(self.canvas_next_step, text=self.Messages["GButton14"],
                                           command=self.analyse_track,**Color_settings.My_colors.Button_Base)
        self.bouton_analyse_track.config(state="disable")
        self.bouton_analyse_track.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General14"]))
        self.bouton_analyse_track.bind("<Leave>", self.HW.remove_tmp_message)


        #Allow to combine with BORIS or similar programs
        '''
        self.bouton_add_event = Button(self.canvas_next_step, text=self.Messages["GButton20"],command=self.add_events)
        self.bouton_add_event.config(state="disable")
        self.bouton_add_event.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General22"]))
        self.bouton_add_event.bind("<Leave>", self.HW.remove_tmp_message)
        '''

        #The info panel will blin when AnimalTA is opened
        self.HW.get_attention(0)

        self.autosave()

    def set_appwindow(self, root):

        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080

        hwnd = windll.user32.GetParent(root.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        root.wm_withdraw()
        root.after(10, lambda: root.wm_deiconify())

    ##Information about versio, citation and guidelines
    def show_infos(self, new_update=None):
        info_win=Toplevel(self.parent)
        info_win.title("Information")
        interface = Interface_info.Information_panel(parent=info_win, current_version=self.current_version, new_update=new_update)

    def show_settings(self):
        info_win=Toplevel(self.parent)
        info_win.title(self.Messages["SettingsT"])
        interface = Interface_settings.Settings_panel(parent=info_win, main=self)

    def move_up(self):
        if self.selected_vid != None:
            Indx = self.liste_of_videos.index(self.selected_vid)
            if Indx>0:
                self.liste_of_videos[Indx],self.liste_of_videos[Indx-1]=self.liste_of_videos[Indx-1],self.liste_of_videos[Indx]
                self.afficher_projects()


    def move_down(self):
        if self.selected_vid != None:
            Indx = self.liste_of_videos.index(self.selected_vid)
            if Indx < (len(self.liste_of_videos)-1):
                self.liste_of_videos[Indx], self.liste_of_videos[Indx + 1] = self.liste_of_videos[Indx + 1], self.liste_of_videos[Indx]
                self.afficher_projects()


    def show_summary(self):
        info_win=Toplevel(self.parent)
        info_win.title(self.Messages["GButton21"])
        interface = Table_summary.table(parent=info_win, main=self)

    ##Window management
    def press_change_size(self, event):
        # We check of the user pressed on a border of the window ton allow to change its size
        largeur = 10
        if event.widget == self and not self.fullscreen_status:
            if event.y > self.parent.winfo_height() - largeur and event.y < self.parent.winfo_height():
                self.pressed_bord = [0, pyautogui.position()[1]]  # 0=bottom, then clockwise
                self.size_before = [self.parent.winfo_width(), self.parent.winfo_height()]

            elif event.x < largeur and event.x > 0:
                self.pressed_bord = [1, pyautogui.position()[0]]  # 0=bottom, then clockwise
                self.size_before = [self.parent.winfo_width(), self.parent.winfo_height()]
                self.parent.win_old_pos = (self.parent.winfo_x(), self.parent.winfo_y())

            elif event.y < largeur and event.y > 0:
                self.pressed_bord = [2, pyautogui.position()[1]]  # 0=bottom, then clockwise
                self.size_before = [self.parent.winfo_width(), self.parent.winfo_height()]
                self.parent.win_old_pos = (self.parent.winfo_x(), self.parent.winfo_y())

            elif event.x > self.parent.winfo_width() - largeur and event.x < self.parent.winfo_width():
                self.pressed_bord = [3, pyautogui.position()[0]]  # 0=bottom, then clockwise
                self.size_before = [self.parent.winfo_width(), self.parent.winfo_height()]

    def change_cursor(self, event):
        # If the cursor is over the border of the frame, we change its shape to indicate that window can be resized
        largeur = 10
        if event.widget == self and not self.fullscreen_status:
            if event.y > self.parent.winfo_height() - largeur and event.y < self.parent.winfo_height():
                self.master.config(cursor="sb_v_double_arrow")
            elif event.y < largeur and event.y > 0:
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
        # Change the size of the windows following te cursor position of the user (see press_change_size function)
        if not self.fullscreen_status and event.widget == self:
            if self.pressed_bord[0] == 0:
                self.changing = True
                diff = pyautogui.position()[1] - self.pressed_bord[1]
                width_M = self.size_before[0]
                height_M = self.size_before[1] + diff
                self.parent.geometry(str(width_M) + "x" + str(height_M))

            if self.pressed_bord[0] == 1:
                self.changing = True
                pos_abs = pyautogui.position()
                diff = pyautogui.position()[0] - self.pressed_bord[1]
                width_M = self.size_before[0] - diff
                height_M = self.size_before[1]
                self.parent.geometry(str(width_M) + "x" + str(height_M))
                deplacement = ("", str(pos_abs[0]),
                               str(self.parent.win_old_pos[1]))
                self.parent.geometry("+".join(deplacement))

            if self.pressed_bord[0] == 2:
                self.changing = True
                pos_abs = pyautogui.position()
                diff = pyautogui.position()[1] - self.pressed_bord[1]
                width_M = self.size_before[0]
                height_M = self.size_before[1] - diff
                self.parent.geometry(str(width_M) + "x" + str(height_M))
                deplacement = ("", str(self.parent.win_old_pos[0]), str(pos_abs[1]))
                self.parent.geometry("+".join(deplacement))

            if self.pressed_bord[0] == 3:
                self.changing = True
                diff = pyautogui.position()[0] - self.pressed_bord[1]
                width_M = self.size_before[0] + diff
                height_M = self.size_before[1]
                self.parent.geometry(str(width_M) + "x" + str(height_M))

    def minimize(self):
        # Minimaze the main window
        self.master.overrideredirect(False)
        self.master.wm_iconify()
        self.master.bind('<FocusIn>', self.on_deiconify)

    def on_deiconify(self, *arg):
        # Come back from minimize state
        if not self.master.wm_state() == "iconic":
            self.master.overrideredirect(True)
            self.master.unbind("<FocusIn>")
            if self.fullscreen_status:
                screen_width = self.master.winfo_screenwidth()
                screen_height = self.master.winfo_screenheight()
                self.parent.geometry("{0}x{1}+0+0".format(screen_width, screen_height))
            self.master.after(10, lambda: self.set_appwindow(self.master))

    def release_size(self, event):
        # When the user release the mouse after resizing the window
        self.pressed_bord = [None, None]
        if self.changing:
            self.afficher_projects()  # We update the project view if the user changed the size of the window
        self.changing = False

    def press_fenetre(self, event):
        # Detect if teh user wants to move thh window
        self.press_position = pyautogui.position()
        self.parent.win_old_pos = (self.parent.winfo_x(), self.parent.winfo_y())

    def move_fenetre(self, event):
        # Move teh window according to cursor position
        if not self.fullscreen_status:
            self.actual_pos = pyautogui.position()
            deplacement = ("", str(self.actual_pos[0] - self.press_position[0] + self.parent.win_old_pos[0]),
                           str(self.actual_pos[1] - self.press_position[1] + self.parent.win_old_pos[1]))
            self.parent.geometry("+".join(deplacement))

    def fermer(self):
        # Close the window
        self.parent.destroy()

    def fullscreen(self):
        # Sett fullscreen mode
        if not self.fullscreen_status:
            self.fullscreen_status = True
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            self.parent.geometry("{0}x{1}+0+0".format(screen_width, screen_height))

        else:
            self.fullscreen_status = False
            self.parent.geometry("1250x720")
        self.update()

        try:#We show the table rows only if the table is visible and not replaced by another window
            self.Second_Menu
        except:
            self.afficher_projects()

    def update_lan(self, *args):
        # Change the language
        if self.folder != None:
            question = MsgBox.Messagebox(parent=self, title=self.Messages["General8"],
                                       message=self.Messages["General9"], Possibilities=[self.Messages["Yes"],self.Messages["No"],self.Messages["Cancel"]])
            self.wait_window(question)
            answer = question.result
            if answer==0:
                f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "w", encoding="utf-8")
                f.write(self.Language.get())
                f.close()
                self.save()
                self.fermer()
            elif answer == 1:
                f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "w", encoding="utf-8")
                f.write(self.Language.get())
                f.close()
                self.fermer()
            else:
                self.Language.set(self.LanguageO)
        else:
            f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "w", encoding="utf-8")
            f.write(self.Language.get())
            f.close()
            self.fermer()



    def grid_param_track(self):
        #Open a new Frame in which the user will be able to set teh tracking parameters
        self.bouton_analyse_track.grid(row=4, column=0, sticky="swe")
        self.bouton_check_track.grid(row=3, column=0, sticky="swe")
        #self.bouton_add_event.grid(row=5, column=0, sticky="swe")
        self.BExtend_track.grid(row=2, sticky="sew")
        self.Show_T_infos.grid(row=1, sticky="sew")
        self.Beginn_track.grid(row=0, sticky="sew")

    def Change_win(self, interface=None):
        #When we want to change the mainFrame by another one
        # We remove the actual canvas
        self.canvas_show.grid_forget()
        self.canvas_next_step.grid_forget()
        self.HW.grid_forget()
        self.Sub_table.grid_forget()
        self.bouton_Lang.config(state="disable")
        self.bouton_New.config(state="disable")
        self.bouton_Save.config(state="disable")
        self.bouton_Add.config(state="disable")
        self.bouton_Open.config(state="disable")
        self.B_settings.config(state="disable")
        self.unbind_everything()


        # We add the new one
        self.Second_Menu = interface

    def unbind_everything(self):
        self.unbind_all("<Up>")
        self.unbind_all("<Down>")
        self.unbind_all("<KeyRelease-Up>")
        self.unbind_all("<KeyRelease-Down>")
        self.unbind_all("<MouseWheel>")
        self.parent.unbind_all("<Button-1>")
        self.unbind_all("<Button-1>")
        self.unbind_all("<Delete>")
        self.unbind_all("<Shift-Delete>")

    def bind_everything(self):
        self.bind_all("<Up>", self.Up)
        self.bind_all("<Down>", self.Bot)
        self.bind_all("<KeyRelease-Up>", self.Rel_UpBot)
        self.bind_all("<KeyRelease-Down>", self.Rel_UpBot)
        self.bind_all("<MouseWheel>", self.on_mousewheel)
        self.parent.bind_all("<Button-1>", self.remove_Fus)
        self.bind_all("<Button-1>", self.remove_Fus)
        self.bind_all("<Delete>", partial(self.supr_video, None, True))
        self.bind_all("<Shift-Delete>", self.supr_multi_video)



    def return_main(self):
        #When we come back from another frame and want to show this one
        # We add the actual canvas
        self.canvas_show.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.HW.grid(row=0, column=1, sticky="nsew")
        self.Sub_table.grid(row=2, column=0, sticky="nsew")
        self.canvas_next_step.grid(row=1, column=1, rowspan=2, sticky="nsew")
        self.update_selections()

        self.bouton_Lang.config(state="normal")
        self.bouton_New.config(state="normal")
        self.bouton_Save.config(state="normal")
        self.bouton_Add.config(state="normal")
        self.bouton_Open.config(state="normal")
        self.B_settings.config(state="normal")

        self.bind_everything()

        # We remove the new one
        self.Second_Menu.grid_forget()
        self.Second_Menu.destroy()
        del self.Second_Menu

        self.afficher_projects()

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.update_row_display()
        self.moveX()

    def update_posX(self, event0=None, event1=0, event2=None):
        self.posX=event1
        self.moveX()

    ##Project management
    def save(self):
        # Save the project
        try:
            load_frame= Class_loading_Frame.Loading(self)#Progression bar
            load_frame.grid()
            load_frame.show_load(0)
            shutil.copyfile(self.file_to_save, self.file_to_save+"old")
            load_frame.show_load(0.5)
            #This is a security to ensure that the old file will not be deleted before ensurong the new one can be proprly saved

            with open(self.file_to_save , 'wb') as fp:
                data_to_save = dict(Project_name=self.project_name.get(), Folder=self.folder, Videos=self.liste_of_videos, ID_project=self.ID_project, Importation_values=self.import_values)
                pickle.dump(data_to_save, fp)

            load_frame.show_load(1)

            #If there was no problem during the save, we delete the security copy
            os.remove(self.file_to_save+"old")

            load_frame.destroy()
            del load_frame

        except Exception as e:
            #If the program was not properly saved, we restore the security copy
            if os.path.isfile(self.file_to_save+"old"):
                os.remove(self.file_to_save)
                os.rename(self.file_to_save+"old",self.file_to_save)

            question = MsgBox.Messagebox(parent=self, title=self.Messages["GWarnT3"],
                                       message=self.Messages["GWarn3"], Possibilities=[self.Messages["Continue"]])
            self.wait_window(question)

    def close_file(self, ask=True):
        # Ask if teh user wants to save the project and then close it
        if not self.folder == None:
            if ask:
                question = MsgBox.Messagebox(parent=self, title=self.Messages["General17"],
                                             message=self.Messages["General18"], Possibilities=[self.Messages["Yes"], self.Messages["No"], self.Messages["Cancel"]])
                self.wait_window(question)
                answer = question.result

            else:
                answer=False

            if answer==0:
                self.save()
                self.close()
            elif answer == 1:
                self.close()
            else:
                pass

    def close(self):
        # Close the project
        self.project_name.set(self.Messages["Untitled"])
        self.liste_of_videos = []
        self.folder = None
        self.afficher_projects()

        self.rows_optns.grid_forget()
        self.bouton_analyse_track.grid_forget()
        self.bouton_check_track.grid_forget()
        #self.bouton_add_event.grid_forget()
        self.BExtend_track.grid_forget()
        self.Show_T_infos.grid_forget()
        self.Beginn_track.grid_forget()
        self.rows_optns.grid_forget()

        self.default_message = self.Messages["Welcome"]
        self.bouton_Save.config(state="disable")
        self.bouton_Close.config(state="disable")
        self.Sub_table.grid_forget()

    def open_file(self):
        # If a project was already open, ask if the user wants to save it and then open another one
        try:
            if not self.folder == None:
                question = MsgBox.Messagebox(parent=self, title=self.Messages["General17"],
                                             message=self.Messages["General18"], Possibilities=[self.Messages["Yes"], self.Messages["No"], self.Messages["Cancel"]])
                self.wait_window(question)
                answer = question.result

                if answer==0:
                    self.save()
                    self.open_file2()
                elif answer == 1:
                    self.open_file2()
                else:
                    pass
            else:
                self.open_file2()
        except:
            self.open_file2()

    def open_file2(self, file=None, new_file=None):
        # Open an existing project
        try:
            if file==None:#If we open a new project, we beginn from
                if new_file==None:
                    self.file_to_open = filedialog.askopenfilename(filetypes=(("AnimalTA", "*.ata"),))
                else:
                    self.file_to_open=new_file

                with open(self.file_to_open, 'rb') as fp:
                    data_to_load = pickle.load(fp)

                self.project_name.set(data_to_load["Project_name"])
                self.folder = data_to_load["Folder"]
                self.liste_of_videos = data_to_load["Videos"]
                self.file_to_save = self.file_to_open

                try:
                    self.ID_project=data_to_load["ID_project"]
                except:
                    self.ID_project = get_random_string(length=10)

                try:
                    self.import_values=data_to_load["Importation_values"]
                except:
                    pass

            else:
                with open(file, 'rb') as fp:
                    data_to_load = pickle.load(fp)

                    # merge the two folders and the subfolders
                    for src_dir, dirs, files in os.walk(data_to_load["Folder"]):
                        cur_dir=src_dir[len(data_to_load["Folder"])+1:]
                        dst_dir=os.path.join(self.folder,cur_dir)
                        if not os.path.exists(dst_dir):
                            os.makedirs(dst_dir)
                        for file_ in files:
                            if file_[-4:]!=".avi":
                                src_file = os.path.join(src_dir, file_)
                                shutil.copy(src_file, dst_dir)
                    for V in data_to_load["Videos"]:
                        V.Folder=self.folder
                        self.liste_of_videos.append(V)


            if not os.path.exists(self.folder):
                question = MsgBox.Messagebox(parent=self, title=self.Messages["General17"],
                                             message=self.Messages["General27"],
                                             Possibilities=[self.Messages["Yes"], self.Messages["No"]])
                self.wait_window(question)
                answer = question.result

                if answer==0:
                    self.folder=filedialog.askdirectory()
                    for V in self.liste_of_videos:
                        V.Folder=self.folder

            if len(self.list_projects)==0:
                for row in range(20):
                    self.list_projects.append(Class_Row_Videos.Row_Can(parent=self.canvas_rows, main_boss=self,
                                                                       Video_file=None,
                                                                       proj_pos=row, bd=2, highlightthickness=1,
                                                                       relief='ridge'))
                    self.list_projects[row].Wrapper.create_window((4, 4), window=self.list_projects[row].canvas_main)
                self.list_projects[0].Wrapper.configure(xscrollcommand=self.vsh.set)

            to_suppr = []

            # Check that videos are still available
            for V in range(len(self.liste_of_videos)):
                # Look for all points of interest
                if self.liste_of_videos[V].Back[0]==False:
                    self.liste_of_videos[V].Back[0]=0# Old versions of animalTA had only two possible background methods (three possibilities since v2.3.2)
                elif self.liste_of_videos[V].Back[0]==True:
                    self.liste_of_videos[V].Back[0]=1

                try:
                    self.liste_of_videos[V].Stab[2]  # Old versions of animalTA did not allowed parameter changes, we check for compatibility problems
                except:
                    self.liste_of_videos[V].Stab.append([30, 3, 0.05, 200])

                try:
                    self.liste_of_videos[V].or_shape  # If the video was cropped in X or Y, we reset to its original size
                except:
                    self.liste_of_videos[V].or_shape = self.liste_of_videos[V].shape  # Old versions of AnimalTA did not had the "or_shape" attribute, this handled exception is to avoid compatibility problems

                try:
                    self.liste_of_videos[V].Cropped_sp
                except:  # Old versions of AnimalTA did not had the "Cropped_sp" attribute, this handled exception is to avoid compatibility problems
                    self.liste_of_videos[V].Cropped_sp = [False, [0, 0, self.liste_of_videos[V].or_shape[0], self.liste_of_videos[V].or_shape[1]]]

                try:
                    self.liste_of_videos[V].User_Name
                except:  # Old versions of AnimalTA did not had the "User_name" attribute, this handled exception is to avoid compatibility problems
                    self.liste_of_videos[V].User_Name = self.liste_of_videos[V].Name

                try:
                    self.liste_of_videos[V].Entrance
                except:  # Old versions of AnimalTA did not had the "Entrance" attribute, this handled exception is to avoid compatibility problems
                    self.liste_of_videos[V].Entrance = []

                try:
                    self.liste_of_videos[V].Events
                except:  # Old versions of AnimalTA did not had the "Entrance" attribute, this handled exception is to avoid compatibility problems
                    self.liste_of_videos[V].Events = []

                try:
                    self.liste_of_videos[V].Rotation
                except:  # Old versions of AnimalTA did not had the "Entrance" attribute, this handled exception is to avoid compatibility problems
                    self.liste_of_videos[V].Rotation = 0



                if self.liste_of_videos[V].Tracked:
                    try:
                        self.liste_of_videos[V].Sequences
                        #For some version, the users may have Sequences name not valid, we correct here.
                        for Ind in range(len(self.liste_of_videos[V].Sequences)):
                            for seq in self.liste_of_videos[V].Sequences[Ind]:
                                if seq[1][0] == "Begin":
                                    seq[1][0]="Beg"
                                if seq[2][0] == "Begin":
                                    seq[2][0]="Beg"
                                if seq[1][0] == "Exploration":
                                    seq[1][0] = "Explo"
                                if seq[2][0] == "Exploration":
                                    seq[2][0] = "Explo"
                                if seq[1][0] == "Spatial event":
                                    seq[1][0] = "Spatial"
                                if seq[2][0] == "Spatial event":
                                    seq[2][0] = "Spatial"
                                if seq[1][2] == "after":
                                    seq[1][2] = "aft"
                                if seq[2][2] == "after":
                                    seq[2][2] = "aft"
                                if seq[1][2] == "before":
                                    seq[1][2] = "bef"
                                if seq[2][2] == "before":
                                    seq[2][2] = "bef"
                                if "First time in " in seq[1][3]:
                                    string=seq[1][3]
                                    seq[1][3] = string.replace("First time in ", "First_in_")
                                if "First time in " in seq[2][3]:
                                    string=seq[2][3]
                                    seq[2][3] = string.replace("First time in ", "First_in_")

                                if "Last time in " in seq[1][3]:
                                    string=seq[1][3]
                                    seq[1][3] = string.replace("Last time in ", "Last_in_")
                                if "Last time in " in seq[2][3]:
                                    string=seq[2][3]
                                    seq[2][3] = string.replace("Last time in ", "Last_in_")

                    except:  # Old versions of AnimalTA did not had the "Entrance" attribute, this handled exception is to avoid compatibility problems
                        self.liste_of_videos[V].Sequences = []
                        for Ar in range(len(self.liste_of_videos[V].Track[1][6])):
                            for i in range(self.liste_of_videos[V].Track[1][6][Ar]):
                                self.liste_of_videos[V].Sequences.append([Interface_sequences.full_sequence])
                    try:
                        self.liste_of_videos[V].Sequences_saved
                    except:
                        self.liste_of_videos[V].Sequences_saved = copy.deepcopy(self.liste_of_videos[V].Sequences)


                '''
                try:
                    self.liste_of_videos[V].Morphometrics
                except:
                    if self.liste_of_videos[V].Tracked:
                       
                        self.liste_of_videos[V].Morphometrics = []
                        for Ar in range(len(self.liste_of_videos[V].Track[1][6])):
                            for i in range(self.liste_of_videos[V].Track[1][6][Ar]):
                                self.liste_of_videos[V].Morphometrics.append([])
                '''
                if len(self.liste_of_videos[V].Track[1])<8:#Old versions of AnimalTA did not allow for lightning corrections or variable number of targets
                    self.liste_of_videos[V].Track[1].append(False)#No lightning correction
                    self.liste_of_videos[V].Track[1].append(True)#Fixed number of tragets
                if len(self.liste_of_videos[V].Track[1])<9:
                    self.liste_of_videos[V].Track[1].append(True)#Fixed number of tragets
                if len(self.liste_of_videos[V].Track[1])<10:
                    self.liste_of_videos[V].Track[1].append(False)#Flicker correction
                if len(self.liste_of_videos[V].Track[1])<11:
                    self.liste_of_videos[V].Track[1].append([0,0,0])#black/colored background

                try:
                    if len(self.liste_of_videos[V].Track[1][10])<3:
                        self.liste_of_videos[V].Track[1][10].append(0)# background
                except:
                    self.liste_of_videos[V].Track[1][10]=[0,0,0]

                if len(self.liste_of_videos[V].Analyses)<5:
                    self.liste_of_videos[V].Analyses.append([[],[],[]])#Deformation of images

                for Arena in self.liste_of_videos[V].Mask[1]:
                    if len(Arena)==4:
                        Arena.append(True)

                '''
                ####For bebugging pruposes only!
                name=self.liste_of_videos[V].File_name[-18:]#For debugging other users problems
                self.liste_of_videos[V].File_name="G:/"+name#For debugging
                self.liste_of_videos[V].Fusion[0][1] = "G:/" + name#For debugging
                self.folder="G:/Project_folder_01012023_03012023_M"#For debugging
                '''


                everything_ok=True
                while not everything_ok:
                    if not Interface_Change_Folder.check_vid(self.liste_of_videos[V]):
                        file_name=ntpath.basename(self.liste_of_videos[V].File_name)
                        if os.path.isfile(self.folder+"/converted_vids/"+file_name):
                            self.liste_of_videos[V].File_name=self.folder+"/converted_vids/"+file_name
                            for F in range(len(self.liste_of_videos[V].Fusion)):
                                if os.path.isfile(self.folder + "/converted_vids/" + ntpath.basename(self.liste_of_videos[V].Fusion[F][1])):
                                    self.liste_of_videos[V].Fusion[F][1] = self.folder+"/converted_vids/"+ ntpath.basename(self.liste_of_videos[V].Fusion[F][1])

                            if Interface_Change_Folder.check_vid(self.liste_of_videos[V]):
                                everything_ok = True

                        else:
                            question = MsgBox.Messagebox(parent=self, title=self.Messages["GWarnT5"],
                                                         message=self.Messages["GWarn5"].format(self.liste_of_videos[V].File_name),
                                                         Possibilities=[self.Messages["GWarn5A"], self.Messages["GWarn5B"], self.Messages["Cancel"]])
                            self.wait_window(question)
                            answer = question.result

                            if answer==1 and self.liste_of_videos[V].clear_files():
                                to_suppr.append(V)
                                everything_ok = True
                            elif answer==0:
                                newWindow = Toplevel(self.parent)
                                interface = Interface_Change_Folder.Change_path(parent=newWindow, boss=self, new_file=self.file_to_open)
                                return
                            else:
                                self.close()
                                return
                    else:
                        everything_ok=True


            if len(to_suppr) > 0:
                for elem in sorted(to_suppr, reverse=True):
                    del self.liste_of_videos[elem]

            # Check that coordinates are still available
            for V in self.liste_of_videos:
                V.check_coos()
            self.afficher_projects()
            self.rows_optns.grid(row=0, column=0, sticky="sewn")


            if len(self.liste_of_videos) > 0:
                self.HW.default_message = self.Messages["General1"]
            else:
                self.HW.default_message = self.Messages["General0"]
            self.HW.remove_tmp_message()

            self.bouton_Save.config(state="normal")
            if len(self.liste_of_videos) > 0:
                self.grid_param_track()

            self.bouton_Close.config(state="normal")
            self.Sub_table.grid(row=2, column=0, sticky="nsew")

        except Exception as e:
            print(e)
            pass
            '''
            CustomDialog(self.master, text="An exception occurred:"+ str(type(e).__name__) + " – " + str(e), title="Debugging")
            self.HW.default_message = self.Messages["General10"]
            self.HW.remove_tmp_message()
            '''

        self.update_row_display()


    def update_row_display(self):
        for row in self.list_projects:
            row.Wrapper.configure(scrollregion=row.Wrapper.bbox("all"))
        self.vsv.config(to=len(self.liste_of_videos) - 1)

    def first_action(self, *arg):
        #At least one action has been done
        self.first = False

    def moveX(self):
        #Move the scrollbar of the video table to a specific location (pos)
        for row in self.list_projects:
            row.Wrapper.xview_moveto(str(self.posX))


    def Up(self, event):
        #Change the scrollbar position according to mouswheel
        if self.moving_proj_speed in self.liste_speeds or self.moving_proj_speed>55:
            self.vsv.set(self.vsv.get() - 1)
        self.moving_proj_speed += 1

    def Rel_UpBot(self,event):
        self.moving_proj_speed =0
        self.afficher_projects()

    def Bot(self, event):
        #Change the scrollbar position according to mouswheel
        if self.moving_proj_speed in self.liste_speeds or self.moving_proj_speed > 55:
            self.vsv.set(self.vsv.get() + 1)
        self.moving_proj_speed += 1

    def on_mousewheel(self, event):
        #Change the scrollbar position according to mouswheel
        self.vsv.set(self.vsv.get() + int(-1 * (event.delta / 120)))
        self.afficher_projects()

    def new_project(self):
        #If user wants to create a new project, we ask for saving the current one
        if not self.folder == None:
            question = MsgBox.Messagebox(parent=self, title=self.Messages["General18"],
                                         message=self.Messages["General17"],
                                         Possibilities=[self.Messages["Yes"], self.Messages["No"], self.Messages["Cancel"]])
            self.wait_window(question)
            answer = question.result

            if answer==0:
                self.save()
                self.new_project2(prev_save=True)
            elif answer == 1:
                self.new_project2()
            else:
                pass
        else:
            self.new_project2()

    def new_project2(self,prev_save=False):
        #Create a new project
        if prev_save:
            question = MsgBox.Messagebox(parent=self, title=self.Messages["GInfoT1"],
                                         message=self.Messages["GInfo1"],
                                         Possibilities=[self.Messages["Continue"]])
            self.wait_window(question)

        try:
            self.file_to_save = filedialog.asksaveasfilename(defaultextension=".ata",
                                                             initialfile="Untitled_project.ata",
                                                             filetypes=(("AnimalTA", "*.ata"),))

            if len(self.file_to_save) > 0:
                file_name = os.path.basename(self.file_to_save)
                point_pos = file_name.rfind(".")
                self.folder = os.path.join(os.path.dirname(self.file_to_save), "Project_folder_" + file_name[:point_pos])
                if not os.path.isdir(self.folder):
                    os.makedirs(self.folder)
                else:
                    shutil.rmtree(self.folder)
                    os.makedirs(self.folder)
                self.project_name.set(file_name[:-4])
                self.HW.default_message = self.Messages["General0"]
                self.HW.remove_tmp_message()
                self.liste_of_videos = []
                self.ID_project = get_random_string(length=10)

                try:
                    self.list_projects
                except:
                    self.list_projects = []

                for row in range(20):
                    self.list_projects.append(Class_Row_Videos.Row_Can(parent=self.canvas_rows, main_boss=self,
                                                                       Video_file=None,
                                                                       proj_pos=row, bd=2, highlightthickness=1,
                                                                       relief='ridge'))
                    self.list_projects[row].Wrapper.create_window((4, 4), window=self.list_projects[row].canvas_main)

                self.list_projects[0].Wrapper.configure(xscrollcommand=self.vsh.set)


                self.afficher_projects()

                self.rows_optns.grid(row=0, column=0, sticky="sewn")

                with open(self.file_to_save, 'wb') as fp:
                    data_to_save = dict(Project_name=self.project_name.get(), Folder=self.folder, Videos=self.liste_of_videos, ID_project=self.ID_project, Importation_values=self.import_values)
                    pickle.dump(data_to_save, fp)
                self.bouton_Save.config(state="normal")

        except Exception as e:
            CustomDialog(self.master, text="An exception occurred:"+ str(type(e).__name__) + " – " + str(e), title="Debugging")

    def afficher_projects(self, *arg):
        # Show the row of the table according to the scrollbar position.
        # We cannot create all the rows to avoid to consume too much memory in the case of m¡numerous videos projects
        self.posX = self.vsh.get()[0]  # Save the Xscrollbar position


        try:
            central = int(self.vsv.get())
            nb_visibles = self.canvas_show.winfo_height() / (130)
            if central>=(len(self.liste_of_videos)-1):
                central=len(self.liste_of_videos)-1

            for P in range(len(self.list_projects)):
                if self.list_projects[P].winfo_ismapped():
                    self.list_projects[P].grid_forget()

            if len(self.liste_of_videos)>0:
                Pos=0
                for who in range(central, min(len(self.liste_of_videos), int(central + round(nb_visibles)) + 1)):
                    self.list_projects[Pos].change_vid(self.liste_of_videos[who],Pos - 1)
                    if not self.list_projects[Pos].winfo_ismapped():
                        self.list_projects[Pos].grid(row=Pos, column=0, sticky="we")
                    Pos+=1



        except Exception as e:
            CustomDialog(self.master, text="An exception occurred:"+ str(type(e).__name__) + " – " + str(e), title="Debugging")
        self.moveX()  # Keep the Xscrollbar position

    def update_projects(self):
        # Update the displayed rows
        for Row in self.list_projects:
            if Row.Video!=None:
                Row.update()

    ##Actions toward videos
    def Roi_extension(self):
        if self.selected_vid != None:
            self.Change_win(Extension_Roi.Light_changes(parent=self.canvas_main, main_frame=self, boss=self.parent, Vid=self.selected_vid))

    def begin_track(self):
        #Open the window to ask for which videos to begin the tracking
        nb_vid_T = False
        for Vid in self.liste_of_videos:
            if Vid.Track[0]:
                nb_vid_T = True
                break #As soon as we found one video

        if nb_vid_T:#If there is at least one video ready
            newWindow = Toplevel(self.parent)
            interface = Interface_selection_track_and_analyses.Extend(parent=newWindow, boss=self, type="Tracking", any_tracked=True)
        else:
            #If the user did not set any tracking parameters, we aske if he want's to go for manual tracking. We left this pannel to avoid users to think the tracking was done but did not work
            question = MsgBox.Messagebox(parent=self, title=self.Messages["GErrorT1"],
                                         message=self.Messages["GError1"],
                                         Possibilities=[self.Messages["Yes"],self.Messages["No"]])
            self.wait_window(question)
            answer = question.result

            if answer==0:
                newWindow = Toplevel(self.parent)
                interface = Interface_selection_track_and_analyses.Extend(parent=newWindow, boss=self, type="Tracking", any_tracked=False)

    def run_analyses(self):
        #Open a window to ask the user to select the videos wanted for analyses
        nb_vid_T = 0
        for Vid in self.liste_of_videos:
            if Vid.Tracked:
                nb_vid_T += 1

        if nb_vid_T > 0:
            newWindow = Toplevel(self.parent)
            interface = Interface_selection_track_and_analyses.Extend(parent=newWindow, boss=self, type="Analyses")
        else:
            question = MsgBox.Messagebox(parent=self, title=self.Messages["GWarnT7"],
                                         message=self.Messages["GWarn7"],
                                         Possibilities=[self.Messages["Continue"]])
            self.wait_window(question)

    def export_vid(self):
        #Open a window for video exportation
        if self.selected_vid != None:
            self.Change_win(Interface_Save_Vids.Lecteur(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                        Vid=self.selected_vid, Video_liste=self.liste_of_videos))

    #Import data
    def import_dat(self):
        if self.selected_vid != None:
            if self.selected_vid.Tracked:
                question = MsgBox.Messagebox(parent=self, title="",
                                             message=self.Messages["GWarn1"],
                                             Possibilities=[self.Messages["Yes"], self.Messages["No"]])
                self.wait_window(question)
                answer = question.result

                if answer==0 and self.selected_vid.clear_files():
                    self.open_import()
            else:
                self.open_import()

    def open_import(self):
        self.unbind_everything()
        if self.selected_vid != None:
            data_files = filedialog.askopenfilenames()
            if len(data_files) > 0:
                newWindow = Toplevel(self.parent)
                Import_data.Int_import(newWindow, self, data_files, Vid=self.selected_vid)

    def check_track(self, speed=0):
        #Open the Frame to allow to check and correct the tracking trajectories
        #speed alows to maintain the same speed of the video reader when changing videos
        if self.selected_vid != None:
            self.Change_win(Interface_Check.Lecteur(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                    Vid=self.selected_vid, Video_liste=self.liste_of_videos, speed=speed))

    def analyse_track(self, CheckVar=None, speed=0):
        #Open a winidow to allow the user to set the analyses parameters
        #Speed indicates the video reader speed, to maintain the same when changing videos
        if self.selected_vid != None:
            self.Change_win(
                Interface_Analyses.Analyse_track(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                  Vid=self.selected_vid, Video_liste=self.liste_of_videos,
                                                  CheckVar=CheckVar, speed=speed))

    def add_events(self, CheckVar=None, speed=0):
        #Open a window to allow the user to set the analyses parameters
        #Speed indicates the video reader speed, to maintain the same when changing videos
        if self.selected_vid != None:
            self.Change_win(Interface_Behavior.Add_Behavior(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                  Vid=self.selected_vid, Video_liste=self.liste_of_videos, speed=speed))

    def extend_track(self):
        #Open a window to allow the user to apply the tracking parameters of selected video to other videos
        newWindow = Toplevel(self.parent)
        interface = Interface_extend.Extend(parent=newWindow, value=[self.selected_vid.Track[1], self.selected_vid.Back], boss=self,
                                            Video_file=self.selected_vid, type="track")

    def Beg_track(self, speed=0):
        #speed alows to maintain the same speed of the video reader when changing videos
        #open a window to allow user to select the videos to be tracked and beginn the tracking process
        if self.selected_vid != None:
            if self.selected_vid.Tracked:
                question = MsgBox.Messagebox(parent=self, title="",
                                             message=self.Messages["GWarn1"],
                                             Possibilities=[self.Messages["Yes"], self.Messages["No"]])
                self.wait_window(question)
                answer = question.result

                if answer==0 and self.selected_vid.clear_files():
                    self.Change_win(Interface_parameters_track.Param_definer(parent=self.canvas_main, main_frame=self,
                                                                             boss=self.parent,
                                                                             Video_file=self.selected_vid, speed=speed))
            else:
                self.Change_win(
                    Interface_parameters_track.Param_definer(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                             Video_file=self.selected_vid, speed=speed))

    def add_video(self):
        try:
            #Add a video inside the current project
            videos_to_add = filedialog.askopenfilenames()
            self.list_to_convert = []
            add_old=[]
            load_frame= Class_loading_Frame.Loading(self)#Progression bar
            load_frame.grid()

            Progress=0
            load_frame.show_load(Progress / len(videos_to_add))
            for file in videos_to_add:
                point_pos = file.rfind(".")
                if file[point_pos:].lower() != ".avi" and file[point_pos:].lower()!=".ata":#If it is not an avi file or an existing animalTA file, the video will be converted
                    self.list_to_convert.append(file)
                elif file[point_pos:].lower() == ".avi" and file not in [Vid.File_name for Vid in self.liste_of_videos]:#If the file was already loaded, we don't take it (user should then use the duplicate video button)
                    #We check that the video does not need to be converted (might happen with some kind of avi encoding)
                    tmp_capture = decord.VideoReader(file)
                    tmp_capture.seek(0)
                    frame0=tmp_capture[0].asnumpy()
                    tmp_capture.seek(0)
                    inf=tmp_capture.get_frame_timestamp(0)[0]
                    tmp_capture.seek(0)
                    if inf:
                        self.list_to_convert.append(file)#If it is needed to convert the video, it is added to the list
                    else:#If not, the video is added to the project
                        self.liste_of_videos.append(Class_Video.Video(File_name=file, Folder=self.folder, shape=frame0.shape, nb_fr=len(tmp_capture), fr_rate=tmp_capture.get_avg_fps()))
                    del tmp_capture
                elif file[point_pos:].lower() == ".ata":
                    add_old.append(file)

                Progress+=1
                load_frame.show_load(Progress/len(videos_to_add))

            if len(add_old)>0:
                self.open_file2(file)

            load_frame.destroy()
            del load_frame
        except:
            load_frame.destroy()
            del load_frame

        if len(self.list_to_convert) > 0:#If some videos need to be converted, we open the conversion window
            newWindow = Toplevel(self.parent)
            interface = Interface_Vids_for_convert.Convert(parent=newWindow, boss=self, list_to_convert=self.list_to_convert)

        self.update()
        self.afficher_projects()
        self.HW.default_message = self.Messages["General1"]
        self.HW.remove_tmp_message()
        self.grid_param_track()
        self.update_selections()
        self.update_row_display()

    def supr_multi_video(self, *args):
        newWindow = Toplevel(self.parent)
        interface = Interface_extend.Extend(parent=newWindow, value="NA", boss=self,
                                            Video_file=self.selected_vid, type="supr",do_self=True)

    def supr_video(self, Vid=None, warn=True, event=None, *args):
        if event==None or (event!=None and event.widget.winfo_class()!="Entry"):
            if Vid==None and self.selected_vid != None:
                Vid=self.selected_vid
            #Delete a video from the project.
            if Vid != None:
                if warn:
                    question = MsgBox.Messagebox(parent=self, title=self.Messages["GWarnT2"],
                                                 message=self.Messages["GWarn2"],
                                                 Possibilities=[self.Messages["Yes"], self.Messages["No"]])
                    self.wait_window(question)
                    answer = question.result

                if (not warn or answer==0) and Vid.clear_files():
                    # Supress associated files
                    pos_R = [index for index, Vid_L in enumerate(self.liste_of_videos) if Vid_L == Vid]
                    self.liste_of_videos.pop(pos_R[0])
                    self.afficher_projects()
                    self.selected_vid = None
                    self.update_selections()
                    self.save()

    def dupli_video(self, Vid):
        #Duplicate an existing video:
        Indx=[V for V in range(len(self.liste_of_videos)) if self.liste_of_videos[V]==Vid][0]
        new_Vid= deepcopy(Vid)

        count=1
        while new_Vid.Name==Vid.Name:
            new_name=Vid.Name + "(" + str(count) +")"
            if new_name not in [V.Name for V in self.liste_of_videos]:
                new_Vid.Name = new_name
            count+=1
            Indx+=1

        count=1
        while new_Vid.User_Name==Vid.User_Name:
            new_name=Vid.User_Name + "(" + str(count) +")"
            if new_name not in [V.User_Name for V in self.liste_of_videos]:
                new_Vid.User_Name = new_name
            count+=1


        if Vid.User_Name == Vid.Name:
            old_file_name = Vid.Name
            point_pos = old_file_name.rfind(".")
            if old_file_name[point_pos:].lower() != ".avi":
                old_file_name = Vid.User_Name
            else:
                old_file_name = old_file_name[:point_pos]
        else:
            old_file_name = Vid.User_Name

        old_coos_file = os.path.join(Vid.Folder, "Coordinates", old_file_name + "_Coordinates.csv")
        old_corrected_coos_file = os.path.join(Vid.Folder, "corrected_coordinates", old_file_name + "_Corrected.csv")

        new_coos_file = os.path.join(Vid.Folder, "Coordinates", new_Vid.User_Name + "_Coordinates.csv")
        new_corrected_coos_file = os.path.join(Vid.Folder, "corrected_coordinates", new_Vid.User_Name + "_Corrected.csv")

        if os.path.isfile(old_coos_file):
            shutil.copy(old_coos_file, new_coos_file)

        if os.path.isfile(old_corrected_coos_file):
            shutil.copy(old_corrected_coos_file, new_corrected_coos_file)

        self.liste_of_videos.insert(Indx, new_Vid)
        self.afficher_projects()
        self.update_row_display()
        self.update_selections()



    def fus_video(self):
        #When user press the "concatenate" button
        if self.wait_for_vid:# If the button was already activated, we deactivate it
            self.wait_for_vid = False
            self.HW.change_default_message(self.Messages["General1"])
            self.HW.change_tmp_message(self.Messages["General1"])
        else:# If not we activate and wait for a  second vidoe to be selected
            self.wait_for_vid = True

    def remove_Fus(self, event):
        #If the user clicks on anything else than a video or the concatenate button, we cancel the concatenation
        event.widget.focus_set()
        if self.wait_for_vid:
            self.fus_video()
        self.update_selections()

    def fusion_two_Vids(self, second_Vid):
        #When the concatenation button was activate and the user select a second video to be concatenated
        if self.selected_vid != second_Vid:#If the two videos are different
            load_frame= Class_loading_Frame.Loading(self)#Progression bar
            load_frame.grid()
            load_frame.show_load(0 / 2)

            if self.selected_vid.or_shape == second_Vid.or_shape and abs(self.selected_vid.Frame_rate[0] - second_Vid.Frame_rate[0])<0.05:#And that they share the same characteristics
                if self.selected_vid.Frame_rate[0] != second_Vid.Frame_rate[0]:
                    new_frame_rate=(self.selected_vid.Frame_rate[0] + second_Vid.Frame_rate[0]) / 2
                    question = MsgBox.Messagebox(parent=self, title="",
                                                 message=self.Messages["GWarn8"].format(self.selected_vid.Frame_rate[0], second_Vid.Frame_rate[0], new_frame_rate),
                                                 Possibilities=[self.Messages["Yes"], self.Messages["Cancel"]])
                    self.wait_window(question)
                    answer = question.result

                else:
                    new_frame_rate=self.selected_vid.Frame_rate[0]

                if self.selected_vid.Frame_rate[0] == second_Vid.Frame_rate[0] or answer==0:
                    if len(self.selected_vid.Fusion) < 2: #If it was not done yet, we prepare the info for the Fusion process (can't be done before as opencv is not accurate in frame counting and decord too slow to manage all the videos at the same time)
                        capture = decord.VideoReader(self.selected_vid.File_name, ctx=decord.cpu(0))
                        capture.seek(0)
                        self.selected_vid.Frame_nb[0] = len(capture)
                        self.selected_vid.Frame_nb[1] = self.selected_vid.Frame_nb[0] / int(round(round(self.selected_vid.Frame_rate[0], 2) / self.selected_vid.Frame_rate[1]))
                        del capture
                        load_frame.show_load(1 / 2)

                    if len(second_Vid.Fusion) < 2: #If it was not done yet, we prepare the info for the Fusion process (can't be done before as opencv is not accurate in frame counting and decord too slow to manage all the videos at the same time)
                        capture = decord.VideoReader(second_Vid.File_name, ctx=decord.cpu(0))
                        capture.seek(0)
                        second_Vid.Frame_nb[0] = len(capture)
                        second_Vid.Frame_nb[1] = second_Vid.Frame_nb[0] / int(round(round(second_Vid.Frame_rate[0], 2) / second_Vid.Frame_rate[1]))
                        del capture
                        load_frame.show_load(2 / 2)

                        # We add the second part after the first one
                        self.selected_vid.Fusion.append([self.selected_vid.Frame_nb[0], second_Vid.File_name])

                    else:#Allow fusion of fusions
                        for subVid in second_Vid.Fusion:
                            self.selected_vid.Fusion.append([subVid[0]+self.selected_vid.Frame_nb[0], subVid[1]])

                    self.selected_vid.Frame_nb[0] += second_Vid.Frame_nb[0]
                    self.selected_vid.Frame_nb[1] = self.selected_vid.Frame_nb[0] / int(round(round(self.selected_vid.Frame_rate[0], 2) / self.selected_vid.Frame_rate[1]))
                    self.selected_vid.Frame_rate[0] = new_frame_rate
                    self.selected_vid.Cropped = [False, [0, self.selected_vid.Frame_nb[0] - 1]]
                    self.selected_vid.clear_files()
                    self.supr_video(Vid=second_Vid, warn=False)
                    self.wait_for_vid = False
                    self.afficher_projects()

            else:#If the two videos does not share the same charcateristic, we inform the user
                self.wait_for_vid = False
                question = MsgBox.Messagebox(parent=self, title=self.Messages["GWarnT4"],
                                             message=self.Messages["GWarn4"],
                                             Possibilities=[self.Messages["Continue"]])
                self.wait_window(question)

            load_frame.destroy()
            del load_frame

        else:
            self.fus_video()

        self.update_row_display()
        self.update_selections()
        self.afficher_projects()

    def update_selections(self):
        #When user select a row, we update all the buttons for them to be activate/deactive and of the right color.
        #Orange= something can be done that hasn't been
        #Blue done but can be modified
        #System, secondary or finished
        if self.selected_vid == None:
            self.Infos_track.set(self.Messages["General2"])
            self.Beginn_track.config(state="normal", **Color_settings.My_colors.Frame_Base)
            self.BExtend_track.config(state="disable")
            self.bouton_check_track.config(state="disable", **Color_settings.My_colors.Frame_Base)
            self.bouton_analyse_track.config(state="disable", **Color_settings.My_colors.Frame_Base)
            #self.bouton_add_event.config(state="disable", activebackground="#f0f0f0", bg="#f0f0f0")
            self.bouton_save_TVid.config(state="disable")
            self.bouton_import_dat.config(state="disable")
            self.move_up_button.config(state="disable", **Color_settings.My_colors.Frame_Base)
            self.move_down_button.config(state="disable", **Color_settings.My_colors.Frame_Base)

        else:
            self.bouton_save_TVid.config(state="normal")
            self.bouton_import_dat.config(state="normal")
            self.move_up_button.config(state="normal", bg=self.list_colors["Moving_arrows"])
            self.move_down_button.config(state="normal", bg=self.list_colors["Moving_arrows"])

            if not self.selected_vid.Track[0] and not self.selected_vid.Tracked:
                self.Beginn_track.config(state="normal", background=self.list_colors["Button_ready"], bg=self.list_colors["Button_ready"], activeforeground=self.list_colors["Fg_Button_ready"], fg=self.list_colors["Fg_Button_ready"])
                self.Infos_track.set(self.no_track)
                self.BExtend_track.config(state="disable")
                self.bouton_check_track.config(state="disable", **Color_settings.My_colors.Frame_Base)
                self.bouton_analyse_track.config(state="disable", **Color_settings.My_colors.Frame_Base)
                #self.bouton_add_event.config(state="disable", activebackground="#f0f0f0", bg="#f0f0f0")

            else:
                self.Beginn_track.config(state="normal", activebackground=self.list_colors["Button_done"], bg=self.list_colors["Button_done"], activeforeground=self.list_colors["Fg_Button_done"], fg=self.list_colors["Fg_Button_done"])
                self.BExtend_track.config(state="normal")

                if self.selected_vid.Track[0]:#If the user choose manual tracking, we may have tracked data without tracking parameters
                    if int(self.selected_vid.Track[1][7]):
                        corr = self.Messages["Yes"]
                    else:
                        corr = self.Messages["No"]

                    if int(self.selected_vid.Track[1][9]):
                        corr_f = self.Messages["Yes"]
                    else:
                        corr_f = self.Messages["No"]

                    if self.selected_vid.Track[1][8]:#If there is a known number of targets
                        NB_tar=str(self.selected_vid.Track[1][6])
                    else:
                        NB_tar = self.Messages["Param13"]

                    self.Infos_track.set(self.Messages["Param10"] + ": " + corr + "\n" +
                                         self.Messages["Param14"] + ": " + corr_f + "\n" +
                                         self.Messages["Names1"] + ": " + str(int(self.selected_vid.Track[1][0])) + "\n" +
                                         self.Messages["Names2"] + ": " + str(int(self.selected_vid.Track[1][1])) + "\n" +
                                         self.Messages["Names3"] + ": " + str(int(self.selected_vid.Track[1][2])) + "\n" +
                                         self.Messages["Names4"] + ": " + str(
                        round(float(self.selected_vid.Track[1][3][0]), 2)) + "-" + str(
                        round(float(self.selected_vid.Track[1][3][1]), 2)) + "\n" +
                                         self.Messages["Names6"] + ": " + str(
                        round(float(self.selected_vid.Track[1][5]), 2)) + "\n" +
                                         self.Messages["Names9"] + ": " + NB_tar)

                else:
                    if self.selected_vid.Track[1][8]:#If there is a known number of targets
                        NB_tar=str(self.selected_vid.Track[1][6])
                    else:
                        NB_tar = self.Messages["Param13"]
                    self.Infos_track.set(self.Messages["Names9"] + ": " + NB_tar)

                point_pos = self.selected_vid.Name.rfind(".")
                file_tracked = os.path.join(self.selected_vid.Folder, "coordinates", self.selected_vid.Name[:point_pos] + "_Coordinates.csv")
                file_trackedP = os.path.join(self.selected_vid.Folder, "coordinates", self.selected_vid.User_Name + "_Coordinates.csv")

                if not self.selected_vid.Tracked or not(os.path.isfile(file_tracked) or os.path.isfile(file_trackedP)):
                    self.bouton_check_track.config(state="disable", **Color_settings.My_colors.Frame_Base)
                    self.bouton_analyse_track.config(state="disable", **Color_settings.My_colors.Frame_Base)
                    #self.bouton_add_event.config(state="disable", activebackground="#f0f0f0",bg="#f0f0f0")


                elif os.path.isfile(file_tracked) or os.path.isfile(file_trackedP):
                    self.Beginn_track.config(state="normal", **Color_settings.My_colors.Button_Base)
                    self.bouton_check_track.config(state="normal")
                    self.bouton_analyse_track.config(state="normal", activebackground=self.list_colors["Button_ready"], activeforeground=self.list_colors["Fg_Button_ready"], fg=self.list_colors["Fg_Button_ready"], bg=self.list_colors["Button_ready"])
                    #self.bouton_add_event.config(state="normal", activebackground="#ff8a33", bg="#ff8a33")

                    file_tracked_Corr = os.path.join(self.selected_vid.Folder, "corrected_coordinates", self.selected_vid.Name[:point_pos] + "_Corrected.csv")
                    file_trackedP_Coor = os.path.join(self.selected_vid.Folder, "corrected_coordinates", self.selected_vid.User_Name + "_Corrected.csv")

                    if ( not (os.path.isfile(file_tracked_Corr) or os.path.isfile(file_trackedP_Coor))):
                        self.bouton_check_track.config(activebackground=self.list_colors["Button_ready"], activeforeground=self.list_colors["Fg_Button_ready"], fg=self.list_colors["Fg_Button_ready"], bg=self.list_colors["Button_ready"])

                    else:
                        self.bouton_check_track.config(activebackground=self.list_colors["Button_done"], activeforeground=self.list_colors["Fg_Button_done"], fg=self.list_colors["Fg_Button_done"], bg=self.list_colors["Button_done"])
                        self.bouton_analyse_track.config(state="normal", activebackground=self.list_colors["Button_ready"], activeforeground=self.list_colors["Fg_Button_ready"], fg=self.list_colors["Fg_Button_ready"], bg=self.list_colors["Button_ready"])
                        #self.bouton_add_event.config(state="normal", activebackground="#ff8a33", bg="#ff8a33")

        try:#If the Rows are not created yet
            for Row in self.list_projects:
                Row.update_selection()
        except Exception as e:
            print(e)
            pass

    def stab_all(self):
        #Apply stabilisation to all videos of the project
        for Vid in self.liste_of_videos:
            Vid.Stab[0] = True
        self.update_projects()

    def autosave(self):
        if self.folder!=None:
            if not os.path.isdir(UserMessages.resource_path(os.path.join("AnimalTA","Files","Autosave"))):  # Create a new directory if was not existing
                os.makedirs(UserMessages.resource_path(os.path.join("AnimalTA","Files","Autosave")))

            threshold =  datetime.timedelta(days=30)
            for file in os.listdir(UserMessages.resource_path(os.path.join("AnimalTA","Files","Autosave"))):
                file_comp=UserMessages.resource_path(os.path.join("AnimalTA","Files","Autosave",file))
                filetime = os.path.getmtime(file_comp)
                now = time.time()
                delta = datetime.timedelta(seconds=now - filetime)
                if delta>threshold:
                    os.remove(file_comp)

            auto_save_location= UserMessages.resource_path(os.path.join("AnimalTA","Files","Autosave",self.project_name.get()+"_"+self.ID_project+".ata"))

            with open(auto_save_location, 'wb') as fp:
                data_to_save = dict(Project_name=self.project_name.get(), Folder=self.folder, Videos=self.liste_of_videos, ID_project=self.ID_project, Importation_values=self.import_values)
                pickle.dump(data_to_save, fp)

        self.parent.after(int(60000 * 15), self.autosave)  # time in minutes


#For debugging
#Code origin: https://stackoverflow.com/questions/35923235/is-there-a-message-box-which-displays-copy-able-text-in-python-2-7
class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, text=None):
        self.data = text
        simpledialog.Dialog.__init__(self, parent, title=title)

    def body(self, parent):

        self.text = Text(self, width=40, height=4)
        self.text.pack(fill="both", expand=True)

        self.text.insert("1.0", self.data)

        return self.text