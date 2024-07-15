from tkinter import *
from tkinter import ttk
from AnimalTA.A_General_tools import Diverse_functions, UserMessages, User_help, Class_Lecteur, Function_draw_mask, Class_loading_Frame, Color_settings
from AnimalTA.E_Post_tracking import Coos_loader_saver as CoosLS
from AnimalTA.E_Post_tracking.b_Analyses import Interface_extend_seqs, Functions_Analyses_Speed, Functions_deformation
import numpy as np
from functools import partial
import pandas as pd
import cv2


full_sequence = ['General', ['Beg', '0', '', '', ''], ['End', '', '', '', '']]

def find_limits(Sequence, Vid, Ind, relative_explo, Coos=[], boundaries=[]):
    if len(Coos)==0:
        max_len=Vid.Cropped[1][1] - Vid.Cropped[1][0]
    else:
        max_len=len(Coos)-1
    #Debut
    if Sequence[1][0]=="Beg":
        deb=0
    elif Sequence[1][0]=="Time":
        if len(boundaries)==0:
            deb=int((float(Sequence[1][1]) * Vid.Frame_rate[1]))
        else:
            deb=int((float(Sequence[1][1]) * Vid.Frame_rate[1])) - boundaries[0]
    elif Sequence[1][0]=="Explo":
        expl_time = relative_explo[int(int(Sequence[1][4]) / 10)]
        if expl_time != "NA":
            deb = int(expl_time)
        else:
            deb = max_len

    elif Sequence[1][0] == "Spatial":
        for shape in Vid.Analyses[1][Vid.Identities[Ind][0]]:
            if ("First_in_"+str(shape[3]))==Sequence[1][3] or ("Last_in_"+str(shape[3]))==Sequence[1][3]:
                entries,outs=find_shape_relation(shape,Vid,Coos,Ind)
                try:
                    val5 = int(Sequence[1][5])
                except:
                    val5 = -1

                if ("First_in_" + str(shape[3])) == Sequence[1][3]:
                    if val5 > 0 and val5 <= len(entries):
                        new_pos = entries[int(Sequence[1][5])-1]
                    else:
                        new_pos = "NA"
                else:
                    if val5 > 0 and val5 <= len(outs):
                        new_pos = outs[int(Sequence[1][5])-1]
                    else:
                        new_pos = "NA"
            else:
                pass

        if new_pos!="NA":
            try:
                if Sequence[1][2] == "aft":
                    deb = new_pos+int((float(Sequence[1][1]) * Vid.Frame_rate[1]))
                else:
                    deb = new_pos- int((float(Sequence[1][1]) * Vid.Frame_rate[1]))
            except:
                return (False, [])
        else:
            deb=max_len


    if Sequence[2][0]=="End":
        end = max_len
    elif Sequence[2][0]=="Time":

        if len(boundaries)==0:
            end=int((float(Sequence[2][1]) * Vid.Frame_rate[1]))
        else:
            end=int((float(Sequence[2][1]) * Vid.Frame_rate[1])) - boundaries[0]
    elif Sequence[2][0]=="Explo":
        expl_time = relative_explo[int(int(Sequence[2][4]) / 10)]
        if expl_time != "NA":
            end = int(expl_time)
        else:
            end = max_len

    elif Sequence[2][0] == "Spatial":
        for shape in Vid.Analyses[1][Vid.Identities[Ind][0]]:
            if ("First_in_"+str(shape[3]))==Sequence[2][3] or ("Last_in_"+str(shape[3]))==Sequence[2][3]:
                entries,outs=find_shape_relation(shape,Vid,Coos,Ind)

                try:
                    val5=int(Sequence[2][5])
                except:
                    val5=-1

                if ("First_in_" + str(shape[3])) == Sequence[2][3]:
                    if val5>0 and val5<=len(entries):
                        new_pos=entries[int(Sequence[2][5])-1]
                    else:
                        new_pos="NA"
                else :
                    if val5>0 and val5<=len(outs):
                        new_pos=outs[int(Sequence[2][5])-1]
                    else:
                        new_pos="NA"
            else:
                pass
        try:
            if new_pos=="NA":
                end=max_len
            elif Sequence[2][2] == "aft":
                end = new_pos+int((float(Sequence[2][1]) * Vid.Frame_rate[1]))
            else:
                end = new_pos- int((float(Sequence[2][1]) * Vid.Frame_rate[1]))

        except:
            return (False, [])

    #General_verifs:
    if deb < 0:
        deb=0
    if end>max_len:
        end=max_len


    if end<=deb:
        return(False, [])

    else:
        return(True, [deb,end])

def find_shape_relation(Shape, Vid, Coos, ID):
    Copy_Coos = np.array(Coos)

    Calc_speed = Functions_Analyses_Speed.speed_calculations(seuil_movement=Vid.Analyses[0])

    mask = Function_draw_mask.draw_mask(Vid)
    Arenas, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    Arenas = Function_draw_mask.Organise_Ars(Arenas)
    Area=Vid.Identities[ID][0]

    Shape_tmp = Shape.copy()
    if Shape_tmp[0] == "Point":
        Dist_to, Inside = Calc_speed.details_Point(Copy_Coos[:, 0], Copy_Coos[:, 1], Shape_tmp, float(Vid.Scale[0]))

    # WARNING!!!!
    elif Shape_tmp[0] == "All_borders":
        Dist_to, Inside = Calc_speed.details_All_borders(Copy_Coos[:, 0], Copy_Coos[:, 1], Shape_tmp, Arenas[Area], float(Vid.Scale[0]))

    elif Shape_tmp[0] == "Borders":
        Dist_to, Inside = Calc_speed.details_Borders(Copy_Coos[:, 0], Copy_Coos[:, 1], Shape_tmp, float(Vid.Scale[0]))

    elif Shape_tmp[0] == "Ellipse" or Shape_tmp[0] == "Rectangle" or Shape_tmp[0] == "Polygon":
        Dist_to, Inside = Calc_speed.details_shape(Copy_Coos[:, 0], Copy_Coos[:, 1], Shape_tmp, float(Vid.Scale[0]), Vid, Arenas[Area])

    if len(np.where(Inside > 0)[0]) > 0:
        filled_Inside = pd.Series(Inside).ffill().to_numpy()
        diff=np.diff(filled_Inside)
        entries=np.where(diff>0.5)[0]+1
        if Inside[np.argmax(~np.isnan(Inside))]>0:
            entries = np.insert(entries, 0, 0, 0)
        outs = np.where(diff< -0.5)[0]
        return([list(entries),list(outs)])
    else:
        return(["NA","NA"])


def compute_explo(method, Vid, Coos, ID, loading_parent):
    load_frame = Class_loading_Frame.Loading(loading_parent)  # Progression bar
    load_frame.grid()
    load_frame.show_load(0)
    Copy_Coos = np.array(Coos)
    relative_explo = []

    mask = Function_draw_mask.draw_mask(Vid)
    Arenas, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    Arenas = Function_draw_mask.Organise_Ars(Arenas)
    Area=Vid.Identities[ID][0]

    expo_res_end = Functions_Analyses_Speed.calculate_exploration(method=method, Vid=Vid,Coos=Copy_Coos,deb=0,end=len(Copy_Coos)-1,Arena=Arenas[Area])
    expo_res_deb = Functions_Analyses_Speed.calculate_exploration(method=method, Vid=Vid,Coos=Copy_Coos,deb=0,end=0,Arena=Arenas[Area])
    summary = np.array([[expo_res_deb[1], 0], [expo_res_end[1], len(Copy_Coos)-1]])

    for val_explo in np.arange(1, -0.1, -0.1):
        val_explo=round(val_explo,3)
        load_frame.show_load(1-val_explo)
        if expo_res_end[1] < val_explo:
            relative_explo.append("NA")
        elif expo_res_deb[1] >= val_explo:
            relative_explo.append(0)
        else:
            found = False

            while not found:
                closest_low = summary[np.where(summary[:, 0] < val_explo)[0][-1]]
                closest_high = summary[np.where(summary[:, 0] >= val_explo)[0][-1]]

                if closest_high[1] - closest_low[1] != 1:
                    expo_res = Functions_Analyses_Speed.calculate_exploration(method=method,Vid=Vid,Coos=Copy_Coos,deb=0,end=int((closest_high[1] + closest_low[1]) / 2),Arena=Arenas[Area])
                    summary = np.vstack([summary, [expo_res[1], int((closest_high[1] + closest_low[1]) / 2)]])
                else:
                    relative_explo.append(closest_high[1])
                    found = True

    relative_explo.reverse()
    load_frame.destroy()
    return(relative_explo)

class Add_sequences(Frame):
    def __init__(self, parent, main, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base)
        self.parent=parent
        self.parent.geometry("1050x620")
        self.main=main
        self.Vid=self.main.Vid

        self.grid(sticky="nsew")
        Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW

        self.parent.attributes('-toolwindow', True)


        self.relative_explo=[]

        self.propagate=False

        self.ready = True
        self.first=True
        self.liste_sequences=[]
        self.all_grid = []


        self.Coos, _ = CoosLS.load_coos(self.Vid, location=self)
        if self.main.Check_Smoothed.get():
            self.Coos=Diverse_functions.smooth_coos(Coos=self.Coos, window_length=self.main.window_length,polyorder=self.main.polyorder)

        if len(self.Vid.Analyses[4][0]) > 0:
            self.Coos = Functions_deformation.deform_coos(self.Coos, self.Vid.Analyses[4][0])

        self.NB_ind = len(self.Vid.Identities)

        #Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Analyses_details_T"])

        #We create an optionmenu to allow the user to select the arena of interest
        self.List_inds_names = dict()
        for ind in range(len(self.Vid.Identities)):
            self.List_inds_names["Ind"+str(ind)]=self.Messages["Arena_short"]+ "{}, ".format(self.Vid.Identities[ind][0])+ self.Messages["Individual_short"] +" {}".format(self.Vid.Identities[ind][1])

        self.Ind_name=StringVar()
        self.Ind_name.set(self.Messages["Arena_short"]+ "{}, ".format(self.Vid.Identities[0][0])+ self.Messages["Individual_short"] +" {}".format(self.Vid.Identities[0][1]))

        selected=list(self.List_inds_names.values()).index(self.Ind_name.get())
        self.Area = self.Vid.Identities[selected][0]
        self.ID=0

        self.Which_ind = OptionMenu(self, self.Ind_name, *self.List_inds_names.values(), command=self.change_ind)
        self.Which_ind["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
        self.Which_ind.config(**Color_settings.My_colors.Button_Base)
        self.Which_ind.grid(row=0, column=0, sticky="nsew")

        self.update_event_list()

        #organization of the Frame
        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid, ecart=0, show_cropped=True)
        self.deb_traj = 0
        self.end_traj = 0
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Scrollbar = self.Vid_Lecteur.Scrollbar
        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub + 1)
        self.Vid_Lecteur.bindings()
        self.Scrollbar.refresh()


        self.Seq_container=Frame(self, **Color_settings.My_colors.Frame_Base)
        self.Seq_container.grid(row=2, column=0, sticky="nsew")
        Grid.columnconfigure(self.Seq_container, 0, weight=100)
        Grid.columnconfigure(self.Seq_container, 1, weight=100)
        Grid.columnconfigure(self.Seq_container, 2, weight=1)
        Grid.rowconfigure(self.Seq_container, 0, weight=100)
        Grid.rowconfigure(self.Seq_container, 1, weight=1)

        self.Seq_Canvas=Canvas(self.Seq_container, **Color_settings.My_colors.Frame_Base)
        self.Seq_Canvas.grid(row=0, column=0, columnspan=2, sticky="nsew")
        Grid.columnconfigure(self.Seq_Canvas, 0, weight=1)
        Grid.rowconfigure(self.Seq_Canvas, 0, weight=1)

        self.Seq_Scrollable=Canvas(self.Seq_Canvas, **Color_settings.My_colors.Frame_Base)
        self.Seq_Scrollable.grid(row=0, column=0, sticky="nsew")

        self.Add_seq_buton=Button(self.Seq_container, text=self.Messages["Sequences1"], command=self.add_seq, **Color_settings.My_colors.Button_Base)
        self.Add_seq_buton.grid(row=1, column=0, sticky="nsew")

        self.Copy_seq_buton=Button(self.Seq_container, text=self.Messages["Sequences2"], command=self.copy_seq, **Color_settings.My_colors.Button_Base)
        self.Copy_seq_buton.grid(row=1, column=1, sticky="nsew")

        self.Seq_Canvas.create_window((0, 0), window=self.Seq_Scrollable, anchor="nw")


        self.vsb=ttk.Scrollbar(self.Seq_container,orient=VERTICAL)
        self.vsb.grid(row=0, column=2, sticky="nsew")
        self.vsb.config(command=self.Seq_Canvas.yview)
        self.Seq_Canvas.config(yscrollcommand=self.vsb.set)

        self.Frame_user = Frame(self, width=150, **Color_settings.My_colors.Frame_Base)
        self.Frame_user.grid(row=0, column=1, rowspan=3, sticky="nsew")
        Grid.columnconfigure(self.Frame_user, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.Frame_user, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.Frame_user, 1, weight=1)  ########NEW
        Grid.rowconfigure(self.Frame_user, 2, weight=100)  ########NEW

        # Help user and parameters
        self.HW = User_help.Help_win(self.Frame_user, default_message=self.Messages["Sequences0"])
        self.HW.grid(row=0, column=0, sticky="nsew")

        Frame_Ana = Frame(self.Frame_user, **Color_settings.My_colors.Frame_Base)
        Frame_Ana.grid(row=2, column=0, columnspan=2, sticky="nsew")
        Grid.columnconfigure(Frame_Ana, 0, weight=1)
        Grid.rowconfigure(Frame_Ana, 0, weight=1)

        self.Quit_button = Button(self.Frame_user, text=self.Messages["Validate"], command=self.close, **Color_settings.My_colors.Button_Base)
        self.Quit_button.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.Quit_button.grid(row=5, column=0, sticky="sew")

        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=100)
        Grid.rowconfigure(self, 2, weight=1)
        self.grid_rowconfigure(0, minsize=25)
        self.grid_rowconfigure(2, minsize=300)
        self.grid_columnconfigure(1, minsize=200)

        self.change_ind()
        self.stay_on_top()
        self.parent.protocol("WM_DELETE_WINDOW", self.close)

    def copy_seq(self):
        #Allow the user to select a list of arenas in which the elements of interest will be duplicated
        newWindow = Toplevel(self.parent.master)
        Interface_extend_seqs.Lists(parent=newWindow, boss=self, liste_videos=self.main.main_frame.liste_of_videos, Current_Vid=self.main.Vid, Current_Area=self.Area, Current_Ind=self.ID)
        self.wait_window(newWindow)

    def remove_all_seq(self):
        for Seq in self.liste_sequences:
            if Seq!=None:
                Seq.grid_forget()
                Seq.destroy()

    def draw_all_seq(self):
        for Seq in self.liste_sequences:
            if Seq!=None:
                Seq.grid(sticky="nsew")
                Seq.show_seq()

        self.Seq_Canvas.configure(scrollregion=self.Seq_Canvas.bbox("all"))


    def add_seq(self):
        found=False
        count=0
        while found==False:
            if "Seq_"+str(count) not in [s.Seq_name.get() for s in self.liste_sequences if s!=None]:
                found=True
            else:
                count+=1

        self.liste_sequences.append(Sequence(parent=self.Seq_Scrollable, main=self, position=len(self.liste_sequences), Name="Seq_"+str(count)))
        self.draw_all_seq()


    def close(self):
        #properly close the parent window
        self.save_seqs()
        self.unbind_all("<Return>")
        self.Vid_Lecteur.proper_close()
        self.parent.destroy()
        self.main.redo_reader()
        self.main.modif_image()

    def save_seqs(self):
        if len(self.liste_sequences)>0:
            self.Vid.Sequences[self.ID]=[]

        for seq in self.liste_sequences:
            if seq!=None:
                to_save=self.convert_seq(seq)
                self.Vid.Sequences[self.ID].append(to_save)


    def convert_seq(self, seq):
        if self.Messages["Sequences_First_Time_in"] in seq.value_start3.get():
            string = seq.value_start3.get()
            Value3_deb = string.replace(self.Messages["Sequences_First_Time_in"], "First_in_")

        elif self.Messages["Sequences_Last_Time_in"] in seq.value_start3.get():
            string = seq.value_start3.get()
            Value3_deb = string.replace(self.Messages["Sequences_Last_Time_in"], "Last_in_")
        else:
            Value3_deb = self.find_general_name(seq.value_start3.get())

        if self.Messages["Sequences_First_Time_in"] in seq.value_end3.get():
            string = seq.value_end3.get()
            Value3_end = string.replace(self.Messages["Sequences_First_Time_in"], "First_in_")

        elif self.Messages["Sequences_Last_Time_in"] in seq.value_end3.get():
            string = seq.value_end3.get()
            Value3_end = string.replace(self.Messages["Sequences_Last_Time_in"], "Last_in_")
        else:
            Value3_end = self.find_general_name(seq.value_end3.get())

        to_save = [seq.Seq_name.get(),
                   [self.find_general_name(seq.type_start.get()), self.find_general_name(seq.value_start.get()),
                    self.find_general_name(seq.value_start2.get()), Value3_deb,
                    self.find_general_name(seq.value_start_explo.get()), seq.value_start5.get()],
                   [self.find_general_name(seq.type_end.get()), self.find_general_name(seq.value_end.get()),
                    self.find_general_name(seq.value_end2.get()), Value3_end,
                    self.find_general_name(seq.value_end_explo.get()), seq.value_end5.get()]]

        return(to_save)

    def find_specific_name(self, val):
        if val=="Beg":
            val=self.Messages["Sequences_Begin"]
        elif val=="End":
            val=self.Messages["Sequences_End"]
        elif val=="Time":
            val=self.Messages["Sequences_Time"]
        elif val=="Explo":
            val=self.Messages["Sequences_Explo"]
        elif val=="Spatial":
            val=self.Messages["Sequences_Spatial_event"]
        elif val=="bef":
            val=self.Messages["Sequences_before"]
        elif val=="aft":
            val=self.Messages["Sequences_after"]
        elif "Last_in_" in val:
            val = val.replace("Last_in_",self.Messages["Sequences_Last_Time_in"])
        elif "First_in_" in val:
            val = val.replace("First_in_",self.Messages["Sequences_First_Time_in"])

        return(val)


    def find_general_name(self, val):
        if val == self.Messages["Sequences_Begin"]:
            val="Beg"
        elif val in self.Messages["Sequences_End"]:
            val="End"
        elif val in self.Messages["Sequences_Time"]:
            val="Time"
        elif val in self.Messages["Sequences_Explo"]:
            val="Explo"
        elif val in self.Messages["Sequences_Spatial_event"]:
            val="Spatial"
        elif val in self.Messages["Sequences_before"]:
            val="bef"
        elif val in self.Messages["Sequences_after"]:
            val="aft"

        return(val)


    def change_ind(self, *arg):
        self.save_seqs()
        self.remove_all_seq()
        self.liste_sequences=[]

        #Change the target of interest
        self.main.highlight = list(self.List_inds_names.keys())[list(self.List_inds_names.values()).index(self.Ind_name.get())]

        Ind = list(self.List_inds_names.values()).index(self.Ind_name.get())
        self.Area = self.Vid.Identities[Ind][0]

        list_inds = np.array([[idx, Ind[1]] for idx, Ind in enumerate(self.Vid.Identities)])
        self.ID = int(list_inds[:, 0][Ind])

        self.relative_explo=[]
        self.Calculate_all(self.ID)

        self.update_sequences()


    def update_sequences(self):
        for S in self.liste_sequences:
            S.destroy()

        self.liste_sequences=[]

        pos = 0
        for seq in self.Vid.Sequences[self.ID]:
            conv_seq1=[]
            for val in seq[1]:
                conv_seq1.append(self.find_specific_name(val))

            conv_seq2 = []
            for val in seq[2]:
                conv_seq2.append(self.find_specific_name(val))

            self.liste_sequences.append(
                Sequence(parent=self.Seq_Scrollable, main=self, position=pos, Name=seq[0], Start_vals=conv_seq1,End_vals=conv_seq2))
            pos += 1

        self.update_event_list()
        self.modif_image()
        self.draw_all_seq()

    def Calculate_all(self, ID):
        load_frame = Class_loading_Frame.Loading(self)  # Progression bar
        load_frame.grid()
        load_frame.show_load(0)

        mask = Function_draw_mask.draw_mask(self.Vid)
        Arenas, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        Arenas = Function_draw_mask.Organise_Ars(Arenas)

        Copy_Coos = np.array(self.Coos[ID])
        Copy_Coos[np.where(Copy_Coos == -1000)] = np.nan
        Dists = np.sqrt(np.diff(Copy_Coos[:, 0]) ** 2 + np.diff(Copy_Coos[:, 1]) ** 2) / float(self.Vid.Scale[0])
        Dists = np.append(np.nan, Dists)
        Speeds = Dists / (1 / self.Vid.Frame_rate[1])
        State = np.zeros(len(Speeds))
        State[np.where(Speeds > self.main.Calc_speed.seuil_movement)] = 1
        State[np.where(np.isnan(Speeds))] = np.nan

        load_frame.show_load(0.3)

        #First entrance and left of the elements of interest
        self.Shapes_data=[[[],[]] for A in range(len(self.main.Calc_speed.Areas[self.Area]))]
        pos=0
        for Shape in self.main.Calc_speed.Areas[self.Area]:
            if not Shape[0]=="Line":
                Shape_tmp=Shape.copy()
                Shape_tmp[2] = float(Shape_tmp[2].get())

                load_frame.show_load(0.3 + (pos/len(self.main.Calc_speed.Areas[self.Area]))*0.3)
                entries, outs = find_shape_relation(Shape_tmp, self.Vid, Copy_Coos, ID)

                self.Shapes_data[pos][0] = entries
                self.Shapes_data[pos][1] = outs

                pos+=1

        #The first and last frame with movements
        self.first_move=np.argmax(State==1)
        self.last_move= len(State) - np.argmax(State[::-1]==1) - 1
        self.max_len=len(State)

        load_frame.destroy()


    def update_event_list(self):
        self.list_events_movements = dict(First=self.Messages["Sequences_First_Move"], Last=self.Messages["Sequences_Last_Move"])
        self.list_events=dict()
        for shape in range(len(self.main.Calc_speed.Areas[self.Area])):
            if not self.main.Calc_speed.Areas[self.Area][shape][0]=="Line":
                info=self.Messages["Sequences_First_Time_in"]+self.main.Calc_speed.Areas[self.Area][shape][3]
                info2 = self.Messages["Sequences_Last_Time_in"]+self.main.Calc_speed.Areas[self.Area][shape][3]

                self.list_events["Shape_in_"+str(shape)]=info
                self.list_events["Shape_out_" + str(shape)] = info2



    def stay_on_top(self):
        #We want the parent windows to always remain at the top.
        if self.ready:
            self.parent.lift()
        self.parent.after(50, self.stay_on_top)


    def modif_image(self, img=[], aff=False, **kwargs):
        if self.Vid.Cropped[0]:
            to_remove = int(round((self.Vid.Cropped[1][0]) / self.Vid_Lecteur.one_every))
        else:
            to_remove = 0

        if len(img) <= 10:
            new_img = np.copy(self.last_empty)
        else:
            self.last_empty = img
            new_img = np.copy(img)

        if len(self.Vid.Analyses[4][0])>0:
            new_img =  cv2.warpPerspective(new_img, self.Vid.Analyses[4][0], (new_img.shape[1], new_img.shape[0]))

        if self.first:
            self.Vid_Lecteur.Size = (new_img.shape[0], new_img.shape[1])
            self.Vid_Lecteur.zoom_sq = [0, 0, new_img.shape[1], new_img.shape[0]]

        if self.Scrollbar.active_pos >= round(
            ((self.Vid.Cropped[1][0] - 1) / self.Vid_Lecteur.one_every)) and self.Scrollbar.active_pos <= round(
            ((self.Vid.Cropped[1][1] - 1) / self.Vid_Lecteur.one_every) + 1):

            new_img = self.main.draw_shapes(np.copy(new_img), to_remove)


        for frame in range(self.deb_traj, self.end_traj):
            if self.Coos[self.ID, frame, 0] != -1000 and  self.Coos[self.ID, frame+1,0] != -1000:
                TMP_tail_1 = (
                    int(self.Coos[self.ID, int(frame), 0]),
                    int(self.Coos[self.ID, int(frame), 1]))

                TMP_tail_2 = (
                    int(self.Coos[
                            self.ID, int(frame+1), 0]),
                    int(self.Coos[
                            self.ID, int(frame+1), 1]))
                new_img = cv2.line(new_img, TMP_tail_1, TMP_tail_2, self.Vid.Identities[self.ID][2], max(int(3 * self.Vid_Lecteur.ratio), 1))

        rectangle = Function_draw_mask.enclosing_rectangle(self.Area, self.main.Vid, ret=False)
        cropx, cropy, width, heigh = rectangle
        new_img=new_img[cropy:(cropy + heigh), cropx:(cropx + width)]
        self.Vid_Lecteur.afficher_img(new_img)
        self.first = False

    def released_can(self, *args):
        pass

    def pressed_can(self, *args):
        pass




class Sequence(Frame):
    def __init__(self, parent, main, position, Name, Start_vals=[], End_vals=[],**kwargs):
        Frame.__init__(self, parent, main, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base, pady=5)
        self.Vid=main.Vid
        self.main=main
        self.pos=position
        self.Messages=self.main.Messages

        self.value_start=StringVar()
        self.value_end=StringVar()

        self.value_start2=StringVar()
        self.value_end2=StringVar()

        self.value_start3=StringVar()
        self.value_end3=StringVar()

        self.value_start_explo=StringVar()
        self.value_end_explo = StringVar()

        self.value_start5=StringVar()#Which entrance in the shape?
        self.value_end5=StringVar()

        if len(Start_vals)>0:
            self.value_start.set(Start_vals[1])
            self.value_start2.set(Start_vals[2])
            self.value_start3.set(Start_vals[3])
            self.value_start_explo.set(Start_vals[4])
            try:
                self.value_start5.set(Start_vals[5])
            except:
                self.value_start5.set(1)

        if len(End_vals) > 0:
            self.value_end.set(End_vals[1])
            self.value_end2.set(End_vals[2])
            self.value_end3.set(End_vals[3])
            self.value_end_explo.set(End_vals[4])
            try:
                self.value_end5.set(End_vals[5])
            except:
                self.value_end5.set(-1)


        #The sequence name
        self.Seq_name=StringVar()
        self.Seq_name.set(Name)
        Entry(self, textvariable=self.Seq_name, **Color_settings.My_colors.Entry_Base).grid(row=0,column=0, columnspan=2, sticky="w")
        Rem_Button=Button(self, text=self.Messages["Analyses_details_sp8"], command=self.terminate, **Color_settings.My_colors.Button_Base)
        Rem_Button.config(background=Color_settings.My_colors.list_colors["Danger"], fg=Color_settings.My_colors.list_colors["Fg_Danger"])
        Rem_Button.grid(row=1,column=0,sticky="w")
        self.warn_glob=Label(self, text="⚠", fg="red", font='Helvetica 22 bold')


        #Beginning of the sequence
        if len(self.main.list_events.values()) > 0:
            list_possibilities_beg = dict(Limits=self.Messages["Sequences_Begin"], Time=self.Messages["Sequences_Time"], Exploration=self.Messages["Sequences_Explo"], Spatial_event=self.Messages["Sequences_Spatial_event"])#, Movement="Movement"
            list_possibilities_end = dict(Limits=self.Messages["Sequences_End"], Time=self.Messages["Sequences_Time"], Exploration=self.Messages["Sequences_Explo"], Spatial_event=self.Messages["Sequences_Spatial_event"])#, Movement="Movement"
        else:
            list_possibilities_beg = dict(Limits=self.Messages["Sequences_Begin"], Time=self.Messages["Sequences_Time"],Exploration=self.Messages["Sequences_Explo"])#, Movement="Movement"
            list_possibilities_end = dict(Limits=self.Messages["Sequences_End"], Time=self.Messages["Sequences_Time"], Exploration=self.Messages["Sequences_Explo"])#, Movement="Movement"
        # Exploration: avant/après pourcentage de zone totale explorée
        # pourcentage d'un element exploré + ajouter infos dans les résultats en général.

        # Social: premier/dernier contact avec ind X
        # première/dernière fois avec au moins X voisins
        # première / dernière fois sans voisins

        # Comportement?
        # premier évènement observé
        # dernier évènement observé
        #sequence comportementale

        self.type_start = StringVar()

        if len(Start_vals)>0:
            self.type_start.set(Start_vals[0])
        else:
            self.type_start.set(self.Messages["Sequences_Begin"])

        Opt1=OptionMenu(self, self.type_start, *list_possibilities_beg.values(), command=partial(self.change_text,-1))
        Opt1["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
        Opt1.config(**Color_settings.My_colors.Button_Base)
        Opt1.grid(row=0,column=3)
        Opt1.bind("<FocusIn>",self.show_seq)
        Opt1.bind("<Button>", self.show_seq)


        self.type_end = StringVar()
        if len(End_vals) > 0:
            self.type_end.set(End_vals[0])
        else:
            self.type_end.set(self.Messages["Sequences_End"])

        Opt2=OptionMenu(self, self.type_end, *list_possibilities_end.values(), command=partial(self.change_text,1))
        Opt2["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
        Opt2.config(**Color_settings.My_colors.Button_Base)
        Opt2.grid(row=0, column=5)
        Opt2.bind("<FocusIn>",self.show_seq)
        Opt2.bind("<Button>", self.show_seq)

        if len(Start_vals) > 0:
            self.change_text(None)
        else:
            self.change_text(0)

    def terminate(self):
        self.main.save_seqs()
        if self.Seq_name.get() in [saved_seq[0] for saved_seq in self.main.Vid.Sequences[self.main.ID]]:
            pos = [saved_seq[0] for saved_seq in self.main.Vid.Sequences[self.main.ID]].index(self.Seq_name.get())
            self.main.Vid.Sequences[self.main.ID].pop(pos)
        if len(self.main.Vid.Sequences[self.main.ID])<1:
            self.main.Vid.Sequences[self.main.ID]=[full_sequence]

        self.main.update_sequences()
        self.destroy()



    def unselect(self):
        self.config(relief="groove", bd=3, highlightthickness = 0)

    def show_seq(self, *args):
        for S in self.main.liste_sequences:
            if S!=None:
                S.unselect()
        self.config(bd = '0',    highlightthickness = 4,   highlightcolor = Color_settings.My_colors.list_colors["Hilight_Frame"], highlightbackground = Color_settings.My_colors.list_colors["Hilight_Frame"])

        self.change_val(self.value_end)
        self.change_val(self.value_start)

    def change_text(self,type_pos=None,*args):
        try:
            self.value_start.trace_vdelete("W",self.trace_start1)
            self.value_start2.trace_vdelete("W", self.trace_start2)
            self.value_start3.trace_vdelete("W", self.trace_start3)
            self.value_start5.trace_vdelete("W", self.trace_start5)
            self.value_end.trace_vdelete("W", self.trace_end1)
            self.value_end2.trace_vdelete("W", self.trace_end2)
            self.value_end3.trace_vdelete("W", self.trace_end3)
            self.value_end5.trace_vdelete("W", self.trace_end5)
            self.value_start_explo.trace_vdelete("W", self.trace_start_explo)
            self.value_end_explo.trace_vdelete("W", self.trace_end_explo)
        except:
            pass

        check_num = (self.register(self.callback))

        self.TxtFrame_deb = Frame(self,width=10, **Color_settings.My_colors.Frame_Base)
        self.TxtFrame_end = Frame(self,width=10, **Color_settings.My_colors.Frame_Base)

        ttk.Separator(self, orient=VERTICAL).grid(column=2,row=0, rowspan=2, sticky="nsew")
        self.TxtFrame_deb.grid(row=1, column=3, sticky="nsew")

        ttk.Separator(self, orient=VERTICAL).grid(column=4,row=0, rowspan=2, sticky="nsew")
        self.TxtFrame_end.grid(row=1, column=5, sticky="nsew")

        Grid.columnconfigure(self,0,weight=0, minsize=75)
        Grid.columnconfigure(self, 1, weight=0, minsize=75)
        Grid.columnconfigure(self, 2, weight=0)
        Grid.columnconfigure(self, 3, weight=100, minsize=320)
        Grid.columnconfigure(self, 4, weight=0)
        Grid.columnconfigure(self, 5, weight=100, minsize=300)

        #Begin
        if self.type_start.get() == self.Messages["Sequences_Begin"]:
            self.value_start.set(0)

        elif self.type_start.get()==self.Messages["Sequences_Time"]:
            if type_pos != None and type_pos <= 0:
                self.value_start.set(0)

            Lab1=Label(self.TxtFrame_deb, text=self.Messages["Sequences3"]+" ", **Color_settings.My_colors.Label_Base)
            Lab1.grid(row=0,column=0, sticky="nsew")

            Ent1=Entry(self.TxtFrame_deb, textvariable=self.value_start, width=10, validate='all', validatecommand=(check_num, '%P'), **Color_settings.My_colors.Entry_Base)
            Ent1.grid(row=0, column=1, sticky="nsew")

            Lab2 = Label(self.TxtFrame_deb, text=" sec", **Color_settings.My_colors.Label_Base)
            Lab2.grid(row=0, column=2, sticky="nsew")


        elif self.type_start.get()==self.Messages["Sequences_Spatial_event"]:
            if type_pos != None and type_pos <= 0:
                self.value_start.set(0)
                self.value_start2.set(self.Messages["Sequences_before"])
                self.value_start3.set(list(self.main.list_events.values())[0])
                self.value_start5.set(0)

            #if self.type_start.get() == self.Messages["Sequences_Spatial_event"]:
            #    self.value_end3.set(list(self.main.list_events.values())[0])

            Lab1=Label(self.TxtFrame_deb, text=self.Messages["Sequences3"]+" ", **Color_settings.My_colors.Label_Base)
            Lab1.grid(row=0,column=0, sticky="nsew")

            Ent1=Entry(self.TxtFrame_deb, textvariable=self.value_start, width=6, validate='all', validatecommand=(check_num, '%P'), **Color_settings.My_colors.Entry_Base)
            Ent1.grid(row=0, column=1, sticky="nsew")

            Lab2=Label(self.TxtFrame_deb, text="sec", **Color_settings.My_colors.Label_Base)
            Lab2.grid(row=0,column=2, sticky="nsew")

            Opt1 = OptionMenu(self.TxtFrame_deb, self.value_start2, *[self.Messages["Sequences_before"], self.Messages["Sequences_after"]])
            Opt1["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
            Opt1.config(**Color_settings.My_colors.Button_Base)
            Opt1.grid(row=0, column=3, sticky="nsew")


            Opt2=OptionMenu(self.TxtFrame_deb, self.value_start3, *self.main.list_events.values())
            Opt2["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
            Opt2.config(**Color_settings.My_colors.Button_Base)
            Opt2.grid(row=0, column=4, sticky="nsew")

            Lab3=Label(self.TxtFrame_deb, text="nº", **Color_settings.My_colors.Label_Base)
            Lab3.grid(row=0,column=5, sticky="nsew")

            Ent2=Entry(self.TxtFrame_deb, textvariable=self.value_start5, width=3, validate='all', validatecommand=(check_num, '%P'), **Color_settings.My_colors.Entry_Base)
            Ent2.grid(row=0, column=6, sticky="nsew")



        elif self.type_start.get() == self.Messages["Sequences_Explo"]:
            if type_pos != None and type_pos <= 0:
                self.value_start_explo.set(1)

            Lab1 = Label(self.TxtFrame_deb, text=self.Messages["Sequences3"]+" ", **Color_settings.My_colors.Label_Base)
            Lab1.grid(row=0, column=0, sticky="nsew")

            Sca1 = Scale(self.TxtFrame_deb, from_=0, to=100, resolution=10, variable=self.value_start_explo, orient=HORIZONTAL, **Color_settings.My_colors.Scale_Base)
            Sca1.grid(row=0, column=1, sticky="nsew")

            Lab2 = Label(self.TxtFrame_deb, text=self.Messages["Sequences4"], **Color_settings.My_colors.Label_Base)
            Lab2.grid(row=0, column=2, sticky="nsew")

        if self.type_end.get()==self.Messages["Sequences_End"]:
            self.value_end.set(str(round(((self.Vid.Cropped[1][1] - self.Vid.Cropped[1][0])/ self.main.Vid_Lecteur.one_every)/self.Vid.Frame_rate[1], 2)))

        elif self.type_end.get() == self.Messages["Sequences_Time"]:
            if type_pos!=None and type_pos>=0:
                self.value_end.set(str(round(((self.Vid.Cropped[1][1] - self.Vid.Cropped[1][0])/ self.main.Vid_Lecteur.one_every)/self.Vid.Frame_rate[1], 2)))

            Lab3=Label(self.TxtFrame_end, text=self.Messages["Sequences5"]+" ", **Color_settings.My_colors.Label_Base)
            Lab3.grid(row=0,column=0, sticky="nsew")

            Ent2=Entry(self.TxtFrame_end, textvariable=self.value_end, width=10, validate='all', validatecommand=(check_num, '%P'), **Color_settings.My_colors.Entry_Base)
            Ent2.grid(row=0, column=1, sticky="nsew")

            Lab4 = Label(self.TxtFrame_end, text=" sec.", **Color_settings.My_colors.Label_Base)
            Lab4.grid(row=0, column=2, sticky="nsew")


        elif self.type_end.get() == self.Messages["Sequences_Spatial_event"]:# or self.type_end.get()=="Movement":
            if type_pos!=None and type_pos>=0:
                self.value_end.set(0)
                self.value_end2.set(self.Messages["Sequences_before"])
                self.value_end3.set(list(self.main.list_events.values())[0])
                self.value_end5.set(1)

                #if self.type_end.get() == self.Messages["Sequences_Spatial_event"]:
                #    self.value_end3.set(list(self.main.list_events.values())[0])

                #elif self.type_end.get() == "Movement":
                #    self.value_end3.set(list(self.main.list_events_movements.values())[0])

            Lab3=Label(self.TxtFrame_end, text=self.Messages["Sequences5"]+" ", **Color_settings.My_colors.Label_Base)
            Lab3.grid(row=0,column=0, sticky="nsew")

            Ent3=Entry(self.TxtFrame_end, textvariable=self.value_end, width=6, validate='all', validatecommand=(check_num, '%P'), **Color_settings.My_colors.Entry_Base)
            Ent3.grid(row=0, column=1, sticky="nsew")

            Lab4=Label(self.TxtFrame_end, text="sec", **Color_settings.My_colors.Label_Base)
            Lab4.grid(row=0,column=2, sticky="nsew")

            Opt3 = OptionMenu(self.TxtFrame_end, self.value_end2, *[self.Messages["Sequences_before"], self.Messages["Sequences_after"]])
            Opt3["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
            Opt3.config(**Color_settings.My_colors.Button_Base)
            Opt3.grid(row=0, column=3, sticky="nsew")

            Opt4 = OptionMenu(self.TxtFrame_end, self.value_end3, *self.main.list_events.values())
            Opt4["menu"].config(**Color_settings.My_colors.OptnMenu_Base)
            Opt4.config(**Color_settings.My_colors.Button_Base)
            Opt4.grid(row=0, column=4, sticky="nsew")

            Lab5=Label(self.TxtFrame_end, text="nº", **Color_settings.My_colors.Label_Base)
            Lab5.grid(row=0,column=5, sticky="nsew")

            Ent4=Entry(self.TxtFrame_end, textvariable=self.value_end5, width=3, validate='all', validatecommand=(check_num, '%P'), **Color_settings.My_colors.Entry_Base)
            Ent4.grid(row=0, column=6, sticky="nsew")


        elif self.type_end.get() == self.Messages["Sequences_Explo"]:
            if type_pos!=None and type_pos>=0:
                self.value_end_explo.set(1)

            Lab3 = Label(self.TxtFrame_end, text=self.Messages["Sequences5"]+" ", **Color_settings.My_colors.Label_Base)
            Lab3.grid(row=0, column=0, sticky="nsew")

            Sca2 = Scale(self.TxtFrame_end, from_=0, to=100, resolution=10, variable=self.value_end_explo, orient=HORIZONTAL, **Color_settings.My_colors.Scale_Base)
            Sca2.grid(row=0, column=1, sticky="nsew")

            Lab4 = Label(self.TxtFrame_end, text=self.Messages["Sequences4"], **Color_settings.My_colors.Label_Base)
            Lab4.grid(row=0, column=2, sticky="nsew")

        self.trace_start1=self.value_start.trace("w", self.change_val)
        self.trace_start2=self.value_start2.trace("w", self.change_val)
        self.trace_start3=self.value_start3.trace("w", self.change_val)
        self.trace_start5=self.value_start5.trace("w", self.change_val)
        self.trace_end1=self.value_end.trace("w", self.change_val)
        self.trace_end2=self.value_end2.trace("w", self.change_val)
        self.trace_end3=self.value_end3.trace("w", self.change_val)
        self.trace_end5=self.value_end5.trace("w", self.change_val)
        self.trace_start_explo=self.value_start_explo.trace("w", self.change_val)
        self.trace_end_explo = self.value_end_explo.trace("w", self.change_val)

        self.warn_deb=Label(self.TxtFrame_deb, text="⚠", font='Helvetica 18 bold', **Color_settings.My_colors.Label_Base)
        self.warn_deb.config(fg=Color_settings.My_colors.list_colors["Danger"])
        self.warn_end = Label(self.TxtFrame_end, text="⚠", font='Helvetica 18 bold', **Color_settings.My_colors.Label_Base)
        self.warn_end.config(fg=Color_settings.My_colors.list_colors["Danger"])

        self.bind("<FocusIn>",self.show_seq)
        self.bind("<Button>", self.show_seq)
        self.TxtFrame_deb.bind("<FocusIn>", self.show_seq)
        self.TxtFrame_end.bind("<FocusIn>",self.show_seq)
        self.TxtFrame_deb.bind("<Button>", self.show_seq)
        self.TxtFrame_end.bind("<Button>", self.show_seq)



    def change_val(self, var, index=None, mode=None):
        new_pos=None
        warn = False
        #Time="Time", Event="Event", Time_B_Event="Time before event", Time_A_Event="Time after event", Social_Event="Social event", Exploration="Exploration percentage"
        if str(var)==str(self.value_start) or str(var)==str(self.value_start2)or str(var)==str(self.value_start3) or str(var)==str(self.value_start5) or str(var)==str(self.value_start_explo):
            cur_type="start"
            val1=self.value_start.get()
            val2=self.value_start2.get()
            val3 = self.value_start3.get()
            val5 = self.value_start5.get()
            val_explo=self.value_start_explo.get()
            type=self.type_start.get()

        elif str(var)==str(self.value_end) or str(var)==str(self.value_end2) or str(var)==str(self.value_end3) or str(var)==str(self.value_end5) or str(var)==str(self.value_end_explo):
            cur_type = "end"
            val1=self.value_end.get()
            val2=self.value_end2.get()
            val3 = self.value_end3.get()
            val5 = self.value_end5.get()
            val_explo = self.value_end_explo.get()
            type = self.type_end.get()

        if (type==self.Messages["Sequences_Time"] or type==self.Messages["Sequences_Begin"] or type==self.Messages["Sequences_End"]) and val1!="":
            new_pos= int((float(val1) * self.main.main.Vid.Frame_rate[1] + self.main.main.Vid_Lecteur.to_sub))


        elif type==self.Messages["Sequences_Spatial_event"] and val1!="":
            if val3!="":
                if val3 not in list(self.main.list_events.values()):
                    val3=list(self.main.list_events.values())[0]

                shape_pos=(list(self.main.list_events.values()).index(val3))//2
                in_or_out=(list(self.main.list_events.values()).index(val3))%2

                try:
                    val5=int(val5)
                except:
                    val5=-1

                if val5>0 and val5<=len(self.main.Shapes_data[shape_pos][in_or_out]) and self.main.Shapes_data[shape_pos][in_or_out][val5-1]!="NA":
                    new_pos = int((float(self.main.Shapes_data[shape_pos][in_or_out][val5-1]) + self.main.main.Vid_Lecteur.to_sub))
                else:
                    new_pos ="NA"



            if new_pos!=None and new_pos!="NA":
                if val2==self.Messages["Sequences_after"]:
                    new_pos += int((float(val1) * self.main.main.Vid.Frame_rate[1]))
                else:
                     new_pos-= int((float(val1) *self.main.main.Vid.Frame_rate[1]))


        # elif type=="Movement" and val1!="":
        #     if val3=="First move":
        #         new_pos = int((float(self.main.first_move) + self.main.main.Vid_Lecteur.to_sub))
        #     if val3=="Last move":
        #         new_pos = int((float(self.main.last_move) + self.main.main.Vid_Lecteur.to_sub))
        #
        #     if new_pos!=None:
        #         if val2=="after":
        #             new_pos += int((float(val1) * self.main.main.Vid.Frame_rate[1]))
        #         else:
        #              new_pos-= int((float(val1) *self.main.main.Vid.Frame_rate[1] ))

        elif type==self.Messages["Sequences_Explo"] and val1!="":
            if len(self.main.relative_explo)<1:
                self.main.relative_explo = compute_explo(method=self.main.main.Infos_explo, Vid=self.Vid, Coos=self.main.Coos[self.main.ID], ID=self.main.ID, loading_parent=self.main)
            expl_time=self.main.relative_explo[int(int(val_explo)/10)]

            if expl_time!="NA":
                new_pos = int(expl_time + self.main.main.Vid_Lecteur.to_sub)
            else:
                warn=True
                new_pos = self.main.max_len + self.main.main.Vid_Lecteur.to_sub - 1


        if new_pos!=None:
            if new_pos=="NA":
                new_pos=self.main.max_len + self.main.main.Vid_Lecteur.to_sub - 1
                warn=True

            elif new_pos < self.main.main.Vid_Lecteur.to_sub:
                new_pos = self.main.main.Vid_Lecteur.to_sub
                warn=True

            elif new_pos >= self.main.max_len + self.main.main.Vid_Lecteur.to_sub:
                new_pos = self.main.max_len + self.main.main.Vid_Lecteur.to_sub - 1
                warn = True

            if cur_type == "start":
                self.main.Scrollbar.crop_beg = new_pos
                if warn:
                    self.warn_deb.grid(row=0, column=7)
                else:
                    self.warn_deb.grid_forget()

            elif cur_type == "end":
                self.main.Scrollbar.crop_end = new_pos
                if warn:
                    self.warn_end.grid(row=0, column=7)
                else:
                    self.warn_end.grid_forget()

            if self.main.Scrollbar.crop_end<=self.main.Scrollbar.crop_beg:
                self.main.Scrollbar.hide_crop=True
                self.warn_glob.grid(row=1, column=1, sticky="nsw")
            else:
                self.main.Scrollbar.hide_crop=False
                self.warn_glob.grid_forget()

            self.main.Scrollbar.active_pos = new_pos
            self.main.Scrollbar.refresh()
            self.main.deb_traj = self.main.Scrollbar.crop_beg - self.main.main.Vid_Lecteur.to_sub
            self.main.end_traj = self.main.Scrollbar.crop_end - self.main.main.Vid_Lecteur.to_sub

            self.main.Vid_Lecteur.update_image(self.main.Scrollbar.active_pos)


    def callback(self, P):
        if P=="":
            return True
        elif " " in P:
            return False
        else:
            try:
                float(P)
                return True
            except:
                return False
