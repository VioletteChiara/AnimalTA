from tkinter import *
from BioTrack import UserMessages
import math

class Ask(Frame):
    def __init__(self, parent, boss, Pt1, Pt2, scale, ratio, **kwargs):
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.grid(sticky="nsew")
        self.parent=parent
        self.boss=boss
        self.length=math.sqrt((Pt2[0]-Pt1[0])**2 + (Pt2[1]-Pt1[1])**2)/float(scale[0])
        self.Ratio=DoubleVar()
        self.Ratio.set(round(ratio,3))
        self.Units = DoubleVar()
        self.Units.set(round(self.Ratio.get()*self.length,3))
        self.UnitsB = DoubleVar()
        self.UnitsB.set(round(self.length-(self.Ratio.get()*self.length),3))
        self.binding=self.bind_all("<Return>",self.validate, add=True)
        self.parent.attributes('-toolwindow', True)
        self.grab_set()


        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        self.Pt1=Pt1
        self.Pt2=Pt2

        if abs(Pt2[0]-Pt1[0])>abs(Pt2[1]-Pt1[1]):
            self.orient = HORIZONTAL
        else:
            self.orient=VERTICAL


        Expl=Label(self, text=self.Messages["Border_portion0"])
        Expl.grid(row=0, column=0, columnspan=2)

        Scale_Prop=Scale(self, from_=0, to=self.length,resolution=0.001, variable=self.Units, orient=self.orient, command=self.update_ratio)
        Scale_Prop.grid(row=1, column=0, columnspan=4, sticky="nsew")


        Lab_Ratio=Label(self,text=self.Messages["Border_portion1"])
        Lab_Ratio.grid(row=2, column=0, columnspan=2)
        regRatio = (self.register(self.update_units), '%P', '%V')
        Entry_ratio=Entry(self, textvariable=self.Ratio, validate="all", validatecommand=regRatio)
        Entry_ratio.grid(row=3, column=0, rowspan=2)
        LRat=Label(self, text="/1")
        LRat.grid(row=3, column=1, rowspan=2, sticky="nsw")

        Lab_Units=Label(self,text=self.Messages["Border_portion2"])
        Lab_Units.grid(row=2, column=2, columnspan=2)
        regUnits = (self.register(self.update_ratio), '%P', '%V')
        Entry_units=Entry(self, textvariable=self.Units, validate="all", validatecommand=regUnits)
        Entry_units.grid(row=3, column=2)
        Units=Label(self, text=scale[1])
        Units.grid(row=3, column=3, sticky="w")

        regUnitsB = (self.register(self.update_ratioB), '%P', '%V')
        Entry_unitsB=Entry(self, textvariable=self.UnitsB, validate="all", validatecommand=regUnitsB)
        Entry_unitsB.grid(row=4, column=2)
        UnitsB=Label(self, text=scale[1])
        UnitsB.grid(row=4, column=3, sticky="w")

        BValidate=Button(self, text=self.Messages["Validate"], background="green", command=self.validate)
        BValidate.grid(row=5, column=0, columnspan=4)

        self.boss.ready=False
        self.stay_on_top()

    def stay_on_top(self):
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)

    def validate(self, *args):
        if self.orient == HORIZONTAL:
            if self.Pt1[0]>self.Pt2[0]:
                self.boss.ratio_border=1-self.Ratio.get()
            else:
                self.boss.ratio_border = self.Ratio.get()

        else:
            if self.Pt1[1]>self.Pt2[1]:
                self.boss.ratio_border=1-self.Ratio.get()
            else:
                self.boss.ratio_border = self.Ratio.get()


        self.parent.destroy()
        self.destroy()
        self.unbind_all("<Return>")
        self.boss.bind_all("<Return>", self.boss.validate_borders)
        self.boss.ready = True#On remet l'autre fenetre au premier plan
        self.grab_release()

    def update_units(self, new_val, method):
        if new_val == "" and method != "focusout":
            return True
        elif new_val != "":
            if method == "key":
                try:
                    new_val = float(new_val)
                    if new_val>1:
                        return False
                    else:
                        self.Units.set(round(new_val * self.length, 3))
                        self.UnitsB.set(round(self.length-(new_val * self.length), 3))
                except:
                    return False

            return True
        else:
            return False

    def update_ratio(self, new_val, method="key"):
        if (new_val == "" or new_val == "-") and method != "focusout":
            return True
        elif new_val != "":
            if method == "key":
                try:
                    new_val = float(new_val)
                    if new_val>self.length:
                        return False
                    else:
                        new_ratio=round(new_val / self.length,3)
                        self.Ratio.set(new_ratio)
                        self.UnitsB.set(round(self.length - new_val,3))
                except:
                    return False

            return True
        else:
            return False

    def update_ratioB(self, new_val, method="key"):
        if (new_val == "" or new_val == "-") and method != "focusout":
            return True
        elif new_val != "":
            if method == "key":
                try:
                    new_val = float(new_val)
                    if new_val>self.length:
                        return False
                    else:
                        new_ratio=round(1-(new_val / self.length),3)
                        self.Ratio.set(new_ratio)
                        self.Units.set(round(self.length-new_val,3))

                except:
                    return False

            return True
        else:
            return False