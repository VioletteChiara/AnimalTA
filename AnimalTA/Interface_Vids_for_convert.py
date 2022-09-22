from tkinter import *
from tkinter import messagebox
from AnimalTA import Class_Video, UserMessages, Class_coverter

class Convert(Frame):
    """When the user ask to add new videos, these videos must be avi. If they are not, this window will open and ask the user which of the videos have to be converted to avi."""
    def __init__(self, parent, boss):
        Frame.__init__(self, parent, bd=5)
        self.parent=parent
        self.boss=boss
        self.grid()
        self.list_vid=self.boss.list_to_convert
        self.grab_set()
        self.all_sel=False
        self.timer=0
        self.cache=False

        #Import messsages
        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()

        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Conversion"])

        self.sel_state=StringVar()
        self.sel_state.set(self.Messages["ExtendB1"])

        #Explication of what is this window
        self.explanations=Label(self, text=self.Messages["ExtendConvert_EX"], wraplength=800)
        self.explanations.grid(row=0,columnspan=2)

        #Button to select the whole list
        self.bouton_sel_all=Button(self,textvariable=self.sel_state,command=self.select_all)
        self.bouton_sel_all.grid(row=1,columnspan=2)

        #The list of videos to be converted
        self.yscrollbar = Scrollbar(self)
        self.Liste=Listbox(self, selectmode = EXTENDED, yscrollcommand=self.yscrollbar.set)
        self.Liste.config(height=15, width=150)
        self.list_vid_minus=[]
        for i in range(len(self.list_vid)):
            self.list_vid_minus.append(self.list_vid[i])
            self.Liste.insert(i, self.list_vid[i])
        self.Liste.grid(row=2,column=0)
        self.yscrollbar.grid(row=2,column=1, sticky="ns")

        #Validate
        self.bouton=Button(self,text=self.Messages["Validate"],command=self.validate)
        self.bouton.grid(row=3)
        self.yscrollbar.config(command=self.Liste.yview)

        #Show the progression of the convertions
        self.loading_canvas=Frame(self)
        self.loading_canvas.grid(row=4,columnspan=2)
        self.loading_state=Label(self.loading_canvas, text="")
        self.loading_state.grid(row=0, column=0)

        self.loading_bar=Canvas(self.loading_canvas, height=10)
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill="red")
        self.loading_bar.grid(row=0, column=1)
        self.focus()

        #Minimise the AnimalTA program to allow user to do something else while converting
        self.bouton_hide = Button(self, text=self.Messages["Do_track1"], command=self.hide)

        self.select_all()

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
        self.bouton.config(state="disable")
        self.bouton_sel_all.config(state="disable")
        self.Liste.config(state="disable")
        self.bouton_hide.grid(row=5)
        for V in list_item:
            pos+=1
            self.loading_state.config(text=self.Messages["Video"] + " {act}/{tot}".format(act=pos,tot=len(list_item)))
            try:
                new_file=Class_coverter.convert_to_avi(self, self.list_vid_minus[V], self.boss.folder)
                self.boss.liste_of_videos.append(Class_Video.Video(File_name=new_file, Folder=self.boss.folder))
            except:
                messagebox.showinfo(self.Messages["GWarnT5"], self.Messages["GWarn6"].format(self.list_vid_minus[V]))
                self.boss.HW.change_tmp_message(self.Messages["General1"])

        #Update the main frame
        self.boss.update_projects()
        self.boss.update_selections()
        self.boss.focus_set()
        self.bouton.config(state="active")
        self.bouton_sel_all.config(state="active")
        self.boss.load_projects()
        self.boss.afficher_projects()

        if self.cache:#If the program was minimised, we bring it back
            self.boss.parent.update_idletasks()
            self.boss.parent.state('normal')
            self.boss.parent.overrideredirect(True)
        self.parent.destroy()

    def show_load(self):
        #Show the progress of the conversion process
        self.loading_bar.delete('all')
        heigh=self.loading_bar.cget("height")
        self.loading_bar.create_rectangle(0, 0, 400, heigh, fill="red")
        self.loading_bar.create_rectangle(0, 0, self.timer*400, heigh, fill="blue")
        self.loading_bar.update()

    def hide(self):
        #Minimise the program
        self.cache=True
        self.parent.wm_state('iconic')
        self.boss.parent.update_idletasks()
        self.boss.parent.overrideredirect(False)
        self.boss.parent.state('iconic')

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