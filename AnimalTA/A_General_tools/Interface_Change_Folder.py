from tkinter import *
from tkinter import ttk
import os
from AnimalTA.A_General_tools import UserMessages, Color_settings
import ntpath
from tkinter import filedialog

class Change_path(Frame):
    def __init__(self, parent, boss, new_file, any_tracked=False):
        Frame.__init__(self, parent, bd=5)
        self.parent=parent
        self.boss=boss
        self.boss.unbind_all("<MouseWheel>")#We don't want the mouse wheel to move the project behind
        self.grid()
        self.list_vid=self.boss.liste_of_videos
        self.grab_set()
        self.all_sel=False
        self.timer=0
        self.new_file=new_file
        self.config(**Color_settings.My_colors.Frame_Base)
        self.list_colors = Color_settings.My_colors.list_colors

        #Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        #The message displayed varies according to whether the user wants to track or analyse videos
        self.sel_state = StringVar()
        self.sel_state.set(self.Messages["ExtendB1"])

        self.winfo_toplevel().title(self.Messages["TChange_path"])
        self.Explanation_lab = Label(self, text=self.Messages["Change_path"], wraplength=700,**Color_settings.My_colors.Label_Base)

        #Button to select all
        self.bouton_sel_all=Button(self,textvariable=self.sel_state,command=self.select_all, **Color_settings.My_colors.Button_Base)
        self.bouton_sel_all.grid(row=2,columnspan=2)

        #List of videos
        self.yscrollbar = ttk.Scrollbar(self)
        self.yscrollbar.grid(row=3,column=1, sticky="ns")

        self.Liste=Listbox(self, selectmode = EXTENDED, yscrollcommand=self.yscrollbar.set, **Color_settings.My_colors.ListBox)
        self.Liste.config(height=15, width=150)
        self.yscrollbar.config(command=self.Liste.yview)

        B_Frame=Frame(self, **Color_settings.My_colors.Frame_Base)
        B_Frame.grid(row=4,column=0, sticky="nsew")
        Grid.columnconfigure(B_Frame, 0, weight=2)
        Grid.columnconfigure(B_Frame, 1, weight=1)
        Grid.columnconfigure(B_Frame, 2, weight=1)

        self.change_path = Button(B_Frame, text=self.Messages["Change_path_button"], command=self.change_path, **Color_settings.My_colors.Button_Base)
        self.change_path.grid(row=0, column=0, sticky="nsew")

        self.boutonv=Button(B_Frame,text=self.Messages["Validate"],command=self.validate, **Color_settings.My_colors.Button_Base)
        self.boutonv.config(bg=self.list_colors["Validate"], fg=self.list_colors["Fg_Validate"])
        self.boutonv.grid(row=0, column=1, sticky="nsew")
        self.boutonv.config(state="disable", bg=self.list_colors["Base_ina"], fg=self.list_colors["Fg_Base_ina"])

        self.boutonc=Button(B_Frame,text=self.Messages["Cancel"],command=self.cancel, **Color_settings.My_colors.Button_Base)
        self.boutonc.config(bg=self.list_colors["Cancel"], fg=self.list_colors["Fg_Cancel"])
        self.boutonc.grid(row=0, column=2, sticky="nsew")

        self.update_list()#According to the situation (manual or not, trcaking or analyses), we will propose different lists of videos

        self.Liste.grid(row=3,column=0)

        #Minimize the window which processing
        self.focus()

        #Stop all process if the windows is closed
        self.parent.protocol("WM_DELETE_WINDOW", self.close)
        self.running=None#A variable used to determine if the tracking is running and to be able to stop it in the case of urgent close

    def cancel(self):
        self.boss.close_file(ask=False)
        self.close()

    def validate(self):
        self.boss.save()
        self.boss.open_file2(new_file=self.new_file)
        self.close()

    def change_path(self):
        new_dir=filedialog.askdirectory()
        list_item = self.Liste.curselection()
        for V in list_item:
            self.list_vid_minus[V].File_name=new_dir+"/"+ntpath.basename(self.list_vid_minus[V].File_name)
            for F in range(len(self.list_vid_minus[V].Fusion)):
                if os.path.isfile(new_dir + "/" + ntpath.basename(self.list_vid_minus[V].Fusion[F][1])):
                    self.list_vid_minus[V].Fusion[F][1]= new_dir +"/" + ntpath.basename(self.list_vid_minus[V].Fusion[F][1])
        self.update_list()

    def update_list(self):
        self.list_vid_minus=[]
        nb_validated=0
        self.Liste.delete(0, 'end')
        for i in range(len(self.list_vid)):#Only video that are ready for tracking can be choose if the user wants to do tracking. If user wants to analyse, only videos which are already tracked.
            self.list_vid_minus.append(self.list_vid[i])
            if os.path.isfile(self.list_vid[i].File_name):
                self.Liste.insert(i, self.list_vid[i].User_Name + " ----- " + u'\u2713')
                self.Liste.itemconfig(len(self.list_vid_minus) - 1, {'fg': self.list_colors["Fg_valide"]})
                nb_validated+=1

            elif os.path.isfile(self.boss.folder+"/converted_vids/"+self.list_vid[i].Name):
                self.list_vid[i].File_name=self.boss.folder+"/"+self.list_vid[i].Name
                self.Liste.insert(i, self.list_vid[i].User_Name + " ----- " + u'\u2713')
                self.Liste.itemconfig(len(self.list_vid_minus) - 1, {'fg': self.list_colors["Fg_valide"]})
                nb_validated+=1

            else:
                self.Liste.insert(i, self.list_vid[i].User_Name + " ----- " + u'\u2717')
                self.Liste.itemconfig(len(self.list_vid_minus) - 1, {'fg': self.list_colors["Fg_not_valide"]})

        if nb_validated==len(self.list_vid_minus):
            self.boutonv.config(state="normal", bg=self.list_colors["Validate"], fg=self.list_colors["Fg_Validate"])
        else:
            self.boutonv.config(state="disable")

    def select_all(self):
        #Sellect all the videos
        if not self.all_sel:
            self.Liste.select_set(0, END)
            self.sel_state.set(self.Messages["ExtendB2"])
            self.all_sel=True
        else:
            self.Liste.selection_clear(0, END)
            self.sel_state.set(self.Messages["ExtendB1"])
            self.all_sel=False

    def close(self):
        self.parent.destroy()
        self.boss.bind_all("<MouseWheel>", self.boss.on_mousewheel)