from tksheet import Sheet
from tkinter import filedialog
from tkinter import *
import os
from AnimalTA.A_General_tools import Function_draw_arenas as Dr, Color_settings, UserMessages
import csv


class table(Frame):
    def __init__(self, parent,main):
        Frame.__init__(self, parent,main)
        self.config(**Color_settings.My_colors.Frame_Base)

        parent.grid_columnconfigure(0, weight = 1)
        parent.grid_rowconfigure(0, weight = 1)
        parent.grid_columnconfigure(0, weight = 1)
        parent.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)



        #Messages importation
        self.Messages = UserMessages.get_dict()

        table=[]
        to_highlight = []
        ID=0
        for V in main.liste_of_videos:
            if V.User_Name!=V.Name:
                to_highlight.append([ID,0])

            if V.Rotation>0:
                to_highlight.append([ID,1])

            if V.Frame_rate[1]!=V.Frame_rate[0]:
                to_highlight.append([ID,2])

            if V.Cropped[0]>0:
                to_highlight.append([ID,3])
                to_highlight.append([ID,4])

            if V.Cropped_sp[0]:
                to_highlight.append([ID,5])
                to_highlight.append([ID, 6])

            if V.Stab[0]:
                to_highlight.append([ID,7])

            if V.Back[0]>0:
                to_highlight.append([ID,8])

            if V.Mask[0]:
                to_highlight.append([ID,9])
                Arenas = Dr.get_arenas(V)
                nb_arenas = len(Arenas)
            else:
                nb_arenas=1

            if V.Scale[0]!=1:
                to_highlight.append([ID,10])

            if V.Track[0]:
                track=True
                to_highlight.append([ID,11])
            else:
                track=False

            if V.Tracked:
                to_highlight.append([ID,12])

            point_pos = V.Name.rfind(".")
            file_tracked_Corr = os.path.join(V.Folder, "corrected_coordinates",
                                             V.Name[:point_pos] + "_Corrected.csv")
            file_trackedP_Coor = os.path.join(V.Folder, "corrected_coordinates",
                                              V.User_Name + "_Corrected.csv")
            corrected=os.path.isfile(file_tracked_Corr) or os.path.isfile(file_trackedP_Coor)

            if corrected:
                to_highlight.append([ID, 13])



            ids_changed=False
            if V.Tracked:
                ids_changed=[name[1] for name in V.Identities] != [name[1] for name in V.Identities_saved]

                if ids_changed:
                    to_highlight.append([ID, 14])

            table.append([V.User_Name,#1
                          V.Rotation*90,#2
                          V.Frame_rate[1],#3
                          V.Cropped[0],#4
                          V.Cropped[1][0]/V.Frame_rate[0],#5
                          V.Cropped[1][1]/V.Frame_rate[0],#6
                          round((V.Cropped[1][1]-V.Cropped[1][0]+1)/V.Frame_rate[0],3),#7
                          V.Cropped_sp[0],#8
                          V.Cropped_sp[1][1],#9
                          V.Cropped_sp[1][0],#10
                          str(V.shape[0]) + ", " + str(V.shape[1]),#11
                          V.Stab[0],#12
                          V.Back[0]>0,#13
                          nb_arenas, #14
                          str(round(V.Scale[0],3))+" px/"+ V.Scale[1],#15
                          track,#16
                          V.Tracked,#17
                          corrected,#18
                          ids_changed])#19
            ID+=1

        self.sheet = Sheet(self, data = table, headers=[self.Messages["Summary_Table_headers1"],
                                                        self.Messages["Summary_Table_headers2"],
                                                        self.Messages["Summary_Table_headers3"],
                                                        self.Messages["Summary_Table_headers4"],
                                                        self.Messages["Summary_Table_headers4b"],
                                                        self.Messages["Summary_Table_headers4c"],
                                                        self.Messages["Summary_Table_headers5"],
                                                        self.Messages["Summary_Table_headers6"],
                                                        self.Messages["Summary_Table_headers6b"],
                                                        self.Messages["Summary_Table_headers6c"],
                                                        self.Messages["Summary_Table_headers7"],
                                                        self.Messages["Summary_Table_headers8"],
                                                        self.Messages["Names7"],
                                                        self.Messages["Names8"],
                                                        self.Messages["Summary_Table_headers9"],
                                                        self.Messages["Summary_Table_headers10"],
                                                        self.Messages["Summary_Table_headers11"],
                                                        self.Messages["Summary_Table_headers12"],
                                                        self.Messages["Summary_Table_headers13"]])
        self.sheet.set_options(top_left_bg=Color_settings.My_colors.list_colors["Table1"],
                               top_left_fg=Color_settings.My_colors.list_colors["Table1"],
                               top_left_fg_highlight=Color_settings.My_colors.list_colors["Table_grid"],

                               table_bg = Color_settings.My_colors.list_colors["Table1"],
                               table_fg=Color_settings.My_colors.list_colors["Fg_T1"],
                               table_grid_fg=Color_settings.My_colors.list_colors["Table_grid"],

                               table_selected_box_cells_fg=Color_settings.My_colors.list_colors["Fg_Table_selected_cell"],
                               table_selected_box_rows_fg=Color_settings.My_colors.list_colors["Fg_Table_selected_cell"],
                               table_selected_box_columns_fg=Color_settings.My_colors.list_colors["Fg_Table_selected_cell"],
                               table_selected_cells_border_fg=Color_settings.My_colors.list_colors["Fg_Table_selected_cell"],
                               table_selected_cells_bg=Color_settings.My_colors.list_colors["Table_selected_cell"],
                               table_selected_cells_fg=Color_settings.My_colors.list_colors["Fg_Table_selected_cell"],
                               table_selected_rows_border_fg=Color_settings.My_colors.list_colors["Fg_Table_selected_cell"],
                               table_selected_rows_bg=Color_settings.My_colors.list_colors["Table_selected_cell"],
                               table_selected_rows_fg=Color_settings.My_colors.list_colors["Fg_Table_selected_cell"],
                               table_selected_columns_border_fg=Color_settings.My_colors.list_colors["Fg_Table_selected_cell"],
                               table_selected_columns_bg=Color_settings.My_colors.list_colors["Table_selected_cell"],
                               table_selected_columns_fg=Color_settings.My_colors.list_colors["Fg_Table_selected_cell"],

                               header_bg=Color_settings.My_colors.list_colors["Table_header"],
                               header_fg=Color_settings.My_colors.list_colors["Fg_Table_header"],
                               header_grid_fg=Color_settings.My_colors.list_colors["Table_grid"],
                               header_selected_cells_bg=Color_settings.My_colors.list_colors["Table_row_col_titles_selected"],
                               header_selected_cells_fg=Color_settings.My_colors.list_colors["Fg_Table_row_col_titles_selected"],
                               header_selected_columns_bg=Color_settings.My_colors.list_colors["Table_row_col_titles_selected"],
                               header_selected_columns_fg=Color_settings.My_colors.list_colors["Fg_Table_row_col_titles_selected"],

                               index_bg=Color_settings.My_colors.list_colors["Table_header"],
                               index_fg=Color_settings.My_colors.list_colors["Fg_Table_header"],
                               index_grid_fg=Color_settings.My_colors.list_colors["Table_grid"],
                               index_selected_cells_bg=Color_settings.My_colors.list_colors["Table_row_col_titles_selected"],
                               index_selected_cells_fg=Color_settings.My_colors.list_colors["Fg_Table_row_col_titles_selected"],
                               index_selected_rows_bg=Color_settings.My_colors.list_colors["Table_row_col_titles_selected"],
                               index_selected_rows_fg=Color_settings.My_colors.list_colors["Fg_Table_row_col_titles_selected"],

                               outline_thickness=1,
                               outline_color=Color_settings.My_colors.list_colors["Table_grid"],
                               frame_bg=Color_settings.My_colors.list_colors["Table_selected_cell"],
                               resizing_line_fg=Color_settings.My_colors.list_colors["Table_grid"],
                               drag_and_drop_bg=Color_settings.My_colors.list_colors["Table_grid"],

        )

        for Cell in to_highlight:
            self.sheet.highlight_cells(row=Cell[0], column=Cell[1], bg=Color_settings.My_colors.list_colors["Button_done"], fg=Color_settings.My_colors.list_colors["Fg_Button_done"])

        self.sheet.enable_bindings()
        self.grid(row = 0, column = 0, sticky = "nswe")
        self.sheet.grid(row = 0, column = 0, sticky = "nswe")

        Button(self,text=self.Messages["GButton3"], command=self.save, **Color_settings.My_colors.Button_Base).grid(row = 1, column = 0, sticky = "nswe")

    def save(self):
        file = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=(("Table", "*.csv"),))
        if file != "":
            data = self.sheet.get_sheet_data()
            with open(file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.sheet.headers())
                writer.writerows(data)

