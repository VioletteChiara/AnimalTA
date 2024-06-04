from tkinter import *
import os
from AnimalTA.A_General_tools import UserMessages, Color_settings


class Loading(Frame):
    #A loading bar
    def __init__(self, parent):
        Frame.__init__(self, parent, bd=5)
        self.config(**Color_settings.My_colors.Frame_Base)

        #Import messsages
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()

        self.Messages = UserMessages.Mess[self.Language.get()]

        self.loading_canvas = Frame(self,**Color_settings.My_colors.Frame_Base)
        self.loading_canvas.grid(row=4, columnspan=2)
        self.loading_state = Label(self.loading_canvas, text=self.Messages["Loading"],**Color_settings.My_colors.Label_Base)
        self.loading_state.grid(row=0, column=0)

        self.loading_bar = Canvas(self.loading_canvas, height=10, **Color_settings.My_colors.Frame_Base)
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill=Color_settings.My_colors.list_colors["Loading_before"])
        self.loading_bar.grid(row=0, column=1)
        self.grab_set()

    def __del__(self):
        self.grab_release()
        self.destroy()


    def show_load(self, prop):
        #Show the progress of the conversion process
        self.loading_bar.delete('all')
        heigh=self.loading_bar.cget("height")
        self.loading_bar.create_rectangle(0, 0, 400, heigh, fill=Color_settings.My_colors.list_colors["Loading_before"])
        self.loading_bar.create_rectangle(0, 0, prop*400, heigh, fill=Color_settings.My_colors.list_colors["Loading_after"])
        self.loading_bar.update()

