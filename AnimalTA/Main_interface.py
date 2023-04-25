from tkinter import *
import os
from AnimalTA.A_General_tools import UserMessages
from AnimalTA.B_Project_organisation import Interface_pretracking
from AnimalTA.B_Project_organisation import test_tres
from tkinter import ttk


#How to run pyinstaller to have the exe file: pyinstaller cli.spec --noconsole --path="< Import path >"

class Mainframe(Tk):
    #Launch the rest of animalTA
    def __init__(self):
        Tk.__init__(self)
        style = ttk.Style(self)
        aktualTheme = style.theme_use()
        style.theme_create("dummy", parent=aktualTheme)
        style.theme_use("dummy")
        style.map('Treeview', background=[('selected', '#7ec9f7')], foreground=[("selected","black")])
        self.open_AnimalTA()

    def open_AnimalTA(self) -> object:
        #test_tres.test_fn()
        self.frame = Interface_pretracking.Interface(self)
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

