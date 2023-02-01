from tkinter import *

import numpy as np

from AnimalTA.A_General_tools import Function_draw_mask, UserMessages, User_help
import cv2
import PIL


"""This script is for next update only, not available not now!"""

class Draw_ent(Frame):
    """In this Frame, the user will have the possibility to indicate the arenas in which the targets can be found. It will later work as a mask and facilitate target's identification."""
    def __init__(self, parent, Img, Entrances, Arenas, boss, scale, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.img=Img
        self.scale=scale
        self.boss=boss#Who is the class calling this one
        self.parent=parent
        self.image_to_show=self.img.copy()
        self.last_image_to_show=self.image_to_show.copy()
        self.ents=Entrances
        self.arenas=Arenas
        self.grid(row=0,column=0,sticky="nsew")
        self.binary=[]#A binary image of the user drawings
        self.tool_size=20
        self.selection=False#Whether the user is selecting a specific border or not
        self.selected_bd=[[] for _ in self.arenas]

        Grid.rowconfigure(self.parent, 0, weight=1)
        Grid.columnconfigure(self.parent, 0, weight=1)

        #Import messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        #Relative to size of the image
        self.zoom_sq=[0,0,self.img.shape[1],self.img.shape[0]]
        self.zoom_strength = 0.3

        self.canvas_img = Canvas(self, bd=0, highlightthickness=0, relief='ridge', width=1000, height=1000)
        self.canvas_img.grid(row=0, column=0, rowspan=2, sticky="nsew")

        #Zoom in/out
        self.canvas_img.bind("<Control-1>", self.Zoom_in)
        self.canvas_img.bind("<Control-3>", self.Zoom_out)
        #Paint
        self.canvas_img.bind("<B1-Motion>", self.click_n_move)
        self.canvas_img.bind("<ButtonPress-1>", self.press)
        self.canvas_img.bind("<ButtonRelease-1>", self.release)
        #Display tool and change it size
        self.canvas_img.bind("<Motion>", self.show_tool)
        self.canvas_img.bind("<MouseWheel>", self.On_mousewheel)

        Grid.rowconfigure(self, 0, weight=100)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)

        self.ratio = 1
        self.final_width = 750
        self.Size = [self.img.shape[0],self.img.shape[1]]

        self.HW = User_help.Help_win(self, default_message=self.Messages["Mask10"], width=300)
        self.HW.grid(row=0, column=1, sticky="nsew")

        User_Fr=Frame(self)
        User_Fr.grid(row=1,column=1,sticky="nsew")

        Grid.columnconfigure(User_Fr, 0, weight=1)

        delete_cnts=Button(User_Fr,text="Delete existing areas", command=self.delete)
        delete_cnts.grid(row=0, column=0, columnspan=2, sticky="nsew")

        borders_scale=Scale(User_Fr,label="Width", from_=0.05,to=int((self.Size[0]/self.scale)/2), resolution=0.01, command=self.draw_borders, orient=HORIZONTAL)
        borders_scale.grid(row=1, column=0, sticky="nsew")

        self.Choose_borders_B=Button(User_Fr,text="select borders", command=self.active_selection)
        self.Choose_borders_B.grid(row=1, column=1, sticky="nsew")

        validate=Button(User_Fr,text="Validate", command=self.validate, background="#6AED35")
        validate.grid(row=2, column=0, columnspan=2, sticky="nsew")

        self.canvas_img.update()
        self.final_width = self.canvas_img.winfo_width()
        self.ratio = self.Size[1] / self.final_width

        self.canvas_img.focus_force()
        self.stay_on_top()
        self.canvas_img.bind("<Configure>", self.afficher)
        self.modif_image()


    def active_selection(self):
        self.selection = not self.selection
        if self.selection:
            self.Choose_borders_B.config(background="grey")
        else:
                self.Choose_borders_B.config(background="SystemButtonFace")

    def draw_borders(self, event):
        self.delete()
        for Ar in range(len(self.arenas)):
            empty = np.zeros([self.Size[0], self.Size[1], 1], np.uint8)

            if len(self.selected_bd[Ar])==0:
                empty = cv2.drawContours(empty, [self.arenas[Ar]], -1, 255, int(float(event)*float(self.scale)*2))  # The width of the entrance area depends of the movemnet threshold of individuals
            else:
                for seg in self.selected_bd[Ar]:
                    empty = Function_draw_mask.draw_line(empty, seg[0], seg[1], 255, int(float(event) * float(self.scale) * 2))
            empty = cv2.drawContours(empty, [self.arenas[Ar]], -1, 0, -1)
            cnts, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            self.ents[Ar]=cnts

        self.modif_image()

    def show_tool(self, event):
        if not self.selection:
            event.x = int(event.x * self.ratio + self.zoom_sq[0])
            event.y = int(event.y * self.ratio + self.zoom_sq[1])
            self.image_to_show=self.last_image_to_show.copy()
            self.image_to_show=cv2.circle(self.image_to_show,[event.x,event.y],self.tool_size,(0,0,0),max(1,int(1*self.ratio)))
            self.afficher()

    def press(self, event):
        event.x = int(event.x * self.ratio + self.zoom_sq[0])
        event.y = int(event.y * self.ratio + self.zoom_sq[1])

        if not self.selection:
            self.binary = np.zeros([self.Size[0], self.Size[1], 1], np.uint8)
            self.binary=cv2.circle(self.binary, [event.x,event.y],self.tool_size,255,-1)
            self.last=[event.x,event.y]
            self.modif_image()

        else:
            count=0
            for Ar in self.arenas:
                approx = cv2.approxPolyDP(Ar, 0.025 * cv2.arcLength(Ar, True), True)
                for pt in range(-1,len(approx)-1):
                    seg=[[approx[pt][0][0],approx[pt][0][1]],[approx[pt+1][0][0],approx[pt+1][0][1]]]
                    if Function_draw_mask.Touched_seg([event.x, event.y], seg):
                        if seg in self.selected_bd[count]:
                            self.selected_bd[count].pop(self.selected_bd[count].index(seg))
                        else:
                            self.selected_bd[count].append(seg)
                count+=1

            self.modif_image()


    def click_n_move(self, event):
        if not self.selection:
            event.x = int(event.x * self.ratio + self.zoom_sq[0])
            event.y = int(event.y * self.ratio + self.zoom_sq[1])
            # When the cursor is moving, we draw line instead of circles to avoid gaps in the drawing if the user is moving the mouse fast
            self.binary=cv2.line(self.binary, self.last,[event.x,event.y],255,self.tool_size*2)
            self.last = [event.x, event.y]
            self.modif_image()


    def release(self, event):
        if not self.selection:

            new_cnts,_=cv2.findContours(self.binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for cnt_ID in range(len(new_cnts)):#If
                touched = []
                for A_ID in range(len(self.arenas)):
                    #If the new drawing touch the arena, or if it touch another entrance area or if it is inside the arena, we consider this new drawing could be an entrance of the arena
                    if self.contour_intersect(new_cnts[cnt_ID],self.arenas[A_ID]) or (len(self.ents[A_ID])>0 and self.contour_intersect(new_cnts[cnt_ID],self.ents[A_ID], multiple=True)):
                        touched.append(A_ID)

                if len(touched)==1:#If the new drawing touch more than one arena or none of them, we don't keep it
                    empty = np.zeros([self.Size[0], self.Size[1], 1], np.uint8)
                    empty=cv2.drawContours(empty,self.ents[touched[0]],-1,255,-1)
                    empty=cv2.drawContours(empty,new_cnts,cnt_ID,255,-1)
                    self.ents[touched[0]],_=cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            self.binary = []
            self.modif_image()

    def On_mousewheel(self, event):
        #Change the size of the tool
        if event.delta>0 or (self.tool_size>5 and event.delta<0):
            self.tool_size = int(self.tool_size  + (event.delta / 120))
            self.show_tool(event)

    def ccw(self, A, B, C):#Code from https://stackoverflow.com/questions/55641425/check-if-two-contours-intersect, https://stackoverflow.com/users/9084775/ivan
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    def contour_intersect(self, cnt_ref, cnt_query, multiple=False):#Code from https://stackoverflow.com/questions/55641425/check-if-two-contours-intersect, https://stackoverflow.com/users/9084775/ivan
        # A a little modification has been added to the original script as it did not consider the link between first and last point of the contours (i.e. I added the -1 in the range)
        #Also, we added the "mutiple" argument that is used to check wether the countour is in contact with more than one other contour
        ## Contour is a list of points
        ## Connect each point to the following point to get a line
        ## If any of the lines intersect, then break
        if not multiple:
            cnt_query=[cnt_query]

        for sub_qu in cnt_query:
            if cv2.pointPolygonTest(sub_qu, [int(cnt_ref[0][0][0]), int(cnt_ref[0][0][1])], False) >= 0:
                return True#If we begin the contour inside the shape, no need to check for intresection, this will also detect contours that are entirely inside others
            for ref_idx in range(-1,len(cnt_ref) - 1):
                ## Create reference line_ref with point AB
                A = cnt_ref[ref_idx][0]
                B = cnt_ref[ref_idx + 1][0]

                for query_idx in range(-1,len(sub_qu) - 1):
                    ## Create query line_query with point CD
                    C = sub_qu[query_idx][0]
                    D = sub_qu[query_idx + 1][0]

                    ## Check if line intersect
                    if self.ccw(A, C, D) != self.ccw(B, C, D) and self.ccw(A, B, C) != self.ccw(A, B, D):
                        ## If true, break loop earlier
                        return True

        return False

    def validate(self):
        self.boss.cnts_entrance=self.ents
        self.boss.bind_all("<Button-1>", self.boss.give_focus)
        self.boss.modif_image()
        self.parent.destroy()

    def delete(self):
        self.ents=[[] for Ar in self.arenas]
        self.modif_image()

    def modif_image(self):
        self.image_to_show=self.img.copy()
        self.image_to_show=cv2.drawContours(self.image_to_show,self.arenas,-1,(255,0,0),max([1,int(2*self.ratio)]))

        for Ar_id in range(len(self.arenas)):
            if len(self.selected_bd[Ar_id])>0:
                for seg in self.selected_bd[Ar_id]:
                    self.image_to_show=cv2.line(self.image_to_show,seg[0],seg[1],(150,0,250),max([1,int(2*self.ratio)]))

        overlay=self.image_to_show.copy()
        if len(self.binary) > 0:
            bool_mask = self.binary[:, :, 0].astype(bool)
            overlay[bool_mask]=(255,255,0)

        for cnts in self.ents:
            overlay = cv2.drawContours(overlay, cnts, -1, (255, 255, 0), -1)

        self.image_to_show = cv2.addWeighted(self.image_to_show, 0.5, overlay, 0.5, 1)
        self.last_image_to_show=self.image_to_show.copy()
        self.afficher()

    def afficher(self, *args):
        # Show the image
        best_ratio = max(self.Size[1] / (self.canvas_img.winfo_width()),
                         self.Size[0] / (self.canvas_img.winfo_height()))
        prev_final_width=self.final_width
        self.final_width=int(self.Size[1]/best_ratio)
        self.ratio=self.ratio*(prev_final_width/self.final_width)

        self.image_to_show2 = self.image_to_show[self.zoom_sq[1]:self.zoom_sq[3], self.zoom_sq[0]:self.zoom_sq[2]]
        self.TMP_image_to_show2 = cv2.resize(self.image_to_show2,
                                             (self.final_width, int(self.final_width * (self.Size[0] / self.Size[1]))))
        self.image_to_show3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP_image_to_show2))
        self.canvas_img.create_image(0, 0, image=self.image_to_show3, anchor=NW)
        self.canvas_img.config(width=self.final_width, height=int(self.final_width * (self.Size[0] / self.Size[1])))

    def Zoom_in(self, event):
        # Zoom in in the image
        self.new_zoom_sq = [0, 0, 0, 0]
        PX = event.x / ((self.zoom_sq[2] - self.zoom_sq[0]) / self.ratio)
        PY = event.y / ((self.zoom_sq[3] - self.zoom_sq[1]) / self.ratio)

        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]
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
            self.afficher()

    def Zoom_out(self, event):
        # Zoom out from the image
        self.new_zoom_sq = [0, 0, 0, 0]
        PX = event.x / ((self.zoom_sq[2] - self.zoom_sq[0]) / self.ratio)
        PY = event.y / ((self.zoom_sq[3] - self.zoom_sq[1]) / self.ratio)

        event.x = event.x * self.ratio + self.zoom_sq[0]
        event.y = event.y * self.ratio + self.zoom_sq[1]

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
        self.afficher()

    def stay_on_top(self):
        # We want this window to remain on the top of the others
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)
