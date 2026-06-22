from tkinter import *
import os
from AnimalTA.A_General_tools import UserMessages, Color_settings
import time

class Loading(Frame):
    #A loading bar
    def __init__(self, parent, text=None, grab=True):
        Frame.__init__(self, parent, bd=5)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent

        #Import messsages
        self.Messages = UserMessages.get_dict()

        self.loading_canvas = Frame(self,**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.loading_canvas.grid(row=4, columnspan=2)

        if text is None:
            text=self.Messages["Loading"]

        self.loading_state = Label(self.loading_canvas, text=text,**Color_settings.My_colors.Label_Base)
        self.loading_state.grid(row=0, column=0)

        self.loading_bar = Canvas(self.loading_canvas, height=10, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill=Color_settings.My_colors.list_colors["Loading_before"])
        self.loading_bar.grid(row=0, column=1)
        if grab:
            self.grab_set()

    def __del__(self):
        self.grab_release()
        self.destroy()

    def show_loading_while(self, thread, fps=30):
        cur_rot = 0
        while thread.is_alive():
            self.loading_bar.delete('all')
            heigh = self.loading_bar.cget("height")
            self.loading_bar.create_rectangle(0, 0, 400, heigh,
                                              fill=Color_settings.My_colors.list_colors["Loading_before"])
            self.loading_bar.create_rectangle(max(0, cur_rot * 400 - 50), 0, min(cur_rot * 400, 450), heigh,
                                              fill=Color_settings.My_colors.list_colors["Loading_after"])
            self.loading_bar.update()

            cur_rot = 0 if cur_rot > 1.25 else cur_rot + 0.025
            time.sleep(1 / fps)


    def show_load(self, prop):
        if prop>=0:
            #Show the progress of the conversion process
            self.loading_bar.delete('all')
            heigh=self.loading_bar.cget("height")
            self.loading_bar.create_rectangle(0, 0, 400, heigh, fill=Color_settings.My_colors.list_colors["Loading_before"])
            self.loading_bar.create_rectangle(0, 0, prop*400, heigh, fill=Color_settings.My_colors.list_colors["Loading_after"])
            self.loading_bar.update()