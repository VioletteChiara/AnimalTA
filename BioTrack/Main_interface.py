from tkinter import *
from BioTrack import Interface_pretracking, Interface_First_Time
from ctypes import windll
from PIL import Image, ImageTk

class Mainframe(Tk):
    def __init__(self):
        Tk.__init__(self)

        f = open("Files/Language", "r")
        Language=(f.read())

        if Language == "Undefined":
            newWindow = Toplevel(self)
            interface = Interface_First_Time.First_params(parent=newWindow, boss=self)
            interface.grid()
        else:
            self.open_BioTrack()


    def open_BioTrack(self):
        self.frame = Interface_pretracking.Interface(self)
        self.frame.grid(sticky="nsew")

    def change(self, frame2, vid=None, liste_of_videos=None):
        self.frame.grid_forget() # delete currrent frame
        if vid==None:
            self.frame = frame2(self, liste_of_videos=liste_of_videos)
        else:
            self.frame = frame2(self, vid=vid, liste_of_videos=liste_of_videos, main_frame=self)
        self.frame.grid(sticky="nsew") # make new frame


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

