from tkinter import *
from AnimalTA.A_General_tools import UserMessages
import math
#import pandas as pd
#from pandastable import Table, TableModel
from functools import partial


class Int_import(Frame):
    """This frame will appear if the user wants to draw a line between two points of the arenas' borders. It allows the user to choose exactly where on the border (in the middle, at 5 cm etc.) the line will be placed"""
    def __init__(self, parent, files, Vid, **kwargs):
        #Pt1 and Pt2: the two extremities of the considered border
        Frame.__init__(self, parent, bd=5, **kwargs)
        self.grid(sticky="nsew")
        self.parent=parent
        self.Vid=Vid

        self.sep=StringVar()# Which separator does the original file use
        self.sep.set("\\t")
        self.header=IntVar() #Do the original file use a header? If 0, we try to determine it automatically, 1 no header, 2 header
        self.header.set(0)

        self.or_Tab=Frame(self)
        self.or_Tab.grid(row=1,column=0)

        self.res_Tab = Frame(self)
        self.res_Tab.grid(row=1, column=1)

        #Options for the user
        Frame_info=Frame(self)
        Frame_info.grid(row=0,column=0, columnspan=2)

        #Choose the separator
        Entry_sep=Entry(Frame_info, textvariable=self.sep)
        Entry_sep.grid(row=0, column=0)
        Validate_Entry=Button(Frame_info, text="MISSING, Separator", command=partial(self.load_files, files))
        Validate_Entry.grid(row=0, column=1)

        #Indicate if the header is present or no
        Check_H = Checkbutton(Frame_info, text='MISSING, Header', variable=self.header, onvalue=2, offvalue=1, command=partial(self.load_files, files))
        Check_H.grid(row=1, column=0, columnspan=2)

        #Indicate which column is the one for Frame number:
        self.Fr_pos=StringVar()
        self.Fr_pos.set(1)
        Entry_Fr_pos=Entry(Frame_info, textvariable=self.Fr_pos)
        Entry_Fr_pos.grid(row=0, column=2)
        Validate_Entry_Fr_pos=Button(Frame_info, text="MISSING, Column_Fr", command=self.create_new)
        Validate_Entry_Fr_pos.grid(row=0, column=3)

        #Indicate which column is the one for Time:
        self.Time_pos=StringVar()
        self.Time_pos.set(1)
        Entry_Fr_pos=Entry(Frame_info, textvariable=self.Time_pos)
        Entry_Fr_pos.grid(row=1, column=2)
        Validate_Entry_Fr_pos=Button(Frame_info, text="MISSING, Column_Time", command=self.create_new)
        Validate_Entry_Fr_pos.grid(row=1, column=3)


        #Importation of messages
        self.Language = StringVar()
        f = open(UserMessages.resource_path("AnimalTA/Files/Language"), "r", encoding="utf-8")
        self.Language.set(f.read())
        self.LanguageO = self.Language.get()
        f.close()
        self.Messages = UserMessages.Mess[self.Language.get()]


        #Button to validate once the position is chosen
        BValidate=Button(self, text=self.Messages["Validate"], background="#6AED35", command=self.validate)
        BValidate.grid(row=5, column=0, columnspan=4)

        self.load_files(files)
        #self.stay_on_top()

    def load_files(self, files, reset_H=False):
        for file in files:
            if self.header.get()==0:
                data = pd.read_csv(file, header=None, sep=self.sep.get(), engine='python')
                if sum([isinstance(val, int) or isinstance(val, float) for val in data.iloc[0]])/len(data.iloc[0])<0.75:
                    data.columns = data.iloc[0]
                    data = data[1:]
                    self.header.set(2)
                else:
                    self.header.set(1)

            elif self.header.get()==2:
                data = pd.read_csv(file, header=[0], sep=self.sep.get(), engine='python')
            else:
                data = pd.read_csv(file, header=None, sep=self.sep.get(), engine='python')

            self.or_data=data
            self.table = pt = Table(self.or_Tab, dataframe=data, showtoolbar=False, showstatusbar=False)

            pt.show()

    def create_new(self):

        if int(self.Time_pos.get())==0 and int(self.Fr_pos.get())==0:
            one_every = int(round(round(self.Vid.Frame_rate[0], 2) / self.Vid.Frame_rate[1]))
            fr_col=range(int(self.Vid.Cropped[1][0]/one_every),int(self.Vid.Cropped[1][1]/one_every+1))
            self.trans_data=pd.DataFrame(fr_col,columns =['Frame'])
            self.trans_data["Time"]=fr_col
            self.trans_data["Time"]=self.trans_data["Time"].div(self.Vid.Frame_rate[1])

        elif int(self.Fr_pos.get())!=0:
            self.trans_data = pd.DataFrame(self.or_data.iloc[:, [int(self.Fr_pos.get())]].copy(), columns=['Frame'])
            self.trans_data["Time"] = self.trans_data["Frame"].copy()
            self.trans_data["Time"] = self.trans_data["Time"].div(self.Vid.Frame_rate[1])

        elif int(self.Time_pos.get())!=0:
            one_every = int(round(round(self.Vid.Frame_rate[0], 2) / self.Vid.Frame_rate[1]))
            fr_col=range(int(self.Vid.Cropped[1][0]/one_every),int(self.Vid.Cropped[1][1]/one_every+1))
            self.trans_data=pd.DataFrame(fr_col,columns =['Frame'])
            self.trans_data["Frame"]=fr_col
            self.trans_data["Time"] = self.or_data.iloc[:,[int(self.Time_pos.get()) - 1]].copy()
            self.trans_data["Frame"] = self.trans_data["Time"].copy()
            self.trans_data["Frame"] *= self.Vid.Frame_rate[1]

        else:
            self.trans_data = self.or_data.iloc[:,[int(self.Fr_pos.get())-1,int(self.Time_pos.get())-1]].copy()
            self.trans_data.columns=["Frame","Time"]

        self.table = pt = Table(self.res_Tab, dataframe=self.trans_data, showtoolbar=False, showstatusbar=False)

        pt.show()




    def stay_on_top(self):
        #This function ensure that this window will always be in front of the others
        self.parent.lift()
        self.parent.after(50, self.stay_on_top)

    def validate(self, *args):
        #Save the user's choice
        #End of this window
        self.parent.destroy()
        self.destroy()
        self.unbind_all("<Return>")
        self.grab_release()
