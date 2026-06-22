from tkinter import *
from tkinter import ttk
from AnimalTA.E_Post_tracking.b_Analyses import Interface_sequences
from AnimalTA.A_General_tools import Function_draw_arenas, UserMessages, Class_loading_Frame, Color_settings
import cv2
import numpy as np
import PIL
import copy


class Lists(Frame):
    """ This Frame displays a list of the videos and their arenas from the project that have been tracked.
    The user can select some arenas to copy-paste there the elements of interest from the current arena"""
    def __init__(self, parent, boss, Current_Vid, Current_Area, Current_Ind, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.boss=boss
        self.grid(sticky="nsew")
        self.Current_Vid=Current_Vid
        self.Current_Ind=Current_Ind
        self.Area=Current_Area

        self.one_every = self.Current_Vid.Frame_rate[0] / self.Current_Vid.Frame_rate[1]
        
        #Import messages
        self.Messages = UserMessages.get_dict()

        Grid.columnconfigure(self.parent, 0, weight=1)
        Grid.rowconfigure(self.parent, 0, weight=1)

        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=100)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=10)
        Grid.rowconfigure(self, 2, weight=1)

        self.winfo_toplevel().title(self.Messages["Auto_range1"])


        #User help
        User_help=Label(self,text=self.Messages["Auto_range2"], wraplength=800, justify=LEFT, **Color_settings.My_colors.Label_Base)
        User_help.grid(row=0, column=0, columnspan=5)


        self.Seq_type = StringVar(self)
        self.Seq_type.set(self.Messages["Sequences_Time"])  # default value

        all_values_shapes = []
        for shape in range(len(self.Current_Vid.Analyses[1][self.Area])):
            if self.Current_Vid.Analyses[1][self.Area][shape][0] != "Line":
                all_values_shapes.append(self.Current_Vid.Analyses[1][self.Area][shape][3])


        if len(all_values_shapes)>0:
            all_types=[self.Messages["Sequences_Time"], self.Messages["Sequences_Explo"],self.Messages["Sequences_Spatial_event"]]
        else:
            all_types = [self.Messages["Sequences_Time"], self.Messages["Sequences_Explo"]]

        dropdown_Menu = OptionMenu(self, self.Seq_type, *all_types ,command=self.change_type)
        dropdown_Menu["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
        dropdown_Menu.config(**Color_settings.My_colors.Button_Base)
        dropdown_Menu.grid(row=1, column=0, columnspan=1, rowspan=2)

        check_num = (self.register(self.show_range))

        self.begin=StringVar()
        self.begin.set("0")
        self.end=StringVar()
        self.end.set("600")
        self.each=StringVar()
        self.each.set("300")

        self.Frame_range=Frame(self, **Color_settings.My_colors.Frame_Base)
        self.Frame_range.config(highlightbackground=Color_settings.My_colors.list_colors["Title1"], highlightthickness=3)
        self.Frame_range.grid(row=1, column=1, columnspan=3, sticky="nsew")

        Label_from=Label(self.Frame_range,text="From:",**Color_settings.My_colors.Label_Base)
        Label_from.grid(row=1, column=1, columnspan=1, sticky="sw")
        Entry_beg=Entry(self.Frame_range,textvariable=self.begin, validate='all', validatecommand=(check_num, '%P'), **Color_settings.My_colors.Entry_Base)
        Entry_beg.grid(row=2, column=1, columnspan=1)

        Label_to=Label(self.Frame_range,text="To:",**Color_settings.My_colors.Label_Base)
        Label_to.grid(row=1, column=2, columnspan=1, sticky="sw")
        Entry_end=Entry(self.Frame_range,textvariable=self.end, validate='all', validatecommand=(check_num, '%P'), **Color_settings.My_colors.Entry_Base)
        Entry_end.grid(row=2, column=2, columnspan=1)

        Label_step=Label(self.Frame_range,text="Steps:",**Color_settings.My_colors.Label_Base)
        Label_step.grid(row=1, column=3, columnspan=1, sticky="sw")
        Entry_each=Entry(self.Frame_range,textvariable=self.each, validate='all', validatecommand=(check_num, '%P'), **Color_settings.My_colors.Entry_Base)
        Entry_each.grid(row=2, column=3, columnspan=1)


        self.Frame_elems=Frame(self, **Color_settings.My_colors.Frame_Base)

        Grid.columnconfigure(self.Frame_elems, 0, weight=10)  ########NEW
        Grid.columnconfigure(self.Frame_elems, 1, weight=5)  ########NEW
        Grid.columnconfigure(self.Frame_elems, 2, weight=5)  ########NEW

        self.Frame_elems.config(highlightbackground=Color_settings.My_colors.list_colors["Title1"], highlightthickness=3)
        self.Entries=DoubleVar()
        check_entries=Checkbutton(self.Frame_elems,text="Entrance to Exit", variable=self.Entries,**Color_settings.My_colors.Checkbutton_Base)
        check_entries.grid(row=0,column=2, sticky="nsew")

        self.Exits=DoubleVar()
        check_exits=Checkbutton(self.Frame_elems,text="Exit to Entrance", variable=self.Exits,**Color_settings.My_colors.Checkbutton_Base)
        check_exits.grid(row=0, column=3, sticky="nsew")


        if len(all_values_shapes)>0:
            self.Shape_name = StringVar()
            self.Shape_name.set(all_values_shapes[0])
            dropdown_elements = OptionMenu(self.Frame_elems, self.Shape_name, *all_values_shapes)
            dropdown_elements["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
            dropdown_elements.config(**Color_settings.My_colors.Button_Base)
            dropdown_elements.grid(row=0, column=1, columnspan=1, rowspan=2, sticky="nsew")

        self.Validate_button=Button(self, text=self.Messages["Validate"], command=self.validate, **Color_settings.My_colors.Button_Base)
        self.Validate_button.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.Validate_button.grid(row=3, columnspan=5, sticky="nsew")

        self.stay_on_top()
        self.boss.ready=False
        self.parent.protocol("WM_DELETE_WINDOW", self.close)


    def change_type(self, event):
        if self.Seq_type.get()==self.Messages["Sequences_Time"]:
            self.begin.set("0")
            self.end.set("600")
            self.each.set("300")
            self.Frame_range.grid(row=1, column=1, columnspan=3, sticky="nsew")
            self.Frame_elems.grid_forget()
        elif self.Seq_type.get()==self.Messages["Sequences_Explo"]:
            self.begin.set("0")
            self.end.set("100")
            self.each.set("10")
            self.Frame_range.grid(row=1, column=1, columnspan=3, sticky="nsew")
            self.Frame_elems.grid_forget()
        elif self.Seq_type.get()==self.Messages["Sequences_Spatial_event"]:
            self.Frame_elems.grid(row=1, column=1, columnspan=3, sticky="nsew")
            self.Frame_range.grid_forget()

    def show_range(self, val):
        end = float(self.end.get())

    def close(self):
        #Close this window properly
        self.parent.destroy()
        self.boss.ready=True

    def validate(self):
        if self.Seq_type.get()!=self.Messages["Sequences_Spatial_event"]:
            #Extend the elements to other arenas
            if self.Seq_type.get()==self.Messages["Sequences_Time"]:
                name_seq_type="Time"
            elif self.Seq_type.get()==self.Messages["Sequences_Explo"]:
                name_seq_type = "Exploration"

            new_seq = ["Auto_" +name_seq_type+ "_" +str(round(float(self.begin.get()),2)) + "_to_" + str(round(float(self.end.get()),2)) + "_each_"+str(round(float(self.each.get()),2)), ["Auto", str(self.begin.get()), self.Seq_type.get(), "End", str(self.begin.get()),str(self.each.get())],
                       ["", str(self.end.get()), "", "", "", "-1"]]
            self.Current_Vid.Sequences[self.Current_Ind].append(new_seq)

        else:
            if self.Entries.get() or self.Exits.get():
                for Shape in self.Current_Vid.Analyses[1][self.Area]:
                    if self.Shape_name.get()==Shape[3]:
                        if self.Entries.get():
                            new_seq = ["Auto_"+Shape[3]+"_In", ["Auto", "", "Element of interest", Shape[3], "Entries", ""],
                                       ["", "", "", "", "", "-1"]]
                            self.Current_Vid.Sequences[self.Current_Ind].append(new_seq)
                        if self.Exits.get():
                            new_seq = ["Auto_"+Shape[3]+"_Out", ["Auto", "", "Element of interest", Shape[3], "Exits", ""],
                                       ["", "", "", "", "", "-1"]]
                            self.Current_Vid.Sequences[self.Current_Ind].append(new_seq)
                        break

        self.parent.destroy()
        self.boss.ready=True
        self.boss.update_sequences()

        #If some elements were replaced in the selected arenas.
        #if Show_warn:
            #messagebox.showinfo(message=self.Messages["GError1"], title=self.Messages["GErrorT1"])


    def stay_on_top(self):
        #Maintain this window on top
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)
