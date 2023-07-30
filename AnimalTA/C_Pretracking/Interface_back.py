from tkinter import *
import os
import cv2
import PIL.Image, PIL.ImageTk
from AnimalTA.A_General_tools import Video_loader as VL, UserMessages, User_help
import numpy as np
import pickle

class Background(Frame):
    """This frame will appear when the user is not satisfied with the automatic background and wants to change it.
    It basically allow the user to select a color in the fram eand then to paint with this color.
    """
    def __init__(self, parent, boss, main_frame, Video_file, portion=False, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.main_frame=main_frame
        self.boss=boss
        self.grid(row=0,column=0,rowspan=2,sticky="nsew")
        self.portion=portion
        self.Tool_circle=BooleanVar()
        self.Tool_circle.set(True)

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
        self.background=self.Vid.Back[1] #We import the existing background
        self.saved_drawn=self.background.copy()
        self.zoom_sq=[0,0,self.Vid.shape[1],self.Vid.shape[0]]

        #Creation of the canvas image
        self.canvas_img = Canvas(self, width=10, height=10, bd=0, highlightthickness=0, relief='ridge')
        self.canvas_img.grid(row=0,column=0, sticky="nsew")
        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)
        self.ratio=1
        self.final_width=750
        self.Size = self.Vid.shape
        self.canvas_img.bind("<Configure>", self.afficher)

        #Help user and parameters
        self.HW= User_help.Help_win(self.parent, default_message=self.Messages["Back2"], width=250)
        self.HW.grid(row=0, column=1,sticky="nsew")

        self.canvas_user = Canvas(self.parent, width=10, height=10, bd=0, highlightthickness=0, relief='ridge')
        self.canvas_user.grid(row=1,column=1,sticky="ns")

        self.Label_color=Label(self.canvas_user, justify=RIGHT, text=self.Messages["Back3"])
        self.Label_color.grid(row=0,column=0,sticky="e")
        self.canvas_color=Canvas(self.canvas_user, width=10, height=10, bd=0, highlightthickness=1, highlightbackground="black", relief='ridge')
        self.canvas_color.grid(row=0,column=1, sticky="nswe")


        RB_tool_shape_square = Radiobutton(self.canvas_user, text="\u25EF", variable=self.Tool_circle, value=True).grid(row=1,column=0)
        RB_tool_shape_circle=Radiobutton(self.canvas_user, text="\u2B1C", variable=self.Tool_circle, value=False).grid(row=1,column=1)

        self.validate_button=Button(self.canvas_user,text=self.Messages["Validate"], background="#6AED35", command=self.validate)
        self.validate_button.grid(row=2,column=0,columnspan=2,sticky="nsew")

        self.B_1Auto=Button(self.canvas_user,text=self.Messages["Back4"], background="orange", command=self.auto_back)
        self.B_1Auto.grid(row=3,column=0,columnspan=2,sticky="nsew")


        self.B_1frame=Button(self.canvas_user,text=self.Messages["Back5"], background="red", command=self.change_for_1)
        self.B_1frame.grid(row=4,column=0,columnspan=2,sticky="nsew")

        if self.portion:
            self.HW.grid_columnconfigure(0,minsize=250)

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

        self.Param_file = UserMessages.resource_path(os.path.join("AnimalTA", "Files", "Settings"))
        with open(self.Param_file, 'rb') as fp:
            Params = pickle.load(fp)
        self.tool_size=Params["Back_tool"]
        self.Color=0

        self.canvas_img.update()
        self.final_width = self.canvas_img.winfo_width()
        self.ratio = self.Size[1] / self.final_width

        self.afficher()


    def auto_back(self):
        #This function remove the previous background a redo a new one with the automatic process
        self.Vid.make_back()
        self.background=self.Vid.Back[1]
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

        self.background=cv2.cvtColor(self.Represent,cv2.COLOR_BGR2GRAY)
        self.afficher()

    def Leave_zoom(self, event):
        #Stop sooming
        self.zooming = False
        if self.painting:
            self.painting=False

    def Zoom_in(self, event):
        #Zoom in the frame
        self.new_zoom_sq=[0,0,0,0]
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

            # Show the result
            self.afficher()
            self.Show_tool(event,zoom=(event.x,event.y))

    def Zoom_out(self, event):
        #Zoom out the frame
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
        #Show the result
        self.afficher()
        self.Show_tool(event)


    def Show_tool(self, event, zoom=[]):
        #Draw a circle around the mouse cursor of the size and shape of the painting tool
        if not len(zoom)>0:
            self.canvas_img.delete(self.tool_view)
            if self.Tool_circle.get():
                self.tool_view=self.canvas_img.create_oval((event.x - self.tool_size/self.ratio,
                                            event.y - self.tool_size/self.ratio,
                                            event.x + self.tool_size/self.ratio,
                                            event.y  + self.tool_size/self.ratio))
            else:
                self.tool_view=self.canvas_img.create_rectangle((event.x - self.tool_size/self.ratio,
                                            event.y - self.tool_size/self.ratio,
                                            event.x + self.tool_size/self.ratio,
                                            event.y  + self.tool_size/self.ratio))

    def point(self, event):
        #When the image is clicked, we begin to paint over it
        if self.painting == False:# If we were not painting before that, we create a black filled binary image
            self.vide = np.zeros(self.background.shape, np.uint8)

        if not self.zooming:
            #When painting, we save the positions where the mouse went.
            if self.Tool_circle.get():
                cv2.circle(self.vide,(int(event.x * self.ratio + self.zoom_sq[0]), int(event.y * self.ratio + self.zoom_sq[1])),self.tool_size, (255, 255, 255), -1)
            else:
                cv2.rectangle(self.vide,
                           (int(event.x * self.ratio + self.zoom_sq[0]-self.tool_size), int(event.y * self.ratio + self.zoom_sq[1]-self.tool_size)),
                           (int(event.x * self.ratio + self.zoom_sq[0]+self.tool_size), int(event.y * self.ratio + self.zoom_sq[1]+self.tool_size)), (255, 255, 255), -1)

            cnts, _ = cv2.findContours(self.vide, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

            if self.painting:
                #If we were already painting, we remove the last save (i.e. it is the same trait as before)
                self.liste_paints.pop()

            self.liste_paints.append([cnts, self.Color])

            #We show the result
            self.afficher()
            self.Show_tool(event)
            self.painting = True
            self.last_paint=[int(event.x * self.ratio + self.zoom_sq[0]),int(event.y * self.ratio + self.zoom_sq[1])]

    def paint(self, event):
        #Similar than above bur for moving cursor
        if self.painting==False:
            self.vide = np.zeros(self.background.shape, np.uint8)

        if not self.zooming:
            #When the cursor is moving, we draw line instead of circles to avoid gaps in the drawing if the user is moving the mouse fast
            if self.Tool_circle.get():
                cv2.line(self.vide,
                         (int(event.x * self.ratio + self.zoom_sq[0]), int(event.y * self.ratio + self.zoom_sq[1])),
                         self.last_paint, (255, 255, 255), self.tool_size * 2)
            else:
                pts=np.array([(int(event.x * self.ratio + self.zoom_sq[0] - self.tool_size),
                                           int(event.y * self.ratio + self.zoom_sq[1] - self.tool_size)), (
                                          int(event.x * self.ratio + self.zoom_sq[0] - self.tool_size),
                                          int(event.y * self.ratio + self.zoom_sq[1] + self.tool_size)), (
                                          int(self.last_paint[0] - self.tool_size),
                                          int(self.last_paint[1] + self.tool_size)), (
                                          int(self.last_paint[0] - self.tool_size),
                                          int(self.last_paint[1] - self.tool_size))],np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.fillPoly(self.vide, [pts], (255, 255, 255))


                pts=np.array([(int(event.x * self.ratio + self.zoom_sq[0] + self.tool_size),
                                           int(event.y * self.ratio + self.zoom_sq[1] - self.tool_size)), (
                                          int(event.x * self.ratio + self.zoom_sq[0] + self.tool_size),
                                          int(event.y * self.ratio + self.zoom_sq[1] + self.tool_size)), (
                                          int(self.last_paint[0] + self.tool_size),
                                          int(self.last_paint[1] + self.tool_size)), (
                                          int(self.last_paint[0] + self.tool_size),
                                          int(self.last_paint[1] - self.tool_size))],np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.fillPoly(self.vide, [pts], (255, 255, 255))


                pts=np.array([(int(event.x * self.ratio + self.zoom_sq[0] - self.tool_size),
                                           int(event.y * self.ratio + self.zoom_sq[1] + self.tool_size)), (
                                          int(event.x * self.ratio + self.zoom_sq[0] + self.tool_size),
                                          int(event.y * self.ratio + self.zoom_sq[1] + self.tool_size)), (
                                          int(self.last_paint[0] + self.tool_size),
                                          int(self.last_paint[1] + self.tool_size)), (
                                          int(self.last_paint[0] - self.tool_size),
                                          int(self.last_paint[1] + self.tool_size))],np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.fillPoly(self.vide, [pts], (255, 255, 255))

                pts=np.array([(int(event.x * self.ratio + self.zoom_sq[0] - self.tool_size),
                                           int(event.y * self.ratio + self.zoom_sq[1] - self.tool_size)), (
                                          int(event.x * self.ratio + self.zoom_sq[0] + self.tool_size),
                                          int(event.y * self.ratio + self.zoom_sq[1] - self.tool_size)), (
                                          int(self.last_paint[0] + self.tool_size),
                                          int(self.last_paint[1] - self.tool_size)), (
                                          int(self.last_paint[0] - self.tool_size),
                                          int(self.last_paint[1] - self.tool_size))],np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.fillPoly(self.vide, [pts], (255, 255, 255))



            cnts, _ = cv2.findContours(self.vide, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

            if self.painting:
                self.liste_paints.pop()

            self.liste_paints.append([cnts, self.Color])
            self.afficher()
            self.Show_tool(event)
            self.last_paint = [int(event.x * self.ratio + self.zoom_sq[0]), int(event.y * self.ratio + self.zoom_sq[1])]
            self.painting=True

    def change_color(self, event):
        #Get the color of the pixel under the mouse and use it for painting
        self.Color=int(self.saved_drawn[int(event.y*self.ratio+self.zoom_sq[1]), int(event.x*self.ratio+self.zoom_sq[0])])
        self.afficher()
        mycolor = '#%02x%02x%02x' % (self.Color,self.Color,self.Color)
        self.canvas_color.config(background=mycolor)
        self.Show_tool(event)


    def On_mousewheel(self, event):
        #Change the size of the tool
        if event.delta>0 or (self.tool_size>1 and event.delta<0):
            self.tool_size = int(self.tool_size  + (event.delta / 120))
        self.afficher()
        self.Show_tool(event)


    def afficher(self, *arg):
        #Change the displayed image
        best_ratio = max(self.Size[1] / (self.canvas_img.winfo_width()),self.Size[0] / (self.canvas_img.winfo_height()))
        prev_final_width=self.final_width
        self.final_width=int(self.Size[1]/best_ratio)
        self.ratio=self.ratio*(prev_final_width/self.final_width)

        empty_back=np.copy(self.background)
        if len(self.liste_paints)>0:
            for paint in self.liste_paints:
                cv2.drawContours(empty_back,paint[0],-1,paint[1],-1)
        self.image_to_show=empty_back[self.zoom_sq[1]:self.zoom_sq[3],self.zoom_sq[0]:self.zoom_sq[2]]
        self.saved_drawn=self.image_to_show.copy()

        self.image_to_show=cv2.resize(self.image_to_show,(self.final_width,int(self.final_width*(self.Size[0]/self.Size[1]))))
        self.image_to_show = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.image_to_show))
        self.canvas_img.create_image(0, 0, image=self.image_to_show, anchor=NW)
        self.canvas_img.config(width=self.final_width, height=int(self.final_width*(self.Size[0]/self.Size[1])))

    def remove_last(self, *arg):
        #To remove the last painting (Ctrl-Z)
        if len(self.liste_paints)>0:
            self.liste_paints.pop()
            self.afficher()

    def validate(self):
        #Validate the changes and save the new background
        if len(self.liste_paints)>0:
            for paint in self.liste_paints:
                cv2.drawContours(self.background,paint[0],-1,paint[1],-1)
        self.Vid.Back[1]=self.background
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