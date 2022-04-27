from tkinter import *
import math

class Scale_log(Frame):
    def __init__(self, parent, variable=None,  command=None, log=False, to=100000, length=100, from_=0, **kwargs):
        Scale.__init__(self, parent, **kwargs)
        self.variable=variable
        self.scale_variable=DoubleVar()
        self.length=length

        self.command=command
        self.log=log
        self.to=to
        self.from_=from_


        if self.log:
            self.fixed_L=math.log(self.to,10)*1000
            self.scale_variable.set(0)
            self.variable.set(0)
        else:
            self.fixed_L = self.to
            self.scale_variable.set(self.to)


        self.slide = Scale(self, orient=HORIZONTAL, command=self.setValue,
                           length=self.length, from_=self.from_, to=self.fixed_L, variable=self.scale_variable,
                           showvalue=0)
        self.text = Label(self, textvariable=self.variable)
        self.slide.pack(side=LEFT, expand=1, fill=X)
        self.text.pack(side=TOP, fill=BOTH)

    def setValue(self, val):
        if self.log:
            val = round(float(val))

            if round(10 ** (val / 1000)-1,3)<1000:
                self.variable.set(round(10 ** (val / 1000)-1,2))
            else:
                self.variable.set("{:.2e}".format(round(10 ** (val / 1000)-1,3)))

        else:
            print("A")
            self.variable.set(round(float(val),3))
        self.command()




# root = Tk()
# s = Slider(root)
# s.pack()
# root.mainloop()