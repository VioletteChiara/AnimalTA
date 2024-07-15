from tkinter import *
import pyautogui



class small_info(Frame):
    def __init__(self, elem, parent, message, *args):
        Frame.__init__(self, parent, bd=5)
        self.info=[]
        self.elem=elem
        self.parent = parent
        self.message = message

        self.elem.bind("<Enter>", self.show_hint)
        self.elem.bind("<Leave>", self.hide_hint)

    def show_hint(self, event):
        self.info = Toplevel(self.parent)
        self.info.wm_overrideredirect(1)

        pos = pyautogui.position()
        new_pos = (pos[0]+10, pos[1])
        self.info.wm_geometry("+%d+%d" % new_pos)

        label = Label(self.info, text=self.message,justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"), wraplength=200)
        label.grid()

    def hide_hint(self, event):
        self.info.destroy()