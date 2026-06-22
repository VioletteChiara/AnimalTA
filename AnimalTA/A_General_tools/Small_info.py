from tkinter import *
import pyautogui
from functools import partial

class small_info(Frame):
    def __init__(self, elem, parent, message, time=1, *args):
        Frame.__init__(self, parent, bd=5)
        self.info=[]
        self.elem=elem
        self.parent = parent
        self.message = message
        self.time=time

        self.out=False

        self.elem.bind("<Enter>", self.begin_time)
        self.elem.bind("<Leave>", self.hide_hint)

    def begin_time(self, *args):
        self.out=False
        self.parent.after(self.time*1000, self.show_hint)

    def show_hint(self, *args):
        if not self.out:
            try:
                self.info.destroy()
            except:
                pass
            self.info = Toplevel(self.parent)
            self.info.wm_overrideredirect(1)
            self.info.attributes("-topmost", True)

            pos = pyautogui.position()
            new_pos = (pos[0]+10, pos[1])
            self.info.wm_geometry("+%d+%d" % new_pos)

            label = Label(self.info, text=self.message,justify=LEFT,
                          background="#ffffe0", relief=SOLID, borderwidth=1,
                          font=("tahoma", "8", "normal"), wraplength=200)
            label.grid()

    def hide_hint(self, *args):
        self.out=True
        try:
            self.info.destroy()
        except:
            pass


class small_info_spe_menus(Frame):
    def __init__(self, menu, entries, parent, messages, time=1, *args):
        Frame.__init__(self, parent, bd=5)
        self.info=[]
        self.menu=menu
        self.entries=entries
        self.parent = parent
        self.messages = messages

        self.old_mess=None

        self.time=time

        self.info_flag=False

        self.real_menu = self.menu["menu"]
        self.real_menu.config(postcommand=self.start_tracking)

    def start_tracking(self):
        self.track_hover()

    def track_hover(self):
        try:
            index = self.real_menu.index("active")
        except:
            index = None

        pos=0
        found_one=None
        for entry in self.entries:
            if index == entry:
                if not self.info_flag:
                    self.begin_time(self.messages[pos])
                found_one=pos
                break
            pos+=1

        if found_one is None or (not self.old_mess is None and self.old_mess!=self.messages[found_one]):
            self.hide_hint()

        # keep checking while menu is open
        self.parent.after(50, self.track_hover)


    def begin_time(self, message, *args):
        self.out=False
        if not self.info_flag:
            self.info_flag=True
            self.parent.after(self.time*1000, partial(self.show_hint, message=message))


    def show_hint(self, message, *args):
        if not self.out:
            self.old_mess=message
            self.info = Toplevel(self.menu)
            self.info.attributes("-topmost", True)
            self.info.wm_overrideredirect(1)

            pos = pyautogui.position()
            new_pos = (pos[0]+10, pos[1])
            self.info.wm_geometry("+%d+%d" % new_pos)

            label = Label(self.info, text=message,justify=LEFT,
                          background="#ffffe0", relief=SOLID, borderwidth=1,
                          font=("tahoma", "8", "normal"), wraplength=200)
            label.grid()


    def hide_hint(self, *args):
        self.out=True
        if self.info_flag:
            try:
                self.info.destroy()
            except:
                pass
            self.info_flag=False
            self.old_mess=None