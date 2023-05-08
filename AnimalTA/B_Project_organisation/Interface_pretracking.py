from tkinter import *
import pyautogui
from tkinter import filedialog
from tkinter import messagebox
import pickle
import shutil
from AnimalTA.C_Pretracking.a_Parameters_track import Interface_parameters_track
from AnimalTA.A_General_tools import Interface_extend, Interface_Save_Vids, Interface_Vids_for_convert, UserMessages, \
    User_help, Interface_selection_track_and_analyses, Class_loading_Frame
from AnimalTA.E_Post_tracking.a_Tracking_verification import Interface_Check
from AnimalTA.E_Post_tracking.b_Analyses import Interface_Analyses
from AnimalTA.B_Project_organisation import Class_Row_Videos, Import_data
from AnimalTA import Class_Video
import os
from functools import partial
import math
import decord
from copy import deepcopy
import webbrowser

os.system("")  # enables ansi escape characters in terminal

class Information_panel(Frame):
    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.grid(sticky="nsew")

        Grid.columnconfigure(parent, 0, weight=1)
        Grid.rowconfigure(parent, 0, weight=1)

        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 2, weight=100)
        Grid.rowconfigure(self, 3, weight=1)
        Grid.rowconfigure(self, 4, weight=1)
        Grid.rowconfigure(self, 5, weight=1)

        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=100)

        #Short summary about current version, how to cite and how to find guidelines.
        Lab_version=Label(self, text="AnimalTA. v2.2.3", font=("Arial", "14", "bold"))
        Lab_version.grid(row=0, column=0,columnspan=2, sticky="nsw")

        Lab_cite=Label(self, text="How to cite:")
        Lab_cite.grid(row=2, column=0,columnspan=2, sticky="nsw")
        Citation= Text(self, height=5, width=75, wrap=WORD)
        Citation.grid(row=3, column=0,columnspan=2, sticky="nswe")
        Citation.insert("1.0", "Chiara V. & Kim S.Y. (2023). AnimalTA: a highly flexible and easy-to-use program for tracking and analyzing animal movement in different environments. Methods in Ecolocy and Evolution, Accepted.")
        Citation.configure(state="disabled")

        Lab_contact=Label(self, text="Contact:")
        Lab_contact.grid(row=5, column=0, sticky="nsw")
        mail= Text(self, height=1, width=30)
        mail.insert("1.0", "contact.AnimalTA@vchiara.eu")
        mail.configure(state="disabled")
        mail.grid(row=5, column=1, sticky="nsw")

        Lab_Help=Label(self, text="Need help? Go check the guidelines or the video tutorials:")
        Lab_Help.grid(row=7, column=0,columnspan=2, sticky="nsew")
        link = Label(self, text="http://vchiara.eu/index.php/animalta", fg="#b448cd", cursor="hand2")
        link.grid(row=8, column=0,columnspan=2, sticky="nsew")
        link.bind("<Button-1>", self.send_link)

        self.rowconfigure(1, minsize=20)
        self.rowconfigure(4, minsize=30)
        self.rowconfigure(6, minsize=30)

    def send_link(self, event):
        webbrowser.open_new_tab("http://vchiara.eu/index.php/animalta")

class Interface(Frame):
    """This is the main Frame of the project, it contains:
    1. A homemade menu option to allow to add, remove video, change the language, save projectes, open projects...
    2. A table with one row per video (see Class_Row_Videos
    3. A set of options to set tracking parameters, correct the trajectories or analyses them."""
    def __init__(self, parent, liste_of_videos=[], **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(background="grey")
        self.parent = parent
        self.posX=0#At the beginning, horizontal scrollbar is at location 0

        # Import language
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        # Window's management
        self.project_name = StringVar()
        self.project_name.set("Untitled")
        self.fullscreen_status = False
        self.pressed_bord = [None, None] #To allow user to change the window size
        self.changing = False# A flag to determine whether the user is changing the size of the window or not

        self.selected_vid = None
        self.Current_capture=None
        self.first = True #If an action have already be done or not
        self.folder = None #Where is the current directory
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
        self.canvas_title_bar = Canvas(self, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_title_bar.grid(row=0, column=0, columnspan=3, sticky="new")
        self.canvas_title_bar.columnconfigure(0, weight=1)
        self.canvas_title_bar.columnconfigure(1, weight=1)
        self.canvas_title_bar.columnconfigure(2, weight=100)
        self.canvas_title_bar.columnconfigure(3, weight=1)
        self.canvas_title_bar.columnconfigure(4, weight=1)
        self.canvas_title_bar.bind("<Button-1>", self.press_fenetre)
        self.canvas_title_bar.bind("<B1-Motion>", self.move_fenetre)

        # Frame containing optaions and the table of videos
        self.canvas_main = Frame(self, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_main.grid(row=1, column=0, sticky="nsew")
        Grid.rowconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 0, weight=1)

        self.canvas_show = Frame(self.canvas_main, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_show.grid(row=0, column=0, rowspan=2, sticky="nsew")

        self.rows_optns = Frame(self.canvas_show, bd=2, highlightthickness=1, relief='ridge')
        Grid.rowconfigure(self.rows_optns, 0, weight=1)
        Grid.columnconfigure(self.rows_optns, 1, weight=1)
        Grid.columnconfigure(self.rows_optns, 2, weight=1)
        Grid.columnconfigure(self.rows_optns, 3, weight=1)
        Grid.columnconfigure(self.rows_optns, 4, weight=1)
        Grid.columnconfigure(self.rows_optns, 5, weight=1)
        Grid.columnconfigure(self.rows_optns, 6, weight=100)
        Grid.columnconfigure(self.rows_optns, 7, weight=1)

        # User help:
        self.HW = User_help.Help_win(self.canvas_main, default_message=self.Messages["Welcome"], width=250)
        self.HW.grid(row=0, column=1, sticky="nsew")

        self.canvas_next_step = Frame(self.canvas_main)
        self.canvas_next_step.grid(row=1, column=1, sticky="nsew")
        Grid.columnconfigure(self.canvas_next_step, 0, weight=1)

        Grid.columnconfigure(self.canvas_main, 0, weight=1000)
        Grid.columnconfigure(self.canvas_main, 1, weight=1)
        Grid.rowconfigure(self.canvas_main, 0, weight=1000)
        Grid.rowconfigure(self.canvas_main, 1, weight=1)

        # Options to interact with the project:
        self.Optns_Lab = Entry(self.rows_optns, textvar=self.project_name, bg="darkgrey", relief="ridge",
                               font=("Arial", 14))
        self.Optns_Lab.grid(row=0, column=0, sticky="w")
        #Add a video
        self.bouton_Add = Button(self.rows_optns, text=self.Messages["GButton7"], command=self.add_video)
        self.bouton_Add.grid(row=0, column=1, sticky="nswe")
        #Do the tracking of some videos
        self.bouton_make_track = Button(self.rows_optns, text=self.Messages["GButton10"], command=self.begin_track)
        self.bouton_make_track.grid(row=0, column=4, sticky="nswe")
        self.bouton_make_track.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General19"]))
        self.bouton_make_track.bind("<Leave>", self.HW.remove_tmp_message)
        #Run the analyses of trajectories
        self.bouton_make_analyses = Button(self.rows_optns, text=self.Messages["GButton15"], command=self.run_analyses)
        self.bouton_make_analyses.grid(row=0, column=5, sticky="nswe")
        self.bouton_make_analyses.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General20"]))
        self.bouton_make_analyses.bind("<Leave>", self.HW.remove_tmp_message)


        #For a future update
        '''
        #Import data from other trackings
        self.bouton_import_dat = Button(self.rows_optns, text="MISSING", command=self.import_dat)
        self.bouton_import_dat.grid(row=0, column=7, sticky="nse")
        self.bouton_import_dat.config(state="disable")
        self.bouton_import_dat.bind("<Enter>", partial(self.HW.change_tmp_message, "MISSING"))
        self.bouton_import_dat.bind("<Leave>", self.HW.remove_tmp_message)
        '''


        #Export selected video
        self.bouton_save_TVid = Button(self.rows_optns, text=self.Messages["GButton18"], command=self.export_vid)
        self.bouton_save_TVid.grid(row=0, column=8, sticky="nse")
        self.bouton_save_TVid.config(state="disable")
        self.bouton_save_TVid.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["GButton19"]))
        self.bouton_save_TVid.bind("<Leave>", self.HW.remove_tmp_message)

        #Special feature, not to be distributed
        #self.bouton_Roi = Button(self.rows_optns, text="Heart Beat", command=self.Roi_extension, background="yellow")
        #self.bouton_Roi.grid(row=0, column=8, sticky="nse")

        #The video table is created here and is associated with a scrollbar
        self.canvas_rows = Canvas(self.canvas_show, bd=2, highlightthickness=1, relief='ridge')
        self.Visualise_vids = Frame(self.canvas_rows, background="#ffffff")
        self.vsh = Scrollbar(self.canvas_show, orient="horizontal", command=self.update_posX)
        self.vsh.bind("<Motion>", self.first_action)
        self.vsh.grid(row=2, column=0, sticky="we")
        self.canvas_rows.configure(xscrollcommand=self.vsh.set)
        self.canvas_rows.create_window((4, 4), window=self.Visualise_vids, anchor="n", tags="self.frame")
        self.canvas_rows.grid(row=1, column=0, sticky="nsew")
        self.vsv = Scale(self.canvas_show, orient="vertical", from_=0, to=0)
        self.vsv.bind("<ButtonRelease-1>", self.afficher_projects)
        self.vsv.grid(row=1, column=1, sticky="ns")

        Grid.columnconfigure(self.canvas_show, 0, weight=1)
        Grid.rowconfigure(self.canvas_show, 1, weight=1)

        self.Visualise_vids.bind("<Configure>", self.onFrameConfigure)
        self.bind_all("<Up>", self.Up)
        self.bind_all("<KeyRelease-Up>", self.Rel_UpBot)
        self.bind_all("<Down>", self.Bot)
        self.bind_all("<KeyRelease-Down>", self.Rel_UpBot)
        self.bind_all("<MouseWheel>", self.on_mousewheel)
        self.parent.bind_all("<Button-1>", self.remove_Fus)
        self.bind_all("<Button-1>", self.remove_Fus)

        # Widgets:
        # Title bar
        #Name of the program
        self.Nom_Logiciel = Label(self.canvas_title_bar, fg="white", text="AnimalTA", bg="purple",
                                  font=("courier new", 12))
        self.Nom_Logiciel.grid(row=0, column=0, sticky="w")
        #More information about AnimalTA:
        B_info=Button(self.canvas_title_bar, text="?",command=self.show_infos)
        B_info.grid(row=0, column=1, sticky="w")

        #Create new project
        self.bouton_New = Button(self.canvas_title_bar, text=self.Messages["GButton1"], command=self.new_project)
        self.bouton_New.grid(row=0, column=2, sticky="e")
        #Open existing project
        self.bouton_Open = Button(self.canvas_title_bar, text=self.Messages["GButton2"], command=self.open_file)
        self.bouton_Open.grid(row=0, column=4, sticky="e")
        #Close the current project
        self.bouton_Close = Button(self.canvas_title_bar, text=self.Messages["GButton17"], command=self.close_file)
        self.bouton_Close.grid(row=0, column=5, sticky="e")
        self.bouton_Close.config(state="disable")#Only if there is a project open
        # Save the current project
        self.bouton_Save = Button(self.canvas_title_bar, text=self.Messages["GButton3"], command=self.save)
        self.bouton_Save.grid(row=0, column=6, sticky="e")
        self.bouton_Save.config(state="disable")#Only if there is a project open
        #Change the language
        OptionLan = list(UserMessages.Mess.keys())
        self.bouton_Lang = OptionMenu(self.canvas_title_bar, self.Language, *OptionLan, command=self.update_lan)
        self.bouton_Lang.grid(row=0, column=7, sticky="e")
        self.canvas_title_bar.columnconfigure(8, minsize=25)
        #Minimize the program
        self.bouton_minimize = Button(self.canvas_title_bar, text="—", command=self.minimize)
        self.bouton_minimize.grid(row=0, column=9, sticky="e")
        #Fullscreen
        self.bouton_fullscreen = Button(self.canvas_title_bar, text=u'\u2B1C', command=self.fullscreen)
        self.bouton_fullscreen.grid(row=0, column=10, sticky="e")
        #Close AnimalTA
        self.bouton_Fermer = Button(self.canvas_title_bar, text="X", fg="white", bg="red", command=self.fermer)
        self.bouton_Fermer.grid(row=0, column=11, sticky="e")

        #Options for the videos outside of the table
        #Define the optiosn for tracking
        self.Beginn_track = Button(self.canvas_next_step, text=self.Messages["GButton4"], command=self.Beg_track)
        self.Beginn_track.config(state="disable")
        self.Beginn_track.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General11"]))
        self.Beginn_track.bind("<Leave>", self.HW.remove_tmp_message)
        #Show the defined options
        self.Show_T_infos = Label(self.canvas_next_step, textvariable=self.Infos_track, wraplength=250)
        #Apply the tracking parameters to other videos
        self.BExtend_track = Button(self.canvas_next_step, text=self.Messages["GButton5"], command=self.extend_track)
        self.BExtend_track.config(state="disable")
        self.BExtend_track.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General12"]))
        self.BExtend_track.bind("<Leave>", self.HW.remove_tmp_message)
        #Correct the trajectories
        self.bouton_check_track = Button(self.canvas_next_step, text=self.Messages["GButton13"],
                                         command=self.check_track)
        self.bouton_check_track.config(state="disable")
        self.bouton_check_track.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General13"]))
        self.bouton_check_track.bind("<Leave>", self.HW.remove_tmp_message)
        #Prepare the analyses of the trajectories
        self.bouton_analyse_track = Button(self.canvas_next_step, text=self.Messages["GButton14"],
                                           command=self.analyse_track)
        self.bouton_analyse_track.config(state="disable")
        self.bouton_analyse_track.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General14"]))
        self.bouton_analyse_track.bind("<Leave>", self.HW.remove_tmp_message)
        #The info panle will blin when AnimalTA is opened
        self.HW.get_attention(0)


    ##Information about versio, citation and guidelines
    def show_infos(self):
        info_win=Toplevel(self.parent)
        info_win.title("Information")
        interface = Information_panel(parent=info_win)


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
        self.quitter = True
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
        try:
            if self.folder != None:
                answer = messagebox.askyesnocancel(self.Messages["General8"], self.Messages["General9"])
                if answer:
                    f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "w", encoding="utf-8")
                    f.write(self.Language.get())
                    f.close()
                    self.save()
                    self.fermer()
                elif answer == False:
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

        except:
            f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "w", encoding="utf-8")
            f.write(self.Language.get())
            f.close()
            self.fermer()

    def grid_param_track(self):
        #Open a new Frame in which the user will be able to set teh tracking parameters
        self.bouton_analyse_track.grid(row=4, column=0, sticky="swe")
        self.bouton_check_track.grid(row=3, column=0, sticky="swe")
        self.BExtend_track.grid(row=2, sticky="sew")
        self.Show_T_infos.grid(row=1, sticky="sew")
        self.Beginn_track.grid(row=0, sticky="sew")

    def Change_win(self, interface):
        #When we want to change the mainFrame by another one
        # We remove the actual canvas
        self.canvas_show.grid_forget()
        self.canvas_next_step.grid_forget()
        self.HW.grid_forget()
        self.bouton_Lang.config(state="disable")
        self.bouton_New.config(state="disable")
        self.bouton_Save.config(state="disable")
        self.bouton_Add.config(state="disable")
        self.bouton_Open.config(state="disable")
        self.unbind_all("<Up>")
        self.unbind_all("<Down>")
        self.unbind_all("<KeyRelease-Up>")
        self.unbind_all("<KeyRelease-Down>")
        self.unbind_all("<MouseWheel>")

        # We add the new one
        self.Second_Menu = interface

    def return_main(self):
        #When we come back from another frame and want to show this one
        # We add the actual canvas
        self.canvas_show.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.HW.grid(row=0, column=1, sticky="nsew")
        self.canvas_next_step.grid(row=1, column=1, sticky="nsew")
        self.update_selections()
        self.bouton_Lang.config(state="active")
        self.bouton_New.config(state="active")
        self.bouton_Save.config(state="active")
        self.bouton_Add.config(state="active")
        self.bouton_Open.config(state="active")
        self.bind_all("<Up>", self.Up)
        self.bind_all("<Down>", self.Bot)
        self.bind_all("<KeyRelease-Up>", self.Rel_UpBot)
        self.bind_all("<KeyRelease-Down>", self.Rel_UpBot)
        self.bind_all("<MouseWheel>", self.on_mousewheel)

        # We remove the new one
        self.Second_Menu.grid_forget()
        self.Second_Menu.destroy()
        del self.Second_Menu

        self.afficher_projects()

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas_rows.configure(scrollregion=self.canvas_rows.bbox("all"))
        self.moveX()

    def update_posX(self, event0=None, event1=0, event2=None):
        self.posX=event1
        self.moveX()

    ##Project management
    def save(self):
        # Save the project
        try:
            shutil.copyfile(self.file_to_save, self.file_to_save+"old")
            #This is a security to ensure that the old file will not be deleted before ensurong the new one can be proprly saved

            with open(self.file_to_save , 'wb') as fp:
                data_to_save = dict(Project_name=self.project_name.get(), Folder=self.folder,
                                    Videos=self.liste_of_videos)
                pickle.dump(data_to_save, fp)

            #If there was no problem during the save, we delete the security copy
            os.remove(self.file_to_save+"old")


        except Exception as e:
            #If the program was not properly saved, we restore the security copy
            if os.path.isfile(self.file_to_save+"old"):
                os.remove(self.file_to_save)
                os.rename(self.file_to_save+"old",self.file_to_save)

            messagebox.showinfo(message=self.Messages["GWarn3"], title=self.Messages["GWarnT3"])


    def close_file(self):
        # Ask if teh user wants to save the project and then close it
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
        # Close the project
        self.project_name.set("Untitled")
        self.liste_of_videos = []
        self.folder = None

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
        # If a project was already open, ask if the user wants to save it and then open another one
        try:
            if not self.folder == None:
                answer = messagebox.askyesnocancel(self.Messages["General17"], self.Messages["General18"])
                if answer:
                    self.save()
                    self.open_file2()
                elif answer == False:
                    self.open_file2()
                else:
                    pass
            else:
                self.open_file2()
        except:
            self.open_file2()

    def open_file2(self, file=None):
        # Open an existing project
        try:
            if file==None:#If we open a new project, we beginn from 0
                self.file_to_open = filedialog.askopenfilename(filetypes=(("AnimalTA", "*.ata"),))
                with open(self.file_to_open, 'rb') as fp:
                    data_to_load = pickle.load(fp)
                    self.project_name.set(data_to_load["Project_name"])
                    self.folder = data_to_load["Folder"]
                    self.liste_of_videos = data_to_load["Videos"]
                    self.file_to_save = self.file_to_open

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
                            print(file_[-3:])
                            if file_[-4:]!=".avi":
                                src_file = os.path.join(src_dir, file_)
                                shutil.copy(src_file, dst_dir)
                    for V in data_to_load["Videos"]:
                        V.Folder=self.folder
                        self.liste_of_videos.append(V)
            try:
                self.list_projects
            except:
                self.list_projects = []
                for row in range(20):
                    self.list_projects.append(Class_Row_Videos.Row_Can(parent=self.Visualise_vids, main_boss=self,
                                                                       Video_file=None,
                                                                       proj_pos=row, bd=2, highlightthickness=1,
                                                                       relief='ridge'))

            to_suppr = []
            # Check that videos are still available
            for V in range(len(self.liste_of_videos)):
                # Look for all points of interest
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

                if len(self.liste_of_videos[V].Track[1])<8:#Old versions of AnimalTA did not allow for lightning corrections or variable number of targets
                    self.liste_of_videos[V].Track[1].append(False)#No lightning correction
                    self.liste_of_videos[V].Track[1].append(True)#Fixed number of tragets

                if len(self.liste_of_videos[V].Track[1])<9:
                    self.liste_of_videos[V].Track[1].append(True)#Fixed number of tragets

                if len(self.liste_of_videos[V].Track[1])<10:
                    self.liste_of_videos[V].Track[1].append(False)#Flicker correction

                if len(self.liste_of_videos[V].Analyses)<5:
                    self.liste_of_videos[V].Analyses.append([[],[],[]])#Deformation of images

                if not os.path.isfile(self.liste_of_videos[V].File_name):
                    resp = messagebox.askyesno(self.Messages["GWarnT5"],self.Messages["GWarn5"].format(self.liste_of_videos[V].File_name))
                    if resp and self.liste_of_videos[V].clear_files():
                        to_suppr.append(V)
                    else:
                        if len(to_suppr) > 0:
                            self.liste_of_videos.pop(to_suppr)
                        self.close()
                        return
            if len(to_suppr) > 0:
                for elem in sorted(to_suppr, reverse=True):
                    del self.liste_of_videos[elem]

            # Check that coordinates are still available
            for V in self.liste_of_videos:
                V.check_coos()
            self.load_projects()
            self.rows_optns.grid(row=0, column=0, sticky="sewn")
            if len(self.liste_of_videos) > 0:
                self.HW.default_message = self.Messages["General1"]
            else:
                self.HW.default_message = self.Messages["General0"]
            self.HW.remove_tmp_message()

            self.bouton_Save.config(state="active")
            if len(self.liste_of_videos) > 0:
                self.grid_param_track()

            self.bouton_Close.config(state="active")
        except Exception as e:
            print(e)
            self.HW.default_message = self.Messages["General10"]
            self.HW.remove_tmp_message()

    def first_action(self, *arg):
        #At least one action has been done
        self.first = False

    def moveX(self):
        #Move the scrollbar of the video table to a specific location (pos)
        self.canvas_rows.xview_moveto(str(self.posX))

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
            answer = messagebox.askyesnocancel(self.Messages["General17"], self.Messages["General18"])
            if answer:
                self.save()
                self.new_project2(prev_save=True)
            elif answer == False:
                self.new_project2()
            else:
                pass
        else:
            self.new_project2()

    def new_project2(self,prev_save=False):
        #Create a new project
        if prev_save:
            messagebox.showinfo(self.Messages["GInfoT1"],self.Messages["GInfo1"])

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
                try:
                    self.list_projects
                except:
                    self.list_projects = []
                    for row in range(20):
                        self.list_projects.append(Class_Row_Videos.Row_Can(parent=self.Visualise_vids, main_boss=self,
                                                                           Video_file=None,
                                                                           proj_pos=row, bd=2, highlightthickness=1,
                                                                           relief='ridge'))

                self.load_projects()
                self.rows_optns.grid(row=0, column=0, sticky="sewn")
                with open(self.file_to_save, 'wb') as fp:
                    data_to_save = dict(Project_name=self.project_name.get(), Folder=self.folder,
                                        Videos=self.liste_of_videos)
                    pickle.dump(data_to_save, fp)
                self.bouton_Save.config(state="active")

        except Exception as e:
            print(e)

    def load_projects(self):
        self.afficher_projects()

    def afficher_projects(self, *arg):
        # Show the row of the table according to the scrollbar position.
        # We cannot create all the rows to avoid to consume too much memory in the case of m¡numerous videos projects
        self.posX = self.vsh.get()[0]  # Save the Xscrollbar position
        try:
            for label in self.Visualise_vids.grid_slaves():
                label.grid_forget()

        except Exception as e:
            print(e)

        try:
            if len(self.liste_of_videos) > 0:

                central = int(self.vsv.get())
                nb_visibles = self.canvas_show.winfo_height() / (130)
                self.vsv.config(to=len(self.liste_of_videos) - 1)

                for P in self.list_projects:
                    P.grid_forget()

                Pos=0
                for who in range(central, min(len(self.liste_of_videos), int(central + round(nb_visibles)) + 1)):
                    self.list_projects[Pos].change_vid(self.liste_of_videos[who],Pos - 1)
                    self.list_projects[Pos].grid(row=Pos, column=0, sticky="we")
                    self.list_projects[Pos].update_selection()
                    Pos+=1


                self.canvas_show.update()

        except Exception as e:
            print(e)

        self.moveX()  # Keep the Xscrollbar position

    def update_projects(self):
        # Update the displayed rows
        for Row in self.list_projects:
            if Row.Video!=None:
                Row.update()

    """
    Not to be distributed
    def Roi_extension(self):
        if self.selected_vid != None:
            self.Change_win(Extension_Roi.Light_changes(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                        Vid=self.selected_vid))
    """

    ##Actions toward videos
    def begin_track(self):
        #Open the window to ask for which videos to begin the tracking
        nb_vid_T = 0
        for Vid in self.liste_of_videos:
            if Vid.Track[0]:
                nb_vid_T += 1

        if nb_vid_T > 0:
            newWindow = Toplevel(self.parent)
            interface = Interface_selection_track_and_analyses.Extend(parent=newWindow, boss=self, type="Tracking")
        else:
            messagebox.showinfo(message=self.Messages["GError1"], title=self.Messages["GErrorT1"])

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
            messagebox.showinfo(message=self.Messages["GWarn7"], title=self.Messages["GWarnT7"])

    def export_vid(self):
        #Open a window for video exportation
        if self.selected_vid != None:
            self.Change_win(Interface_Save_Vids.Lecteur(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                        Vid=self.selected_vid, Video_liste=self.liste_of_videos))

    #For a future update
    '''
    def import_dat(self):
        if self.selected_vid != None:
            data_files = filedialog.askopenfilenames()
            if len(data_files)>0:
                newWindow = Toplevel(self.parent)
                Import_data.Int_import(newWindow, data_files, Vid=self.selected_vid)

    '''


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

    def extend_track(self):
        #Open a window to allow the user to apply the tracking parameters of selected vidoe to other videos
        newWindow = Toplevel(self.parent)
        interface = Interface_extend.Extend(parent=newWindow, value=self.selected_vid.Track[1], boss=self,
                                            Video_file=self.selected_vid, type="track")

    def Beg_track(self, speed=0):
        #speed alows to maintain the same speed of the video reader when changing videos
        #open a window to allow user to select the videos to be tracked and beginn the tracking process
        if self.selected_vid != None:
            if self.selected_vid.Tracked:
                response = messagebox.askyesno(message=self.Messages["GWarn1"])
                if response and self.selected_vid.clear_files():
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
                        self.liste_of_videos.append(
                            Class_Video.Video(File_name=file, Folder=self.folder, shape=frame0.shape, nb_fr=len(tmp_capture), fr_rate=tmp_capture.get_avg_fps()))
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

        self.load_projects()
        self.HW.default_message = self.Messages["General1"]
        self.HW.remove_tmp_message()
        self.grid_param_track()
        self.update_selections()

    def supr_video(self, Vid):
        #Delete a video from the project.
        if Vid != None:
            answer = messagebox.askyesno(self.Messages["GWarnT2"], self.Messages["GWarn2"])
            if answer and Vid.clear_files():
                # Supress associated files
                pos_R = [index for index, Vid_L in enumerate(self.liste_of_videos) if Vid_L == Vid]
                self.liste_of_videos.pop(pos_R[0])
                self.load_projects()
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

        new_Vid.User_Name=new_Vid.Name

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
        self.load_projects()
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
        if self.wait_for_vid:
            self.fus_video()
        self.update_selections()

    def fusion_two_Vids(self, second_Vid):
        #When the concatenation button was activate and the user select a second video to be concatenated
        if self.selected_vid != second_Vid:#If the two videos are different
            if self.selected_vid.or_shape == second_Vid.or_shape and self.selected_vid.Frame_rate[0] == second_Vid.Frame_rate[0]:#And that they share the same characteristics
                if len(self.selected_vid.Fusion) < 2: #If it was not done yet, we prepare the info for the Fusion process (can't be done before as opencv is not accurate in frame counting and decord too slow to manage all the videos at the same time)
                    capture = decord.VideoReader(self.selected_vid.File_name, ctx=decord.cpu(0))
                    self.selected_vid.Frame_nb[0] = len(capture)
                    self.selected_vid.Frame_nb[1] = self.selected_vid.Frame_nb[0] / round(
                        self.selected_vid.Frame_rate[0] / self.selected_vid.Frame_rate[1])
                    del capture

                if len(second_Vid.Fusion) < 2: #If it was not done yet, we prepare the info for the Fusion process (can't be done before as opencv is not accurate in frame counting and decord too slow to manage all the videos at the same time)
                    capture = decord.VideoReader(second_Vid.File_name, ctx=decord.cpu(0))
                    second_Vid.Frame_nb[0] = len(capture)
                    second_Vid.Frame_nb[1] = second_Vid.Frame_nb[0] / round(second_Vid.Frame_rate[0] / second_Vid.Frame_rate[1])
                    del capture

                # We add the second part after the first one
                self.selected_vid.Fusion.append([self.selected_vid.Frame_nb[0], second_Vid.File_name])
                self.selected_vid.Frame_nb[0] += second_Vid.Frame_nb[0]
                self.selected_vid.Frame_nb[1] = math.floor(self.selected_vid.Frame_nb[0] / round(
                    self.selected_vid.Frame_rate[0] / self.selected_vid.Frame_rate[1]))
                self.selected_vid.Cropped = [False, [0, self.selected_vid.Frame_nb[0]]]
                self.supr_video(Vid=second_Vid)
                self.wait_for_vid = False
                self.afficher_projects()
            else:#If the two videos does not share the same charcateristic, we inform the user
                self.wait_for_vid = False
                messagebox.showinfo(message=self.Messages["GWarn4"], title=self.Messages["GWarnT4"])
        else:
            self.fus_video()
        self.update_selections()

    def update_selections(self):
        #When user select a row, we update all the buttons for them to be activate/deactive and of the right color.
        #Orange= something can be done that hasn't been
        #Blue done but can be modified
        #System, secondary or finished
        if self.selected_vid == None:
            self.Infos_track.set(self.Messages["General2"])
            self.Beginn_track.config(state="active", bg="SystemButtonFace", activebackground="SystemButtonFace")
            self.BExtend_track.config(state="disable")
            self.bouton_check_track.config(state="disable", activebackground="SystemButtonFace", bg="SystemButtonFace")
            self.bouton_analyse_track.config(state="disable", activebackground="SystemButtonFace",
                                             bg="SystemButtonFace")
            self.bouton_save_TVid.config(state="disable")
            #self.bouton_import_dat.config(state="disable")
        else:
            self.bouton_save_TVid.config(state="active")
            #self.bouton_import_dat.config(state="active")

            if not self.selected_vid.Track[0]:
                self.Beginn_track.config(state="active", activebackground="#ff8a33", bg="#ff8a33")
                self.Infos_track.set(self.no_track)
                self.BExtend_track.config(state="disable")
                self.bouton_check_track.config(state="disable", activebackground="SystemButtonFace",
                                               bg="SystemButtonFace")
                self.bouton_analyse_track.config(state="disable", activebackground="SystemButtonFace",
                                                 bg="SystemButtonFace")

            else:
                self.Beginn_track.config(state="active", activebackground="#3aa6ff", bg="#3aa6ff")
                self.BExtend_track.config(state="active")
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

                point_pos = self.selected_vid.Name.rfind(".")
                file_tracked = os.path.join(self.selected_vid.Folder, "coordinates", self.selected_vid.Name[:point_pos] + "_Coordinates.csv")
                file_trackedP = os.path.join(self.selected_vid.Folder, "coordinates", self.selected_vid.User_Name + "_Coordinates.csv")

                if not self.selected_vid.Tracked or not(os.path.isfile(file_tracked) or os.path.isfile(file_trackedP)):
                    self.bouton_check_track.config(state="disable", activebackground="SystemButtonFace",
                                                   bg="SystemButtonFace")
                    self.bouton_analyse_track.config(state="disable", activebackground="SystemButtonFace",
                                                     bg="SystemButtonFace")

                elif os.path.isfile(file_tracked) or os.path.isfile(file_trackedP):
                    self.Beginn_track.config(state="active", bg="SystemButtonFace", activebackground="SystemButtonFace")
                    self.bouton_check_track.config(state="active")
                    self.bouton_analyse_track.config(state="active", activebackground="#ff8a33", bg="#ff8a33")


                    file_tracked_Corr = os.path.join(self.selected_vid.Folder, "corrected_coordinates", self.selected_vid.Name[:point_pos] + "_Corrected.csv")
                    file_trackedP_Coor = os.path.join(self.selected_vid.Folder, "corrected_coordinates", self.selected_vid.User_Name + "_Corrected.csv")

                    if ( not (os.path.isfile(file_tracked_Corr) or os.path.isfile(file_trackedP_Coor))):
                        self.bouton_check_track.config(activebackground="#ff8a33", bg="#ff8a33")

                    else:
                        self.bouton_check_track.config(activebackground="#3aa6ff", bg="#3aa6ff")
                        self.bouton_analyse_track.config(state="active", activebackground="#ff8a33", bg="#ff8a33")

        try:#If the Rows are not created yet
            for Row in self.list_projects:
                Row.update_selection()
        except:
            pass

    def stab_all(self):
        #Apply stabilisation to all videos of the project
        for Vid in self.liste_of_videos:
            Vid.Stab[0] = True

        self.update_projects()
