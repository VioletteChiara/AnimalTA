from tkinter import *
from AnimalTA import UserMessages


class Modify(Frame):
    """This little frame allows the user to modify the parameters of the smoothing filter."""
    def __init__(self, parent, boss, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.parent=parent
        self.boss=boss
        self.grid()
        self.grab_set()
        self.parent.attributes('-toolwindow', True)

        #If the video has less than 100 frames, we limit the windows lenght parameter to the length of the video, if not the maximum is 100.
        self.max_windows=min(len(self.boss.Coos_brutes["Ind0"]),100)
        if self.max_windows%2==0:
            self.max_windows-=1

        #Importation of the messages
        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        #The two parameters we are interested in
        or_val_wl=self.boss.window_length
        or_val_poly = self.boss.polyorder
        self.past=or_val_wl

        self.winfo_toplevel().title(self.Messages["Smooth0"])

        #We create two scales to allow the user to change the parameters values
        self.Label_wlen=Label(self, text=self.Messages["Smooth1"])
        self.Label_wlen.grid(row=0, column=1)

        self.scale_wlen_all=Scale(self,from_=3, to=self.max_windows, command=self.move_scaleWL, orient=HORIZONTAL, length=300)
        self.scale_wlen_all.grid(row=1, column=1)
        self.scale_wlen_all.set(or_val_wl)

        self.minus_wlen_all=Button(self,text="<",command=self.move_scaleWL_min)
        self.minus_wlen_all.grid(row=1, column=0)

        self.plus_wlen_all=Button(self,text=">",command=self.move_scaleWL_plus)
        self.plus_wlen_all.grid(row=1, column=2)

        self.Label_poly=Label(self, text=self.Messages["Smooth2"])
        self.Label_poly.grid(row=3, column=1)

        self.scale_poly_all=Scale(self,from_=1, to=self.scale_wlen_all.get()-1, command=self.move_scale_poly, orient=HORIZONTAL, length=300)
        self.scale_poly_all.grid(row=4, column=1)
        self.scale_poly_all.set(or_val_poly)

        self.minus_poly_all=Button(self,text="<",command=self.move_scale_poly_min)
        self.minus_poly_all.grid(row=4, column=0)

        self.plus_poly_all=Button(self,text=">",command=self.move_scale_poly_plus)
        self.plus_poly_all.grid(row=4, column=2)

        #Show the result of the smoothing filter with set parameters
        self.Show_param=Button(self,text=self.Messages["Smooth3"],command=self.change_param)
        self.Show_param.grid(row=6, column=0)

        #Save the parameters and close this Frame
        self.Validate_param=Button(self,text=self.Messages["Validate"],command=self.validate)
        self.Validate_param.grid(row=6, column=1)

        self.rowconfigure(2, minsize=30)
        self.rowconfigure(5, minsize=30)

    def move_scaleWL_min(self):
        #Decrease the windows length parameter by 2 (only odd numbers are accepted)
        self.plus_wlen_all.config(state="active")
        n=self.scale_wlen_all.get()-2
        self.scale_wlen_all.set(n)
        self.fix(n)

    def move_scaleWL_plus(self):
        # Increase the windows length parameter by 2 (only odd numbers are accepted)
        self.minus_wlen_all.config(state="active")
        n=self.scale_wlen_all.get()+2
        self.scale_wlen_all.set(n)
        self.fix(n)

    def move_scaleWL(self,n):
        #Update teh buttons and values when the windows scale is chnaged by user
        self.fix(n)
        self.minus_wlen_all.config(state="active")
        self.plus_wlen_all.config(state="active")
        if int(n)<=3:
            self.minus_wlen_all.config(state="disable")
        if int(n)>=self.max_windows:
            self.plus_wlen_all.config(state="disable")

    def fix(self, n):
        #Ensure that only odds number are used as parameter
        n = int(n)
        if not n % 2:
            self.scale_wlen_all.set(n + 1 if n > self.past else n - 1)
            self.past = self.scale_wlen_all.get()
        self.scale_poly_all.config(to=min(self.scale_wlen_all.get()-1,5))

    def move_scale_poly_min(self):
        #Decrease the polyorder parameter by 1
        self.plus_poly_all.config(state="active")
        n=self.scale_poly_all.get()-1
        if n>=1:
            self.scale_poly_all.set(n)
        if n<=self.scale_wlen_all.get()-1:
            self.minus_poly_all.config(state="disable")

    def move_scale_poly_plus(self):
        #Increase the polyorder parameter by 1
        self.minus_poly_all.config(state="active")
        n=self.scale_poly_all.get()+1
        if n<=self.scale_wlen_all.get()-1:
            self.scale_poly_all.set(n)
        if n>=self.max_windows:
            self.plus_poly_all.config(state="disable")

    def move_scale_poly(self,n):
        #Change the button state when the value of polyorder is modified directly on the scale by user
        self.minus_poly_all.config(state="active")
        self.plus_poly_all.config(state="active")
        if int(n)<2:
            self.minus_poly_all.config(state="disable")
        if int(n)>=self.scale_wlen_all.get()-1:
            self.plus_poly_all.config(state="disable")

    def change_param(self):
        #Save the new values
        self.boss.polyorder=self.scale_poly_all.get()
        self.boss.window_length = self.scale_wlen_all.get()
        self.boss.change_type_coos(modif=True)

    def validate(self):
        #Save and destroy
        self.change_param()
        self.grab_release()
        self.parent.destroy()

"""
root = Tk()
root.geometry("+100+100")

interface = Modify(parent=root, boss=None)
root.mainloop()
"""