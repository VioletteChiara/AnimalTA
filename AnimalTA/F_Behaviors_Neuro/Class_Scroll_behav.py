from tkinter import *

class Pers_Scroll(Canvas):
    '''
    This Class is a personalized scrollbar/timeline. It is part of the Video Reader and allow to view a specific frame of the video, to move between frames etc.
    '''
    def __init__(self, parent, container, ind, arena, behav, behav_ID, events, color, ecart=0, **kw):
            Frame.__init__(self, parent, kw)

            self.propagate(0)
            Grid.rowconfigure(self, 0, weight=1)
            Grid.columnconfigure(self, 0, weight=1)
            Grid.columnconfigure(self, 1, weight=1)
            Grid.columnconfigure(self, 2, weight=1)
            Grid.columnconfigure(self, 3, weight=100)

            #Delete behav
            But=Button(self, text="Del", command=self.remove)
            But.grid(row=0, column=0, sticky="nsew")

            # Behavior_name
            Lab1=Label(self, text=behav)
            Lab1.grid(row=0, column=1, sticky="nsew")

            # Individual_name
            Lab2=Label(self, text="Arena: " + arena + ", Ind: " + ind, fg=color)
            Lab2.grid(row=0,column=2, sticky="ew")

            self.Frame_for_scroll = Canvas(self, height=5)
            self.Frame_for_scroll.grid(row=0, column=3, sticky="nsew")
            Grid.columnconfigure(self.Frame_for_scroll, 0, weight=1)


            self.Top=container #Boss frame which has the information
            self.Video=self.Top.Vid#The video we are interested in
            self.parent=parent#The frame widget of the Video reader within which this scrollbar will appear
            self.decalage=25#Esthetical point
            self.size_hide=40#Esthetical point
            self.Frame_for_scroll.config(width=self.parent.winfo_width(), height=25)
            self.events=events
            self.behav_ID=behav_ID


            self.fr_rate=self.Video.Frame_rate[1]
            self.one_every=self.Video.Frame_rate[0] / self.Video.Frame_rate[1]#Related to the frame rate, if it has been modified by the user: 1 frame evry self.one_every frames will be displayed. If not modified by user, this equals one.
            self.ecart=round(ecart*self.one_every) #If the video has been cropped, how much supplementary frames do we show in the timebar? (same value for before/after cropped frames)

            self.crop_beg = round(self.Video.Cropped[1][0] / self.one_every)
            self.crop_end = round(self.Video.Cropped[1][1] / self.one_every)

            if self.ecart!=0:
                self.debut=max(0,self.crop_beg-ecart)
                self.fin = min(self.Video.Frame_nb[1] - 1, self.crop_end + ecart)
            else:
                self.debut=0
                self.fin = self.Video.Frame_nb[1] - 1

            self.video_length = self.fin - self.debut
            self.active_pos=self.crop_beg#the current position of the frame reader (implemented at the first frame of the video, after cropping)
            self.refresh()

            self.Frame_for_scroll.bind("<Motion>", self.afficher_frame)#Display a little square/info to tell the user what is the frame number under the mouse cursor
            self.Frame_for_scroll.bind("<Button-1>", self.activate_position)#Change the current frame
            self.Frame_for_scroll.bind("<B1-Motion>", self.move_position)#Change the current frame

    def close_N_destroy(self):
        '''
        Destroy the Scrollbar, this is called when the Video Reader is destroyed
        '''
        self.Frame_for_scroll.delete("all")
        self.Frame_for_scroll.unbind_all("<Motion>")
        self.Frame_for_scroll.unbind_all("<Button-1>")
        self.Frame_for_scroll.unbind_all("<B1-Motion>")

    def remove(self):
        self.Top.remove_event(self.behav_ID)
        self.destroy()


    def refresh(self, *args):
        #Draw/Redraw the timeline, each time something is modified or that the containing widget size changes, the timeline is redraw.
        width=self.Frame_for_scroll.winfo_width()
        largscroll = width - 60
        self.Frame_for_scroll.delete("all")
        self.Frame_for_scroll.create_rectangle(self.decalage-1, 2, largscroll + self.decalage+1, 20, fill='grey75')
        self.Frame_for_scroll.create_rectangle((self.active_pos-self.debut) / self.video_length * largscroll + self.decalage - 2, 2,(self.active_pos-self.debut) / self.video_length * largscroll + self.decalage + 2, 20,outline="black", width=2)

        for event in self.events:
            self.Frame_for_scroll.create_rectangle(((float(event)*self.fr_rate)-self.debut) / self.video_length * largscroll + self.decalage - 2,5,
                                  ((float(event)*self.fr_rate)-self.debut) / self.video_length * largscroll + self.decalage + 2,
                                  15, fill="#7638c7", outline="white", width=0.5)

    def afficher_frame(self,event):
        '''
        Draw a little rectangle and show text under the mouse cursor to indicates which of the frame would be selected if the user click.
        '''
        width=self.Frame_for_scroll.winfo_width()
        largscroll = width - 60
        if event.x>self.decalage and event.x<largscroll+self.decalage and event.y>0 and event.y<20:
            self.refresh()

    def activate_position(self,event):
        '''
        When timeline is clicked
        Change the current frame displayed on the Video Reader.
        '''
        width=self.Frame_for_scroll.winfo_width()
        largscroll = width - 60
        if event.x>self.decalage and event.x<largscroll+self.decalage and event.y>0 and event.y<20:
            self.active_pos=int(self.debut + round((event.x-self.decalage) * self.video_length / largscroll))
            self.refresh()
            self.Top.update_image(self.active_pos)

    def move_position(self,event):
        '''
        When the user B1-Motion on the timeline.
        Change the current frame displayed on the Video Reader.
        '''
        width=self.Frame_for_scroll.winfo_width()
        largscroll = width - 60
        if event.x>self.decalage and event.x<largscroll+self.decalage:
            self.active_pos=int(self.debut + round((event.x-self.decalage) * self.video_length / largscroll))
            self.refresh()
            self.Top.update_image(self.active_pos)