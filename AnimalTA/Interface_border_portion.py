from tkinter import *
from AnimalTA import UserMessages
import math

class Ask(Frame):
    """This frame will appear if the user wants to draw a line between two points of the arenas' borders. It allows the user to choose exactly where on the border (in the middle, at 5 cm etc.) the line will be placed"""
    def __init__(self, parent, boss, Pt1, Pt2, scale, ratio, **kwargs):
        #Pt1 and Pt2: the two extremities of the considered border
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.grid(sticky="nsew")
        self.parent=parent
        self.boss=boss

        self.length=math.sqrt((Pt2[0]-Pt1[0])**2 + (Pt2[1]-Pt1[1])**2)/float(scale[0])#Legnth of the border (in units)
        self.Ratio=DoubleVar()
        self.Ratio.set(round(ratio,3))#the default position of the line (expressed in proportion of the border)
        self.Units = DoubleVar()
        self.Units.set(round(self.Ratio.get()*self.length,3))#The position in units
        self.UnitsB = DoubleVar()
        self.UnitsB.set(round(self.length-(self.Ratio.get()*self.length),3))#The position in units from the other side of the border (i.e. if self.Units=1/3, self.UnitsB=2/3)
        self.binding=self.bind_all("<Return>",self.validate, add=True)
        self.parent.attributes('-toolwindow', True)
        self.grab_set()

        #Importation of messages
        self.Language = StringVar()
        f = open("Files/Language", "r")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]

        self.Pt1=Pt1
        self.Pt2=Pt2

        #We determmine wether the border is more horizontal or more vertical so the slider looks as much as possible to the border itself
        if abs(Pt2[0]-Pt1[0])>abs(Pt2[1]-Pt1[1]):
            self.orient = HORIZONTAL
        else:
            self.orient=VERTICAL

        #Frame organization
        #Title
        Expl=Label(self, text=self.Messages["Border_portion0"])
        Expl.grid(row=0, column=0, columnspan=2)

        #Slider
        Scale_Prop=Scale(self, from_=0, to=self.length,resolution=0.001, variable=self.Units, orient=self.orient, command=self.update_ratio_scale)
        Scale_Prop.grid(row=1, column=0, columnspan=4, sticky="nsew")

        #Visual information + manual entry
        Lab_Ratio=Label(self,text=self.Messages["Border_portion1"])
        Lab_Ratio.grid(row=2, column=0, columnspan=2)
        regRatio = (self.register(self.update_ratio), '%P', '%V')
        Entry_ratio=Entry(self, textvariable=self.Ratio, validate="all", validatecommand=regRatio)
        Entry_ratio.grid(row=3, column=0, rowspan=2)
        LRat=Label(self, text="/1")
        LRat.grid(row=3, column=1, rowspan=2, sticky="nsw")

        #Units informations
        Lab_Units=Label(self,text=self.Messages["Border_portion2"])
        Lab_Units.grid(row=2, column=2, columnspan=2)
        regUnits = (self.register(self.update_units), '%P', '%V')
        Entry_units=Entry(self, textvariable=self.Units, validate="all", validatecommand=regUnits)
        Entry_units.grid(row=3, column=2)
        Units=Label(self, text=scale[1])
        Units.grid(row=3, column=3, sticky="w")

        regUnitsB = (self.register(self.update_unitsB), '%P', '%V')
        Entry_unitsB=Entry(self, textvariable=self.UnitsB, validate="all", validatecommand=regUnitsB)
        Entry_unitsB.grid(row=4, column=2)
        UnitsB=Label(self, text=scale[1])
        UnitsB.grid(row=4, column=3, sticky="w")

        #Button to validate once the position is chosen
        BValidate=Button(self, text=self.Messages["Validate"], background="#6AED35", command=self.validate)
        BValidate.grid(row=5, column=0, columnspan=4)

        self.boss.ready=False
        self.stay_on_top()


    def update_ratio_scale(self, val):
        #If the value is modified using the scale
        val=float(val)
        self.UnitsB.set(round(self.length - (val * self.length), 3))
        self.Ratio.set(round(val/self.length,2))

    def stay_on_top(self):
        #This function ensure that this window will always be in front of the others
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)

    def validate(self, *args):
        #Save the user's choice
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

        #End of this window
        self.parent.destroy()
        self.destroy()
        self.unbind_all("<Return>")
        self.boss.bind_all("<Return>", self.boss.validate_borders)
        self.boss.ready = True#On remet l'autre fenetre au premier plan
        self.grab_release()

    def update_ratio(self, new_val, method):
        #If the user is writting directly the position wanted, we check that they are valid entries (only floats >0 and <1)
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

    def update_units(self, new_val, method="key"):
        #If the user is writting directly the position wanted, we check that they are valid entries (only floats < border length)
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

    def update_unitsB(self, new_val, method="key"):
        # Same here but in the opposite direction, we check that they are valid entries (only floats < border length)
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