from tkinter import *
from BioTrack import UserMessages

class Help_win(Frame):
    def __init__(self, parent, default_message="",width=0, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(height=100, highlightthickness=4, relief='flat', highlightbackground="RoyalBlue3")

        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        self.default_message=default_message


        #Titre
        Info_title=Label(self, text=self.Messages["Info"],  justify=CENTER, background="RoyalBlue3", fg="white", font=("Helvetica", 16, "bold"))
        Info_title.grid(row=0, sticky="new")
        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1000)

        Container=Frame(self)
        Container.grid(row=1, sticky="nsew")
        Grid.columnconfigure(Container, 0, weight=100)
        Grid.columnconfigure(Container, 1, weight=1)
        Grid.rowconfigure(Container, 0, weight=1)

        self.Canvas_txt=Canvas(Container, width=width)
        Scrollbar_txt=Scrollbar(Container, orient="vertical", command=self.Canvas_txt.yview)
        Grid.columnconfigure(self.Canvas_txt, 0, weight=1)
        Grid.rowconfigure(self.Canvas_txt, 0, weight=1)

        Frame_txt=Frame(self.Canvas_txt)
        Frame_txt.bind("<Configure>", self.redo_scrollable)
        Frame_txt.grid(row=0, column=0, sticky="nsew")


        self.Canvas_txt.create_window((0, 0), window=Frame_txt, anchor="nw")
        self.Canvas_txt.configure(yscrollcommand=Scrollbar_txt.set)


        self.user_message=StringVar()
        self.user_message.set(self.default_message)
        self.User_help=Label(Frame_txt, textvariable=self.user_message, justify=LEFT)

        self.User_help.grid(row=0, column=0, sticky="new")
        self.Canvas_txt.bind("<Configure>", self.set_label_wrap)

        self.Canvas_txt.grid(row=0, column=0, sticky="nsew")
        Scrollbar_txt.grid(row=0, column=1, sticky="ns")



    def set_label_wrap(self, event):
        self.User_help.configure(wraplength=event.width - 10)

    def redo_scrollable(self, *args):
        self.Canvas_txt.configure(scrollregion=self.Canvas_txt.bbox("all"))

    def get_attention(self, count):
        curcol = self.User_help.cget("bg")
        if curcol == "red":
            self.User_help.config(bg="SystemButtonFace")
        else:
            self.User_help.config(bg="red")
        if (count) < 5:
            count += 1
            self.User_help.after(250, self.get_attention, count)

    def change_tmp_message(self, new_message, *args):
        self.user_message.set(new_message)
        self.Canvas_txt.yview_moveto("0.0")


    def remove_tmp_message(self, *args):
        self.user_message.set(self.default_message)
        self.Canvas_txt.yview_moveto("0.0")

    def change_default_message(self, new_message, *args):
        self.default_message=new_message
        self.remove_tmp_message()
        self.Canvas_txt.yview_moveto("0.0")

