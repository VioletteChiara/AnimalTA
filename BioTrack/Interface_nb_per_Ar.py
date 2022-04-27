from tkinter import *
from BioTrack import UserMessages, Function_draw_mask as Dr
import cv2
import PIL
import numpy as np

class Assign(Frame):
    def __init__(self, parent, boss, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.boss=boss
        self.grid()
        self.grab_set()

        self.max_windows=1001

        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()


        self.Messages = UserMessages.Mess[self.Language.get()]
        self.winfo_toplevel().title(self.Messages["Param9"])

        self.mask = Dr.draw_mask(self.boss.Vid)
        self.Arenas, _ = cv2.findContours(self.mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.Arenas = Dr.Organise_Ars(self.Arenas)


        self.Img_Fr=Frame(self)
        self.Img_Fr.grid(row=0, column=0)

        self.Opn_Fr = Frame(self)
        self.Opn_Fr.grid(row=0, column=1)

        self.canvas_video=Canvas(self.Img_Fr)
        self.canvas_video.grid()

        self.TMP_image_to_show=np.copy(self.boss.TMP_image_to_show)
        self.TMP_image_to_show=cv2.drawContours(self.TMP_image_to_show,self.Arenas,-1,(255,0,0),8)
        for Ar in range(len(self.Arenas)):
            self.TMP_image_to_show=cv2.putText(self.TMP_image_to_show,str(Ar),(self.Arenas[Ar][0][0][0],self.Arenas[Ar][0][0][1]+50),cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 3)


        self.TMP_image_to_show=cv2.resize(self.TMP_image_to_show,(int(self.boss.Vid.shape[1]/3),int(self.boss.Vid.shape[0]/3)))
        self.image_to_show2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.TMP_image_to_show))
        self.can_import = self.canvas_video.create_image(0, 0, image=self.image_to_show2, anchor=NW)
        self.canvas_video.config(height=self.TMP_image_to_show.shape[0], width=self.TMP_image_to_show.shape[1])
        self.canvas_video.itemconfig(self.can_import, image=self.image_to_show2)

        self.all_vals_var=[IntVar(self,x) for x in self.boss.liste_ind_per_ar]
        for row in range(len(self.Arenas)):
            Label(self.Opn_Fr, text=self.Messages["Arena"] + " " + str(row)).grid(row=row, column=0)
            Scale(self.Opn_Fr,from_=1, to=20, variable=self.all_vals_var[row], orient=HORIZONTAL).grid(row=row, column=1)

        self.B_validate = Button(self.Opn_Fr, text=self.Messages["Validate"], command=self.validate)
        self.B_validate.grid()

    def validate(self):
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