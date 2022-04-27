from tkinter import *
from BioTrack import UserMessages, Function_draw_mask
import math
import cv2
from copy import deepcopy

class Extend(Frame):
    def __init__(self, parent, boss, value, Video_file, type=None, do_self=False, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.boss=boss
        self.grid(sticky="nsew")
        self.Vid = Video_file
        self.type=type
        self.list_vid=self.boss.liste_of_videos
        self.do_self=do_self
        self.value=value
        self.all_sel=False

        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()

        Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW

        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Extend1"] + " "+ self.Messages[type])

        self.sel_state=StringVar()
        self.sel_state.set(self.Messages["ExtendB1"])

        self.bouton_sel_all=Button(self,textvariable=self.sel_state,command=self.select_all)
        self.bouton_sel_all.grid(row=0,columnspan=2, sticky="nsew")

        self.yscrollbar = Scrollbar(self)
        self.yscrollbar.grid(row=1,column=1, sticky="ns")

        self.Liste=Listbox(self, selectmode = "multiple", width=100, yscrollcommand=self.yscrollbar.set)

        self.bouton=Button(self,text=self.Messages["Validate"],command=self.validate)
        self.bouton.grid(row=2, sticky="nsew")
        self.yscrollbar.config(command=self.Liste.yview)


        self.loading_canvas=Frame(self)
        self.loading_state=Label(self.loading_canvas, text="")
        self.loading_state.grid(row=0, column=0)

        self.loading_bar=Canvas(self.loading_canvas, height=10)
        self.loading_bar.create_rectangle(0, 0, 400, self.loading_bar.cget("height"), fill="red")
        self.loading_bar.grid(row=0, column=1)


        self.list_vid_minus=[]
        for i in range(len(self.list_vid)):
            if self.list_vid[i]!=self.Vid or self.do_self:
                if not (type=="analyses_smooth" or type=="analyses_thresh" or type=="analyses_explo") or (self.list_vid[i].Tracked):
                    self.list_vid_minus.append(self.list_vid[i])
                    self.Liste.insert(i, self.list_vid[i].File_name)
                    if self.list_vid[i].Tracked:
                        self.Liste.itemconfig(self.Liste.size()-1, {'fg': 'red'})

        self.Liste.grid(row=1,column=0, sticky="nsew")

        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=100)  ########NEW
        Grid.rowconfigure(self, 2, weight=1)  ########NEW

        self.grab_set()

    def select_all(self):
        if not self.all_sel:
            self.Liste.select_set(0, END)
            self.sel_state.set(self.Messages["ExtendB2"])
            self.all_sel=True
        else:
            self.Liste.selection_clear(0, END)
            self.sel_state.set(self.Messages["ExtendB1"])
            self.all_sel=False

    def validate(self):
        if self.type=="back":
            self.loading_canvas.grid(row=3, column=0, columnspan=2)

        list_item = self.Liste.curselection()
        nb_items=len(list_item)
        item=0
        for V in list_item:
            if self.type=="scale":
                self.list_vid_minus[V].Scale[0]=self.value[0]
                self.list_vid_minus[V].Scale[1] = self.value[1]
            elif self.type=="mask":
                self.list_vid_minus[V].Mask[0] = 1
                self.list_vid_minus[V].Mask[1]=deepcopy(self.value)
            elif self.type=="track":
                self.list_vid_minus[V].Track[0] = 1
                mask = Function_draw_mask.draw_mask(self.list_vid_minus[V])
                Arenas, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                nb_ar=len(Arenas)
                self.list_vid_minus[V].Track[1]=deepcopy(self.value)
                self.list_vid_minus[V].Track[1][6]=deepcopy(self.value)[6][0:nb_ar]
                
            elif self.type=="fps":
                if self.list_vid_minus[V].Frame_rate[1]!=self.list_vid_minus[V].Frame_rate[0]/self.value:
                    self.list_vid_minus[V].Frame_rate[1]=self.list_vid_minus[V].Frame_rate[0]/self.value
                    self.list_vid_minus[V].Frame_nb[1] = math.floor(self.list_vid_minus[V].Frame_nb[0] / round(self.list_vid_minus[V].Frame_rate[0] / self.list_vid_minus[V].Frame_rate[1]))  ######NEW
                    self.list_vid_minus[V].Cropped=[False,[0,self.list_vid_minus[V].Frame_nb[0]]]
                    self.list_vid_minus[V].Back = [False, []]

            elif self.type=="stab":
                if self.list_vid_minus[V].Stab!=(1-self.value):
                    self.list_vid_minus[V].Stab=(1-self.value)
                    self.list_vid_minus[V].Back = [False, []]

            elif self.type=="back":
                self.loading_bar.delete('all')
                heigh = self.loading_bar.cget("height")
                self.loading_bar.create_rectangle(0, 0, 400, heigh, fill="red")
                self.loading_bar.create_rectangle(0, 0, ((item+1)/nb_items) * 400, heigh, fill="blue")
                self.loading_bar.update()
                self.loading_state.config(text=self.Messages["Video"] + ": {act}/{tot}".format(act=item+1, tot=nb_items))
                self.list_vid_minus[V].make_back()

            elif self.type=="analyses_smooth":
                if self.list_vid_minus[V].Tracked:
                    self.list_vid_minus[V].Smoothed = deepcopy(self.value)

            elif self.type=="analyses_thresh":
                if self.list_vid_minus[V].Tracked:
                    self.list_vid_minus[V].Analyses[0] = deepcopy(self.value)

            elif self.type=="analyses_explo":
                if self.list_vid_minus[V].Tracked:
                    print(self.list_vid_minus[V].Analyses)
                    self.list_vid_minus[V].Analyses[2] = deepcopy(self.value)

            if self.list_vid_minus[V].Tracked and self.type!="analyses_smooth" and self.type!="analyses_thresh" and self.type!="analyses_explo":
                self.list_vid_minus[V].clear_files()
                self.list_vid_minus[V].Tracked=False


            item+=1

        self.boss.update_projects()
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