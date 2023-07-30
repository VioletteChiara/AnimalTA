from tkinter import *
from AnimalTA.A_General_tools import UserMessages
import os
import pickle


class Settings_panel(Frame):
    def __init__(self, parent, main, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.main=main
        Grid.columnconfigure(parent, 0, weight=1)
        Grid.rowconfigure(parent, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 2, weight=1)
        Grid.rowconfigure(self, 3, weight=1)
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)

        self.grid(sticky="nsew")

        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        self.Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
        with open(self.Param_file, 'rb') as fp:
            Params = pickle.load(fp)

        self.Sound_track=BooleanVar()
        self.Sound_track.set(Params["Sound_alert_track"])

        self.Pop_track=BooleanVar()
        self.Pop_track.set(Params["Pop_alert_track"])

        self.Size_img_display=IntVar()
        self.Size_img_display.set(Params["Size_img_display"])

        self.Back_tool=IntVar()
        self.Back_tool.set(Params["Back_tool"])

        Checkbutton(self, text=self.Messages["Settings1"], variable=self.Sound_track).grid(row=0, columnspan=2, sticky="sw")
        Checkbutton(self, text=self.Messages["Settings2"], variable=self.Pop_track).grid(row=1, columnspan=2, sticky="sw")

        Label(self, text=self.Messages["Settings3"]).grid(row=2, column=0, sticky="sw")
        Scale(self, from_=100, to=2000, variable=self.Size_img_display, orient=HORIZONTAL).grid(row=2,column=1, sticky="sw")

        Label(self, text=self.Messages["Settings4"]).grid(row=3, column=0, sticky="sw")
        Scale(self, from_=1, to=100, variable=self.Back_tool, orient=HORIZONTAL).grid(row=3,column=1, sticky="sw")


        Button(self, text=self.Messages["Validate"], background="#6AED35", command=self.validate).grid(row=4, columnspan=2, sticky="sew")

        self.stay_on_top()

    def stay_on_top(self):
        # We want this window to be always on top of the others
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)

    def validate(self):
        with open(self.Param_file, 'wb') as fp:
            data_to_save = dict(Sound_alert_track=self.Sound_track.get(), Pop_alert_track=self.Pop_track.get(), Size_img_display=self.Size_img_display.get(), Back_tool=self.Back_tool.get())
            pickle.dump(data_to_save, fp)

        try:#If there is a project open, we update
            self.main.update_projects()
        except:
            pass

        self.destroy()
        self.parent.destroy()