from tkinter import *
from tkinter import ttk
from AnimalTA.E_Post_tracking.b_Analyses.Elements_management import Function_extend_elements, Class_list_arenas
from AnimalTA.A_General_tools import Function_draw_arenas, UserMessages, Class_loading_Frame, Color_settings
import cv2
import numpy as np
import PIL
import copy
import os

class Lists(Frame):
    """ This Frame displays a list of the videos and their arenas from the project that have been tracked.
    The user can select some arenas to copy-paste there the elements of interest from the current arena"""
    def __init__(self, parent, boss, liste_videos, Current_Vid, Current_Area, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.boss=boss
        self.grid()
        self.Current_Vid=Current_Vid
        self.Current_Area=Current_Area
        self.liste_videos=liste_videos

        #Import messages
        self.Messages = UserMessages.get_dict()

        Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW

        self.winfo_toplevel().title(self.Messages["Extend_Ana0"])


        #User help
        User_help=Label(self,text=self.Messages["Extend_Ana1"], wraplength=800, justify=LEFT, **Color_settings.My_colors.Label_Base)
        User_help.grid(row=0, column=0, columnspan=5)

        #Listbox of shapes in current arena with button to select/unselect all
        self.Button_sel_al=Button(self,text=self.Messages["ExtendB1"], command=self.select_all_objs, **Color_settings.My_colors.Button_Base)
        self.Button_sel_al.grid(row=1, column=0, columnspan=2)
        self.all_sel_objs = False
        self.yscrollbar = ttk.Scrollbar(self)
        self.Liste_objects=Listbox(self, selectmode = "multiple", width=50, height=20, exportselection=0, yscrollcommand=self.yscrollbar.set, **Color_settings.My_colors.ListBox)
        self.yscrollbar.config(command=self.Liste_objects.yview)
        ID = 0

        for Shape in self.boss.main.Vid.Analyses[1][Current_Area]:
            self.Liste_objects.insert(END, Shape[3])
            ID += 1

        self.Liste_objects.grid(row=2, column=0, sticky="nsew")
        self.yscrollbar.grid(row=2,column=1, sticky="ns")
        self.Liste_objects.bind('<<ListboxSelect>>', self.check_button)

        Arrow=Label(self, text=u'\u279F', font=('Helvatical bold',20), **Color_settings.My_colors.Label_Base)
        Arrow.grid(row=2,column=2)

        # Listbox of other arenas
        self.List_arenas=Class_list_arenas.List_arenas(self, boss, liste_videos, Current_Vid, Current_Area)
        self.List_arenas.grid(row=2, column=3, sticky="nsew")


        self.Validate_button=Button(self, text=self.Messages["Validate"], command=self.validate, **Color_settings.My_colors.Button_Base)
        self.Validate_button.grid(row=3, column=0,columnspan=6, sticky="nsew")
        self.Validate_button.config(state="disable")

        self.parent.update()



        self.stay_on_top()
        self.boss.ready=False
        self.parent.protocol("WM_DELETE_WINDOW", self.close)

        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=1)  ########NEW
        Grid.rowconfigure(self, 2, weight=1)  ########NEW
        Grid.rowconfigure(self, 3, weight=1)  ########NEW
        Grid.columnconfigure(self, 0, weight=100)  ########NEW
        Grid.columnconfigure(self, 1, weight=1)  ########NEW
        Grid.columnconfigure(self, 2, weight=100)  ########NEW
        Grid.columnconfigure(self, 3, weight=1)  ########NEW





    def select_all_objs(self):
        #Select all the elements of interest inside the current arena
        if not self.all_sel_objs:
            self.Liste_objects.select_set(0, END)
            self.Button_sel_al.config(text=self.Messages["ExtendB2"])
            self.all_sel_objs=True
        else:
            self.Liste_objects.selection_clear(0, END)
            self.Button_sel_al.config(text=self.Messages["ExtendB1"])
            self.all_sel_objs=False
        self.check_button()#On actualise le bouton de validation

    def close(self):
        #Close this window properly
        self.parent.destroy()
        self.boss.ready=True

    def validate(self):
        Load_show=Class_loading_Frame.Loading(self)
        Load_show.grid(row=6,column=0,columnspan=6)

        #Extend the elements to other arenas
        list_of_shapes=[self.boss.main.Vid.Analyses[1][self.Current_Area][i] for i in self.Liste_objects.curselection()]

        Or_Arenas = Function_draw_arenas.get_arenas(self.Current_Vid)

        Np_style_pts=np.array([self.List_arenas.pointers[i] for i in self.List_arenas.Liste_Vids.curselection()])
        list_of_vids =[]
        for Vid in Np_style_pts[:,0]:#Look for all videos with at least one selected arena
            if Vid not in list_of_vids:
                list_of_vids.append(Vid)

        nb_V=0

        for Vid in list_of_vids:#For each of these videos, we look for the arenas
            Load_show.show_load(nb_V/len(list_of_vids))#Show the progress
            nb_V += 1

            Arenas = Function_draw_arenas.get_arenas(Vid)

            for Area in range(len(Arenas)):
                if Area in [self.List_arenas.pointers[i][1] for i in self.List_arenas.Liste_Vids.curselection() if self.List_arenas.pointers[i][0]==Vid]:#If the arena was selected
                    list_of_points = []
                    if not (Area==self.Current_Area and Vid == self.Current_Vid):#We ensure it is not the current arena
                        for shape in list_of_shapes:
                            #we first check if an element of interest with similar name has already been defined:
                            if shape[0] != "Borders" and shape[0] != "All_borders":
                                list_of_points = list_of_points + shape[1]
                            elif shape[0] == "Borders":
                                for bd in shape[1]:
                                    list_of_points = list_of_points + bd
                            elif shape[0] == "All_borders":
                                Shape2=shape[2]

                                if Vid == self.Current_Vid:
                                    if shape[3] not in [Ars[3] for Ars in self.boss.main.Vid.Analyses[1][Area]]:#If this shape does not exist yet
                                        self.boss.main.Vid.Analyses[1][Area].append(["All_borders", [], Shape2, shape[3]])
                                    else:
                                        position=[Ars[3] for Ars in self.boss.main.Vid.Analyses[1][Area]].index(shape[3])#If this shape already exists inside the arena, we remplace it
                                        self.boss.main.Vid.Analyses[1][position]=["All_borders", [], Shape2, shape[3]]
                                else:
                                    if shape[3] not in [Ars[3] for Ars in Vid.Analyses[1][Area]]:#If this shape does not exist yet
                                        Vid.Analyses[1][Area].append(["All_borders", [], Shape2, shape[3]])
                                    else:
                                        position=[Ars[3] for Ars in Vid.Analyses[1][Area]].index(shape[3])#If this shape already exists inside the arena, we remplace it
                                        Vid.Analyses[1][Area][position]=["All_borders", [], Shape2, shape[3]]

                        if len(list_of_points) > 0:
                            work, new_pts = Function_extend_elements.match_shapes(Arenas[Area], Or_Arenas[self.Current_Area], list_of_points)
                            if work:
                                for shape in list_of_shapes:
                                    if shape[0]!="Borders" and shape[0]!="All_borders":
                                        Shape2=shape[2]

                                        if Vid == self.Current_Vid:
                                            if shape[3] not in [Ars[3] for Ars in self.boss.main.Vid.Analyses[1][Area]]:  # if this element did not exist
                                                self.boss.main.Vid.Analyses[1][Area].append([shape[0], new_pts[0:len(shape[1])], Shape2, shape[3]])
                                            else:
                                                position = [Ars[3] for Ars in self.boss.main.Vid.Analyses[1][Area]].index(shape[3])  # if an element with similar name was already present in the arena, we replace it and throw a warning.
                                                self.boss.main.Vid.Analyses[1][Area][position] = [shape[0], new_pts[0:len(shape[1])],Shape2, shape[3]]

                                        else:
                                            if shape[3] not in [Ars[3] for Ars in Vid.Analyses[1][Area]]:  # if this element did not exist
                                                Vid.Analyses[1][Area].append([shape[0], new_pts[0:len(shape[1])],Shape2, shape[3]])
                                            else:
                                                position = [Ars[3] for Ars in Vid.Analyses[1][Area]].index(shape[3])  # if an element with similar name was already present in the arena, we replace it and throw a warning.
                                                Vid.Analyses[1][Area][position] = [shape[0], new_pts[0:len(shape[1])],Shape2, shape[3]]

                                        del new_pts[0:len(shape[1])]

                                    elif shape[0] == "Borders":
                                        new_shape2 = []
                                        for bd in shape[1]:
                                            new_shape2.append(new_pts[0:len(bd)])
                                            del new_pts[0:len(bd)]
                                            Shape2=shape[2]

                                        if Vid == self.Current_Vid:
                                            if shape[3] not in [Ars[3] for Ars in self.boss.main.Vid.Analyses[1][Area]]:
                                                self.boss.main.Vid.Analyses[1][Area].append([shape[0], new_shape2, Shape2, shape[3]])
                                            else:
                                                position = [Ars[3] for Ars in self.boss.main.Vid.Analyses[1][Area]].index(shape[3])
                                                self.boss.main.Vid.Analyses[1][Area][position] = [shape[0], new_shape2, Shape2, shape[3]]

                                        else:
                                            if shape[3] not in [Ars[3] for Ars in Vid.Analyses[1][Area]]:
                                                Vid.Analyses[1][Area].append([shape[0], new_shape2, Shape2, shape[3]])
                                            else:
                                                position = [Ars[3] for Ars in Vid.Analyses[1][Area]].index(shape[3])
                                                Vid.Analyses[1][Area][position] = [shape[0], new_shape2, Shape2, shape[3]]

        self.Current_Vid.Analyses[1] = copy.deepcopy(self.boss.main.Vid.Analyses[1])

        self.parent.destroy()
        self.boss.ready=True

        #If some elements were replaced in the selected arenas.
        #if Show_warn:
            #messagebox.showinfo(message=self.Messages["GError1"], title=self.Messages["GErrorT1"])

    def check_button(self, *arg):
        #The user can validate only if at least one element and one arena were selected
        if len(self.List_arenas.Liste_Vids.curselection())>0 and len(self.Liste_objects.curselection())>0:
            self.Validate_button.config(state="normal", background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        else:
            self.Validate_button.config(state="disable", **Color_settings.My_colors.Button_Base)


    def stay_on_top(self):
        #Maintain this window on top
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)
