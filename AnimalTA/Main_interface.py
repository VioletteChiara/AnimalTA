from tkinter import *
import os
from AnimalTA.A_General_tools import UserMessages, Diverse_functions, Color_settings
from AnimalTA.B_Project_organisation import Interface_pretracking
import subprocess
import urllib.request
from tkinter import ttk
import urllib.request
import pickle
from ctypes import windll
import threading
import sys
import tempfile
import shutil

# pyinstaller cli.py --noconsole
class Mainframe(Tk):
    #Launch the rest of animalTA
    def __init__(self):
        Tk.__init__(self)

        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            # Your logic to handle the file here
        else:
            file_path=None

        #Change here the last version
        current_version="v3.2.2"

        #We check the parameters
        Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))

        temp_dir = tempfile.gettempdir()
        temp_destination = os.path.join(temp_dir, "Settings_AnimalTA_10082024")

        if os.path.exists(temp_destination):
            shutil.copy(temp_destination, Param_file)
            os.remove(temp_destination)

        if not os.path.isfile(Param_file):
            with open(Param_file, 'wb') as fp:
                Params = dict(Sound_alert_track=True, Pop_alert_track=True, Size_img_display=600, Back_tool=20,
                              Low_priority=False, Use_Kalman=False, Check_hide_missing=False,
                              Relative_background=False, Keep_entrance=False, Color_GUI="Light",Auto_update=False)
                pickle.dump(Params, fp)
        else:
            with open(Param_file, 'rb') as fp:
                Params = pickle.load(fp)

            modifications = False
            if "Size_img_display" not in Params.keys():
                Params["Size_img_display"] = 600
                modifications = True

            if "Back_tool" not in Params.keys():
                Params["Back_tool"] = 20
                modifications = True

            if "Low_priority" not in Params.keys():
                Params["Low_priority"] = False
                modifications = True

            if "Use_Kalman" not in Params.keys():
                Params["Use_Kalman"] = False
                modifications = True

            if "Check_hide_missing" not in Params.keys():
                Params["Check_hide_missing"] = False
                modifications = True

            if "Relative_background" not in Params.keys():
                Params["Relative_background"] = False
                modifications = True

            if "Keep_entrance" not in Params.keys():
                Params["Keep_entrance"] = False
                modifications = True

            if "Color_GUI" not in Params.keys():
                Params["Color_GUI"] = "Light"
                modifications = True

            if "Auto_update" not in Params.keys():
                Params["Auto_update"] = False
                modifications = True


            if modifications:
                with open(Param_file, 'wb') as fp:
                    pickle.dump(Params, fp)

        Diverse_functions.low_priority(Params["Low_priority"])

        try:
            # We look for new updates:
            try:
                f = open(UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Last_downloaded")), "r", encoding="utf-8")
                Last_downloaded=f.read()
                f.close()
            except:
                Last_downloaded=current_version
                f = open(UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Last_downloaded")), "w", encoding="utf-8")
                f.write(current_version)
                f.close()

            last_version = urllib.request.urlopen("http://vchiara.eu/Last_version.txt").read().decode('utf-8')
            if last_version!= current_version:
                new_update = last_version
                installer_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "last_update.exe"))
                if Params["Auto_update"]:
                    if Last_downloaded!=last_version or not os.path.exists(installer_file):
                        Th_dwonload = threading.Thread(target=Diverse_functions.download_new_version, args=(last_version,))
                        Th_dwonload.start()

                        new_update = None
                    else:
                        update_res=self.do_update()
                        new_update = None
                        installer_file = UserMessages.resource_path(
                            os.path.join("AnimalTA", "Files", "last_update.exe"))
                        installer_file_tmp = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "last_update.crdownload"))

                        try:
                            os.remove(installer_file_tmp)
                        except Exception as e:
                            pass


                        try:
                            os.remove(installer_file)
                        except Exception as e:
                            pass


            else:
                new_update = None
                installer_file = UserMessages.resource_path(
                    os.path.join("AnimalTA", "Files", "last_update.exe"))
                installer_file_tmp = UserMessages.resource_path(
                    os.path.join("AnimalTA", "Files", "last_update.crdownload"))

                try:
                    os.remove(installer_file_tmp)
                except Exception as e:
                    pass

                try:
                    os.remove(installer_file)
                except Exception as e:
                    pass


        except Exception as e:
            print(e)
            new_update = None

        self.open_AnimalTA(current_version, new_update, file_path)

    def do_update(self):
        try:
            Update_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "last_update.exe"))
            Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))

            # Get the system's temporary directory
            temp_dir = tempfile.gettempdir()
            temp_destination = os.path.join(temp_dir, "Settings_AnimalTA_10082024")

            # Copy the file
            shutil.copy(Param_file, temp_destination)

            subprocess.Popen([Update_file, '/SILENT'], shell=True)
            sys.exit()

        except Exception as e:
            print(e)
            return (False, e)

    def open_AnimalTA(self, current_version, new_update, file_path) -> object:
        #test_tres.test_fn()
        # If there was no parameters file, we add a new one: (versions before 3.0.0 did not had those)
        self.frame = Interface_pretracking.Interface(self, current_version, new_update, file_path=file_path)
        self.frame.grid(sticky="nsew")


GWL_EXSTYLE=-20
WS_EX_APPWINDOW=0x00040000
WS_EX_TOOLWINDOW=0x00000080



def set_appwindow(root):
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())


root=Mainframe()
style = ttk.Style()
style.theme_use('clam')

#We create the styles:
style.map(
    "Horizontal.TScrollbar",
    background=[('active', Color_settings.My_colors.list_colors["Base"]), ('!active', Color_settings.My_colors.list_colors["Base"])],
    troughcolor=[('active', Color_settings.My_colors.list_colors["Glider_Base"]), ('!active', Color_settings.My_colors.list_colors["Glider_Base"])],
)


style.configure(
    "Horizontal.TScrollbar",
    arrowsize=15,
    arrowcolor=Color_settings.My_colors.list_colors["Arrow_N_Relief_scroll"],
    bordercolor=Color_settings.My_colors.list_colors["Arrow_N_Relief_scroll"],
    gripcount=0,
    relief="flat",
    padding=0
)

style.map(
    "Vertical.TScrollbar",
    background=[('active', Color_settings.My_colors.list_colors["Base"]), ('!active', Color_settings.My_colors.list_colors["Base"])],
    troughcolor=[('active', Color_settings.My_colors.list_colors["Glider_Base"]), ('!active', Color_settings.My_colors.list_colors["Glider_Base"])],
)

style.configure(
    "Vertical.TScrollbar",
    arrowsize=15,
    arrowcolor=Color_settings.My_colors.list_colors["Arrow_N_Relief_scroll"],
    borderwidth=0,  # Set border width to 0 to remove the default border
    highlightthickness=0,  # Remove highlight
    gripcount=0,
    relief="flat",  # Ensure relief is flat to remove any 3D effects
    padding=0,
    background=Color_settings.My_colors.list_colors["Base"],  # Set the background color
    troughcolor=Color_settings.My_colors.list_colors["Glider_Base"]  # Set the trough color
)

def fixed_map(option):
    # Fix for setting text colour for Tkinter 8.6.9
    # From: https://core.tcl.tk/tk/info/509cafafae
    #
    # Returns the style map for 'option' with any styles starting with
    # ('!disabled', '!selected', ...) filtered out.

    # style.map() returns an empty list for missing options, so this
    # should be future-safe.
    return [elm for elm in style.map('Treeview', query_opt=option) if
            elm[:2] != ('!disabled', '!selected')]


style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))
style.configure("Treeview", background=Color_settings.My_colors.list_colors["Table1"],
                fieldbackground=Color_settings.My_colors.list_colors["Table1"],
                foreground=Color_settings.My_colors.list_colors["Fg_T1"])
style.configure("Treeview.Heading", background=Color_settings.My_colors.list_colors["Header_check"],
                foreground=Color_settings.My_colors.list_colors["Fg_Header_check"])

style.map("Treeview.Heading",
          background=[("active", Color_settings.My_colors.list_colors["Header_check"])],
          foreground=[("active", Color_settings.My_colors.list_colors["Fg_Header_check"])])

style.map("Treeview",
          background=[("selected", Color_settings.My_colors.list_colors["Selected_row_check"])],
          foreground=[("selected", Color_settings.My_colors.list_colors["Fg_Selected_row_check"])])


root.overrideredirect(1)
root.geometry("1250x720")
root.geometry("+100+100")
root.after(10, lambda: set_appwindow(root))
root.iconbitmap(UserMessages.resource_path(os.path.join("AnimalTA","Files","Logo.ico")))

Grid.rowconfigure(root,0,weight=1)
Grid.columnconfigure(root,0,weight=1)
root.mainloop()