from tkinter import *
from tkinter import ttk
from AnimalTA.A_General_tools import UserMessages, Diverse_functions, Color_settings
from AnimalTA.E_Post_tracking.b_Analyses import Interface_sequences
import copy
import os
import pandas as pd
from pandastable import Table, TableModel, util


class Int_import(Frame):
    def __init__(self, parent, boss, files, Vid, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.list_colors=Color_settings.My_colors.list_colors
        self.grid(sticky="nsew")
        self.parent=parent
        self.Vid=Vid
        self.boss=boss
        self.files=files

        self.sep=StringVar()# Which separator does the original file use
        self.sep.set(self.boss.import_values["Sep"])

        self.header=IntVar() #Do the original file use a header? If 0, we try to determine it automatically, 1 no header, 2 header
        self.header.set(self.boss.import_values["Header"])

        self.or_Tab=Frame(self)
        self.or_Tab.grid(row=1,column=0)

        self.res_Tab = Frame(self)
        self.res_Tab.grid(row=1, column=1)


        #Options for the user
        Frame_info=Frame(self)
        Frame_info.grid(row=0,column=0, columnspan=2)

        #Choose the separator
        self.Entry_Sep=Entry(Frame_info, textvariable=self.sep)
        self.Entry_Sep.grid(row=0, column=1)
        Validate_Entry=Label(Frame_info, text='Separator:')
        Validate_Entry.grid(row=0, column=0)


        #Indicate if the header is present or no
        Check_H = Checkbutton(Frame_info, text='Header', variable=self.header, onvalue=2, offvalue=1, command=self.create_new, **Color_settings.My_colors.Checkbutton_Base)
        Check_H.grid(row=1, column=0, columnspan=2)


        ttk.Separator(Frame_info, orient=VERTICAL).grid(row=0, column=2, rowspan=3, sticky="ns")
        ttk.Separator(Frame_info, orient=VERTICAL).grid(row=0, column=3, rowspan=3, sticky="ns")
        ttk.Separator(Frame_info, orient=VERTICAL).grid(row=0, column=4, rowspan=3, sticky="ns")

        #Indicate which column is the one for Frame number:
        self.Fr_pos=StringVar()
        self.Fr_pos.set(self.boss.import_values["Fr_col"])
        self.Entry_Fr_pos=Entry(Frame_info, textvariable=self.Fr_pos, **Color_settings.My_colors.Entry_Base)
        self.Entry_Fr_pos.grid(row=0, column=6, sticky="w")
        Label(Frame_info, text=self.Messages["Import_data1"]+":").grid(row=0, column=5, sticky="w")


        #Indicate which column is the one for Time:
        self.Time_pos=StringVar()
        self.Time_pos.set(self.boss.import_values["Time_col"])
        self.Entry_Time_pos=Entry(Frame_info, textvariable=self.Time_pos, **Color_settings.My_colors.Entry_Base)
        self.Entry_Time_pos.grid(row=1, column=6, sticky="w")
        Label(Frame_info, text=self.Messages["Import_data2"]+":").grid(row=1, column=5, sticky="w", **Color_settings.My_colors.Frame_Base, fg=self.list_colors["Fg_Base"])
        ttk.Separator(Frame_info, orient=VERTICAL).grid(row=0, column=7, rowspan=3, sticky="ns")


        #Indicates what kind of global organisation the file has
        self.orga_ind=IntVar()
        self.orga_ind.set(self.boss.import_values["Ind_col"])
        Rad_inds_columns=Radiobutton(Frame_info,text=self.Messages["Import_data3"], variable=self.orga_ind, value=0, command=self.create_new, **Color_settings.My_colors.Radiobutton_Base)
        Rad_inds_columns.grid(row=0, column=8, columnspan=2, sticky="w")
        Rad_inds_rows=Radiobutton(Frame_info,text=self.Messages["Import_data4"], variable=self.orga_ind, value=1, command=self.create_new, **Color_settings.My_colors.Radiobutton_Base)
        Rad_inds_rows.grid(row=1, column=8, columnspan=2, sticky="w")

        self.ID_pos=StringVar()
        self.ID_pos.set(self.boss.import_values["ID_col"])
        Label(Frame_info, text="     "+self.Messages["Import_data5"]+":", **Color_settings.My_colors.Label_Base).grid(row=2, column=8)
        self.Entry_ID_column=Entry(Frame_info, textvariable=self.ID_pos)
        self.Entry_ID_column.grid(row=2, column=9)
        if self.orga_ind.get()==0:
            self.Entry_ID_column.config(state="disabled")

        ttk.Separator(Frame_info, orient=VERTICAL).grid(row=0, column=10, rowspan=3, sticky="ns")
        self.Col_X=StringVar()
        self.Col_X.set(self.boss.import_values["Col_x"])
        Label(Frame_info, text=self.Messages["Import_data6"]+":").grid(row=0, column=11)
        self.Entry_X_pos=Entry(Frame_info, textvariable=self.Col_X)
        self.Entry_X_pos.grid(row=0, column=12)

        self.Col_Y=StringVar()
        self.Col_Y.set(self.boss.import_values["Col_y"])
        Label(Frame_info, text=self.Messages["Import_data7"]+":").grid(row=1, column=11)
        self.Entry_Y_pos=Entry(Frame_info, textvariable=self.Col_Y)
        self.Entry_Y_pos.grid(row=1, column=12)

        ttk.Separator(Frame_info, orient=VERTICAL).grid(row=0, column=13, rowspan=3, sticky="ns")

        Validate_new_pos=Button(Frame_info, text=self.Messages["Import_data8"], command=self.create_new, **Color_settings.My_colors.Button_Base)
        Validate_new_pos.config( bg=Color_settings.My_colors.list_colors["Button_ready"], fg=Color_settings.My_colors.list_colors["Fg_Button_ready"])
        Validate_new_pos.grid(row=3, column=0, columnspan=20, sticky="nsew")


        #Importation of messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]


        #Button to validate once the position is chosen
        self.BValidate=Button(self, text=self.Messages["Validate"], **Color_settings.My_colors.Button_Base, command=self.validate)
        self.BValidate.grid(row=5, column=0, sticky="nsew")
        self.BValidate.config(state="disable", **Color_settings.My_colors.Button_Base)

        B_Cancel=Button(self, text=self.Messages["Cancel"], **Color_settings.My_colors.Button_Base, command=self.End_of_win)
        B_Cancel.config(background=Color_settings.My_colors.list_colors["Cancel"],fg=Color_settings.My_colors.list_colors["Fg_Cancel"])
        B_Cancel.grid(row=5, column=1, sticky="nsew")


        self.stay_on_top()
        self.create_new()

    def load_files(self, files, reset_H=False):
        try:
            for file in files:
                if self.header.get()==0:
                    data = pd.read_csv(file, header=None, sep=self.sep.get(), engine='python')
                    if sum([isinstance(val, int) or isinstance(val, float) for val in data.iloc[0]])/len(data.iloc[0])<0.75:
                        data.columns = data.iloc[0]
                        data = data[1:]
                        self.header.set(2)
                    else:
                        self.header.set(1)

                elif self.header.get()==2:
                    data = pd.read_csv(file, header=[0], sep=self.sep.get(), engine='python', na_filter = False)
                else:
                    data = pd.read_csv(file, header=None, sep=self.sep.get(), engine='python', na_filter = False)

                self.or_data=data
                self.table = Table(self.or_Tab, dataframe=data, showtoolbar=False, showstatusbar=False)

                self.table.show()
                self.resize_columns(self.table)
            return True
        except:
            return False

    def is_number(selse, char):
        try:
            float(char)
        except ValueError:
            return False
        else:
            return True

    def extract_row_number(self, char):
        #Find all X columns:
        try:
            if char!="":
                if ("[" == char[0] and "]" == char[-1]) or self.is_number(char):#If the user gave a column number or a list of columns
                    char = char.replace(" ", "")
                    if ("[" == char[0] and "]" == char[-1]):
                        list_columns=char[1:-1].split(",")
                        list_columns=[int(val)-1 for val in list_columns]
                    else:
                        list_columns =[int(char)-1]

                    return (True, list_columns)

                else:
                    correct = [idx for idx, name in enumerate(self.or_data.columns.values) if char == name]
                    list_columns =[idx for idx, name in enumerate(self.or_data.columns.values) if char in name and not char == name]
                    list_columns=correct+list_columns
                    if len(list_columns)>0:
                        return (True, list_columns)
                    else:
                        return(False, [])
            else:
                return(False, [])
        except:
            return(False, [])


    def create_new(self):
        all_clear = True

        loaded=self.load_files(self.files)

        if loaded:
            self.Entry_Sep.config(**Color_settings.My_colors.Entry_Base)

            if self.orga_ind.get()==0:
                self.Entry_ID_column.config(state="disabled")
            else:
                self.Entry_ID_column.config(state="normal")

            if self.Time_pos.get()=="" and self.Fr_pos.get()=="":
                one_every = self.Vid.Frame_rate[0] / self.Vid.Frame_rate[1]
                fr_col=range(round(self.Vid.Cropped[1][0]/one_every),round(self.Vid.Cropped[1][1]/one_every+1))
                self.trans_data=pd.DataFrame(fr_col,columns =['Frame'])
                self.trans_data["Time"]=fr_col
                self.trans_data["Time"]=self.trans_data["Time"].div(self.Vid.Frame_rate[1])

            elif self.Fr_pos.get()!="":
                try:
                    try:
                        Fr_pos = self.or_data.columns.get_loc(self.Fr_pos.get())
                    except:
                        Fr_pos = int(self.Fr_pos.get()) - 1

                    self.trans_data = pd.DataFrame(self.or_data.iloc[:, [int(Fr_pos)]].copy())
                    self.trans_data.columns = ["Frame"]
                    self.trans_data["Time"] = self.trans_data["Frame"].copy()
                    self.trans_data["Time"] = pd.to_numeric(self.trans_data["Time"])
                    self.trans_data["Time"] = self.trans_data["Time"].div(self.Vid.Frame_rate[1])
                    self.trans_data["Frame"] = self.trans_data.Frame.astype(float)
                    self.trans_data["Frame"] = self.trans_data["Frame"].round()
                    self.trans_data["Frame"] = self.trans_data.Frame.astype(int)
                    self.Entry_Fr_pos.config(**Color_settings.My_colors.Entry_Base)
                except:
                    self.trans_data = pd.DataFrame()
                    self.Entry_Fr_pos.config(**Color_settings.My_colors.Entry_error)
                    all_clear=False

            else:
                try:
                    try:
                        Time_pos = self.or_data.columns.get_loc(self.Time_pos.get())
                    except:
                        Time_pos = int(self.Time_pos.get())-1

                    self.trans_data = pd.DataFrame(self.or_data.iloc[:, [int(Time_pos)]].copy())
                    self.trans_data.columns = ["Time"]
                    self.trans_data["Frame"] = self.trans_data["Time"].copy()
                    self.trans_data["Frame"] = pd.to_numeric(self.trans_data["Frame"])
                    self.trans_data["Frame"] = self.trans_data["Frame"].multiply(self.Vid.Frame_rate[1])
                    self.trans_data["Frame"] = self.trans_data["Frame"].round()
                    self.trans_data["Frame"] = self.trans_data.Frame.astype(int)
                    self.trans_data=self.trans_data[["Frame","Time"]]
                    self.Entry_Time_pos.config(**Color_settings.My_colors.Entry_Base)
                except:
                    self.trans_data = pd.DataFrame()
                    self.Entry_Time_pos.config(**Color_settings.My_colors.Entry_error)
                    all_clear=False


            if self.orga_ind.get()==1:
                ID_ok=False
                self.trans_data["Arena"] = 0
                self.trans_data["Ind"] = ""
                if self.ID_pos.get() != "":
                    ID_ok = True
                    selected_columns=self.ID_pos.get().split("+")
                    for SC in selected_columns:
                        if SC[0]=="\"" and SC[-1]=="\"":
                            self.trans_data["Ind"] = self.trans_data["Ind"].astype(str) + SC[1:-1]
                        else:
                            try:
                                try:
                                    T_ID_pos = self.or_data.columns.get_loc(SC)
                                except:
                                    T_ID_pos = int(SC) - 1

                                column_name = self.or_data.columns[int(T_ID_pos)]
                                self.trans_data["Ind"] = self.trans_data["Ind"].astype(str) + self.or_data[column_name].astype(str)
                            except:
                                ID_ok=False

                if not ID_ok:
                    self.trans_data.drop(columns=["Ind"])
                    self.Entry_ID_column.config(**Color_settings.My_colors.Entry_error)
                    all_clear=False
                else:
                    self.Entry_ID_column.config(**Color_settings.My_colors.Entry_Base)


            # Driver code
            valideX, columnsX = self.extract_row_number(self.Col_X.get())
            valideY, columnsY = self.extract_row_number(self.Col_Y.get())
            if valideX and valideY and len(columnsX)==len(columnsY):
                if self.orga_ind.get() == 0:
                    [0]*len(columnsX)
                    if int(sum(self.Vid.Track[1][6])) == len(columnsX):
                        arenas=[]
                        passed = 0
                        arena = 0
                        for I in range(len(columnsX)):
                            arenas.append(arena)
                            passed += 1
                            if passed >= int(sum(self.Vid.Track[1][6][0:(arena+1)])):
                                arena += 1
                    else:
                        arenas = []

                    ind=0
                    for col in range(len(columnsX)):
                        self.trans_data["X_Arena"+str(arenas[col])+"_Ind"+str(ind)]=self.or_data.iloc[:, [int(columnsX[col])]].copy()
                        self.trans_data["Y_Arena"+str(arenas[col])+"_Ind" + str(ind)] = self.or_data.iloc[:, [int(columnsY[col])]].copy()
                        self.trans_data["X_Arena"+str(arenas[col])+"_Ind"+str(ind)]=pd.to_numeric(self.trans_data["X_Arena"+str(arenas[col])+"_Ind"+str(ind)], errors='coerce').fillna("NA")
                        self.trans_data["Y_Arena"+str(arenas[col])+"_Ind"+str(ind)]=pd.to_numeric(self.trans_data["Y_Arena"+str(arenas[col])+"_Ind"+str(ind)], errors='coerce').fillna("NA")
                        ind+=1
                else:
                    self.trans_data["X"] = self.or_data.iloc[:, [int(columnsX[0])]].copy()
                    self.trans_data["Y"] = self.or_data.iloc[:, [int(columnsY[0])]].copy()

                    pd.to_numeric(self.trans_data['X'],errors='coerce').fillna("NA")
                    pd.to_numeric(self.trans_data['Y'], errors='coerce').fillna("NA")

                self.Entry_X_pos.config(**Color_settings.My_colors.Entry_Base)
                self.Entry_Y_pos.config(**Color_settings.My_colors.Entry_Base)
            else:
                all_clear = False
                self.Entry_X_pos.config(**Color_settings.My_colors.Entry_error)
                self.Entry_Y_pos.config(**Color_settings.My_colors.Entry_error)


            #We fill the NAs:
            if self.orga_ind.get()==0:
                missing_rows=sorted(set(range(self.trans_data.Frame.iat[0], self.trans_data.Frame.iat[-1])) - set(self.trans_data["Frame"]))

                missing_rows=pd.DataFrame(missing_rows, columns=["Frame"])

                missing_rows["Time"] = missing_rows["Frame"].copy()
                missing_rows["Time"] = pd.to_numeric(missing_rows["Time"])
                missing_rows["Time"] = missing_rows["Time"].div(self.Vid.Frame_rate[1])

                for col in self.trans_data.columns:
                    if col!="Time" and col !="Frame":
                        missing_rows[col]="NA"

                self.trans_data=pd.concat([self.trans_data, missing_rows])
                self.trans_data=self.trans_data.sort_values(["Frame"])

            self.table_new = Table(self.res_Tab, dataframe=self.trans_data, showtoolbar=False, showstatusbar=False)

            self.table_new.show()
            self.resize_columns(self.table_new)

        else:
            self.Entry_Sep.config(**Color_settings.My_colors.Entry_error)
            all_clear=False


        if all_clear:
            self.BValidate.config(state="normal", bg=self.list_colors["Validate"], fg=self.list_colors["Fg_Validate"])
        else:
            self.BValidate.config(state="disable", **Color_settings.My_colors.Button_Base)



    def resize_columns(self, table):
        cols = table.model.getColumnCount()
        for col in range(cols):
            colname = table.model.getColumnName(col)
            t=len(colname)
            l = table.model.getlongestEntry(col)
            l =max(l,t)
            txt = ''.join(['X' for i in range(l)])
            tw,tl = util.getTextLength(txt, table.maxcellwidth, font=table.thefont)
            table.columnwidths[colname] = tw

    def stay_on_top(self):
        #This function ensure that this window will always be in front of the others
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)

    def End_of_win(self):
        self.parent.destroy()
        self.destroy()
        self.boss.afficher_projects()
        self.boss.bind_everything()
        self.boss.save()
        self.boss.update()
        self.boss.update_selections()
        self.boss.update_row_display()
        self.unbind_all("<Return>")
        self.grab_release()


    def validate(self, *args):
        #Save the user's choice
        #End of this window
        self.Vid.Identities = []
        self.Vid.Sequences = []

        if self.orga_ind.get()==1:
            self.Vid.Track[1][8] = False
            nb_ind=len(list(pd.unique(self.trans_data["Ind"])))
            for Ind in list(pd.unique(self.trans_data["Ind"])):
                self.Vid.Identities.append([0, str(Ind), Diverse_functions.random_color()[0]])  # 0: identity of target, from 0 to N, 1: in which arene, 2:Name of the target, 3:Color of the target
                self.Vid.Sequences.append([Interface_sequences.full_sequence])
        else:
            self.Vid.Track[1][8] = True
            nb_ind=int((len(self.trans_data.columns)-2)/2)
            if int(sum(self.Vid.Track[1][6])) == nb_ind:
                passed = 0
                arena = 0
                for Ind in range(int((len(self.trans_data.columns)-2)/2)):
                    self.Vid.Identities.append([arena, "Ind"+str(Ind), Diverse_functions.random_color()[0]])  # 0: identity of target, from 0 to N, 1: in which arene, 2:Name of the target, 3:Color of the target
                    self.Vid.Sequences.append([Interface_sequences.full_sequence])
                    passed+=1
                    if passed>=int(sum(self.Vid.Track[1][6][0:(arena+1)])):
                        arena+=1

            else:
                for Ind in range(int((len(self.trans_data.columns)-2)/2)):
                    self.Vid.Identities.append([0, "Ind"+str(Ind), Diverse_functions.random_color()[0]])  # 0: identity of target, from 0 to N, 1: in which arene, 2:Name of the target, 3:Color of the target
                    self.Vid.Sequences.append([Interface_sequences.full_sequence])

                self.Vid.Track[1][6] = [0 for i in self.Vid.Track[1][6]]
                self.Vid.Track[1][6][0] = nb_ind


        if self.Vid.User_Name == self.Vid.Name:
            file_name = self.Vid.Name
            point_pos = file_name.rfind(".")
            if file_name[point_pos:].lower() != ".avi":
                file_name = self.Vid.User_Name
            else:
                file_name = file_name[:point_pos]
        else:
            file_name = self.Vid.User_Name

        if not os.path.isdir(os.path.join(self.boss.folder, "coordinates")):
            os.makedirs(os.path.join(self.boss.folder, "coordinates"))

        To_save = os.path.join(self.boss.folder, "Coordinates", file_name + "_Coordinates.csv")
        self.trans_data.to_csv(To_save, sep=";", index=False)

        self.Vid.Tracked = True
        self.Vid.saved_repartition = copy.deepcopy(self.Vid.Track[1][6])
        self.Vid.Identities_saved = copy.deepcopy(self.Vid.Identities)
        self.Vid.Sequences_saved = copy.deepcopy(self.Vid.Sequences)

        self.boss.import_values={"Sep": self.sep.get(), "Header": self.header.get(), "Fr_col":self.Fr_pos.get(), "Time_col":self.Time_pos.get(),"Ind_col":self.orga_ind.get(),"ID_col":self.ID_pos.get(),"Col_x":self.Col_X.get(), "Col_y":self.Col_Y.get()}#The defaults value for importing data

        self.End_of_win()

