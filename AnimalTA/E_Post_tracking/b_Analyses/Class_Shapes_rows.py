from tkinter import *
import numpy as np
import cv2
from AnimalTA.A_General_tools import Function_draw_mask, UserMessages


#This file contains classes herited from Frame. They are Frames widgets which will show the characteristics of an element of interest (in the Analyses part) and allow to modify or delete it.

class Row_Point(Frame):
    '''
    The widget for a point as an element of interest.
    parent=the container of this frame
    main=the panel in which the container is displayed. the main object is also related to the current video
            > "self.main.Calc_speed.Areas" is a list of all the elements of interest
    MArea=the identification number of the current element of interest
    Shape=the characterstics of the point (Shape[0]=the kind of element (in that case, always a Point),Shape[1]=[Xcoord, Ycoord], Shape[2]=the radius of the circle around the point, Shape[3] the name of the element)
    label=the name of the element (either PointX or any other name filled by the user
    Ind=Which target is selected (the one used to display the metrics relative to that element of interest)
    '''
    def __init__(self, parent, main, boss, MArea, Shape, label, Ind, **kw):
        Frame.__init__(self, parent, **kw)
        self.MArea=MArea
        self.boss=boss
        self.main=main
        self.Shape=Shape
        self.Ind=Ind

        self.Mean_dist=StringVar()#Averaged distance between the selected Ind and the Point of interest
        self.Latency=StringVar()#Latency before the target approach at less than Shape[2] units from the point of interest
        self.Prop_Time=StringVar()#Proportion of time the target spent at less than Shape[2] units from the point of interest
        self.update_infos()#(Re)calculate the three values above

        # Import the language settings
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        #Display the name of the element of interest as an Entry (so it can be modified) along with a button to supress it.
        regLab = (self.register(self.change_area_name), '%P', '%V')
        Lab=Entry(self, validate="all", validatecommand=regLab)
        Lab.insert(0, label)
        Lab.config()
        Lab.grid(row=0, column=0, sticky="w")
        supr_button=Button(self, text=self.Messages["Analyses_details_sp8"], command=self.supress)
        supr_button.grid(row=0, column=1, sticky="w")

        #Display the averaged distance to the point
        Title_mean_dist=Label(self, text=self.Messages["Analyses_details_sp_Lab1"])
        Title_mean_dist.grid(row=1, column=1, sticky="w")
        Frame_show=Frame(self)
        Frame_show.grid(row=2, column=1)
        Lab_arr=Label(Frame_show, text=">")
        Lab_arr.grid(row=0, column=0, sticky="w")
        self.Lab_mean_dist=Label(Frame_show, textvariable=self.Mean_dist)
        self.Lab_mean_dist.grid(row=0, column=1, sticky="w")
        Label_unit1=Label(Frame_show, text=self.main.Vid.Scale[1])
        Label_unit1.grid(row=0, column=2, sticky="w")

        #Display the latency before the target approach at less than Shape[2] units from the point of interest
        Title_Latency=Label(self, text=self.Messages["Analyses_details_sp_Lab2"])
        Title_Latency.grid(row=4, column=1, sticky="w")
        Inter_Check_entry = (self.register(self.Check_entry), '%P', '%V')
        self.Scale_Radius=Entry(self, textvariable=self.Shape[2], validate="all", validatecommand=Inter_Check_entry)#The user can change here the value of Shape[2]
        self.Scale_Radius.grid(row=4, column=2, sticky="w")
        self.Shape[2].trace('w', self.inter_draw)
        Label_unit2=Label(self, text=self.main.Vid.Scale[1])
        Label_unit2.grid(row=4, column=3, sticky="w")
        Frame_show2=Frame(self)
        Frame_show2.grid(row=5, column=1)
        Lab_arr2=Label(Frame_show2, text=">")
        Lab_arr2.grid(row=0, column=0, sticky="w")
        self.Lab_Latency=Label(Frame_show2, textvariable=self.Latency)
        self.Lab_Latency.grid(row=0, column=1, sticky="w")
        Label_unit3=Label(Frame_show2, text="sec")
        Label_unit3.grid(row=0, column=2, sticky="w")

        #Display the proportion of time the target spent at less than Shape[2] units from the point of interest
        Title_Prop_Time=Label(self, text=self.Messages["Analyses_details_sp_Lab3"])
        Title_Prop_Time.grid(row=6, column=1, sticky="w")
        Title_Prop_Time_Val = Label(self, textvariable=self.Shape[2])
        Title_Prop_Time_Val.grid(row=6, column=2, sticky="w")
        Label_unit4=Label(self, text=self.main.Vid.Scale[1])
        Label_unit4.grid(row=6, column=3, sticky="w")
        Frame_show3=Frame(self)
        Frame_show3.grid(row=7, column=1)
        Lab_arr3=Label(Frame_show3, text=">")
        Lab_arr3.grid(row=0, column=0, sticky="w")
        self.Lab_Prop_Time=Label(Frame_show3, textvariable=self.Prop_Time)
        self.Lab_Prop_Time.grid(row=0, column=1, sticky="w")


    def update_infos(self):
        '''This function calculates the three measures of interest to be displayed:
        self.Mean_dist: Averaged distance between the selected Ind and the Point of interest
        self.Latency: Latency before the target approach at less than Shape[2] units from the point of interest
        self.Prop_Time: Proportion of time the target spent at less than Shape[2] units from the point of interest

        Each time, the value is rounded.
        If the value cannot be calculated, the self.main.Calc_speed.calculate_dist_lat returns "NA".
        '''
        new_vals=self.main.Calc_speed.calculate_dist_lat(parent=self.main, Point=self.Shape[1][0], ind=self.Ind, Dist=self.Shape[2].get())
        if new_vals[0]!="NA":
            self.Mean_dist.set(round(new_vals[0],3))
        else:
            self.Mean_dist.set("NA")

        if new_vals[1]!="NA":
            self.Latency.set(str(round(new_vals[1], 3)))
        else:
            self.Latency.set("NA")

        if new_vals[2] != "NA":
            self.Prop_Time.set(str(round(new_vals[2], 3)))
        else:
            self.Prop_Time.set("NA")


    def change_area_name(self, new_val, method):
        '''
        This function is called when the user want to change the name of the element. It allows to avoid that the same name is assigned twice
        '''
        auto_modif=False
        if new_val in [shape[3] for shape in self.main.Calc_speed.Areas[self.MArea] if shape!=self.Shape]:
            new_val=new_val+"_1"
            auto_modif=True
        self.Shape[3]=new_val
        if method=="focusout" and auto_modif:
            self.boss.show_results()
        return(True)


    def supress(self):
        '''
        Supress this widget and supress the corresponding element of interest from the list of elements (self.main.Calc_speed.Areas)
        '''
        for shape in range(len(self.main.Calc_speed.Areas[self.MArea])):
            if self.main.Calc_speed.Areas[self.MArea][shape] == self.Shape:
                self.main.Calc_speed.Areas[self.MArea].pop(shape)
                self.boss.show_results()
                self.boss.show_img()
                self.update_infos()
                self.boss.add_pt = [None]
                self.boss.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="active")
                break
        self.destroy()


    def inter_draw(self, *args):
        '''
        This function is called when the value of Shape[2] is modified.
        It updates the displayed frame (in that case, the area of the circle around the point of interest is modified)
        '''
        try:
            float(self.Shape[2].get())
            if float(self.Shape[2].get())!=0 :
                self.boss.show_img()
                self.update_infos()
        except:
            pass

    def Check_entry(self, new_val, method):
        '''
        Avoid the user to add non-numeric or negative inputs for Shape[2]
        '''
        if new_val=="" and method!="focusout":
            return True
        elif new_val!="":
            if method == "key":
                try:
                    if float(new_val) >= 0:
                        return True
                    else:
                        return False
                except Exception as e:
                    print(e)
                    return False
            return True
        else:
            return False

class Row_Line(Frame):
    '''
    The widget for a line as an element of interest.
    parent=the container of this frame
    main=the panel in which the container is displayed. the main object is also related to the current video
            > "self.main.Calc_speed.Areas" is a list of all the elements of interest
    MArea=the identification number of the current element of interest
    Shape=the characterstics of the line (Shape[0]=the kind of element (in that case, always a Line),Shape[1]=[pt1, pt2], Shape[2]=None, Shape[3]=the name of the element)
    label=the name of the element (either LineX or any other name filled by the user)
    Ind=Which target is selected (the one used to display the metrics relative to that element of interest)
    '''
    def __init__(self, parent, main, boss, MArea, Shape, label, Ind, **kw):
        Frame.__init__(self, parent, **kw)
        self.MArea=MArea
        self.boss=boss
        self.main=main
        self.Shape=Shape
        self.Ind=Ind

        self.Mean_dist=StringVar()#Average distance to the segment
        self.Nb_cross=StringVar()#Number of time the target crossed the segment
        self.Lat_cross=StringVar()#Latency before the first time the target crossed the segment
        self.update_infos()

        # Import the language settings
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        # Display the name of the element of interest as an Entry (so it can be modified) along with a button to supress it.
        regLab = (self.register(self.change_area_name), '%P', '%V')
        Lab=Entry(self, validate="all", validatecommand=regLab)
        Lab.insert(0, label)
        Lab.config()
        Lab.grid(row=0, column=0, sticky="w")
        supr_button=Button(self, text=self.Messages["Analyses_details_sp8"], command=self.supress)
        supr_button.grid(row=0, column=1, sticky="w")

        #Display the mean distance between the target and the segment
        Title_mean_dist=Label(self, text=self.Messages["Analyses_details_sp_Lab4"])
        Title_mean_dist.grid(row=1, column=1, sticky="w")
        Frame_show=Frame(self)
        Frame_show.grid(row=2, column=1)
        Lab_arr=Label(Frame_show, text=">")
        Lab_arr.grid(row=0, column=0, sticky="w")
        self.Lab_mean_dist=Label(Frame_show, textvariable=self.Mean_dist)
        self.Lab_mean_dist.grid(row=0, column=1, sticky="w")
        Label_unit1=Label(Frame_show, text=self.main.Vid.Scale[1])
        Label_unit1.grid(row=0, column=2, sticky="w")

        # Display the number of time the target crossed the segment
        Title_nb_cross=Label(self, text=self.Messages["Analyses_details_sp_Lab5"])
        Title_nb_cross.grid(row=3, column=1, sticky="w")
        Frame_show2=Frame(self)
        Frame_show2.grid(row=4, column=1)
        Lab_arr2=Label(Frame_show2, text=">")
        Lab_arr2.grid(row=0, column=0, sticky="w")
        self.Lab_nb_cross=Label(Frame_show2, textvariable=self.Nb_cross)
        self.Lab_nb_cross.grid(row=0, column=1, sticky="w")

        # Display the latency before the target crossed the segment for the first time
        Title_lat_cross=Label(self, text=self.Messages["Analyses_details_sp_Lab6"])
        Title_lat_cross.grid(row=5, column=1, sticky="w")
        Frame_show3=Frame(self)
        Frame_show3.grid(row=6, column=1)
        Lab_arr3=Label(Frame_show3, text=">")
        Lab_arr3.grid(row=0, column=0, sticky="w")
        self.Lab_lat_cross=Label(Frame_show3, textvariable=self.Lat_cross)
        self.Lab_lat_cross.grid(row=0, column=1, sticky="w")
        Label_unit3=Label(Frame_show3, text="sec")
        Label_unit3.grid(row=0, column=2, sticky="w")


    def update_infos(self):
        '''This function calculates the three measures of interest to be displayed:
        self.Mean_dist: Average distance to the segment
        self.Nb_cross: Number of time the target crossed the segment
        self.Lat_cross: Latency before the first time the target crossed the segment
        Each time, the value is rounded.
        If the value cannot be calculated, the self.main.Calc_speed.calculate_dist_line returns "NA". Same for self.main.Calc_speed.calculate_intersect
        '''

        new_vals=self.main.Calc_speed.calculate_dist_line(parent=self.main, Points=self.Shape[1], ind=self.Ind)
        Crosses=self.main.Calc_speed.calculate_intersect(parent=self.main, Points=self.Shape[1], ind=self.Ind)

        if new_vals=="NA":
            self.Mean_dist.set("NA")
        else:
            self.Mean_dist.set(round(float(new_vals),3))

        self.Nb_cross.set(Crosses[0])

        if Crosses[2]=="NA":
            self.Lat_cross.set("NA")
        else:
            self.Lat_cross.set(round(float(Crosses[2]),3))

    def supress(self):
        '''
        Supress this widget and supress the corresponding element of interest from the list of elements (self.main.Calc_speed.Areas)
        '''
        for shape in range(len(self.main.Calc_speed.Areas[self.MArea])):
            if self.main.Calc_speed.Areas[self.MArea][shape] == self.Shape:
                self.main.Calc_speed.Areas[self.MArea].pop(shape)
                self.boss.show_results()
                self.boss.show_img()
                self.update_infos()
                self.boss.add_pt = [None]
                self.boss.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="active")
                break
        self.destroy()

    def change_area_name(self, new_val, method):
        '''
        This function is called when the user want to change the name of the element. It allows to avoid that the same name is assigned twice
        '''
        auto_modif=False
        if new_val in [shape[3] for shape in self.main.Calc_speed.Areas[self.MArea] if shape!=self.Shape]:
            new_val=new_val+"_1"
            auto_modif=True
        self.Shape[3]=new_val
        if method=="focusout" and auto_modif:
            self.boss.show_results()
        return(True)

class Row_All_Border(Frame):
    '''
    The widget for the borders of the arena as an element of interest.
    parent=the container of this frame
    main=the panel in which the container is displayed. the main object is also related to the current video
            > "self.main.Calc_speed.Areas" is a list of all the elements of interest
    MArea=the identification number of the current element of interest
    Shape=the characterstics of the element (Shape[0]=the kind of element (in that case, always All_borders),Shape[1]=None, Shape[2]=The width of the border, Shape[3]=The name of the element)
    label=the name of the element (either All_borderX or any other name filled by the user)
    Ind=Which target is selected (the one used to display the metrics relative to that element of interest)
    '''
    def __init__(self, parent, main, boss,MArea, Shape, Area, label, Ind, **kw):
        Frame.__init__(self, parent, **kw)
        self.MArea=MArea
        self.boss=boss
        self.main=main
        self.Shape=Shape
        self.Ind=Ind
        self.Area=Area

        self.Mean_dist = StringVar()#Average distance between the target and the closest border
        self.Prop_inside = StringVar()#Proportion of time the taregt spent inside the border's width
        self.update_infos()

        #Import language
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        #Display the name of the element of interest as an Entry (so it can be modified) along with a button to supress it.
        regLab = (self.register(self.change_area_name), '%P', '%V')
        Lab=Entry(self, validate="all", validatecommand=regLab)
        Lab.insert(0, label)
        Lab.config()
        Lab.grid(row=0, column=0, sticky="w")
        supr_button=Button(self, text=self.Messages["Analyses_details_sp8"], command=self.supress)
        supr_button.grid(row=0, column=1, sticky="w")

        #Display the average distance to the closest border
        Title_mean_dist=Label(self, text=self.Messages["Analyses_details_sp_Lab7"])
        Title_mean_dist.grid(row=1, column=1, sticky="w")
        Frame_show=Frame(self)
        Frame_show.grid(row=2, column=1)
        Lab_arr=Label(Frame_show, text=">")
        Lab_arr.grid(row=0, column=0, sticky="w")
        self.Lab_mean_dist=Label(Frame_show, textvariable=self.Mean_dist)
        self.Lab_mean_dist.grid(row=0, column=1, sticky="w")
        Label_unit1=Label(Frame_show, text=self.main.Vid.Scale[1])
        Label_unit1.grid(row=0, column=2, sticky="w")

        #Display the proportion of time the target spent at less than Shape[2] units from the border
        Title_prop_inside=Label(self, text=self.Messages["Analyses_details_sp_Lab8"])
        Title_prop_inside.grid(row=3, column=1, sticky="w")
        Inter_Check_entry = (self.register(self.Check_entry), '%P', '%V')
        self.Scale_Dist = Entry(self, textvariable=self.Shape[2], validate="all", validatecommand=Inter_Check_entry)
        self.Scale_Dist.grid(row=3, column=2, sticky="w")
        self.Shape[2].trace('w', self.inter_draw)
        Label_unit2=Label(self, text=self.main.Vid.Scale[1])
        Label_unit2.grid(row=3, column=3, sticky="w")
        Frame_show2=Frame(self)
        Frame_show2.grid(row=4, column=1)
        Lab_arr2=Label(Frame_show2, text=">")
        Lab_arr2.grid(row=0, column=0, sticky="w")
        self.Lab_prop_inside=Label(Frame_show2, textvariable=self.Prop_inside)
        self.Lab_prop_inside.grid(row=0, column=1, sticky="w")

    def inter_draw(self, *args):
        '''
        This function is called when the value of Shape[2] is modified.
        It updates the displayed frame (in that case, the borders width will appear in red)
        '''
        try:
            float(self.Shape[2].get())
            if float(self.Shape[2].get()) >= 0:
                self.boss.show_img()
                self.update_infos()
        except Exception as e:
            pass


    def Check_entry(self, new_val, method):
        if new_val == "" and method != "focusout":
            return True
        elif new_val != "":
            if method == "key":
                try:
                    if float(new_val) >= 0:
                        return True
                    else:
                        return False
                except Exception as e:
                    print(e)
                    return False
            return True
        else:
            return False


    def update_infos(self):
        '''This function calculates the two measures of interest to be displayed:
        self.Mean_dist: Average distance to the closest border
        self.Prop_inside: Proportion of time the target spent at less than Shape[2] units from the borders

        Each time, the value is rounded.
        If the value cannot be calculated, the self.main.Calc_speed.calculate_dist_border returns "NA".
        '''
        new_vals=self.main.Calc_speed.calculate_dist_border(parent=self.main, Area=self.Area, ind=self.Ind, shape=self.Shape)
        if new_vals[0]=="NA":
            self.Mean_dist.set(new_vals[0])
        else:
            self.Mean_dist.set(round(new_vals[0],3))

        if new_vals[1] == "NA":
            self.Prop_inside.set(new_vals[1])
        else:
            self.Prop_inside.set(round(new_vals[1], 3))



    def supress(self):
        '''
        Supress this widget and supress the corresponding element of interest from the list of elements (self.main.Calc_speed.Areas)
        '''
        for shape in range(len(self.main.Calc_speed.Areas[self.MArea])):
            if self.main.Calc_speed.Areas[self.MArea][shape] == self.Shape:
                self.main.Calc_speed.Areas[self.MArea].pop(shape)
                self.boss.show_results()
                self.boss.show_img()
                self.update_infos()
                self.boss.add_pt = [None]
                self.boss.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="active")
                break
        self.destroy()

    def change_area_name(self, new_val, method):
        '''
        This function is called when the user want to change the name of the element. It allows to avoid that the same name is assigned twice
        '''

        auto_modif=False
        if new_val in [shape[3] for shape in self.main.Calc_speed.Areas[self.MArea] if shape!=self.Shape]:
            new_val=new_val+"_1"
            auto_modif=True
        self.Shape[3]=new_val
        if method=="focusout" and auto_modif:
            self.boss.show_results()
        return(True)

class Row_Border(Frame):
    '''
    The widget for one or more borders of the arena as an element of interest.
    parent=the container of this frame
    main=the panel in which the container is displayed. the main object is also related to the current video
            > "self.main.Calc_speed.Areas" is a list of all the elements of interest
    MArea=the identification number of the current element of interest
    Shape=the characterstics of the element (Shape[0]=the kind of element (in that case, always Borders),Shape[1]= a list of all the segments of border considered: [[Seg1pt1,Seg1pt2],[Seg2pt1,Seg2pt2],[Seg3pt1,Seg2pt2]...], Shape[2]=The width of the borders, Shape[3]=The name of the element)
    label=the name of the element (either BorderX or any other name filled by the user)
    Ind=Which target is selected (the one used to display the metrics relative to that element of interest)
    '''
    def __init__(self, parent, main, boss, MArea, Shape, label, Ind, **kw):
        Frame.__init__(self, parent, **kw)
        self.MArea=MArea
        self.boss=boss
        self.main=main
        self.Shape=Shape
        self.Ind=Ind

        self.Mean_dist = StringVar()# Average distance between the target and the closest selected border
        self.Prop_inside = StringVar()# Proportion of time the target spent inside the selected border's width
        self.Lat_inside = StringVar()# Latency to enter inside one of the selected border's width
        self.update_infos()

        #Import language
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        #Display the name of the element of interest as an Entry (so it can be modified) along with a button to supress it.
        regLab = (self.register(self.change_area_name), '%P', '%V')
        Lab=Entry(self, validate="all", validatecommand=regLab)
        Lab.insert(0, label)
        Lab.config()
        Lab.grid(row=0, column=0, sticky="w")
        supr_button=Button(self, text=self.Messages["Analyses_details_sp8"], command=self.supress)
        supr_button.grid(row=0, column=1, sticky="w")

        #Display the average distance to the closest selected border
        Title_mean_dist=Label(self, text=self.Messages["Analyses_details_sp_Lab9"])
        Title_mean_dist.grid(row=1, column=1, sticky="w", columnspan=3)
        Frame_show=Frame(self)
        Frame_show.grid(row=2, column=1)
        Lab_arr=Label(Frame_show, text=">")
        Lab_arr.grid(row=0, column=0, sticky="w")
        self.Lab_mean_dist=Label(Frame_show, textvariable=self.Mean_dist)
        self.Lab_mean_dist.grid(row=0, column=1, sticky="w")
        Label_unit1=Label(Frame_show, text=self.main.Vid.Scale[1])
        Label_unit1.grid(row=0, column=2, sticky="w")

        #Display the proportion of time the target spent at less than Shape[2] units from one of the selected borders
        Title_prop_inside=Label(self, text=self.Messages["Analyses_details_sp_Lab8"])
        Title_prop_inside.grid(row=3, column=1, sticky="w")
        Inter_Check_entry = (self.register(self.Check_entry), '%P', '%V')
        self.Scale_Dist = Entry(self, textvariable=self.Shape[2], validate="all", validatecommand=Inter_Check_entry)
        self.Scale_Dist.grid(row=3, column=2, sticky="w")
        self.Shape[2].trace('w', self.inter_draw)
        Label_unit2=Label(self, text=self.main.Vid.Scale[1])
        Label_unit2.grid(row=3, column=3, sticky="w")
        Frame_show2=Frame(self)
        Frame_show2.grid(row=4, column=1)
        Lab_arr2=Label(Frame_show2, text=">")
        Lab_arr2.grid(row=0, column=0, sticky="w")
        self.Lab_prop_inside=Label(Frame_show2, textvariable=self.Prop_inside)
        self.Lab_prop_inside.grid(row=0, column=1, sticky="w")

        #Display the latency before the target entered at less than Shape[2] units from one of the selected borders
        Title_lat_inside=Label(self, text=self.Messages["Analyses_details_sp_Lab10"])
        Title_lat_inside.grid(row=5, column=1, sticky="w")
        self.Scale_Dist2 = Label(self, textvariable=self.Shape[2])
        self.Scale_Dist2.grid(row=5, column=2, sticky="w")
        Label_unit3=Label(self, text=self.main.Vid.Scale[1])
        Label_unit3.grid(row=5, column=3, sticky="w")
        Frame_show3=Frame(self)
        Frame_show3.grid(row=6, column=1)
        Lab_arr3=Label(Frame_show3, text=">")
        Lab_arr3.grid(row=0, column=0, sticky="w")
        self.Lab_lat_inside=Label(Frame_show3, textvariable=self.Lat_inside)
        self.Lab_lat_inside.grid(row=0, column=1, sticky="w")
        Label_unit4=Label(Frame_show3, text="sec")
        Label_unit4.grid(row=0, column=2, sticky="w")

    def inter_draw(self, *args):
        '''
        This function is called when the value of Shape[2] is modified.
        It updates the displayed frame (in that case, the area of the circle around the point of interest is modified)
        '''
        try:
            float(self.Shape[2].get())
            if float(self.Shape[2].get()) >= 0:
                self.boss.show_img()
                self.update_infos()
        except Exception as e:
            pass


    def Check_entry(self, new_val, method):
        '''
        Avoid the user to add non-numeric or negative inputs for Shape[2]
        '''
        if new_val == "" and method != "focusout":
            return True
        elif new_val != "":
            if method == "key":
                try:
                    if float(new_val) >= 0:
                        return True
                    else:
                        return False
                except Exception as e:
                    print(e)
                    return False
            return True
        else:
            return False


    def update_infos(self):
        '''This function calculates the three measures of interest to be displayed:
        self.Mean_dist: Averaged distance between the selected Ind and the closest selected border
        self.Latency: Latency before the target approach at less than Shape[2] units from one of the selected borders
        self.Prop_Time: Proportion of time the target spent at less than Shape[2] units from one of the selected borders

        Each time, the value is rounded.
        If the value cannot be calculated, the self.main.Calc_speed.calculate_dist_sep_border returns "NA".
        '''
        new_vals=self.main.Calc_speed.calculate_dist_sep_border(parent=self.main, shape=self.Shape, ind=self.Ind)
        if new_vals[0]=="NA":
            self.Mean_dist.set(new_vals[0])
        else:
            self.Mean_dist.set(round(new_vals[0],3))

        if new_vals[1] == "NA":
            self.Prop_inside.set(new_vals[1])
        else:
            self.Prop_inside.set(round(new_vals[1], 3))

        if new_vals[2] == "NA":
            self.Lat_inside.set(new_vals[2])
        else:
            self.Lat_inside.set(round(new_vals[2], 3))


    def supress(self):
        '''
        Supress this widget and supress the corresponding element of interest from the list of elements (self.main.Calc_speed.Areas)
        '''
        for shape in range(len(self.main.Calc_speed.Areas[self.MArea])):
            if self.main.Calc_speed.Areas[self.MArea][shape] == self.Shape:
                self.main.Calc_speed.Areas[self.MArea].pop(shape)
                self.boss.show_results()
                self.boss.show_img()
                self.update_infos()
                self.boss.add_pt = [None]
                self.boss.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="active")
                break
        self.destroy()

    def change_area_name(self, new_val, method):
        '''
        This function is called when the user want to change the name of the element. It allows to avoid that the same name is assigned twice
        '''
        auto_modif=False
        if new_val in [shape[3] for shape in self.main.Calc_speed.Areas[self.MArea] if shape!=self.Shape]:
            new_val=new_val+"_1"
            auto_modif=True
        self.Shape[3]=new_val
        if method=="focusout" and auto_modif:
            self.boss.show_results()
        return(True)

class Row_Shape(Frame):
    '''
    The widget for one shape as an element of interest.
    parent=the container of this frame
    main=the panel in which the container is displayed. the main object is also related to the current video
            > "self.main.Calc_speed.Areas" is a list of all the elements of interest
    MArea=the identification number of the current element of interest
    Shape=the characteristics of the element (Shape[0]=the kind of element (in that case, Ellipse, Rectangle or Poly),Shape[1]= a list of all the corners: [pt1,pt2,pt3...], Shape[2]=None, Shape[3]=The name of the element)
    label=the name of the element (either EllipseX, RectangleX, PolyX or any other name filled by the user)
    Ind=Which target is selected (the one used to display the metrics relative to that element of interest)
    '''
    def __init__(self, parent, main, boss, MArea, Shape, label, Ind, **kw):
        Frame.__init__(self, parent, **kw)
        self.MArea=MArea
        self.boss=boss
        self.main=main
        self.Shape=Shape
        self.Ind=Ind

        self.Prop_inside = StringVar()#Proportion of time the target spent inside the element's shape
        self.Lat_inside = StringVar()#Latency before the target enter inside the shape
        self.update_infos()

        #Import the language
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        # Display the name of the element of interest as an Entry (so it can be modified) along with a button to supress it.
        regLab = (self.register(self.change_area_name), '%P', '%V')
        Lab=Entry(self, validate="all", validatecommand=regLab)
        Lab.insert(0, label)
        Lab.config()
        Lab.grid(row=0, column=0, sticky="w")
        supr_button = Button(self, text=self.Messages["Analyses_details_sp8"], command=self.supress)
        supr_button.grid(row=0, column=1, sticky="w")

        # Display the proportion of time the target spent inside the element's shape.
        Title_prop_inside=Label(self, text=self.Messages["Analyses_details_sp_Lab11"])
        Title_prop_inside.grid(row=1, column=1, sticky="w")
        Frame_show=Frame(self)
        Frame_show.grid(row=2, column=1)
        Lab_arr=Label(Frame_show, text=">")
        Lab_arr.grid(row=0, column=0, sticky="w")
        self.Lab_prop_inside=Label(Frame_show, textvariable=self.Prop_inside)
        self.Lab_prop_inside.grid(row=0, column=1, sticky="w")

        # Display the latency before the target enter inside the shape.
        Title_lat_inside=Label(self, text=self.Messages["Analyses_details_sp_Lab12"])
        Title_lat_inside.grid(row=3, column=1, sticky="w")
        Frame_show2=Frame(self)
        Frame_show2.grid(row=4, column=1)
        Lab_arr3=Label(Frame_show2, text=">")
        Lab_arr3.grid(row=0, column=0, sticky="w")
        self.Lab_lat_inside=Label(Frame_show2, textvariable=self.Lat_inside)
        self.Lab_lat_inside.grid(row=0, column=1, sticky="w")
        Label_unit4=Label(Frame_show2, text="sec")
        Label_unit4.grid(row=0, column=2, sticky="w")

    def update_infos(self):
        '''This function calculates the three measures of interest to be displayed:
        self.Prop_inside: Proportion of time the target spent inside the element's shape
        self.Lat_inside: Latency before the target enter inside the shape.

        Each time, the value is rounded.
        If the value cannot be calculated, the self.main.Calc_speed.calculate_dist_lat returns "NA".
        '''
        if len(self.Shape[1])>0:
            empty=np.zeros([self.boss.image.shape[0],self.boss.image.shape[1],1], np.uint8)
            if self.Shape[0]=="Ellipse":
                Function_draw_mask.Draw_elli(empty, [po[0] for po in self.Shape[1]], [po[1] for po in self.Shape[1]], 255, thick=-1)
            elif self.Shape[0]=="Rectangle":
                Function_draw_mask.Draw_rect(empty, [po[0] for po in self.Shape[1]], [po[1] for po in self.Shape[1]], 255, thick=-1)
            elif self.Shape[0]=="Polygon":
                Function_draw_mask.Draw_Poly(empty, [po[0] for po in self.Shape[1]], [po[1] for po in self.Shape[1]], 255, thick=-1)

            cnt, _=cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            cnt=[]

        new_vals=self.main.Calc_speed.calculate_time_inside(parent=self.main, cnt=cnt, ind=self.Ind)


        if new_vals[0] == "NA":
            self.Prop_inside.set(new_vals[0])
        else:
            self.Prop_inside.set(round(new_vals[0], 3))

        if new_vals[1] == "NA":
            self.Lat_inside.set(new_vals[1])
        else:
            self.Lat_inside.set(round(new_vals[1], 3))


    def supress(self):
        '''
        Supress this widget and supress the corresponding element of interest from the list of elements (self.main.Calc_speed.Areas)
        '''
        for shape in range(len(self.main.Calc_speed.Areas[self.MArea])):
            if self.main.Calc_speed.Areas[self.MArea][shape] == self.Shape:
                self.main.Calc_speed.Areas[self.MArea].pop(shape)
                self.boss.show_results()
                self.boss.show_img()
                self.update_infos()
                self.boss.add_pt = [None]
                self.boss.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="active")
                break
        self.destroy()

    def change_area_name(self, new_val, method):
        '''
        This function is called when the user want to change the name of the element. It allows to avoid that the same name is assigned twice
        '''
        auto_modif=False
        if new_val in [shape[3] for shape in self.main.Calc_speed.Areas[self.MArea] if shape!=self.Shape]:
            new_val=new_val+"_1"
            auto_modif=True
        self.Shape[3]=new_val
        if method=="focusout" and auto_modif:
            self.boss.show_results()
        return(True)