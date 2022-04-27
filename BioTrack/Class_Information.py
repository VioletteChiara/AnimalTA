from tkinter import *
import numpy as np
import cv2
from BioTrack import Class_Scroll_crop, UserMessages
import time
import math
import PIL.Image, PIL.ImageTk


class Lecteur(Frame):
    def __init__(self, parent, Vid, ecart=0, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.Vid=Vid
        self.ecart=ecart


        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        self.Messages = UserMessages.Mess[self.Language.get()]
        f.close()



        #Relative to the video:
        self.capture = cv2.VideoCapture(self.Vid.File_name)
        self.one_every = int(round(round(self.Vid.Frame_rate[0], 2) / self.Vid.Frame_rate[1]))
        self.current_part = 0
        self.fr_rate = self.Vid.Frame_rate[1]
        self.wait = (1 / (self.fr_rate))
        if self.Vid.Cropped[0]:
            self.to_sub = round(((self.Vid.Cropped[1][0]) / self.one_every))
        else:
            self.to_sub = 0
        self.Size=self.Vid.shape

        if self.Vid.Cropped[0]:
            self.update_image(self.Vid.Cropped[1][0]/self.one_every, first=True)
        else:
            self.update_image(0, first=True)


        #Pour le zoom:
        self.final_width = 250
        self.zoom_strength = 0.3
        self.zoom_sq = [0, 0, self.Vid.shape[1], self.Vid.shape[0]]
        self.ratio = self.Size[1] / self.final_width

        self.playing=False

        self.canvas_video = Canvas(self, bd=2, highlightthickness=1, relief='ridge')
        self.canvas_video.grid(row=1, column=0, sticky="nsew")
        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=1)  ########NEW



        self.Frame_scrollbar = Frame(self)
        self.Frame_scrollbar.grid(row=2, column=0, sticky="swe")
        Grid.columnconfigure(self.Frame_scrollbar, 0, weight=1)  ########NEW
        self.Scrollbar = Class_Scroll_crop.Pers_Scroll(self.Frame_scrollbar, container=self, bd=2, highlightthickness=1, relief='ridge', ecart=self.ecart)  #################NEWWWW
        self.Scrollbar.grid(sticky="ew")  #################NEWWWW

        self.canvas_buttons = Frame(self, bd=2, highlightthickness=1, background="grey")
        self.canvas_buttons.grid(row=3, column=0, sticky="nsew")
        Grid.columnconfigure(self.canvas_buttons, 0, weight=1)  ########NEW

        # Widgets:
        self.bouton_Play = Button(self.canvas_buttons, text=self.Messages["PlayB1"], command=self.play)
        self.bouton_Play.grid(row=0, column=1, sticky="we")
        self.bouton_Stop = Button(self.canvas_buttons, text=self.Messages["PlayB2"], command=self.stop)
        self.bouton_Stop.grid(row=0, column=3, sticky="we")
        self.bouton_GTBeg = Button(self.canvas_buttons, text=self.Messages["PlayB3"], command=self.GotoBeg)
        self.bouton_GTBeg.grid(row=0, column=5, sticky="we")
        self.bouton_GTEnd = Button(self.canvas_buttons, text=self.Messages["PlayB4"], command=self.GotoEnd)
        self.bouton_GTEnd.grid(row=0, column=7, sticky="we")

        self.speed=IntVar()
        self.speed.set(0)
        self.Speed_S = Scale(self.canvas_buttons, label=self.Messages["Control10"], variable=self.speed, from_=-5, to=10, orient=HORIZONTAL, command=self.change_speed, background="SystemButtonFace")
        self.Speed_S.grid(row=0, column=9, sticky="we")

        self.canvas_buttons.grid_columnconfigure((1,3,5,7,9), weight=3, uniform="column")
        self.canvas_buttons.grid_columnconfigure((0,2,4,6,8), weight=1, uniform="column")
        self.canvas_buttons.columnconfigure(5, minsize=50)

        self.canvas_video.focus_set()  ###########


    def change_speed(self, *args):
        if self.speed.get()==0:
            self.wait=(1 / (self.fr_rate))
        elif self.speed.get()<0:
            self.wait = (1 / (self.fr_rate))*(abs(self.speed.get()))
        elif self.speed.get()>0:
            self.wait = (1 / (self.fr_rate))/(abs(self.speed.get())+1)
        self.jump_image=0

    def resize(self, event):
        self.afficher_img(self.last_img)

    def GotoBeg(self):
        if not self.Vid.Cropped[0]:
            new_frame=0
        else:
            new_frame=int(self.Vid.Cropped[1][0]/self.one_every)

        self.Scrollbar.active_pos = new_frame  ####NEW
        self.Scrollbar.refresh()
        self.update_image(new_frame)


    def GotoEnd(self):
        if not self.Vid.Cropped[0]:
            new_frame = int((self.Vid.Frame_nb[1])/self.one_every)-1
        else:
            new_frame = int(self.Vid.Cropped[1][1]/self.one_every)

        self.Scrollbar.active_pos = new_frame  ####NEW
        self.Scrollbar.refresh()
        self.update_image(new_frame)


    def playbacks(self, *arg):
        if self.playing:
            self.stop()
        else:
            self.play()


    def back1(self, *arg):
        if self.Scrollbar.active_pos>0 and ((self.ecart>0 and self.Scrollbar.active_pos>self.Vid.Cropped[1][0]/self.one_every-self.ecart) or self.ecart==0) :
            self.Scrollbar.active_pos=self.Scrollbar.active_pos-1
            self.Scrollbar.refresh()

            if self.Vid.Fusion[self.current_part][0]>(self.Scrollbar.active_pos * self.one_every):
                self.current_part-=1
                self.capture.release()
                self.capture = cv2.VideoCapture(self.Vid.Fusion[self.current_part][1])

            self.capture.set(cv2.CAP_PROP_POS_FRAMES, int(self.Scrollbar.active_pos*self.one_every)-self.Vid.Fusion[self.current_part][0])###NEW
            self.ret, self.TMP_image_to_show = self.capture.read()
            self.TMP_image_to_show = cv2.cvtColor(self.TMP_image_to_show, cv2.COLOR_BGR2RGB)
            self.parent.modif_image(self.TMP_image_to_show)


    def move1(self, *arg):
        if self.Scrollbar.active_pos<(self.Vid.Frame_nb[1]-1) and ((self.ecart > 0 and self.Scrollbar.active_pos<(self.Vid.Cropped[1][1]/self.one_every) + self.ecart) or self.ecart == 0):
            self.Scrollbar.active_pos+=1
            self.Scrollbar.refresh()
            for img in range(self.one_every):####NEW
                self.ret, TMP_image_to_show = self.capture.read()####NEW
                if not self.ret:
                    self.current_part+=1#On passe à la section suivante
                    self.capture.release()
                    self.capture=cv2.VideoCapture(self.Vid.Fusion[self.current_part][1])
                    self.ret, TMP_image_to_show = self.capture.read()
            TMP_image_to_show = cv2.cvtColor(TMP_image_to_show, cv2.COLOR_BGR2RGB)
            if self.ret:
                self.parent.modif_image(TMP_image_to_show)


    def play(self, select=False, remove_select=False, begin=0):
        within=self.Scrollbar.active_pos < (self.Vid.Frame_nb[1] - 1) and ((self.ecart > 0 and self.Scrollbar.active_pos < (self.Vid.Cropped[1][1]/self.one_every) + self.ecart) or self.ecart == 0)
        if within:
            self.ret=True
            self.playing=True

        self.jump_image = 0

        while self.ret and within:######NEW
            duration_beg=time.time()
            self.Scrollbar.active_pos=self.Scrollbar.active_pos+(1+self.jump_image)
            self.Scrollbar.refresh()

            within = self.Scrollbar.active_pos < (self.Vid.Frame_nb[1] - 1) and ((self.ecart > 0 and self.Scrollbar.active_pos < (self.Vid.Cropped[1][1]/self.one_every) + self.ecart) or self.ecart == 0)
            for img in range(self.one_every*(self.jump_image+1)):####NEW
                ret, TMP_image_to_show = self.capture.read()
                if not ret and self.current_part<len(self.Vid.Fusion)-1:
                    self.current_part+=1#On passe à la section suivante
                    self.capture.release()
                    self.capture=cv2.VideoCapture(self.Vid.Fusion[self.current_part][1])
                    ret, TMP_image_to_show = self.capture.read()
            TMP_image_to_show = cv2.cvtColor(TMP_image_to_show, cv2.COLOR_BGR2RGB)

            if ret:
                self.parent.modif_image(TMP_image_to_show)

            duration=0####NEW
            while duration < (self.wait*(self.jump_image+1)):####NEW
                duration=time.time()-duration_beg####NEW

            if duration>(self.wait*(self.jump_image+1)*1.1):
                self.jump_image += 1
            elif duration<(self.wait*(self.jump_image+1)*1.1) and self.jump_image>0:
                self.jump_image -= 1


            self.Scrollbar.refresh()
            if ret:
                self.update()
            else:
                self.stop()

            #Only for view and correct tracks

            if select:
                if not remove_select:
                    self.parent.tree.selection_add(self.parent.tree.get_children("")[begin:((self.Scrollbar.active_pos + 1) - self.to_sub)])
                else:
                    for item in self.parent.tree.selection():
                        self.parent.tree.selection_remove(item)
                    self.parent.tree.selection_add(self.parent.tree.get_children("")[begin:((self.Scrollbar.active_pos + 1) - self.to_sub)])

    def stop(self):
        self.ret=False
        self.playing = False

    def update_image(self, frame, first=False):
        if len(self.Vid.Fusion)>1:#Si on a plus d'une video
            Which_part = [index for index, Fu_inf in enumerate(self.Vid.Fusion) if Fu_inf[0] <= (frame * self.one_every)][-1]
            if Which_part!=self.current_part:#si on veut aller à un endroit différent
                self.capture.release()
                self.capture = cv2.VideoCapture(self.Vid.Fusion[Which_part][1])
                self.current_part=Which_part
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, int(frame * self.one_every)-self.Vid.Fusion[self.current_part][0])

        if first:
            self.ret, self.Prem_image_to_show = self.capture.read()
            TMP_image_to_show = np.copy(self.Prem_image_to_show)
            TMP_image_to_show = cv2.cvtColor(TMP_image_to_show, cv2.COLOR_BGR2RGB)  ###############3
            self.last_img=TMP_image_to_show
        else:
            self.ret, TMP_image_to_show = self.capture.read()
            TMP_image_to_show = cv2.cvtColor(TMP_image_to_show, cv2.COLOR_BGR2RGB)###############3
            self.parent.modif_image(TMP_image_to_show)


    def Zoom_in(self, event):
        self.new_zoom_sq = [0, 0, 0, 0]
        PX = (event.x- (self.canvas_video.winfo_width()-self.shape[1])/2) / ((self.zoom_sq[2] - self.zoom_sq[0]) / self.ratio)
        PY = (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2) / ((self.zoom_sq[3] - self.zoom_sq[1]) / self.ratio)

        event.x = int( self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
        event.y = int( self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]

        ZWX = (self.zoom_sq[2] - self.zoom_sq[0]) * (1 - self.zoom_strength)
        ZWY = (self.zoom_sq[3] - self.zoom_sq[1]) * (1 - self.zoom_strength)

        if ZWX > 100:
            self.new_zoom_sq[0] = int(event.x - PX * ZWX)
            self.new_zoom_sq[2] = int(event.x + (1 - PX) * ZWX)
            self.new_zoom_sq[1] = int(event.y - PY * ZWY)
            self.new_zoom_sq[3] = int(event.y + (1 - PY) * ZWY)

            self.ratio = ZWX / self.final_width
            self.zoom_sq = self.new_zoom_sq
            self.zooming = True
            self.afficher_img(self.last_img)

    def Zoom_out(self, event):
        self.new_zoom_sq = [0, 0, 0, 0]
        PX = (event.x- (self.canvas_video.winfo_width()-self.shape[1])/2) / ((self.zoom_sq[2] - self.zoom_sq[0]) / self.ratio)
        PY = (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2) / ((self.zoom_sq[3] - self.zoom_sq[1]) / self.ratio)

        event.x = int( self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
        event.y = int( self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]

        ZWX = (self.zoom_sq[2] - self.zoom_sq[0]) * (1 + self.zoom_strength)
        ZWY = (self.zoom_sq[3] - self.zoom_sq[1]) * (1 + self.zoom_strength)

        if ZWX < self.Size[1] and ZWY < self.Size[0]:
            if int(event.x - PX * ZWX) >= 0 and int(event.x + (1 - PX) * ZWX) <= self.Size[1]:
                self.new_zoom_sq[0] = int(event.x - PX * ZWX)
                self.new_zoom_sq[2] = int(event.x + (1 - PX) * ZWX)
            elif int(event.x + (1 - PX) * ZWX) > self.Size[1]:
                self.new_zoom_sq[0] = int(self.Size[1] - ZWX)
                self.new_zoom_sq[2] = int(self.Size[1])
            elif int(event.x - PX * ZWX) < 0:
                self.new_zoom_sq[0] = 0
                self.new_zoom_sq[2] = int(ZWX)

            if int(event.y - PY * ZWY) >= 0 and int(event.y + (1 - PY) * ZWY) <= self.Size[0]:
                self.new_zoom_sq[1] = int(event.y - PY * ZWY)
                self.new_zoom_sq[3] = self.new_zoom_sq[1] + int(ZWY)

            elif int(event.y + (1 - PY) * ZWY) > self.Size[0]:
                self.new_zoom_sq[1] = int(self.Size[0] - ZWY)
                self.new_zoom_sq[3] = int(self.Size[0])
            elif int(event.y - PY * ZWY) < 0:
                self.new_zoom_sq[1] = 0
                self.new_zoom_sq[3] = int(ZWY)
            self.ratio = ZWX / self.final_width


        else:
            self.new_zoom_sq = [0, 0, self.Size[1], self.Size[0]]
            self.ratio = self.Size[1] / self.final_width

        self.zoom_sq = self.new_zoom_sq
        self.zooming = False
        self.afficher_img(self.last_img)


    def bindings(self):
        self.bind_all("<Right>", self.move1)
        self.bind_all("<Left>", self.back1)
        self.bind_all("<space>", self.playbacks)
        self.canvas_video.bind("<Control-1>", self.Zoom_in)
        self.canvas_video.bind("<Control-3>", self.Zoom_out)
        self.canvas_video.bind("<Configure>", self.resize)
        self.Frame_scrollbar.bind("<Configure>", self.Scrollbar.refresh)

        self.canvas_video.bind("<Button-1>", self.callback)
        self.canvas_video.bind("<B1-Motion>", self.callback_move)
        self.canvas_video.bind("<ButtonRelease>", self.release)

    def callback(self, event):
        event.x = int( self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
        event.y = int( self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]
        self.parent.pressed_can((event.x,event.y))

    def callback_move(self, event):
        event.x = int( self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
        event.y = int( self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]
        if  event.x >= 0 and event.y >= 0 and event.x <= self.Vid.shape[1] and event.y <= self.Vid.shape[0]:
            self.parent.moved_can((event.x,event.y))

    def release(self, event):
        event.x = int( self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
        event.y = int( self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]
        self.parent.released_can((event.x,event.y))

    def afficher_img(self, img):
        self.last_img=img
        best_ratio = max(self.Size[1] / (self.canvas_video.winfo_width()-5), self.Size[0] / (self.canvas_video.winfo_height()-5))
        prev_final_width = self.final_width

        self.final_width = int(math.floor(self.Size[1] / best_ratio))
        self.ratio = self.ratio * (prev_final_width / self.final_width)


        image_to_show2 = img[self.zoom_sq[1]:self.zoom_sq[3], self.zoom_sq[0]:self.zoom_sq[2]]
        TMP_image_to_show2 = cv2.resize(image_to_show2,(self.final_width, int(self.final_width * (self.Size[0] / self.Size[1]))))

        self.shape= TMP_image_to_show2.shape

        if self.Scrollbar.active_pos<self.Scrollbar.crop_beg or self.Scrollbar.active_pos>self.Scrollbar.crop_end:
            img2= cv2.add(TMP_image_to_show2,np.array([-75.0]))
        else:
            img2=TMP_image_to_show2

        self.image_to_show3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img2))

        self.can_import = self.canvas_video.create_image((self.canvas_video.winfo_width()-self.shape[1])/2, (self.canvas_video.winfo_height()-self.shape[0])/2, image=self.image_to_show3, anchor=NW)
        self.canvas_video.config(height=self.shape[0],width=self.shape[1])
        self.canvas_video.itemconfig(self.can_import, image=self.image_to_show3)
        self.update_idletasks()

    def proper_close(self):
        self.stop()
        self.capture.release()
        self.Scrollbar.destroy()