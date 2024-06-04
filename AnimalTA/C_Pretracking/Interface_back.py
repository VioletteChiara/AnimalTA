from tkinter import *
import os
import cv2
import PIL.Image, PIL.ImageTk
from AnimalTA.A_General_tools import Video_loader as VL, UserMessages, User_help, Color_settings
import numpy as np
import pickle

class Background(Frame):
    """This frame will appear when the user is not satisfied with the automatic background and wants to change it.
    It basically allow the user to select a color in the fram eand then to paint with this color.
    """
    def __init__(self, parent, boss, main_frame, Video_file, portion=False, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.config(**Color_settings.My_colors.Frame_Base)
        self.parent=parent
        self.main_frame=main_frame
        self.boss=boss
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.portion=portion
        self.Tool_circle=BooleanVar()
        self.Tool_circle.set(True)
        self.mouse_pos=[0,0]

        if self.portion:#If you do a temporary background for a correction of a part of the video
            Grid.columnconfigure(self.parent, 0, weight=1)
            Grid.rowconfigure(self.parent, 0, weight=1)
            self.parent.geometry("1200x750")

        # Messages importation
        self.Language = StringVar()
        f = open(UserMessages.resource_path(os.path.join("AnimalTA","Files","Language")), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        self.Vid = Video_file
        if len(self.Vid.Back[1].shape)==2:
            self.background = cv2.cvtColor(self.Vid.Back[1].copy(), cv2.COLOR_GRAY2RGB)#We import the existing background
        else:
            self.background=self.Vid.Back[1].copy()

        self.saved_drawn=self.background.copy()

        self.zoom_sq=[0,0,self.Vid.shape[1],self.Vid.shape[0]]

        #Creation of the canvas image
        self.canvas_img = Canvas(self, width=10, height=10, bd=0, **Color_settings.My_colors.Frame_Base)
        self.canvas_img.update()
        self.canvas_img.grid(row=0,column=0, sticky="nsew")
        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)

        self.Size = self.Vid.shape
        self.final_width = self.canvas_img.winfo_width()
        self.ratio = self.Size[1] / self.final_width
        self.zoom_sq = [0, 0, self.Vid.shape[1], self.Vid.shape[0]]  # If not, we show the cropped frames
        self.ZinSQ = [-1, ["NA", "NA"]]  # used to zoom in a particular area

        self.canvas_img.bind("<Configure>", self.afficher)

        #Help user and parameters
        self.HW= User_help.Help_win(self.parent, default_message=self.Messages["Back2"], width=250,
                                    shortcuts={self.Messages["Short_left_click"]:self.Messages["Short_left_click_En"],
                                               self.Messages["Short_right_click"]: self.Messages["Short_right_click_Ba"],
                                               self.Messages["Short_Mousewheel"]: self.Messages[ "Short_Mousewheel_T"],
                                               self.Messages["Short_Ctrl_click"]:self.Messages["Short_Ctrl_click_G"],
                                               self.Messages["Short_Ctrl_Rclick"]: self.Messages["Short_Ctrl_Rclick_G"],
                                               self.Messages["Short_Ctrl_click_drag"]: self.Messages[ "Short_Ctrl_click_drag_G"]})

        self.HW.grid(row=0, column=1,sticky="nsew")

        self.canvas_user = Canvas(self.parent, width=10, height=10, bd=0, highlightthickness=0, **Color_settings.My_colors.Frame_Base)
        self.canvas_user.grid(row=1,column=1,sticky="ns")

        self.Label_color=Label(self.canvas_user, justify=RIGHT, text=self.Messages["Back3"], **Color_settings.My_colors.Label_Base)
        self.Label_color.grid(row=0,column=0,sticky="e")

        self.Color=(255,0,0)
        self.canvas_color=Canvas(self.canvas_user, width=10, height=10, bd=0, highlightthickness=1, background="red", relief='ridge')
        self.canvas_color.grid(row=0,column=1, sticky="nswe")


        RB_tool_shape_square = Radiobutton(self.canvas_user, text="\u25EF", variable=self.Tool_circle, value=True, **Color_settings.My_colors.Radiobutton_Base).grid(row=1,column=0)
        RB_tool_shape_circle=Radiobutton(self.canvas_user, text="\u2B1C", variable=self.Tool_circle, value=False, **Color_settings.My_colors.Radiobutton_Base).grid(row=1,column=1)

        self.validate_button=Button(self.canvas_user,text=self.Messages["Validate"], command=self.validate, **Color_settings.My_colors.Button_Base)
        self.validate_button.config(background=Color_settings.My_colors.list_colors["Validate"],fg=Color_settings.My_colors.list_colors["Fg_Validate"])
        self.validate_button.grid(row=2,column=0,columnspan=2,sticky="nsew")

        self.B_1Auto=Button(self.canvas_user,text=self.Messages["Back4"], command=self.auto_back, **Color_settings.My_colors.Button_Base)
        self.B_1Auto.config(background=Color_settings.My_colors.list_colors["Cancel"],fg=Color_settings.My_colors.list_colors["Fg_Cancel"])
        self.B_1Auto.grid(row=3,column=0,columnspan=2,sticky="nsew")


        self.B_1frame=Button(self.canvas_user,text=self.Messages["Back5"], command=self.change_for_1, **Color_settings.My_colors.Button_Base)
        self.B_1frame.config(background=Color_settings.My_colors.list_colors["Danger"], fg=Color_settings.My_colors.list_colors["Fg_Danger"])
        self.B_1frame.grid(row=4,column=0,columnspan=2,sticky="nsew")

        if self.portion:
            self.HW.grid_columnconfigure(0,minsize=250)

        self.zooming=False
        self.zoom_strength=1.25
        self.canvas_img.bind("<Button-1>",self.point)
        self.canvas_img.bind("<Control-B1-Motion>", self.Sq_Zoom_mov)
        self.canvas_img.bind("<B1-ButtonRelease>", lambda x: self.Zoom(event=x,Zin=True))
        self.canvas_img.bind("<Control-B3-ButtonRelease>", lambda x: self.Zoom(event=x,Zin=False))
        self.canvas_img.bind("<Control-B1-Motion>", self.Sq_Zoom_mov)
        self.bind_all("<Control-z>", self.remove_last)
        self.canvas_img.bind("<Button-3>", self.change_color)
        self.canvas_img.bind("<B1-Motion>", self.paint)
        self.canvas_img.bind("<MouseWheel>", self.On_mousewheel)
        self.canvas_img.bind("<Motion>", self.Show_tool)


        self.liste_paints=[]
        self.painting=False
        self.tool_view=self.canvas_img.create_oval((0,0,0,0))
        self.vide=[]

        self.Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
        with open(self.Param_file, 'rb') as fp:
            Params = pickle.load(fp)
        self.tool_size=Params["Back_tool"]

        self.canvas_img.update()



        self.afficher()

    def auto_back(self):
        #This function remove the previous background a redo a new one with the automatic process
        self.Vid.make_back()
        self.background=self.Vid.Back[1]

        if len(self.background.shape)==2:
            self.background = cv2.cvtColor(self.background.copy(), cv2.COLOR_GRAY2RGB)#We import the existing background


        self.liste_paints=[]
        self.afficher()

    def change_for_1(self):
        #This function remove the previous background and take the first frame of the video instead
        self.liste_paints=[]
        Which_part=0
        if self.Vid.Cropped[0]:
            if len(self.Vid.Fusion) > 1:  # Si on a plus d'une video
                Which_part = [index for index, Fu_inf in enumerate(self.Vid.Fusion) if Fu_inf[0] <= self.Vid.Cropped[1][0]][-1]
        self.capture = VL.Video_Loader(self.Vid, self.Vid.Fusion[Which_part][1])
        self.Represent = self.capture[self.Vid.Cropped[1][0]-self.Vid.Fusion[Which_part][0]]

        if len(self.Represent.shape) == 2:
            self.background = cv2.cvtColor(self.Represent.copy(),
                                           cv2.COLOR_GRAY2RGB)  # We import the existing background

        self.afficher()

    def Leave_zoom(self, event):
        #Stop sooming
        self.zooming = False
        if self.painting:
            self.painting=False


    def Sq_Zoom_beg(self, event):
        event_t_x = int( self.ratio * (event.x - (self.canvas_img.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
        event_t_y = int( self.ratio * (event.y - (self.canvas_img.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]
        self.ZinSQ=[0,[event_t_x,event_t_y],[event.x,event.y]]
        self.canvas_img.delete("Rect")

    def Sq_Zoom_mov(self,event):
        self.canvas_img.delete("Rect")
        event_t_x = int( self.ratio * (event.x - (self.canvas_img.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
        event_t_y = int( self.ratio * (event.y - (self.canvas_img.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]
        zoom_sq = [min(self.ZinSQ[1][0], event_t_x), min(self.ZinSQ[1][1], event_t_y), max(self.ZinSQ[1][0], event_t_x),max(self.ZinSQ[1][1], event_t_y)]
        if (zoom_sq[2] - zoom_sq[0]) > 50 and (zoom_sq[3] - zoom_sq[1])>50 and event_t_x>=0 and event_t_x<=self.Size[1] and event_t_y>=0 and event_t_y<=self.Size[0] and self.ZinSQ[1][0]>=0 and self.ZinSQ[1][0]<=self.Size[1] and self.ZinSQ[1][1]>=0 and self.ZinSQ[1][1]<=self.Size[0]:
            self.canvas_img.create_rectangle(self.ZinSQ[2][0], self.ZinSQ[2][1], event.x, event.y, outline="white", tags="Rect")
        else:
            self.canvas_img.create_rectangle(self.ZinSQ[2][0], self.ZinSQ[2][1], event.x, event.y, outline="red", tags="Rect")
        self.canvas_img.create_rectangle(self.ZinSQ[2][0],self.ZinSQ[2][1],event.x,event.y, dash=(3,3), outline="black", tags="Rect")

        if self.ZinSQ[0]>=0:
            self.ZinSQ[0]+=1


    def Zoom(self, event, Zin=True):
        '''When the user hold <Ctrl> and click on the frame, zoom on the image.
        If <Ctrl> and right click, zoom out'''
        self.painting=False
        if not bool(event.state & 0x1) and bool(event.state & 0x4):
            self.new_zoom_sq = [0, 0, self.Size[1], self.Size[0]]
            event.x = int( self.ratio * (event.x - (self.canvas_img.winfo_width()-self.shape[1])/2)) + self.zoom_sq[0]
            event.y = int( self.ratio * (event.y - (self.canvas_img.winfo_height()-self.shape[0])/2)) + self.zoom_sq[1]
            PX = event.x / self.Size[1]
            PY = event.y / self.Size[0]

            if self.ZinSQ[0]<3:
                if Zin:
                    new_total_width = self.Size[1] / self.ratio * self.zoom_strength
                    new_total_height = self.Size[0] / self.ratio * self.zoom_strength
                else:
                    new_total_width = self.Size[1] / self.ratio / self.zoom_strength
                    new_total_height = self.Size[0] / self.ratio / self.zoom_strength


                if new_total_width>self.canvas_img.winfo_width():
                    missing_px=new_total_width - (self.canvas_img.winfo_width()-5)
                    ratio_old_new=self.Size[1]/new_total_width
                    self.new_zoom_sq[0] = int(PX * missing_px*ratio_old_new)
                    self.new_zoom_sq[2] = int(self.Size[1] - ((1 - PX) * missing_px*ratio_old_new))

                if new_total_height>self.canvas_img.winfo_height():
                    missing_px=new_total_height - (self.canvas_img.winfo_height()-5)
                    ratio_old_new=self.Size[0]/new_total_height
                    self.new_zoom_sq[1] = int(PY * missing_px*ratio_old_new)
                    self.new_zoom_sq[3] = int(self.Size[0] - ((1 - PY) * missing_px*ratio_old_new))

                if self.new_zoom_sq[3]-self.new_zoom_sq[1] > 50 and self.new_zoom_sq[2]-self.new_zoom_sq[0]>50:
                    self.zoom_sq = self.new_zoom_sq
                    self.update_ratio()
                    self.afficher()

            elif event.x>=0 and event.x<=self.Size[1] and event.y>=0 and event.y<=self.Size[0] and self.ZinSQ[1][0]>=0 and self.ZinSQ[1][0]<=self.Size[1] and self.ZinSQ[1][1]>=0 and self.ZinSQ[1][1]<=self.Size[0]:
                zoom_sq = [min(self.ZinSQ[1][0], event.x), min(self.ZinSQ[1][1], event.y) , max(self.ZinSQ[1][0], event.x), max(self.ZinSQ[1][1], event.y)]
                if (zoom_sq[2] - zoom_sq[0]) > 50 and (zoom_sq[3] - zoom_sq[1])>50:
                    self.zoom_sq=zoom_sq
                    self.update_ratio()
                    self.afficher()
                self.ZinSQ = [-1, ["NA", "NA"]]

            self.zooming = False
            if self.painting:
                self.painting = False
            self.canvas_img.delete("Rect")


    def update_ratio(self, *args):
        '''Calculate the ratio between the original size of the video and the displayed image'''
        self.ratio=max((self.zoom_sq[2]-self.zoom_sq[0])/self.canvas_img.winfo_width(),(self.zoom_sq[3]-self.zoom_sq[1])/self.canvas_img.winfo_height())


    def Show_tool(self, event, corr=False, zoom=[]):
        if not corr:
            event.x = int(self.ratio * (event.x - (self.canvas_img.winfo_width()-self.shape[1])/2) + self.zoom_sq[0])
            event.y = int(self.ratio * (event.y - (self.canvas_img.winfo_height()-self.shape[0])/2) + self.zoom_sq[1])
        self.mouse_pos=(event.x,event.y)
        self.afficher()

    def point(self, event):
        #When the image is clicked, we begin to paint over it

        if not bool(event.state & 0x1) and bool(event.state & 0x4):
            self.Sq_Zoom_beg(event)
        else:
            event.x = int(self.ratio * (event.x - (self.canvas_img.winfo_width() - self.shape[1]) / 2)) + self.zoom_sq[ 0]
            event.y = int(self.ratio * (event.y - (self.canvas_img.winfo_height() - self.shape[0]) / 2)) + self.zoom_sq[ 1]

            if self.painting == False:# If we were not painting before that, we create a black filled binary image
                self.vide = np.zeros([self.background.shape[0],self.background.shape[1],1], np.uint8)

            if not self.zooming:
                #When painting, we save the positions where the mouse went.
                if self.Tool_circle.get():
                    cv2.circle(self.vide,(event.x, event.y),self.tool_size, (255, 255, 255), -1)
                else:
                    cv2.rectangle(self.vide,
                               (event.x-self.tool_size, event.y-self.tool_size),
                               (event.x+self.tool_size, event.y+self.tool_size), (255, 255, 255), -1)

                cnts, _ = cv2.findContours(self.vide, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

                if self.painting:
                    #If we were already painting, we remove the last save (i.e. it is the same trait as before)
                    self.liste_paints.pop()

                self.liste_paints.append([cnts, self.Color])

                #We show the result
                self.Show_tool(event, corr=True)
                self.painting = True
                self.last_paint=[event.x,event.y]

    def paint(self, event):
        event.x = int(self.ratio * (event.x - (self.canvas_img.winfo_width() - self.shape[1]) / 2)) + self.zoom_sq[0]
        event.y = int(self.ratio * (event.y - (self.canvas_img.winfo_height() - self.shape[0]) / 2)) + self.zoom_sq[1]
        #Similar than above bur for moving cursor
        if self.painting==False:
            self.vide = np.zeros(self.background.shape, np.uint8)

        if not self.zooming:
            #When the cursor is moving, we draw line instead of circles to avoid gaps in the drawing if the user is moving the mouse fast
            if self.Tool_circle.get():
                cv2.line(self.vide,
                         (event.x, event.y),
                         self.last_paint, (255, 255, 255), self.tool_size * 2)
            else:
                pts = np.array([(int(event.x  - self.tool_size),
                                 int(event.y  - self.tool_size)), (
                                    int(event.x - self.tool_size),
                                    int(event.y + self.tool_size)), (
                                    int(self.last_paint[0] - self.tool_size),
                                    int(self.last_paint[1] + self.tool_size)), (
                                    int(self.last_paint[0] - self.tool_size),
                                    int(self.last_paint[1] - self.tool_size))], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.fillPoly(self.vide, [pts], (255, 255, 255))

                pts = np.array([(int(event.x + self.tool_size),
                                 int(event.y - self.tool_size)), (
                                    int(event.x + self.tool_size),
                                    int(event.y + self.tool_size)), (
                                    int(self.last_paint[0] + self.tool_size),
                                    int(self.last_paint[1] + self.tool_size)), (
                                    int(self.last_paint[0] + self.tool_size),
                                    int(self.last_paint[1] - self.tool_size))], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.fillPoly(self.vide, [pts], (255, 255, 255))

                pts = np.array([(int(event.x - self.tool_size),
                                 int(event.y + self.tool_size)), (
                                    int(event.x + self.tool_size),
                                    int(event.y + self.tool_size)), (
                                    int(self.last_paint[0] + self.tool_size),
                                    int(self.last_paint[1] + self.tool_size)), (
                                    int(self.last_paint[0] - self.tool_size),
                                    int(self.last_paint[1] + self.tool_size))], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.fillPoly(self.vide, [pts], (255, 255, 255))

                pts = np.array([(int(event.x - self.tool_size),
                                 int(event.y - self.tool_size)), (
                                    int(event.x + self.tool_size),
                                    int(event.y - self.tool_size)), (
                                    int(self.last_paint[0] + self.tool_size),
                                    int(self.last_paint[1] - self.tool_size)), (
                                    int(self.last_paint[0] - self.tool_size),
                                    int(self.last_paint[1] - self.tool_size))], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.fillPoly(self.vide, [pts], (255, 255, 255))

            cnts, _ = cv2.findContours(self.vide, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

            if self.painting:
                self.liste_paints.pop()

            self.liste_paints.append([cnts, self.Color])
            self.afficher()
            self.Show_tool(event, corr=True)
            self.last_paint = [event.x, event.y]
            self.painting=True

    def change_color(self, event):
        if not bool(event.state & 0x1) and not bool(event.state & 0x4):
            #Get the color of the pixel under the mouse and use it for painting
            event.x = int(self.ratio * (event.x - (self.canvas_img.winfo_width() - self.shape[1]) / 2)) + self.zoom_sq[0]
            event.y = int(self.ratio * (event.y - (self.canvas_img.winfo_height() - self.shape[0]) / 2)) + self.zoom_sq[1]

            self.Color=self.saved_drawn[event.y, event.x, :]

            self.afficher()
            mycolor = '#%02x%02x%02x' % (self.Color[0],self.Color[1],self.Color[2])
            self.canvas_color.config(background=mycolor)
            self.Show_tool(event, corr=True)


    def On_mousewheel(self, event):
        #Change the size of the tool
        if event.delta>0 or (self.tool_size>1 and event.delta<0):
            self.tool_size = int(self.tool_size  + (event.delta / 120))
        self.afficher()
        self.Show_tool(event)


    def afficher(self, *arg):
        #Change the displayed image
        self.update_ratio()
        self.final_width=int(self.Size[1]/self.ratio)

        empty_back=np.copy(self.background)
        self.shape = empty_back.shape
        if not self.Size==empty_back.shape:
            self.Size = empty_back.shape
            self.zoom_sq = [0, 0, self.Size[1], self.Size[0]]  # If not, we show the cropped frames

        if len(self.liste_paints)>0:
            for paint in self.liste_paints:
                cv2.drawContours(empty_back,paint[0],-1,(int(paint[1][0]),int(paint[1][1]),int(paint[1][2])),-1)

        #Draw a circle around the mouse cursor of the size and shape of the painting tool
        if self.Tool_circle.get():
            cv2.circle(empty_back, self.mouse_pos, self.tool_size, (0, 0, 0), max(1,int(2*self.ratio)))
        else:
            cv2.rectangle(empty_back, (int(self.mouse_pos[0]-self.tool_size),int(self.mouse_pos[1]-self.tool_size)), (int(self.mouse_pos[0]+self.tool_size),int(self.mouse_pos[1]+self.tool_size)), (0, 0, 0), max(1,int(2*self.ratio)))


        self.saved_drawn = empty_back.copy()

        self.image_to_show=empty_back[self.zoom_sq[1]:self.zoom_sq[3],self.zoom_sq[0]:self.zoom_sq[2]]

        width=int((self.zoom_sq[2]-self.zoom_sq[0])/self.ratio)
        height=int((self.zoom_sq[3]-self.zoom_sq[1])/self.ratio)

        TMP_image_to_show2 = cv2.resize(self.image_to_show,(width, height))
        self.shape= TMP_image_to_show2.shape

        self.image_to_show3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(TMP_image_to_show2))
        self.can_import = self.canvas_img.create_image((self.canvas_img.winfo_width() - self.shape[1]) / 2,
                                                         (self.canvas_img.winfo_height() - self.shape[0]) / 2,
                                                         image=self.image_to_show3, anchor=NW)

        self.canvas_img.config(height=self.shape[1], width=self.shape[0])
        self.canvas_img.itemconfig(self.can_import, image=self.image_to_show3)
        self.update_idletasks()

    def remove_last(self, *arg):
        #To remove the last painting (Ctrl-Z)
        if len(self.liste_paints)>0:
            self.liste_paints.pop()
            self.afficher()

    def validate(self):
        #Validate the changes and save the new background
        if len(self.liste_paints)>0:
            for paint in self.liste_paints:
                cv2.drawContours(self.background,paint[0],-1,(int(paint[1][0]),int(paint[1][1]),int(paint[1][2])),-1)

        if len(self.background.shape)==2:
            self.Vid.Back[1] = cv2.cvtColor(self.background, cv2.COLOR_GRAY2RGB)  # We import the existing background
        else:
            self.Vid.Back[1] = self.background

        if self.portion:
            self.boss.PortionWin.grab_set()

        self.End_of_window()

    def End_of_window(self):
        #End the window properly
        self.unbind_all("<Button-1>")
        self.grab_release()
        self.HW.grid_forget()
        self.HW.destroy()
        self.canvas_user.grid_forget()
        self.canvas_user.destroy()
        if not self.portion:
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