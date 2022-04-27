from tkinter import *
import UserMessages, Class_color_infos as Col_I
import cv2
import PIL.Image, PIL.ImageTk


class Define_Col_Dict(Frame):
    def __init__(self, parent, boss, Color_profiles, **kwargs):
        self.boss=boss
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.grid()
        self.Color_profiles = Color_profiles

        self.palette = cv2.imread("D:/Post-doc/TRacking_software/Palette_couleurs.png")
        self.palette = cv2.cvtColor(self.palette, cv2.COLOR_BGR2RGB)
        self.Size_palette = self.palette.shape
        self.palette2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.palette))



        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        self.winfo_toplevel().title(self.Messages["Extend1"])

        self.yscrollbar = Scrollbar(self)
        self.yscrollbar.grid(row=1,column=1, sticky="ns")


        self.Choose_color = Canvas(self, width=50)
        self.Choose_color.grid(row=1,column=2, columnspan=2, sticky="nsew")
        self.Choose_color.create_image(0, 0, image=self.palette2, anchor=NW)
        self.Choose_color.config(width=int(self.Size_palette[1]), height=int(self.Size_palette[0]))
        self.Choose_color.bind("<Button-1>",self.define_new_col)
        self.Choose_color.bind("<B1-Motion>",self.define_new_col)

        self.Show_color_L = Label(self, text="Current color:")
        self.Show_color_L.grid(row=2,column=2, sticky="e")

        self.Show_color = Canvas(self, width=30, height=25)
        self.Show_color.grid(row=2,column=3)
        self.default_col=self.Show_color["background"]

        self.Liste=Listbox(self, selectmode = "BROWSE", yscrollcommand=self.yscrollbar.set)
        self.Liste.config(height=40, width=50)
        self.Liste.bind("<ButtonRelease>", self.show_selected_col)


        self.new_name=StringVar()
        self.new_nameE=Entry(self,textvariable=self.new_name)
        self.new_nameE.grid(row=2,column=0)
        self.new_nameE.bind("<Button-1>",self.focus_lost)

        self.Add_button = Button(self, text="Add a new color", command=self.add_new_col)
        self.Add_button.grid(row=3, column=0)
        self.bind_all("<Return>",self.add_new_col)

        self.Del_button = Button(self, text="Remove the color", command=self.delete_col)
        self.Del_button.grid(row=3, column=2)

        self.bouton=Button(self,text=self.Messages["Validate"],command=self.validate)
        self.bouton.grid(row=4, columnspan=2)
        self.yscrollbar.config(command=self.Liste.yview)

        pos=0
        for i in self.Color_profiles:
            self.Liste.insert(pos, i)
            pos += 1

        self.Liste.grid(row=1,column=0)
        self.focus()

    def focus_lost(self, *event):
        self.Show_color.configure(bg=self.default_col)
        self.Liste.selection_clear(0,"end")

    def define_new_col(self, event):
        selected_col = self.Liste.curselection()
        if len(selected_col)>0 and event.y>0 and event.y<self.palette.shape[0] and event.x>0 and event.x<self.palette.shape[1]:
            new_col=tuple(self.palette[event.y,event.x])
            self.Color_profiles[self.Liste.get(selected_col[0])].color=new_col
            self.change_cur_col(new_col)

    def show_selected_col(self, *event):
        selected_col = self.Liste.curselection()
        new_col=self.Color_profiles[self.Liste.get(selected_col)].color
        self.change_cur_col(new_col)


    def change_cur_col(self, col):
        new_col="#%02x%02x%02x" % col
        self.Show_color.configure(bg=new_col)



    def validate(self):
        self.boss.Liste_all_col_info=self.Color_profiles
        self.boss.Save_colors()
        self.boss.update_CheckB()
        self.boss.show_graph()
        self.parent.destroy()

    def add_new_col(self, *args):
        if len(self.new_name.get())>0:
            new_name=self.new_name.get()

            while new_name in self.Color_profiles:
                new_name=new_name+"_copy"

            self.Color_profiles[new_name]=Col_I.Color_info(color=(0,0,0))
            self.Liste.insert(len(self.Color_profiles), new_name)
            self.Liste.selection_clear(0, 'end')
            self.Liste.selection_set("end")
            self.new_name.set("")
            self.show_selected_col()

    def delete_col(self):
        selected_col=self.Liste.curselection()
        if len(selected_col)>0:
            self.Show_color.configure(bg=self.default_col)

            del self.Color_profiles[self.Liste.get(selected_col[0])]
            self.Liste.delete(selected_col[0])





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