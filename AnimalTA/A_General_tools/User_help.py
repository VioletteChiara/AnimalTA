from tkinter import *
from tkinter import ttk
import os
from AnimalTA.A_General_tools import UserMessages, Color_settings
import PIL
import cv2

class Help_win(Frame):
    def __init__(self, parent, default_message="", shortcuts={}, legend={},width=0, **kwargs):
        """This Frame is reused everywhere in the program and consist in a little text of explanation about how the program is working.
        The text is changing according to which step of the program the user is doing."""
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.list_colors = Color_settings.My_colors.list_colors
        self.config(height=100, highlightthickness=4, relief='flat', highlightcolor=self.list_colors["Title1"], highlightbackground=self.list_colors["Title1"], background=self.list_colors["Base"])

        #Messages importation
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]
        self.default_message=default_message

        self.logo = cv2.imread(UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Logo_fond.png")))
        self.logo = cv2.cvtColor(self.logo, cv2.COLOR_BGR2RGB)
        self.Size_logo = self.logo.shape
        self.logo = cv2.resize(self.logo, (int(self.Size_logo[1] / 2), int(self.Size_logo[0] / 2)))
        self.logo2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.logo))

        #Title
        Info_title=Label(self, text=self.Messages["Info"],  justify=CENTER, background=self.list_colors["Title1"], fg=self.list_colors["Fg_Title1"], font=("Helvetica", 16, "bold"))
        Info_title.grid(row=0, sticky="new")
        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1000)


        Container=Frame(self, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        Container.grid(row=1, sticky="nsew")
        Grid.columnconfigure(Container, 0, weight=100)
        Grid.columnconfigure(Container, 1, weight=1)
        Grid.rowconfigure(Container, 0, weight=1)

        self.Canvas_txt=Canvas(Container, width=width, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        Scrollbar_txt=ttk.Scrollbar(Container, orient="vertical", command=self.Canvas_txt.yview)
        Grid.columnconfigure(self.Canvas_txt, 0, weight=1)
        Grid.rowconfigure(self.Canvas_txt, 0, weight=1)

        #Text
        self.Frame_txt=Frame(self.Canvas_txt, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.Frame_txt.bind("<Configure>", self.redo_scrollable)
        self.Frame_txt.grid(row=0, column=0, sticky="nsew")
        self.Canvas_txt.create_window((0, 0), window=self.Frame_txt, anchor="nw")
        self.Canvas_txt.configure(yscrollcommand=Scrollbar_txt.set)
        self.user_message=StringVar()
        self.user_message.set(self.default_message)
        self.User_help=Label(self.Frame_txt, textvariable=self.user_message, justify=LEFT, **Color_settings.My_colors.Label_Base, bd=0, highlightthickness=0)
        self.User_help.grid(row=0, column=0, sticky="new")
        self.Canvas_txt.bind("<Configure>", self.set_label_wrap)
        self.Canvas_txt.grid(row=0, column=0, sticky="nsew")
        Scrollbar_txt.grid(row=0, column=1, sticky="ns")#Scrollbar in case of long text

        Grid.columnconfigure(self.Frame_txt, 0, weight=1)
        Grid.rowconfigure(self.Frame_txt, 0, weight=1000, minsize=125)
        Grid.rowconfigure(self.Frame_txt, 1, weight=1)
        Grid.rowconfigure(self.Frame_txt, 2, minsize=1)
        Grid.rowconfigure(self.Frame_txt, 3, minsize=1)
        Grid.rowconfigure(self.Frame_txt, 4, weight=1000)

        self.view_logo = Canvas(self.Frame_txt, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.view_logo.config(width=0, height=0)
        self.view_logo.grid(row=1, columnspan=2, sticky="ns")

        if len(legend)>0:
            cur_col=0
            Fr_legend=Frame(self.Frame_txt, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
            Fr_legend.grid(row=2,sticky="nsew")
            Grid.rowconfigure(Fr_legend, 0, weight=1)

            for i, (name,value) in enumerate(legend.items()):
                Label(Fr_legend, text=name, bg=value, height=4).grid(row=0,column=cur_col, sticky="nsew")
                Grid.columnconfigure(Fr_legend, cur_col, weight=1, minsize=int(250 / len(legend)))
                cur_col+=1

        #Shortcuts infos:
        if len(shortcuts)>0:
            Short_title=Label(self.Frame_txt, text="\n"+self.Messages["Shortcuts"]+":", **Color_settings.My_colors.Label_Base, bd=0, highlightthickness=0,  justify=CENTER, font=("Helvetica", 10, "bold"))
            Short_title.grid(row=3, sticky="w")

            #Text
            Frame_short=Frame(self.Frame_txt, **Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
            Frame_short.grid(row=4, column=0, sticky="nw")
            Grid.columnconfigure(Frame_short, 0, weight=100, minsize=100)
            Grid.columnconfigure(Frame_short, 1, weight=1)
            Grid.columnconfigure(Frame_short, 2, weight=100)

            pos=0
            for i, (name,value) in enumerate(shortcuts.items()):
                Lab1=Label(Frame_short, text=name, justify=CENTER, fg=self.list_colors["Fg_T1"], background=self.list_colors["Table1"],wraplength=130)
                Lab1.grid(row=pos, column=0, sticky="nsew")
                Frame(Frame_short, width=1, background=self.list_colors["Separator_T1"]).grid(row=pos, column=1, sticky="news")
                Lab2=Label(Frame_short, text=value, justify=LEFT, fg=self.list_colors["Fg_T1"], background=self.list_colors["Table1"],wraplength=130)
                Lab2.grid(row=pos, column=2, sticky="nsew")
                Frame(Frame_short, height=1, background=self.list_colors["Separator_T1"]).grid(row=pos+1, column=0, columnspan=3, sticky="nsew")
                Frame(Frame_short, height=1, background=self.list_colors["Separator_T1"]).grid(row=pos + 2, column=0, columnspan=3, sticky="nsew")

                Grid.rowconfigure(Frame_short, pos, weight=10)
                Grid.rowconfigure(Frame_short, pos+1, weight=1)
                Grid.rowconfigure(Frame_short, pos+1, weight=1)

                pos+=3



    def set_label_wrap(self, event):
        #Fix width of the text according to available space
        self.User_help.configure(wraplength=event.width - 10)

    def redo_scrollable(self, *args):
        self.Canvas_txt.configure(scrollregion=self.Canvas_txt.bbox("all"))

    def get_attention(self, count):
        #Make the text blink to attract user's attention
        Grid.rowconfigure(self.Frame_txt, 0, weight=1000, minsize=0)
        self.view_logo.config(width=int(self.Size_logo[1] / 2), height=int(self.Size_logo[0] / 2))

        if count%2==0:
            self.view_logo.delete("all")
        else:
            self.view_logo.create_image(0, 0, image=self.logo2, anchor=NW)
        if (count) < 10:
            count += 1
            self.User_help.after(200, self.get_attention, count)
        else:
            Grid.rowconfigure(self.Frame_txt, 0, weight=1000, minsize=125)
            self.view_logo.config(width=0, height=0)


    #There are default messages (when the user is not interacting with anything)
    #And temporary messages which appear only when user is interacting with something (cursor over a button for instance)
    #When the temporary message disapear it is replaced by the default one.
    def change_tmp_message(self, new_message, *args):
        #Replace the message by a temporary one (for instance info about a button over which the cursor is)
        self.user_message.set(new_message)
        self.Canvas_txt.yview_moveto("0.0")

    def remove_tmp_message(self, *args):
        #The temporary message is changed by the defauts message (for instance the user take the cursor out of a button whose info were displayed)
        self.user_message.set(self.default_message)
        self.Canvas_txt.yview_moveto("0.0")

    def change_default_message(self, new_message, *args):
        #Change the default message
        self.default_message=new_message
        self.remove_tmp_message()
        self.Canvas_txt.yview_moveto("0.0")


