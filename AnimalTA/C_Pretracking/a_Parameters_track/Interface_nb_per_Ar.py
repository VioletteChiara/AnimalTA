from tkinter import *
from AnimalTA.A_General_tools import Function_draw_mask as Dr, UserMessages
import cv2
import PIL
import numpy as np

class Assign(Frame):
    """ This is a small Frame in which the user can define the nomber of targets per arena, in the case the number is variable between arenas."""
    def __init__(self, parent, boss, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.boss=boss
        self.grid(sticky="nsew")
        self.config()
        self.grab_set()

        Grid.columnconfigure(self.parent,0,weight=1)
        Grid.rowconfigure(self.parent, 0, weight=1)

        #Message importation
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()


        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Param9"])

        #We look for the arenas and their names
        self.mask = Dr.draw_mask(self.boss.Vid)
        self.Arenas, _ = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.Arenas = Dr.Organise_Ars(self.Arenas)

        Grid.columnconfigure(self,0,weight=1)
        Grid.rowconfigure(self, 0, weight=1)

        self.canvas_video=Canvas(self)
        self.canvas_video.grid(row=0, column=0, sticky="nsew")

        #We create one slider for each arena
        self.Opn_Fr = Frame(self)
        self.Opn_Fr.grid(row=0, column=1, sticky="nsew")
        self.all_vals_var=[IntVar(self,x) for x in self.boss.liste_ind_per_ar]
        for row in range(len(self.Arenas)):
            Label(self.Opn_Fr, text=self.Messages["Arena"] + " " + str(row)).grid(row=row, column=0)
            Scale(self.Opn_Fr,from_=1, to=100, variable=self.all_vals_var[row], orient=HORIZONTAL).grid(row=row, column=1)

        #Validation button
        self.B_validate = Button(self.Opn_Fr, text=self.Messages["Validate"], command=self.validate, background="#6AED35")
        self.B_validate.grid(columnspan=2)

        self.final_width = 700

        self.canvas_video.update()
        self.final_width = self.canvas_video.winfo_width()
        self.Size=self.boss.Vid.shape
        self.ratio = self.Size[1] / self.final_width

        #The image to be displayed
        self.TMP_image_to_show=np.copy(self.boss.last_empty)

        self.bind("<Configure>", self.show_img)
        self.show_img()

    def show_img(self, *args):
        #Display the image
        best_ratio = max(self.Size[1] / (self.canvas_video.winfo_width()),self.Size[0] / (self.canvas_video.winfo_height()))
        prev_final_width = self.final_width
        self.final_width = int(self.Size[1] / best_ratio)
        self.ratio = self.ratio * (prev_final_width / self.final_width)

        #Draw the contours of the arenas
        self.TMP_image_to_show_Cop=np.copy(self.TMP_image_to_show)
        self.TMP_image_to_show_Cop=cv2.drawContours(self.TMP_image_to_show_Cop,self.Arenas,-1,(255,0,0),max(1,int(2*self.ratio)))

        if self.final_width>0.001:
            for Ar in range(len(self.Arenas)):
                x,y,w,h =cv2.boundingRect(self.Arenas[Ar])
                (w, h), _ = cv2.getTextSize(str(Ar), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, thickness=1)
                self.TMP_image_to_show_Cop = cv2.putText(self.TMP_image_to_show_Cop, str(Ar), (x+ max(int(5*self.ratio),1), y + h + max(int(5*self.ratio),1)),cv2.FONT_HERSHEY_DUPLEX,  max(0.8*self.ratio,1), (255, 0, 0), max(int(2*self.ratio),1))

            self.TMP_image_to_show2 = cv2.resize(self.TMP_image_to_show_Cop,(self.final_width, int(self.final_width * (self.Size[0] / self.Size[1]))))
            self.image_to_show3 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP_image_to_show2))
            self.canvas_video.create_image(0, 0, image=self.image_to_show3, anchor=NW)
            self.canvas_video.config(width=self.final_width, height=int(self.final_width * (self.Size[0] / self.Size[1])))


    def validate(self):
        #Save and destroy the parent window
        self.boss.liste_ind_per_ar = [x.get() for x in self.all_vals_var]
        self.boss.modif_image()
        self.grab_release()
        self.parent.destroy()



"""
root = Tk()
root.geometry("+100+100")

interface = Modify(parent=root, boss=None)
root.mainloop()
"""