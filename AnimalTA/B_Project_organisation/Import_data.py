import time
from tkinter import *
from tkinter import ttk
import cv2
from AnimalTA.A_General_tools import UserMessages, Diverse_functions, \
    Color_settings, Message_simple_question as MsgBox, \
    Function_draw_arenas as Dr, Class_loading_Frame, \
    Small_info
from AnimalTA.E_Post_tracking.b_Analyses import Interface_sequences
import copy
import os
import pandas as pd
from pandastable import Table, TableModel, util
from tkinter import filedialog
import re
import threading
import h5py


class Int_import(Frame):
    def __init__(self, parent, boss, files, Vid, physical=True, new=True, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.list_colors = Color_settings.My_colors.list_colors
        if physical:
            self.grid(sticky="nsew")
        self.parent = parent

        Grid.rowconfigure(self.parent, 0, weight=1)
        Grid.columnconfigure(self.parent, 0, weight=1)

        self.Vid = Vid
        self.boss = boss
        self.files = files

        self.config(**Color_settings.My_colors.Frame_Base)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.rowconfigure(self, 2, weight=1000)
        Grid.rowconfigure(self, 5, weight=1)
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)

        # Messages importation
        self.Messages = UserMessages.get_dict()

        self.sep = StringVar()  # Which separator does the original file use
        self.sep.set(self.boss.import_values["Sep"])

        self.header = IntVar()  # Do the original file use a header? If 0, we try to determine it automatically, 1 no header, 2 header
        self.header.set(self.boss.import_values["Header"])

        or_Tab_Label = Label(self, text=self.Messages["Import_data15"], **Color_settings.My_colors.Label_Base)
        or_Tab_Label.config(font=("Helvetica 13 bold"))
        or_Tab_Label.grid(row=1, column=0)
        self.or_Tab = Frame(self, **Color_settings.My_colors.Frame_Base)
        self.or_Tab.grid(row=2, column=0, sticky="nsew")

        res_Tab_Label = Label(self, text=self.Messages["Import_data16"], **Color_settings.My_colors.Label_Base)
        res_Tab_Label.config(font=("Helvetica 13 bold"))
        res_Tab_Label.grid(row=1, column=1)
        self.res_Tab = Frame(self, **Color_settings.My_colors.Frame_Base)
        self.res_Tab.grid(row=2, column=1, sticky="nsew")

        # Options for the user
        Frame_info = Frame(self, **Color_settings.My_colors.Frame_Base)
        Frame_info.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Choose the separator
        self.Entry_Sep = Entry(Frame_info, textvariable=self.sep, **Color_settings.My_colors.Entry_Base)
        self.Entry_Sep.grid(row=0, column=1, sticky="nsew")
        Validate_Entry = Label(Frame_info, text=self.Messages["Import_data17"] + ":",
                               **Color_settings.My_colors.Label_Base)
        Validate_Entry.grid(row=0, column=0, sticky="nsew")
        Small_info.small_info(elem=Validate_Entry, parent=self, message=self.Messages["Import_data17_expl"])
        Small_info.small_info(elem=self.Entry_Sep, parent=self, message=self.Messages["Import_data17_expl"])

        # Indicate if the header is present or no
        Check_H = Checkbutton(Frame_info, text=self.Messages["Import_data18"] + ":", variable=self.header, onvalue=2,
                              offvalue=1, command=self.create_new, **Color_settings.My_colors.Checkbutton_Base)
        Check_H.grid(row=1, column=0, columnspan=2, sticky="nsew")
        Small_info.small_info(elem=Check_H, parent=self, message=self.Messages["Import_data18_expl"])

        ttk.Separator(Frame_info, orient=VERTICAL).grid(row=0, column=2, rowspan=3, sticky="ns")
        ttk.Separator(Frame_info, orient=VERTICAL).grid(row=0, column=3, rowspan=3, sticky="ns")
        ttk.Separator(Frame_info, orient=VERTICAL).grid(row=0, column=4, rowspan=3, sticky="ns")

        # Indicate which column is the one for Frame number:
        self.Fr_pos = StringVar()
        self.Fr_pos.set(self.boss.import_values["Fr_col"])
        self.Entry_Fr_pos = Entry(Frame_info, textvariable=self.Fr_pos, **Color_settings.My_colors.Entry_Base)
        self.Entry_Fr_pos.grid(row=0, column=6, sticky="w")
        Label_fr = Label(Frame_info, text=self.Messages["Import_data1"] + ":", **Color_settings.My_colors.Label_Base)
        Label_fr.grid(row=0, column=5, sticky="w")
        Small_info.small_info(elem=Label_fr, parent=self, message=self.Messages["Import_data1_expl"])
        Small_info.small_info(elem=self.Entry_Fr_pos, parent=self, message=self.Messages["Import_data1_expl"])

        # Indicate which column is the one for Time:
        self.Time_pos = StringVar()
        self.Time_pos.set(self.boss.import_values["Time_col"])
        self.Entry_Time_pos = Entry(Frame_info, textvariable=self.Time_pos, **Color_settings.My_colors.Entry_Base)
        self.Entry_Time_pos.grid(row=1, column=6, sticky="w")
        Label_time = Label(Frame_info, text=self.Messages["Import_data2"] + ":", **Color_settings.My_colors.Label_Base)
        Label_time.grid(row=1, column=5, sticky="w")
        Small_info.small_info(elem=Label_time, parent=self, message=self.Messages["Import_data2_expl"])
        Small_info.small_info(elem=self.Entry_Time_pos, parent=self, message=self.Messages["Import_data2_expl"])

        ttk.Separator(Frame_info, orient=VERTICAL).grid(row=0, column=7, rowspan=3, sticky="ns")

        # Indicates what kind of global organisation the file has
        self.orga_ind = IntVar()
        self.orga_ind.set(self.boss.import_values["Ind_col"])
        Rad_inds_columns = Radiobutton(Frame_info, text=self.Messages["Import_data3"], variable=self.orga_ind, value=0,
                                       command=self.create_new, **Color_settings.My_colors.Radiobutton_Base)
        Rad_inds_columns.grid(row=0, column=8, columnspan=2, sticky="w")
        Rad_inds_rows = Radiobutton(Frame_info, text=self.Messages["Import_data4"], variable=self.orga_ind, value=1,
                                    command=self.create_new, **Color_settings.My_colors.Radiobutton_Base)
        Rad_inds_rows.grid(row=1, column=8, columnspan=2, sticky="w")
        Small_info.small_info(elem=Rad_inds_columns, parent=self, message=self.Messages["Import_data3_expl"])
        Small_info.small_info(elem=Rad_inds_rows, parent=self, message=self.Messages["Import_data4_expl"])

        self.ID_pos = StringVar()
        self.ID_pos.set(self.boss.import_values["ID_col"])
        Label_ID = Label(Frame_info, text="     " + self.Messages["Import_data5"] + ":",
                         **Color_settings.My_colors.Label_Base)
        Label_ID.grid(row=2, column=8)
        self.Entry_ID_column = Entry(Frame_info, textvariable=self.ID_pos)
        self.Entry_ID_column.grid(row=2, column=9)
        if self.orga_ind.get() == 0:
            self.Entry_ID_column.config(state="disabled")
        Small_info.small_info(elem=Label_ID, parent=self, message=self.Messages["Import_data5_expl"])
        Small_info.small_info(elem=self.Entry_ID_column, parent=self, message=self.Messages["Import_data5_expl"])

        ttk.Separator(Frame_info, orient=VERTICAL).grid(row=0, column=10, rowspan=3, sticky="ns")
        self.Col_X = StringVar()
        self.Col_X.set(self.boss.import_values["Col_x"])
        Label_ColX = Label(Frame_info, text=self.Messages["Import_data6"] + ":", **Color_settings.My_colors.Label_Base)
        Label_ColX.grid(row=0, column=11)
        self.Entry_X_pos = Entry(Frame_info, textvariable=self.Col_X)
        self.Entry_X_pos.grid(row=0, column=12)
        Small_info.small_info(elem=Label_ColX, parent=self, message=self.Messages["Import_data6_expl"])
        Small_info.small_info(elem=self.Entry_X_pos, parent=self, message=self.Messages["Import_data6_expl"])

        self.Col_Y = StringVar()
        self.Col_Y.set(self.boss.import_values["Col_y"])
        Label(Frame_info, text=self.Messages["Import_data7"] + ":", **Color_settings.My_colors.Label_Base).grid(row=1,
                                                                                                                column=11)
        self.Entry_Y_pos = Entry(Frame_info, textvariable=self.Col_Y)
        self.Entry_Y_pos.grid(row=1, column=12)
        Small_info.small_info(elem=Label_ColX, parent=self, message=self.Messages["Import_data7_expl"])
        Small_info.small_info(elem=self.Entry_X_pos, parent=self, message=self.Messages["Import_data7_expl"])

        ttk.Separator(Frame_info, orient=VERTICAL).grid(row=0, column=13, rowspan=3, sticky="ns")

        Validate_new_pos = Button(Frame_info, text=self.Messages["Import_data8"], command=self.create_new,
                                  **Color_settings.My_colors.Button_Base)
        Validate_new_pos.config(bg=Color_settings.My_colors.list_colors["Button_ready"],
                                fg=Color_settings.My_colors.list_colors["Fg_Button_ready"])
        Validate_new_pos.grid(row=3, column=0, columnspan=14, sticky="nsew")
        Small_info.small_info(elem=Validate_new_pos, parent=self, message=self.Messages["Import_data8_expl"])

        Grid.rowconfigure(Frame_info, 0, weight=1)
        Grid.rowconfigure(Frame_info, 1, weight=1)
        Grid.rowconfigure(Frame_info, 2, weight=1)
        Grid.rowconfigure(Frame_info, 3, weight=1)

        for col in range(14):
            Grid.columnconfigure(Frame_info, col, weight=100)

        Grid.columnconfigure(Frame_info, 2, weight=1)  # Separator columns are smaller
        Grid.columnconfigure(Frame_info, 3, weight=1)  # Separator columns are smaller
        Grid.columnconfigure(Frame_info, 4, weight=1)  # Separator columns are smaller
        Grid.columnconfigure(Frame_info, 7, weight=1)  # Separator columns are smaller
        Grid.columnconfigure(Frame_info, 10, weight=1)  # Separator columns are smaller
        Grid.columnconfigure(Frame_info, 13, weight=1)  # Separator columns are smaller

        # Button to validate once the position is chosen
        self.BValidate = Button(self, text=self.Messages["Validate"], **Color_settings.My_colors.Button_Base,
                                command=self.validate)
        self.BValidate.grid(row=5, column=0, sticky="nsew")
        self.BValidate.config(state="disable", **Color_settings.My_colors.Button_Base)

        B_Cancel = Button(self, text=self.Messages["Cancel"], **Color_settings.My_colors.Button_Base,
                          command=self.End_of_win)
        B_Cancel.config(background=Color_settings.My_colors.list_colors["Cancel"],
                        fg=Color_settings.My_colors.list_colors["Fg_Cancel"])
        B_Cancel.grid(row=5, column=1, sticky="nsew")

        self.Arenas = Dr.get_arenas(self.Vid)

        self.reset_ind_in_arenas()
        self.stay_on_top()
        if new:
            self.create_new()

    def reset_ind_in_arenas(self):
        self.Ind_in_arenas = [0 for A in range(len(self.Vid.Track[1][6]))]

    def load_files(self, files, show=True):
        self.reset_ind_in_arenas()
        try:
            for file in files:
                if self.header.get() == 0:
                    data = pd.read_csv(file, header=None, sep=self.sep.get(), engine='python')
                    if sum([isinstance(val, int) or isinstance(val, float) for val in data.iloc[0]]) / len(
                            data.iloc[0]) < 0.75:
                        data.columns = data.iloc[0]
                        data = data[1:]
                        self.header.set(2)
                        data = data.rename(
                            columns={col: str(idx + 1) + " | " + col for idx, col in enumerate(data.columns)})
                    else:
                        self.header.set(1)

                elif self.header.get() == 2:
                    data = pd.read_csv(file, header=0, sep=self.sep.get(), engine='python', na_filter=False)
                    data = data.rename(
                        columns={col: str(idx + 1) + " | " + col for idx, col in enumerate(data.columns)})
                else:
                    data = pd.read_csv(file, header=None, sep=self.sep.get(), engine='python', na_filter=False)

                self.or_data = data
                self.table = Table(self.or_Tab, dataframe=data, showtoolbar=False, showstatusbar=False)
                if show:
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
        # Find all X columns:
        try:
            if char != "":
                if ("[" == char[0] and "]" == char[-1]) or self.is_number(
                        char):  # If the user gave a column number or a list of columns
                    char = char.replace(" ", "")
                    if ("[" == char[0] and "]" == char[-1]):
                        list_columns = char[1:-1].split(",")
                        list_columns = [int(val) - 1 for val in list_columns]
                    else:
                        list_columns = [int(char) - 1]

                    return (True, list_columns)

                else:
                    correct = [idx for idx, name in enumerate(self.or_data.columns.values) if char == name]
                    list_columns = [idx for idx, name in enumerate(self.or_data.columns.values) if
                                    char in name and not char == name]
                    list_columns = correct + list_columns
                    if len(list_columns) > 0:
                        return (True, list_columns)
                    else:
                        return (False, [])
            else:
                return (False, [])
        except:
            return (False, [])

    def create_new(self):
        all_clear = True
        show_warn = False

        loaded = self.load_files(self.files)
        if loaded:
            self.Entry_Sep.config(**Color_settings.My_colors.Entry_Base)

            if self.orga_ind.get() == 0:
                self.Entry_ID_column.config(state="disabled")
            else:
                self.Entry_ID_column.config(state="normal")

            Fr_pos_found = False
            Time_pos_found = False
            if self.Fr_pos.get() != "":
                column = self.find_column(self.Fr_pos.get(), self.or_data.columns)
                if not column is None:
                    Frames = pd.DataFrame(self.or_data[[column]].copy())
                    self.trans_data = add_Time_from_frames(Frames, self.Vid)
                    self.Entry_Fr_pos.config(**Color_settings.My_colors.Entry_Base)
                    Fr_pos_found = True

            if not Fr_pos_found and self.Time_pos.get() != "":
                column = self.find_column(self.Time_pos.get(), self.or_data.columns)
                if not column is None:
                    self.trans_data = pd.DataFrame(self.or_data[[column]].copy())
                    self.trans_data.columns = ["Time"]
                    self.trans_data["Frame"] = self.trans_data["Time"].copy()
                    self.trans_data["Frame"] = pd.to_numeric(self.trans_data["Frame"])
                    self.trans_data["Frame"] = self.trans_data["Frame"].multiply(self.Vid.Frame_rate[1])
                    self.trans_data["Frame"] = self.trans_data["Frame"].round()
                    self.trans_data["Frame"] = self.trans_data.Frame.astype(int)
                    self.trans_data = self.trans_data[["Frame", "Time"]]
                    self.Entry_Time_pos.config(**Color_settings.My_colors.Entry_Base)
                    Time_pos_found = True

            if not Time_pos_found and not Fr_pos_found:
                one_every = self.Vid.Frame_rate[0] / self.Vid.Frame_rate[1]
                fr_col = range(round(self.Vid.Cropped[1][0] / one_every), round(self.Vid.Cropped[1][1] / one_every + 1))
                self.trans_data = pd.DataFrame(fr_col, columns=['Frame'])
                self.trans_data["Time"] = fr_col
                self.trans_data["Time"] = self.trans_data["Time"].div(self.Vid.Frame_rate[1])
                self.Entry_Time_pos.config(**Color_settings.My_colors.Entry_error)
                self.Entry_Fr_pos.config(**Color_settings.My_colors.Entry_error)

            if self.orga_ind.get() == 1:
                ID_ok = False
                self.trans_data["Arena"] = 0
                self.trans_data["Ind"] = ""
                if self.ID_pos.get() != "":
                    ID_ok = True
                    selected_columns = self.ID_pos.get().split("+")
                    for SC in selected_columns:
                        if SC[0] == "\"" and SC[-1] == "\"":
                            self.trans_data["Ind"] = self.trans_data["Ind"].astype(str) + SC[1:-1]
                        else:
                            column = self.find_column(SC, self.or_data.columns)
                            if not column is None:
                                self.trans_data["Ind"] = self.trans_data["Ind"].astype(str) + self.or_data[
                                    column].astype(str)
                            else:
                                ID_ok = False

                if not ID_ok:
                    self.trans_data.drop(columns=["Ind"])
                    self.Entry_ID_column.config(**Color_settings.My_colors.Entry_error)
                    all_clear = False
                else:
                    self.Entry_ID_column.config(**Color_settings.My_colors.Entry_Base)

            # Driver code
            valideX, columnsX = self.extract_row_number(self.Col_X.get())
            valideY, columnsY = self.extract_row_number(self.Col_Y.get())
            if valideX and valideY and len(columnsX) == len(columnsY):
                if self.orga_ind.get() == 0:
                    [0] * len(columnsX)
                    if len(self.Vid.Track[1][6]) > 1:
                        for I in range(len(columnsX)):
                            colX = self.or_data.iloc[:, columnsX[I]]  # ← Series, not DataFrame
                            colX = pd.to_numeric(colX, errors='coerce')
                            X_mean = int(colX.mean())

                            colY = self.or_data.iloc[:, columnsY[I]]
                            colY = pd.to_numeric(colY, errors='coerce')
                            Y_mean = int(colY.mean())

                            show_warn_ind, Are = find_ind_ar(self.Arenas, [X_mean, Y_mean])
                            self.Ind_in_arenas[Are] += 1
                            if show_warn_ind:
                                show_warn = True

                    else:
                        Are = 0
                        self.Ind_in_arenas[Are] = len(columnsX)

                    ind = 0
                    for col in range(len(columnsX)):
                        self.trans_data["X_Arena" + str(Are) + "_Ind" + str(ind)] = self.or_data.iloc[:,
                                                                                    [int(columnsX[col])]].copy()
                        self.trans_data["Y_Arena" + str(Are) + "_Ind" + str(ind)] = self.or_data.iloc[:,
                                                                                    [int(columnsY[col])]].copy()
                        self.trans_data["X_Arena" + str(Are) + "_Ind" + str(ind)] = pd.to_numeric(
                            self.trans_data["X_Arena" + str(Are) + "_Ind" + str(ind)], errors='coerce').fillna("NA")
                        self.trans_data["Y_Arena" + str(Are) + "_Ind" + str(ind)] = pd.to_numeric(
                            self.trans_data["Y_Arena" + str(Are) + "_Ind" + str(ind)], errors='coerce').fillna("NA")
                        ind += 1
                else:

                    Load_show = Class_loading_Frame.Loading(self.parent, text=self.Messages["Import_data9"])
                    Load_show.grid()
                    completed_parts = []

                    for col in range(len(columnsX)):
                        Load_show.show_load(col / len(columnsX))

                        sub_trans = self.trans_data.copy()

                        sub_trans["X"] = pd.to_numeric(
                            self.or_data.iloc[:, int(columnsX[col])],
                            errors="coerce"
                        )
                        sub_trans["Y"] = pd.to_numeric(
                            self.or_data.iloc[:, int(columnsY[col])],
                            errors="coerce"
                        )

                        means = (
                            sub_trans
                                .groupby("Ind")[["X", "Y"]]
                                .mean()
                                .round()
                                .fillna(0)
                                .astype(int)
                        )

                        arena_map = {}

                        pos = 0
                        for ind, row in means.iterrows():
                            Load_show.show_load((1 / len(columnsX)) * (pos / len(means)) + col / len(columnsX))
                            pos += 1

                            if len(self.Vid.Track[1][6]) > 1:
                                show_warn_ind, Are = find_ind_ar(self.Arenas, [float(row["X"]), float(row["Y"])])
                            else:
                                Are = 0

                            arena_map[ind] = Are
                            self.Ind_in_arenas[Are] += 1

                        sub_trans["Arena"] = sub_trans["Ind"].map(arena_map)

                        if len(columnsX) > 1:
                            suffix = "_" + self.or_data.columns[int(columnsX[col])]
                            sub_trans["Ind"] = sub_trans["Ind"] + suffix

                        sub_trans[["X", "Y"]] = sub_trans[["X", "Y"]].fillna("NA")

                        completed_parts.append(sub_trans)

                    completed_table = pd.concat(completed_parts, ignore_index=True)
                    self.trans_data = completed_table

                    Load_show.destroy()
                    del Load_show

                self.Entry_X_pos.config(**Color_settings.My_colors.Entry_Base)
                self.Entry_Y_pos.config(**Color_settings.My_colors.Entry_Base)
            else:
                all_clear = False
                self.Entry_X_pos.config(**Color_settings.My_colors.Entry_error)
                self.Entry_Y_pos.config(**Color_settings.My_colors.Entry_error)

            # We fill the NAs:
            if self.orga_ind.get() == 0:
                missing_rows = sorted(set(range(self.trans_data.Frame.iat[0], self.trans_data.Frame.iat[-1])) - set(
                    self.trans_data["Frame"]))
                missing_rows = pd.DataFrame(missing_rows, columns=["Frame"])

                missing_rows["Time"] = missing_rows["Frame"].copy()
                missing_rows["Time"] = pd.to_numeric(missing_rows["Time"])
                missing_rows["Time"] = missing_rows["Time"].div(self.Vid.Frame_rate[1])

                for col in self.trans_data.columns:
                    if col != "Time" and col != "Frame":
                        missing_rows[col] = "NA"

                self.trans_data = pd.concat([self.trans_data, missing_rows])

            if self.orga_ind.get() == 0:
                self.trans_data = orga_table(self.trans_data)

            if self.orga_ind.get() == 1:
                self.trans_data = self.trans_data.sort_values(["Frame", "Ind"])
            else:
                self.trans_data = self.trans_data.sort_values(["Frame"])
            self.table_new = Table(self.res_Tab, dataframe=self.trans_data, showtoolbar=False, showstatusbar=False)

            self.table_new.show()
            self.resize_columns(self.table_new)

        else:
            self.Entry_Sep.config(**Color_settings.My_colors.Entry_error)
            all_clear = False

        if all_clear:
            self.BValidate.config(state="normal", bg=self.list_colors["Validate"], fg=self.list_colors["Fg_Validate"])
        else:
            self.BValidate.config(state="disable", **Color_settings.My_colors.Button_Base)


        return (show_warn)

    def resize_columns(self, table):
        cols = table.model.getColumnCount()
        for col in range(cols):
            colname = table.model.getColumnName(col)
            t = len(colname)
            l = table.model.getlongestEntry(col)
            l = max(l, t)
            txt = ''.join(['X' for i in range(l)])
            tw, tl = util.getTextLength(txt, table.maxcellwidth, font=table.thefont)
            table.columnwidths[colname] = tw

    def stay_on_top(self):
        # This function ensure that this window will always be in front of the others
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)

    def End_of_win(self, bind=True):
        return_to_boss(self.boss, bind)
        self.unbind_all("<Return>")
        self.grab_release()
        self.parent.destroy()
        self.destroy()

    def validate(self, *args):
        # Save the user's choice
        # End of this window
        load_frame = Class_loading_Frame.Loading(self, text="Saving file")  # Progression bar CTXT
        load_frame.grid(sticky="ew", row=16, columnspan=2)

        save_th = threading.Thread(
            target=self.save_and_finish,
            daemon=True
        )
        save_th.start()

        load_frame.show_loading_while(save_th)

        load_frame.destroy()
        del load_frame

    def save_and_finish(self, *args):

        save_vid(type=self.orga_ind.get(), Vid=self.Vid, boss=self.boss, new_tab=self.trans_data,
                 new_IDs=self.Ind_in_arenas)
        self.boss.import_values = {"Sep": self.sep.get(), "Header": self.header.get(), "Fr_col": self.Fr_pos.get(),
                                   "Time_col": self.Time_pos.get(), "Ind_col": self.orga_ind.get(),
                                   "ID_col": self.ID_pos.get(), "Col_x": self.Col_X.get(),
                                   "Col_y": self.Col_Y.get()}  # The defaults value for importing data
        self.End_of_win()

    def find_column(self, SC, columns):
        columns_adjusted = [col.split(" | ")[1] for col in columns]
        if SC in self.or_data.columns:
            column_name = columns[int(columns.get_loc(SC))]
        elif SC in columns_adjusted:
            column_name = columns[columns_adjusted.index(SC)]
        elif SC.isdigit() and int(SC) > 0 and int(SC) < len(self.or_data.columns):
            column_name = columns[int(SC) - 1]
        else:
            column_name = None

        return (column_name)


def import_listed(prog, Vid, boss):
    Messages = UserMessages.get_dict()

    show_warn = False  # The individuals are inside arenas
    type_data = 0  # Data are organised in columns
    names = None  # If individuals do have a name attributed

    # We begin by preparing the rows with Frames and Time:
    Frames = create_Frames(Vid)
    new_tab = add_Time_from_frames(Frames, Vid)

    # We then prepare the list of individuals
    Ind_in_arenas = [0 for A in range(len(Vid.Track[1][6]))]
    Arenas = Dr.get_arenas(Vid)

    boss.unbind_everything()

    if prog == "AnimalTA":
        file = filedialog.askopenfile()
        file = file.name

        # load the data file
        DataFrame = pd.read_csv(file, sep=";", header=0, engine='python', na_filter=True, index_col=None)
        nb_ind = int((len(DataFrame.columns) - 2) / 2)

        for ind in range(nb_ind):
            if len(Vid.Track[1][6]) > 1:
                X_mean = int(DataFrame.iloc[:, 2 + 2 * ind].mean())
                Y_mean = int(DataFrame.iloc[:, 3 + 2 * ind].mean())
                show_warn_ind, Are = find_ind_ar(Arenas, [X_mean, Y_mean])
                Ind_in_arenas[Are] += 1
                if show_warn_ind:
                    show_warn = True
            else:
                Are = 0
                Ind_in_arenas[0] += 1

            # Rename columns
            sub_data = DataFrame[["Frame", DataFrame.columns[2 + 2 * ind], DataFrame.columns[3 + 2 * ind]]]
            sub_data.columns = ["Frame", "X_Arena" + str(Are) + "_Ind" + str(Ind_in_arenas[Are] - 1),
                                "Y_Arena" + str(Are) + "_Ind" + str(Ind_in_arenas[Are] - 1)]
            # We reorganise the table
            new_tab = pd.merge(new_tab, sub_data, on="Frame", how='left')

        new_tab = orga_table(new_tab)
        new_tab = new_tab.fillna("NA")



    elif prog == "ToxTrack":
        # If you wish to import data from a ToxTrack project, indicate the path for the folder "Project_ToxTrack/My_Video/".
        # You must have first saved the results of the trackings from ToxTrack (Results > Statistics > Save Results) without applying calibration
        data_folder = filedialog.askdirectory()
        all_files = os.listdir(data_folder)
        all_files = [file for file in all_files if bool(re.search('Tracking_RealSpace_', file))]

        if not (len(all_files)) > 0:
            question = MsgBox.Messagebox(parent=boss, title=Messages["Import_data10"],
                                         message=Messages["Import_data11"],
                                         Possibilities=[Messages["Continue"]])
            boss.wait_window(question)
            return

        else:
            Load_show = Class_loading_Frame.Loading(boss, text=Messages["Import_data12"])
            Load_show.grid()

            Load_show.show_load(0)

            for arena_idx, arena_file in enumerate(all_files):
                Load_show.show_load(arena_idx / len(all_files))

                arena_df = pd.read_csv(os.path.join(data_folder, arena_file), sep="\t", header=0, engine='python',
                                       na_filter=False, index_col=None)
                arena_df.rename(columns={arena_df.columns[0]: "Frame"}, inplace=True)
                arena_df["Frame"] = (arena_df["Frame"] * Vid.Frame_rate[1]).round()  # We convert Time to Frame

                # Ind ID is saved in a column
                for ind in arena_df["Track"].unique():
                    Load_show.show_load(
                        arena_idx / len(all_files) + (ind / (len(arena_df["Track"].unique()))) * (1 / len(all_files)))
                    filtered_df = arena_df[arena_df.iloc[:, 2] == ind]
                    filtered_df.columns = ["Frame", "_", "Ind", "X", "Y", "_1"]

                    # If there is more than one arena, we associte the individuals with corresponding arenas
                    if len(Vid.Track[1][6]) > 1:
                        X_mean = int(filtered_df["X"].mean())
                        Y_mean = int(filtered_df["Y"].mean())
                        show_warn_ind, Are = find_ind_ar(Arenas, [X_mean, Y_mean])
                        Ind_in_arenas[Are] += 1
                        if show_warn_ind:
                            show_warn = True
                    else:
                        Are = 0
                        Ind_in_arenas[0] += 1

                    filtered_df.columns = ["Frame", "_", "Ind",
                                           "X_Arena" + str(Are) + "_Ind" + str(Ind_in_arenas[Are] - 1),
                                           "Y_Arena" + str(Are) + "_Ind" + str(Ind_in_arenas[Are] - 1), "_"]
                    # We reorganise the table
                    new_tab = pd.merge(new_tab, filtered_df[
                        ["Frame", "X_Arena" + str(Are) + "_Ind" + str(Ind_in_arenas[Are] - 1),
                         "Y_Arena" + str(Are) + "_Ind" + str(Ind_in_arenas[Are] - 1)]], on="Frame", how='left')
        new_tab = orga_table(new_tab)
        new_tab = new_tab.fillna("NA")

    elif prog == "SLEAP":
        file = filedialog.askopenfile()
        file = file.name

        # load the data file
        newWindow = Toplevel(boss)
        importation_class = Int_import(newWindow, boss, [file], Vid=Vid, physical=False, new=False)

        importation_class.sep.set(",")
        importation_class.header.set(2)
        importation_class.Fr_pos.set("2")
        importation_class.orga_ind.set(1)
        importation_class.ID_pos.set("track")

        importation_class.load_files(importation_class.files, show=False)
        nb_ind = int((len(importation_class.or_data.columns) - 3) / 3)

        importation_class.Col_X.set(str(list(range(4, (((nb_ind + 1) * 3)) + 1, 3))))
        importation_class.Col_Y.set(str(list(range(5, ((nb_ind + 1) * 3) + 2, 3))))
        show_warn = importation_class.create_new()
        new_tab = importation_class.trans_data.copy()
        Ind_in_arenas = importation_class.Ind_in_arenas.copy()
        importation_class.End_of_win(bind=False)
        type_data = 1

    elif prog == "Loopy":
        file = filedialog.askopenfile()
        file = file.name

        # load the data file
        newWindow = Toplevel(boss)
        importation_class = Int_import(newWindow, boss, [file], Vid=Vid, physical=False, new=False)

        importation_class.sep.set(",")
        importation_class.header.set(2)
        importation_class.Fr_pos.set("5")
        importation_class.orga_ind.set(1)
        importation_class.ID_pos.set("name")
        importation_class.load_files(importation_class.files, show=False)
        importation_class.Col_X.set("10")
        importation_class.Col_Y.set("11")
        show_warn = importation_class.create_new()
        new_tab = importation_class.trans_data.copy()
        Ind_in_arenas = importation_class.Ind_in_arenas.copy()
        importation_class.End_of_win(bind=False)
        type_data = 1

    elif prog == "DeepLabCut":
        file = filedialog.askopenfile()
        file = file.name
        names = [[] for A in range(len(Vid.Track[1][6]))]

        Frames = create_Frames(Vid)
        new_tab = add_Time_from_frames(Frames, Vid)

        Load_show = Class_loading_Frame.Loading(boss)
        Load_show.grid()

        Load_show.loading_state.config(text=Messages["Import_data12"])

        DataFrame = None

        def _load_hdf():
            nonlocal DataFrame
            DataFrame = pd.read_hdf(file)

        load_th = threading.Thread(
            target=_load_hdf,
            daemon=True
        )
        load_th.start()
        Load_show.show_loading_while(load_th)

        Load_show.loading_state.config(text=Messages["Import_data13"])
        Load_show.show_load(0)

        list_col = DataFrame.columns.to_list()
        all_inds = [[col[1], col[2], col[1] + "_" + col[2]] for col in list_col if col[3] == "x"]

        nb_ind = len(all_inds)
        columns_to_add = {}
        for ind in range(nb_ind):
            Load_show.show_load(ind / nb_ind)
            df_x = DataFrame.xs('x', axis=1, level='coords')
            df_x = df_x.xs(all_inds[ind][0], axis=1, level='individuals')
            df_x = df_x.xs(all_inds[ind][1], axis=1, level='bodyparts').squeeze()

            df_y = DataFrame.xs('y', axis=1, level='coords')
            df_y = df_y.xs(all_inds[ind][0], axis=1, level='individuals')
            df_y = df_y.xs(all_inds[ind][1], axis=1, level='bodyparts').squeeze()
            if len(Vid.Track[1][6]) > 1:
                X_mean = int(df_x.mean())
                Y_mean = int(df_y.mean())
                show_warn_ind, Are = find_ind_ar(Arenas, [X_mean, Y_mean])
                Ind_in_arenas[Are] += 1
                names[Are].append(all_inds[ind][2])
                if show_warn_ind:
                    show_warn = True
            else:
                Are = 0
                Ind_in_arenas[0] += 1
                names[Are].append(all_inds[ind][2])

            # We add teh new columns
            col_name = "X_Arena" + str(Are) + "_Ind" + str(Ind_in_arenas[Are] - 1)
            columns_to_add[col_name] = pd.to_numeric(df_x, errors='coerce').replace(0, "NA").fillna("NA")

            col_name = "Y_Arena" + str(Are) + "_Ind" + str(Ind_in_arenas[Are] - 1)
            columns_to_add[col_name] = pd.to_numeric(df_y, errors='coerce').replace(0, "NA").fillna("NA")

        new_tab = pd.concat([new_tab, pd.DataFrame(columns_to_add)], axis=1)
        Load_show.destroy()
        del Load_show

    Load_show = Class_loading_Frame.Loading(boss)
    Load_show.grid()
    Load_show.loading_state.config(text=Messages["Import_data14"])

    save_th = threading.Thread(
        target=save_vid,
        kwargs=dict(
            type=type_data,
            new_tab=new_tab,
            Vid=Vid,
            new_IDs=Ind_in_arenas,
            boss=boss,
            names=names
        ),
        daemon=True
    )
    save_th.start()

    Load_show.show_loading_while(save_th)

    if show_warn:
        question = MsgBox.Messagebox(parent=boss, title="Warning",
                                     message="Warning: A target spent a lot of time outside from the defined arenas, ensure that your arenas are correctly defined.",
                                     Possibilities=["Continue"])
        boss.wait_window(question)

    boss.bind_everything()
    return_to_boss(boss)
    Load_show.destroy()
    del Load_show


def orga_table(new_tab):
    first_cols = new_tab.iloc[:, :2]  # The first columns are 'Frame' and 'Time', no need to order them

    # Select the remaining columns and parse/sort them
    remaining_cols = new_tab.iloc[:, 2:]  # Skip the first column
    sorted_cols = sorted(remaining_cols.columns, key=parse_column)  # Sort column names
    remaining_cols = remaining_cols[sorted_cols]  # Reorder DataFrame columns

    # Concatenate the first column and the sorted remaining columns
    new_tab = pd.concat([first_cols, remaining_cols], axis=1)
    return new_tab


def parse_column(col):
    parts = col.split("_")
    arena = int(parts[1][5:])  # Extract arena number
    ind = int(parts[2][3:])  # Extract individual index
    xy = parts[0]  # Extract 'X' or 'Y'
    return (arena, ind, xy)


# Sort columns based on (arena, individual, 'X' before 'Y')


def find_ind_ar(Arenas, Pt):  # Find in whci arena is the point
    all_dists = []
    for idx, Are in enumerate(Arenas):
        distance = cv2.pointPolygonTest(Are, Pt, True)
        if distance >= 0:
            return (False,
                    idx)  # False/True refers to whether the target was detected inside an existing arena (False) or was associated to the closest one (True)
        else:
            all_dists.append(distance)
    return (True, all_dists.index(max(all_dists)))  # max because of the target is outside it is negative value


def return_to_boss(boss, bind=True):
    if bind:
        boss.bind_everything()
    boss.update()
    boss.update_selections()
    boss.update_row_display()
    boss.afficher_projects()
    boss.save()


def save_vid(type, new_tab, Vid, boss, new_IDs=None, names=None, load_fr=None):
    Vid.Identities = []
    Vid.Sequences = []

    if type == 1:
        Vid.Track[1][8] = False
        nb_ind = len(pd.unique(new_tab["Ind"]))
    else:
        Vid.Track[1][8] = True
        nb_ind = int((len(new_tab.columns) - 2) / 2)


    if new_IDs is None:
        new_IDs = [0 for i in Vid.Track[1][6]]
        new_IDs[0] = nb_ind

    passed = 0
    for Ar in range(len(new_IDs)):
        for ind in range(new_IDs[Ar]):
            if type == 0:
                if names == None:
                    Vid.Identities.append([Ar, "Ind" + str(ind), Diverse_functions.random_color()[
                        0]])  # 0: identity of target, from 0 to N, 1: in which arene, 2:Name of the target, 3:Color of the target
                else:
                    Vid.Identities.append([Ar, names[Ar][ind], Diverse_functions.random_color()[
                        0]])  # 0: identity of target, from 0 to N, 1: in which arene, 2:Name of the target, 3:Color of the target

            else:
                Vid.Identities.append(
                    [new_tab.loc[new_tab["Ind"] == pd.unique(new_tab["Ind"])[passed], "Arena"].iloc[0],
                     pd.unique(new_tab["Ind"])[passed], Diverse_functions.random_color()[
                         0]])  # 0: identity of target, from 0 to N, 1: in which arene, 2:Name of the target, 3:Color of the target

            passed += 1
            Vid.Sequences.append([Interface_sequences.full_sequence])

    Vid.Track[1][6] = new_IDs

    if Vid.User_Name == Vid.Name:
        file_name = Vid.Name
        point_pos = file_name.rfind(".")
        if file_name[point_pos:].lower() != ".avi":
            file_name = Vid.User_Name
        else:
            file_name = file_name[:point_pos]
    else:
        file_name = Vid.User_Name

    if not os.path.isdir(os.path.join(boss.folder, "coordinates")):
        os.makedirs(os.path.join(boss.folder, "coordinates"))

    To_save = os.path.join(boss.folder, "Coordinates", file_name + "_Coordinates.csv")
    new_tab.to_csv(To_save, sep=";", index=False)

    Vid.Tracked = True
    Vid.saved_repartition = copy.deepcopy(Vid.Track[1][6])
    Vid.Identities_saved = copy.deepcopy(Vid.Identities)
    Vid.Sequences_saved = copy.deepcopy(Vid.Sequences)


def create_Frames(Vid):
    one_every = Vid.Frame_rate[0] / Vid.Frame_rate[1]
    return pd.DataFrame(range(round(Vid.Cropped[1][0] / one_every), round(Vid.Cropped[1][1] / one_every) + 1))


def add_Time_from_frames(new_tab, Vid):
    new_tab.columns = ["Frame"]
    new_tab["Time"] = new_tab["Frame"].copy()
    new_tab["Time"] = pd.to_numeric(new_tab["Time"])
    new_tab["Time"] = new_tab["Time"].div(Vid.Frame_rate[1])
    new_tab["Frame"] = new_tab.Frame.astype(float)
    new_tab["Frame"] = new_tab["Frame"].round()
    new_tab["Frame"] = new_tab.Frame.astype(int)

    return (new_tab)


def add_missing_rows(df, Vid):
    missing_rows = sorted(set(range(df.Frame.iat[0], df.Frame.iat[-1])) - set(df["Frame"]))
    missing_rows = pd.DataFrame(missing_rows, columns=["Frame"])

    missing_rows["Time"] = missing_rows["Frame"].copy()
    missing_rows["Time"] = pd.to_numeric(missing_rows["Time"])
    missing_rows["Time"] = missing_rows["Time"].div(Vid.Frame_rate[1])

    for col in df.columns:
        if col != "Time" and col != "Frame":
            missing_rows[col] = "NA"

    new_tab = pd.concat([df, missing_rows])
    new_tab = new_tab.sort_values(["Frame"])

    return (new_tab)
