from tkinter import *
from AnimalTA.A_General_tools import Function_draw_mask, UserMessages, User_help
from AnimalTA.E_Post_tracking.b_Analyses import Class_Shapes_rows, Interface_border_portion, Interface_extend_elements, Functions_deformation
import numpy as np
import PIL
import math
import cv2
from operator import itemgetter


"""This script codes four classes inherited from Frame, each one associated with one kind of data analyses. 
The objective of these frame is to allow the user to determine the parameters associated with each of these analyses.
1. Basic: analyses of individual trajectories: distance traveled, time moving, etc
2. Spacial: analyses of the relationship between the trajectories and some elements of interest defined by user
3. Exploration: analyses of the proportion of the arenas explored by the targets
4. Interindividual: analyses of between-targets interactions (if N>1 for the arena)"""

class Details_basics(Frame):
    #This Frame display a graph and associated results.
    #It allows the user to change the movement thershold of the targets (under this threshold, targets are considered stopped).
    def __init__(self, parent, main, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.parent.geometry("1050x620")
        self.main=main
        self.grid(sticky="nsew")
        self.ready=False
        self.parent.attributes('-toolwindow', True)

        Grid.columnconfigure(self.parent, 0, weight=1)
        Grid.rowconfigure(self.parent, 0, weight=1)

        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=100)

        #Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Analyses_details_T"])

        self.moving =False

        # An optionmenu to select which target we want to follow
        self.List_inds_names=dict()
        for ind in range(len(self.main.Vid.Identities)):
            self.List_inds_names[ind]=self.Messages["Arena_short"]+ "{}, ".format(self.main.Vid.Identities[ind][0])+ self.Messages["Individual_short"] +" {}".format(self.main.Vid.Identities[ind][1])
        self.Ind_name=StringVar()
        self.Ind_name.set(self.Messages["Arena_short"]+ "{}, ".format(self.main.Vid.Identities[0][0])+ self.Messages["Individual_short"] +" {}".format(self.main.Vid.Identities[0][1]))
        self.Which_ind = OptionMenu(self, self.Ind_name, *self.List_inds_names.values(), command=self.change_ind)
        self.Which_ind.grid(row=0, column=0,sticky="n")

        #A graph is shown that represent the movement speed of the taregt as a function of time.
        #In this graph, the user can also see and modify the target's movement threshold.
        Frame_for_Graph=Frame(self)
        Frame_for_Graph.grid(row=1, column=0, stick="nsew")
        Grid.columnconfigure(Frame_for_Graph, 0, weight=1)  ########NEW
        Grid.columnconfigure(Frame_for_Graph, 1, weight=1)  ########NEW
        Grid.columnconfigure(Frame_for_Graph, 2, weight=100)  ########NEW

        Grid.rowconfigure(Frame_for_Graph, 0, weight=100)  ########NEW
        Grid.rowconfigure(Frame_for_Graph, 1, weight=1)  ########NEW
        Grid.rowconfigure(Frame_for_Graph, 2, weight=1)  ########NEW

        self.Ylab_can = Canvas(Frame_for_Graph, width=20, height=300)
        self.Ylab_can.grid(row=0,column=0, sticky="nsew")

        self.Yaxe_can = Canvas(Frame_for_Graph, width=50, height=300)
        self.Yaxe_can.grid(row=0,column=1, sticky="nsew")

        self.Graph=Canvas(Frame_for_Graph, width=300, height=300, scrollregion=(0,0,0,0))
        self.Graph.grid(row=0,column=2,sticky="nsew")
        self.Graph.bind("<Configure>", self.show_graph)
        self.Graph.bind("<Button-1>", self.callback)
        self.Graph.bind("<B1-Motion>", self.move_seuil)

        self.Xaxe_can = Canvas(Frame_for_Graph, height=15)
        self.Xaxe_can.grid(row=1,column=2, sticky="nsew")
        self.Xaxe_can.create_text(210, 7, text=self.Messages["Analyses_details_graph_X"])

        hsb=Scrollbar(Frame_for_Graph, orient=HORIZONTAL, command=self.Graph.xview)
        hsb.grid(row=2,column=2,sticky="ew")
        self.Graph.config(xscrollcommand=hsb.set)
        self.stay_on_top()

        User_Frame=Frame(self)
        User_Frame.grid(row=1, column=1, sticky="nsew")
        Grid.rowconfigure(User_Frame, 0, weight=100)
        Grid.rowconfigure(User_Frame, 1, weight=1)


        #Help user
        self.HW= User_help.Help_win(User_Frame, default_message=self.Messages["Analyses_details0"].format(round(self.main.Calc_speed.seuil_movement, 3), self.main.Vid.Scale[1]))
        self.HW.grid(row=0, column=0,sticky="nsew")
        self.HW.grid_propagate(False)

        #The results related to the current target will appear in this Frame, they are updated each time that the movement threshold is changed.
        Frame_for_results=Frame(User_Frame)
        Frame_for_results.grid(row=1, column=0)

        ##Different results
        # Prop time lost
        self.Prop_lost=StringVar()
        self.Prop_lost.set("0.0")
        self.Label_Prop_lost=Label(Frame_for_results, text=self.Messages["Analyses_details_Lab1"])
        self.Label_Prop_lost.grid(row=1, column=0, sticky="e")
        self.Show_Prop_lost=Label(Frame_for_results, textvariable=self.Prop_lost)
        self.Show_Prop_lost.grid(row=1, column=1, sticky="w")
        self.Show_Prop_lost.grid()
        self.Label_Prop_lost.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Analyses_details1"]))
        self.Label_Prop_lost.bind("<Leave>", self.HW.remove_tmp_message)

        #Mean speed
        self.Mean_Speed=StringVar()
        self.Mean_Speed.set("0.0")
        self.Label_mean=Label(Frame_for_results, text=self.Messages["Analyses_details_Lab2"])
        self.Label_mean.grid(row=2, column=0, sticky="e")
        self.Show_mean=Label(Frame_for_results, textvariable=self.Mean_Speed)
        self.Show_mean.grid(row=2, column=1, sticky="w")
        self.Label_mean.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Analyses_details2"]))
        self.Label_mean.bind("<Leave>", self.HW.remove_tmp_message)

        # Mean speed in move
        self.Mean_Speed_Move=StringVar()
        self.Mean_Speed_Move.set("0.0")
        self.Label_mean_move=Label(Frame_for_results, text=self.Messages["Analyses_details_Lab3"])
        self.Label_mean_move.grid(row=3, column=0, sticky="e")
        self.Show_mean_move=Label(Frame_for_results, textvariable=self.Mean_Speed_Move)
        self.Show_mean_move.grid(row=3, column=1, sticky="w")
        self.Show_mean_move.grid()
        self.Label_mean_move.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Analyses_details3"]))
        self.Label_mean_move.bind("<Leave>", self.HW.remove_tmp_message)

        # Prop time move
        self.Prop_move=StringVar()
        self.Prop_move.set("0.0")
        self.Label_Prop_move=Label(Frame_for_results, text=self.Messages["Analyses_details_Lab4"])
        self.Label_Prop_move.grid(row=4, column=0, sticky="e")
        self.Show_Prop_move=Label(Frame_for_results, textvariable=self.Prop_move)
        self.Show_Prop_move.grid(row=4, column=1, sticky="w")
        self.Show_Prop_move.grid()
        self.Label_Prop_move.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Analyses_details4"]))
        self.Label_Prop_move.bind("<Leave>", self.HW.remove_tmp_message)

        # Dist traveled
        self.Dist_total=StringVar()
        self.Dist_total.set("0.0")
        self.Label_Dist_total=Label(Frame_for_results, text=self.Messages["Analyses_details_Lab5"])
        self.Label_Dist_total.grid(row=5, column=0, sticky="e")
        self.Show_Dist_total=Label(Frame_for_results, textvariable=self.Dist_total)
        self.Show_Dist_total.grid(row=5, column=1, sticky="w")
        self.Show_Dist_total.grid()
        self.Label_Dist_total.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Analyses_details5"]))
        self.Label_Dist_total.bind("<Leave>", self.HW.remove_tmp_message)

        # Dist traveled while moving
        self.Dist_total_move=StringVar()
        self.Dist_total_move.set("0.0")
        self.Label_Dist_total_move=Label(Frame_for_results, text=self.Messages["Analyses_details_Lab6"])
        self.Label_Dist_total_move.grid(row=6, column=0, sticky="e")
        self.Show_Dist_total_move=Label(Frame_for_results, textvariable=self.Dist_total_move)
        self.Show_Dist_total_move.grid(row=6, column=1, sticky="w")
        self.Show_Dist_total_move.grid()
        self.Label_Dist_total_move.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Analyses_details6"]))
        self.Label_Dist_total_move.bind("<Leave>", self.HW.remove_tmp_message)

        #Close the Frame/window
        self.Quit_button=Button(self, text=self.Messages["Analyses_details_B1"], command=self.parent.destroy, background="#6AED35")
        self.Quit_button.grid(row=7, column=0, columnspan=2, sticky="sew")

        #Show the results for the selected target
        self.update_vals()


        #Entry to modify manually the threshold:

        Lab_ent_thresh=Label(Frame_for_results, text=self.Messages["Names6"])
        Lab_ent_thresh.grid(row=0, column=0, sticky="e")
        verif_E_float = (self.register(self.update_threshold), '%P', '%V')
        tmp_var=StringVar()
        tmp_var.set("")
        self.Ent_threshold=Entry(Frame_for_results, textvariable=tmp_var, validatecommand=verif_E_float, validate="all")
        self.Ent_threshold.grid(row=0, column=1, sticky="e")


    def update_vals(self):
        # Show the results values for the selected target
        self.show_Mean_Speed()
        self.show_Prop_lost()
        self.show_calculate_dist()
        self.update_vals_flex()

    def update_vals_flex(self):
        # Update the values for the selected target that are impacted by the movement threshold
        self.show_Mean_Speed_Move()
        self.show_Prop_move()
        self.show_calculate_dist_move()


    ##Different functions to calculate the results:
    #Time lost:
    def show_Prop_lost(self):
        Ind=list(self.List_inds_names.keys())[list(self.List_inds_names.values()).index(self.Ind_name.get())]
        new_val=self.main.Calc_speed.calculate_lost(parent=self.main,ind=Ind)
        if new_val != "NA":
            self.Prop_lost.set(str(round(new_val, 3)))
        else:
            self.Prop_lost.set("NA")

    #Time moving:
    def show_Prop_move(self):
        Ind=list(self.List_inds_names.values()).index(self.Ind_name.get())
        new_val=self.main.Calc_speed.calculate_prop_move(parent=self.main,ind=Ind)
        if new_val!="NA":
            self.Prop_move.set(str(round(new_val,3)))
        else:
            self.Prop_move.set("NA")

    #Speed
    def show_Mean_Speed(self):
        Ind=list(self.List_inds_names.values()).index(self.Ind_name.get())
        new_val=self.main.Calc_speed.calculate_mean_speed(parent=self.main,ind=Ind, in_move=False)
        if new_val!="NA":
            self.Mean_Speed.set(str(round(new_val,3)))
        else:
            self.Mean_Speed.set("NA")

    #Speed while moving
    def show_Mean_Speed_Move(self):
        Ind = list(self.List_inds_names.values()).index(self.Ind_name.get())
        new_val=self.main.Calc_speed.calculate_mean_speed(parent=self.main,ind=Ind, in_move=True)
        if new_val!="NA":
            self.Mean_Speed_Move.set(str(round(new_val,3)))
        else:
            self.Mean_Speed_Move.set("NA")

    # Distance traveled
    def show_calculate_dist(self):
        Ind = list(self.List_inds_names.values()).index(self.Ind_name.get())
        new_val, meander = self.main.Calc_speed.calculate_dist(parent=self.main, ind=Ind, in_move=False)
        if new_val != "NA":
            self.Dist_total.set(str(round(new_val, 3)))
        else:
            self.Dist_total.set("NA")

    # Distance traveled while moving
    def show_calculate_dist_move(self):
        Ind = list(self.List_inds_names.values()).index(self.Ind_name.get())
        new_val, meander = self.main.Calc_speed.calculate_dist(parent=self.main, ind=Ind, in_move=True)
        if new_val != "NA":
            self.Dist_total_move.set(str(round(new_val, 3)))
        else:
            self.Dist_total_move.set("NA")

    def change_ind(self, *arg):
        #If the user wants to see the results associated with another target
        self.add_cur_loc()
        self.update_vals()
        self.main.highlight = list(self.List_inds_names.keys())[list(self.List_inds_names.values()).index(self.Ind_name.get())]
        self.main.modif_image()
        self.show_graph()

    def show_graph(self, *args):
        #Display the graph
        Ind=list(self.List_inds_names.values()).index(self.Ind_name.get())
        self.main.highlight = Ind
        Ys=self.main.Calc_speed.get_all_speeds_NAs(parent=self.main, ind=Ind, in_move=False)
        self.draw_graph(range(len(Ys)),Ys)
        self.add_seuil()

    def draw_graph(self,Xs,Ys):
        #Draw the graph
        #Xs and Ys are time and speed.

        # Clear last graph
        self.Graph.delete("all")
        self.Yaxe_can.delete("all")
        self.Ylab_can.delete("all")

        self.ecart=50#Esthetical point, to allow nice representation of the axes
        self.Width=len(Ys) #Maximum width
        self.Height = self.Graph.winfo_height() #The height is adapted to the space available
        self.Graph.config(scrollregion=(0,0,self.Width, self.Height))

        if max(Ys) > 0:
            Ymax=max(Ys)
        else:
            Ymax=1

        self.Ratio_Ys=(self.Height-self.ecart*2)/Ymax
        Corr_Ys=[self.Ratio_Ys*val for val in Ys]

        self.Ratio_Xs = (self.Width) / max(Xs)
        Corr_Xs = [self.Ratio_Xs * val for val in Xs]

        #Axes labels
        self.Ylab_can.create_text(10,self.Height/2,text=self.Messages["Analyses_details_graph_Y"].format(self.main.Vid.Scale[1]),angle=90)

        #Axes values
        self.Graph.create_line(0,self.Height-self.ecart,self.Width,self.Height-self.ecart, width=2)
        for text in np.arange (0, Ymax, Ymax/6):
            self.Yaxe_can.create_text(self.ecart/2,(self.Height-(self.ecart+text*self.Ratio_Ys)),text=round(text,2))
            self.Yaxe_can.create_line(self.Yaxe_can.winfo_width()-10,(self.Height-(self.ecart+text*self.Ratio_Ys)),self.Yaxe_can.winfo_width()+10,(self.Height-(self.ecart+text*self.Ratio_Ys)))

        self.Graph.create_line(0, self.ecart, 0, self.Height-self.ecart, width=2)
        for text in np.arange(200, (self.main.Vid.Cropped[1][1]-self.main.Vid.Cropped[1][0])/self.main.one_every, 200):
            self.Graph.create_text(text,self.Height-(self.ecart/2),text=round(((int((text)/self.Ratio_Xs) + int(round((self.main.Vid.Cropped[1][0])/self.main.one_every)))/self.main.Vid.Frame_rate[1]),2))
            self.Graph.create_line(text-1,self.Height-(self.ecart)+10,text-1,self.Height-(self.ecart))

        #Draw the data
        for point in range(len(Ys)):
            if point>0:
                self.Graph.create_line(Corr_Xs[point-1], self.Height-(Corr_Ys[point-1]+self.ecart),Corr_Xs[point], self.Height-(Corr_Ys[point]+self.ecart), fill="black")

        #Draw a line to show where we are in the video (which frame is displayed on the video reader)
        self.add_cur_loc()
        self.ready=True
        self.main.modif_image()

    def add_seuil(self):
        #Draw an horizontal line on the graph to show the threshold limit
        val=self.main.Calc_speed.seuil_movement
        self.seuil_line=self.Graph.create_line(0, self.Height - (self.Ratio_Ys*val + self.ecart), self.Width,self.Height - (self.Ratio_Ys*val + self.ecart), fill="red", width=2)


    def add_cur_loc(self):
        # Draw a line to show where we are in the video (which frame is displayed on the video reader)
        try:
            self.Graph.delete(self.line_pos)
        except:
            pass
        cur_pos=self.main.Scrollbar.active_pos- int(round((self.main.Vid.Cropped[1][0])/self.main.one_every))
        self.line_pos=self.Graph.create_line(cur_pos*self.Ratio_Xs,self.ecart,cur_pos*self.Ratio_Xs,self.Height-self.ecart, width=2, fill="blue")

    def stay_on_top(self):
        # We want this window to remain on the top of the others
        if self.ready:
            self.parent.lift()
            self.add_cur_loc()
        self.parent.after(50, self.stay_on_top)

    def callback(self, event):
        #Interaction between user and graph.
        x = event.widget.canvasx(event.x)
        y = event.widget.canvasy(event.y)

        #If the user selected the threshold line, we move it
        if y<(self.Height-(self.main.Calc_speed.seuil_movement*self.Ratio_Ys+self.ecart)+5) and y>(self.Height-(self.main.Calc_speed.seuil_movement*self.Ratio_Ys+self.ecart)-5):
            self.moving=True

        #Else, we move display the video associated with the time's value clicked by the user (X axis value).
        else:
            self.moving = False
            self.main.Scrollbar.active_pos=int((x)/self.Ratio_Xs) + int(round((self.main.Vid.Cropped[1][0])/self.main.one_every))
            self.main.Scrollbar.refresh()
            self.main.Vid_Lecteur.update_image(int((x)/self.Ratio_Xs)+ int(round((self.main.Vid.Cropped[1][0])/self.main.one_every)))

    def move_seuil(self, event):
        #Move the movement threshold and change its value
        try:
            if self.moving:
                self.Graph.delete(self.seuil_line)
                if event.widget.canvasy(event.y)>self.ecart and event.widget.canvasy(event.y)<(self.Height-self.ecart):
                    self.main.Calc_speed.seuil_movement=round((self.Height-event.widget.canvasy(event.y)-self.ecart)/self.Ratio_Ys,3)

                self.Ent_threshold.delete(0, END)  # deletes the current value
                self.Ent_threshold.insert(0, str(round(self.main.Calc_speed.seuil_movement,3)))  # inserts new value assigned by 2nd parameter
                self.HW.change_default_message(self.Messages["Analyses_details0"].format(round(self.main.Calc_speed.seuil_movement,3),self.main.Vid.Scale[1]))
        except:
            print("Overflow")


    def update_threshold(self, new_val, method):
        # Avoid user to writting non numerical values in the Entry box
        if new_val == "" and method != "focusout":
            return True
        elif new_val != "" :
            try:
                new_val = float(new_val)
                self.main.Calc_speed.seuil_movement=new_val
                self.Graph.delete(self.seuil_line)
                self.add_seuil()
                self.update_vals_flex()
                self.HW.change_default_message(self.Messages["Analyses_details0"].format(round(self.main.Calc_speed.seuil_movement,3),self.main.Vid.Scale[1]))
                return True
            except Exception as e:
                print(e)
                return False
        else:
            return False

class Details_spatial(Frame):
    """
    This frame show the arenas and allow the user to add elements of interest inside each of them. These elements may be of various kind (points, lines, shapes, etc.).
    The results associated with these elements and with the trajectory of the selected target are also displayed.
    """
    def __init__(self, parent, main, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.parent.geometry("1050x620")
        self.main=main
        self.grid(sticky="news")
        self.ready=False
        self.add_pt=[None,-1]
        self.zoom_strength = 0.3
        self.final_width = 250
        self.under_mouse=None
        self.show_mask=False
        Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW
        self.last_cur_pos = self.main.Scrollbar.active_pos - int(round((self.main.Vid.Cropped[1][0]) / self.main.one_every))
        self.parent.attributes('-toolwindow', True)

        #Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Analyses_details_sp_T"])

        #A menubar in which we will be able to add new elements of interest.
        self.menubar = Menu(self.parent)
        self.parent.config(menu=self.menubar)
        file_menu = Menu(self.menubar, tearoff=False)
        Type_Point=Menu(file_menu, tearoff=0)
        Type_Point.add_command(label=self.Messages["Analyses_details_sp_Menu1_1"], command=self.add_point)
        Type_Point.add_command(label=self.Messages["Analyses_details_sp_Menu1_2"], command=self.add_point_center)
        file_menu.add_cascade(label=self.Messages["Analyses_details_sp_Menu1"],menu=Type_Point)

        Type_Line=Menu(file_menu, tearoff=0)
        Type_Line.add_command(label=self.Messages["Analyses_details_sp_Menu1_1"], command=self.add_line)
        Type_Line.add_command(label=self.Messages["Analyses_details_sp_Menu2_2"], command=self.add_line_border)
        file_menu.add_cascade(label=self.Messages["Analyses_details_sp_Menu2"],menu=Type_Line)

        Type_border=Menu(file_menu, tearoff=0)
        Type_border.add_command(label=self.Messages["Analyses_details_sp_Menu3_1"], command=self.add_border)
        Type_border.add_command(label=self.Messages["Analyses_details_sp_Menu3_2"], command=self.add_all_borders)
        file_menu.add_cascade(label=self.Messages["Analyses_details_sp_Menu3"],menu=Type_border)

        Type_Shape = Menu(file_menu, tearoff=0)
        Type_Shape.add_command(label=self.Messages["Analyses_details_sp_Menu4_1"], command=self.add_ellipse)
        Type_Shape.add_command(label=self.Messages["Analyses_details_sp_Menu4_2"], command=self.add_rectangle)
        Type_Shape.add_command(label=self.Messages["Analyses_details_sp_Menu4_3"], command=self.add_poly)
        file_menu.add_cascade(label=self.Messages["Analyses_details_sp_Menu4"], menu=Type_Shape)

        self.menubar.add_cascade(label=self.Messages["Analyses_details_sp_Menu0"], menu=file_menu)

        #Optionlist to change the identity of the target of interest
        self.List_inds_names = dict()
        for ind in range(len(self.main.Vid.Identities)):
            self.List_inds_names[ind]=self.Messages["Arena_short"]+ "{}, ".format(self.main.Vid.Identities[ind][0])+ self.Messages["Individual_short"] +" {}".format(self.main.Vid.Identities[ind][1])

        self.Ind_name=StringVar()
        self.Ind_name.set(self.Messages["Arena_short"]+ "{}, ".format(self.main.Vid.Identities[0][0])+ self.Messages["Individual_short"] +" {}".format(self.main.Vid.Identities[0][1]))

        self.Which_ind = OptionMenu(self, self.Ind_name, *self.List_inds_names.values(), command=self.change_ind)
        self.Which_ind.grid(row=0, column=0,)

        #One frame of the video is used to show the arenas and to place, show and modify the elements of interest
        self.Canvas_for_video=Canvas(self, width=700, height=500, bd=0, highlightthickness=0)
        self.Canvas_for_video.grid(row=1, column=0, sticky="nsew")
        Grid.columnconfigure(self, 0, weight=5)  ########NEW
        Grid.columnconfigure(self, 1, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=1)  ########NEW
        self.Canvas_for_video.update()
        self.load_img()

        #Bindings for interactive image
        self.Canvas_for_video.bind("<Configure>", self.show_img)
        self.Canvas_for_video.bind("<Button-1>", self.callback)
        self.Canvas_for_video.bind("<Control-1>", self.Zoom_in)
        self.Canvas_for_video.bind("<Control-3>", self.Zoom_out)
        self.Canvas_for_video.bind("<B1-Motion>", self.callback_move_vid)

        self.Frame_user=Frame(self, width=150)
        self.Frame_user.grid(row=0, column=1, rowspan=2, sticky="nsew")
        Grid.columnconfigure(self.Frame_user, 0, weight=1)  ########NEW
        Grid.columnconfigure(self.Frame_user, 1, weight=1)  ########NEW
        Grid.rowconfigure(self.Frame_user, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.Frame_user, 1, weight=1)  ########NEW
        Grid.rowconfigure(self.Frame_user, 2, weight=100)  ########NEW

        #Help user and parameters
        self.HW= User_help.Help_win(self.Frame_user, default_message=self.Messages["Analyses_details_sp0"])
        self.HW.grid(row=0, column=0, columnspan=3,sticky="nsew")

        #Buttons to modify the elements defined by user
        self.Button_expend=Button(self.Frame_user, text=self.Messages["Analyses_details_sp_B1"], command=self.expend, width=37)
        self.Button_expend.grid(row=1, column=0, sticky="new")
        self.Button_expend.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Analyses_details_sp1"]))
        self.Button_expend.bind("<Leave>", self.HW.remove_tmp_message)

        self.Supress_This=Button(self.Frame_user, text=self.Messages["Analyses_details_sp_B2"], command=self.supr_this, width=37)
        self.Supress_This.grid(row=1, column=1, sticky="new")
        self.Supress_This.bind("<Enter>", lambda a:self.HW.change_tmp_message(self.Messages["Analyses_details_sp2"]))
        self.Supress_This.bind("<Leave>", self.HW.remove_tmp_message)

        Frame_Ana=Frame(self.Frame_user)
        Frame_Ana.grid(row=2, column=0, columnspan=2, sticky="nsew")
        Grid.columnconfigure(Frame_Ana, 0, weight=1)  ########NEW
        Grid.rowconfigure(Frame_Ana, 0, weight=1)  ########NEW

        #Where the results associated with elements of interest are shown
        self.Liste_analyses=Canvas(Frame_Ana, height=200, width=400)
        self.Liste_analyses.grid(row=0, column=0, sticky="nsew")
        self.Liste_analyses.columnconfigure(0, weight=1)

        self.vsb=Scrollbar(Frame_Ana, orient=VERTICAL, command=self.Liste_analyses.yview)
        self.vsb.grid(row=0,column=1, sticky="ns")
        self.Frame_for_results=Frame(self.Liste_analyses)
        self.Frame_for_results.bind("<Configure>",self.on_frame_conf)

        self.Liste_analyses.create_window((4,4), window=self.Frame_for_results, anchor="nw")
        self.Liste_analyses.configure(yscrollcommand=self.vsb.set)
        self.Frame_for_results.columnconfigure(0, weight=1)

        #More general buttons
        self.Quit_button=Button(self.Frame_user, text=self.Messages["Analyses_details_sp_B3"], command=self.close, background="#6AED35")
        self.Quit_button.grid(row=3, column=0, columnspan=2, sticky="sew")

        self.Supress_All_Vid=Button(self.Frame_user, text=self.Messages["Analyses_details_sp_B4"], command=self.supr_all_this_vid, width=35, background="orange")
        self.Supress_All_Vid.grid(row=4, column=0, sticky="new")

        self.Supress_All=Button(self.Frame_user, text=self.Messages["Analyses_details_sp_B5"], command=self.supr_all, width=35, background="red")
        self.Supress_All.grid(row=4, column=1, sticky="new")

        self.ready = True
        self.stay_on_top()
        self.show_results()

        self.bind_all("<Return>", self.validate_borders)
        self.parent.protocol("WM_DELETE_WINDOW", self.close)


    def supr_this(self):
        #Supress all elements of interest inside the current arena
        self.main.Calc_speed.Areas[self.Area]=[]
        self.show_results()
        self.show_img()

    def supr_all_this_vid(self):
        # Supress all elements of interest in this video (all arenas)
        for Ar in range(len(self.main.Calc_speed.Areas)):
            self.main.Calc_speed.Areas[Ar]=[]
        self.show_results()
        self.show_img()

    def supr_all(self):
        # Supress all elements of interest in all videos
        for Vid in self.main.main_frame.liste_of_videos:
            if Vid==self.main.Vid:
                self.supr_all_this_vid()
            for Ar in range(len(Vid.Analyses[1])):
                Vid.Analyses[1][Ar] = []
        self.show_results()
        self.show_img()

    def expend(self):
        #Allow the user to select a list of arenas in which the elements of interest will be duplicated
        newWindow = Toplevel(self.parent.master)
        Interface_extend_elements.Lists(parent=newWindow, boss=self, liste_videos=self.main.main_frame.liste_of_videos, Current_Vid=self.main.Vid, Current_Area=self.Area)
        self.wait_window(newWindow)


    def on_frame_conf(self, *arg):
        #Ensure that all results of elements of interest are comprised in the Canvas
        self.Liste_analyses.configure(scrollregion=self.Liste_analyses.bbox("all"))

    def update_area(self):
        #If the user changes the target of interest, the function look for which is the new arena and save its contour
        place = 0
        self.Area = None
        selected=list(self.List_inds_names.values()).index(self.Ind_name.get())
        for Ar in range(len(self.main.Vid.Track[1][6])):
            for Ind in range(self.main.Vid.Track[1][6][Ar]):
                if selected==place:
                    self.Area=Ar
                place+=1

        mask = Function_draw_mask.draw_mask(self.main.Vid)
        Arenas, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        Arenas = Function_draw_mask.Organise_Ars(Arenas)
        self.Arena_pts = Arenas[self.Area]

        if len(self.main.Vid.Analyses[4][0])>0:
            self.Arena_pts=self.Arena_pts[:, 0, :]
            self.Arena_pts = np.array([self.Arena_pts], dtype=np.float32)
            self.Arena_pts = cv2.perspectiveTransform(self.Arena_pts, self.main.Vid.Analyses[4][0])
            self.Arena_pts=cv2.convexHull(self.Arena_pts.astype(np.int32))



    def load_img(self,*args):
        #Load the image and hilight the position of the current arena
        self.Ind = list(self.List_inds_names.keys())[list(self.List_inds_names.values()).index(self.Ind_name.get())]
        self.update_area()

        #Create mask (everything black except the inside of the arena)
        self.image_clean1=self.main.img_no_shapes
        mask=np.zeros([self.image_clean1.shape[0], self.image_clean1.shape[1], 1], np.uint8)
        mask=cv2.drawContours(mask, [self.Arena_pts], -1,(255,255,255),-1)

        #Application of the mask so it appears as a black veil everywhere except where the arena is
        self.image_clean_trans=cv2.bitwise_and(self.image_clean1, self.image_clean1, mask=mask)
        blend=0.5
        self.image_clean=cv2.addWeighted(self.image_clean1, blend, self.image_clean_trans, 1 - blend, 0)

        #Info for zoom in/out
        self.image=np.copy(self.image_clean)
        self.Size=self.image.shape
        self.ratio = self.Size[1] / self.final_width
        self.zoom_sq = [0, 0, self.image.shape[1], self.image.shape[0]]
        self.show_img()

    def show_img(self, *args):
        #Show the image to be displayed (with visible elemenst of interest)

        self.draw_shapes()#Draw the elements of interest
        best_ratio = max(self.Size[1] / (self.Canvas_for_video.winfo_width()),
                         self.Size[0] / (self.Canvas_for_video.winfo_height()))
        prev_final_width = self.final_width
        self.final_width = int(math.ceil(self.Size[1] / best_ratio))
        self.ratio = self.ratio * (prev_final_width / self.final_width)
        image_to_show = self.image[self.zoom_sq[1]:self.zoom_sq[3], self.zoom_sq[0]:self.zoom_sq[2]]
        image_to_show1 = cv2.resize(image_to_show,(self.final_width, int(self.final_width * (self.Size[0] / self.Size[1]))))
        self.image_to_show2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(image_to_show1))
        self.Canvas_for_video.create_image(0, 0, image=self.image_to_show2, anchor=NW)
        self.Canvas_for_video.config(width=self.final_width, height=int(self.final_width * (self.Size[0] / self.Size[1])))


    def change_ind(self, *arg):
        #Change the current target
        self.validate_borders()
        self.main.highlight = list(self.List_inds_names.keys())[list(self.List_inds_names.values()).index(self.Ind_name.get())]
        self.Ind = list(self.List_inds_names.keys())[list(self.List_inds_names.values()).index(self.Ind_name.get())]
        self.update_area()

        for widg in self.Frame_for_results.grid_slaves():
            if widg.Shape[1] == self.Area:
                widg.Ind = self.Ind
                widg.update_infos()

        self.main.modif_image()
        self.load_img()
        self.show_results()

    def stay_on_top(self):
        #We want the Frame window parent to stay on top
        if self.ready:
            self.parent.lift()
            self.change_image()
        self.parent.after(50, self.stay_on_top)

    def change_image(self):
        #Change the displayedimage according to the position in the video
        cur_pos=self.main.Scrollbar.active_pos- int(round((self.main.Vid.Cropped[1][0])/self.main.one_every))
        if cur_pos!=self.last_cur_pos:
            self.load_img()
        self.last_cur_pos=cur_pos


    def validate_borders(self, *args):
        #Validation of the borders selected by user (user pressed <Return> key after having selected the borders desired)
        if self.add_pt[0]=="Borders" or self.add_pt[0]=="Ellipse" or self.add_pt[0]=="Rectangle" or self.add_pt[0]=="Polygon":
            self.add_pt=[None,-1]
            self.show_mask = False
            self.show_img()
            self.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="active")
            self.HW.change_default_message(self.Messages["Analyses_details_sp00"])
            self.show_results()




    ####### self.add_pt is a variable whose value is [None,-1] when the user did not ask to addnew element of interest.
    # When the user ask to add an element of interest, self.add_pt is modified according to the kind of element.
    # This allows later to know what to do when the user will indicate coordinates on the frame.
    def add_point(self):
        # In that case, user asked to add a point
        self.add_pt=["Point"]
        self.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="disabled")
        self.HW.change_default_message(self.Messages["Analyses_details_sp4"])

    def add_line(self):
        # In that case, user asked to add a line
        self.add_pt=["Line",1]
        self.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="disabled")
        self.HW.change_default_message(self.Messages["Analyses_details_sp3"])

    def add_line_border(self):
        # In that case, user asked to add a line whose extremity are attached to a corner or a border
        self.add_pt = ["Line_border", 1]
        self.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="disabled")
        self.show_mask=True
        self.show_img()
        self.HW.change_default_message(self.Messages["Analyses_details_sp7"])

    def add_border(self):
        # In that case, user asked to add one or more borders
        self.add_pt = ["Borders", 1]
        self.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="disabled")
        self.show_mask = True
        self.show_img()
        self.show_results()
        self.HW.change_default_message(self.Messages["Analyses_details_sp5"])

    def add_ellipse(self):
        # In that case, user asked to add an ellipse
        self.add_pt = ["Ellipse", 1]
        self.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="disabled")
        self.show_img()
        self.show_results()
        self.HW.change_default_message(self.Messages["Analyses_details_sp6"])

    def add_rectangle(self):
        # In that case, user asked to add a rectangle
        self.add_pt = ["Rectangle", 1]
        self.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="disabled")
        self.show_img()
        self.show_results()
        self.HW.change_default_message(self.Messages["Analyses_details_sp6"])

    def add_poly(self):
        # In that case, user asked to add a polygon
        self.add_pt = ["Polygon", 1]
        self.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="disabled")
        self.show_img()
        self.show_results()
        self.HW.change_default_message(self.Messages["Analyses_details_sp6"])

    def add_all_borders(self):
        # Special case, the element to add does not require more user input (in that case, all borders are selected)
        self.main.Calc_speed.Areas[self.Area].append(["All_borders",[],DoubleVar(),self.Messages["List_elem_Bds_all"]+str(len(self.main.Calc_speed.Areas[self.Area]))])
        self.show_img()
        self.show_results()

    def add_point_center(self):
        #Special case, the element to add does not require more user input (in that case, a point placed in the center of the arena)
        M = cv2.moments(self.Arena_pts)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        self.main.Calc_speed.Areas[self.Area].append(["Point", [(cX, cY)], DoubleVar(),self.Messages["List_elem_Pt"]+str(len(self.main.Calc_speed.Areas[self.Area]))])
        # 0=Type of area, 1=Area, 2 = Pts locations, 3 =others.
        self.show_img()
        self.show_results()

    def callback(self, event):
        #The user clicked on the image
        PtX=int(event.widget.canvasx(event.x) * self.ratio + self.zoom_sq[0])
        PtY=int(event.widget.canvasy(event.y) * self.ratio + self.zoom_sq[1])

        #We first check if user clicked on an existing point (i.e. points being part of an element of interest)
        self.under_mouse=None
        for shape in self.main.Calc_speed.Areas[self.Area]:
            if shape[0]!="Borders":
                for pt in range(len(shape[1])):
                    dist=math.sqrt((PtX-shape[1][pt][0])**2 + (PtY-shape[1][pt][1])**2)
                    if dist<7:
                        self.under_mouse=[shape,pt]

        #If it was not a point already defined, we verify of the user wanted to add any new element:
        ### self.main.Calc_speed.Areas is a list of arenas in which there are sublists of elements of interest.
        if self.under_mouse==None and self.add_pt[0]=="Point":#If the user wanted to add a point
            self.main.Calc_speed.Areas[self.Area].append(["Point",[(PtX,PtY)],DoubleVar(),self.Messages["List_elem_Pt"]+str(len(self.main.Calc_speed.Areas[self.Area]))])
            #0=Type of area, 1 = Pts locations, 2 =type of analyses.
            self.show_img()
            self.show_results()
            self.add_pt = [None,-1]
            self.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="active")
            self.HW.change_default_message(self.Messages["Analyses_details_sp00"])

        elif self.under_mouse==None and self.add_pt[0]=="Line":#If the user wanted to add a line
            if self.add_pt[1]==1:# If no points were defined yet
                self.main.Calc_speed.Areas[self.Area].append(["Line",[(PtX,PtY)],DoubleVar(),self.Messages["List_elem_Line"]+str(len(self.main.Calc_speed.Areas[self.Area]))])
                #0=Type of area, 1 = Pts locations, 2 =type of analyses.
                self.add_pt[1]-=1 # We indicate that one point was defined

            elif self.add_pt[1]==0:# If there was already one point defined
                self.main.Calc_speed.Areas[self.Area][len(self.main.Calc_speed.Areas[self.Area])-1][1].append((PtX,PtY))
                self.add_pt = [None,-1]
                self.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="active")
                self.HW.change_default_message(self.Messages["Analyses_details_sp00"])
                self.show_results()
            self.show_img()

        elif self.under_mouse==None and self.add_pt[0]=="Line_border":# Same here but the points location are limited to the borders/corners
            for pt in range(len(self.list_of_pts)): # self.list_of_pts summarize the corners of the arena
                dist = math.sqrt((PtX - self.list_of_pts[pt][0]) ** 2 + (PtY - self.list_of_pts[pt][1]) ** 2)
                if dist < 7: #If the user clicked on a corner, the point get the same coordinates as this corner
                    if self.add_pt[1] == 1:
                        self.main.Calc_speed.Areas[self.Area].append(["Line", [self.list_of_pts[pt]], DoubleVar(), self.Messages["List_elem_Line"]+str(len(self.main.Calc_speed.Areas[self.Area]))])
                        self.add_pt[1] -= 1
                    elif self.add_pt[1]==0:
                        self.main.Calc_speed.Areas[self.Area][len(self.main.Calc_speed.Areas[self.Area]) - 1][1].append(self.list_of_pts[pt])
                        self.add_pt = [None, -1]
                        self.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="active")
                        self.HW.change_default_message(self.Messages["Analyses_details_sp00"])
                        self.show_mask = False
                        self.show_results()
                    break #Useless to do the whole loop if we found a first point

                if Function_draw_mask.Touched_seg((PtX, PtY), [self.list_of_pts[pt], self.list_of_pts[pt - 1]]):#If not, we check if the point is touching a contour border
                    self.ask_portion(self.list_of_pts[pt],self.list_of_pts[pt-1]) #We ask the user where on the border the point should be placed.
                    if self.add_pt[1] == 1:#If it was the first point, we save it and wiat for the second
                        self.main.Calc_speed.Areas[self.Area].append(["Line", [(int(round(self.list_of_pts[pt-1][0]*self.ratio_border+self.list_of_pts[pt][0]*(1-self.ratio_border))),int(round(self.list_of_pts[pt-1][1]*self.ratio_border+self.list_of_pts[pt][1]*(1-self.ratio_border))))], DoubleVar(), self.Messages["List_elem_Line"]+str(len(self.main.Calc_speed.Areas[self.Area]))])
                        self.add_pt[1] -= 1
                    elif self.add_pt[1] == 0: # If it is the second point, we save the element, allow to add other element and display the results associated with the segment.
                        self.main.Calc_speed.Areas[self.Area][len(self.main.Calc_speed.Areas[self.Area]) - 1][1].append((int(round(self.list_of_pts[pt-1][0] * self.ratio_border + self.list_of_pts[pt][0] * (1 - self.ratio_border))),
                                       int(round(self.list_of_pts[pt-1][1] * (self.ratio_border) + self.list_of_pts[pt][1] * (1 - self.ratio_border)))))
                        self.add_pt = [None]
                        self.menubar.entryconfig(self.Messages["Analyses_details_sp_Menu0"], state="active")
                        self.HW.change_default_message(self.Messages["Analyses_details_sp00"])
                        self.show_mask = False
                        self.show_results()
                    break #Useless to do the whole loop if we found a first point

            self.show_img()

        elif self.under_mouse==None and self.add_pt[0]=="Borders":#If the user wanted to add a border
            for pt in range(len(self.list_of_pts)):
                Pt=self.list_of_pts[pt]
                Last_pt = self.list_of_pts[pt-1]
                if Function_draw_mask.Touched_seg((PtX, PtY), [Pt, Last_pt]):
                    if self.add_pt[1]==1:# If there was no border selected yet
                        self.main.Calc_speed.Areas[self.Area].append(["Borders", [[Pt,Last_pt]], DoubleVar(), self.Messages["List_elem_Bds"]+str(len(self.main.Calc_speed.Areas[self.Area]))])
                        self.add_pt[1]=0 # We indicate that there is at least one selected border
                    else:# If there was already at least one border selected, we add the new one to the list (if it is not the same than one already added)
                        if [Pt,Last_pt] not in self.main.Calc_speed.Areas[self.Area][len(self.main.Calc_speed.Areas[self.Area]) - 1][1]:
                            self.main.Calc_speed.Areas[self.Area][len(self.main.Calc_speed.Areas[self.Area]) - 1][1].append([Pt,Last_pt])
                    break
            self.show_img()

        elif self.under_mouse==None and (self.add_pt[0]=="Ellipse" or self.add_pt[0]=="Rectangle" or self.add_pt[0]=="Polygon"):
            # If the user wanted to add a shape (ellipse, rectangle or polygon)
            if self.add_pt[1]==1:#If it is the first point of this shape, we create the element in the list
                self.main.Calc_speed.Areas[self.Area].append([self.add_pt[0], [(PtX,PtY)], DoubleVar(), self.Messages["List_elem_"+self.add_pt[0]]+"_"+str(len(self.main.Calc_speed.Areas[self.Area]))])
                self.add_pt[1] = 0
            else:# Else, we add the point to the existing element
                self.main.Calc_speed.Areas[self.Area][len(self.main.Calc_speed.Areas[self.Area]) - 1][1].append((PtX,PtY))
            self.show_img()

    def callback_move_vid(self, event):
        #If the user drag a point on the image
        event.x = int(event.x * self.ratio + self.zoom_sq[0])
        event.y = int(event.y * self.ratio + self.zoom_sq[1])

        if self.under_mouse!=None and event.x >= 0 and event.y >= 0 and event.x <= self.Size[1] and event.y <= self.Size[0]:
            #If it remain inside the image, the point position is updated
            self.under_mouse[0][1][self.under_mouse[1]] = [event.x,event.y]
            self.show_img()

            for widg in self.Frame_for_results.grid_slaves():
                if widg.Shape == self.under_mouse[0]:#We update the associated results
                    widg.Shape[1][self.under_mouse[1]]=[event.x,event.y]
                    widg.Ind=self.Ind
                    widg.update_infos()

    def draw_shapes(self, *args):
        #Draw all the elements of interest.
        self.image=np.copy(self.image_clean)
        if self.show_mask: #We also highlight the borders and corners if we are expecting the user to select one of them (line stick to border or borders selection)
            self.list_of_pts=[]
            approx = cv2.approxPolyDP(self.Arena_pts, 0.025 * cv2.arcLength(self.Arena_pts, True), True)
            for pt in range(len(approx)):
                self.list_of_pts.append((int(round(approx[pt][0][0])),int(round(approx[pt][0][1]))))
                cv2.line(self.image, (int(round(approx[pt][0][0])),int(round(approx[pt][0][1]))),(int(round(approx[pt-1][0][0])),int(round(approx[pt-1][0][1]))),(150, 150, 255),2)
            for pt in range(len(approx)):
                cv2.circle(self.image, (int(round(approx[pt][0][0])),int(round(approx[pt][0][1]))), 5, (0, 0, 0), -1)
                cv2.circle(self.image, (int(round(approx[pt][0][0])),int(round(approx[pt][0][1]))), 3, (150, 150, 255), -1)

        ID=0
        overlay = self.image.copy()
        #Draw the different shapes
        for shape in self.main.Calc_speed.Areas[self.Area]:
            if shape[0]=="Point":
                cv2.circle(self.image, shape[1][0], 7, (0, 0, 0), -1)
                cv2.circle(self.image, shape[1][0], 5, (0, 0, 175), -1)
                cv2.putText(self.image, str(ID), (shape[1][0][0] + 5, shape[1][0][1] - 5), cv2.FONT_HERSHEY_DUPLEX,fontScale=1, color=(0, 0, 10), thickness=5)
                cv2.putText(self.image,str(ID), (shape[1][0][0]+5,shape[1][0][1]-5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(0,0,75),thickness=2)
                cv2.circle(self.image, shape[1][0], int(round(float(shape[2].get()) * float(self.main.Vid.Scale[0]))),(0, 0, 100), 2)
                overlay = cv2.circle(overlay, shape[1][0],int(round(float(shape[2].get())*float(self.main.Vid.Scale[0]))), (0, 0, 175), -1)

            if shape[0]=="Line":
                for pt in shape[1]:
                    cv2.circle(self.image, pt, 7, (0, 0, 0), -1)
                    cv2.circle(self.image, pt, 5, (175, 0, 175), -1)

                if len(shape[1])>1:
                    cv2.line(self.image,shape[1][0],shape[1][1],color=(150, 0, 150),thickness=2)
                cv2.putText(self.image, str(ID), (pt[0] + 5, pt[1] - 5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1,color=(50, 0, 50), thickness=5)
                cv2.putText(self.image,str(ID), (pt[0]+5,pt[1]-5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(150, 0, 150),thickness=2)

            if shape[0]=="All_borders":
                self.image=cv2.drawContours(self.image, [self.Arena_pts],-1, (255, 0, 0), 2)

                if shape[2].get()>0:
                    empty=np.zeros((self.image.shape[0],self.image.shape[1]), np.uint8)
                    border = cv2.drawContours(np.copy(empty), [self.Arena_pts], -1, (255,255,255),int(round(shape[2].get() * float(self.main.Vid.Scale[0]) * 2)))
                    area = cv2.drawContours(np.copy(empty), [self.Arena_pts], -1, (255,255,255),-1)
                    empty=cv2.bitwise_and(border,border, mask=area)
                    inside_border,_=cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    self.image = cv2.drawContours(self.image, inside_border, -1, (150, 0, 0), 2)
                    overlay=cv2.drawContours(overlay, inside_border,-1, (255, 0, 0), -1)
                cv2.putText(self.image, str(ID), (self.Arena_pts[0][0][0] + 5, self.Arena_pts[0][0][1] - 5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(75, 0, 0), thickness=3)
                cv2.putText(self.image,str(ID), (self.Arena_pts[0][0][0]+5,self.Arena_pts[0][0][1]-5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(255,0,0),thickness=2)

            if shape[0]=="Borders":
                for bord in shape[1]:
                    cv2.line(self.image, bord[0], bord[1], color=(255, 0, 0), thickness=2)

                empty = np.zeros((self.image.shape[0], self.image.shape[1]), np.uint8)
                border=np.copy(empty)

                for bord in shape[1]:
                    border=cv2.line(border, bord[0], bord[1], color=(255, 0, 0), thickness=2)
                cnts,_=cv2.findContours(border, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                border = cv2.drawContours(border, cnts,-1, (255, 255, 255),int(round(shape[2].get() * float(self.main.Vid.Scale[0]) * 2)))
                area = cv2.drawContours(np.copy(empty), [self.Arena_pts], -1, (255, 255, 255), -1)
                empty = cv2.bitwise_and(border, border, mask=area)
                inside_border, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                self.image = cv2.drawContours(self.image, inside_border, -1, (150, 0, 0), 2)
                overlay = cv2.drawContours(overlay, inside_border, -1, (255, 0, 0), -1)

                cv2.putText(self.image, str(ID), (bord[0][0] + 5, bord[0][1] - 5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1,color=(75, 0, 0),thickness=5)
                cv2.putText(self.image, str(ID), (bord[0][0] + 5, bord[0][1] - 5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1,color=(255, 0, 0),thickness=2)

            if shape[0]=="Ellipse":
                for pt in shape[1]:
                    cv2.circle(self.image, pt, 7, (0, 0, 0), -1)
                    cv2.circle(self.image, pt, 5, (0, 255, 0), -1)

                if len(shape[1])>1:
                    Function_draw_mask.Draw_elli(self.image, [po[0] for po in shape[1]], [po[1] for po in shape[1]], (0, 255, 0))
                    Function_draw_mask.Draw_elli(overlay, [po[0] for po in shape[1]], [po[1] for po in shape[1]], (0, 255, 0), thick=-1)
                cv2.putText(self.image,str(ID), (pt[0]+5,pt[1]-5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(0,75,0),thickness=5)
                cv2.putText(self.image, str(ID), (pt[0] + 5, pt[1] - 5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1,color=(0, 255, 0), thickness=2)

            if shape[0]=="Rectangle":
                for pt in shape[1]:
                    cv2.circle(self.image, pt, 7, (0, 0, 0), -1)
                    cv2.circle(self.image, pt, 5, (0, 175, 175), -1)

                if len(shape[1])>1:
                    Function_draw_mask.Draw_rect(self.image, [po[0] for po in shape[1]], [po[1] for po in shape[1]], color=(0, 75, 75))
                    Function_draw_mask.Draw_rect(overlay, [po[0] for po in shape[1]], [po[1] for po in shape[1]], color=(0, 175, 175), thick=-1)
                cv2.putText(self.image, str(ID), (pt[0] + 5, pt[1] - 5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1,color=(0, 50, 50), thickness=5)
                cv2.putText(self.image,str(ID), (pt[0]+5,pt[1]-5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(0, 175, 175),thickness=2)

            if shape[0]=="Polygon":
                for pt in shape[1]:
                    cv2.circle(self.image, pt, 7, (0, 0, 0), -1)
                    cv2.circle(self.image, pt, 5, (150, 150, 0), -1)

                if len(shape[1])>1:
                    Function_draw_mask.Draw_Poly(self.image, [po[0] for po in shape[1]], [po[1] for po in shape[1]], (75, 75, 0))
                    Function_draw_mask.Draw_Poly(overlay, [po[0] for po in shape[1]], [po[1] for po in shape[1]], (150, 150, 0), thick=-1)
                cv2.putText(self.image, str(ID), (pt[0] + 5, pt[1] - 5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1,color=(50, 50, 0), thickness=5)
                cv2.putText(self.image,str(ID), (pt[0]+5,pt[1]-5), cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(150, 150, 0),thickness=2)

            ID += 1
        self.image = cv2.addWeighted(self.image, 0.5, overlay, 0.5, 0)

    def ask_portion(self,Pt1, Pt2):
        #This open a window in which the user can select where on the segment a point will be placed.
        self.ratio_border = 0.5
        newWindow = Toplevel(self.parent.master)
        Interface_border_portion.Ask(parent=newWindow, boss=self, Pt1=Pt1, Pt2=Pt2, scale=self.main.Vid.Scale, ratio=self.ratio_border)
        self.wait_window(newWindow)

    def show_results(self):
        #Update the results related to the different elements of interest

        for widg in self.Frame_for_results.grid_slaves():#We destroy all
            widg.destroy()
            try:
                for ti in widg.Shape[3].trace_vinfo():
                    widg.Shape[3].trace_vdelete(*ti)
            except:
                pass
            widg.destroy()

        if len(self.main.Calc_speed.Areas[self.Area])>0:
            self.Button_expend.config(state="active")
            self.Supress_This.config(state="active")
            self.HW.change_default_message(self.Messages["Analyses_details_sp00"])
        else:
            self.Button_expend.config(state="disable")
            self.Supress_This.config(state="disable")
            self.HW.change_default_message(self.Messages["Analyses_details_sp0"])

        ID=0
        for shape in self.main.Calc_speed.Areas[self.Area]:#We rebuild all
            if shape[0]=="Point":
                new= Class_Shapes_rows.Row_Point(parent=self.Frame_for_results, main=self.main, boss=self, MArea=self.Area, Shape=shape, label=shape[3], Ind=self.Ind)
                new.grid(sticky="w")

            if shape[0]=="Line":
                new= Class_Shapes_rows.Row_Line(parent=self.Frame_for_results, main=self.main, boss=self, MArea=self.Area, Shape=shape, label=shape[3], Ind=self.Ind)
                new.grid(sticky="w")

            if shape[0]=="All_borders":
                new= Class_Shapes_rows.Row_All_Border(parent=self.Frame_for_results, main=self.main, boss=self, MArea=self.Area, Shape=shape, Area=self.Arena_pts, label=shape[3], Ind=self.Ind)
                new.grid(sticky="w")

            if shape[0]=="Borders":
                new= Class_Shapes_rows.Row_Border(parent=self.Frame_for_results, main=self.main, boss=self, MArea=self.Area, Shape=shape, label=shape[3], Ind=self.Ind)
                new.grid(sticky="w")

            if shape[0]=="Ellipse" or shape[0]=="Rectangle" or shape[0]=="Polygon":
                new= Class_Shapes_rows.Row_Shape(parent=self.Frame_for_results, main=self.main, boss=self, MArea=self.Area, Shape=shape, label=shape[3], Ind=self.Ind)
                new.grid(sticky="w")

            ID+=1

    def Zoom_in(self, event):
        #Zoom in the image
        self.new_zoom_sq = [0, 0, 0, 0]
        PX = event.x / ((self.zoom_sq[2] - self.zoom_sq[0]) / self.ratio)
        PY = event.y / ((self.zoom_sq[3] - self.zoom_sq[1]) / self.ratio)

        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]
        ZWX = (self.zoom_sq[2] - self.zoom_sq[0]) * (1 - self.zoom_strength)
        ZWY = (self.zoom_sq[3] - self.zoom_sq[1]) * (1 - self.zoom_strength)

        if ZWX > 100:
            self.new_zoom_sq[0] = int(event.x - PX * ZWX)
            self.new_zoom_sq[2] = int(event.x + (1 - PX) * ZWX)
            self.new_zoom_sq[1] = int(event.y - PY * ZWY)
            self.new_zoom_sq[3] = int(event.y + (1 - PY) * ZWY)

            self.ratio = ZWX / self.final_width
            self.zoom_sq = self.new_zoom_sq
            self.zooming = True
            self.show_img()

    def Zoom_out(self, event):
        #Zoom out from the image
        self.new_zoom_sq = [0, 0, 0, 0]
        PX = event.x / ((self.zoom_sq[2] - self.zoom_sq[0]) / self.ratio)
        PY = event.y / ((self.zoom_sq[3] - self.zoom_sq[1]) / self.ratio)

        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]

        ZWX = (self.zoom_sq[2] - self.zoom_sq[0]) * (1 + self.zoom_strength)
        ZWY = (self.zoom_sq[3] - self.zoom_sq[1]) * (1 + self.zoom_strength)

        if ZWX < self.Size[1] and ZWY < self.Size[0]:
            if int(event.x - PX * ZWX) >= 0 and int(event.x + (1 - PX) * ZWX) <= self.Size[1]:
                self.new_zoom_sq[0] = int(event.x - PX * ZWX)
                self.new_zoom_sq[2] = int(event.x + (1 - PX) * ZWX)
            elif int(event.x + (1 - PX) * ZWX) > self.Size[1]:
                self.new_zoom_sq[0] = int(self.Size[1] - ZWX)
                self.new_zoom_sq[2] = int(self.Size[1])
            elif int(event.x - PX * ZWX) < 0:
                self.new_zoom_sq[0] = 0
                self.new_zoom_sq[2] = int(ZWX)

            if int(event.y - PY * ZWY) >= 0 and int(event.y + (1 - PY) * ZWY) <= self.Size[0]:
                self.new_zoom_sq[1] = int(event.y - PY * ZWY)
                self.new_zoom_sq[3] = self.new_zoom_sq[1] + int(ZWY)

            elif int(event.y + (1 - PY) * ZWY) > self.Size[0]:
                self.new_zoom_sq[1] = int(self.Size[0] - ZWY)
                self.new_zoom_sq[3] = int(self.Size[0])
            elif int(event.y - PY * ZWY) < 0:
                self.new_zoom_sq[1] = 0
                self.new_zoom_sq[3] = int(ZWY)
            self.ratio = ZWX / self.final_width


        else:
            self.new_zoom_sq = [0, 0, self.image.shape[1], self.image.shape[0]]
            self.ratio = self.Size[1] / self.final_width

        self.zoom_sq = self.new_zoom_sq
        self.zooming = False
        self.show_img()

    def close(self):
        #Close the parent window
        self.unbind_all("<Return>")
        self.main.modif_image()
        self.parent.destroy()

class Details_explo(Frame):
    def __init__(self, parent, main, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent = parent
        self.parent.geometry("1050x620")
        self.main = main
        self.grid(sticky="news")
        self.ready = False
        self.add_pt = [None, -1]
        self.zoom_strength = 0.3
        self.final_width = 251
        Grid.columnconfigure(self.parent, 0, weight=1)
        Grid.rowconfigure(self.parent, 0, weight=1)
        self.last_cur_pos = self.main.Scrollbar.active_pos - int(round((self.main.Vid.Cropped[1][0]) / self.main.one_every))
        self.parent.attributes('-toolwindow', True)

        # Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Analyses_details_sp_T"])

        #Add an optionmenu to select the target of interest
        self.List_inds_names = dict()
        for ind in range(len(self.main.Vid.Identities)):
            self.List_inds_names["Ind"+str(ind)]=self.Messages["Arena_short"]+ "{}, ".format(self.main.Vid.Identities[ind][0])+ self.Messages["Individual_short"] +" {}".format(self.main.Vid.Identities[ind][1])

        self.Ind_name=StringVar()
        self.Ind_name.set(self.Messages["Arena_short"]+ "{}, ".format(self.main.Vid.Identities[0][0])+ self.Messages["Individual_short"] +" {}".format(self.main.Vid.Identities[0][1]))

        self.Which_ind = OptionMenu(self, self.Ind_name, *self.List_inds_names.values(), command=self.change_ind)
        self.Which_ind.grid(row=0, column=0, )

        self.Canvas_for_video = Canvas(self, width=700, height=500, bd=0, highlightthickness=0)
        self.Canvas_for_video.grid(row=1, column=0, sticky="nsew")
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        self.Canvas_for_video.update()
        self.load_img()


        self.Canvas_for_video.bind("<Control-1>", self.Zoom_in)
        self.Canvas_for_video.bind("<Control-3>", self.Zoom_out)
        self.Canvas_for_video.bind("<Configure>", self.show_img)

        self.Frame_user = Frame(self, width=150)
        self.Frame_user.grid(row=0, column=1, rowspan=2, sticky="nsew")
        Grid.columnconfigure(self.Frame_user, 0, weight=1)
        Grid.columnconfigure(self.Frame_user, 1, weight=1)
        Grid.rowconfigure(self.Frame_user, 0, weight=1)
        Grid.rowconfigure(self.Frame_user, 1, weight=1)
        Grid.rowconfigure(self.Frame_user, 2, weight=100)

        # Help user and parameters
        self.HW = User_help.Help_win(self.Frame_user, default_message=self.Messages["Analyses_details_exp0"])
        self.HW.grid(row=0, column=0, columnspan=2, sticky="nsew")

        Frame_Ana = Frame(self.Frame_user)
        Frame_Ana.grid(row=2, column=0, columnspan=2, sticky="nsew")
        Grid.columnconfigure(Frame_Ana, 0, weight=1)
        Grid.rowconfigure(Frame_Ana, 0, weight=1)

        Frame_check = Frame(Frame_Ana)
        Frame_check.grid(row=0, column=0, columnspan=3)

        #Show the parameters and the results
        self.param_p = IntVar(value=self.main.Infos_explo[2])
        self.param_p_explo =Frame(Frame_Ana)
        Grid.columnconfigure(self.param_p_explo, 0, weight=1)
        Grid.columnconfigure(self.param_p_explo, 1, weight=1)

        lab_param_p = Label(self.param_p_explo, text=self.Messages["Analyses_details_exp_Lab3"])
        lab_param_p.grid(row=0, column=0, sticky="nse")


        #We have checkbuttons to allow user to select which of the three methods is prefered
        self.shape_mesh = IntVar()
        self.shape_mesh.set(self.main.Infos_explo[0])
        # The target explores a circular area around it at each frame
        Check_mod = Checkbutton(Frame_check, text=self.Messages["Analyses_details_exp1"], variable=self.shape_mesh, onvalue=0, command=self.show_explored)
        Check_mod.grid(row=0, column=0)

        #Traditional method
        #Rectangular mesh
        Check_rect = Checkbutton(Frame_check, text=self.Messages["Analyses_details_exp2"], variable=self.shape_mesh, onvalue=1, command=self.show_explored)
        Check_rect.grid(row=0, column=1)

        #circular mesh
        Check_circle = Checkbutton(Frame_check, text=self.Messages["Analyses_details_exp3"], variable=self.shape_mesh, onvalue=2, command=self.show_explored)
        Check_circle.grid(row=0, column=2)
        #In the case of the circle, we have a second parameter which allow to change the shape of the internal cells
        scale_param_p = Scale(self.param_p_explo, from_=1, variable=self.param_p, to=4, resolution=1, orient=HORIZONTAL, command=self.show_explored)
        scale_param_p.grid(row=0, column=1, sticky="nsw")

        Grid.columnconfigure(Frame_Ana, 0, weight=1)
        Grid.columnconfigure(Frame_Ana, 1, weight=20)
        Grid.columnconfigure(Frame_Ana, 2, weight=3)
        Grid.columnconfigure(Frame_Ana, 3, weight=1)

        #This  is the main parameter: the  area that a target explore, either a circle around the target or the size of each cell in a mesh.
        self.Explo_size_squares=StringVar(value=self.main.Infos_explo[1])

        scale_mm2=(1/float(self.main.Vid.Scale[0]))**2
        self.min_explo_area=(cv2.contourArea(self.Arena_pts)*scale_mm2)/1000

        #We can define it using the scale
        Squares_explo_lab=Label(Frame_Ana, text=self.Messages["Analyses_details_exp_Lab4"])
        Squares_explo_lab.grid(row=1, column=0, sticky="se")
        self.Explo_size_squares_scale=StringVar(value=self.main.Infos_explo[1])
        self.Explo_size_squares_scale.trace("w", lambda a,b,c: self.Explo_size_squares.set(self.Explo_size_squares_scale.get()))
        Squares_explo=Scale(Frame_Ana, from_=self.min_explo_area, variable=self.Explo_size_squares_scale, to=(cv2.contourArea(self.Arena_pts)*scale_mm2), resolution=0.05, orient=HORIZONTAL)
        Squares_explo.grid(row=1, column=1, sticky="nsew")

        #Or writing directly in the Entry box
        verif_E_float = (self.register(self.update_area_val), '%P', '%V')
        Squares_explo_entry=Entry(Frame_Ana,textvariable=self.Explo_size_squares, width=10, validate="all", validatecommand=verif_E_float, background="grey80")
        Squares_explo_entry.grid(row=1,column=2, sticky="se")

        self.Explo_size_squares.trace("w", self.show_explored)

        Squares_explo_units=Label(Frame_Ana, text=str(self.main.Vid.Scale[1])+"\u00b2")
        Squares_explo_units.grid(row=1, column=3, sticky="sw")

        #Result variable
        self.Prop_explored=DoubleVar()

        Frame_res = Frame(self.Frame_user)
        Frame_res.grid(row=3, column=0)

        self.type_res=StringVar()
        self.type_res.set(self.Messages["Analyses_details_exp_Lab1"])
        Show_res_lab=Label(Frame_res, textvariable=self.type_res)
        Show_res_lab.grid(row=0, column=0, sticky="nsew")

        Show_res=Label(Frame_res, textvariable=self.Prop_explored)
        Show_res.grid(row=0, column=1, sticky="w")

        self.Quit_button = Button(self.Frame_user, text=self.Messages["Analyses_details_sp_B3"], command=self.close, background="#6AED35")
        self.Quit_button.grid(row=5, column=0, columnspan=2, sticky="sew")

        self.ready = True
        self.stay_on_top()
        self.show_explored()
        self.parent.protocol("WM_DELETE_WINDOW", self.close)



    def show_explored(self, *arg):
        #Update the value result
        if self.Explo_size_squares.get()!="":
            if self.shape_mesh.get()==0:
                self.draw_mod()
            if (float(self.Explo_size_squares.get())*float(self.main.Vid.Scale[0]))>=(self.min_explo_area*float(self.main.Vid.Scale[0])-1):
                self.Explo_size_squares_scale.set(self.Explo_size_squares.get())
                if self.shape_mesh.get() == 1:
                    self.draw_squares()
                elif self.shape_mesh.get() == 2:
                    self.draw_circles()
            self.show_img()


    def draw_mod(self):
        #Draw a red path where the target traveled, this path width is determined by user. In the end, we will calculate the proportion of arena pixels being part of this path.
        self.param_p_explo.grid_forget()
        self.type_res.set(self.Messages["Analyses_details_exp_Lab1"])
        radius=math.sqrt((float(self.Explo_size_squares.get()))/math.pi)
        self.image=np.copy(self.image_clean)
        empty=np.zeros((self.image.shape[0],self.image.shape[1],1), np.uint8)

        last_pt=["NA","NA"]
        if radius > 0:
            for pt in self.main.Coos[self.Ind]:
                if pt[0]!="NA" and last_pt[0]!="NA" and pt[0]!=-1000 and last_pt[0]!=-1000:
                    cv2.line(empty, (int(float(last_pt[0])), int(float(last_pt[1]))),
                             (int(float(pt[0])), int(float(pt[1]))), (1), max(1,int(radius * float(self.main.Vid.Scale[0])))*2)
                elif pt[0]!="NA":
                    cv2.circle(empty,(int(float(pt[0])),int(float(pt[1]))),int(radius*float(self.main.Vid.Scale[0])),(1),-1)
                last_pt=pt

        mask = np.zeros([self.image.shape[0], self.image.shape[1], 1], np.uint8)
        mask=cv2.drawContours(mask, [self.Arena_pts], -1,(255),-1)
        empty=cv2.bitwise_and(mask, empty)

        self.Prop_explored.set(round(len(np.where(empty > [0])[0])/len(np.where(mask == [255])[0]),3))
        bool_mask = empty.astype(bool)
        empty=cv2.cvtColor(empty, cv2.COLOR_GRAY2RGB)
        empty[:,:,0]=empty[:,:,0]*255

        alpha=0.5
        self.image[bool_mask] = cv2.addWeighted(self.image, alpha, empty, 1 - alpha, 0)[bool_mask]


    def draw_squares(self):
        #We draw a rectangular mesh on the top of the arena and color the cells according to the proportion of time the target spent in each of them
        #We also set the number of visited cell as the result to be shown
        self.param_p_explo.grid_forget()
        self.type_res.set(self.Messages["Analyses_details_exp_Lab2"])

        self.image = np.copy(self.image_clean)
        No_NA_Coos = np.array(self.main.Coos[self.Ind])
        No_NA_Coos = No_NA_Coos[np.all(No_NA_Coos != -1000, axis=1)]
        No_NA_Coos = No_NA_Coos.astype('float')

        largeur = math.sqrt(float(self.Explo_size_squares.get()) * float(self.main.Vid.Scale[0]) ** 2)
        nb_squares_v = math.ceil((max(self.Arena_pts[:, :, 0]) - min(self.Arena_pts[:, :, 0])) / largeur)
        nb_squares_h = math.ceil((max(self.Arena_pts[:, :, 1]) - min(self.Arena_pts[:, :, 1])) / largeur)

        max_x = min(self.Arena_pts[:, :, 0]) + nb_squares_v * (largeur)
        max_y = min(self.Arena_pts[:, :, 1]) + nb_squares_h * (largeur)

        decal_x = (max_x - max(self.Arena_pts[:, :, 0])) / 2
        decal_y = (max_y - max(self.Arena_pts[:, :, 1])) / 2

        colors = np.array([[255] * 128 + [255] * 128 + list(reversed(range(256))),
                           [255] * 128 + list(reversed(range(0, 256, 2))) + [0] * 256,
                           list(reversed(range(0, 256, 2))) + [0] * 128 + [0] * 256], dtype=int).T

        if len(No_NA_Coos)>0:

            Xs = (np.floor((No_NA_Coos[:, 0] - (min(self.Arena_pts[:, :, 0]) - decal_x)) / largeur))
            Ys = (np.floor((No_NA_Coos[:, 1] - (min(self.Arena_pts[:, :, 1]) - decal_y)) / largeur))

            XYs = np.array(list(zip(Xs, Ys)))
            unique, count = np.unique(XYs, axis=0, return_counts=True)
            self.Prop_explored.set(len(unique))
            self.image = cv2.rectangle(self.image, pt1=(int(min(self.Arena_pts[:, :, 0]) - decal_x),int(min(self.Arena_pts[:, :, 1])-decal_y)), pt2=(int(min(self.Arena_pts[:, :, 0])- decal_x +largeur*nb_squares_v), int(min(self.Arena_pts[:, :, 1])- decal_y+largeur*nb_squares_h)), color=[int(c) for c in colors[0]], thickness=-1)

            for square in range(len(count)):
                color = colors[int(round((count[square]/sum(count))*(len(colors)-1)))]
                self.image = cv2.rectangle(self.image, pt1=(
                    int(min(self.Arena_pts[:, :, 0]) - decal_x + unique[square][0] * (largeur)),
                    int(min(self.Arena_pts[:, :, 1]) - decal_y + unique[square][1] * (largeur))),
                                           pt2=(int(min(self.Arena_pts[:, :, 0]) - decal_x + (unique[square][0] + 1) * (
                                               largeur)),
                                                int(min(self.Arena_pts[:, :, 1]) - decal_y + (unique[square][1] + 1) * (
                                                    largeur))),
                                           color=[int(c) for c in color], thickness=-1)

        else:
            self.Prop_explored.set("NA")

        for vert in range(nb_squares_v + 1):
            self.image = cv2.line(self.image, pt1=(int(min(self.Arena_pts[:, :, 0]) - decal_x + vert * (largeur)),
                                                   int(min(self.Arena_pts[:, :, 1]) - decal_y)), pt2=(
            int(min(self.Arena_pts[:, :, 0]) - decal_x + vert * (largeur)),
            int(max(self.Arena_pts[:, :, 1]) + decal_y)), color=(0, 0, 0), thickness=2)

        for horz in range(nb_squares_h + 1):
            self.image = cv2.line(self.image, pt1=(int(min(self.Arena_pts[:, :, 0]) - decal_x),
                                                   int(min(self.Arena_pts[:, :, 1]) - decal_y + horz * (largeur))),
                                  pt2=(int(max(self.Arena_pts[:, :, 0]) + decal_x),
                                       int(min(self.Arena_pts[:, :, 1]) - decal_y + horz * (largeur))),
                                  color=(0, 0, 0),
                                  thickness=2)

        self.image[(50) : (self.image.shape[0]-50), (self.image.shape[1] - 75):(self.image.shape[1])]=(150,150,150)

        for raw in range(self.image.shape[0]-150):
            color=colors[int((raw/(self.image.shape[0]-150))*(len(colors)-1))]
            self.image[self.image.shape[0]-75-raw,(self.image.shape[1]-65):(self.image.shape[1]-45)]=color

        self.image=cv2.putText(self.image,"100%",(self.image.shape[1]-43,75), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4,color=(0, 0, 0), thickness=1)
        self.image = cv2.putText(self.image, "50%", (self.image.shape[1] - 43, int(self.image.shape[0]/2)), cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.4, color=(0, 0, 0), thickness=1)
        self.image=cv2.putText(self.image, "0%", (self.image.shape[1]-43, self.image.shape[0] - 75), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4,color=(0, 0, 0), thickness=1)



    def draw_circles(self, *arg):
        #We draw a circular mesh on the top of the arena and color the cells according to the proportion of time the target spent in each of them
        #We also set the number of visited cell as the result to be shown
        #The calculation used come from the paper: Beckers, B., & Beckers, P. (2012). A general rule for disk and hemisphere partition into equal-area cells. Computational Geometry, 45(7), 275-283.
        self.param_p_explo.grid(row=4, column=0, columnspan=3, sticky="nsew")
        self.type_res.set(self.Messages["Analyses_details_exp_Lab2"])

        self.image = np.copy(self.image_clean)
        No_NA_Coos = np.asarray(self.main.Coos[self.Ind])
        No_NA_Coos = No_NA_Coos[np.all(No_NA_Coos != -1000, axis=1)]
        No_NA_Coos = No_NA_Coos.astype('float')

        M=cv2.moments(self.Arena_pts)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        max_size=max(list(np.sqrt((self.Arena_pts[:,:, 0] - cX) ** 2 + (self.Arena_pts[:,:, 1] - cY) ** 2)))

        last_rad = math.sqrt((float(self.Explo_size_squares.get()) * float(self.main.Vid.Scale[0])**2)/math.pi)
        last_nb = 1

        list_rads=[last_rad]
        list_nb=[1]
        list_angles=[[0]]

        while last_rad< max_size:
            new_rad= ((math.sqrt(last_nb)+math.sqrt(self.param_p.get()**2))/math.sqrt(last_nb)) * last_rad
            new_nb = int(round((math.sqrt(last_nb) + math.sqrt(self.param_p.get()**2))**2))
            cur_nb=new_nb-last_nb

            list_nb.append(cur_nb)

            one_angle=(2*math.pi)/cur_nb
            cur_angle=0
            tmp_angles=[0]
            for angle in range(cur_nb):
                cur_angle += one_angle
                tmp_angles.append(cur_angle)


            list_angles.append(tmp_angles)
            list_rads.append(new_rad)

            last_rad = new_rad
            last_nb=new_nb

        if len(No_NA_Coos)>0:
            #We summarise the position of the individual:
            Dists=list(np.sqrt((No_NA_Coos[:,0]-cX)**2 + (No_NA_Coos[:,1]-cY)**2))
            Circles=([np.argmax(list_rads>dist) for dist in Dists])#In which circle
            Angles= np.arctan2((No_NA_Coos[:,1]-cY),(No_NA_Coos[:,0]-cX))
            liste_angles_per_I=list(itemgetter(*Circles)(list_angles))
            Portions=([np.argmax(liste_angles_per_I[idx]>=(angle+math.pi)) for idx,angle in enumerate(Angles)])#In which portion

            Pos=np.array(list(zip(Circles,Portions)))

            unique, count=np.unique(Pos, axis=0, return_counts=True)#On regarde ou la bete est et combien de fois
            self.Prop_explored.set(len(unique))

            colors=np.array([[255]*128 + [255]*128 + list(reversed(range(256))),[255]*128 + list(reversed(range(0,256,2)))+ [0]*256,list(reversed(range(0,256,2)))+[0]*128 +[0]*256], dtype=int).T

            self.image = cv2.circle(self.image, (cX, cY), int(last_rad), [int(c) for c in colors[0]], -1)

            for square in range(len(unique)):
                color = colors[int(round((count[square]/sum(count))*(len(colors)-1)))]
                if unique[square][0]==0:
                    self.image = cv2.circle(self.image, (cX, cY), (int(list_rads[unique[square][0]])), color=[int(c) for c in color], thickness=-1)
                else:
                    diameters=[int(list_rads[unique[square][0]]),int(list_rads[unique[square][0]-1])]
                    first_angle = 180+((list_angles[unique[square][0]][unique[square][1]])*180/math.pi)
                    sec_angle = 180+((list_angles[unique[square][0]][unique[square][1]-1])*180/math.pi)

                    empty_img= np.zeros([self.image.shape[0], self.image.shape[1], 1], np.uint8)
                    empty_img=cv2.ellipse(empty_img, (cX,cY), (diameters[0],diameters[0]), 0, startAngle=first_angle+1, endAngle=sec_angle-1, color=255, thickness=1)
                    empty_img = cv2.ellipse(empty_img, (cX, cY), (diameters[1], diameters[1]), 0,startAngle=first_angle+1, endAngle=sec_angle-1, color=255, thickness=1)

                    pt1=(int(cX + math.cos((first_angle)/180*math.pi)*(diameters[0]+2)),int(cY + math.sin(first_angle/180*math.pi) * (diameters[0]+2)))
                    pt2 = (int(cX + math.cos((first_angle)/180*math.pi) * (diameters[1]-2)), int(cY + math.sin(first_angle/180*math.pi) * (diameters[1]-2)))
                    empty_img=cv2.line(empty_img,pt1,pt2,255,1)#We draw the limits

                    pt1=(int(cX + math.cos((sec_angle)/180*math.pi)*(diameters[0]+2)),int(cY + math.sin(sec_angle/180*math.pi) * (diameters[0]+2)))
                    pt2 = (int(cX + math.cos(sec_angle/180*math.pi) * (diameters[1]-2)), int(cY + math.sin(sec_angle/180*math.pi) * (diameters[1]-2)))
                    empty_img=cv2.line(empty_img,pt1,pt2,255,1)#We draw the limits
                    empty_img = cv2.rectangle(empty_img, (0, 0), (self.image.shape[1], self.image.shape[0]), color=255,thickness=1)#If the shape is bigger than image


                    cnts, h = cv2.findContours(empty_img, cv2.RETR_CCOMP , cv2.CHAIN_APPROX_SIMPLE)
                    cnts=[cnts[i] for i in range(len(cnts)) if h[0][i][3] >= 0]
                    self.image=cv2.drawContours(self.image,cnts,-1,[int(c) for c in color],-1)


        for circle in range(len(list_rads)):
            self.image = cv2.circle(self.image, (cX, cY), int(list_rads[circle]), (0, 0, 0), 2)
            if circle>0:
                for cur_angle in list_angles[circle]:
                    pt1=(int(cX + math.cos(math.pi+cur_angle)*list_rads[circle-1]),int(cY + math.sin(math.pi+cur_angle) * list_rads[circle-1]))
                    pt2 = (int(cX + math.cos(math.pi+cur_angle) * list_rads[circle]), int(cY + math.sin(math.pi+cur_angle) * list_rads[circle]))
                    self.image=cv2.line(self.image,pt1,pt2,(0,0,0),2)#We draw the limits
        self.image = cv2.circle(self.image, (cX, cY), int(last_rad), (0, 0, 0), 2)



        self.image[(50) : (self.image.shape[0]-50), (self.image.shape[1] - 75):(self.image.shape[1])]=(150,150,150)

        for raw in range(self.image.shape[0]-150):
            color=colors[int((raw/(self.image.shape[0]-150))*(len(colors)-1))]
            self.image[self.image.shape[0]-75-raw,(self.image.shape[1]-65):(self.image.shape[1]-45)]=color

        self.image=cv2.putText(self.image,"100%",(self.image.shape[1]-43,75), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4,color=(0, 0, 0), thickness=1)
        self.image = cv2.putText(self.image, "50%", (self.image.shape[1] - 43, int(self.image.shape[0] / 2)),
                                 cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=(0, 0, 0), thickness=1)

        self.image=cv2.putText(self.image, "0%", (self.image.shape[1]-43, self.image.shape[0] - 75), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4,color=(0, 0, 0), thickness=1)

    def close(self):
        #Close properly this window
        self.main.Infos_explo = [self.shape_mesh.get(), self.Explo_size_squares.get(), self.param_p.get()]
        self.unbind_all("<Return>")
        self.main.modif_image()
        self.parent.destroy()

    def on_frame_conf(self, *arg):
        self.Liste_analyses.configure(scrollregion=self.Liste_analyses.bbox("all"))

    def update_area(self):
        #When we change the target of interest, we look for the new arena and save its contours
        place = 0
        self.Area = None
        selected=list(self.List_inds_names.values()).index(self.Ind_name.get())
        for Ar in range(len(self.main.Vid.Track[1][6])):
            for Ind in range(self.main.Vid.Track[1][6][Ar]):
                if selected==place:
                    self.Area=Ar
                place+=1

        mask = Function_draw_mask.draw_mask(self.main.Vid)
        Arenas, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        Arenas = Function_draw_mask.Organise_Ars(Arenas)
        self.Arena_pts = Arenas[self.Area]

        if len(self.main.Vid.Analyses[4][0])>0:
            self.Arena_pts=self.Arena_pts[:, 0, :]
            self.Arena_pts = np.array([self.Arena_pts], dtype=np.float32)
            self.Arena_pts = cv2.perspectiveTransform(self.Arena_pts, self.main.Vid.Analyses[4][0])
            self.Arena_pts=cv2.convexHull(self.Arena_pts.astype(np.int32))

    def load_img(self,*args):
        #Load the image to be displayed
        self.Ind = list(self.List_inds_names.values()).index(self.Ind_name.get())
        self.update_area()

        self.image_clean1=self.main.img_no_shapes
        mask=np.zeros([self.image_clean1.shape[0], self.image_clean1.shape[1], 1], np.uint8)
        mask=cv2.drawContours(mask, [self.Arena_pts], -1,(255,255,255),-1)

        self.image_clean_trans=cv2.bitwise_and(self.image_clean1, self.image_clean1, mask=mask)
        blend=0.5
        self.image_clean=cv2.addWeighted(self.image_clean1, blend, self.image_clean_trans, 1 - blend, 0)

        self.image=np.copy(self.image_clean)
        self.Size=self.image.shape
        self.ratio = self.Size[1] / self.final_width
        self.zoom_sq = [0, 0, self.image.shape[1], self.image.shape[0]]
        self.show_img()

    def show_img(self, *args):
        #Resize the image and display it in the canvas dedicated
        best_ratio = max(self.Size[1] / (self.Canvas_for_video.winfo_width()),
                         self.Size[0] / (self.Canvas_for_video.winfo_height()))
        prev_final_width = self.final_width
        self.final_width = int(math.ceil(self.Size[1] / best_ratio))
        self.ratio = self.ratio * (prev_final_width / self.final_width)
        image_to_show = self.image[self.zoom_sq[1]:self.zoom_sq[3], self.zoom_sq[0]:self.zoom_sq[2]]
        image_to_show1 = cv2.resize(image_to_show,(self.final_width, int(self.final_width * (self.Size[0] / self.Size[1]))))
        self.image_to_show2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(image_to_show1))
        self.Canvas_for_video.create_image(0, 0, image=self.image_to_show2, anchor=NW)
        self.Canvas_for_video.config(width=self.final_width, height=int(self.final_width * (self.Size[0] / self.Size[1])))



    def change_ind(self, *arg):
        #Change the target of interest
        self.main.highlight = list(self.List_inds_names.keys())[list(self.List_inds_names.values()).index(self.Ind_name.get())]
        self.Ind = list(self.List_inds_names.values()).index(self.Ind_name.get())
        self.update_area()
        self.main.modif_image()
        self.load_img()
        self.show_explored()

    def stay_on_top(self):
        #We want this window to be always on top of the others
        if self.ready:
            self.parent.lift()
            self.change_image()
        self.parent.after(50, self.stay_on_top)

    def change_image(self):
        #If the displayed image is changed, display it
        cur_pos=self.main.Scrollbar.active_pos- int(round((self.main.Vid.Cropped[1][0])/self.main.one_every))
        if cur_pos!=self.last_cur_pos:
            self.load_img()
            self.show_explored()
        self.last_cur_pos=cur_pos


    def Zoom_in(self, event):
        #Zoom in the image
        self.new_zoom_sq = [0, 0, 0, 0]
        PX = event.x / ((self.zoom_sq[2] - self.zoom_sq[0]) / self.ratio)
        PY = event.y / ((self.zoom_sq[3] - self.zoom_sq[1]) / self.ratio)

        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]
        ZWX = (self.zoom_sq[2] - self.zoom_sq[0]) * (1 - self.zoom_strength)
        ZWY = (self.zoom_sq[3] - self.zoom_sq[1]) * (1 - self.zoom_strength)

        if ZWX > 100:
            self.new_zoom_sq[0] = int(event.x - PX * ZWX)
            self.new_zoom_sq[2] = int(event.x + (1 - PX) * ZWX)
            self.new_zoom_sq[1] = int(event.y - PY * ZWY)
            self.new_zoom_sq[3] = int(event.y + (1 - PY) * ZWY)

            self.ratio = ZWX / self.final_width
            self.zoom_sq = self.new_zoom_sq
            self.zooming = True
            self.show_img()

    def Zoom_out(self, event):
        # Zoom out the image
        self.new_zoom_sq = [0, 0, 0, 0]
        PX = event.x / ((self.zoom_sq[2] - self.zoom_sq[0]) / self.ratio)
        PY = event.y / ((self.zoom_sq[3] - self.zoom_sq[1]) / self.ratio)

        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]

        ZWX = (self.zoom_sq[2] - self.zoom_sq[0]) * (1 + self.zoom_strength)
        ZWY = (self.zoom_sq[3] - self.zoom_sq[1]) * (1 + self.zoom_strength)

        if ZWX < self.Size[1] and ZWY < self.Size[0]:
            if int(event.x - PX * ZWX) >= 0 and int(event.x + (1 - PX) * ZWX) <= self.Size[1]:
                self.new_zoom_sq[0] = int(event.x - PX * ZWX)
                self.new_zoom_sq[2] = int(event.x + (1 - PX) * ZWX)
            elif int(event.x + (1 - PX) * ZWX) > self.Size[1]:
                self.new_zoom_sq[0] = int(self.Size[1] - ZWX)
                self.new_zoom_sq[2] = int(self.Size[1])
            elif int(event.x - PX * ZWX) < 0:
                self.new_zoom_sq[0] = 0
                self.new_zoom_sq[2] = int(ZWX)

            if int(event.y - PY * ZWY) >= 0 and int(event.y + (1 - PY) * ZWY) <= self.Size[0]:
                self.new_zoom_sq[1] = int(event.y - PY * ZWY)
                self.new_zoom_sq[3] = self.new_zoom_sq[1] + int(ZWY)

            elif int(event.y + (1 - PY) * ZWY) > self.Size[0]:
                self.new_zoom_sq[1] = int(self.Size[0] - ZWY)
                self.new_zoom_sq[3] = int(self.Size[0])
            elif int(event.y - PY * ZWY) < 0:
                self.new_zoom_sq[1] = 0
                self.new_zoom_sq[3] = int(ZWY)
            self.ratio = ZWX / self.final_width


        else:
            self.new_zoom_sq = [0, 0, self.image.shape[1], self.image.shape[0]]
            self.ratio = self.Size[1] / self.final_width

        self.zoom_sq = self.new_zoom_sq
        self.zooming = False
        self.show_img()

    def update_area_val(self, new_val, method):
        # Avoid user to writting non numerical values in the Entry box
        if new_val == "" and method != "focusout":
            return True
        elif new_val != "":
            try:
                new_val = float(new_val)
                return True
            except Exception as e:
                print(e)
                return False
        else:
            return False

class Details_inter(Frame):
    def __init__(self, parent, main, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.parent.geometry("1050x620")
        self.main=main
        self.grid(sticky="nsew")
        Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW
        self.ready=False
        self.parent.attributes('-toolwindow', True)

        #Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Analyses_details_T"])

        self.final_width = 250
        self.zoom_strength = 0.3
        self.last_cur_pos = self.main.Scrollbar.active_pos - int(round((self.main.Vid.Cropped[1][0]) / self.main.one_every))

        #We create an optionmenu to allow the user to select the arena of interest
        self.List_inds_names = dict()
        for ind in range(len(self.main.Vid.Identities)):
            self.List_inds_names["Ind"+str(ind)]=self.Messages["Arena_short"]+ "{}, ".format(self.main.Vid.Identities[ind][0])+ self.Messages["Individual_short"] +" {}".format(self.main.Vid.Identities[ind][1])

        self.Ind_name=StringVar()
        self.Ind_name.set(self.Messages["Arena_short"]+ "{}, ".format(self.main.Vid.Identities[0][0])+ self.Messages["Individual_short"] +" {}".format(self.main.Vid.Identities[0][1]))

        self.Which_ind = OptionMenu(self, self.Ind_name, *self.List_inds_names.values(), command=self.change_ind)
        self.Which_ind.grid(row=0, column=0, )

        #organization of the Frame
        self.Canvas_for_video = Canvas(self, width=700, height=500, bd=0, highlightthickness=0)
        self.Canvas_for_video.grid(row=1, column=0, sticky="nsew")
        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.columnconfigure(self, 1, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=1)  ########NEW
        self.Canvas_for_video.update()
        self.Dist_soc = StringVar(value=self.main.Infos_inter)
        self.load_img()

        self.Canvas_for_video.bind("<Control-1>", self.Zoom_in)
        self.Canvas_for_video.bind("<Control-3>", self.Zoom_out)
        self.Canvas_for_video.bind("<Configure>", self.show_img)

        self.Frame_user = Frame(self, width=150)
        self.Frame_user.grid(row=0, column=1, rowspan=2, sticky="nsew")
        Grid.columnconfigure(self.Frame_user, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.Frame_user, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.Frame_user, 1, weight=1)  ########NEW
        Grid.rowconfigure(self.Frame_user, 2, weight=100)  ########NEW


        # Help user and parameters
        self.HW = User_help.Help_win(self.Frame_user, default_message=self.Messages["Analyses_details_inter0"])
        self.HW.grid(row=0, column=0, sticky="nsew")

        Frame_Ana = Frame(self.Frame_user)
        Frame_Ana.grid(row=2, column=0, columnspan=2, sticky="nsew")
        Grid.columnconfigure(Frame_Ana, 0, weight=1)  ########NEW
        Grid.rowconfigure(Frame_Ana, 0, weight=1)  ########NEW


        #allow the user to choose the threshold distance between two targets to consider that they are close
        Squares_explo = Label(Frame_Ana, text=self.Messages["Analyses_details_inter_Lab1"])
        Squares_explo.grid(row=1, column=0, sticky="se")

        Squares_explo = Scale(Frame_Ana, from_=0.01, variable=self.Dist_soc,to=math.sqrt((((max(cv2.minAreaRect(self.Arena_pts)[1]) / float(self.main.Vid.Scale[0])) ** 2))/math.pi),
                              resolution=0.05, orient=HORIZONTAL)
        Squares_explo.grid(row=1, column=1, sticky="nsew")

        verif_E_float = (self.register(self.update_area_val), '%P', '%V')
        Squares_explo_entry = Entry(Frame_Ana, textvariable=self.Dist_soc, width=10, validate="all",
                                    validatecommand=verif_E_float, background="grey80")
        Squares_explo_entry.grid(row=1, column=2, sticky="se")
        self.Dist_soc.trace("w", self.dist_soc_updated)

        Squares_explo_units = Label(Frame_Ana, text=str(self.main.Vid.Scale[1]))
        Squares_explo_units.grid(row=1, column=3, sticky="sw")

        #Show the results:
        Frame_res = Frame(self.Frame_user)
        Frame_res.grid(row=3, column=0, columnspan=2, sticky="nsew")

        self.Nb_nei=StringVar()
        self.Prop_time_nei=StringVar()
        self.Min_dist_nei = StringVar()

        #Averagee number of neighbors
        Show_res_lab=Label(Frame_res, text=self.Messages["Analyses_details_inter_Lab2"])
        Show_res_lab.grid(row=0, column=0, sticky="nsew")
        Show_res=Label(Frame_res, textvariable=self.Nb_nei)
        Show_res.grid(row=0, column=1, sticky="w")

        #Proportion of time with at least one neighbor
        Show_res2_lab = Label(Frame_res, text=self.Messages["Analyses_details_inter_Lab3"])
        Show_res2_lab.grid(row=1, column=0, sticky="nsew")
        Show_res2 = Label(Frame_res, textvariable=self.Prop_time_nei)
        Show_res2.grid(row=1, column=1, sticky="w")

        #Average distance to the closest neighbor
        Show_res3_lab = Label(Frame_res, text=self.Messages["Analyses_details_inter_Lab4"])
        Show_res3_lab.grid(row=2, column=0, sticky="nsew")
        Show_res3 = Label(Frame_res, textvariable=self.Min_dist_nei)
        Show_res3.grid(row=2, column=1, sticky="w")
        Show_res_unit3 = Label(Frame_res, text=self.main.Vid.Scale[1])
        Show_res_unit3.grid(row=2, column=2, sticky="w")

        self.Quit_button = Button(self.Frame_user, text=self.Messages["Analyses_details_sp_B3"], command=self.close, background="#6AED35")
        self.Quit_button.grid(row=5, column=0, sticky="sew")

        self.ready = True
        self.stay_on_top()
        self.parent.protocol("WM_DELETE_WINDOW", self.close)

        self.show_soc()


    def dist_soc_updated(self, *args):
        #Avoid a but if the user wat typing in the Entrybox
        if not self.Dist_soc.get()=="":
            self.show_soc()

    def show_soc(self, *args):
        #Recalculate the results values and display them

        # Extract the coordinates of interest (i.e. of targets that are associated to the considered arena)
        Pts_coos = []
        if self.Area>0:
            nb_prev=sum([self.main.Vid.Track[1][6][Ar] for Ar in range(0,self.Area)])
        else:
            nb_prev=0
        for fish in range(self.main.Vid.Track[1][6][self.Area]):
            Pts_coos.append(self.main.Coos[fish + nb_prev])

        #Calculate the values
        avg_nb_nei, prop_with_nei, min_dist_nei, sum_dists=self.main.Calc_speed.calculate_nei(Pts_coos = Pts_coos, ind=int(self.Ind)-nb_prev, dist=self.Dist_soc.get(), Scale = float(self.main.Vid.Scale[0]), Fr_rate=self.main.Vid.Frame_rate[1])

        #Show them to user
        self.Nb_nei.set(round(avg_nb_nei,3))
        self.Prop_time_nei.set(round(prop_with_nei,3))
        self.Min_dist_nei.set(round(min_dist_nei/self.main.Vid.Scale[0],3))
        self.show_img()

    def close(self):
        #properly close the parent window
        self.main.Infos_inter = self.Dist_soc.get()
        self.unbind_all("<Return>")
        self.main.modif_image()
        self.parent.destroy()

    def on_frame_conf(self, *arg):
        #We resize the canvas in a way it always fit the window
        self.Liste_analyses.configure(scrollregion=self.Liste_analyses.bbox("all"))

    def update_area(self):
        #When the user change the target of interest, this function look for which arena is associated to the target and take the contour of the arena
        place = 0
        self.Area = None
        selected = list(self.List_inds_names.values()).index(self.Ind_name.get())
        for Ar in range(len(self.main.Vid.Track[1][6])):
            for Ind in range(self.main.Vid.Track[1][6][Ar]):
                if selected == place:
                    self.Area = Ar
                place += 1

        mask = Function_draw_mask.draw_mask(self.main.Vid)
        Arenas, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        Arenas = Function_draw_mask.Organise_Ars(Arenas)
        self.Arena_pts = Arenas[self.Area]

    def load_img(self, *args):
        #Load the image and hilight the position of the current arena
        self.Ind = list(self.List_inds_names.values()).index(self.Ind_name.get())
        self.update_area()

        #Create mask (everything black except the inside of the arena)
        self.image_clean1 = self.main.img_no_shapes
        mask = np.zeros([self.image_clean1.shape[0], self.image_clean1.shape[1], 1], np.uint8)
        mask = cv2.drawContours(mask, [self.Arena_pts], -1, (255, 255, 255), -1)
        mask = Functions_deformation.transform(mask, self.main.Vid.Analyses[4][1], self.main.Vid.Analyses[4][2])

        #Application of the mask so it appears as a black veil everywhere except where the arena is
        self.image_clean_trans = cv2.bitwise_and(self.image_clean1, self.image_clean1, mask=mask)
        blend = 0.5
        self.image_clean = cv2.addWeighted(self.image_clean1, blend, self.image_clean_trans, 1 - blend, 0)

        self.image = np.copy(self.image_clean)

        # Info for zoom in/out
        self.Size = self.image.shape
        self.ratio = self.Size[1] / self.final_width
        self.zoom_sq = [0, 0, self.image.shape[1], self.image.shape[0]]
        self.show_img()

    def show_img(self, *args):
        #Display the image
        try:
            if self.main.Scrollbar.active_pos >= round(((self.main.Vid.Cropped[1][0]) / self.main.Vid_Lecteur.one_every)) and self.main.Scrollbar.active_pos <= int(round((self.main.Vid.Cropped[1][1]) / self.main.Vid_Lecteur.one_every)) and self.main.Coos[self.Ind][self.last_cur_pos][0]!="NA":
                overlay = np.copy(self.image_clean)
                cv2.circle(overlay, (int(float(self.main.Coos[self.Ind][self.last_cur_pos][0])), int(float(self.main.Coos[self.Ind][self.last_cur_pos][1]))),int(float(self.Dist_soc.get()) * float(self.main.Vid.Scale[0])), (255, 0, 0), -1)
                self.image = cv2.addWeighted(self.image_clean, 0.5, overlay, 0.5, 0)
            else:
                self.image = np.copy(self.image_clean)

            best_ratio = max(self.Size[1] / (self.Canvas_for_video.winfo_width()),
                             self.Size[0] / (self.Canvas_for_video.winfo_height()))
            prev_final_width = self.final_width
            self.final_width = int(math.ceil(self.Size[1] / best_ratio))
            self.ratio = self.ratio * (prev_final_width / self.final_width)
            image_to_show = self.image[self.zoom_sq[1]:self.zoom_sq[3], self.zoom_sq[0]:self.zoom_sq[2]]
            image_to_show1 = cv2.resize(image_to_show,
                                        (self.final_width, int(self.final_width * (self.Size[0] / self.Size[1]))))
            self.image_to_show2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(image_to_show1))
            self.Canvas_for_video.create_image(0, 0, image=self.image_to_show2, anchor=NW)
            self.Canvas_for_video.config(width=self.final_width,height=int(self.final_width * (self.Size[0] / self.Size[1])))

        except Exception as e:#Sometime changing the timebar too fast make bugs
            pass

    def change_ind(self, *arg):
        #Change the target of interest
        self.main.highlight = list(self.List_inds_names.keys())[
            list(self.List_inds_names.values()).index(self.Ind_name.get())]
        self.Ind = list(self.List_inds_names.values()).index(self.Ind_name.get())
        self.update_area()
        self.main.modif_image()
        self.load_img()
        self.show_soc()

    def stay_on_top(self):
        #We want the parent windows to always remain at the top.
        if self.ready:
            self.parent.lift()
            self.change_image()
        self.parent.after(50, self.stay_on_top)

    def change_image(self):
        #If the user wants to see the elements of interest drawn over another image from the video
        cur_pos = self.main.Scrollbar.active_pos - int(round((self.main.Vid.Cropped[1][0]) / self.main.one_every))
        if cur_pos != self.last_cur_pos:
            self.last_cur_pos = cur_pos
            self.load_img()

    def Zoom_in(self, event):
        #Zoom in the image
        self.new_zoom_sq = [0, 0, 0, 0]
        PX = event.x / ((self.zoom_sq[2] - self.zoom_sq[0]) / self.ratio)
        PY = event.y / ((self.zoom_sq[3] - self.zoom_sq[1]) / self.ratio)

        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]
        ZWX = (self.zoom_sq[2] - self.zoom_sq[0]) * (1 - self.zoom_strength)
        ZWY = (self.zoom_sq[3] - self.zoom_sq[1]) * (1 - self.zoom_strength)

        if ZWX > 100:
            self.new_zoom_sq[0] = int(event.x - PX * ZWX)
            self.new_zoom_sq[2] = int(event.x + (1 - PX) * ZWX)
            self.new_zoom_sq[1] = int(event.y - PY * ZWY)
            self.new_zoom_sq[3] = int(event.y + (1 - PY) * ZWY)

            self.ratio = ZWX / self.final_width
            self.zoom_sq = self.new_zoom_sq
            self.zooming = True
            self.show_img()

    def Zoom_out(self, event):
        #Zoom out from the image
        self.new_zoom_sq = [0, 0, 0, 0]
        PX = event.x / ((self.zoom_sq[2] - self.zoom_sq[0]) / self.ratio)
        PY = event.y / ((self.zoom_sq[3] - self.zoom_sq[1]) / self.ratio)

        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]

        ZWX = (self.zoom_sq[2] - self.zoom_sq[0]) * (1 + self.zoom_strength)
        ZWY = (self.zoom_sq[3] - self.zoom_sq[1]) * (1 + self.zoom_strength)

        if ZWX < self.Size[1] and ZWY < self.Size[0]:
            if int(event.x - PX * ZWX) >= 0 and int(event.x + (1 - PX) * ZWX) <= self.Size[1]:
                self.new_zoom_sq[0] = int(event.x - PX * ZWX)
                self.new_zoom_sq[2] = int(event.x + (1 - PX) * ZWX)
            elif int(event.x + (1 - PX) * ZWX) > self.Size[1]:
                self.new_zoom_sq[0] = int(self.Size[1] - ZWX)
                self.new_zoom_sq[2] = int(self.Size[1])
            elif int(event.x - PX * ZWX) < 0:
                self.new_zoom_sq[0] = 0
                self.new_zoom_sq[2] = int(ZWX)

            if int(event.y - PY * ZWY) >= 0 and int(event.y + (1 - PY) * ZWY) <= self.Size[0]:
                self.new_zoom_sq[1] = int(event.y - PY * ZWY)
                self.new_zoom_sq[3] = self.new_zoom_sq[1] + int(ZWY)

            elif int(event.y + (1 - PY) * ZWY) > self.Size[0]:
                self.new_zoom_sq[1] = int(self.Size[0] - ZWY)
                self.new_zoom_sq[3] = int(self.Size[0])
            elif int(event.y - PY * ZWY) < 0:
                self.new_zoom_sq[1] = 0
                self.new_zoom_sq[3] = int(ZWY)
            self.ratio = ZWX / self.final_width


        else:
            self.new_zoom_sq = [0, 0, self.image.shape[1], self.image.shape[0]]
            self.ratio = self.Size[1] / self.final_width

        self.zoom_sq = self.new_zoom_sq
        self.zooming = False
        self.show_img()

    def update_area_val(self, new_val, method):
        #Limit user to writing numerical values when writing directly in the Entry box
        if new_val == "" and method != "focusout":
            return True
        elif new_val != "":
            try:
                new_val = float(new_val)
                return True
            except Exception as e:
                print(e)
                return False
        else:
            return False



