from tkinter import *
import pyautogui
from tkinter import filedialog
from tkinter import messagebox
import pickle
import shutil
from AnimalTA import Interface_Check, UserMessages, Interface_extend, Interface_Analyses3, Class_Video, \
    Class_Row_Videos, Interface_Vids_for_track, Interface_parameters_track, Interface_Vids_for_convert, \
    Interface_Save_Vids, User_help, Extension_Roi
import os
from functools import partial
from win32api import GetMonitorInfo, MonitorFromPoint
import math
import decord

os.system("")  # enables ansi escape characters in terminal


class Interface(Frame):
    """This is the main Frame of the project, it contains:
    1. A homemade menu option to allow to add, remove video, change the language, save projectes, open projects...
    2. A table with one row per video (see Class_Row_Videos
    3. A set of options to set tracking parameters, correct the trajectories or analyses them."""

    def __init__(self, parent, liste_of_videos=[], **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(background="grey")
        self.parent = parent

        # Import language
        self.Language = StringVar()
        f = open("Files/Language", "r")
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
        self.first = True #If an action have already be done or not
        self.folder = None #Where is the current directory
        self.wait_for_vid = False  # For fusion process, if we expect the user to select a second vid, = True
        self.liste_of_videos = liste_of_videos
        self.Infos_track = StringVar()
        self.no_track = self.Messages["General7"]
        self.Infos_track.set(self.Messages["General2"])

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
        #Supress selected video
        self.bouton_Supr = Button(self.rows_optns, text=self.Messages["GButton8"], command=self.supr_video)
        self.bouton_Supr.grid(row=0, column=2, sticky="nswe")
        self.bouton_Supr.config(state="disable")
        #Concatenate two videos
        self.bouton_Fus = Button(self.rows_optns, text=self.Messages["GButton16"], command=self.fus_video)
        self.bouton_Fus.grid(row=0, column=3, sticky="nswe")
        self.bouton_Fus.config(state="disable")
        self.bouton_Fus.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General15"]))
        self.bouton_Fus.bind("<Leave>", self.HW.remove_tmp_message)
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
        #Export selected video
        self.bouton_save_TVid = Button(self.rows_optns, text=self.Messages["GButton18"], command=self.export_vid)
        self.bouton_save_TVid.grid(row=0, column=7, sticky="nse")
        self.bouton_save_TVid.config(state="disable")
        self.bouton_save_TVid.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["GButton19"]))
        self.bouton_save_TVid.bind("<Leave>", self.HW.remove_tmp_message)

        #Special feature, not to be distributed
        #self.bouton_Roi = Button(self.rows_optns, text="Heart Beat", command=self.Roi_extension, background="yellow")
        #self.bouton_Roi.grid(row=0, column=8, sticky="nse")

        #The video table is created here and is associated with a scrollbar
        self.canvas_rows = Canvas(self.canvas_show, bd=2, highlightthickness=1, relief='ridge')
        self.Visualise_vids = Frame(self.canvas_rows, background="#ffffff")
        self.vsh = Scrollbar(self.canvas_show, orient="horizontal", command=self.canvas_rows.xview)
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
        self.bind_all("<MouseWheel>", self.on_mousewheel)
        self.parent.bind_all("<Button-1>", self.remove_Fus)
        self.bind_all("<Button-1>", self.remove_Fus)

        # Widgets:
        # Title bar
        #Name of the program
        self.Nom_Logiciel = Label(self.canvas_title_bar, fg="white", text="AnimalTA", bg="purple",
                                  font=("courier new", 12))
        self.Nom_Logiciel.grid(row=0, column=0, sticky="w")
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
            self.master.set_appwindow(root=self.master)
            self.master.unbind("<FocusIn>")
            if self.fullscreen_status:
                monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
                work_area = monitor_info.get("Work")
                self.parent.geometry("{0}x{1}+0+0".format(work_area[2], work_area[3]))

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
            monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
            work_area = monitor_info.get("Work")
            self.parent.geometry("{0}x{1}+0+0".format(work_area[2], work_area[3]))

        else:
            self.fullscreen_status = False
            self.parent.geometry("1250x720")
        self.update()

        self.afficher_projects()

    def update_lan(self, *args):
        # Change the language
        try:
            if self.folder != None:
                answer = messagebox.askyesnocancel(self.Messages["General8"], self.Messages["General9"])
                if answer:
                    f = open("Files/Language", "w")
                    f.write(self.Language.get())
                    f.close()
                    self.save()
                    self.fermer()
                elif answer == False:
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
        self.bind_all("<MouseWheel>", self.on_mousewheel)
        self.afficher_projects()

        # We remove the new one
        self.Second_Menu.grid_forget()
        self.Second_Menu.destroy()

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        Xpos = self.vsh.get()[0]  # Save the Xscrollbar position
        self.canvas_rows.configure(scrollregion=self.canvas_rows.bbox("all"))
        if self.first:
            self.moveX()
        else:
            self.moveX(Xpos)  # Keep the Xscrollbar position

    ##Project management
    def save(self):
        # Save the project
        try:
            with open(self.file_to_save, 'wb') as fp:
                data_to_save = dict(Project_name=self.project_name.get(), Folder=self.folder,
                                    Videos=self.liste_of_videos)
                pickle.dump(data_to_save, fp)
        except Exception as e:
            print(e)
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
        self.list_projects = []
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

    def open_file2(self):
        # Open an existing project
        try:
            self.file_to_open = filedialog.askopenfilename(filetypes=(("AnimalTA", "*.ata"),))
            with open(self.file_to_open, 'rb') as fp:
                data_to_load = pickle.load(fp)
                self.project_name.set(data_to_load["Project_name"])
                self.folder = data_to_load["Folder"]
                self.liste_of_videos = data_to_load["Videos"]

            to_suppr = []
            # Check that videos are still available
            for V in range(len(self.liste_of_videos)):
                if not os.path.isfile(self.liste_of_videos[V].File_name):
                    resp = messagebox.askyesno(self.Messages["GWarnT5"],
                                               self.Messages["GWarn5"].format(self.liste_of_videos[V].File_name))
                    if resp:
                        self.liste_of_videos[V].clear_files()
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
            self.file_to_save = self.file_to_open
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

    def moveX(self, pos=0.0):
        #Move the scrollbar of the video table to a specific location (pos)
        self.canvas_rows.xview_moveto(str(pos))

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
                self.new_project2()
            elif answer == False:
                self.new_project2()
            else:
                pass
        else:
            self.new_project2()

    def new_project2(self):
        #Create a new project
        try:
            self.file_to_save = filedialog.asksaveasfilename(defaultextension=".ata",
                                                             initialfile="Untitled_project.ata",
                                                             filetypes=(("AnimalTA", "*.ata"),))
            if len(self.file_to_save) > 0:
                file_name = os.path.basename(self.file_to_save)
                point_pos = file_name.rfind(".")
                self.folder = os.path.dirname(self.file_to_save) + "/Project_folder_" + file_name[:point_pos]
                if not os.path.isdir(self.folder):
                    os.makedirs(self.folder)
                else:
                    shutil.rmtree(self.folder)
                    os.makedirs(self.folder)
                self.project_name.set(file_name[:-4])
                self.HW.default_message = self.Messages["General0"]
                self.HW.remove_tmp_message()
                self.liste_of_videos = []
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
        self.list_projects = []
        self.afficher_projects()

    def afficher_projects(self, *arg):
        # Show the row of the table according to the scrollbar position.
        # We cannot create all the rows to avoid to consume too much memory in the case of m¡numerous videos projects
        Xpos = self.vsh.get()[0]  # Save the Xscrollbar position
        try:
            for label in self.Visualise_vids.grid_slaves():
                label.grid_forget()

        except Exception as e:
            print(e)

        try:
            if len(self.liste_of_videos) > 0:
                Ypos = 0
                central = int(self.vsv.get())
                nb_visibles = self.canvas_show.winfo_height() / (130)
                self.vsv.config(to=len(self.liste_of_videos) - 1)
                self.list_projects = []
                for who in range(central, min(len(self.liste_of_videos), int(central + round(nb_visibles)) + 1)):
                    self.list_projects.append(Class_Row_Videos.Row_Can(parent=self.Visualise_vids, main_boss=self,
                                                                       Video_file=self.liste_of_videos[who],
                                                                       proj_pos=Ypos - 1, bd=2, highlightthickness=1,
                                                                       relief='ridge'))
                    self.list_projects[len(self.list_projects) - 1].grid(row=Ypos, column=0, sticky="we")
                    self.list_projects[len(self.list_projects) - 1].update_selection()

                    Ypos += 1
                self.canvas_show.update()

        except Exception as e:
            print(e)

        self.moveX(Xpos)  # Keep the Xscrollbar position

    def update_projects(self):
        # Update the displayed rows
        for Row in self.list_projects:
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
            newWindow = Toplevel(self.parent.master)
            interface = Interface_Vids_for_track.Extend(parent=newWindow, boss=self, type="Tracking")
        else:
            messagebox.showinfo(message=self.Messages["GError1"], title=self.Messages["GErrorT1"])

    def run_analyses(self):
        #Open a window to ask the user to select the videos wanted for analyses
        nb_vid_T = 0
        for Vid in self.liste_of_videos:
            if Vid.Tracked:
                nb_vid_T += 1

        if nb_vid_T > 0:
            newWindow = Toplevel(self.parent.master)
            interface = Interface_Vids_for_track.Extend(parent=newWindow, boss=self, type="Analyses")
        else:
            messagebox.showinfo(message="You must before process to video tracking", title="Error, no video ready")

    def export_vid(self):
        #Open a window for video exportation
        if self.selected_vid != None:
            self.Change_win(Interface_Save_Vids.Lecteur(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                        Vid=self.selected_vid, Video_liste=self.liste_of_videos))

    def check_track(self):
        #Open the Frame to allow to check and correct the tracking trajectories
        if self.selected_vid != None:
            self.Change_win(Interface_Check.Lecteur(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                    Vid=self.selected_vid, Video_liste=self.liste_of_videos))

    def analyse_track(self, CheckVar=None):
        #Open a Fram to allow the user to set the analyses parameters
        if self.selected_vid != None:
            self.Change_win(
                Interface_Analyses3.Analyse_track(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                  Vid=self.selected_vid, Video_liste=self.liste_of_videos,
                                                  CheckVar=CheckVar))

    def extend_track(self):
        #Open a window to allow the user to apply the tracking parameters of selected vidoe to other videos
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.selected_vid.Track[1], boss=self,
                                            Video_file=self.selected_vid, type="track")

    def Beg_track(self):
        #open a window to allow user to select the videos to be tracked and beginn the tracking process
        if self.selected_vid != None:
            if self.selected_vid.Tracked:
                response = messagebox.askyesno(message=self.Messages["GWarn1"])
                if response:
                    self.selected_vid.clear_files()
                    self.Change_win(Interface_parameters_track.Param_definer(parent=self.canvas_main, main_frame=self,
                                                                             boss=self.parent,
                                                                             Video_file=self.selected_vid))
            else:
                self.Change_win(
                    Interface_parameters_track.Param_definer(parent=self.canvas_main, main_frame=self, boss=self.parent,
                                                             Video_file=self.selected_vid))

    def add_video(self):
        #Add a video inside the current project
        videos_to_add = filedialog.askopenfilenames()
        self.list_to_convert = []
        for file in videos_to_add:
            point_pos = file.rfind(".")
            if file[point_pos:].lower() != ".avi":#If it is not an avi fils, the video will be converted
                self.list_to_convert.append(file)
            elif file not in [Vid.File_name for Vid in self.liste_of_videos]:#If the file was already loaded, we don't take it
                self.liste_of_videos.append(Class_Video.Video(File_name=file, Folder=self.folder))

        if len(self.list_to_convert) > 0:#If some videos need to be converted, we open the conversion window
            newWindow = Toplevel(self.parent.master)
            interface = Interface_Vids_for_convert.Convert(parent=newWindow, boss=self)

        self.load_projects()
        self.HW.default_message = self.Messages["General1"]
        self.HW.remove_tmp_message()
        self.grid_param_track()
        self.update_selections()

    def supr_video(self, Vid="NA"):
        #Delete a vdieo from the project. if Vid="NA", teh deleted video is the selected one
        if Vid == "NA":
            Vid_to_supr = self.selected_vid
        else:
            Vid_to_supr = Vid

        if Vid_to_supr != None:
            answer = messagebox.askyesno(self.Messages["GWarnT2"], self.Messages["GWarn2"])
            if answer:
                # Supress associated files
                self.selected_vid.clear_files()
                pos_R = [index for index, Vid_L in enumerate(self.liste_of_videos) if Vid_L == Vid_to_supr]
                self.liste_of_videos.pop(pos_R[0])
                self.load_projects()
                self.selected_vid = None
                self.update_selections()
                self.save()

    def fus_video(self):
        #When user press the "concatenate" button
        if self.wait_for_vid:# If the button was already activated, we deactivate it
            self.wait_for_vid = False
            self.HW.change_default_message(self.Messages["General1"])
            self.HW.change_tmp_message(self.Messages["General1"])
            self.bouton_Fus.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General15"]))
            self.bouton_Fus.config(bg="SystemButtonFace", activebackground="SystemButtonFace")
        else:# If not we activate and wait for a  second vidoe to be selected
            self.wait_for_vid = True
            self.HW.change_default_message(self.Messages["General16"])
            self.HW.change_tmp_message(self.Messages["General16"])
            self.bouton_Fus.bind("<Enter>", partial(self.HW.change_tmp_message, self.Messages["General16"]))
            self.bouton_Fus.config(bg="red", activebackground="red", state="active")

    def remove_Fus(self, event):
        #If the user clicks on anything else than a video or the concatenate button, we cancel the concatenation
        if self.wait_for_vid and event.widget != self.bouton_Fus:
            self.fus_video()

    def fusion_two_Vids(self, second_Vid):
        #When the concatenation button was activate and the user select a second video to be concatenated
        if self.selected_vid != second_Vid:#If the two videos are different
            if self.selected_vid.shape == second_Vid.shape and self.selected_vid.Frame_rate[0] == second_Vid.Frame_rate[0]:#And that they share the same characteristics
                if len(self.selected_vid.Fusion) < 2: #If it was not done yet, we prepare the info for the Fusion process (can't be done before as opencv is not accurate in frame counting and decord too slow to manage all the videos at the same time)
                    capture = decord.VideoReader(self.selected_vid.File_name, ctx=decord.cpu(0))
                    self.selected_vid.Frame_nb[0] = len(capture)
                    self.selected_vid.Frame_nb[1] = self.selected_vid.Frame_nb[0] / round(
                        self.selected_vid.Frame_rate[0] / self.selected_vid.Frame_rate[1])
                    del capture

                if len(second_Vid.Fusion) < 2: #If it was not done yet, we prepare the info for the Fusion process (can't be done before as opencv is not accurate in frame counting and decord too slow to manage all the videos at the same time)
                    capture = decord.VideoReader(second_Vid.File_name, ctx=decord.cpu(0))
                    second_Vid.Frame_nb[0] = len(capture)
                    second_Vid.Frame_nb[1] = second_Vid.Frame_nb[0] / round(
                        second_Vid.Frame_rate[0] / second_Vid.Frame_rate[1])
                    del capture

                # We add the second part after the first one
                self.selected_vid.Fusion.append([self.selected_vid.Frame_nb[0], second_Vid.File_name])
                self.selected_vid.Frame_nb[0] += second_Vid.Frame_nb[0]
                self.selected_vid.Frame_nb[1] = math.floor(self.selected_vid.Frame_nb[0] / round(
                    self.selected_vid.Frame_rate[0] / self.selected_vid.Frame_rate[1]))
                self.selected_vid.Cropped = [False, [0, self.selected_vid.Frame_nb[0]]]
                self.supr_video(Vid=second_Vid)
                self.wait_for_vid = False

                self.bouton_Fus.config(bg="SystemButtonFace", activebackground="SystemButtonFace")
                self.afficher_projects()
            else:#If the two videos does not share the same charcateristic, we inform the user
                self.wait_for_vid = False
                self.bouton_Fus.config(bg="SystemButtonFace", activebackground="SystemButtonFace")
                messagebox.showinfo(message=self.Messages["GWarn4"], title=self.Messages["GWarnT4"])

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
                self.Infos_track.set(self.Messages["Param10"] + ": " + corr + "\n" +
                                     self.Messages["Names1"] + ": " + str(int(self.selected_vid.Track[1][0])) + "\n" +
                                     self.Messages["Names2"] + ": " + str(int(self.selected_vid.Track[1][1])) + "\n" +
                                     self.Messages["Names3"] + ": " + str(int(self.selected_vid.Track[1][2])) + "\n" +
                                     self.Messages["Names4"] + ": " + str(
                    round(float(self.selected_vid.Track[1][3][0]), 2)) + "-" + str(
                    round(float(self.selected_vid.Track[1][3][1]), 2)) + "\n" +
                                     self.Messages["Names6"] + ": " + str(
                    round(float(self.selected_vid.Track[1][5]), 2)) + "\n" +
                                     self.Messages["Names9"] + ": " + str(self.selected_vid.Track[1][6]))

                if not self.selected_vid.Tracked:
                    self.bouton_check_track.config(state="disable", activebackground="SystemButtonFace",
                                                   bg="SystemButtonFace")
                    self.bouton_analyse_track.config(state="disable", activebackground="SystemButtonFace",
                                                     bg="SystemButtonFace")
                else:
                    self.Beginn_track.config(state="active", bg="SystemButtonFace", activebackground="SystemButtonFace")
                    self.bouton_check_track.config(state="active")
                    point_pos = self.selected_vid.Name.rfind(".")
                    file_tracked_with_corr = self.selected_vid.Folder + "/corrected_coordinates/" + self.selected_vid.Name[
                                                                                                    :point_pos] + "_Corrected.csv"
                    if os.path.isfile(file_tracked_with_corr):
                        self.bouton_check_track.config(activebackground="#3aa6ff", bg="#3aa6ff")
                    else:
                        self.bouton_check_track.config(activebackground="#ff8a33", bg="#ff8a33")

                    self.bouton_analyse_track.config(state="active", activebackground="#ff8a33", bg="#ff8a33")

        for Row in self.list_projects:
            Row.update_selection()

    def stab_all(self):
        #Apply stabilisation to all videos of the project
        for Vid in self.liste_of_videos:
            Vid.Stab[0] = True

        self.update_projects()
