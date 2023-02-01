from tkinter import *
from AnimalTA.A_General_tools import UserMessages
from AnimalTA.B_Project_organisation import Interface_pretracking
from ctypes import windll
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
        self.frame = Interface_pretracking.Interface(self)
        self.frame.grid(sticky="nsew")

    def set_appwindow(self,root):
        hwnd = windll.user32.GetParent(root.winfo_id())
        style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
        # re-assert the new window style
        root.wm_withdraw()
        root.after(10, lambda: root.wm_deiconify())

GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080

root=Mainframe()
root.overrideredirect(1)
root.geometry("1250x720")
root.geometry("+100+100")
img = PhotoImage(file=UserMessages.resource_path("AnimalTA/Files/Logo.png"))
root.wm_iconphoto(True, img)
root.after(10, lambda: root.set_appwindow(root=root))


Grid.rowconfigure(root,0,weight=1)
Grid.columnconfigure(root,0,weight=1)
root.mainloop()

