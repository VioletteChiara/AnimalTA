from tkinter import *
from AnimalTA.A_General_tools import Color_settings

class Pers_Scroll(Canvas):
    '''
    This Class is a personalized scrollbar/timeline. It is part of the Video Reader and allow to view a specific frame of the video, to move between frames etc.
    '''
    def __init__(self, parent, container, width=800, ecart=0, show_cropped=True, **kw):
            Canvas.__init__(self, parent, kw)
            self.list_colors = Color_settings.My_colors.list_colors
            self.Top=container #Here the Video reader
            self.Video=self.Top.Vid#The video we are interested in
            self.parent=parent#The frame widget of the Video reader within which this scrollbar will appear
            self.decalage=25#Esthetical point
            self.size_hide=40#Esthetical point
            self.config(width=width, height=50, borderwidth=0,**Color_settings.My_colors.Frame_Base, highlightthickness=0)

            self.hide_crop=False

            self.fr_rate=self.Video.Frame_rate[1]
            self.one_every=self.Video.Frame_rate[0]/ self.Video.Frame_rate[1]#Related to the frame rate, if it has been modified by the user: 1 frame evry self.one_every frames will be displayed. If not modified by user, this equals one.
            self.ecart=ecart*self.one_every #If the video has been cropped, how much supplementary frames do we show in the timebar? (same value for before/after cropped frames)

            self.crop_beg = round(self.Video.Cropped[1][0] / self.one_every)
            self.crop_end = round(self.Video.Cropped[1][1] / self.one_every)

            if self.ecart!=0 or show_cropped:
                self.debut=max(0,self.crop_beg-ecart)
                self.fin = min(self.Video.Frame_nb[1] - 1, self.crop_end + ecart)
            else:
                self.debut=0
                self.fin = self.Video.Frame_nb[1] - 1

            if show_cropped:
                self.to_show_sub=self.crop_beg
            else:
                self.to_show_sub=0

            self.video_length = self.fin - self.debut
            self.active_pos=self.crop_beg#the current position of the frame reader (implemented at the first frame of the video, after cropping)
            self.refresh()

            self.bind("<Motion>", self.afficher_frame)#Display a little square/info to tell the user what is the frame number under the mouse cursor
            self.bind("<Button-1>", self.activate_position)#Change the current frame
            self.bind("<B1-Motion>", self.move_position)#Change the current frame

    def close_N_destroy(self):
        '''
        Destroy the Scrollbar, this is called when the Video Reader is destroyed
        '''
        self.delete("all")
        self.unbind_all("<Motion>")
        self.unbind_all("<Button-1>")
        self.unbind_all("<B1-Motion>")

    def refresh(self, *args):
        #Draw/Redraw the timeline, each time something is modified or that the containing widget size changes, the timeline is redraw.
        width=self.parent.winfo_width()
        largscroll = width - 60
        largscan = width - 10
        self.delete("all")
        self.create_rectangle(0, 0, self.decalage, 20, fill=self.list_colors["Timeline_back"])
        self.create_rectangle(self.decalage-1, 0, largscroll + self.decalage+1, 20, fill=self.list_colors["Timeline_out"])
        self.create_rectangle(0, 20, largscan, 50, fill=self.list_colors["Timeline_back"], outline=self.list_colors["Timeline_back"])
        self.create_text(self.decalage, 27, fill=self.list_colors["Fg_Timeline"], font="Times 10 bold", text=self.debut-self.to_show_sub)
        self.create_text(largscroll + self.decalage, 27, fill=self.list_colors["Fg_Timeline"], font="Times 10 bold",text=self.fin-self.to_show_sub)
        self.create_text(largscroll + self.decalage, 40, fill=self.list_colors["Fg_Timeline"], font="Times 10 bold",text=str(round((self.video_length-self.to_show_sub)/self.fr_rate,2))+" s")

        if not self.hide_crop:
            self.create_rectangle((self.crop_beg-self.debut) / self.video_length * largscroll + self.decalage - 2, 0,(self.crop_beg-self.debut) / self.video_length * largscroll + self.decalage + 2, 20, fill=self.list_colors["Timeline_deb"],outline="", width=2)
            self.create_rectangle((self.crop_beg-self.debut) / self.video_length * largscroll + self.decalage - self.size_hide, 20,(self.crop_beg-self.debut) / self.video_length * largscroll + self.decalage + self.size_hide, 50, fill=self.list_colors["Timeline_back"],outline="", width=2)
            self.create_text((self.crop_beg-self.debut) / self.video_length * largscroll + self.decalage, 27, fill=self.list_colors["Timeline_deb"],font="Times 10 bold", text=self.crop_beg-self.to_show_sub)
            self.create_text((self.crop_beg-self.debut) / self.video_length * largscroll + self.decalage, 40, fill=self.list_colors["Timeline_deb"],font="Times 10 bold", text=str(round((self.crop_beg-self.to_show_sub)/self.fr_rate,2))+ " s")

            self.create_rectangle((self.crop_end-self.debut)  / self.video_length * largscroll + self.decalage - 2, 0,(self.crop_end-self.debut)  / self.video_length * largscroll + self.decalage + 2, 20, fill=self.list_colors["Timeline_end"],outline="", width=2)
            self.create_rectangle((self.crop_end-self.debut) / self.video_length * largscroll + self.decalage - self.size_hide, 20,(self.crop_end-self.debut)  / self.video_length * largscroll + self.decalage + self.size_hide, 50, fill=self.list_colors["Timeline_back"],outline="", width=2)
            self.create_text((self.crop_end-self.debut)  / self.video_length * largscroll + self.decalage, 27, fill=self.list_colors["Timeline_end"],font="Times 10 bold", text=self.crop_end - self.to_show_sub)
            self.create_text((self.crop_end-self.debut)  / self.video_length * largscroll + self.decalage, 40, fill=self.list_colors["Timeline_end"],font="Times 10 bold", text=str(round((self.crop_end - self.to_show_sub)/self.fr_rate,2))+ " s")
            self.create_rectangle((self.crop_beg-self.debut) / self.video_length * largscroll + self.decalage + 2, 0,(self.crop_end-self.debut) / self.video_length * largscroll + self.decalage - 2, 20, fill=self.list_colors["Timeline_in"],outline="", width=2)

        self.create_rectangle((self.active_pos-self.debut) / self.video_length * largscroll + self.decalage - 2, 0,(self.active_pos-self.debut) / self.video_length * largscroll + self.decalage + 2, 20,outline=self.list_colors["Fg_Timeline"], width=2)
        self.create_rectangle((self.active_pos-self.debut) / self.video_length * largscroll + self.decalage - self.size_hide, 20,
                              (self.active_pos-self.debut) / self.video_length * largscroll + self.decalage + self.size_hide, 50,
                              fill=self.list_colors["Timeline_back"], outline=self.list_colors["Timeline_back"])
        self.create_text((self.active_pos-self.debut) / self.video_length * largscroll + self.decalage, 27, fill=self.list_colors["Fg_Timeline"],font="Times 10 bold", text=self.active_pos - self.to_show_sub)
        self.create_text((self.active_pos-self.debut) / self.video_length * largscroll + self.decalage, 40, fill=self.list_colors["Fg_Timeline"],font="Times 10 bold", text=str(round((self.active_pos - self.to_show_sub)/self.fr_rate,2)) +" s")

    def afficher_frame(self,event):
        '''
        Draw a little rectangle and show text under the mouse cursor to indicates which of the frame would be selected if the user click.
        '''
        width=self.parent.winfo_width()
        largscroll = width - 60
        if event.x>self.decalage and event.x<largscroll+self.decalage and event.y>0 and event.y<20:
            self.refresh()
            self.create_rectangle(event.x-self.size_hide,20,event.x+self.size_hide,50, fill=self.list_colors["Timeline_back"],outline=self.list_colors["Timeline_back"])
            self.create_text(event.x,27, fill=self.list_colors["Fg_Timeline"], font="Times 10 bold", text=(int((event.x-self.decalage) * self.video_length / largscroll)+ self.debut - self.to_show_sub))
            self.create_text(event.x,40, fill=self.list_colors["Fg_Timeline"], font="Times 10 bold", text=str(round(int(self.debut- self.to_show_sub+((event.x-self.decalage) * self.video_length / largscroll))/self.fr_rate,2))+" s")

    def activate_position(self,event):
        '''
        When timeline is clicked
        Change the current frame displayed on the Video Reader.
        '''
        width=self.parent.winfo_width()
        largscroll = width - 60
        if event.x>self.decalage and event.x<largscroll+self.decalage and event.y>0 and event.y<20:
            self.active_pos=int(self.debut + int((event.x-self.decalage) * self.video_length / largscroll))
            self.refresh()
            self.Top.update_image(self.active_pos)

    def move_position(self,event):
        '''
        When the user B1-Motion on the timeline.
        Change the current frame displayed on the Video Reader.
        '''
        width=self.parent.winfo_width()
        largscroll = width - 60
        if event.x>self.decalage and event.x<(largscroll+self.decalage):
            self.active_pos=int(self.debut + round((event.x-self.decalage) * self.video_length / largscroll))
            self.refresh()
            self.Top.update_image(self.active_pos)
        elif event.x<self.decalage:
            self.active_pos=int(self.debut)
            self.refresh()
            self.Top.update_image(self.active_pos)

        elif event.x>(largscroll+self.decalage):
            self.active_pos=int(self.debut + round((largscroll) * self.video_length / largscroll))
            self.refresh()
            self.Top.update_image(self.active_pos)