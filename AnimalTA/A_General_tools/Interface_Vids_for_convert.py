from tkinter import *
from tkinter import ttk
import os

from AnimalTA.A_General_tools import UserMessages, Class_converter, Color_settings, Message_simple_question as MsgBox
from AnimalTA import Class_Video


class Convert(Frame):
    """When the user ask to add new videos, these videos must be avi. If they are not, this window will open and ask the user which of the videos have to be converted to avi."""
    def __init__(self, parent, boss, list_to_convert, Video=None):
        Frame.__init__(self, parent, bd=5)
        self.config(**Color_settings.My_colors.Frame_Base)
        self.parent=parent
        self.boss=boss
        self.grid()
        self.list_vid=list_to_convert
        self.grab_set()
        self.all_sel=False
        self.timer=0
        self.cache=False
        self.Vid=Video

        #Import messsages
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()

        #We import colors
        list_colors=Color_settings.My_colors.list_colors

        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Conversion"])

        self.sel_state=StringVar()
        self.sel_state.set(self.Messages["ExtendB1"])

        #Explication of what is this window
        self.explanations=Label(self, text=self.Messages["ExtendConvert_EX"], wraplength=800,**Color_settings.My_colors.Label_Base)
        self.explanations.grid(row=0,columnspan=2)

        #Button to select the whole list
        self.bouton_sel_all=Button(self,textvariable=self.sel_state,command=self.select_all, **Color_settings.My_colors.Button_Base)
        self.bouton_sel_all.grid(row=1,columnspan=2)

        #The list of videos to be converted
        self.yscrollbar = ttk.Scrollbar(self)
        self.Liste=Listbox(self, selectmode = EXTENDED, yscrollcommand=self.yscrollbar.set, **Color_settings.My_colors.ListBox)
        self.Liste.config(height=15, width=150)
        self.list_vid_minus=[]
        for i in range(len(self.list_vid)):
            self.list_vid_minus.append(self.list_vid[i])
            self.Liste.insert(i, self.list_vid[i])
        self.Liste.grid(row=2,column=0)
        self.yscrollbar.grid(row=2,column=1, sticky="ns")

        self.FPS_corr=BooleanVar()
        self.FPS_corr.set(False)
        Checkbutton(self,text=self.Messages["Convert_fps"], variable=self.FPS_corr, command=self.ask_fps, **Color_settings.My_colors.Checkbutton_Base).grid(row=3)

        self.fps_val = 25
        self.Fr_fps = Frame_new_fps(parent=self)


        #Validate
        Frame_Buttons=Frame(self, **Color_settings.My_colors.Frame_Base)
        Frame_Buttons.grid(row=5, sticky="nsew")
        Grid.columnconfigure(Frame_Buttons,0, weight=1)
        Grid.columnconfigure(Frame_Buttons, 1, weight=1)
        self.bouton=Button(Frame_Buttons,text=self.Messages["Validate"], **Color_settings.My_colors.Button_Base, width=15)
        self.bouton.config(bg=list_colors["Validate"], fg=list_colors["Fg_Validate"],command=self.validate)
        self.bouton.grid(row=0, column=0, sticky="e")

        self.bouton_cancel=Button(Frame_Buttons,text=self.Messages["Cancel"], **Color_settings.My_colors.Button_Base, width=15)
        self.bouton_cancel.config(bg=list_colors["Cancel"], fg=list_colors["Fg_Cancel"],command=self.End_of_window)
        self.bouton_cancel.grid(row=0, column=1, sticky="w")
        self.yscrollbar.config(command=self.Liste.yview)

        #Show the progression of the convertions
        self.loading_canvas=Frame(self, **Color_settings.My_colors.Frame_Base)
        self.loading_canvas.grid(row=6,columnspan=2)
        self.loading_state=Label(self.loading_canvas, text="", **Color_settings.My_colors.Label_Base)
        self.loading_state.grid(row=0, column=0)

        self.loading_bar=Canvas(self.loading_canvas, height=10, **Color_settings.My_colors.Frame_Base)
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill=Color_settings.My_colors.list_colors["Loading_before"])
        self.loading_bar.grid(row=0, column=1)


        #Minimise the AnimalTA program to allow user to do something else while converting
        self.bouton_hide = Button(self, text=self.Messages["Do_track1"], command=self.hide, **Color_settings.My_colors.Button_Base)
        self.select_all()

    def ask_fps(self):
        if self.FPS_corr.get():
            self.Fr_fps.grid(row=4, sticky="nsew")
            self.bouton.config(state="disable", **Color_settings.My_colors.Button_Base)
        else:
            self.Fr_fps.grid_forget()
            self.bouton.config(state="normal", background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])



    def select_all(self):
        #Select all the videos of the list
        if not self.all_sel:
            self.Liste.select_set(0, END)
            self.sel_state.set(self.Messages["ExtendB2"])
            self.all_sel=True
        else:
            self.Liste.selection_clear(0, END)
            self.sel_state.set(self.Messages["ExtendB1"])
            self.all_sel=False

    def validate(self):
        #Run the convertions and close this window in the end
        list_item = self.Liste.curselection()
        pos=0
        #We don't want user to interact with buttons during conversions
        self.bouton.config(state="disable", **Color_settings.My_colors.Button_Base)
        self.bouton_sel_all.config(state="disable", **Color_settings.My_colors.Button_Base)
        self.Liste.config(state="disable", **Color_settings.My_colors.ListBox)
        self.bouton_hide.grid(row=7)

        self.list_errors=[]
        for V in list_item:
            pos+=1
            self.loading_state.config(text=self.Messages["Video"] + " {act}/{tot}".format(act=pos,tot=len(list_item)))

            if not self.FPS_corr.get():
                self.fps_val=None

            try:
                new_file= Class_converter.convert_to_avi(self, self.list_vid_minus[V], self.boss.folder, self.fps_val)
                if new_file!="Error":
                    if self.Vid==None:
                        self.boss.liste_of_videos.append(Class_Video.Video(File_name=new_file, Folder=self.boss.folder))
                else:
                    self.list_errors.append(self.list_vid_minus[V])

            except:
                self.list_errors.append(self.list_vid_minus[V])

        for elem in self.list_errors:
            question = MsgBox.Messagebox(parent=self, title=self.Messages["GWarnT5"],
                                       message=self.Messages["GWarn6"], Possibilities=self.Messages["Continue"])
            self.wait_window(question)

            self.boss.HW.change_tmp_message(self.Messages["General1"])

        #Update the main frame
        if self.Vid == None:
            self.boss.update_projects()
            self.boss.update_selections()
            self.boss.focus_set()
            self.bouton.config(state="normal", background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
            self.bouton_sel_all.config(state="normal")
            self.boss.afficher_projects()

            if self.cache:#If the program was minimised, we bring it back
                self.boss.parent.update_idletasks()
                self.boss.parent.state('normal')
                self.boss.parent.overrideredirect(True)

        self.End_of_window()

    def End_of_window(self):
        self.boss.update_row_display()
        self.parent.destroy()

    def show_load(self):
        #Show the progress of the conversion process
        self.loading_bar.delete('all')
        heigh=self.loading_bar.cget("height")
        self.loading_bar.create_rectangle(0, 0, 400, heigh, fill=Color_settings.My_colors.list_colors["Loading_before"])
        self.loading_bar.create_rectangle(0, 0, self.timer*400, heigh, fill=Color_settings.My_colors.list_colors["Loading_after"])
        self.loading_bar.update()

    def hide(self):
        #Minimise the program
        self.cache=True
        self.parent.wm_state('iconic')
        self.boss.parent.update_idletasks()
        self.boss.parent.overrideredirect(False)
        self.boss.parent.state('iconic')



class Frame_new_fps(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, **Color_settings.My_colors.Frame_Base)
        self.config(background=Color_settings.My_colors.list_colors["Entry_error"])
        self.parent=parent
        self.tmp_val=StringVar()
        self.tmp_val.set(25)

        Grid.columnconfigure(self,0,weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)

        Entry(self, textvariable=self.tmp_val, **Color_settings.My_colors.Entry_Base).grid()
        Button(self,text=self.parent.Messages["Validate"], command=self.end, **Color_settings.My_colors.Button_Base).grid()

    def end(self):
        try:
            self.parent.fps_val=float(self.tmp_val.get())
        except:
            pass

        self.parent.bouton.config(state="normal", background=Color_settings.My_colors.list_colors["Validate"], fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.grid_forget()



"""
root = Tk()
root.geometry("+100+100")
Video_file=Class_Video.Video(File_name="D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01.avi")
Video_file.Back[0]=True

im=cv2.imread("D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01_background.bmp")
im=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
Video_file.Back[1]=im
interface = Scale(parent=root, boss=None, Video_file=Video_file)
root.mainloop()
"""