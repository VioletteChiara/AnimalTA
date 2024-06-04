from AnimalTA.A_General_tools import  UserMessages
import os
import pickle


class Color_GUI:
    def __init__(self):
        self.Button_Base = {}
        self.Scale_Base = {}
        self.Frame_Base = {}
        self.Entry_error = {}
        self.Entry_Base = {}
        self.list_colors=self.refresh()


    def refresh(self):
        # We first define what kind of backgroudn we want:
        Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
        with open(Param_file, 'rb') as fp:
            Params = pickle.load(fp)

        if Params["Color_GUI"]=="Dark":
            self.list_colors={}
        #elif Params["Color_GUI"]=="Light":
        self.list_colors = {"Table1":"#fefdfb",
                            "Table2":"#e5ecff",
                            "Glider_T1":"#dbd8ba",
                            "Glider_T2":"#abb5d6",
                            "Fg_T1": "black",
                            "Fg_T2": "black",
                            "Rad_T1": "white",
                            "Rad_T2": "white",
                            "Separator_T1":"grey40",
                            "Title1":"RoyalBlue2",
                            "Fg_Title1":"white",
                            "Frame":"RoyalBlue4",
                            "Title_ana":"#6495ed",

                            "Base":"#f0f0f0",
                            "Fg_Base":"black",
                            "Base_ina": "#f0f0f0",
                            "Fg_Base_ina": "#6D6D6D",
                            "Border_Base": "#f0f0f0",
                            "Glider_Base":"grey80",
                            "Rad_Base":"white",

                            "Selected_Base": "#0078D7",
                            "Fg_Selected_Base": "white",

                            "Selected_main":"#8AE766",
                            "Not_selected_main":"#C90505",
                            "Fusion_main":"#B632AA",

                            "Entry_Base": "white",
                            "Fg_Entry_Base": "black",

                            "Entry_error": "#C90505",
                            "Fg_Entry_error": "white",

                            "Button_ready":"#ECDD41",
                            "Fg_Button_ready": "black",
                            "Button_done": "#3aa6ff",
                            "Fg_Button_done": "black",
                            "Button_half": "#bfe62b",
                            "Fg_Button_half": "black",

                            "Entry_dark": "darkgrey",
                            "Validate":"#8AE766",
                            "Fg_Validate":"black",
                            "Moving_arrows":"#e5ecff",

                            "Loading_before":"red",
                            "Loading_after":"blue",

                            "Timeline_out":"grey",
                            "Timeline_deb":"#3800D6",
                            "Timeline_in": "#8E3E9F",
                            "Timeline_end": "#D60000",
                            "Timeline_back": "#f0f0f0",
                            "Fg_Timeline":"black",

                            "Cancel":"#FFC251",
                            "Fg_Cancel": "black",

                            "Danger":"#DB0000",
                            "Fg_Danger": "white",

                            "Fg_valide":"#0BB02C",
                            "Fg_not_valide":"#9F0000",

                            "Table_header":"grey95",
                            "Fg_Table_header": "black",
                            "Table_grid":"grey20",
                            "Table_row_col_titles_selected": "#B19EFF",
                            "Fg_Table_row_col_titles_selected": "#1E0D64",
                            "Table_selected_cell": "#EEEAFF",
                            "Fg_Table_selected_cell": "#1E0D64",

                            "NAs":"#ffa1a1",
                            "Fg_NAs":"black",
                            "Header_check":"grey95",
                            "Fg_Header_check":"black",
                            "Selected_row_check":"#9DD8FF",
                            "Fg_Selected_row_check":"black",

                            "NA_present":"#ffa1a1",
                            "Fg_NA_present":"black",
                            "NA_absent":"#8de3a4",
                            "Fg_NA_absent":"black",

                            "Threshold_ana":"red",
                            "Position_ana":"blue",

                            "Hilight_Frame":"green",

                            "Arrow_N_Relief_scroll":"grey30",
                            }

        if Params["Color_GUI"]=="Test":
            self.list_colors = {x:"black" for x in self.list_colors}

        self.Button_Base = {"background":self.list_colors["Base"],"activebackground":self.list_colors["Base"], "fg":self.list_colors["Fg_Base"], "activeforeground":self.list_colors["Fg_Base"], "disabledforeground":self.list_colors["Fg_Base_ina"], "highlightbackground": self.list_colors["Border_Base"]}

        self.Scale_Base = {"background": self.list_colors["Base"], "activebackground": self.list_colors["Base"],
                            "fg": self.list_colors["Fg_Base"], "troughcolor": self.list_colors["Glider_Base"], "highlightbackground": self.list_colors["Border_Base"]}

        self.Frame_Base = {"background": self.list_colors["Base"], "highlightbackground": self.list_colors["Border_Base"]}

        self.Entry_error = {"highlightbackground": self.list_colors["Border_Base"],"fg": self.list_colors["Fg_Entry_error"],"background": self.list_colors["Entry_error"],"disabledforeground":self.list_colors["Fg_Base_ina"], "disabledbackground":self.list_colors["Base_ina"]}
        self.Entry_Base = {"fg": self.list_colors["Fg_Entry_Base"],"background": self.list_colors["Entry_Base"],"highlightbackground": self.list_colors["Border_Base"],"disabledforeground":self.list_colors["Fg_Base_ina"], "disabledbackground":self.list_colors["Base_ina"], "selectbackground":self.list_colors["Selected_Base"], "selectforeground":self.list_colors["Fg_Selected_Base"]}
        self.OptnMenu_Base = {"bg":self.list_colors["Base"], "fg":self.list_colors["Fg_Base"],"activebackground":self.list_colors["Selected_Base"], "activeforeground":self.list_colors["Fg_Selected_Base"]}
        self.Checkbutton_Base={"activeforeground":self.list_colors["Fg_Base"], "fg":self.list_colors["Fg_Base"], "selectcolor":self.list_colors["Rad_Base"], "bg":self.list_colors["Base"], "activebackground":self.list_colors["Base"]}
        self.Radiobutton_Base={"activeforeground":self.list_colors["Fg_Base"], "fg":self.list_colors["Fg_Base"], "selectcolor":self.list_colors["Rad_Base"], "bg":self.list_colors["Base"], "activebackground":self.list_colors["Base"]}
        self.Label_Base={"background": self.list_colors["Base"], "highlightbackground": self.list_colors["Border_Base"], "fg":self.list_colors["Fg_Base"]}
        self.ListBox={"bg":self.list_colors["Base"], "fg":self.list_colors["Fg_Base"],"selectbackground":self.list_colors["Selected_Base"], "selectforeground":self.list_colors["Fg_Selected_Base"], "highlightbackground": self.list_colors["Border_Base"]}

        return(self.list_colors)




My_colors=Color_GUI()