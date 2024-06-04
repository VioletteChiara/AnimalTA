from tkinter import *
from tkinter import ttk
import cv2
import numpy as np
import scipy.signal
from AnimalTA.A_General_tools import UserMessages, Class_Lecteur, Class_change_vid_menu, Class_loading_Frame, Class_stabilise
import math
import os

class Light_changes(Frame):
    def __init__(self, parent, boss,main_frame, Vid, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.main_frame=main_frame
        self.boss=boss
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.Vid = Vid
        self.multiple_width=2.5
        self.limits=[]
        self.selected_ind=0
        self.N_lim=False

        Grid.columnconfigure(self.parent, 0, weight=1)  ########NEW
        Grid.rowconfigure(self.parent, 0, weight=1)  ########NEW

        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()

        self.Messages = UserMessages.Mess[self.Language.get()]

        self.pts=[[200,200],[300,300]]

        self.fr_rate=self.Vid.Frame_rate[1]
        self.one_every=int(round(round(self.Vid.Frame_rate[0],2)/self.Vid.Frame_rate[1]))

        # Name of the vieo and optionmenu to jump from one video to another
        self.choice_menu = Class_change_vid_menu.Change_Vid_Menu(self, self.main_frame, self.Vid, "stab")
        self.choice_menu.grid(row=0, column=0)

        Grid.columnconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 0, weight=1)  ########NEW
        Grid.rowconfigure(self, 1, weight=100)  ########NEW
        Grid.rowconfigure(self, 2, weight=1)  ########NEW
        # Visualisation de la video et barre de temps

        self.Vid_Lecteur = Class_Lecteur.Lecteur(self, self.Vid)
        self.Vid_Lecteur.grid(row=1, column=0, sticky="nsew")
        self.Scrollbar=self.Vid_Lecteur.Scrollbar

        self.Vid_Lecteur.canvas_video.update()
        self.Vid_Lecteur.update_image(self.Vid_Lecteur.to_sub)
        self.Vid_Lecteur.bindings()


        self.buttons=Frame(self.parent)
        self.buttons.grid(row=0,column=1)
        Light_Button=Button(self.buttons, text="run measures", command=self.get_light, width=75, background="#6AED35")
        Light_Button.grid()

        New_limits=Button(self.buttons, text="new limits", command=self.new_limits, width=75)
        New_limits.grid()

        Reset_limits=Button(self.buttons, text="reset limits", command=self.reset_limits, width=75)
        Reset_limits.grid()

        Fr_results=Frame(self.buttons)
        Fr_results.grid(sticky="nsew")
        Grid.columnconfigure(Fr_results, 0, weight=1)  ########NEW
        Grid.columnconfigure(Fr_results, 1, weight=1)  ########NEW

        self.PPS=StringVar()
        self.PPS.set("NA")
        first_FR=Frame(Fr_results)
        first_FR.grid(row=0, column=0, sticky="nswe")
        Label_pps=Label(first_FR, text="Heart-beat:")
        Label_pps.grid(row=0,column=0)
        Label_result=Label(first_FR, textvariable=self.PPS)
        Label_result.grid(row=0,column=1)
        Label_units1=Label(first_FR, text="peaks/sec")
        Label_units1.grid(row=0,column=2)

        seco_FR=Frame(Fr_results)
        seco_FR.grid(row=0, column=1, sticky="nsew")
        self.duree_mes=StringVar()
        self.duree_mes.set("NA")
        Label_pps=Label(seco_FR, text="Measurement duration:")
        Label_pps.grid(row=0,column=0)
        Label_result=Label(seco_FR, textvariable=self.duree_mes)
        Label_result.grid(row=0,column=1)
        Label_units2=Label(seco_FR, text="sec")
        Label_units2.grid(row=0,column=2)

        self.Frame_for_Graph=Frame(self.parent)
        self.Frame_for_Graph.grid(row=2, column=0, columnspan=1, stick="nsew")
        Grid.columnconfigure(self.Frame_for_Graph, 0, weight=1)  ########NEW
        Grid.columnconfigure(self.Frame_for_Graph, 1, weight=1)  ########NEW
        Grid.columnconfigure(self.Frame_for_Graph, 2, weight=100)  ########NEW

        Grid.rowconfigure(self.Frame_for_Graph, 0, weight=100)  ########NEW
        Grid.rowconfigure(self.Frame_for_Graph, 1, weight=1)  ########NEW
        Grid.rowconfigure(self.Frame_for_Graph, 2, weight=1)  ########NEW

        self.Ylab_can = Canvas(self.Frame_for_Graph, width=20, height=175)
        self.Ylab_can.grid(row=0,column=0, sticky="nsew")

        self.Yaxe_can = Canvas(self.Frame_for_Graph, width=50, height=300)
        self.Yaxe_can.grid(row=0,column=1, sticky="nsew")

        self.Graph=Canvas(self.Frame_for_Graph, width=300, height=200, scrollregion=(0,0,0,0))
        self.Graph.grid(row=0,column=2,sticky="nsew")

        self.Xaxe_can = Canvas(self.Frame_for_Graph, height=15)
        self.Xaxe_can.grid(row=1,column=2, sticky="nsew")
        self.Xaxe_can.create_text(210, 7, text=self.Messages["Analyses_details_graph_X"])

        hsb=ttk.Scrollbar(self.Frame_for_Graph, orient=HORIZONTAL, command=self.Graph.xview)
        hsb.grid(row=2,column=2,sticky="ew")
        self.Graph.config(xscrollcommand=hsb.set)
        self.Graph.bind("<Button-1>", self.callback)
        self.Graph.bind("<Shift-1>", self.add_pt)
        self.Graph.bind("<B1-Motion>", self.move_graph)
        self.Graph.bind("<ButtonRelease-1>", self.release_graph())


        Close_win=Button(self.buttons, text="Return to menu", command=self.End_of_window, width=75, background="red")
        Close_win.grid()


    def give_focus(self,event):###############
        if event.widget.winfo_class()!="Entry":################
            self.Vid_Lecteur.focus_set()####################

    def remove_focus(self, *arg):
        self.Vid_Lecteur.focus_set()

    def modif_image(self, img, move=False, aff=True, **kwargs):
        new_img=np.copy(img)
        self.last_empty = img

        if self.Vid.Stab[0]:
            new_img = Class_stabilise.find_best_position(Vid=self.Vid, Prem_Im=self.Vid_Lecteur.Prem_image_to_show, frame=new_img, show=False)


        self.Vid_Lecteur.update_ratio()#Ensure the "ratio" (how much the image size should be modified according to available space) is correctly calculated

        if self.Scrollbar.active_pos>self.Scrollbar.crop_end or self.Scrollbar.active_pos<self.Scrollbar.crop_beg:
            new_img = cv2.addWeighted(new_img, 1, new_img, 0, 1)

        for pt in self.pts:
            new_img=cv2.circle(new_img,(int(pt[0]),int(pt[1])),max(1,int(5*self.Vid_Lecteur.ratio)),(255,0,0),-1)
        cv2.circle(new_img,(int((self.pts[0][0]+self.pts[1][0])/2), int((self.pts[0][1]+self.pts[1][1])/2)),int(math.sqrt((self.pts[0][0]-self.pts[1][0])**2 + (self.pts[0][1]-self.pts[1][1])**2)/2),(255,0,0),max(1,int(2.5*self.Vid_Lecteur.ratio)))




        try:
            self.draw_graph(range(len(self.Lights)),self.Lights)
        except:
            pass

        if move:
            try:
                self.Graph.xview_moveto(str((self.Scrollbar.active_pos-self.multiple_width+self.Vid_Lecteur.to_sub)/self.Vid.Frame_nb[1]))
            except:
                pass

        if aff:
            self.Vid_Lecteur.afficher_img(new_img)

        return(new_img)



    def change_vid(self, vid):
        self.End_of_window()
        self.main_frame.selected_vid = self.dict_Names[vid].Video
        self.main_frame.Roi_extension()


    def End_of_window(self):
        try:
            self.Vid_Lecteur.proper_close()
        except:
            pass

        self.grab_release()

        self.buttons.grid_forget()
        self.Frame_for_Graph.grid_forget()

        self.buttons.destroy()
        self.Frame_for_Graph.destroy()

        self.unbind_all("<Button-1>")
        self.boss.update()
        self.grab_release()

        self.main_frame.return_main()

    def pressed_can(self, Pt, Shift):
        self.clicked = False
        if int(self.Scrollbar.active_pos) >= round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every) and int(
                self.Scrollbar.active_pos) <= round(self.Vid.Cropped[1][1] / self.Vid_Lecteur.one_every):
            for ind in range(len(self.pts)):
                center = self.pts[ind]
                if center[0] != "NA":
                    dist_clic = math.sqrt((int(center[0]) - Pt[0]) ** 2 + (int(center[1]) - Pt[1]) ** 2)
                    if dist_clic < max(2,(7*self.Vid_Lecteur.ratio)):
                        self.selected_ind = ind
                        self.clicked = True
                    self.modif_image(self.last_empty)

    def moved_can(self, Pt, *args):
        if self.clicked and Pt[0]>=0 and Pt[1]>=0 and Pt[0]<=self.Vid.shape[1] and Pt[1]<=self.Vid.shape[0]:
            self.pts[self.selected_ind]=[Pt[0],Pt[1]]
            self.modif_image(self.last_empty)

    def released_can(self, Pt):
        self.clicked=False


    def get_light(self):
        self.Vid_Lecteur.stop()
        self.Vid_Lecteur.unbindings()

        self.Lights=[]
        self.peaks=[]

        if self.Vid.Cropped[0]:
            start = self.Vid.Cropped[1][0]
            end = self.Vid.Cropped[1][1]
            self.Vid_Lecteur.Scrollbar.active_pos = round(self.Vid.Cropped[1][0] / self.Vid_Lecteur.one_every) - 1
        else:
            start = 0
            end = self.Vid.Frame_nb[1] - 1
            self.Vid_Lecteur.Scrollbar.active_pos = 0


        loading_bar=Class_loading_Frame.Loading(self.parent)
        loading_bar.grid(row=2, column=1)

        for frame in np.arange(int(start), int(end) + self.Vid_Lecteur.one_every, self.Vid_Lecteur.one_every):
            frame=int(frame)
            try:
                loading_bar.show_load((frame - start) / ((end + self.Vid_Lecteur.one_every) - start - 1))
                new_img = self.Vid_Lecteur.move1(aff=False)
                new_img=cv2.cvtColor(new_img,cv2.COLOR_BGR2GRAY)
                empty=np.zeros_like(new_img)
                empty=cv2.circle(empty,(int((self.pts[0][0]+self.pts[1][0])/2), int((self.pts[0][1]+self.pts[1][1])/2)),int(math.sqrt((self.pts[0][0]-self.pts[1][0])**2 + (self.pts[0][1]-self.pts[1][1])**2)/2),(255,255,255),-1)

                self.Lights.append(np.mean(new_img[np.where(empty>0)]))
            except:
                pass

        loading_bar.destroy()
        del loading_bar

        mini= min(self.Lights)-1
        maxi = max(self.Lights)+1

        self.Lights=[(maxi-mini)-(L-mini) for L in self.Lights]
        self.peaks=list(scipy.signal.find_peaks(self.Lights, distance=2, prominence=0.5)[0])
        self.draw_graph(range(len(self.Lights)),self.Lights)
        self.Vid_Lecteur.bindings()

    def draw_graph(self,Xs,Ys):
        self.last_posX=float(self.Graph.xview()[0])
        self.Graph.delete("all")
        self.Yaxe_can.delete("all")
        self.Ylab_can.delete("all")

        self.ecart=50
        #self.Graph.update()
        self.Width=len(Ys)
        self.Height = self.Graph.winfo_height()
        self.Graph.config(scrollregion=(0,0,self.Width*self.multiple_width, self.Height))
        if max(Ys) > 0:
            Ymax=max(Ys)
        else:
            Ymax=1

        self.Ratio_Ys=(self.Height-self.ecart*2)/Ymax
        Corr_Ys=[self.Ratio_Ys*val for val in Ys]

        self.Ratio_Xs = (self.Width*self.multiple_width) / max(Xs)
        Corr_Xs = [self.Ratio_Xs * val for val in Xs]

        #Axes labels
        self.Ylab_can.create_text(10,self.Height/2,text="Light",angle=90)

        #Axes values
        self.Graph.create_line(0,self.Height-self.ecart,self.Width*self.multiple_width,self.Height-self.ecart, width=2)
        for text in np.arange (0, Ymax, Ymax/6):
            self.Yaxe_can.create_text(self.ecart/2,(self.Height-(self.ecart+text*self.Ratio_Ys)),text=round(text,2))
            self.Yaxe_can.create_line(self.Yaxe_can.winfo_width()-self.multiple_width,(self.Height-(self.ecart+text*self.Ratio_Ys)),self.Yaxe_can.winfo_width()+self.multiple_width,(self.Height-(self.ecart+text*self.Ratio_Ys)))

        self.Graph.create_line(0, self.ecart, 0, self.Height-self.ecart, width=2)

        for text in np.arange(200, ((self.Vid.Cropped[1][1]-self.Vid.Cropped[1][0])/self.one_every)*self.multiple_width, 200):
            self.Graph.create_text(text,self.Height-(self.ecart/2),text=round(((int((text)/self.Ratio_Xs) + round(self.Vid.Cropped[1][0])/self.one_every)/self.Vid.Frame_rate[1]),2))
            self.Graph.create_line(text-1,self.Height-(self.ecart)+self.multiple_width,text-1,self.Height-(self.ecart))


        for section in self.limits:
            if section[0]!="NA":
                self.limits_line = self.Graph.create_line((section[0]) * self.Ratio_Xs, self.ecart, (section[0]) * self.Ratio_Xs,
                                                       self.Height - self.ecart, width=2, fill="black")

            if section[1] != "NA":
                self.limits_line2 = self.Graph.create_line((section[1]) * self.Ratio_Xs, self.ecart, (section[1]) * self.Ratio_Xs,
                                                       self.Height - self.ecart, width=2, fill="black")

                self.limits_show = self.Graph.create_line((section[0]) * self.Ratio_Xs, self.ecart, (section[1]) * self.Ratio_Xs,
                                                       self.ecart, width=2, fill="black")

                self.rect_lim=self.Graph.create_rectangle((section[0]) * self.Ratio_Xs, self.ecart, (section[1]) * self.Ratio_Xs,
                                                       self.Height - self.ecart, width=2, fill="grey")


        for point in range(len(Ys)):
            if point>0:
                self.Graph.create_line(Corr_Xs[point-1]-2, self.Height-(Corr_Ys[point-1]+self.ecart),Corr_Xs[point]-2, self.Height-(Corr_Ys[point]+self.ecart), fill="black")

        for peak in self.peaks:
            self.Graph.create_oval(int(Corr_Xs[peak]-2),self.Height-int(Corr_Ys[peak]-2+self.ecart),int(Corr_Xs[peak]+2),self.Height-int(Corr_Ys[peak]+2+self.ecart),fill="red")

        cur_pos = self.Scrollbar.active_pos - round(self.Vid.Cropped[1][0] / self.one_every)+1
        self.line_pos = self.Graph.create_line((cur_pos-2) * self.Ratio_Xs , self.ecart, (cur_pos-2) * self.Ratio_Xs  , self.Height - self.ecart, width=2, fill="blue")

        self.ready=True
        self.calculate_pps()
        self.Corr_Xs = Corr_Xs.copy()
        self.Corr_Ys = Corr_Ys.copy()

        self.Graph.xview_moveto(self.last_posX)

    def add_pt(self, event):
        x = event.widget.canvasx(event.x)
        if int(round(x/self.multiple_width)) not in self.peaks:
            self.peaks.append(int(round(x/self.multiple_width)))
            self.draw_graph(range(len(self.Lights)), self.Lights)


    def callback(self, event):
        x = event.widget.canvasx(event.x)
        y = event.widget.canvasy(event.y)
        if self.N_lim:
            if self.limits[len(self.limits)-1][0]=="NA":
                self.limits[len(self.limits)-1][0]=round(x/self.multiple_width)
            elif self.limits[len(self.limits)-1][1]=="NA":
                self.limits[len(self.limits)-1][1]=round(x/self.multiple_width)
                self.N_lim=False
                self.calculate_pps()
            self.draw_graph(range(len(self.Lights)),self.Lights)

        else:
            self.selected_lim=None
            if len(self.limits)>0 and self.limits[len(self.limits)-1][1]!="NA":
                for section in range(len(self.limits)):
                    if x>(self.limits[section][0]*self.multiple_width)-self.multiple_width and x<(self.limits[section][0]*self.multiple_width)+self.multiple_width:
                        self.selected_lim=[section,0]
                    elif  x>((self.limits[section][1])*self.multiple_width)-self.multiple_width and x<((self.limits[section][1])*self.multiple_width)+self.multiple_width:
                        self.selected_lim=[section,1]

            if self.selected_lim==None:
                to_del=[]
                for IDpeak in range(len(self.peaks)):
                    PT=[int(self.Corr_Xs[self.peaks[IDpeak]]), self.Height - int(self.Corr_Ys[self.peaks[IDpeak]] - 2 + self.ecart)]
                    dist_clic = math.sqrt((int(x) - PT[0]) ** 2 + (int(y) - PT[1]) ** 2)

                    if dist_clic<5:
                        to_del.append(IDpeak)

                if len(to_del)>0:
                    for i in sorted(to_del, reverse=True):
                        self.peaks.pop(i)
                    self.draw_graph(range(len(self.Lights)), self.Lights)

                else:
                    self.Scrollbar.active_pos = int((x) / self.Ratio_Xs) + round(self.Vid.Cropped[1][0] / self.one_every)
                    self.Scrollbar.refresh()
                    self.Vid_Lecteur.update_image(int((x) / self.Ratio_Xs) + round(self.Vid.Cropped[1][0] / self.one_every))
                    self.draw_graph(range(len(self.Lights)),self.Lights)

    def move_graph(self,event):
        x = event.widget.canvasx(event.x)
        if self.selected_lim!=None:
            self.limits[self.selected_lim[0]][self.selected_lim[1]]=round(x/self.multiple_width)
        self.draw_graph(range(len(self.Lights)),self.Lights)
        self.calculate_pps()

    def release_graph(self):
        self.selected_lim=None

    def calculate_pps(self):
        if len(self.limits) == 0 or self.limits[len(self.limits)-1][1]!="NA":
            start = self.Vid.Cropped[1][0]-self.Vid_Lecteur.to_sub
            end = self.Vid.Cropped[1][1]-self.Vid_Lecteur.to_sub

            all_pts=list(range(start,end))
            filtered_L=self.peaks.copy()

            if len(self.limits)>0:
                all_pts=[]
                filtered_L=[]
                for section in self.limits:
                    all_pts=all_pts+[L for L in list(range(start,end)) if L>=min(section) and L<max(section)]
                    filtered_L=filtered_L+[L for L in self.peaks.copy() if L>=min(section) and L<max(section)]

            self.PPS.set(round(len(filtered_L)/(len(all_pts)/self.Vid.Frame_rate[0]),3))
            self.duree_mes.set(round((len(all_pts)/self.Vid.Frame_rate[0]), 3))

    def new_limits(self):
        if len(self.limits)==0 or self.limits[len(self.limits) - 1][1] != "NA":
                self.N_lim=True
                self.limits.append(["NA","NA"])

    def reset_limits(self):
        self.limits=[]
        self.draw_graph(range(len(self.Lights)), self.Lights)
        self.calculate_pps()



"""
root = Tk()
root.geometry("+100+100")
Video_file=Class_Video.Video(File_name="D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01.avi")
interface = Cropping(parent=root, boss=None, Video_file=Video_file)
root.mainloop()

"""