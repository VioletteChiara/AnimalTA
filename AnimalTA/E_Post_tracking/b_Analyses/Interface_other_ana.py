from tkinter import *

from AnimalTA.A_General_tools import UserMessages, Color_settings, Interface_extend, Small_info, Diverse_functions
from tkinter import ttk


"""This script allow to add some more precise and punctually used kind of analysis."""

class Details_other(Frame):
    #This Frame display a graph and associated results.
    #It allows the user to change the movement thershold of the targets (under this threshold, targets are considered stopped).
    def __init__(self, parent, main, Vid, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.parent.geometry("1050x620")
        self.main=main
        self.grid(sticky="nsew")
        self.ready=False
        self.parent.attributes('-toolwindow', True)
        self.Vid=Vid

        Grid.columnconfigure(self.parent, 0, weight=1)
        Grid.rowconfigure(self.parent, 0, weight=1)

        #Import messages
        self.Messages = UserMessages.get_dict()
        self.winfo_toplevel().title(self.Messages["Other_Ana1"])

        self.stay_on_top()

        self.morpho=BooleanVar()
        try:
            self.morpho.set(self.Vid.Morphometrics)
        except:
            self.morpho.set(False)


        self.crosses=BooleanVar()
        try:
            self.crosses.set(self.Vid.More_ana_Crosses)
        except:
            self.crosses.set(False)

        self.explored=BooleanVar()
        try:
            self.explored.set(self.Vid.Explored_complex)
        except:
            self.explored.set(False)


        row=0
        #CTXT, for version v4, we will not use the Morphometric part
        self.Morphometrics=Checkbutton(self, text="Add morphometric measurements", var=self.morpho, **Color_settings.My_colors.Checkbutton_Base)
        #self.Morphometrics.grid(row=row, column=0, sticky="new")
        Small_info.small_info(elem=self.Morphometrics, parent=self,
                              message="Use the target's .")
        Morphometrics_apply=Button(self, text=self.Messages["Analyses_B1"],command= self.apply_morpho, **Color_settings.My_colors.Button_Base)
        #Morphometrics_apply.grid(row=row, column=1, sticky="new")
        #row += 1

        #ttk.Separator(self, orient=HORIZONTAL).grid(row=row, columnspan=2, sticky="new")
        row += 1

        self.segment_corsses=Checkbutton(self, text=self.Messages["Other_Ana2"], var=self.crosses, **Color_settings.My_colors.Checkbutton_Base)
        self.segment_corsses.grid(row=row, column=0, sticky="new")
        Small_info.small_info(elem=self.segment_corsses, parent=self,
                              message=self.Messages["Other_Ana2_expl"])
        Segment_apply=Button(self, text=self.Messages["Analyses_B1"],command= self.apply_segments, **Color_settings.My_colors.Button_Base)
        Segment_apply.grid(row=row, column=1, sticky="new")
        row+=1

        ttk.Separator(self, orient=HORIZONTAL).grid(row=row, columnspan=2, sticky="ew")
        row += 1

        #CTXT
        self.segment_corsses=Checkbutton(self, text="Data related to quality of explored area around the target", var=self.explored, **Color_settings.My_colors.Checkbutton_Base)
        #self.segment_corsses.grid(row=row, column=0, sticky="new")
        Small_info.small_info(elem=self.segment_corsses, parent=self,
                              message="Count number...")
        Segment_apply=Button(self, text=self.Messages["Analyses_B1"],command= self.apply_explored, **Color_settings.My_colors.Button_Base)
        #Segment_apply.grid(row=row, column=1, sticky="new")
        #row+=1

        #ttk.Separator(self, orient=HORIZONTAL).grid(row=row, columnspan=2, sticky="ew")
        row += 1

        #Stops and moves durations
        Label(self,text=self.Messages["Other_Ana6"], bg=Color_settings.My_colors.list_colors["Title1"], fg=Color_settings.My_colors.list_colors["Fg_Title1"]).grid(sticky="nsew",row=row, column=0, columnspan=2)
        row += 1
        durations_sm=Frame(self, **Color_settings.My_colors.Frame_Base)
        durations_sm.grid(row=row, column=0)

        self.list_stops_moves_options=Diverse_functions.list_stops_moves_options

        for elem in self.list_stops_moves_options:
            if elem not in self.Vid.Stops_Moves_options[0]:
                self.Vid.Stops_Moves_options[0][elem] = False

        self.list_stops_moves_options={elem:BooleanVar(value=self.Vid.Stops_Moves_options[0][elem]) for elem in self.list_stops_moves_options}

        self.sm_hole_dur=self.Vid.Stops_Moves_options[1]

        nb_row=len(self.list_stops_moves_options)//3
        sub_row=0
        col=0
        for elem in self.list_stops_moves_options:
            Checkbutton(durations_sm, text=elem, var=self.list_stops_moves_options[elem],**Color_settings.My_colors.Checkbutton_Base).grid(row=sub_row, column=col, sticky="nsw")
            sub_row+=1
            if sub_row>nb_row:
                sub_row=0
                col+=1


        Label(durations_sm, **Color_settings.My_colors.Label_Base, text=self.Messages["Other_Ana4"]).grid(row=0,column=col+1, rowspan=2, sticky="nse")
        regLab = (self.register(self.change_sm_hole_dur), '%P', '%V')

        entry=Entry(durations_sm, text=str(self.sm_hole_dur), **Color_settings.My_colors.Entry_Base, validate="all", validatecommand=regLab)
        entry.grid(row=0,column=col+2, rowspan=2)
        entry.insert(0, str(self.sm_hole_dur))
        Label(durations_sm, **Color_settings.My_colors.Label_Base, text=self.Messages["Crop9"]).grid( row=0, column=col + 3, rowspan=2)

        Details_apply=Button(self, text=self.Messages["Analyses_B1"],command= self.apply_sm, **Color_settings.My_colors.Button_Base)
        Details_apply.grid(row=row, column=1, sticky="new")
        row +=1

        ttk.Separator(self, orient=HORIZONTAL).grid(row=row, columnspan=2, sticky="ew")
        row += 1


        #Change details_data options
        Label(self,text=self.Messages["Other_Ana5"], bg=Color_settings.My_colors.list_colors["Title1"], fg=Color_settings.My_colors.list_colors["Fg_Title1"]).grid(sticky="nsew",row=row, column=0, columnspan=2)
        row += 1

        frame_all_details=Frame(self, **Color_settings.My_colors.Frame_Base)
        frame_all_details.grid(row=row, column=0)

        self.list_details_options=Diverse_functions.list_details_options

        for elem in self.list_details_options:
            if elem not in self.Vid.Details_options:
                self.Vid.Details_options[elem] = False

        self.details_data_options={elem:BooleanVar(value=self.Vid.Details_options[elem]) for elem in self.list_details_options}

        nb_row=len(self.details_data_options)//3
        sub_row=0
        col=0
        for elem in self.list_details_options:
            c=Checkbutton(frame_all_details, text=elem, var=self.details_data_options[elem],**Color_settings.My_colors.Checkbutton_Base)
            c.grid(row=sub_row, column=col, sticky="nsw")
            Small_info.small_info(elem=c,parent=self,message=self.Messages[elem+"_Details_exple"])
            sub_row+=1
            if sub_row>nb_row:
                sub_row=0
                col+=1

        Details_apply=Button(self, text=self.Messages["Analyses_B1"],command= self.apply_details, **Color_settings.My_colors.Button_Base)
        Details_apply.grid(row=row, column=1, sticky="new")
        row +=1

        ttk.Separator(self, orient=HORIZONTAL).grid(row=row, columnspan=2, sticky="new")
        row += 1

        #Group level data:
        Label(self,text=self.Messages["Other_Ana7"], bg=Color_settings.My_colors.list_colors["Title1"], fg=Color_settings.My_colors.list_colors["Fg_Title1"]).grid(sticky="nsew",row=row, column=0, columnspan=2)
        row += 1
        group_data=Frame(self, **Color_settings.My_colors.Frame_Base)
        group_data.grid(row=row, column=0)

        self.list_group_options=Diverse_functions.list_group_options

        for elem in self.list_group_options:
            if elem not in self.Vid.Group_data:
                self.Vid.Group_data[elem] = False

        self.list_group_options={elem:BooleanVar(value=self.Vid.Group_data[elem]) for elem in self.list_group_options}

        nb_row=len(self.list_group_options)//3
        sub_row=0
        col=0
        for elem in self.list_group_options:
            Checkbutton(group_data, text=elem, var=self.list_group_options[elem],**Color_settings.My_colors.Checkbutton_Base).grid(row=sub_row, column=col, sticky="nsw")
            sub_row+=1
            if sub_row>nb_row:
                sub_row=0
                col+=1

        Details_apply=Button(self, text=self.Messages["Analyses_B1"],command= self.apply_gr, **Color_settings.My_colors.Button_Base)
        Details_apply.grid(row=row, column=1, sticky="new")
        row +=1

        ttk.Separator(self, orient=HORIZONTAL).grid(row=row, columnspan=2, sticky="ew")
        row += 1



        Grid.columnconfigure(self, 0, weight=1)
        for r in range(row+1):
            Grid.rowconfigure(self, r, weight=1)


        Grid.rowconfigure(self, row, weight=1000)
        row += 1

        #Close the Frame/window
        self.Quit_button=Button(self, text=self.Messages["Validate"], command=self.save, **Color_settings.My_colors.Button_Base)
        self.Quit_button.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.Quit_button.grid(row=row, column=0, columnspan=2, sticky="sew")

        Grid.rowconfigure(self, row, weight=1)



    def change_sm_hole_dur(self, new_val, method="key"):
        # If the user is writting directly the position wanted, we check that they are valid entries (only floats < border length)
        if (new_val == "" or new_val == "-") and method != "focusout":
            return True
        elif new_val != "":
            if method == "key":
                try:
                    self.sm_hole_dur = float(new_val)
                except:
                    return False

            return True
        else:
            return False

    def apply_explored(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.explored.get(),
                                            boss=self.main,
                                            Video_file=self.Vid, type="analyses_explored")

    def apply_segments(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.crosses.get(),
                                            boss=self.main,
                                            Video_file=self.Vid, type="analyses_segments")

    def apply_sm(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=[{elem:self.list_stops_moves_options[elem].get() for elem in self.list_stops_moves_options},self.sm_hole_dur],
                                            boss=self.main,
                                            Video_file=self.Vid, type="analyses_sm")
    def apply_gr(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value={elem:self.list_group_options[elem].get() for elem in self.list_group_options},
                                            boss=self.main,
                                            Video_file=self.Vid, type="analyses_gr")

    def apply_details(self):
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value={elem:self.details_data_options[elem].get() for elem in self.details_data_options},
                                            boss=self.main,
                                            Video_file=self.Vid, type="analyses_details")
    def apply_morpho(self):
        """Extend the deformation parameters to other videos"""
        newWindow = Toplevel(self.parent.master)
        interface = Interface_extend.Extend(parent=newWindow, value=self.morpho.get(),
                                            boss=self.main,
                                            Video_file=self.Vid, type="analyses_morpho")


    def save(self):
        self.Vid.Morphometrics=self.morpho.get()
        self.Vid.More_ana_Crosses=self.crosses.get()
        self.Vid.Details_options = {elem:self.details_data_options[elem].get() for elem in self.details_data_options}
        self.Vid.Stops_Moves_options=[{elem:self.list_stops_moves_options[elem].get() for elem in self.list_stops_moves_options}, self.sm_hole_dur]
        self.Vid.Group_data = {elem:self.list_group_options[elem].get() for elem in self.list_group_options}
        self.Vid.Explored_complex=self.explored.get()
        self.parent.destroy()

    def stay_on_top(self):
        # We want this window to remain on the top of the others
        if self.ready:
            self.parent.lift()
            self.add_cur_loc()
        self.parent.after(50, self.stay_on_top)
