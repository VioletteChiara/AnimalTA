from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
import numpy as np
import math
from BioTrack import UserMessages


class Scale(Frame):
    def __init__(self, parent, boss, main_frame, Video_file, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.boss=boss
        self.main_frame=main_frame
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.Vid = Video_file
        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]


        self.capture = cv2.VideoCapture(self.Vid.File_name)
        Which_part = 0
        if self.Vid.Cropped[0]:
            if len(self.Vid.Fusion) > 1:  # Si on a plus d'une video
                Which_part = [index for index, Fu_inf in enumerate(self.Vid.Fusion) if Fu_inf[0] <= self.Vid.Cropped[1][0]][-1]
                if Which_part != 0:  # si on est pas dans la première partie de la vidéo
                    self.capture.release()
                    self.capture = cv2.VideoCapture(self.Vid.Fusion[Which_part][1])

        self.capture.set(cv2.CAP_PROP_POS_FRAMES, self.Vid.Cropped[1][0] - self.Vid.Fusion[Which_part][0])
        ret, self.Represent = self.capture.read()

        self.shape=(self.Represent.shape[0],self.Represent.shape[1])


        self.image_to_show=np.copy(self.Represent)
        self.image_to_show=cv2.cvtColor(self.image_to_show,cv2.COLOR_BGR2RGB)

        self.zoom_sq=[0,0,self.Vid.shape[1],self.Vid.shape[0]]
        self.zoom_strength = 0.3

        self.ratio=0.75
        self.Pt_select=None
        self.dist=0
        self.Mem_size="NA"
        self.ratio_val=StringVar()
        self.ratio_val.set("NA")
        self.ratio_text=StringVar()
        self.ratio_text.set("px/?")

        self.canvas_img = Canvas(self, bd=0, highlightthickness=0, relief='ridge')
        self.canvas_img.grid(row=0, column=0, sticky="nsew")
        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW

        self.canvas_User_help = Frame(self.parent, width=150,  highlightthickness=4, relief='flat', highlightbackground="RoyalBlue3")
        self.canvas_User_help.grid(row=0, column=1, sticky="new")
        Info_title=Label(self.canvas_User_help, text=self.Messages["Info"],  justify=CENTER, background="RoyalBlue3", fg="white", font=("Helvetica", 16, "bold"))
        Info_title.grid(row=0, sticky="new")
        Grid.columnconfigure(self.canvas_User_help, 0, weight=1)

        self.canvas_bt_global=Canvas(self.parent, height=10, bd=0, highlightthickness=0, relief='ridge')
        self.canvas_bt_global.grid(row=1,column=1, sticky="nsew")

        self.msg_user=StringVar()
        self.canvas_User_help.update()
        self.Message_user_lab = Label(self.canvas_User_help,textvariable=self.msg_user, wraplengt=self.canvas_User_help.winfo_width()-10, borderwidth=2, anchor="e")
        self.Message_user_lab.grid(row=1,column=0, sticky="news")
        self.Message_user_lab.grid_rowconfigure(1, weight=1)
        self.Message_user_lab.grid_columnconfigure(1, weight=1)
        self.msg_user.set(self.Messages["Scale2"])

        self.UI_Size_label = Label(self.canvas_bt_global,text=self.Messages["Scale3"])
        self.UI_Size_label.grid(row=2,column=0)
        self.UI_Size=Entry(self.canvas_bt_global)
        self.regUI_Size = self.register(self.UI_Size_update)
        self.UI_Size.config(validate="focusout", validatecommand=(self.regUI_Size,"%P"))
        self.UI_Size.grid(row=2,column=1)
        self.UI_Size.bind("<Return>", self.remove_focus)


        self.Check_units=Listbox(self.canvas_bt_global, exportselection=0)
        self.Check_units.config(height=3)
        self.Check_units.insert(1, "m")
        self.Check_units.insert(2, "cm")
        self.Check_units.insert(3, "mm")
        self.Check_units.grid(row=2,column=2)
        self.Check_units.bind('<<ListboxSelect>>', self.update_ui)


        self.UI_ratio_label = Label(self.canvas_bt_global,text="Ratio:")
        self.UI_ratio_label.grid(row=4,column=0)

        self.ratio_val_label = Label(self.canvas_bt_global,textvariable=self.ratio_val)
        self.ratio_val_label.grid(row=4,column=1)

        self.ratio_post_label = Label(self.canvas_bt_global,textvariable=self.ratio_text)
        self.ratio_post_label.grid(row=4,column=2)


        self.bouton_validate = Button(self.canvas_bt_global, text=self.Messages["Validate"], background="green", fg="black", command=self.validate)
        self.bouton_validate.grid(row=6, column=0, columnspan=3,sticky="nsew")

        self.ratio=1
        self.final_width=750
        self.Size = self.Vid.shape
        self.canvas_img.bind("<Configure>", self.afficher)

        self.canvas_img.focus_force()
        self.liste_points = []
        self.unit=False

        self.UI_Size.insert(0, "NA")
        self.canvas_img.bind("<Button-1>", self.callback_mask)
        self.canvas_img.bind("<B1-Motion>", self.move_pt_mask)
        self.canvas_img.bind("<Control-1>", self.Zoom_in)
        self.canvas_img.bind("<Control-3>", self.Zoom_out)


        self.canvas_img.update()
        self.final_width = self.canvas_img.winfo_width()
        self.ratio = self.Size[1] / self.final_width


        self.afficher()

    def update_ui(self,event):
        self.unit=True
        list_item=self.Check_units.curselection()
        if len(list_item)>0:
            self.ratio_text.set("px/{}".format(["m","cm","mm"][list_item[0]]))

    def remove_focus(self, *arg):
        self.canvas_img.focus_set()

    def UI_Size_update(self, new_val):
        if new_val=="":
            self.UI_Size.delete(0, END)
            self.UI_Size.insert(0, self.Mem_size)
            return False
        else:
            try:
                float(new_val)
                self.UI_Size.delete(0, END)
                self.UI_Size.insert(0, new_val)
                self.Mem_size=new_val
                self.ratio_val.set(round(float(self.dist)/float(self.Mem_size),2))
                self.afficher()
                return True
            except:
                self.UI_Size.delete(0, END)
                self.UI_Size.insert(0, self.Mem_size)
                return False



    def validate(self):
        self.UI_Size_update(self.UI_Size.get())
        if self.Mem_size != "NA" and self.unit and self.dist>0:
            list_item = self.Check_units.curselection()
            self.Vid.Scale[0] = self.ratio_val.get()
            self.Vid.Scale[1] = ["m","cm","mm"][list_item[0]]
            self.End_of_window()
        elif self.Mem_size == "NA":
            self.msg_user.set(self.Messages["Scale4"])
        elif not self.unit:
            self.msg_user.set(self.Messages["Scale5"])
        elif self.dist==0:
            self.msg_user.set(self.Messages["Scale6"])


    def End_of_window(self):
        self.unbind_all("<Button-1>")
        self.boss.update()
        self.grab_release()
        self.canvas_User_help.grid_forget()
        self.canvas_User_help.destroy()
        self.canvas_bt_global.grid_forget()
        self.canvas_bt_global.destroy()
        self.main_frame.return_main()

    def move_pt_mask(self, event):
        if self.Pt_select is not None:
            self.liste_points[self.Pt_select]=[int(event.x * self.ratio + self.zoom_sq[0]),int(event.y * self.ratio + self.zoom_sq[1])]
            self.UI_Size_update(self.UI_Size.get())
            self.afficher()

    def callback_mask(self, event):
        #Si c'est le premier point
        event.x=int(event.x * self.ratio + self.zoom_sq[0])
        event.y = int(event.y * self.ratio + self.zoom_sq[1])

        if len(self.liste_points)<1:
            self.liste_points.append([event.x,event.y])
            self.Pt_select=0

        elif len(self.liste_points)<=2:
            # On verifie si on a cliqué sur un point existant.
            self.Pt_select = None
            for j in range(len(self.liste_points)):
                    if math.sqrt((self.liste_points[j][0] - event.x) ** 2 + (
                            self.liste_points[j][1] - event.y ) ** 2) < 10:
                        self.Pt_select = j  # Point selectionné est le Xeme
                        break

            #Si on a pas cliqué sur un point existant, on ajoute le nouveau point
            if len(self.liste_points)<2 and self.Pt_select is None:
                self.liste_points.append([event.x,event.y])
                self.Pt_select=len(self.liste_points)-1

            if len(self.liste_points)==2 and self.Pt_select is None:
                self.liste_points.pop(1)
                self.liste_points.append([event.x, event.y])
                self.Pt_select=1

        self.afficher()
        self.UI_Size_update(self.UI_Size.get())


    def afficher(self, *args):
        self.Message_user_lab.config(wraplengt=self.canvas_User_help.winfo_width() - 10)

        self.TMP_image_to_show=np.copy(self.image_to_show)

        if len(self.liste_points)>0:
            for pt in self.liste_points:
                self.TMP_image_to_show=cv2.circle(self.TMP_image_to_show,tuple(pt),max(1,round(3*self.ratio)),(255,0,0),-1)

        if len(self.liste_points)==2:
            self.dist=math.sqrt((self.liste_points[0][0]-self.liste_points[1][0])**2+(self.liste_points[0][1]-self.liste_points[1][1])**2)
            self.TMP_image_to_show=cv2.line(self.TMP_image_to_show,tuple(self.liste_points[0]),tuple(self.liste_points[1]),(255,0,0),max(1,round(1.5*self.ratio)))
            cv2.putText(self.TMP_image_to_show,str(round(self.dist,1))+" px",(self.liste_points[1][0]-50,self.liste_points[1][1]-25),cv2.FONT_HERSHEY_SIMPLEX,1*self.ratio,(255,255,255),int(6*self.ratio))
            cv2.putText(self.TMP_image_to_show, str(round(self.dist, 1)) + " px",(self.liste_points[1][0] - 50, self.liste_points[1][1] - 25), cv2.FONT_HERSHEY_SIMPLEX,1 * self.ratio, (0, 0, 0), int(3*self.ratio))


        best_ratio = max(self.Size[1] / (self.canvas_img.winfo_width()),self.Size[0] / (self.canvas_img.winfo_height()))
        prev_final_width=self.final_width
        self.final_width=int(self.Size[1]/best_ratio)
        self.ratio=self.ratio*(prev_final_width/self.final_width)

        self.image_to_show2=self.TMP_image_to_show[self.zoom_sq[1]:self.zoom_sq[3],self.zoom_sq[0]:self.zoom_sq[2]]

        self.TMP_image_to_show2 = cv2.resize(self.image_to_show2,
                                             (self.final_width, int(self.final_width * (self.Size[0] / self.Size[1]))))
        self.image_to_show3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP_image_to_show2))
        self.canvas_img.create_image(0, 0, image=self.image_to_show3, anchor=NW)
        self.canvas_img.config(width=self.final_width, height=int(self.final_width * (self.Size[0] / self.Size[1])))



    def Zoom_in(self, event):
        self.new_zoom_sq=[0,0,0,0]
        or_event=event
        PX=event.x/((self.zoom_sq[2]-self.zoom_sq[0])/self.ratio)
        PY=event.y/((self.zoom_sq[3]-self.zoom_sq[1])/self.ratio)

        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]
        ZWX = (self.zoom_sq[2]-self.zoom_sq[0])*(1-self.zoom_strength)
        ZWY = (self.zoom_sq[3]-self.zoom_sq[1])*(1-self.zoom_strength)

        if ZWX>100:
            self.new_zoom_sq[0] = int(event.x-PX*ZWX)
            self.new_zoom_sq[2] = int(event.x+(1-PX)*ZWX)
            self.new_zoom_sq[1] = int(event.y - PY*ZWY)
            self.new_zoom_sq[3] = int(event.y + (1-PY)*ZWY)

            self.ratio=ZWX/self.final_width
            self.zoom_sq=self.new_zoom_sq
            self.zooming = True
            self.afficher()

    def Zoom_out(self, event):
        self.new_zoom_sq = [0, 0, 0, 0]
        PX = event.x / ((self.zoom_sq[2] - self.zoom_sq[0]) / self.ratio)
        PY = event.y / ((self.zoom_sq[3] - self.zoom_sq[1]) / self.ratio)

        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]
        ZWX = (self.zoom_sq[2] - self.zoom_sq[0]) * (1 + self.zoom_strength)
        ZWY = (self.zoom_sq[3] - self.zoom_sq[1]) * (1 + self.zoom_strength)

        if ZWX<self.Size[1] and ZWY<self.Size[0]:
            if int(event.x - PX * ZWX)>=0 and int(event.x + (1 - PX) * ZWX)<=self.Size[1]:
                self.new_zoom_sq[0] = int(event.x - PX * ZWX)
                self.new_zoom_sq[2] = int(event.x + (1 - PX) * ZWX)
            elif int(event.x + (1 - PX) * ZWX)>self.Size[1]:
                self.new_zoom_sq[0] = int(self.Size[1]-ZWX)
                self.new_zoom_sq[2] = int(self.Size[1])
            elif int(event.x - PX * ZWX)<0:
                self.new_zoom_sq[0] = 0
                self.new_zoom_sq[2] = int(ZWX)

            if int(event.y - PY * ZWY)>=0 and int(event.y + (1 - PY) * ZWY)<=self.Size[0]:
                self.new_zoom_sq[1] = int(event.y - PY * ZWY)
                self.new_zoom_sq[3] = int(event.y + (1 - PY) * ZWY)
            elif int(event.y + (1 - PY) * ZWY)>self.Size[0]:
                self.new_zoom_sq[1] = int(self.Size[0]-ZWY)
                self.new_zoom_sq[3] = int(self.Size[0])
            elif int(event.y - PY * ZWY)<0:
                self.new_zoom_sq[1] = 0
                self.new_zoom_sq[3] = int(ZWY)

            self.ratio = ZWX / self.final_width


        else:
            self.new_zoom_sq=[0,0,self.Vid.shape[1],self.Vid.shape[0]]
            self.ratio=self.Size[1]/self.final_width


        self.zoom_sq = self.new_zoom_sq
        self.zooming = False
        self.afficher()



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