from tkinter import *
from BioTrack import UserMessages


class First_params(Frame):
    def __init__(self, parent, boss, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.boss=boss

        self.winfo_toplevel().title("Please select your language")
        self.parent.geometry("400x200+300+200")
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)


        self.grid(sticky="eswn")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        List_languages=list(UserMessages.Mess.keys())
        self.languages = Listbox(self)
        for lan in range(len(List_languages)):
            self.languages.insert(lan, List_languages[lan])
        self.languages.grid()


        Validate=Button(self, text="Validate", command=self.validate)
        Validate.grid()

        self.stay_on_top()
        self.parent.protocol("WM_DELETE_WINDOW", self.boss.destroy)#Si l'utilisateur ferme la fenêtre


    def validate(self):
        f = open("Files/Language", "w")
        f.write(self.languages.get(self.languages.curselection()))
        f.close()
        self.boss.open_BioTrack()
        self.parent.destroy()

    def stay_on_top(self):
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)








"""
root = Tk()
root.geometry("+100+100")
Video_file=Class_Video.Video(File_name="D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01.avi")
Video_file.Back[0]=True

im=cv2.imread("D:/Post-doc/Experiments/Group_composition/Shoaling/Videos_conv_cut/Track_by_mark/Deinterlace/14_12_01_background.bmp")
im=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
Video_file.Back[1]=im
interface = Scale(parent=root, boss=None, Video_file=Video_file)
root.mainloop()
"""