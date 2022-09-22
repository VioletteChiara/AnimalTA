from tkinter import *
from AnimalTA import Interface_pretracking, UserMessages
from ctypes import windll

class Mainframe(Tk):
    #Launch the rest of animalTA
    def __init__(self):
        Tk.__init__(self)
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
img = PhotoImage(file='Files/Logo.png')
root.wm_iconphoto(True, img)
root.after(10, lambda: root.set_appwindow(root=root))


Grid.rowconfigure(root,0,weight=1)
Grid.columnconfigure(root,0,weight=1)
root.mainloop()

