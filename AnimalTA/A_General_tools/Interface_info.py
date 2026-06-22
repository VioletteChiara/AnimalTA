import pickle
from tkinter import *
import webbrowser
from AnimalTA.A_General_tools import Color_settings, Diverse_functions,UserMessages, Interface_settings
from AnimalTA.B_Project_organisation import Interface_pretracking
import threading
from itertools import cycle
import time
import tempfile
import sys
import subprocess
import os
import shutil

class Information_panel(Frame):
    def __init__(self, parent, current_version, master, new_update=None, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.master=master
        self.grid(sticky="nsew")
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.new_update=new_update

        #Impotrt the language settings
        self.Messages = UserMessages.get_dict()


        Grid.columnconfigure(parent, 0, weight=1)
        Grid.rowconfigure(parent, 0, weight=1)

        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 2, weight=100)
        Grid.rowconfigure(self, 3, weight=1)
        Grid.rowconfigure(self, 4, weight=1)
        Grid.rowconfigure(self, 5, weight=1)

        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)

        #Short summary about current version, how to cite and how to find guidelines.
        Crow=0
        if new_update!=None:
            Lab_update=Label(self, text=self.Messages["Interface_Info_L2"] + new_update, font=("Arial", "20", "bold"), **Color_settings.My_colors.Label_Base)
            Lab_update.config(fg=Color_settings.My_colors.list_colors["Fg_not_valide"])
            Lab_update.grid(row=Crow, column=0,columnspan=2, sticky="nsew")
            Crow+=1

            link = Label(self, text=self.Messages["Interface_Info_L3"]+ "http://vchiara.eu/index.php/animalta", font=("Arial", "14", "bold"), cursor="hand2", **Color_settings.My_colors.Label_Base)
            link.config(fg="#b448cd")
            link.grid(row=Crow, column=0, columnspan=2, sticky="nsew")
            link.bind("<Button-1>", self.send_link)
            Crow += 1

            Lab11 = Label(self, text=self.Messages["Interface_Info_L1"], font=("Arial", "16", "bold"), **Color_settings.My_colors.Label_Base)
            Lab11.grid(row=Crow, column=0, columnspan=2, sticky="nsew")
            Crow += 1

            ponctB=Button(self, text=self.Messages["Interface_Info_L4"], command=self.do_update, **Color_settings.My_colors.Button_Base)
            ponctB.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
            ponctB.grid(row=Crow, column=0,columnspan=1, sticky="nsew")

            auto_upB = Button(self, text=self.Messages["Interface_Info_L5"], command=self.activate_auto, **Color_settings.My_colors.Button_Base)
            auto_upB.config(background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
            auto_upB.grid(row=Crow, column=1, columnspan=1, sticky="nsew")

            # Space
            Crow += 1
            #Space
            Crow += 1

            #CTXT
            Lab_version=Label(self, text="AnimalTA. Release version 4.2.0", font=("Arial", "14", "bold"), justify=LEFT, **Color_settings.My_colors.Label_Base)
            Lab_version.grid(row=Crow, column=0,columnspan=2, sticky="nsw")
            Crow += 1

        else:
            # CTXT
            Lab_version=Label(self, text="AnimalTA. Release version 4.2.0" , font=("Arial", "14", "bold"), **Color_settings.My_colors.Label_Base)
            Lab_version.grid(row=Crow, column=0,columnspan=2, sticky="nsw")
            Crow += 1

        Lab_cite=Label(self, text=self.Messages["Interface_Info_L6"], **Color_settings.My_colors.Label_Base)
        Lab_cite.grid(row=Crow, column=0,columnspan=2, sticky="nsw")
        Crow += 1

        Citation= Text(self, height=5, width=75, wrap=WORD, **Color_settings.My_colors.Label_Base)
        Citation.grid(row=Crow, column=0,columnspan=2, sticky="nswe")
        Citation.insert("1.0", "Chiara, V., & Kim, S.-Y. (2023). AnimalTA: A highly flexible and easy-to-use program for tracking and analysing animal movement in different environments. Methods in Ecology and Evolution, 14, 1699– 1707. https://doi.org/10.1111/2041-210X.14115")
        Citation.configure(state="disabled")
        Crow += 1

        #Space
        Crow += 1

        Lab_contact=Label(self, text=self.Messages["Interface_Info_L7"], **Color_settings.My_colors.Label_Base)
        Lab_contact.grid(row=Crow, column=0, sticky="nse")

        mail= Text(self, height=1, width=30, **Color_settings.My_colors.Label_Base)
        mail.insert("1.0", "contact.AnimalTA@vchiara.eu")
        mail.configure(state="disabled")
        mail.grid(row=Crow, column=1, sticky="nsw")
        Crow += 1

        #Space
        Crow += 1

        Lab_Help=Label(self, text=self.Messages["Interface_Info_L8"], **Color_settings.My_colors.Label_Base)
        Lab_Help.grid(row=Crow, column=0,columnspan=2, sticky="nsew")
        Crow += 1

        link = Label(self, text="http://vchiara.eu/index.php/animalta", cursor="hand2", **Color_settings.My_colors.Label_Base)
        link.config( fg="#b448cd")
        link.grid(row=Crow, column=0,columnspan=2, sticky="nsew")
        link.bind("<Button-1>", self.send_link)
        Crow += 1

        self.spinner_chars = cycle(
            ["Loading", ".Loading.", "..Loading..", "...Loading...", "... Loading ...", "...  Loading  ...", "...   Loading   ...", "...    Loading    ...", "...     Loading     ...", "...      Loading      ...", "...       Loading       ...", "..       Loading       ..", ".        Loading        ."]*3 +
             ["Loading","<Loading>","<\"Loading\">", "<\",Loading,\">", "<\",_Loading_,\">", "<\",_, Loading ,_,\">", "<\",_,}  Loading  {,_,\">", "<\",_,}-   Loading   -{,_,\">","<\",_,}--    Loading    --{,_,\">", "<\",_,}---     Loading      ---{,_,\">", "<\",_,}---      Loading       ---{,_,\">", "<\",_,}---       Loading        ---{,_,\">"])

        self.spinner_label = Label(self, text="", cursor="hand2", font=("Arial", "20", "bold"), **Color_settings.My_colors.Label_Base)
        self.spinner_label.grid(row=Crow, column=0,columnspan=3, sticky="nsew")
        Crow += 1

        for irow in range(Crow+1):
            self.rowconfigure(irow, minsize=30)

        self.stay_on_top()

    def stay_on_top(self):
        # We want this window to be always on top of the others
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)

    def send_link(self, event):
        webbrowser.open_new_tab("http://vchiara.eu/index.php/animalta")


    def spinning_cursor(self):
        while not self.download_done:
            self.spinner_label.config(text=next(self.spinner_chars))
            self.update()
            time.sleep(0.25)  # Schedule the function to run again after 100 ms

    def do_update(self):
        try:
            self.update_successful=False
            self.download_done=False
            Th_download = threading.Thread(target=Diverse_functions.download_new_version, args=((self.new_update,self)))
            Th_download.start()
            self.spinning_cursor()
            Th_download.join()

            if self.update_successful:
                Update_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "last_update.exe"))
                Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))

                # Get the system's temporary directory
                temp_dir = tempfile.gettempdir()
                temp_destination = os.path.join(temp_dir, "Settings_AnimalTA_10082024")

                # Copy the file
                shutil.copy(Param_file, temp_destination)
                subprocess.Popen([Update_file, '/SILENT'], shell=True)
                sys.exit()

            else:
                Interface_pretracking.CustomDialog(self.master,
                                                   text=self.Messages["Interface_Warn_2"],
                                                   title=self.Messages["Interface_Warn_1"])
        except:
            pass


    def activate_auto(self):
        Interface_settings.change_params("Auto_update",True)
        self.download_done=False
        Th_download = threading.Thread(target=Diverse_functions.download_new_version, args=((self.new_update,self)))
        Th_download.start()
        self.spinning_cursor()
        Th_download.join()

        Update_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "last_update.exe"))
        Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))

        # Get the system's temporary directory
        temp_dir = tempfile.gettempdir()
        temp_destination = os.path.join(temp_dir, "Settings_AnimalTA_10082024")

        # Copy the file
        shutil.copy(Param_file, temp_destination)

        subprocess.Popen([Update_file, '/SILENT'], shell=True)
        sys.exit()