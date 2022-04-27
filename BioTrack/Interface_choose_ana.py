from tkinter import *
from BioTrack import UserMessages, Ana_dict


class Liste_ana(Frame):
    def __init__(self, parent, boss, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.boss=boss
        self.grid()

        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()

        self.list_anas = Ana_dict.list_anas

        Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW

        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Extend1"])

        self.sel_state=StringVar()
        self.sel_state.set(self.Messages["ExtendB1"])

        self.yscrollbar = Scrollbar(self)
        self.yscrollbar.grid(row=1,column=1, sticky="ns")

        self.Liste=Listbox(self, selectmode = "single", width=100, yscrollcommand=self.yscrollbar.set)

        self.bouton=Button(self,text=self.Messages["Validate"],command=self.validate)
        self.bouton.grid(row=2, sticky="nsew")
        self.yscrollbar.config(command=self.Liste.yview)


        self.loading_canvas=Frame(self)
        self.loading_state=Label(self.loading_canvas, text="")
        self.loading_state.grid(row=0, column=0)

        self.loading_bar=Canvas(self.loading_canvas, height=10)
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill="red")
        self.loading_bar.grid(row=0, column=1)



        for key in self.list_anas:
            self.Liste.insert(END, self.list_anas[key])


        self.Liste.grid(row=1,column=0, sticky="nsew")

        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=100)  ########NEW
        Grid.rowconfigure(self, 2, weight=1)  ########NEW

        self.grab_set()

    def validate(self):
        selection=self.Liste.curselection()
        if len(selection)>0:
            sel_type=(list(self.list_anas.keys())[list(self.list_anas.values()).index(self.Liste.get(selection))])
            self.boss.add_ana_row(sel_type)
            self.grab_release()
            self.parent.destroy()




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