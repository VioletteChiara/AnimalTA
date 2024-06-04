from tkinter import *
from AnimalTA.A_General_tools import UserMessages, Color_settings, Small_info


class Details_back(Frame):
    """ This is a small Frame in which the user can define the nomber of targets per arena, in the case the number is variable between arenas."""
    def __init__(self, parent, boss, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.boss=boss
        self.grid(sticky="nsew")
        self.config(**Color_settings.My_colors.Frame_Base)
        self.grab_set()

        Grid.columnconfigure(self.parent,0,weight=1)
        Grid.rowconfigure(self.parent, 0, weight=1)


        #Message importation
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()


        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title("")

        #Choose relative/absolute background

        self.target_type = IntVar()
        self.target_type.set(self.boss.target_type.get())

        Frame_color_targ=Frame(self, **Color_settings.My_colors.Frame_Base)
        Frame_color_targ.config(highlightbackground=Color_settings.My_colors.list_colors["Frame"], highlightthickness=2, borderwidth=2)
        Frame_color_targ.grid(row=0, column=0, sticky="nsew")

        Grid.columnconfigure(Frame_color_targ, 0, weight=1)
        Grid.columnconfigure(Frame_color_targ, 1, weight=1)
        Grid.columnconfigure(Frame_color_targ, 2, weight=1)
        Grid.rowconfigure(Frame_color_targ, 0, weight=1)
        Grid.rowconfigure(Frame_color_targ, 1, weight=1)

        Title1=Label(Frame_color_targ, text=self.Messages["Supp_Param0"], **Color_settings.My_colors.Label_Base)
        Title1.config(background=Color_settings.My_colors.list_colors["Title1"], fg=Color_settings.My_colors.list_colors["Fg_Title1"], font=("Helvetica",13,"bold"), justify=CENTER)
        Title1.grid(row=0, columnspan=3, column=0, sticky="nsew")


        R1=Radiobutton(Frame_color_targ, text=self.Messages["Supp_Param1"], value=0, variable=self.target_type, **Color_settings.My_colors.Radiobutton_Base)
        R1.grid(row=1, column=0)
        Small_info.small_info(elem=R1, parent=self, message=self.Messages["Supp_Param1_ex"])
        R2=Radiobutton(Frame_color_targ, text=self.Messages["Supp_Param2"], value=1, variable=self.target_type, **Color_settings.My_colors.Radiobutton_Base)
        R2.grid(row=1, column=1)
        Small_info.small_info(elem=R2, parent=self, message=self.Messages["Supp_Param2_ex"])
        R3=Radiobutton(Frame_color_targ, text=self.Messages["Supp_Param3"], value=2, variable=self.target_type, **Color_settings.My_colors.Radiobutton_Base)
        R3.grid(row=1, column=2)
        Small_info.small_info(elem=R3, parent=self, message=self.Messages["Supp_Param3_ex"])


        Frame_rel_back=Frame(self, **Color_settings.My_colors.Frame_Base)
        Frame_rel_back.config(highlightbackground=Color_settings.My_colors.list_colors["Frame"], highlightthickness=2, borderwidth=2)
        Frame_rel_back.grid(row=1, column=0, sticky="nsew")

        Title1=Label(Frame_rel_back, text=self.Messages["Supp_Param0B"], **Color_settings.My_colors.Label_Base)
        Title1.config(background=Color_settings.My_colors.list_colors["Title1"], fg=Color_settings.My_colors.list_colors["Fg_Title1"], font=("Helvetica",13,"bold"), justify=CENTER)
        Title1.grid(row=0, columnspan=2, column=0, sticky="nsew")

        self.rel_back=IntVar()
        self.rel_back.set(self.boss.rel_back.get())
        R4=Radiobutton(Frame_rel_back, text=self.Messages["Supp_Param4"], value=0, variable=self.rel_back, **Color_settings.My_colors.Radiobutton_Base)
        R4.grid(row=1, column=0)
        Small_info.small_info(elem=R4, parent=self, message=self.Messages["Supp_Param4_ex"])
        R5=Radiobutton(Frame_rel_back, text=self.Messages["Supp_Param5"], value=1, variable=self.rel_back, **Color_settings.My_colors.Radiobutton_Base)
        R5.grid(row=1, column=1)
        Small_info.small_info(elem=R5, parent=self, message=self.Messages["Supp_Param5_ex"])

        Grid.columnconfigure(Frame_rel_back, 0, weight=1)
        Grid.columnconfigure(Frame_rel_back, 1, weight=1)
        Grid.rowconfigure(Frame_rel_back, 0, weight=1)
        Grid.rowconfigure(Frame_rel_back, 1, weight=1)


        #Validation button
        self.B_validate = Button(self, text=self.Messages["Validate"], command=self.validate, **Color_settings.My_colors.Button_Base)
        self.B_validate.config(bg=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.B_validate.grid(sticky="nsew")

        Grid.columnconfigure(self,0,weight=1)
        Grid.rowconfigure(self, 0, weight=10)
        Grid.rowconfigure(self, 1, weight=10)
        Grid.rowconfigure(self, 2, weight=1)


    def validate(self):
        #Save and destroy the parent window
        self.boss.rel_back.set(self.rel_back.get())
        self.boss.target_type.set(self.target_type.get())
        self.boss.modif_image()
        self.grab_release()
        self.parent.destroy()



"""
root = Tk()
root.geometry("+100+100")

interface = Modify(parent=root, boss=None)
root.mainloop()
"""