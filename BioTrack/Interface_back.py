from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
import decord
from BioTrack import UserMessages
import numpy as np


class Background(Frame):
    def __init__(self, parent, boss, main_frame, Video_file, portion=False, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.main_frame=main_frame
        self.boss=boss
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.portion=portion

        if self.portion:
            Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
            Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW
            self.parent.geometry("1200x750")


        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        self.Vid = Video_file
        self.background=self.Vid.Back[1]
        self.zoom_sq=[0,0,self.Vid.shape[1],self.Vid.shape[0]]

        self.canvas_img = Canvas(self, width=10, height=10, bd=0, highlightthickness=0, relief='ridge')
        self.canvas_img.grid(row=0,column=0, sticky="nsew")
        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        self.ratio=1
        self.final_width=750
        self.Size = self.Vid.shape
        self.canvas_img.bind("<Configure>", self.afficher)



        self.canvas_help = Frame(self.parent, width=50,  highlightthickness=4, relief='flat', highlightbackground="RoyalBlue3")
        self.canvas_help.grid(row=0, column=1, sticky="new")
        Info_title=Label(self.canvas_help, text=self.Messages["Info"],  justify=CENTER, background="RoyalBlue3", fg="white", font=("Helvetica", 16, "bold"))
        Info_title.grid(row=0, sticky="new")
        Grid.columnconfigure(self.canvas_help, 0, weight=1)
        self.Label_user = Label(self.canvas_help, justify=LEFT,text=self.Messages["Back2"], wraplengt=250)
        self.Label_user.grid(row=1,column=0,columnspan=2,sticky="nsew")

        self.canvas_user = Canvas(self.parent, width=10, height=10, bd=0, highlightthickness=0, relief='ridge')
        self.canvas_user.grid(row=1,column=1,sticky="ns")

        self.Label_color=Label(self.canvas_user, justify=RIGHT, text=self.Messages["Back3"])
        self.Label_color.grid(row=0,column=0,sticky="e")
        self.canvas_color=Canvas(self.canvas_user, width=10, height=10, bd=0, highlightthickness=1, highlightbackground="black", relief='ridge')
        self.canvas_color.grid(row=0,column=1, sticky="nswe")
        self.validate_button=Button(self.canvas_user,text=self.Messages["Validate"], background="green", command=self.validate)
        self.validate_button.grid(row=1,column=0,columnspan=2,sticky="nsew")

        self.B_1Auto=Button(self.canvas_user,text=self.Messages["Back4"], background="orange", command=self.auto_back)
        self.B_1Auto.grid(row=2,column=0,columnspan=2,sticky="nsew")
        self.B_1frame=Button(self.canvas_user,text=self.Messages["Back5"], background="red", command=self.change_for_1)
        self.B_1frame.grid(row=3,column=0,columnspan=2,sticky="nsew")

        if self.portion:
            self.canvas_help.grid_columnconfigure(0,minsize=250)




        self.Size=self.background.shape
        self.zooming=False
        self.zoom_strength=0.3
        self.canvas_img.bind("<Button-1>",self.point)
        self.canvas_img.bind("<Control-1>", self.Zoom_in)
        self.canvas_img.bind("<ButtonRelease-1>", self.Leave_zoom)
        self.canvas_img.bind("<Control-3>", self.Zoom_out)
        self.bind_all("<Control-z>", self.remove_last)
        self.canvas_img.bind("<Button-3>", self.change_color)
        self.canvas_img.bind("<B1-Motion>", self.paint)
        self.canvas_img.bind("<MouseWheel>", self.On_mousewheel)
        self.canvas_img.bind("<Motion>", self.Show_tool)

        self.liste_paints=[]
        self.painting=False
        self.tool_view=self.canvas_img.create_oval((0,0,0,0))
        self.vide=[]
        self.tool_size=20
        self.Color=0

        self.canvas_img.update()
        self.final_width = self.canvas_img.winfo_width()
        self.ratio = self.Size[1] / self.final_width

        self.afficher()


    def auto_back(self):
        self.Vid.make_back()
        self.background=self.Vid.Back[1]
        self.liste_paints=[]
        self.afficher()

    def change_for_1(self):
        self.capture = decord.VideoReader(self.Vid.File_name)
        self.liste_paints=[]
        Which_part=0
        if self.Vid.Cropped[0]:
            if len(self.Vid.Fusion) > 1:  # Si on a plus d'une video
                Which_part = [index for index, Fu_inf in enumerate(self.Vid.Fusion) if Fu_inf[0] <= self.Vid.Cropped[1][0]][-1]
                if Which_part!=0:#si on est pas dans la première partie de la vidéo
                    self.capture = decord.VideoReader(self.Vid.Fusion[Which_part][1])

        self.Represent = self.capture[self.Vid.Cropped[1][0]-self.Vid.Fusion[Which_part][0]-1].asnumpy()
        self.background=cv2.cvtColor(self.Represent,cv2.COLOR_BGR2GRAY)
        self.afficher()

    def Leave_zoom(self, event):
        self.zooming = False
        if self.painting:
            self.painting=False

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
            self.Show_tool(event,zoom=(event.x,event.y))

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
        self.Show_tool(event)


    def Show_tool(self, event, zoom=[]):
        if not len(zoom)>0:
            self.canvas_img.delete(self.tool_view)
            self.tool_view=self.canvas_img.create_oval((event.x - self.tool_size/self.ratio,
                                        event.y - self.tool_size/self.ratio,
                                        event.x + self.tool_size/self.ratio,
                                        event.y  + self.tool_size/self.ratio))


    def point(self, event):
        if self.painting == False:
            self.vide = np.zeros(self.background.shape, np.uint8)

        if not self.zooming:
            cv2.circle(self.vide,
                       (int(event.x * self.ratio + self.zoom_sq[0]), int(event.y * self.ratio + self.zoom_sq[1])),
                       self.tool_size, (255, 255, 255), -1)
            cnts, _ = cv2.findContours(self.vide, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

            if self.painting:
                self.liste_paints.pop()

            self.liste_paints.append([cnts, self.Color])
            self.afficher()
            self.Show_tool(event)
            self.painting = True

    def paint(self, event):
        if self.painting==False:
            self.vide = np.zeros(self.background.shape, np.uint8)

        if not self.zooming:
            cv2.circle(self.vide, (int(event.x * self.ratio + self.zoom_sq[0]), int(event.y * self.ratio + self.zoom_sq[1])),
                       self.tool_size, (255, 255, 255), -1)
            cnts, _ = cv2.findContours(self.vide, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

            if self.painting:
                self.liste_paints.pop()

            self.liste_paints.append([cnts, self.Color])
            self.afficher()
            self.Show_tool(event)
            self.painting=True

    def change_color(self, event):
        self.Color=int(self.background[int(event.y*self.ratio+self.zoom_sq[1]), int(event.x*self.ratio+self.zoom_sq[0])])
        self.afficher()
        mycolor = '#%02x%02x%02x' % (self.Color,self.Color,self.Color)
        self.canvas_color.config(background=mycolor)
        self.Show_tool(event)


    def On_mousewheel(self, event):
        if event.delta>0 or (self.tool_size>5 and event.delta<0):
            self.tool_size = int(self.tool_size  + (event.delta / 120))
        self.afficher()
        self.Show_tool(event)


    def afficher(self, *arg):
        best_ratio = max(self.Size[1] / (self.canvas_img.winfo_width()),self.Size[0] / (self.canvas_img.winfo_height()))
        prev_final_width=self.final_width
        self.final_width=int(self.Size[1]/best_ratio)
        self.ratio=self.ratio*(prev_final_width/self.final_width)

        empty_back=np.copy(self.background)
        if len(self.liste_paints)>0:
            for paint in self.liste_paints:
                cv2.drawContours(empty_back,paint[0],-1,paint[1],-1)
        self.image_to_show=empty_back[self.zoom_sq[1]:self.zoom_sq[3],self.zoom_sq[0]:self.zoom_sq[2]]
        self.image_to_show=cv2.resize(self.image_to_show,(self.final_width,int(self.final_width*(self.Size[0]/self.Size[1]))))
        self.image_to_show = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.image_to_show))
        self.canvas_img.create_image(0, 0, image=self.image_to_show, anchor=NW)
        self.canvas_img.config(width=self.final_width, height=int(self.final_width*(self.Size[0]/self.Size[1])))

    def remove_last(self, *arg):
        if len(self.liste_paints)>0:
            self.liste_paints.pop()
            self.afficher()

    def validate(self):
        if len(self.liste_paints)>0:
            for paint in self.liste_paints:
                cv2.drawContours(self.background,paint[0],-1,paint[1],-1)
        self.Vid.Back[1]=self.background
        if not self.portion:
            self.boss.update_back()
        if self.portion:
            self.boss.PortionWin.grab_set()
        self.End_of_window()

    def End_of_window(self):
        self.unbind_all("<Button-1>")
        self.grab_release()
        self.canvas_help.grid_forget()
        self.canvas_help.destroy()
        self.canvas_user.grid_forget()
        self.canvas_user.destroy()
        if not self.portion:
            self.boss.update()
            self.main_frame.return_main()
        if self.portion:
            self.parent.destroy()

"""
root = Tk()
root.geometry("+100+100")
Video_file=Class_Video.Video(File_name="D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01.avi")
Video_file.Back[0]=True

im=cv2.imread("D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01_background.bmp")
im=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
Video_file.Back[1]=im
interface = Background(parent=root, boss=None, Video_file=Video_file)
root.mainloop()
"""