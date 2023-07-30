from tkinter import *
import os
from AnimalTA.A_General_tools import UserMessages
from AnimalTA.B_Project_organisation import Interface_pretracking
from tkinter import ttk
import urllib.request
import pickle

#How to run pyinstaller to have the exe file: pyinstaller cli.spec --noconsole --path="< Import path >"
class Mainframe(Tk):
    #Launch the rest of animalTA
    def __init__(self):
        Tk.__init__(self)

        #Change here the last version
        current_version="v2.3.3"

        try:
            # We look for new updates:
            last_version = urllib.request.urlopen("http://vchiara.eu/Last_version.txt").read().decode('utf-8')
            if last_version!= current_version:
                new_update = last_version
            else:
                new_update = None
        except:
            new_update = None


        style = ttk.Style(self)
        aktualTheme = style.theme_use()
        style.theme_create("dummy", parent=aktualTheme)
        style.theme_use("dummy")
        style.map('Treeview', background=[('selected', '#7ec9f7')], foreground=[("selected","black")])

        self.open_AnimalTA(current_version, new_update)

    def open_AnimalTA(self, current_version, new_update) -> object:
        #test_tres.test_fn()
        # If there was no parameters file, we add a new one: (versions before 3.0.0 did not had those)
        Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
        if not os.path.isfile(Param_file):
            with open(Param_file, 'wb') as fp:
                Params = dict(Sound_alert_track=True, Pop_alert_track=True, Size_img_display=600, Back_tool=20)
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

            if modifications:
                with open(Param_file, 'wb') as fp:
                    pickle.dump(Params, fp)


        self.frame = Interface_pretracking.Interface(self, current_version, new_update)
        self.frame.grid(sticky="nsew")

root=Mainframe()
root.overrideredirect(1)
root.geometry("1250x720")
root.geometry("+100+100")
img = PhotoImage(file=UserMessages.resource_path(os.path.join("AnimalTA","Files","Logo.png")))
root.wm_iconphoto(True, img)


Grid.rowconfigure(root,0,weight=1)
Grid.columnconfigure(root,0,weight=1)
root.mainloop()