from tkinter import *
from tkinter import messagebox
import numpy as np
import cv2
from BioTrack import Class_Scroll_crop, UserMessages
import time
import math
import PIL.Image, PIL.ImageTk
import decord

import psutil


class Lecteur(Frame):
    """
    A class inherited from TkFrame that will contain the video reader.
    It allows to visualize the video, zoom in/out, move in the video time space (with a time-bar) and interact with its
    containers (higher level classes) through bindings on the image canvas.
    """

    def __init__(self, parent, Vid, ecart=0, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.Vid=Vid
        self.ecart=ecart
        self.first=True

        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        self.Messages = UserMessages.Mess[self.Language.get()]
        f.close()

        self.bind("<Configure>", self.update_ratio)



        #Relative to the video:
        self.one_every = int(round(round(self.Vid.Frame_rate[0], 2) / self.Vid.Frame_rate[1]))
        self.current_part = 0
        self.fr_rate = self.Vid.Frame_rate[1]
        self.wait = (1 / (self.fr_rate))

        self.to_sub = round(((self.Vid.Cropped[1][0]) / self.one_every))
        self.Size=self.Vid.shape

        self.update_image(self.Vid.Cropped[1][0]/self.one_every, first=True)
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
        self.Speed_S = Scale(self.canvas_buttons, label=self.Messages["Control10"], variable=self.speed, from_=-10, to=100, orient=HORIZONTAL, command=self.change_speed, background="SystemButtonFace")
        self.Speed_S.grid(row=0, column=9, sticky="we")

        self.canvas_buttons.grid_columnconfigure((1,3,5,7,9), weight=3, uniform="column")
        self.canvas_buttons.grid_columnconfigure((0,2,4,6,8), weight=1, uniform="column")
        self.canvas_buttons.columnconfigure(5, minsize=50)

        self.canvas_video.focus_set()  ###########
        self.check_memory_overload()

        #For zoom:
        self.final_width = 250
        self.zoom_strength = 0.3
        self.zoom_sq = [0, 0, self.Vid.shape[1], self.Vid.shape[0]]
        self.ratio = self.Size[1] / self.final_width


    def update_ratio(self, *args):
        best_ratio = max(self.Size[1] / (self.canvas_video.winfo_width() - 5),
                         self.Size[0] / (self.canvas_video.winfo_height() - 5))
        prev_final_width = self.final_width

        self.final_width = int(math.floor(self.Size[1] / best_ratio))
        self.ratio = self.ratio * (prev_final_width / self.final_width)

    def check_memory_overload(self):
        self.parent.after(1000, self.check_memory_overload)
        if psutil.virtual_memory()._asdict()["percent"]>99.8:
            self.parent.End_of_window()
            messagebox.showinfo(self.Messages["TError_memory"], self.Messages["Error_memory"])


    def change_speed(self, *args):
        if self.speed.get()==0:
            self.wait=(1 / (self.fr_rate))
        elif self.speed.get()<0:
            self.wait = (1 / (self.fr_rate))*(abs(self.speed.get()))
        elif self.speed.get()>0:
            self.wait = (1 / (self.fr_rate))/(abs(self.speed.get())+1)
        self.jump_image=1

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
                self.capture = decord.VideoReader(self.Vid.Fusion[self.current_part][1], ctx=decord.cpu(0))


            TMP_image_to_show = self.capture[int(self.Scrollbar.active_pos*self.one_every)-self.Vid.Fusion[self.current_part][0]].asnumpy()
            self.parent.modif_image(TMP_image_to_show)


    def move1(self, event=None, nb_fr=1, aff=True, *arg):
        if self.Scrollbar.active_pos<(self.Vid.Frame_nb[1]-nb_fr) and ((self.ecart > 0 and self.Scrollbar.active_pos<(self.Vid.Cropped[1][1]/self.one_every) + self.ecart -nb_fr) or self.ecart == 0):
            self.Scrollbar.active_pos+=nb_fr
            self.Scrollbar.refresh()

            if (self.Scrollbar.active_pos*self.one_every)-self.Vid.Fusion[self.current_part][0]<len(self.capture):
                TMP_image_to_show = self.capture[int(self.Scrollbar.active_pos*self.one_every)-self.Vid.Fusion[self.current_part][0]].asnumpy()

            else:
                self.current_part += 1
                self.capture = decord.VideoReader(self.Vid.Fusion[self.current_part][1], ctx=decord.cpu(0))
                TMP_image_to_show = self.capture[int(self.Scrollbar.active_pos * self.one_every) - self.Vid.Fusion[self.current_part][0]].asnumpy()

            return(self.parent.modif_image(TMP_image_to_show, aff=aff))



    def play(self, select=False, remove_select=False, begin=0):
        within=self.Scrollbar.active_pos < (self.Vid.Frame_nb[1] - 1) and ((self.ecart > 0 and self.Scrollbar.active_pos < (self.Vid.Cropped[1][1]/self.one_every) + self.ecart) or self.ecart == 0)
        if within:
            self.playing=True

        self.jump_image = 1
        while self.playing and within:######NEW
            duration_beg=time.time()
            within = self.Scrollbar.active_pos < (self.Vid.Frame_nb[1] - 1) and ((self.ecart > 0 and self.Scrollbar.active_pos < (self.Vid.Cropped[1][1]/self.one_every) + self.ecart) or self.ecart == 0)

            self.move1(nb_fr=self.jump_image)

            #Only for view and correct tracks
            self.update()

            if select:
                if not remove_select:
                    self.parent.tree.selection_add(self.parent.tree.get_children("")[begin:((self.Scrollbar.active_pos + 1) - self.to_sub)])
                else:
                    for item in self.parent.tree.selection():
                        self.parent.tree.selection_remove(item)
                    self.parent.tree.selection_add(self.parent.tree.get_children("")[begin:((self.Scrollbar.active_pos + 1) - self.to_sub)])


            duration=0
            while duration <= (self.wait*(self.jump_image)-0.00001):#To ensure that we keep the good frame rate
                duration=time.time()-duration_beg

            if duration>(self.wait*(self.jump_image)*1.1):
                self.jump_image += int((duration/(self.wait*(self.jump_image))-1))
            elif duration<(self.wait*(self.jump_image)*1.1) and self.jump_image>1:
                self.jump_image -= max(1,int(((self.wait*(self.jump_image)/duration)-1)))


    def stop(self):
        self.playing = False

    def update_image(self, frame, first=False):
        frame=int(frame)
        Which_part=0
        if len(self.Vid.Fusion)>1:#If videos were concatenated
            Which_part = [index for index, Fu_inf in enumerate(self.Vid.Fusion) if Fu_inf[0] <= (frame * self.one_every)][-1]

        if first:
            self.capture = decord.VideoReader(self.Vid.Fusion[Which_part][1], ctx=decord.cpu(0))

            self.Prem_image_to_show = self.capture[int(frame * self.one_every) - self.Vid.Fusion[self.current_part][0]].asnumpy()
            TMP_image_to_show = np.copy(self.Prem_image_to_show)
            self.last_img=TMP_image_to_show

            self.Vid.Frame_nb[0]=len(self.capture)
            self.Vid.Frame_nb[1] = self.Vid.Frame_nb[0]/self.one_every
            if not self.Vid.Cropped[0]:
                self.Vid.Cropped[1][1]=self.Vid.Frame_nb[0]-1

        else:
            if Which_part!=self.current_part:#If we are changing from one video segment to another (concatenated videos)
                self.capture = decord.VideoReader(self.Vid.Fusion[Which_part][1], ctx=decord.cpu(0))


            TMP_image_to_show = self.capture[int(frame * self.one_every) - self.Vid.Fusion[self.current_part][0]].asnumpy()
            self.parent.modif_image(TMP_image_to_show)

        self.current_part = Which_part


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
            self.parent.modif_image(self.parent.last_empty)

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
        self.parent.modif_image(self.parent.last_empty)


    def bindings(self):
        self.bind_all("<Right>", self.move1)
        self.bind_all("<Left>", self.back1)
        self.bind_all("<space>", self.playbacks)
        self.canvas_video.bind("<Control-1>", self.Zoom_in)
        self.canvas_video.bind("<Control-3>", self.Zoom_out)
        self.canvas_video.bind("<Shift-1>", lambda x: self.callback(event=x,Shift=True))
        self.canvas_video.bind("<Configure>", self.resize)
        self.Frame_scrollbar.bind("<Configure>", self.Scrollbar.refresh)

        self.canvas_video.bind("<Button-1>", self.callback)
        self.canvas_video.bind("<B1-Motion>", self.callback_move)
        self.canvas_video.bind("<ButtonRelease>", self.release)

    def unbindings(self):
        self.unbind_all("<Right>")
        self.unbind_all("<Left>")
        self.unbind_all("<space>")
        self.canvas_video.unbind("<Control-1>")
        self.canvas_video.unbind("<Control-3>")
        self.canvas_video.unbind("<Shift-1>")
        self.canvas_video.unbind("<Configure>")
        self.Frame_scrollbar.unbind("<Configure>")

        self.canvas_video.unbind("<Button-1>")
        self.canvas_video.unbind("<B1-Motion>")
        self.canvas_video.unbind("<ButtonRelease>")

    def callback(self, event, Shift=False):
        event.x = int( self.ratio * (event.x - (self.canvas_video.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
        event.y = int( self.ratio * (event.y - (self.canvas_video.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]
        self.parent.pressed_can((event.x,event.y), Shift)

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
        if self.first:
            self.first=False
            self.Size=img.shape
            self.ratio=self.Size[1]/self.final_width

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
        self.unbindings()
        del self.capture
        self.stop()
        self.Scrollbar.close_N_destroy()
        self.Scrollbar.destroy()
