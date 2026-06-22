from tkinter import *
from tkinter import ttk
from AnimalTA.A_General_tools import Function_draw_arenas, UserMessages, Class_loading_Frame, Color_settings



class Lists(Frame):
    """ This Frame displays a list of the videos and their arenas from the project that have been tracked.
    The user can select some arenas to copy-paste there the elements of interest from the current arena"""
    def __init__(self, parent, boss, Vid, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base, bd=0, highlightthickness=0)
        self.parent=parent
        self.boss=boss
        self.grid(sticky="nsew")
        self.Vid=Vid

        #Import messages
        self.Messages = UserMessages.get_dict()

        Grid.columnconfigure(self.parent, 0, weight=1)
        Grid.rowconfigure(self.parent, 0, weight=1)

        self.winfo_toplevel().title("Delete individuals")#CTXT

        # Listbox of other arenas
        self.Button_sel_al_o=Button(self,text=self.Messages["ExtendB1"], command=self.select_all_inds, **Color_settings.My_colors.Button_Base)
        self.Button_sel_al_o.grid(row=0, column=0, columnspan=2)
        self.all_sel_areas=False
        self.yscrollbar2 = ttk.Scrollbar(self)
        self.yscrollbar2.grid(row=1, column=1, sticky="ns")
        self.Liste_Inds = Listbox(self, selectmode = EXTENDED, width=50, exportselection=0, yscrollcommand=self.yscrollbar2.set, **Color_settings.My_colors.ListBox)
        self.yscrollbar2.config(command=self.Liste_Inds.yview)

        self.to_remove_sel=[]#The Video cannot be selecetd, only the arenas
        for Ind in range(len(self.Vid.Identities)):
            self.Liste_Inds.insert(Ind,self.Messages["Arena"] + "_" + str( Vid.Identities[Ind][0]) + "_" + Vid.Identities[Ind][1])
            self.Liste_Inds.itemconfig(Ind, fg=Color_settings.My_colors.list_colors["Fg_T1"],
                                       bg=Color_settings.My_colors.list_colors["Table1"])
            self.to_remove_sel = [0] + [val + 1 for val in self.to_remove_sel if val>0]


        self.Liste_Inds.grid(row=1, column=0, sticky="nsew")

        self.Validate_button=Button(self, text=self.Messages["Validate"], command=self.validate, **Color_settings.My_colors.Button_Base)
        self.Validate_button.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.Validate_button.grid(row=2, column=0, columnspan=2, sticky="nsew")

        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=100)
        Grid.rowconfigure(self, 2, weight=1)

        self.stay_on_top()
        self.boss.ready=False
        self.parent.protocol("WM_DELETE_WINDOW", self.close)

    def select_all_inds(self):
        #Select/unselect all arenas
        self.Liste_Inds.select_set(0, END)
        self.Button_sel_al_o.config(text=self.Messages["ExtendB2"])
        self.all_sel_areas=True

    def close(self):
        #Close this window properly
        self.parent.destroy()

    def validate(self):
        Load_show=Class_loading_Frame.Loading(self)
        Load_show.grid(row=6,column=0,columnspan=6)
        self.boss.list_inds_returned=self.Liste_Inds.curselection()
        self.parent.destroy()

        #If some elements were replaced in the selected arenas.
        #if Show_warn:
            #messagebox.showinfo(message=self.Messages["GError1"], title=self.Messages["GErrorT1"])



    def stay_on_top(self):
        #Maintain this window on top
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)
