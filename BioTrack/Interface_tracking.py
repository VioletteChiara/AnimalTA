from tkinter import *
from BioTrack import Canvas_1I_1A, UserMessages


class User_inter(Frame):
    def __init__(self, parent, main_frame, vid, liste_of_videos, portion=False, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.grid(sticky="nsew")
        self.Vid=vid
        self.grab_set()
        self.main_frame=main_frame
        self.liste_of_videos=liste_of_videos
        self.portion=portion
        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()

        self.Messages = UserMessages.Mess[self.Language.get()]


        # Canvas:
        # Barre de titre
        self.rows_optns = Frame(self, bd=2, highlightthickness=1, relief='flat')
        self.rows_optns.grid(sticky="w")

        # Widget row options:
        self.Optns_Lab = Label(self.rows_optns, textvar=self.main_frame.project_name, bg="darkgrey", relief="flat",
                               font=("Arial", 14))
        self.Optns_Lab.grid(row=0, column=0, sticky="w")

        self.Video_name = Label(self.rows_optns, text=self.Vid.Name, bg="lightgrey", relief="flat",
                               font=("Arial", 12))
        self.Video_name.grid(row=0, column=1, sticky="w")





        # Widgets:
        # Barre de titre
        self.position_mouse = StringVar()
        self.position_mouse.set("x=0, y=0")
        self.position_mouse_lab = Label(self.rows_optns, textvariable=self.position_mouse)
        self.position_mouse_lab.grid(row=0, column=2)

        #Canvas_1I_1A:
        self.Can_1I_1A= Canvas_1I_1A.T1I_1A(parent=self, video=self.Vid, main_frame=self.main_frame, liste_of_videos=self.liste_of_videos, portion=self.portion, height=150, bd=2, highlightthickness=1, relief='ridge')
        self.Can_1I_1A.grid(row=4)

